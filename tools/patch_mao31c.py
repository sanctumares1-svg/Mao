#!/usr/bin/env python3
"""Mao 3.1, stage 4: the word card.
 - characters with their own syllable under each one
 - the meaning and where it comes from (Mao / БКРС / your own); honest note when there is no Russian
 - HSK level, part of speech, measure word; senses and examples from БКРС (loaded when the card opens)
 - other readings of a character; parts of each character
 - stroke-order animation; «Потренировать письмо»; your own translation without touching the dictionary
 - dictionary results open the same card before adding"""
import re
P = '/tmp/claude-0/mao/www/index.html'
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, n, a[:100])
    s = s.replace(a, b)


def card_tpl(X, full):
    sen_n = 'z.n' if full else 'z.n'
    return f"""
    <div style="display:flex;justify-content:center;gap:{{{{ {X}.gap }}}}px;flex-wrap:wrap">
      <sc-for list="{{{{ {X}.cs }}}}" as="c" hint-placeholder-count="2"><span style="display:flex;flex-direction:column;align-items:center;gap:2px"><span style="font:600 {{{{ {X}.fs }}}}px/1.1 'Noto Serif SC',serif">{{{{ c.c }}}}</span><span style="font-size:{{{{ {X}.pfs }}}}px;font-weight:500;color:var(--ac);min-height:1.1em">{{{{ c.py }}}}</span></span></sc-for>
    </div>
    <sc-if value="{{{{ {X}.pyLine }}}}" hint-placeholder-val="{{{{ false }}}}"><span style="font-size:22px;font-weight:500;color:var(--ac);text-align:center">{{{{ {X}.p }}}}</span></sc-if>
    <span style="font-size:19px;text-align:center;line-height:1.35">{{{{ {X}.m }}}}</span>
    <sc-if value="{{{{ {X}.noRu }}}}" hint-placeholder-val="{{{{ false }}}}"><span style="font-size:13.5px;color:var(--ac);text-align:center;line-height:1.4;max-width:300px">Русского перевода в словаре нет. Впишите свой — тогда слово можно учить и проверять.</span></sc-if>
    <sc-if value="{{{{ {X}.hasMeta }}}}" hint-placeholder-val="{{{{ true }}}}"><span style="font-size:12.5px;color:var(--mu);text-align:center">{{{{ {X}.meta }}}}</span></sc-if>
    <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:4px">
      <button onClick="{{{{ {X}.say }}}}" style="height:40px;padding:0 14px 0 10px;border-radius:999px;border:1px solid var(--ln);background:var(--sf);color:var(--ink);font-size:14px;cursor:pointer;display:flex;align-items:center;gap:6px"><span class="mi" style="font-size:20px">&#xe050;</span>Послушать</button>
      <sc-if value="{{{{ {X}.canAnim }}}}" hint-placeholder-val="{{{{ true }}}}"><button onClick="{{{{ {X}.anim }}}}" style="height:40px;padding:0 14px 0 10px;border-radius:999px;border:1px solid var(--ln);background:var(--sf);color:var(--ink);font-size:14px;cursor:pointer;display:flex;align-items:center;gap:6px"><span class="mi" style="font-size:20px">&#xe037;</span>Порядок черт</button></sc-if>
    </div>
    <sc-if value="{{{{ {X}.animOn }}}}" hint-placeholder-val="{{{{ false }}}}"><canvas ref="{{{{ {X}.animRef }}}}" style="width:150px;height:150px;border-radius:12px;background:var(--sf);border:1.5px solid var(--ln);flex:none;color:var(--ink)"></canvas></sc-if>
    <sc-if value="{{{{ {X}.hasSen }}}}" hint-placeholder-val="{{{{ false }}}}"><div style="width:100%;display:flex;flex-direction:column;gap:8px;padding:12px 14px;border-radius:14px;background:var(--sf2);text-align:left">
      <span style="font-size:12px;font-weight:600;color:var(--mu)">{{{{ {X}.senL }}}}</span>
      <sc-for list="{{{{ {X}.sen }}}}" as="z" hint-placeholder-count="2"><div style="display:flex;flex-direction:column;gap:3px"><span style="font-size:14.5px;line-height:1.45"><span style="color:var(--mu)">{{{{ {sen_n} }}}} </span>{{{{ z.t }}}}</span><sc-for list="{{{{ z.xs }}}}" as="x" hint-placeholder-count="1"><span style="padding-left:16px;font-size:13.5px;line-height:1.45;display:flex;flex-direction:column"><span><span style="font-family:'Noto Serif SC',serif;font-weight:600">{{{{ x.zh }}}}</span> <span style="color:var(--ac)">{{{{ x.py }}}}</span></span><span style="color:var(--mu)">{{{{ x.ru }}}}</span></span></sc-for></div></sc-for>
      <span style="font-size:11.5px;color:var(--mu);line-height:1.4">{{{{ {X}.exNote }}}}</span>
    </div></sc-if>
    <sc-if value="{{{{ {X}.loading }}}}" hint-placeholder-val="{{{{ false }}}}"><span style="font-size:13px;color:var(--mu)">Открываю статью словаря…</span></sc-if>
    <sc-if value="{{{{ {X}.hasRd }}}}" hint-placeholder-val="{{{{ false }}}}"><div style="width:100%;padding:10px 14px;border-radius:14px;background:var(--sf2);font-size:13.5px;line-height:1.5;text-align:left"><span style="color:var(--mu)">Другие чтения: </span>{{{{ {X}.rd }}}}</div></sc-if>
    <sc-if value="{{{{ {X}.hasParts }}}}" hint-placeholder-val="{{{{ false }}}}"><div style="width:100%;padding:10px 14px;border-radius:14px;background:var(--sf2);font-size:13.5px;line-height:1.5;color:var(--ink);white-space:pre-line;text-align:left"><span style="color:var(--mu)">Из чего состоит: </span>{{{{ {X}.parts }}}}</div></sc-if>"""


