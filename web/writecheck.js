/* Mao: handwriting check against Make Me a Hanzi stroke medians (Arphic Public License).
   Coordinates: reference medians are stored in a 256 box, y downwards. User strokes come in 0..1. */
(function () {
  'use strict';
  let map = null, loading = null;
  function load() {
    if (map) return Promise.resolve(map);
    if (loading) return loading;
    loading = (window.MaoText ? MaoText('strokes.txt') : fetch('strokes.txt').then(r => { if (!r.ok) throw 0; return r.text(); })).then(t => {
      const m = new Map();
      for (const l of t.split('\n')) {
        const i = l.indexOf('\t'); if (i < 1) continue;
        m.set(l.slice(0, i), l.slice(i + 1));
      }
      map = m; return m;
    }).catch(() => { loading = null; map = new Map(); return map; });
    return loading;
  }
  function ref(ch) {
    if (!map) return null;
    const raw = map.get(ch); if (!raw) return null;
    return raw.split('|').map(s => s.split(' ').map(p => { const [x, y] = p.split(','); return [x / 256, y / 256]; }));
  }
  const len = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
  function resample(pts, n) {
    n = n || 32;
    if (pts.length === 1) return Array.from({ length: n }, () => pts[0]);
    let total = 0; for (let i = 1; i < pts.length; i++) total += len(pts[i - 1], pts[i]);
    if (total < 1e-6) return Array.from({ length: n }, () => pts[0]);
    const step = total / (n - 1), out = [pts[0]];
    let acc = 0, prev = pts[0], i = 1;
    while (out.length < n - 1 && i < pts.length) {
      const d = len(prev, pts[i]);
      if (acc + d >= step) {
        const t = (step - acc) / d; const p = [prev[0] + t * (pts[i][0] - prev[0]), prev[1] + t * (pts[i][1] - prev[1])];
        out.push(p); prev = p; acc = 0;
      } else { acc += d; prev = pts[i]; i++; }
    }
    while (out.length < n) out.push(pts[pts.length - 1]);
    return out;
  }
  function bbox(strokes) {
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const s of strokes) for (const p of s) { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]); }
    return { x0, y0, x1, y1, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, s: Math.max(x1 - x0, y1 - y0, 0.05) };
  }
  // fit strokes into a unit box by their own bounding box (shape comparison independent of size/position)
  function fit(strokes, b) { return strokes.map(s => s.map(p => [(p[0] - b.cx) / b.s + 0.5, (p[1] - b.cy) / b.s + 0.5])); }
  const mean = (a, b) => { let t = 0; for (let i = 0; i < a.length; i++) t += len(a[i], b[i]); return t / a.length; };
  const sc = d => Math.max(0, Math.min(1, 1 - (d - 0.05) / 0.22));

  // score one character: user strokes (0..1 within the character's cell) vs reference
  function scoreChar(ch, user, mode) {
    const R = ref(ch);
    if (!R) return { ch, ok: false, nodata: true };
    if (!user.length) return { ch, ok: true, score: 0, badUser: [], badRef: R.map((_, i) => i), ref: R, empty: true };
    const ub = bbox(user), rb = bbox(R);
    const U = fit(user, ub).map(s => resample(s)), F = fit(R, rb).map(s => resample(s));
    const strict = mode !== 'soft';
    const per = new Array(F.length).fill(0), userScore = new Array(U.length).fill(0), match = new Array(F.length).fill(-1);
    if (strict) {
      for (let k = 0; k < F.length; k++) if (k < U.length) { per[k] = sc(mean(U[k], F[k])); userScore[k] = per[k]; match[k] = k; }
    } else {
      const used = new Set();
      for (let k = 0; k < F.length; k++) {
        let best = -1, bs = 0;
        for (let j = 0; j < U.length; j++) {
          if (used.has(j)) continue;
          const s1 = sc(Math.min(mean(U[j], F[k]), mean(U[j].slice().reverse(), F[k])));
          if (s1 > bs) { bs = s1; best = j; }
        }
        if (best >= 0) { used.add(best); per[k] = bs; userScore[best] = bs; match[k] = best; }
      }
    }
    let score = 100 * per.reduce((a, b) => a + b, 0) / F.length;
    const diff = Math.abs(U.length - F.length);
    if (diff > 1) score -= (strict ? 12 : 6) * (diff - 1);
    // proportions: compare aspect ratio of the whole character
    const ua = (ub.x1 - ub.x0 + 0.02) / (ub.y1 - ub.y0 + 0.02), ra = (rb.x1 - rb.x0 + 0.02) / (rb.y1 - rb.y0 + 0.02);
    const ar = Math.abs(Math.log(ua / ra)); if (ar > 0.45) score -= Math.min(20, (ar - 0.45) * 30);
    score = Math.max(0, Math.min(100, Math.round(score)));
    const badRef = [], badUser = [];
    per.forEach((v, k) => { if (v < 0.55) badRef.push(k); });
    userScore.forEach((v, j) => { if (v < 0.55) badUser.push(j); });
    return { ch, ok: true, score, badRef, badUser, ref: R, nUser: U.length, nRef: F.length, match };
  }

  // chars: array of characters; groups: array (per char) of strokes arrays (0..1 inside that char's cell)
  function check(chars, groups, mode) {
    const per = chars.map((ch, i) => scoreChar(ch, groups[i] || [], mode));
    const scored = per.filter(p => p.ok && !p.nodata);
    if (!scored.length) return { nodata: true, per };
    const score = Math.round(scored.reduce((a, p) => a + p.score, 0) / scored.length);
    const verdict = score >= 75 ? 'ok' : score >= 50 ? 'close' : 'bad';
    return { score, verdict, per };
  }

  // split strokes drawn in one box into n cells (by stroke centre x inside the text layout area)
  function split(strokes, n, x0, w) {
    const cells = Array.from({ length: n }, () => []);
    for (const s of strokes) {
      const cx = s.reduce((a, p) => a + p[0], 0) / s.length;
      const k = Math.max(0, Math.min(n - 1, Math.floor((cx - x0) / (w / n))));
      cells[k].push(s.map(p => [(p[0] - (x0 + k * w / n)) / (w / n), p[1]]));
    }
    return cells;
  }

  // distance between one user stroke and one reference stroke, both in the same 0..1 box (no size normalisation)
  function strokeDist(user, refStroke, allowRev) {
    const U = resample(user), F = resample(refStroke);
    const d = mean(U, F); if (!allowRev) return d;
    return Math.min(d, mean(U.slice().reverse(), F));
  }
  // calligraphic stroke shapes (outlines) — what a correct stroke turns into, like in Laoshi / Hanzi Writer.
  // Stored in the 1024 box of Make Me a Hanzi with y up; the transform maps them into the 0..1 cell.
  let omap = null, oload = null; const pcache = new Map();
  function loadOutlines() {
    if (omap) return Promise.resolve(omap);
    if (oload) return oload;
    oload = (window.MaoText ? MaoText('outlines.txt') : fetch('outlines.txt').then(r => { if (!r.ok) throw 0; return r.text(); })).then(t => {
      const m = new Map(); let i = 0;
      while (i < t.length) { let j = t.indexOf('\n', i); if (j < 0) j = t.length; const k = t.indexOf('\t', i); if (k > i && k < j) m.set(t.slice(i, k), t.slice(k + 1, j)); i = j + 1; }
      omap = m; return m;
    }).catch(() => { oload = null; omap = new Map(); return omap; });
    return oload;
  }
  // Path2D list for a character in a canvas of W×H (cached)
  function paths(ch, W, H) {
    if (!omap || typeof Path2D === 'undefined') return null;
    const raw = omap.get(ch); if (!raw) return null;
    const key = ch + '|' + W + 'x' + H; if (pcache.has(key)) return pcache.get(key);
    let out = null;
    try {
      const M = new DOMMatrix([W / 1024, 0, 0, -H / 1024, 0, 900 * H / 1024]);
      out = raw.split('|').map(d => { const p = new Path2D(); p.addPath(new Path2D(d), M); return p; });
    } catch (e) { out = null; }
    if (pcache.size > 300) pcache.clear();
    pcache.set(key, out); return out;
  }
  window.WCheck = { load, ref, check, split, strokeDist, ready: () => !!map, has: ch => !!(map && map.has(ch)), loadOutlines, paths, outlinesReady: () => !!omap };
})();
