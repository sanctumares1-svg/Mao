#!/usr/bin/env python3
"""Mao dictionary build: CC-CEDICT index + Russian from 大БКРС (bkrs.info).

Inputs (tools/src/):
  dict_base.txt   — the CC-CEDICT index Mao used before (h, trad, pinyin, en, ru-manual, hsk-flag)
  hsk-words.txt   — HSK 2.0/3.0 words with their lowest level (1–6)
  bkrs/e/*.json   — 大БКРС entries [h, pinyin, text, extra?] (from the daily dump, converted to JSON)

Outputs (www/):
  dict.txt        — one line per CEDICT reading: h, trad, pinyin, en, ru-short, hsk, src, cl
                    src: m = Mao's checked HSK translation, b = БКРС, '' = no Russian
  ru/NNN.json     — БКРС details for the word card, loaded only when a card is opened:
                    {h: {p, b: [{y: reading, pos, s: [senses], x: [[zh, py, ru], ...]}]}}
  dictver.txt     — version of the data

Rules: only Russian that is in БКРС or checked by hand; machine translations from the
JSON conversion ("m" extra) and auto pinyin are not used as dictionary data.
Example pinyin is made from CC-CEDICT word readings and marked as automatic in the app.
"""
import json, os, re, sys, glob, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
WWW = os.path.join(HERE, '..', 'www')
NSHARD = 256
CY = re.compile('[а-яё]', re.I)
HAN = re.compile('[㐀-鿿\U00020000-\U0002ffff]')
TONES = {'a': 'āáǎà', 'e': 'ēéěè', 'i': 'īíǐì', 'o': 'ōóǒò', 'u': 'ūúǔù', 'ü': 'ǖǘǚǜ'}
MARK = {c: (b, i + 1) for b, s in TONES.items() for i, c in enumerate(s)}


def shard_of(h):
    return ord(h[0]) % NSHARD


def num_to_marks(syl):
    m = re.match(r'^([a-zA-ZüÜ:]+?)([1-5])$', syl)
    if not m:
        return syl.replace('u:', 'ü').replace('v', 'ü') if re.match('^[a-z:]+$', syl) else syl
    s, t = m.group(1).replace('u:', 'ü').replace('v', 'ü'), int(m.group(2))
    if t == 5:
        return s
    low = s.lower()
    i = re.search('[ae]', low)
    i = i.start() if i else low.find('ou')
    if i < 0:
        for j in range(len(low) - 1, -1, -1):
            if low[j] in 'iouü':
                i = j
                break
    if i < 0:
        return s
    return s[:i] + TONES[low[i]][t - 1] + s[i + 1:]


def marked_key(p):
    """any pinyin -> 'toneless|tones' ('dōngxi' -> 'dongxi|1', 'dong1 xi5' -> 'dongxi|1')"""
    p = unicodedata.normalize('NFC', p.lower())
    letters, tones = '', ''
    for part in re.split(r"[\s'’\-,]+", p):
        if not part:
            continue
        if re.search(r'\d', part):
            for syl in re.findall(r'([a-z:ü]+)(\d?)', part):
                letters += syl[0].replace('u:', 'v').replace('ü', 'v')
                tones += syl[1] if syl[1] in '1234' and syl[1] else ''
            continue
        for ch in part:
            if ch in MARK:
                letters += MARK[ch][0].replace('ü', 'v')
                tones += str(MARK[ch][1])
            else:
                letters += 'v' if ch == 'ü' else ch
    return letters + '|' + tones


def toneless(k):
    return k.split('|')[0]


def strip_tags(s):
    s = re.sub(r'\[p\](.*?)\[/p\]', r'\1', s)
    s = re.sub(r'\[i\](.*?)\[/i\]', r'(\1)', s)
    s = re.sub(r'\[/?[a-z]+\]', '', s)
    s = re.sub(r'\(\((.*?)\)\)', r'(\1)', s)
    return re.sub(r'\s+', ' ', s).strip()


PY_TOKEN = re.compile(r"^[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü'’\-]+$", re.I)


def is_py_word(w):
    w = w.strip(',;')
    return bool(w) and bool(PY_TOKEN.match(w)) and bool(re.search('[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]', w) or w in ('de', 'le', 'me', 'ma', 'ne', 'ba', 'zi', 'men', 'ge', 'zhe', 'li', 'shang', 'xia', 'lai', 'qu'))


def lead_readings(s):
    """«háng, hàng компания…» -> (['háng','hàng'], 'компания…')"""
    ys = []
    while True:
        m = re.match(r"^([a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü'’]+)(,?)\s+", s, re.I)
        if not m or not is_py_word(m.group(1)) or CY.search(m.group(1)):
            break
        ys.append(m.group(1))
        s = s[m.end():]
        if not m.group(2):
            break
    return ys, s