# ---- learn card ----
a = s.index('<!-- ============ ЗНАКОМСТВО ============ -->')
b = s.index('<!-- ============ ВЫБОР ИЗ 4 ============ -->')
s = s[:a] + """<!-- ============ ЗНАКОМСТВО ============ -->
<sc-if value="{{ isCard }}" hint-placeholder-val="{{ false }}">
  <div class="scr" style="flex:1;min-height:0;overflow-y:auto;display:flex;flex-direction:column;align-items:center;justify-content:safe center;gap:10px;padding:8px 24px">""" + card_tpl('card', False) + """
  </div>
  <div style="padding:10px 20px 18px;flex:none;display:flex;flex-direction:column;gap:4px"><button onClick="{{ learnNextB }}" style="height:56px;border-radius:16px;border:0;background:var(--pr);color:var(--onpr);font-size:16px;font-weight:600;cursor:pointer">Дальше</button><button onClick="{{ learnKnownB }}" style="height:44px;border:0;background:none;color:var(--mu);font-size:14px;cursor:pointer">Уже знаю это слово</button></div>
</sc-if>

""" + s[b:]

# ---- word sheet ----
a = s.index('<sc-if value="{{ sheetWord }}"')
b = s.index('<sc-if value="{{ sheetPickDay }}"')
s = s[:a] + """<sc-if value="{{ sheetWord }}" hint-placeholder-val="{{ false }}">
        <div class="scr" style="padding:8px 22px 24px;display:flex;flex-direction:column;align-items:center;gap:8px;overflow-y:auto">
          <span style="font-size:12.5px;color:var(--mu)">{{ sw.top }}</span>""" + card_tpl('sw', True) + """
          <sc-if value="{{ sw.editing }}" hint-placeholder-val="{{ false }}"><div style="width:100%;display:flex;flex-direction:column;gap:6px"><input value="{{ sw.editV }}" onChange="{{ sw.onEdit }}" placeholder="Свой перевод" style="height:46px;border-radius:12px;border:1px solid var(--ln);background:var(--bg);color:var(--ink);font-size:15px;padding:0 12px;outline:none"><div style="display:flex;gap:8px"><button onClick="{{ sw.editCancel }}" style="flex:1;height:44px;border-radius:12px;border:1.5px solid var(--ln);background:none;color:var(--ink);font-size:14px;cursor:pointer">Отмена</button><button onClick="{{ sw.editSave }}" style="flex:1;height:44px;border-radius:12px;border:0;background:var(--pr);color:var(--onpr);font-size:14px;font-weight:600;cursor:pointer">Сохранить</button></div></div></sc-if>
          <sc-if value="{{ sw.isWord }}" hint-placeholder-val="{{ true }}"><div style="width:100%;display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px">
            <button onClick="{{ sw.write }}" style="height:48px;border-radius:14px;border:0;background:var(--pr);color:var(--onpr);font-size:14px;font-weight:600;cursor:pointer">Потренировать письмо</button>
            <button onClick="{{ sw.ask }}" style="height:48px;border-radius:14px;border:0;background:var(--prs);color:var(--pr);font-size:14px;font-weight:600;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px"><span class="mi" style="font-size:20px">&#xe8af;</span>Спросить</button>
            <button onClick="{{ sw.editOpen }}" style="height:44px;border-radius:14px;border:1.5px solid var(--ln);background:none;color:var(--ink);font-size:13.5px;cursor:pointer">{{ sw.editL }}</button>
            <button onClick="{{ sw.edit }}" style="height:44px;border-radius:14px;border:1.5px solid var(--ln);background:none;color:var(--ink);font-size:13.5px;cursor:pointer">Править урок</button>
          </div></sc-if>
          <sc-if value="{{ sw.canRestore }}" hint-placeholder-val="{{ false }}"><button onClick="{{ sw.restore }}" style="height:40px;border:0;background:none;color:var(--mu);font-size:13px;cursor:pointer">Вернуть перевод словаря: {{ sw.dictM }}</button></sc-if>
          <sc-if value="{{ sw.isDict }}" hint-placeholder-val="{{ false }}"><button onClick="{{ sw.addIt }}" style="width:100%;height:50px;border-radius:14px;border:0;background:{{ sw.addBg }};color:{{ sw.addFg }};font-size:15px;font-weight:600;cursor:pointer;margin-top:6px">{{ sw.addL }}</button></sc-if>
        </div>
      </sc-if>
      """ + s[b:]

