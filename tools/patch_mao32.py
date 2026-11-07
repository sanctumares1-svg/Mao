#!/usr/bin/env python3
"""Mao 3.2: smoother first stroke, a lesson that explains itself, sensible answer options.
Lesson flows («Быстрый урок», «Снежный ком»), intervals and success conditions are NOT changed."""
P = '/tmp/claude-0/mao/www/index.html'
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, n, a[:120])
    s = s.replace(a, b)


# ---------- 1. drawing: nothing re-renders the app while the finger is down; live ink on its own layer ----------
rep("""g.beginPath();g.moveTo(x,y);g.lineTo(x+.1,y+.1);g.stroke();this.lp0=[x,y];this.lm=[x,y];this.wS=this.wS||[];this.wS.push([[x/c.width,y/c.height,1]]);if(this.state.wMsg)this.setState({wMsg:null});if(!this.state.wHas)this.setState({wHas:true});}""",
    """g.beginPath();g.moveTo(x,y);g.lineTo(x+.1,y+.1);g.stroke();this.lp0=[x,y];this.lm=[x,y];this.wS=this.wS||[];this.wS.push([[x/c.width,y/c.height,1]]);}""")
rep("""this.drw=true;const [x,y]=this.wPt(e),g=c.getContext('2d');""",
    """this.drw=true;const [x,y]=this.wPt(e),ov=this.wOv(),g=(ov||c).getContext('2d');if(ov)g.clearRect(0,0,ov.width,ov.height);""")
rep("""  wMove(e){if(!this.drw||(this.pid!=null&&e.pointerId!==this.pid))return;const c=this.wcEl();if(!c)return;const g=c.getContext('2d');""",
    """  // the finger's line is drawn on a transparent layer above the cell: redraws of the cell (hints, animations) never touch it
  wOv(){const c=this.wcEl();const o=c&&c.parentNode?c.parentNode.querySelector('canvas[data-ov]'):null;if(o&&(o.width!==c.width||o.height!==c.height)){o.width=c.width;o.height=c.height;}return o;}
  wOvClear(){const o=this.wOv();if(o)o.getContext('2d').clearRect(0,0,o.width,o.height);}
  wMove(e){if(!this.drw||(this.pid!=null&&e.pointerId!==this.pid))return;const c=this.wcEl();if(!c)return;const ov=this.wOv(),g=(ov||c).getContext('2d');""")
rep("""  wUp(e){if(!this.drw||(e&&this.pid!=null&&e.pointerId!==this.pid))return;this.drw=false;this.pid=null;this.wSnapLast();}""",
    """  wUp(e){if(!this.drw||(e&&this.pid!=null&&e.pointerId!==this.pid))return;this.drw=false;this.pid=null;if(this.state.wMsg)this.setState({wMsg:null});this.wSnapLast();this.wOvClear();}""")
rep("""const R=this.wCurRef();if(!R){this.wMeta[j]={k:-1};this.setState({wN:this.wS.length});return;}""",
    """const R=this.wCurRef();if(!R){this.wMeta[j]={k:-1};this.setState({wN:this.wS.length,wHas:true});this.wRender();return;}""")
rep("""const exp=[...Array(R.length).keys()].find(i=>!used.has(i));if(exp==null)return;
    const xf=""", """const exp=[...Array(R.length).keys()].find(i=>!used.has(i));if(exp==null){this.wS.pop();this.wRender();return;}
    const xf=""")
rep("""    (this.wS||[]).forEach((st,j)=>{const m=(this.wMeta||[])[j];const snapped=m&&m.k>=0;""",
    """    (this.wS||[]).forEach((st,j)=>{if(this.drw&&j===this.wS.length-1)return;const m=(this.wMeta||[])[j];const snapped=m&&m.k>=0;""")
rep("""  wClear(){clearInterval(this.wAnimT);const c=this.wcEl();if(c)c.getContext('2d').clearRect(0,0,c.width,c.height);""",
    """  wClear(){clearInterval(this.wAnimT);const c=this.wcEl();if(c)c.getContext('2d').clearRect(0,0,c.width,c.height);this.wOvClear();""")
