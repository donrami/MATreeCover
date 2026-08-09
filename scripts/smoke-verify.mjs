#!/usr/bin/env node
// FR-011 smoke driver (feature 014, T027): verifies the interactive surface of the
// current bundle in a FRESH chromium profile: zoom controls, building/district
// popups, trees toggle, story-modal dismissal, console cleanliness.
// Usage: node scripts/smoke-verify.mjs [--url http://127.0.0.1:8088/] [--chrome /usr/bin/chromium]
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const args = Object.fromEntries(process.argv.slice(2).map((a, i, arr) =>
  a.startsWith('--') ? [a.slice(2), arr[i + 1] ?? true] : null).filter(Boolean));
const URL = args.url ?? 'http://127.0.0.1:8088/';
const chrome = args.chrome ?? '/usr/bin/chromium';
const port = 9700 + Math.floor(Math.random() * 90);
const profile = mkdtempSync(join(tmpdir(), 'smoke-'));
const proc = spawn(chrome, [
  '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
  `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws;
const idRef = { id: 0 };
async function cdp(method, params = {}, sessionId) {
  const id = ++idRef.id;
  ws.send(JSON.stringify({ id, sessionId, method, params }));
  return new Promise((resolve, reject) => {
    const onMsg = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id === id) { ws.removeEventListener('message', onMsg); msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result); }
    };
    ws.addEventListener('message', onMsg);
  });
}

try {
  let version;
  for (let i = 0; i < 50; i++) {
    try { version = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json(); break; } catch { await sleep(200); }
  }
  ws = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  const { targetId } = await cdp('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await cdp('Target.attachToTarget', { targetId, flatten: true });
  const send = (method, params = {}) => cdp(method, params, sessionId);

  await send('Page.enable');
  await send('Network.enable');
  const consoleErrors = [];
  const tileReqs = { buildings: 0 };
  const onMsg = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.sessionId !== sessionId) return;
    if (msg.method === 'Runtime.consoleAPICalled' && msg.params.type === 'error') {
      consoleErrors.push(msg.params.args.map(a => a.value ?? a.description ?? '').join(' ').slice(0, 120));
    }
    if (msg.method === 'Network.requestWillBeSent' && msg.params.request.url.includes('buildings.pmtiles')) tileReqs.buildings++;
  };
  ws.addEventListener('message', onMsg);

  const evalJs = async (expr) => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result.value;

  await send('Page.navigate', { url: URL });
  await new Promise((resolve) => {
    const onNav = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.method === 'Page.loadEventFired' && msg.sessionId === sessionId) { ws.removeEventListener('message', onNav); resolve(); }
    };
    ws.addEventListener('message', onNav);
  });
  await sleep(5000);

  const results = {};
  results.title = await evalJs(`document.title`);
  results.controls = await evalJs(`['.maplibregl-ctrl-zoom-in', '.maplibregl-ctrl-zoom-out', '.maplibregl-ctrl-compass', '#baeume', '#legend'].every(s => !!document.querySelector(s))`);
  results.legendLabels = await evalJs(`document.querySelector('#legend')?.innerText.includes('0') && document.querySelector('#legend')?.innerText.includes('100')`);

  // dismiss the first-visit story modal
  await evalJs(`document.querySelector('#story-close')?.click(); true`);
  await sleep(300);

  // zoom via real input; zoom works if new pmtiles tile requests appear
  const zoomBtn = await evalJs(`(() => { const b = document.querySelector('.maplibregl-ctrl-zoom-in'); const r = b.getBoundingClientRect(); return { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2) }; })()`);
  const beforeTiles = tileReqs.buildings;
  for (let i = 0; i < 2; i++) {
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: zoomBtn.x, y: zoomBtn.y, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: zoomBtn.x, y: zoomBtn.y, button: 'left', clickCount: 1 });
    await sleep(1200);
  }
  results.zoomFiresTiles = tileReqs.buildings > beforeTiles;

  // click a grid of points until a popup opens; classify building vs district
  const canvasRect = await evalJs(`(() => { const c = document.querySelector('#map canvas'); const r = c.getBoundingClientRect(); return { x: r.x, y: r.y, w: r.width, h: r.height }; })()`);
  const popupTypes = [];
  for (const [fx, fy] of [[0.5, 0.5], [0.55, 0.52], [0.45, 0.55], [0.6, 0.48], [0.52, 0.6], [0.48, 0.42]]) {
    const cx = Math.round(canvasRect.x + canvasRect.w * fx);
    const cy = Math.round(canvasRect.y + canvasRect.h * fy);
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: cx, y: cy, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: cx, y: cy, button: 'left', clickCount: 1 });
    await sleep(500);
    const p = await evalJs(`(() => { const p = document.querySelector('.maplibregl-popup'); if (!p) return null; const t = p.innerText.replace(/\s+/g, ' '); p.querySelector('.maplibregl-popup-close-button')?.click(); return t.slice(0, 160); })()`);
    if (p) popupTypes.push(p.includes('Baumanteil im 60-m-Umkreis') && !p.includes('Durchschnitt') ? 'building' : 'district');
    await sleep(200);
  }
  results.popupTypes = popupTypes;
  results.buildingPopupSeen = popupTypes.includes('building');
  results.districtPopupSeen = popupTypes.includes('district');
  results.onlyOnePopupAtATime = popupTypes.length > 0;

  // trees toggle
  results.treesToggle = await evalJs(`(() => { const b = document.querySelector('#baeume'); const a0 = b.getAttribute('aria-pressed'); b.click(); const a1 = b.getAttribute('aria-pressed'); b.click(); const a2 = b.getAttribute('aria-pressed'); return a0 === 'false' && a1 === 'true' && a2 === 'false'; })()`);

  // ---- ko-fi donation button (feature 017, US1): desktop viewports, button
  // visible in the surface footer while the panel is expanded, hidden when
  // collapsed (FR-001), click opens the exact Ko-fi URL in a new tab, the
  // map page stays open and interactive in the original tab ----
  const koFi = { widths: {} };
  for (const width of [768, 1280, 1920]) {
    const w = {};
    await send('Emulation.setDeviceMetricsOverride', { width, height: 800, deviceScaleFactor: 1, mobile: false });
    await send('Page.navigate', { url: URL });
    await new Promise((resolve) => {
      const onNav = (ev) => {
        const msg = JSON.parse(ev.data);
        if (msg.method === 'Page.loadEventFired' && msg.sessionId === sessionId) { ws.removeEventListener('message', onNav); resolve(); }
      };
      ws.addEventListener('message', onNav);
    });
    await sleep(5000);
    // dismiss the first-visit story modal so it cannot intercept the click
    await evalJs(`document.querySelector('#story-close')?.click(); true`);
    await sleep(300);
    w.visibleInFooter = await evalJs(`(() => { const a = document.querySelector('.ko-fi'); if (!a) return false; const r = a.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.top >= 0 && r.bottom <= window.innerHeight; })()`);
    // expanded-only visibility (FR-001): collapsing hides the footer, re-expanding restores it
    w.collapsedHidesFooter = await evalJs(`(() => { const t = document.querySelector('#surface-toggle'); const a = document.querySelector('.ko-fi'); if (!t || !a) return false; t.click(); const r1 = a.getBoundingClientRect(); const hidden = r1.width === 0 && r1.height === 0; t.click(); const r2 = a.getBoundingClientRect(); return hidden && r2.width > 0 && r2.height > 0; })()`);
    const koFiPos = await evalJs(`(() => { const a = document.querySelector('.ko-fi'); const r = a.getBoundingClientRect(); return { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2) }; })()`);
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: koFiPos.x, y: koFiPos.y, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: koFiPos.x, y: koFiPos.y, button: 'left', clickCount: 1 });
    let koFiTarget = null;
    for (let i = 0; i < 25 && !koFiTarget; i++) {
      await sleep(200);
      const targets = (await cdp('Target.getTargets')).targetInfos;
      koFiTarget = targets.find(t => t.type === 'page' && t.url.startsWith('https://ko-fi.com/M4Q624RYOV'));
    }
    w.newTabUrl = koFiTarget ? koFiTarget.url : null;
    w.openedExactUrl = !!koFiTarget && (koFiTarget.url === 'https://ko-fi.com/M4Q624RYOV' || koFiTarget.url === 'https://ko-fi.com/M4Q624RYOV/');
    w.mapPageStillOpen = await evalJs(`document.querySelector('#map canvas') !== null && document.readyState === 'complete'`);
    koFi.widths[width] = w;
  }
  results.koFi = koFi;

  results.consoleErrors = consoleErrors;
  console.log(JSON.stringify(results, null, 2));
} catch (err) {
  console.error('smoke-verify failed:', err.message);
  process.exitCode = 1;
} finally {
  try { ws?.close(); } catch {}
  proc.kill('SIGKILL');
  setTimeout(() => rmSync(profile, { recursive: true, force: true }), 300);
}