# dictionary rows open the card
rep("""<div style="display:flex;align-items:center;gap:14px;padding:12px 12px 12px 16px;border-bottom:1px solid var(--ln)"><span style="font:600 26px 'Noto Serif SC',serif;min-width:56px">{{ r.h }}</span><span style="display:flex;flex-direction:column;gap:2px;flex:1;min-width:0">""",
    """<div style="display:flex;align-items:center;gap:14px;padding:12px 12px 12px 16px;border-bottom:1px solid var(--ln)"><button onClick="{{ r.open }}" style="display:flex;align-items:center;gap:14px;flex:1;min-width:0;border:0;background:none;color:var(--ink);text-align:left;padding:0;cursor:pointer"><span style="font:600 26px 'Noto Serif SC',serif;min-width:56px">{{ r.h }}</span><span style="display:flex;flex-direction:column;gap:2px;flex:1;min-width:0">""")
rep("""<span style="font-size:14px;line-height:1.35">{{ r.m }}</span></span><sc-if value="{{ r.have }}\"""",
    """<span style="font-size:14px;line-height:1.35;color:{{ r.mc }}">{{ r.m }}</span></span></button><sc-if value="{{ r.have }}\"""")

# ---- data ----
rep("""  // ---- writing screen values (v8 layout, 2.9 stroke checking) ----""",
    """  // ---- the word card: everything the dictionary knows about this word and reading ----
  cardData(h,p,o){const E=window.EDict&&EDict.ready()?EDict:null;o=o||{};const nz=x=>String(x||'').replace(/[\\s'’]/g,'').toLowerCase();
    const e=E?(E.best(h).filter(x=>x.h===h||x.t===h).find(x=>nz(x.p)===nz(p))||E.find(h)):null;const ch=[...h];const syl=e&&e.syl&&nz(e.p)===nz(p)?e.syl:null;
    const n=ch.length,fs=n>4?44:n>3?54:n>2?64:n>1?84:110;
    let d=E?E.detailsNow(h):null;if(d===undefined){E.details(h).then(()=>this.forceUpdate());}
    let sen=[],pos='';if(d&&d.b){const all=[];d.b.forEach(b=>b.s.forEach(x=>all.push({...x,y:x.y||b.y||[],pos:b.pos||''})));const anyY=all.some(x=>x.y.length);
      sen=anyY?all.filter(x=>x.y.some(y=>EDict.sameReading(y,p))):all;if(!sen.length&&!anyY)sen=all;pos=(sen[0]&&sen[0].pos)||'';}
    const nS=o.full?8:3,nX=o.full?2:1;const senV=sen.filter(x=>x.t).slice(0,nS).map((x,i)=>({n:i+1+'.',t:x.t,xs:(x.x||[]).slice(0,nX).map(q=>({zh:q[0],py:q[1]||'',ru:q[2]}))}));
    const src=o.mSrc;const meta=[e&&e.lv?'HSK '+e.lv:'',pos,e&&e.cl?'сч. слово '+e.cl.split(',')[0]:'',src==='b'?'перевод: БКРС':src==='user'?'свой перевод':src==='m'?'перевод: Mao':src==='ai'?'перевод нейросети — проверьте':''].filter(Boolean).join(' · ');
    const rd=n===1&&E?E.readings(h).filter(r=>nz(r.p)!==nz(p)&&r.m).slice(0,4).map(r=>r.p+' — '+shortM(r.m)).join('; '):'';
    const parts=o.mn?(o.mn.parts.map(x=>x[0]+' '+x[1]).join(' + ')+(o.mn.note?'\\n'+o.mn.note:'')):(window.Explain&&Explain.ready()?Explain.partsShort(h):'');
    const key=(o.tag||'c')+'|'+h;const animOn=!!(this.state.animK===key);
    return {cs:ch.map((c,i)=>({c,py:syl?syl[i]:''})),pyLine:!syl,p,gap:n>3?4:8,fs,pfs:n>3?15:18,m:o.m||'',noRu:!o.m,hasMeta:!!meta,meta,say:()=>this.speak(h),
      canAnim:!!(window.WCheck&&WCheck.ready()&&ch.some(c=>WCheck.has(c))),anim:()=>this.setState({animK:animOn?null:key}),animOn,animRef:el=>{if(el&&el.dataset.k!==h){el.dataset.k=h;this.sAnim(el,h);}},
      hasSen:senV.length>0,sen:senV,senL:'ЗНАЧЕНИЯ · БКРС',exNote:senV.some(x=>x.xs.length)?'Пиньинь в примерах подобран автоматически по словарю — возможны неточности в многозначных словах.':'',
      loading:d===undefined&&!!E,hasRd:!!rd,rd,hasParts:!!parts,parts};}
  // stroke order: strokes appear one by one in their outlines, character after character
  sAnim(el,h){const c=[...h].filter(x=>window.WCheck&&WCheck.has(x));if(!c.length)return;const r=Math.min(3,window.devicePixelRatio||1);const W=Math.round(150*r);el.width=W;el.height=W;const g=el.getContext('2d');const tok={};this.saTok=tok;
    const css=getComputedStyle(this.phoneRef.current||document.body);const ol=css.getPropertyValue('--ol').trim()||'#ddd',ink=getComputedStyle(el).color||'#222';let ci=0,si=0,t0=performance.now();
    const step=now=>{if(this.saTok!==tok||!el.isConnected||el.dataset.k!==h)return;const ch=c[ci];const OP=WCheck.paths(ch,W,W),R=WCheck.ref(ch);if(!OP||!R){ci=(ci+1)%c.length;return requestAnimationFrame(step);}
      g.clearRect(0,0,W,W);g.fillStyle=ol;OP.forEach(p=>g.fill(p));g.fillStyle=ink;g.strokeStyle=ink;for(let i=0;i<si;i++)g.fill(OP[i]);
      const pr=Math.min(1,(now-t0)/480);if(si<OP.length)this.wInk(g,OP[si],R[si],W,W,pr);
      if(pr>=1){si++;t0=now;if(si>OP.length){si=0;ci=(ci+1)%c.length;t0=now+500;}}requestAnimationFrame(step);};
    requestAnimationFrame(step);}
  practiceWrite(id){const qz=this.mkQuiz([id],'Прописи','test');qz.write=true;this.setState({screen:'quiz',quiz:qz,sheet:null,animK:null});}
  // ---- writing screen values (v8 layout, 2.9 stroke checking) ----""")

