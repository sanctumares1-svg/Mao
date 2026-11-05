/* Mao: offline explanation of a character — parts, which part gives the meaning and which the sound,
   and words with this character. Decomposition data: Make Me a Hanzi (Arphic Public License). */
(function () {
  'use strict';
  let map = null, loading = null;
  // Russian names of common radicals and their side forms
  const RAD = {
    '氵': 'вода', '冫': 'лёд', '亻': 'человек', '人': 'человек', '口': 'рот', '囗': 'ограда', '木': 'дерево', '女': 'женщина', '扌': 'рука', '手': 'рука',
    '讠': 'речь', '言': 'речь', '艹': 'трава', '饣': 'еда', '食': 'еда', '宀': 'крыша', '心': 'сердце', '忄': 'сердце', '日': 'солнце', '月': 'луна / тело',
    '土': 'земля', '钅': 'металл', '金': 'металл', '火': 'огонь', '灬': 'огонь', '纟': 'нить', '糸': 'нить', '辶': 'движение', '门': 'дверь', '马': 'лошадь',
    '鸟': 'птица', '鱼': 'рыба', '犭': 'зверь', '疒': 'болезнь', '衤': 'одежда', '衣': 'одежда', '礻': 'алтарь', '示': 'алтарь', '目': 'глаз', '足': 'нога', '⻊': 'нога',
    '车': 'повозка', '贝': 'раковина / деньги', '页': 'голова', '雨': 'дождь', '竹': 'бамбук', '⺮': 'бамбук', '米': 'рис', '石': 'камень', '禾': 'злак', '力': 'сила',
    '刂': 'нож', '刀': 'нож', '阝': 'холм / город', '彳': 'шаг', '尸': 'тело', '广': 'навес', '厂': 'утёс', '攵': 'действие', '欠': 'зевать', '王': 'нефрит', '玉': 'нефрит',
    '田': 'поле', '虫': 'насекомое', '舌': 'язык', '耳': 'ухо', '走': 'идти', '酉': 'кувшин', '见': 'видеть', '大': 'большой', '小': 'маленький', '子': 'ребёнок',
    '山': 'гора', '水': 'вода', '工': 'работа', '巾': 'ткань', '弓': 'лук', '戈': 'алебарда', '方': 'сторона', '止': 'стоп', '白': 'белый', '皿': 'сосуд',
    '立': 'стоять', '穴': 'пещера', '羊': 'баран', '牛': 'бык', '牜': 'бык', '犬': 'собака', '夕': 'вечер', '寸': 'вершок', '又': 'рука', '十': 'десять',
    '八': 'восемь', '丷': 'восемь', '儿': 'ноги', '几': 'стол', '冖': 'покров', '亠': 'крышка', '卜': 'гадание', '厶': 'частный', '廴': 'шагать', '夂': 'идти',
    '彡': 'узор', '户': 'дверь', '斤': 'топор', '欠': 'зевать', '殳': 'оружие', '毛': 'шерсть', '气': 'пар', '片': 'щепка', '父': 'отец', '爫': 'когти',
    '生': 'жизнь', '用': 'польза', '矢': 'стрела', '老': 'старый', '耂': 'старый', '肉': 'мясо', '自': 'сам', '至': 'достигать', '色': 'цвет', '血': 'кровь',
    '行': 'идти', '角': 'рог', '谷': 'долина', '豆': 'боб', '身': 'тело', '辛': 'горький', '里': 'деревня', '青': 'синий', '非': 'не', '面': 'лицо',
    '音': 'звук', '风': 'ветер', '飞': 'летать', '首': 'голова', '香': 'аромат', '高': 'высокий', '黑': 'чёрный', '一': 'один', '丨': 'черта', '丿': 'откидная',
    '丶': 'точка', '乙': 'крюк', '亅': 'крючок', '二': 'два', '冂': 'рамка', '凵': 'яма', '勹': 'обёртка', '匕': 'ложка', '匚': 'ящик', '卩': 'печать',
    '⺈': 'нож', '⺊': 'гадание', '⺌': 'маленький', '⺍': 'маленький', '⺧': 'бык', '⺶': 'баран', '⺼': 'тело', '龵': 'рука', '罒': 'сеть', '覀': 'запад',
    '中': 'середина', '文': 'письмо', '火': 'огонь', '长': 'длинный', '东': 'восток', '西': 'запад'
  };
  function load() {
    if (map) return Promise.resolve(map);
    if (loading) return loading;
    loading = fetch('decomp.txt').then(r => { if (!r.ok) throw 0; return r.text(); }).then(t => {
      const m = new Map();
      for (const l of t.split('\n')) { const c = l.split('\t'); if (c[0]) m.set(c[0], { rad: c[1] || '', parts: [...(c[2] || '')], type: c[3] || '', ph: c[4] || '', se: c[5] || '' }); }
      map = m; return m;
    }).catch(() => { loading = null; map = new Map(); return map; });
    return loading;
  }
  const short = m => String(m || '').split(/[;,(]/)[0].trim().slice(0, 22);
  function ruOf(c) {
    if (RAD[c]) return RAD[c];
    const e = window.EDict && EDict.ready() && EDict.find(c);
    return e && e.m && /[а-яё]/i.test(e.m) ? short(e.m) : '';
  }
  function pyOf(c) { const e = window.EDict && EDict.ready() && EDict.find(c); return e && e.p ? e.p : ''; }
  const strip = p => String(p || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  // one line about one character: "饭 = 饣 «еда» + 反 «обратный» · смысл — от 饣, звучание — от 反 (fǎn)"
  function charLine(ch) {
    const d = map && map.get(ch); if (!d || !d.parts.length) return '';
    const parts = d.parts.map(c => c + (ruOf(c) ? ' «' + ruOf(c) + '»' : '')).join(' + ');
    let why = '';
    if (d.type === 's' && d.ph) { const pp = pyOf(d.ph), pc = pyOf(ch); why = ' · смысл — от ' + (d.se || d.rad) + ', звучание — от ' + d.ph + (pp ? ' (' + pp + (strip(pp) === strip(pc) ? ', так же' : '') + ')' : ''); }
    else if (d.type === 'i') why = ' · смысл складывается из частей';
    else if (d.type === 'p') why = ' · знак-рисунок';
    return ch + ' = ' + parts + why;
  }
  // short line for the learning card: "饣 еда + 反 обратный"
  function partsShort(h) {
    if (!map) return '';
    return [...new Set([...h])].filter(c => map.has(c)).map(c => { const d = map.get(c); return d.parts.length ? d.parts.map(x => x + (ruOf(x) ? ' ' + ruOf(x) : '')).join(' + ') : ''; }).filter(Boolean).join('  ·  ');
  }
  function text(w) {
    const lines = [w.h + ' ' + (w.p || '') + ' — «' + (w.m || '') + '»'];
    const chars = [...new Set([...w.h].filter(c => /[㐀-鿿]/.test(c)))];
    chars.forEach(c => { const l = charLine(c); if (l) lines.push(l); });
    chars.forEach(c => {
      const ex = window.EDict && EDict.ready() ? EDict.withChar(c, 3, w.h) : [];
      if (ex.length) lines.push('Слова с ' + c + ': ' + ex.map(e => e.h + ' ' + e.p + ' — ' + short(e.m)).join('; '));
    });
    if (chars.length === 1) { const d = map && map.get(chars[0]); if (d && d.rad && RAD[d.rad]) lines.push('Ключ (радикал): ' + d.rad + ' «' + RAD[d.rad] + '» — по нему знак ищут в словарях.'); }
    return lines.join('\n');
  }
  window.Explain = { load, ready: () => !!map, text, charLine, partsShort, ruOf };
})();
