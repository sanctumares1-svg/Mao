/* EVINE: bridge between the web UI and the Android shell (EvineNative). Safe to load in a browser without it. */
(function () {
  'use strict';
  const N = window.EvineNative || null;
  window.EVINE = { native: !!N };

  // --- Theme: follow the phone's dark mode reported by Android ---
  if (N && N.isDark) {
    const orig = window.matchMedia ? window.matchMedia.bind(window) : null;
    const L = [];
    let dark = !!N.isDark();
    window.matchMedia = function (q) {
      if (/prefers-color-scheme\s*:\s*dark/.test(q)) {
        return { get matches() { return dark; }, media: q, onchange: null,
          addEventListener: (e, f) => L.push(f), removeEventListener: (e, f) => { const i = L.indexOf(f); if (i >= 0) L.splice(i, 1); },
          addListener: f => L.push(f), removeListener: f => { const i = L.indexOf(f); if (i >= 0) L.splice(i, 1); } };
      }
      return orig ? orig(q) : { matches: false, addEventListener() {}, removeEventListener() {} };
    };
    window.__evineDark = function (d) { dark = !!d; L.slice().forEach(f => { try { f({ matches: dark }); } catch (e) {} }); };
  }

  // --- Free AI through the Android shell (no keys) ---
  if (N && N.claude) {
    let seq = 0; const P = {};
    window.__claudeDone = function (id, ok, text) { const p = P[id]; if (!p) return; delete P[id]; ok ? p.res(text) : p.rej(new Error(text || 'error')); };
    window.claude = {
      hasKey: () => true, // Mao 2.2: free AI, no keys
      complete: prompt => new Promise((res, rej) => {
        if (!window.claude.hasKey()) return rej(new Error('no key'));
        const id = 'c' + (++seq); P[id] = { res, rej };
        try { N.claude(id, String(prompt)); } catch (e) { delete P[id]; rej(e); }
      })
    };
  }

  // --- Files: export/import backup through the system file picker ---
  window.__fileOpened = function (txt) { const f = window.__fileCb; window.__fileCb = null; f && f(txt); };
  window.__fileSaved = function (ok) { const a = window.__app; if (a && a.toast) a.toast(ok ? 'Копия сохранена' : 'Файл не сохранён'); };
  window.EVINE.saveFile = function (name, text) {
    if (N && N.saveFile) { N.saveFile(name, text); return true; }
    try { const b = new Blob([text], { type: 'application/json' }); const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = name; a.click(); return true; } catch (e) { return false; }
  };
  window.EVINE.openFile = function (cb) {
    if (N && N.openFile) { window.__fileCb = cb; N.openFile(); return true; }
    return false;
  };

  // --- Speech ---
  window.EVINE.speak = function (text, rate, voice) {
    if (N && N.speak) { const ok = N.speak(String(text), Number(rate) || 0.8, voice || 'f'); if (!ok) { const a = window.__app; a && a.toast && a.toast('Нет китайского голоса. Установите его в настройках телефона: Язык → Синтез речи'); } return true; }
    return false;
  };

  // --- Start-up: Android keeps the page hidden behind the cat splash until the first screen is drawn and fonts are loaded ---
  if (N && N.ready) {
    const t0 = Date.now();
    const done = () => requestAnimationFrame(() => requestAnimationFrame(() => {
      try { const el = document.querySelector('[data-th]'); if (el && N.setBars) N.setBars(getComputedStyle(el).getPropertyValue('--bg').trim() || '#F5F5F8', el.getAttribute('data-th') === 'd'); } catch (e) {}
      try { N.ready(); } catch (e) {}
    }));
    const tick = () => {
      const el = document.querySelector('[data-th]');
      if (el && el.querySelector('button')) {
        const f = document.fonts && document.fonts.ready;
        if (f) Promise.race([f, new Promise(r => setTimeout(r, 2500))]).then(done); else done();
      } else if (Date.now() - t0 < 8000) setTimeout(tick, 40);
      else done();
    };
    tick();
  }

  // --- Updates from GitHub: Android calls this; the app shows a banner (or keeps it until the app is up) ---
  window.__evineUpdate = function (u) { const a = window.__app; if (a && a.onUpdate) a.onUpdate(u); else (window.__updQ = window.__updQ || []).push(u); };

  // --- System bars follow the app background ---
  if (N && N.setBars) {
    let last = '';
    setInterval(function () {
      const el = document.querySelector('[data-th]'); if (!el) return;
      const bg = getComputedStyle(el).getPropertyValue('--bg').trim(); const th = el.getAttribute('data-th');
      const k = bg + th; if (bg && k !== last) { last = k; try { N.setBars(bg, th === 'd'); } catch (e) {} }
    }, 400);
  }

  // --- Android back button (Mao screens) ---
  window.__evineBack = function () {
    const a = window.__app; if (!a) return false;
    const s = a.state;
    if (s.toast && s.toast.act) { a.setState({ toast: null }); }
    if (s.sheet) { a.setState({ sheet: null, resetAsk: false }); return true; }
    if (s.screen === 'goal') { if (!s.onboarded) return false; a.setState({ screen: 'tab', gd: null }); return true; }
    if (s.screen === 'quiz' || s.screen === 'learn' || s.screen === 'mc') { a.exit(); return true; }
    if (s.screen === 'result') { a.goTab('home'); return true; }
    if (s.screen === 'add' && s.addFrom === 'dayEdit' && s.de) { a.setState({ screen: 'dayEdit' }); return true; }
    if (s.screen === 'dayEdit') { a.setState({ screen: 'tab', tab: 'words', de: null }); return true; }
    if (s.screen !== 'tab') { a.setState({ screen: 'tab' }); return true; }
    if (s.q) { a.setState({ q: '' }); return true; }
    if (s.tab !== 'home') { a.goTab('home'); return true; }
    return false;
  };

})();