def parse_text(text, multi):
    """БКРС article -> blocks [{pos, y, s: [{y: [readings], t, x: [[zh, ru]], a: archaic}]}]"""
    blocks, cur = [], None
    POS_RE = re.compile(r'\[p\](.*?)\[/p\]')

    def new(y=None, pos=''):
        b = {'pos': pos, 'y': y or [], 's': []}
        blocks.append(b)
        return b
    for raw in text.split('\n'):
        line = raw.strip()
        if not line:
            continue
        plain = strip_tags(line)
        head = re.match(r'^(I{1,3}|IV|V|VI{0,3}|IX|X)(?:\s+|$)(.*)$', line)
        if head:
            rest = head.group(2)
            pm = POS_RE.search(rest)
            ys = [w.strip(',') for w in strip_tags(POS_RE.sub(' ', rest)).split() if is_py_word(w.strip(','))] if multi else []
            cur = new(ys, strip_tags(pm.group(1)) if pm else '')
            continue
        if multi and not CY.search(plain) and not HAN.search(plain) and all(is_py_word(w.strip(',')) for w in plain.split()):
            cur = new([w.strip(',') for w in plain.split()])
            continue
        if cur is None:
            cur = new()
        if HAN.match(plain):
            m = CY.search(plain)
            if m:
                i = m.start()
                while i > 0 and plain[i - 1] in '(«["':
                    i -= 1
                zh = re.sub(r'\s*\([a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü\s]+\)\s*', '', plain[:i])
                zh = re.sub(r'\([\u3400-\u9fff]+\)', '', zh).strip(' ―—-')
                ru = plain[i:].strip()
                if not cur['s']:
                    cur['s'].append({'y': [], 't': '', 'x': []})
                sx = cur['s'][-1]['x']
                if 1 < len(zh) <= 24 and len(sx) < 3 and len(ru) <= 140:
                    sx.append([zh, ru])
            continue
        body = re.sub(r'^(\d+\)|[а-я]\))\s*', '', plain).strip()
        if re.match(r'^[А-Я]$', body):
            continue
        pm = POS_RE.search(line)
        if pm and pm.start() < 14 and not cur['pos']:
            cur['pos'] = strip_tags(pm.group(1))
        ys, body = lead_readings(body) if multi else ([], body)
        if pm:
            body = re.sub('^' + re.escape(strip_tags(pm.group(1))) + r'\s*', '', body)
        if not CY.search(body):
            continue
        arch = body.startswith('*')
        body = body.lstrip('* ').strip()
        if len(cur['s']) < 14:
            cur['s'].append({'y': ys or cur['y'], 't': body if len(body) <= 160 else body[:157].rsplit(' ', 1)[0] + '…', 'x': [], 'a': 1 if arch else 0})
    for b in blocks:
        b['s'] = [x for x in b['s'] if (x['t'] or x['x']) and not re.match(r'^[А-ЯA-Z]\.?$', x['t'])]
    return [b for b in blocks if b['s']]


def reading_match(y, rkey):
    k = marked_key(y)
    if k == rkey:
        return 2
    if toneless(k) == toneless(rkey) and k.endswith('|'):
        return 1           # «dongxi» in БКРС = neutral tones
    return 0


def senses_for(blocks, rkey, multi):
    allsen = [s for b in blocks for s in b['s'] if s['t']]
    if not multi or not any(s['y'] for s in allsen):
        return allsen
    for want in (2, 1):
        got = [s for s in allsen if any(reading_match(y, rkey) == want for y in s['y'])]
        if got:
            return got
    return []


def short_gloss(sens):
    """first sense (and the second, if the first is short), comments in parentheses removed"""
    out = []
    for s in sorted(sens, key=lambda x: x.get('a', 0)):
        t = re.sub(r'\([^)]*\)', '', s['t'])
        hm = HAN.search(t)
        if hm:
            t = t[:hm.start()]
        t = t.replace(':', '')
        t = re.sub(r'\s+([;,])', r'\1', re.sub(r'\s+', ' ', t)).strip(' ;,.')
        t = re.sub(r'[;,]\s*[;,]', ';', t)
        if not t or not CY.search(t) or re.match(r'^(см\.|то же|вм\.|сокр\.)', t):
            continue
        out.append(t)
        if len(out) == 2 or len(out[0]) > 14:
            break
    g = '; '.join(out)
    if len(g) > 70:
        g = g[:68].rsplit(' ', 1)[0].rstrip(',;') + '…'
    return g