rep("""      card={h:cw.h,p:cw.p,m:cw.m,fs:cw.h.length>2?72:cw.h.length>1?92:120,mWarn:cw.mSrc==='ai',hasParts:!!parts,parts};}""",
    """      card={...this.cardData(cw.h,cw.p,{m:cw.m,mSrc:cw.mSrc,mn:cw.mn,tag:'learn'}),h:cw.h};}""")
a = s.index("      sw:(()=>{if(s.sheet!=='word')return {};")
b = s.index("})(),", a) + len("})(),")
s = s[:a] + """      sw:(()=>{if(s.sheet==='dict'&&s.dictE){const e=s.dictE;const ex=ws.find(x=>x.h===e.h);const ad=s.addDay||this.bulkTarget();const r=this.ruFor(e);
          return {...this.cardData(e.h,e.p,{m:r.m,mSrc:r.mSrc,full:true,tag:'dict'}),top:'Словарь'+(e.en&&!r.m?' · по-английски: '+e.en:''),isWord:false,isDict:true,
            addL:ex?'Уже в уроке '+ex.d:'Добавить в урок '+ad,addBg:ex?'var(--sf2)':'var(--pr)',addFg:ex?'var(--mu)':'var(--onpr)',addIt:()=>{if(ex)return;this.addWord(e,ad);this.setState({sheet:null});}};}
        if(s.sheet!=='word')return {};const w=this.W(s.wid);if(!w)return {};
        const stl=w.s==='new'?'новое':this.isDue(w)?'повторить сегодня':w.s==='hard'?'трудное':w.next?'повтор '+fmtD(pISO(w.next)).replace(/ \\d{4}$/,''):'выучено';
        const de=this.dictFor(w);const dictM=de&&de.m&&de.m!==w.m?de.m:'';
        return {...this.cardData(w.h,w.p,{m:w.m,mSrc:w.mSrc,mn:w.mn,full:true,tag:'word'}),top:lessonL(w.d)+' · '+stl,isWord:true,isDict:false,
          write:()=>this.practiceWrite(w.id),ask:()=>{this.setState({sheet:null,screen:'tab',tab:'ask'});this.sendChat('Разбери '+w.h);},edit:()=>this.setState({sheet:null,screen:'dayEdit',de:{n:w.d,t0:(s.lessons.find(l=>l.n===w.d)||{}).t}}),
          editing:s.swEdit!=null,editV:s.swEdit||'',onEdit:e=>this.setState({swEdit:e.target.value}),editCancel:()=>this.setState({swEdit:null}),editOpen:()=>this.setState({swEdit:w.m||''}),editL:w.m?'Изменить перевод':'Вписать перевод',
          editSave:()=>{const v=String(s.swEdit||'').trim();if(!v)return this.toast('Пустой перевод не сохраняется');if(!/[а-яё]/i.test(v))return this.toast('Напишите перевод по-русски');this.upd({words:this.state.words.map(x=>x.id===w.id?{...x,m:v,mSrc:'user',mEdited:true}:x),myRu:{...(this.state.myRu||{}),[w.k||w.h]:v},swEdit:null});this.toast('Перевод сохранён — словарь не изменён');},
          canRestore:!!dictM&&w.mSrc==='user',dictM:shortM(dictM),restore:()=>{const my={...(this.state.myRu||{})};delete my[w.k||w.h];this.upd({words:this.state.words.map(x=>x.id===w.id?{...x,m:de.m,mSrc:de.src||'m',mEdited:false}:x),myRu:my});}};})(),""" + s[b:]