rep("""this.wBad=null;this.wSnapAn=null;this.drw=false;this.setState({wIdx:k""", """this.wBad=null;this.wSnapAn=null;this.drw=false;this.wOvClear();this.setState({wIdx:k""")
rep("""onPointerCancel="{{ wUp }}" style="position:absolute;inset:0;width:100%;height:100%;touch-action:none;cursor:crosshair;color:var(--ink)"></canvas>""",
    """onPointerCancel="{{ wUp }}" style="position:absolute;inset:0;width:100%;height:100%;touch-action:none;cursor:crosshair;color:var(--ink)"></canvas><canvas data-ov="1" width="576" height="576" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none"></canvas>""")

# ---------- 2. one word for one thing: «иероглиф», not «знак» ----------
rep("""this.wSay('Знак '+(idx+1)+' готов')""", """this.wSay('Иероглиф '+(idx+1)+' готов')""")
rep("""al:'Знак '+(i+1)""", """al:'Иероглиф '+(i+1)""")
rep("""doneL:last?'Готово':'Знак '+(idx+2)""", """doneL:last?'Готово':'Следующий'""")
rep("""this.toast('Сначала напишите знак в клетке')""", """this.toast('Сначала напишите иероглиф в клетке')""")
rep("""wAskL:trace?'Обведите знак':wScr?'Напишите по памяти':'Напишите на бумаге'""",
    """wAskL:trace?'Обведите по контуру: от цифры, по стрелке':wScr?'Напишите по памяти':'Напишите на бумаге'""")

# ---------- 3. the lesson shows where you are: steps in the header, «?» explains the method ----------
rep("""<div style="width:12px"></div></div>
    <span style="text-align:center;font-size:13px;color:var(--mu);padding-bottom:4px">{{ runLabel }}</span>""",
    """<sc-if value="{{ runStepsOn }}" hint-placeholder-val="{{ false }}"><button onClick="{{ howOpen }}" aria-label="Как проходит урок" style="width:32px;height:32px;border-radius:16px;border:1.5px solid var(--ln);background:none;color:var(--mu);font-size:15px;font-weight:700;cursor:pointer;flex:none">?</button></sc-if><sc-if value="{{ runStepsOff }}" hint-placeholder-val="{{ false }}"><div style="width:12px"></div></sc-if></div>
    <sc-if value="{{ runStepsOn }}" hint-placeholder-val="{{ false }}"><div style="display:flex;justify-content:center;flex-wrap:wrap;gap:2px;padding:2px 12px 2px"><sc-for list="{{ runSteps }}" as="r" hint-placeholder-count="4"><span style="font-size:12px;padding:3px 8px;white-space:nowrap;border-radius:10px;background:{{ r.bg }};color:{{ r.fg }};font-weight:{{ r.fw }}">{{ r.l }}</span></sc-for></div></sc-if>
    <span style="text-align:center;font-size:13px;color:var(--mu);padding-bottom:4px">{{ runLabel }}</span>""")
rep("""runLabel=(snow?'Снежный ком · слово ':'Знакомство · ')+(st.li+1)+' из '+n;""", """runLabel='слово '+(st.li+1)+' из '+n;""")
rep("""runLabel=(snow&&les?'Снежный ком · проверка · осталось ':'Выбор · осталось ')+left;""",
    """runLabel=les?'вопросов осталось: '+left:'Выбор · осталось '+left;""")
rep("""runLabel='Обводка · '+(st?st.li:1)+' из '+(st?st.ids.length:1);}""", """runLabel='слово '+(st?st.li:1)+' из '+(st?st.ids.length:1);}""")
rep("""runLabel='Письмо · '+Math.min(qz.i+1,n)+' из '+n+(qz.round>1?' · круг '+qz.round:'');}""",
    """runLabel=(st?'':'Письмо · ')+'слово '+Math.min(qz.i+1,n)+' из '+n+(qz.round>1?' · круг '+qz.round:'');}""")
# values: steps + the explanation sheet
rep("""      runPct,runLabel,exitRun:()=>this.exit(),""",
    """      runPct,runLabel,exitRun:()=>this.exit(),...this.howVals(),""")