def main():
    base = os.path.join(SRC, 'dict_base.txt')
    rows = []
    for l in open(base, encoding='utf-8'):
        if l.startswith('#') or not l.strip():
            continue
        c = l.rstrip('\n').split('\t')
        while len(c) < 6:
            c.append('')
        rows.append(c)
    hsk = {}
    for l in open(os.path.join(SRC, 'hsk-words.txt'), encoding='utf-8'):
        if l.startswith('#'):
            continue
        c = l.rstrip('\n').split('\t')
        if len(c) == 2 and c[1].isdigit():
            hsk[c[0]] = int(c[1])
    bk = {}
    nfiles = 0
    for f in sorted(glob.glob(os.path.join(SRC, 'bkrs', 'e', '*.json')), key=lambda p: int(os.path.basename(p)[:-5])):
        nfiles += 1
        for it in json.load(open(f, encoding='utf-8')):
            h, p, t = it[0], it[1], it[2]
            x = it[3] if len(it) > 3 else {}
            if h in bk or not CY.search(t):
                continue           # no Russian in БКРС itself: the JSON's machine translation ("m") is not used
            bk[h] = (p if not x.get('a') else '', t)
    print('БКРС files', nfiles, 'entries with Russian', len(bk))

    # best CEDICT reading per word (for example pinyin): HSK, then lower-case (not a name), then first
    best = {}
    for c in rows:
        h, n = c[0], c[2]
        if n.startswith('='):
            continue
        sc = (0 if c[4] else 1, 0 if c[5] else 1, 1 if re.match('^[A-Z]', n) else 0)
        if h not in best or sc < best[h][0]:
            best[h] = (sc, n)

    def ex_pinyin(zh, head='', head_py=''):
        """pinyin of an example: CC-CEDICT word readings; the headword itself takes the reading of its sense"""
        out, i = [], 0
        while i < len(zh):
            if not HAN.match(zh[i]):
                ch = zh[i]
                if re.match('[0-9A-Za-z]', ch):
                    j = i
                    while j < len(zh) and re.match('[0-9A-Za-z.%]', zh[j]):
                        j += 1
                    out.append(zh[i:j])
                    i = j
                    continue
                if ch in '，,':
                    out.append(',')
                elif ch in '。！？!?；;：:':
                    out.append(ch if ch in '!?;:' else '.')
                i += 1
                continue
            if head and head_py and zh.startswith(head, i):
                out.append(head_py)
                i += len(head)
                continue
            for L in range(min(6, len(zh) - i), 0, -1):
                w = zh[i:i + L]
                if w in best:
                    out.append(''.join(num_to_marks(s) for s in best[w][1].lower().split()))
                    i += L
                    break
            else:
                return ''          # an unknown character: no pinyin rather than a guess
        txt = ' '.join(out).replace(' ,', ',').replace(' .', '.')
        return txt

    details = {}
    out_rows, nb, nm, nnone = [], 0, 0, 0
    for c in rows:
        h, t, n, en, ru, flag = c[0], c[1], c[2], c[3], c[4], c[5]
        lv = hsk.get(h, 0)
        cl = ''
        mcl = re.search(r'CL:([^;]+)', en)
        if mcl:
            cl = ','.join(dict.fromkeys(re.findall(r'([㐀-鿿]+)(?:\|[㐀-鿿]+)?\[', mcl.group(1))))
            en = re.sub(r';?\s*CL:[^;]+', '', en).strip('; ')
        src = 'm' if ru else ''
        reading = n[1:] if n.startswith('=') else ' '.join(num_to_marks(s) for s in n.split())
        rkey = marked_key(reading)
        if h in bk:
            bp, text = bk[h]
            multi = (',' in bp) or bool(re.search(r'^\s*(I|II)\s', text, re.M))
            if h not in details:
                blocks = parse_text(text, multi)
                for b in blocks:
                    for x in b['s']:
                        ys = x['y'] or b['y']
                        hp = ys[0].strip(',') if multi and len(ys) == 1 else ''
                        x['x'] = [[zh, ex_pinyin(zh, h, hp), r] for zh, r in x['x']]
                details[h] = {'p': bp, 'm': multi, 'b': blocks}
            sens = senses_for(details[h]['b'], rkey, multi)
            if re.match('^[A-Z]', n):
                sens = []         # a surname / place name reading: the common word's senses do not belong to it
            if sens and not ru:
                g = short_gloss(sens)
                if g:
                    ru, src = g, 'b'
        if src == 'b':
            nb += 1
        elif src == 'm':
            nm += 1
        else:
            nnone += 1
        out_rows.append([h, t, n, en, ru, str(lv or ''), src, cl])
    ver = '2026.11.07-bkrs261102'
    with open(os.path.join(WWW, 'dict.txt'), 'w', encoding='utf-8') as f:
        f.write('#mao-dict\t' + ver + '\n')
        for r in out_rows:
            f.write('\t'.join(r) + '\n')
    sh = {}
    for h, d in details.items():
        d.pop('m', None)
        for b in d['b']:
            if not b['y']:
                b.pop('y')
            if not b['pos']:
                b.pop('pos')
            for x in b['s']:
                if not x['x']:
                    x.pop('x')
                if not x.get('a'):
                    x.pop('a', None)
                if not x['y'] or x['y'] == b.get('y'):
                    x.pop('y')
        sh.setdefault(shard_of(h), {})[h] = d
    od = os.path.join(WWW, 'ru')
    os.makedirs(od, exist_ok=True)
    for fn in glob.glob(os.path.join(od, '*.json')):
        os.remove(fn)
    tot = 0
    for k, m in sh.items():
        p = os.path.join(od, '%03d.json' % k)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(m, f, ensure_ascii=False, separators=(',', ':'))
        tot += os.path.getsize(p)
    open(os.path.join(WWW, 'dictver.txt'), 'w').write(ver + '\n')
    print('rows', len(out_rows), 'ru from Mao', nm, 'from БКРС', nb, 'without Russian', nnone)
    print('details', len(details), 'shards', len(sh), 'MB', round(tot / 1e6, 1))


if __name__ == '__main__':
    main()
