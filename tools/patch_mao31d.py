#!/usr/bin/env python3
"""Mao 3.1, stage 5: the Mao assistant works from the dictionary.
 - offline: characters → explanation; «как сказать …» → dictionary search (whole phrase first);
   pinyin → dictionary; topics → words; anything else → an honest «this needs the neural network»
 - with the neural network on: dictionary entries for the words in the question go into the prompt
   as checked data, and the model is told not to invent translations"""
P = '/tmp/claude-0/mao/www/index.html'
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, n, a[:100])
    s = s.replace(a, b)


def method(name, new):
    global s
    i = s.find('\n  ' + name + '(')
    assert i >= 0, name
    j = s.find('\n  ', i + 3)
    while s[j + 3] == ' ':
        j = s.find('\n  ', j + 3)
    s = s[:i] + '\n' + new.rstrip('\n') + s[j:]


method('offlineMao', r"""  offlineMao(t){const E=window.EDict;if(!E||!E.ready())return 'Словарь ещё загружается — спросите через пару секунд.';
    const sh=m=>shortM(m);const line=e=>e.h+' '+e.p+' — '+(e.m?sh(e.m):'русского перевода в словаре нет');
    const seg=x=>{const c=[...x],o=[];let i=0;while(i<c.length){let l=Math.min(4,c.length-i);for(;l>1;l--)if(E.find(c.slice(i,i+l).join('')))break;o.push(c.slice(i,i+l).join(''));i+=l;}return o;};
    const low=t.toLowerCase().replace(/ё/g,'е').trim();const han=t.match(/[㐀-鿿]+/g);
    const why=/(почему|зачем|объясни|грамматик|когда (ставят|употребл|использ)|как (употребл|использ|строит)|правил|разниц|отлича)/.test(low);
    if(han){const out=[];han.slice(0,3).forEach(hh=>(E.find(hh)?[hh]:seg(hh)).slice(0,3).forEach(x=>{const e=E.find(x);out.push(e?(window.Explain&&Explain.ready()?Explain.text(e):line(e)):x+' — этого слова нет в словаре Mao.');}));
      if(why)out.push('Это то, что есть в словаре. Объяснить грамматику подробно без нейросети я не могу — включите её в Настройках.');return out.join('\n\n');}
    const tm=low.match(/(?:слова|слов)?\s*(про|на тему|по теме|о|об)\s+([а-я -]{3,40})/);
    if(/подбер|подобра|слова (про|на|по|о)|слов (про|на|по|о)/.test(low)){const topic=(tm?tm[2]:low.replace(/подбер\S*|подобра\S*|слова?|мне|пожалуйста|[?!.,]/g,'')).trim();if(!topic)return 'На какую тему подобрать слова? Например: «подбери слова про еду».';
      let list=(E.topic(topic)||[]).slice(0,8).map(h=>E.find(h)).filter(Boolean);if(list.length<8)E.byRu(topic,12).forEach(e=>{if(list.length<8&&!list.some(x=>x.h===e.h))list.push(e);});
      const head=tm?'Слова '+tm[1]+' '+tm[2]:'Слова по теме «'+topic+'»';
      if(!list.length)return 'В словаре не нашлось слов по запросу «'+topic+'». Попробуйте другое слово: «еда», «семья», «работа», «погода».';
      return head+':\n'+list.map(line).join('\n')+'\n\nЧтобы учить их: «Слова» → «Следующий урок» → своя тема.';}
    if(why)return 'Это вопрос не про одно слово, а про язык. Без нейросети я отвечаю только по словарю: пришлите иероглиф (了), русское слово («как сказать кошка») или тему («подбери слова про еду»). Для объяснений грамматики включите нейросеть в Настройках.';
    // pinyin: «xuexi», «xué xí»
    const py=low.replace(/[?!.,«»"]/g,'').trim();if(/^[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü' 0-9]+$/.test(py)&&/[a-z]/.test(py)){const r=E.search(py,6);return r.length?'«'+py+'» в словаре:\n'+r.map(line).join('\n'):'Слова с пиньинем «'+py+'» в словаре нет.';}
    const q=low.replace(/как (сказать|будет|по-китайски|написать)|что значит|что такое|по-китайски|перевод\S*|переведи|слово|[?!.,«»"]/g,'').replace(/\s+/g,' ').trim();
    if(!q)return 'Напишите иероглиф, русское слово или тему — отвечу по словарю.';
    // the whole phrase first («как дела» is a phrase, not «дела» + «как»)
    let r=E.search(q,6).filter(e=>e.m);const whole=r.filter(e=>e.m.toLowerCase().replace(/ё/g,'е').split(/[;,]\s*/).some(x=>x.trim()===q));if(whole.length)r=whole;
    if(r.length)return '«'+q+'» по-китайски:\n'+r.slice(0,6).map(line).join('\n')+(whole.length?'':'\n\nТочного совпадения нет — это ближайшие слова из словаря.');
    return 'В словаре нет «'+q+'». Попробуйте одно слово в начальной форме («кошка», «работать») или включите нейросеть в Настройках.';}""")

# with the neural network: checked dictionary data in the prompt
rep("""    const msgs=[{role:'system',content:AISYS},...chat.slice(-10).map(m=>({role:m.r==='me'?'user':'assistant',content:m.t}))];""",
    """    const ctx=this.dictContext(txt);const msgs=[{role:'system',content:AISYS+(ctx?'\\n\\nПроверенные данные словаря Mao (БКРС, CC-CEDICT) — используй их как источник значений:\\n'+ctx+'\\nЕсли нужного слова здесь нет и ты не уверен в переводе — так и скажи, не придумывай.':'\\nЕсли не уверен в переводе слова — так и скажи, не придумывай.')},...chat.slice(-10).map(m=>({role:m.r==='me'?'user':'assistant',content:m.t}))];""")
rep("""  aiChat(msgs,onChunk){""", """  // dictionary lines for the words in a question (characters, or a Russian word to look up)
  dictContext(t){const E=window.EDict;if(!E||!E.ready())return '';const out=[];const add=e=>{if(e&&out.length<8&&!out.some(x=>x.startsWith(e.h+' '+e.p)))out.push(e.h+' '+e.p+' — '+(e.m||'русского перевода нет')+(e.lv?' (HSK '+e.lv+')':''));};
    (t.match(/[㐀-鿿]+/g)||[]).slice(0,4).forEach(h=>{const f=E.find(h);if(f){add(f);E.readings(h).slice(0,3).forEach(add);}else[...h].slice(0,4).forEach(c=>add(E.find(c)));});
    if(!out.length){const q=t.toLowerCase().replace(/как (сказать|будет)|по-китайски|что значит|[?!.,«»"]/g,'').trim();if(q&&/[а-я]/.test(q))E.search(q,5).filter(e=>e.m).forEach(add);}
    return out.join('\\n');}
  aiChat(msgs,onChunk){""")
open(P, 'w', encoding='utf-8').write(s)
print('ok')