rep("""  // ---- writing screen values (v8 layout, 2.9 stroke checking) ----""",
    """  // ---- where the learner is in the lesson, and how the lesson works (text only; the flow itself is unchanged) ----
  howVals(){const s=this.state,st=s.study,snow=(s.method||'fast')==='snow',scr=s.screen,qz=s.quiz;const inLesson=!!st&&['learn','mc','quiz'].includes(scr);
    const names=snow?['Новое слово','Проверка','Письмо']:['Знакомство','Обводка','Выбор','Письмо'];
    let cur=-1;if(inLesson){if(scr==='learn')cur=0;else if(scr==='mc')cur=snow?1:2;else if(qz&&qz.kind==='trace')cur=1;else if(qz&&qz.kind==='check')cur=snow?2:3;}
    const runSteps=names.map((l,i)=>({l,bg:i===cur?'var(--prs)':'transparent',fg:i===cur?'var(--pr)':'var(--mu)',fw:i===cur?600:400}));
    const B=s.chunk||5,iv='1, 3, 7, 14, 30, 60 и 120 дней';
    const howSteps=snow?[
      {n:1,t:'Новое слово',d:'Иероглиф, пиньинь, перевод и звук. «Порядок черт» покажет, как он пишется.'},
      {n:2,t:'Проверка — «снежный ком»',d:'Со второго слова после каждого нового — короткая проверка: перевод ↔ иероглиф. В неё входят слова этого урока, поэтому ком растёт с каждым словом. Ошиблись — вопрос повторится.'},
      {n:3,t:'Письмо по памяти',d:'В конце урока напишите каждое слово сами. Забыли — «Подсказка» покажет контур.'}]:[
      {n:1,t:'Знакомство',d:'Иероглиф, пиньинь, перевод и звук. «Порядок черт» покажет, как он пишется.'},
      {n:2,t:'Обводка',d:'Сразу после знакомства обведите иероглиф по серому контуру. Цифра — где начать черту, стрелка — куда вести.'},
      {n:3,t:'Выбор',d:'После каждых '+B+' слов — быстрая проверка: выберите перевод или иероглиф. Ошиблись — вопрос повторится в конце проверки.'},
      {n:4,t:'Письмо по памяти',d:'В конце урока напишите каждое слово сами. Забыли — «Подсказка» покажет контур.'}];
    return {runSteps,runStepsOn:inLesson,runStepsOff:!inLesson,howOpen:()=>this.setState({sheet:'howto'}),sheetHow:s.sheet==='howto',
      howT:snow?'Как проходит урок: «Снежный ком»':'Как проходит урок',
      howSub:'Каждое новое слово проходит '+(snow?'три':'четыре')+' шага — так оно запоминается и на вид, и по смыслу, и рукой.',howSteps,
      howAfter:'Потом Mao сам напомнит повторить слова — через '+iv+'. Ошибка — слово вернётся завтра.'};}
  // ---- writing screen values (v8 layout, 2.9 stroke checking) ----""")
rep("""      <sc-if value="{{ sheetBackup }}" hint-placeholder-val="{{ false }}">""",
    """      <sc-if value="{{ sheetHow }}" hint-placeholder-val="{{ false }}">
        <div class="scr" style="padding:8px 20px 22px;display:flex;flex-direction:column;gap:12px;overflow-y:auto">
          <span style="font:700 20px 'Noto Serif',serif">{{ howT }}</span>
          <span style="font-size:14px;color:var(--mu);line-height:1.45">{{ howSub }}</span>
          <sc-for list="{{ howSteps }}" as="h" hint-placeholder-count="4"><div style="display:flex;gap:12px;align-items:flex-start"><span style="flex:none;width:28px;height:28px;border-radius:14px;background:var(--prs);color:var(--pr);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px">{{ h.n }}</span><div style="display:flex;flex-direction:column;gap:2px"><span style="font-size:15px;font-weight:600">{{ h.t }}</span><span style="font-size:13.5px;color:var(--mu);line-height:1.4">{{ h.d }}</span></div></div></sc-for>
          <span style="font-size:13.5px;line-height:1.45;padding:10px 12px;border-radius:12px;background:var(--sf2)">{{ howAfter }}</span>
          <button onClick="{{ closeSheet }}" style="width:100%;height:50px;border-radius:14px;border:0;background:var(--pr);color:var(--onpr);font-size:15px;font-weight:600;cursor:pointer">Понятно</button>
        </div>
      </sc-if>
      <sc-if value="{{ sheetBackup }}" hint-placeholder-val="{{ false }}">""")
