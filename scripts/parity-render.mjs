#!/usr/bin/env node
// Rendered parity check (feature 014, T010/T011): measures how many buildings
// render at the initial view and at fixed zooms, samples properties, and
// captures screenshots. Runs against a bundle served on 127.0.0.1:8088.
// The --archive pmtiles is copied over dist/buildings.pmtiles before each run,
// so current and rebuilt archives are compared through the same bundle.
// Usage: node scripts/parity-render.mjs --archive <pmtiles> --out <dir> [--chrome /usr/bin/chromium]
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, copyFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const args = Object.fromEntries(process.argv.slice(2).map((a, i, arr) =>
  a.startsWith('--') ? [a.slice(2), arr[i + 1] ?? true] : null).filter(Boolean));
const archive = args.archive;
if (!archive) { console.error('usage: --archive <pmtiles> --out <dir> [--chrome <path>]'); process.exit(2); }
const chrome = args.chrome ?? '/usr/bin/chromium';
const outDir = args.out;
const URL = 'http://127.0.0.1:8088/';
const DIST_PMTILES = '/home/mainuser/Desktop/MATreeCover/dist/buildings.pmtiles';

copyFileSync(archive, DIST_PMTILES);

const port = 9900 + Math.floor(Math.random() * 90);
const profile = mkdtempSync(join(tmpdir(), 'parity-'));
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
  await send('Page.addScriptToEvaluateOnNewDocument', { source: `window.__parity = { mapReady: false };` });

  const evalJs = async (expr) => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result.value;

  await send('Page.navigate', { url: URL });
  await new Promise((resolve) => {
    const onMsg = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.method === 'Page.loadEventFired' && msg.sessionId === sessionId) { ws.removeEventListener('message', onMsg); resolve(); }
    };
    ws.addEventListener('message', onMsg);
  });
  await sleep(5000);
  // dismiss story modal if present, wait for the map
  await evalJs(`document.querySelector('#story-close')?.click(); true`);
  await evalJs(`new Promise(r => { const m = window.__map; if (!m) return r(false); if (m.loaded()) return r(true); m.once('idle', () => r(true)); })`);
  await sleep(2000);

  mkdirSync(outDir, { recursive: true });
  const results = {};
  const zooms = [null, 12, 14, 16, 18]; // null = initial camera
  for (const z of zooms) {
    const label = z === null ? 'initial' : `z${z}`;
    if (z !== null) {
      await evalJs(`window.__map.setZoom(${z}); true`);
      await sleep(4500);
    }
    const stats = await evalJs(`(() => {
      const m = window.__map;
      const feats = m.queryRenderedFeatures({ layers: ['buildings-fill'] });
      const sample = feats.slice(0, 50).map(f => ({ v: f.properties.value, h: f.properties.has_value }));
      return { count: feats.length, sample };
    })()`);
    results[label] = { count: stats.count, propertySampleOk: stats.sample.every(s => s.h === true && typeof s.v === 'number') };
    const shot = await send('Page.captureScreenshot', { format: 'png' });
    writeFileSync(join(outDir, `${label}.png`), Buffer.from(shot.data, 'base64'));
    console.log(`${label}: buildings=${stats.count}`);
  }
  if (outDir) writeFileSync(join(outDir, 'parity.json'), JSON.stringify(results, null, 2) + '\n');
} catch (err) {
  console.error('parity-render failed:', err.message);
  process.exitCode = 1;
} finally {
  try { ws?.close(); } catch {}
  proc.kill('SIGKILL');
  setTimeout(() => rmSync(profile, { recursive: true, force: true }), 300);
}
