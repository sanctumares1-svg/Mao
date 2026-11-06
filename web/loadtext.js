/* Mao: reads big text files off the main thread (decoding 10+ MB of UTF-8 blocks the screen for a few hundred ms).
   Usage: window.MaoText(url) -> Promise<string>. Falls back to a normal fetch if workers are not available. */
(function () {
  'use strict';
  let w = null, seq = 0; const wait = new Map();
  try {
    w = new Worker('loadtext-worker.js');
    w.onmessage = e => { const p = wait.get(e.data.id); if (!p) return; wait.delete(e.data.id); clearTimeout(p.t); e.data.ok ? p.res(e.data.text) : p.fall(); };
    w.onerror = () => { w = null; wait.forEach(p => { clearTimeout(p.t); p.fall(); }); wait.clear(); };
  } catch (e) { w = null; }
  const direct = url => fetch(url).then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); });
  window.MaoText = url => {
    if (!w) return direct(url);
    return new Promise((res, rej) => {
      const id = ++seq;
      const fall = () => direct(url).then(res, rej);
      // a worker that cannot reach the file (some WebViews) — read it the usual way
      wait.set(id, { res, fall, t: setTimeout(() => { if (wait.delete(id)) fall(); }, 6000) });
      w.postMessage({ id, url: new URL(url, location.href).href });
    });
  };
})();