# shown once, before the first lesson
rep("""  startStudy(day){const s=this.state;day=day??s.cur;""",
    """  startStudy(day){const s=this.state;day=day??s.cur;if(!s.howSeen)setTimeout(()=>{if(this.state.study)this.upd({howSeen:1,sheet:'howto'});},300);""")
rep("""  PK=['m31',""", """  PK=['howSeen','m31',""")

# ---------- 4. the learning card: the word, not the bibliography ----------
rep("""const src=o.mSrc;const meta=[e&&e.lv?'HSK '+e.lv:'',pos,e&&e.cl?'сч. слово '+e.cl.split(',')[0]:'',src==='b'?'перевод: БКРС':src==='user'?'свой перевод':src==='m'?'перевод: Mao':src==='ai'?'перевод нейросети — проверьте':''].filter(Boolean).join(' · ');""",
    """const src=o.mSrc,lrn=o.tag==='learn';const meta=[e&&e.lv?'HSK '+e.lv:'',pos,e&&e.cl?'сч. слово '+e.cl.split(',')[0]:'',src==='b'&&!lrn?'перевод: БКРС':src==='user'?'свой перевод':src==='m'&&!lrn?'перевод: Mao':src==='ai'?'перевод нейросети — проверьте':''].filter(Boolean).join(' · ');""")
rep("""senL:'ЗНАЧЕНИЯ · БКРС',exNote:senV.some(x=>x.xs.length)?""", """senL:lrn?'ЗНАЧЕНИЯ':'ЗНАЧЕНИЯ · БКРС',exNote:!lrn&&senV.some(x=>x.xs.length)?""")
# on the learning card the first dictionary sense usually repeats the translation — skip it when it does
rep("""const nS=o.full?8:3,nX=o.full?2:1;const senV=sen.filter(x=>x.t)""",
    """const nS=o.full?8:3,nX=o.full?2:1;const nzR=t=>String(t||'').toLowerCase().replace(/ё/g,'е').replace(/[^а-яa-z]+/g,' ').trim();const mainR=nzR(o.m);
    if(o.tag==='learn'&&sen.length&&mainR&&nzR(String(sen[0].t).replace(/\\(.*?\\)/g,'')).split(' ').filter(x=>x.length>2).every(x=>mainR.includes(x)))sen=sen.slice(1);
    const senV=sen.filter(x=>x.t)""")

# ---------- 5. home on day one ----------
rep("""    const steps=[stp(dueN?(stIn?'later':'now'):'done','Повторение',dueN?dueN+' '+pl(dueN,WF):'готово'),""",
    """    const steps=[knownN||dueN?stp(dueN?(stIn?'later':'now'):'done','Повторение',dueN?dueN+' '+pl(dueN,WF):'на сегодня всё'):stp('later','Повторение','начнётся после урока'),""")
rep("""      {zh:'考',c:'var(--pr)',l:'Тест',sub:'10 слов',go:()=>this.startTest('quick')},
      {zh:'写',c:'var(--ac)',l:'Прописи',sub:'5 слов от руки',go:()=>this.startTest('write')}];""",
    """      {zh:'考',c:'var(--pr)',l:'Тест',sub:knownN?'10 слов':'после урока',go:()=>this.startTest('quick')},
      {zh:'写',c:'var(--ac)',l:'Прописи',sub:knownN?'5 слов от руки':'после урока',go:()=>this.startTest('write')}];""")

# ---------- 6. answer options: short, clean, from checked translations ----------
rep("""  mcOpts(it){const w=this.W(it.id);if(!w)return [];const sh=m=>String(m||'').split(/[;(]/)[0].trim().slice(0,30);""",
    """  mcOpts(it){const w=this.W(it.id);if(!w)return [];const sh=m=>{let t=String(m||'').split(/[;(]/)[0].trim();if(t.length>28){const ps=t.split(/,\\s*/);t=ps[0];for(const x of ps.slice(1)){if(t.length+x.length>24)break;t+=', '+x;}if(t.length>28)t=t.slice(0,28).replace(/\\s+\\S*$/,'')+'…';}return t.replace(/[\\s,.:]+$/,'');};""")

open(P, 'w', encoding='utf-8').write(s)
print('ok')