rep("""hasSheet:!!s.sheet,closeSheet:()=>this.setState({sheet:null,resetAsk:false}),stop:e=>e.stopPropagation(),sheetTopic:s.sheet==='topic',sheetWord:s.sheet==='word',""",
    """hasSheet:!!s.sheet,closeSheet:()=>this.setState({sheet:null,resetAsk:false,swEdit:null,animK:null}),stop:e=>e.stopPropagation(),sheetTopic:s.sheet==='topic',sheetWord:s.sheet==='word'||s.sheet==='dict',""")
rep("""const openW=id=>()=>this.setState({sheet:'word',wid:id,partsOpen:false});""",
    """const openW=id=>()=>this.setState({sheet:'word',wid:id,partsOpen:false,swEdit:null,animK:null});""")
rep("""return {h:e.h,p:e.p,m:shortM(ru)||(e.en?e.en+' (англ.)':''),have:!!ex,can:!ex,dayL:ex?'Урок '+ex.d:'',add:()=>this.addWord(e,addDay)};});}""",
    """return {h:e.h,p:e.p,m:shortM(ru)||(e.en?'нет русского перевода · англ.: '+e.en:'нет перевода'),mc:ru?'var(--ink)':'var(--mu)',have:!!ex,can:!ex,dayL:ex?'Урок '+ex.d:'',add:()=>this.addWord(e,addDay),open:()=>this.setState({sheet:'dict',dictE:e,animK:null})};});}""")
open(P, 'w', encoding='utf-8').write(s)
print('ok')
