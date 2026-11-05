/* EVINE dictionary: CC-CEDICT (CC BY-SA 4.0, MDBG) + Russian for HSK 3.0 levels 1–3 */
(function () {
  'use strict';
  const TONES = { a: 'āáǎà', e: 'ēéěè', i: 'īíǐì', o: 'ōóǒò', u: 'ūúǔù', 'ü': 'ǖǘǚǜ' };
  const MARK = {};
  for (const b in TONES) [...TONES[b]].forEach((c, i) => { MARK[c] = [b, i + 1]; });

  function numToMarks(s) {
    return s.replace(/([a-zA-ZüÜ:]+?)([1-5])/g, (m, syl, t) => {
      syl = syl.replace(/u:|v/g, 'ü');
      if (t === '5') return syl;
      const k = +t - 1, low = syl.toLowerCase();
      let i = low.search(/[ae]/);
      if (i < 0) i = low.indexOf('ou');
      if (i < 0) for (let j = low.length - 1; j >= 0; j--) if ('iouü'.includes(low[j])) { i = j; break; }
      if (i < 0) return syl;
      return syl.slice(0, i) + TONES[low[i]][k] + syl.slice(i + 1);
    });
  }
  // CEDICT "jie3 jie5" -> "jiějie": syllables of one word are written together, as in textbooks.
  // An apostrophe separates a syllable that starts with a, o, e: "Xi1 an1" -> "Xī'ān".
  function displayPy(n) {
    let out = '';
    for (const tk of n.replace(/u:/g, 'v').split(/\s+/).filter(Boolean)) {
      if (/^[,·，]$/.test(tk)) { out = out.replace(/\s+$/, '') + tk + ' '; continue; }
      let m = numToMarks(tk);
      if (out && !/\s$/.test(out) && /^[aoeāáǎàōóǒòēéěè]/i.test(m)) m = "'" + m;
      out += m;
    }
    return out.trim();
  }
  // marked pinyin -> numbered without spaces (no tone 5), plain, tone digits
  function markedKeys(p) {
    let num = '', tones = '';
    const parts = p.toLowerCase().replace(/['’\-]/g, ' ').split(/\s+/).filter(Boolean);
    for (const part of parts) {
      let out = '', t = 0;
      for (const ch of part) { if (MARK[ch]) { out += MARK[ch][0]; t = MARK[ch][1]; } else out += ch; }
      out = out.replace(/ü/g, 'v');
      num += out + (t || ''); tones += t || '';
    }
    return { num, plain: num.replace(/\d/g, ''), tones };
  }
  const stripMarks = s => s.toLowerCase().replace(/[ǖǘǚǜü]/g, 'v').normalize('NFD').replace(/[\u0300-\u036f]/g, '');

  let rows = [], state = 'loading';
  const listeners = [];
  let RUC = {};
  try { RUC = JSON.parse(localStorage.getItem('evine-ruc') || '{}') || {}; } catch (e) { RUC = {}; }
  const saveRuc = () => { try { localStorage.setItem('evine-ruc', JSON.stringify(RUC)); } catch (e) {} };

  function parse(txt) {
    const out = [], freq = new Map();
    const lines = txt.split('\n');
    for (const l of lines) {
      if (!l) continue;
      const c = l.split('\t');
      const e = { h: c[0], t: c[1] || '', n: c[2] || '', en: c[3] || '', ru: c[4] || '', lv: +(c[5] || 0) };
      // Russian was attached to a surname entry ("San1", "Yu2"): the word itself is written in lower case.
      // Real names (Китай, Пекин) and languages (китайский язык) keep the capital letter.
      if (e.ru && /^[A-Z]/.test(e.n) && /^[а-яё]/.test(e.ru) && !/язык/.test(e.ru)) e.n = e.n.toLowerCase();
      if (e.n.charAt(0) === '=') { e.p = e.n.slice(1); const k = markedKeys(e.p); e.num = k.num; e.plain = k.plain; e.tones = k.tones; }
      else {
        const sy = e.n.toLowerCase().split(' ');
        e.num = sy.join('').replace(/u:/g, 'v').replace(/5/g, '');
        e.plain = e.num.replace(/\d/g, '');
        e.tones = sy.map(s => (s.match(/[1-4]$/) || [''])[0]).join('');
      }
      e.key = e.h + '|' + e.num;
      e.len = [...e.h].length;
      out.push(e);
      for (const ch of e.h) freq.set(ch, (freq.get(ch) || 0) + 1);
    }
    for (const e of out) { let m = 1e9; for (const ch of e.h) m = Math.min(m, freq.get(ch) || 0); e.f = m; }
    return out;
  }

  function load() {
    fetch('dict.txt').then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); })
      .then(txt => { rows = parse(txt); state = 'ready'; listeners.splice(0).forEach(f => { try { f(); } catch (e) {} }); })
      .catch(() => { state = 'error'; listeners.splice(0).forEach(f => { try { f(); } catch (e) {} }); });
  }

  const shortEn = en => { let t = en.split(';').map(x => x.trim()).filter(x => !/[\u3400-\u9fff]/.test(x)).slice(0, 3).join('; '); if (t.length > 90) t = t.slice(0, 88).replace(/[ ,;]+[^ ,;]*$/, '') + '…'; return t; };
  const ruOf = e => e.ru || RUC[e.key] || '';
  const rank = (exact) => (a, b) => (exact(b) - exact(a)) || ((b.lv ? 1 : 0) - (a.lv ? 1 : 0)) || ((ruOf(b) ? 1 : 0) - (ruOf(a) ? 1 : 0)) || (a.len - b.len) || (b.f - a.f);

  function search(q, limit) {
    limit = limit || 30; q = (q || '').trim(); if (!q || !rows.length) return [];
    const lq = q.toLowerCase(); let res = [];
    if (/[\u3400-\u9fff]/.test(q)) {
      res = rows.filter(e => e.h.includes(q) || (e.t && e.t.includes(q)));
      res.sort(rank(e => e.h === q || e.t === q ? 2 : e.h.startsWith(q) ? 1 : 0));
    } else if (/[а-яё]/i.test(q)) {
      const hit = e => { const r = ruOf(e); if (!r) return 0; const low = r.toLowerCase(); const parts = low.split(/[;,()]\s*/).map(s => s.trim()); return parts.includes(lq) ? 3 : parts.some(p => p.startsWith(lq)) ? 2 : low.includes(lq) ? 1 : 0; };
      res = rows.filter(e => hit(e) > 0);
      res.sort((a, b) => hit(b) - hit(a) || (b.lv ? 1 : 0) - (a.lv ? 1 : 0) || a.len - b.len || b.f - a.f);
    } else {
      const raw = lq.replace(/[\s'’]/g, '');
      if (/\d/.test(raw)) {
        const k = raw.replace(/ü|u:/g, 'v').replace(/5/g, '');
        res = rows.filter(e => e.num.startsWith(k));
        res.sort(rank(e => e.num === k ? 1 : 0));
      } else {
        const marked = /[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]/.test(raw);
        const k = stripMarks(raw);
        const tq = marked ? [...raw].map(c => MARK[c] ? MARK[c][1] : '').join('') : '';
        res = rows.filter(e => e.plain.startsWith(k) && (!tq || e.tones.startsWith(tq)));
        res.sort(rank(e => e.plain === k ? 1 : 0));
      }
      res = res.slice(0, limit);
      if (/^[a-z][a-z \-']{2,}$/.test(lq) && res.length < limit) {
        const rx = new RegExp('(^|[^a-z])' + lq.replace(/[-']/g, '\\$&') + '([^a-z]|$)');
        const en = rows.filter(e => !res.includes(e) && rx.test(e.en.toLowerCase()));
        en.sort((a, b) => (a.en.toLowerCase().startsWith(lq) ? 0 : 1) - (b.en.toLowerCase().startsWith(lq) ? 0 : 1) || (b.lv ? 1 : 0) - (a.lv ? 1 : 0) || a.len - b.len || b.f - a.f);
        res = res.concat(en.slice(0, limit - res.length));
      }
    }
    return res.slice(0, limit).map(e => ({ h: e.h, t: e.t && e.t !== e.h ? e.t : '', p: e.p || displayPy(e.n), m: ruOf(e), en: shortEn(e.en), hsk: e.lv > 0, lv: e.lv, key: e.key }));
  }

  // background Russian translation of English-only entries through Claude (needs API key)
  const pending = new Set(), tried = new Set(), failed = new Set(); let queue = [], timer = null; const cbs = [];
  // ---- fast lookup for lists: by characters and by toneless pinyin ----
  let byH = null, byP = null;
  function index() {
    if (byH) return;
    byH = new Map(); byP = new Map();
    const add = (m, k, e) => { const a = m.get(k); if (a) a.push(e); else m.set(k, [e]); };
    for (const e of rows) { add(byH, e.h, e); if (e.t && e.t !== e.h) add(byH, e.t, e); add(byP, e.plain, e); }
  }
  let hskPool = null;
  const STOP = new Set(['про', 'для', 'тему', 'теме', 'тема', 'слова', 'слов', 'слово', 'подбери', 'подбор', 'дай', 'мне', 'как', 'что', 'это', 'по', 'на', 'или', 'все', 'весь']);
  const outE = e => out(e);
  const out = e => ({ h: e.h, t: e.t && e.t !== e.h ? e.t : '', p: e.p || displayPy(e.n), m: ruOf(e), en: shortEn(e.en), hsk: e.lv > 0, lv: e.lv, key: e.key });
  const lvR = e => e.lv > 0 ? e.lv : 9;
  const low = e => (/^[A-Z]/.test(e.n) ? 1 : 0);
  function bestRows(q) {
    q = String(q || '').trim(); if (!q || state !== 'ready') return [];
    index();
    if (/[\u3400-\u9fff]/.test(q)) {
      const c = (byH.get(q) || []).slice();
      c.sort((a, b) => (lvR(a) - lvR(b)) || ((ruOf(b) ? 1 : 0) - (ruOf(a) ? 1 : 0)) || (low(a) - low(b)) || ((a.h === q ? 0 : 1) - (b.h === q ? 0 : 1)));
      return c;
    }
    let tones = null, plain;
    const raw = q.toLowerCase().replace(/['’\-\s]/g, '');
    if (/\d/.test(raw)) { plain = raw.replace(/u:/g, 'v').replace(/ü/g, 'v').replace(/\d/g, ''); tones = (raw.match(/[1-4]/g) || []).join(''); }
    else if (/[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]/.test(raw)) { const k = markedKeys(q); plain = k.plain; tones = k.tones; }
    else plain = stripMarks(raw);
    if (!/^[a-zv]+$/.test(plain)) return [];
    let c = (byP.get(plain) || []);
    if (tones !== null) c = c.filter(e => e.tones === tones);
    c = c.slice();
    c.sort((a, b) => (lvR(a) - lvR(b)) || ((ruOf(b) ? 1 : 0) - (ruOf(a) ? 1 : 0)) || (low(a) - low(b)) || (b.f - a.f) || (a.len - b.len));
    return c;
  }

  function translate(items, cb) {
    if (cb) cbs.push(cb);
    for (const it of items) if (it.key && !RUC[it.key] && !pending.has(it.key) && !tried.has(it.key) && !queue.some(x => x.key === it.key)) queue.push(it);
    clearTimeout(timer);
    timer = setTimeout(flush, 600);
  }
  function flush() {
    const c = window.claude; if (!c || !c.complete || !(c.hasKey && c.hasKey())) { queue = []; return; }
    const batch = queue.splice(0, 12); if (!batch.length) return;
    batch.forEach(x => { pending.add(x.key); tried.add(x.key); });
    const list = batch.map((x, i) => i + '. ' + x.h + ' (' + x.p + '): ' + x.en).join('\n');
    const prompt = 'Переведи на русский язык китайские слова для словаря ученика. Дай краткий перевод ТОЛЬКО по-русски (кириллицей): 1–3 основных значения через «; », без пояснений и без английских слов.\n' + list + '\nОтветь только JSON-массивом строк в том же порядке, длиной ' + batch.length + '.';
    c.complete(prompt).then(txt => {
      let arr = null; try { arr = JSON.parse(String(txt).match(/\[[\s\S]*\]/)[0]); } catch (e) {}
      batch.forEach((x, i) => { pending.delete(x.key); const r = arr && typeof arr[i] === 'string' ? arr[i].trim() : ''; if (r && /[а-яё]/i.test(r)) RUC[x.key] = r; else failed.add(x.key); });
      saveRuc(); cbs.splice(0).forEach(f => { try { f(); } catch (e) {} });
      if (queue.length) flush();
    }).catch(() => { batch.forEach(x => { pending.delete(x.key); failed.add(x.key); }); cbs.splice(0).forEach(f => { try { f(); } catch (e) {} }); });
  }

  let TOP = null;
  fetch('topics.txt').then(r => r.ok ? r.text() : '').then(t => { TOP = {}; t.split('\n').forEach(l => { const i = l.indexOf('='); if (i > 0) TOP[l.slice(0, i).trim().toLowerCase()] = l.slice(i + 1).trim().split(/\s+/).filter(Boolean); }); }).catch(() => { TOP = {}; });
  window.EDict = {
    topic: name => (TOP && TOP[(name || '').trim().toLowerCase()]) || [],
    failed: key => failed.has(key),
    retry: () => { tried.clear(); failed.clear(); },
    load, search, translate, numToMarks,
    ready: () => state === 'ready', state: () => state, count: () => rows.length,
    onReady: f => { if (state !== 'loading') f(); else listeners.push(f); },
    ru: key => RUC[key] || '', pending: key => pending.has(key) || queue.some(x => x.key === key),
    find: h => { const e = bestRows(h)[0]; return e && (e.h === h || e.t === h) ? out(e) : null; },
    // one entry of a pasted list -> dictionary matches, best first (characters or pinyin with/without tones)
    best: q => bestRows(q).slice(0, 6).map(out),
    py: displayPy,
    // ---- offline helpers (Mao 2.8) ----
    // words that contain a character: HSK first, short first
    withChar: (ch, n, except) => { if (state !== 'ready') return []; index(); const out = []; for (const e of rows) { if (e.h.indexOf(ch) < 0 || e.h === except || !ruOf(e)) continue; out.push(e); } out.sort((a, b) => (lvR(a) - lvR(b)) || (a.len - b.len) || (b.f - a.f)); const seen = new Set(); return out.filter(e => !seen.has(e.h) && seen.add(e.h)).slice(0, n || 4).map(outE); },
    // words by a Russian word or topic ("еда", "кошка", "на работе"): match the beginning of words in the translation
    byRu: (q, n) => { if (state !== 'ready') return []; const stems = String(q || '').toLowerCase().replace(/ё/g, 'е').split(/[^а-я]+/).filter(t => t.length >= 3 && !STOP.has(t)).map(t => t.length >= 7 ? t.slice(0, t.length - 2) : t.length >= 5 ? t.slice(0, t.length - 1) : t);
      if (!stems.length) return [];
      const full = String(q || '').toLowerCase().replace(/ё/g, 'е').split(/[^а-я]+/).filter(t => t.length >= 3 && !STOP.has(t));
      // first the whole words ("семья"), then shorter stems ("работ" for «работать, работа»)
      const whole = new RegExp('(^|[^а-я])(' + full.join('|') + ')([^а-я]|$)', 'i');
      const pass = list => { const re = new RegExp('(^|[^а-я])(' + list.join('|') + ')', 'i'); const o = []; for (const e of rows) { const r = ruOf(e); if (r && re.test(r.toLowerCase().replace(/ё/g, 'е'))) o.push(e); } const w = e => whole.test(ruOf(e).toLowerCase().replace(/ё/g, 'е')) ? 0 : 1; o.sort((a, b) => (w(a) - w(b)) || (lvR(a) - lvR(b)) || (a.len - b.len) || (b.f - a.f)); return o; };
      const out = [...pass(full), ...pass(stems)];
      const seen = new Set(); return out.filter(e => !seen.has(e.h) && seen.add(e.h)).slice(0, n || 20).map(outE); },
    // random HSK words of a given length (for answer choices)
    sample: (n, len) => { if (state !== 'ready') return []; if (!hskPool) hskPool = rows.filter(e => e.lv > 0 && ruOf(e)); let p = hskPool.filter(e => !len || e.len === len); if (p.length < n) p = hskPool; const out = []; for (let i = 0; i < n * 3 && out.length < n; i++) { const e = p[Math.floor(Math.random() * p.length)]; if (!out.includes(e)) out.push(e); } return out.map(outE); },
    isHsk: h => rows.some(x => x.h === h && x.lv > 0)
  };
  load();
})();