# ---------- 7. background work waits while the finger is on the cell (dictionary parse, startup re-renders) ----------
def patch_bg():
    global s
    s = open(P, encoding='utf-8').read()
    rep("""this.drw=true;const [x,y]=this.wPt(e),ov=this.wOv()""", """this.drw=true;window.__maoInk=true;const [x,y]=this.wPt(e),ov=this.wOv()""")
    rep("""this.drw=false;this.pid=null;if(this.state.wMsg)this.setState({wMsg:null});this.wSnapLast();this.wOvClear();}""",
        """this.drw=false;this.pid=null;window.__maoInk=false;if(this.state.wMsg)this.setState({wMsg:null});this.wSnapLast();this.wOvClear();}""")
    rep("""this.wBad=null;this.wSnapAn=null;this.drw=false;this.wOvClear();""", """this.wBad=null;this.wSnapAn=null;this.drw=false;window.__maoInk=false;this.wOvClear();""")
    rep("""WCheck.loadOutlines().then(()=>this.wRender());},1500);if(window.Explain)Explain.load().then(()=>this.forceUpdate());""",
        """WCheck.loadOutlines().then(()=>this.idle(()=>this.wRender()));},300);if(window.Explain)Explain.load().then(()=>this.idle(()=>this.forceUpdate()));""")
    rep("""window.EDict&&EDict.onReady(()=>this.forceUpdate());""", """window.EDict&&EDict.onReady(()=>this.idle(()=>this.forceUpdate()));""")
    rep("""  fixRu(){const s=this.state;if(!window.EDict||!EDict.ready())return;""",
        """  // run f when the finger is not on the writing cell (a full re-render mid-stroke makes the line jerk)
  idle(f){if(this.drw)return setTimeout(()=>this.idle(f),200);f();}
  fixRu(){const s=this.state;if(!window.EDict||!EDict.ready())return;if(this.drw)return setTimeout(()=>this.fixRu(),300);""")
    open(P, 'w', encoding='utf-8').write(s)
    d = '/tmp/claude-0/mao/www/dict.js'
    t = open(d, encoding='utf-8').read()
    a = """    const step = () => {
      const t0 = performance.now();
      while (pos < txt.length && performance.now() - t0 < 25) {"""
    assert t.count(a) == 1
    t = t.replace(a, """    // short slices (12 ms leave room for a 60 Hz frame); paused entirely while the finger draws
    const step = () => {
      if (window.__maoInk) return setTimeout(step, 150);
      const t0 = performance.now();
      while (pos < txt.length && performance.now() - t0 < 12) {""")
    a = """const fin = () => { const t1 = performance.now(); for (; k < out.length && performance.now() - t1 < 25; k++)"""
    assert t.count(a) == 1
    t = t.replace(a, """const fin = () => { if (window.__maoInk) return setTimeout(fin, 150); const t1 = performance.now(); for (; k < out.length && performance.now() - t1 < 12; k++)""")
    open(d, 'w', encoding='utf-8').write(t)
    w = '/tmp/claude-0/mao/www/writecheck.js'
    t = open(w, encoding='utf-8').read()
    a = """    oload = (window.MaoText ? MaoText('outlines.txt') : fetch('outlines.txt').then(r => { if (!r.ok) throw 0; return r.text(); })).then(t => {"""
    assert t.count(a) == 1
    t = t.replace(a, """    const idle = () => new Promise(r => { const f = () => window.__maoInk ? setTimeout(f, 150) : r(); f(); });
    oload = (window.MaoText ? MaoText('outlines.txt') : fetch('outlines.txt').then(r => { if (!r.ok) throw 0; return r.text(); })).then(t => idle().then(() => t)).then(t => {""")
    open(w, 'w', encoding='utf-8').write(t)
    print('bg ok')


if __name__ == '__main__':
    patch_bg()


def patch_fit():
    global s
    s = open(P, encoding='utf-8').read()
    rep("100dvh - 330px", "100dvh - 356px")
    rep("""let cur=-1;if(inLesson){""", """let cur=-1;const lessonQ=!!st&&(scr==='learn'||(scr==='mc'&&s.mc&&s.mc.kind==='lesson')||(scr==='quiz'&&qz&&(qz.kind==='trace'||qz.kind==='check')));if(inLesson){""")
    rep("""runStepsOn:inLesson,runStepsOff:!inLesson,""", """runStepsOn:lessonQ,runStepsOff:!lessonQ,""")
    open(P, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    patch_fit()
