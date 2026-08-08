#!/usr/bin/env node
// Perf probe: cold/warm load + interaction latency via CDP. Zero dependencies (Node >= 22, native WebSocket).
// Method follows validation/perf-budget.json: headless Chromium, CDP throttle, rAF probe.
// Usage: node scripts/perf-probe.mjs --url <url> --out <json> [--chrome /usr/bin/chromium] [--throttle 1]
import { spawn } from 'node:child_process';
import { writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const args = Object.fromEntries(process.argv.slice(2).map((a, i, arr) =>
  a.startsWith('--') ? [a.slice(2), arr[i + 1] ?? true] : null).filter(Boolean));
const url = args.url;
if (!url) { console.error('usage: --url <url> [--out <json>] [--chrome <path>] [--throttle 0|1]'); process.exit(2); }
const chrome = args.chrome ?? '/usr/bin/chromium';
const out = args.out;
const throttle = args.throttle !== '0';
const port = 9300 + Math.floor(Math.random() * 500);
const profile = mkdtempSync(join(tmpdir(), 'perf-probe-'));

const proc = spawn(chrome, [
  '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
  '--disk-cache-size=536870912', '--disk-cache-dir=' + profile + '/cache',
  `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const idRef = { id: 0 };

async function cdp(ws, method, params = {}) {
  const id = ++idRef.id;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => {
    const onMsg = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id === id) {
        ws.removeEventListener('message', onMsg);
        msg.error ? reject(new Error(`${method}: ${msg.error.message}`)) : resolve(msg.result);
      }
    };
    ws.addEventListener('message', onMsg);
  });
}

let ws;
try {
  // wait for the debugger endpoint
  let version;
  for (let i = 0; i < 50; i++) {
    try {
      version = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
      break;
    } catch { await sleep(200); }
  }
  if (!version) throw new Error('chromium debugger did not start');
  ws = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

  // page target
  const { targetId } = await cdp(ws, 'Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await cdp(ws, 'Target.attachToTarget', { targetId, flatten: true });
  const pageWs = ws; // single connection, flatten:true routes via sessionId in every message
  const sendPage = async (method, params = {}) => {
    const id = ++idRef.id;
    pageWs.send(JSON.stringify({ id, sessionId, method, params }));
    return new Promise((resolve, reject) => {
      const onMsg = (ev) => {
        const msg = JSON.parse(ev.data);
        if (msg.id === id) { pageWs.removeEventListener('message', onMsg); msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result); }
      };
      pageWs.addEventListener('message', onMsg);
    });
  };

  await sendPage('Page.enable');
  await sendPage('Network.enable');
  if (throttle) {
    await sendPage('Emulation.setCPUThrottlingRate', { rate: 4 });
    await sendPage('Network.emulateNetworkConditions', {
      offline: false, latency: 150,
      downloadThroughput: 200000, uploadThroughput: 100000,
    });
  } else {
    await sendPage('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  }
  // LCP/CLS observers installed before any navigation
  await sendPage('Page.addScriptToEvaluateOnNewDocument', { source: `
    window.__perf = { lcp: [], cls: 0, inps: [] };
    try { new PerformanceObserver(l => { for (const e of l.getEntries()) window.__perf.lcp.push(e.startTime); }).observe({ type: 'largest-contentful-paint', buffered: true }); } catch {}
    try { new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__perf.cls += e.value; }).observe({ type: 'layout-shift', buffered: true }); } catch {}
    try { new PerformanceObserver(l => { for (const e of l.getEntries()) if (e.interactionId) window.__perf.inps.push(e.duration); }).observe({ type: 'event', buffered: true }); } catch {}
  ` });

  const evalJs = async (expr) => (await sendPage('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result.value;

  const load = async () => {
    await sendPage('Page.navigate', { url });
    await new Promise((resolve) => {
      const onMsg = (ev) => {
        const msg = JSON.parse(ev.data);
        if (msg.method === 'Page.loadEventFired' && msg.sessionId === sessionId) {
          pageWs.removeEventListener('message', onMsg);
          resolve();
        }
      };
      pageWs.addEventListener('message', onMsg);
    });
    await sleep(4000);
    return evalJs(`(() => {
      const nav = performance.getEntriesByType('navigation')[0];
      const res = [...performance.getEntriesByType('resource')];
      const host = new URL(location.href).host;
      const same = res.filter(e => { try { return new URL(e.name).host === host; } catch { return false; } });
      return {
        ttfb_ms: Math.round(nav.responseStart),
        fcp_ms: Math.round((performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime || 0),
        lcp_ms: Math.round(window.__perf.lcp.length ? window.__perf.lcp[window.__perf.lcp.length - 1] : 0),
        cls: +window.__perf.cls.toFixed(3),
        load_ms: Math.round(nav.loadEventEnd),
        sameOriginKB: Math.round(same.reduce((s, e) => s + (e.transferSize || 0), 0) / 1024),
        requests: same.length,
        canvas: !!document.querySelector('#map canvas')
      };
    })()`);
  };

  await sendPage('Network.setCacheDisabled', { cacheDisabled: false });
  await sendPage('Network.clearBrowserCache');
  const cold = await load();
  await sleep(1000);
  const warm = await load();

  // interactions: real CDP input (trusted events produce INP interactionIds), rAF probe
  const realClick = async (selector) => {
    const rect = await evalJs(`(() => { const el = document.querySelector(${JSON.stringify(selector)}); if (!el) return null; const r = el.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; })()`);
    if (!rect) return null;
    await evalJs(`window.__t0 = performance.now()`);
    await sendPage('Input.dispatchMouseEvent', { type: 'mousePressed', x: rect.x, y: rect.y, button: 'left', clickCount: 1 });
    await sendPage('Input.dispatchMouseEvent', { type: 'mouseReleased', x: rect.x, y: rect.y, button: 'left', clickCount: 1 });
    return evalJs(`new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(Math.round(performance.now() - window.__t0)))))`);
  };
  const clickMapAt = async (fx, fy) => {
    const rect = await evalJs(`(() => { const m = document.getElementById('map'); const r = m.getBoundingClientRect(); return { x: r.x + r.width * ${fx}, y: r.y + r.height * ${fy} }; })()`);
    await evalJs(`window.__t0 = performance.now()`);
    await sendPage('Input.dispatchMouseEvent', { type: 'mousePressed', x: rect.x, y: rect.y, button: 'left', clickCount: 1 });
    await sendPage('Input.dispatchMouseEvent', { type: 'mouseReleased', x: rect.x, y: rect.y, button: 'left', clickCount: 1 });
    return evalJs(`new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(Math.round(performance.now() - window.__t0)))))`);
  };

  const interactions = {};
  // SC-005 method: click dispatch to effect settle, 5 runs each, median reported
  const med = (vals) => { const s = [...vals].sort((a, b) => a - b); return s[Math.floor(s.length / 2)]; };
  for (const [key, fn] of Object.entries({
    zoom_in: () => realClick('.maplibregl-ctrl-zoom-in'),
    zoom_out: () => realClick('.maplibregl-ctrl-zoom-out'),
    trees_toggle: () => realClick('#baeume'),
    popup: () => clickMapAt(0.5, 0.5),
    surface_toggle: () => realClick('#surface-toggle'),
  })) {
    const runs = [];
    for (let i = 0; i < 5; i++) {
      const t = await fn();
      if (t !== null) runs.push(t);
      await sleep(250);
    }
    interactions[key] = { runs, median_ms: runs.length ? med(runs) : null };
  }
  await sleep(400);
  const popupSettled = await evalJs(`(() => { const p = document.querySelector('.maplibregl-popup'); if (p) { p.querySelector('.maplibregl-popup-close-button')?.click(); return true; } return false; })()`);
  const inps = await evalJs(`window.__perf.inps.length ? Math.round(Math.max(...window.__perf.inps)) : null`);
  const result = { url, chrome, throttle, cold, warm, interactions, popup_settled: popupSettled, inp_worst_ms: inps, captured_at: new Date().toISOString() };
  if (out) writeFileSync(out, JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result, null, 2));
} catch (err) {
  console.error('perf-probe failed:', err.message);
  process.exitCode = 1;
} finally {
  try { ws?.close(); } catch {}
  proc.kill('SIGKILL');
  setTimeout(() => rmSync(profile, { recursive: true, force: true }), 500);
}
