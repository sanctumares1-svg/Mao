#!/usr/bin/env python3
"""Mao 3.1, stage 2: lessons and day plan, saving the lesson, translations in words, goal checks,
empty fields, backup without keys, toasts, small screens. Snowball algorithm is not touched."""
P = '/tmp/claude-0/mao/www/index.html'
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, n, a[:100])
    s = s.replace(a, b)


# ---------- saved state ----------
rep("PK=['m30',", "PK=['m31','study','myRu','m30',")
rep("defaults(){return {m30:1,", "defaults(){return {m31:1,m30:1,myRu:{},study:null,")

# ---------- translations: one source of truth per word ----------
rep("  ruNeed(m){return !m||m==='перевод загружается…'||!/[а-яё]/i.test(m);}",
    """  ruNeed(m){return !m||m==='перевод загружается…'||!/[а-яё]/i.test(m)||/^нет перевода/.test(m);}
  // a word can be learned and tested only with a Russian meaning from the dictionary or written by the user
  mOk(w){return !!w&&!!w.m&&/[а-яё]/i.test(w.m)&&!/^нет перевода|^перевод загружается/.test(w.m)&&w.mSrc!=='none'&&w.mSrc!=='ai';}
  // the dictionary entry of this word's reading (w.k = dictionary key, else the pinyin)
  dictFor(w){if(!window.EDict||!EDict.ready())return null;const L=EDict.best(w.h).filter(e=>e.h===w.h||e.t===w.h);if(!L.length)return null;const nz=x=>String(x||'').replace(/[\\s'’]/g,'').toLowerCase();
    return (w.k&&L.find(e=>e.key===w.k))||L.find(e=>nz(e.p)===nz(w.p)&&e.m)||L.find(e=>nz(e.p)===nz(w.p))||L.find(e=>e.m)||L[0];}
  // meaning for a new word: the user's own translation of this word, else the dictionary, else none (shown honestly)
  ruFor(e){const my=(this.state.myRu||{})[e.key||e.h];if(my)return {m:my,mSrc:'user'};if(e.m&&/[а-яё]/i.test(e.m))return {m:e.m,mSrc:e.src||'m'};return {m:'',mSrc:'none'};}""")

# fixRu: normalise every saved word against the new dictionary (keeps user edits)
rep("""      this.upd({words,m29fix:true});if(fixed||flag)setTimeout(()=>this.toast('Переводы проверены: исправлено '+fixed+(flag?', проверьте вручную '+flag+' («Слова» → кнопка правки у урока)':'')),800);return setTimeout(()=>this.fixRu(),50);}""",
    """      this.upd({words,m29fix:true});return setTimeout(()=>this.fixRu(),50);}
    {let ch=0;const words=this.state.words.map(w=>{if(w.mEdited)return w.mSrc==='user'?w:(ch++,{...w,mSrc:'user'});const e=this.dictFor(w);
      if(e&&e.m&&/[а-яё]/i.test(e.m)){if(w.m!==e.m||w.mSrc!==e.src||w.k!==e.key){ch++;return {...w,m:e.m,mSrc:e.src||'m',k:e.key};}return w;}
      if(this.ruNeed(w.m)){if(w.m!==''||w.mSrc!=='none'){ch++;return {...w,m:'',mSrc:'none',...(e?{k:e.key}:{})};}return w;}
      if(w.mSrc!=='ai'){ch++;return {...w,mSrc:'ai'};}return w;});
      if(ch||!this.state.m31)this.upd({words,m31:1});}""")
rep("""s.words.forEach(w=>{if(!this.ruNeed(w.m))return;const e=EDict.find(w.h);if(e&&e.m&&/[а-яё]/i.test(e.m)){upd.push([w.id,e.m]);return;}if(!ai){if(w.m==='перевод загружается…')upd.push([w.id,'нет перевода — впишите в «Править урок»']);return;}need.push""",
    """s.words.forEach(w=>{if(!this.ruNeed(w.m)||w.mSrc==='none'||!ai||true)return;need.push""")

# new words get their meaning from the dictionary (or honestly none)
rep("""    const mk=(h,o)=>{const e=window.EDict&&EDict.find(h);return {h,t:e&&e.t||'',p:(o&&o.p)||(e&&e.p)||'',m:(e&&e.m&&/[а-яё]/i.test(e.m)?e.m:'')||(o&&o.m)||'перевод загружается…',en:e&&e.en||'',hsk:!!(e&&e.hsk)};};""",
    """    const mk=(h,o)=>{const e=window.EDict&&EDict.find(h);const r=e?this.ruFor(e):{m:'',mSrc:'none'};const ai=!r.m&&o&&o.m;return {h,t:e&&e.t||'',p:(e&&e.p)||(o&&o.p)||'',m:r.m||(ai?o.m:''),mSrc:r.m?r.mSrc:(ai?'ai':'none'),k:e?e.key:'',en:e&&e.en||'',hsk:!!(e&&e.hsk)};};""")
rep("""    let id=this.state.nextId;const add=list.map(x=>({id:id++,...x,d:this.state.cur,s:'new',due:false}));""",
    """    let id=this.state.nextId;const add=list.filter(x=>x.m).map(x=>({id:id++,...x,d:this.state.cur,s:'new',due:false}));""")
rep("""const prev=s.words;const ru=(e.m&&/[а-яё]/i.test(e.m)?e.m:'')||(window.EDict&&e.key?EDict.ru(e.key):'');
    const w={id:s.nextId,h:e.h,t:e.t,p:e.p,m:ru||'перевод загружается…',en:e.en||'',d:n,s:'new',due:false,hsk:e.hsk!=null?!!e.hsk:!!(window.EDict&&EDict.isHsk(e.h))};
    if(!ru&&window.EDict&&this.aiOn())EDict.translate([{...e,key:e.key||('w|'+e.h),en:e.en||'?'}],()=>{const r2=EDict.ru(e.key||('w|'+e.h));if(r2)this.upd({words:this.state.words.map(x=>x.id===w.id&&this.ruNeed(x.m)?{...x,m:r2}:x)});});""",
    """const prev=s.words;const r=this.ruFor(e);
    const w={id:s.nextId,h:e.h,t:e.t,p:e.p,m:r.m,mSrc:r.mSrc,k:e.key||'',en:e.en||'',d:n,s:'new',due:false,hsk:e.hsk!=null?!!e.hsk:!!(window.EDict&&EDict.isHsk(e.h))};""")
rep("""    this.toast(e.h+' → урок '+n,()=>this.upd({words:prev}));}""",
    """    this.toast(r.m?e.h+' → урок '+n:e.h+' → урок '+n+' · русского перевода нет — впишите его в «Править урок»',()=>this.upd({words:prev}));}""")
rep("""    const add=R.map(r=>({id:id++,h:r.h,t:r.t||'',p:r.p||'',m:r.m||'перевод загружается…',en:r.en||'',d:r.d||tg,s:'new',due:false,hsk:r.hsk!=null?!!r.hsk:!!(window.EDict&&EDict.isHsk(r.h))}));""",
    """    const add=R.map(r=>{const my=(this.state.myRu||{})[r.ekey||r.h];const m=my||(r.m&&/[а-яё]/i.test(r.m)?r.m:'');return {id:id++,h:r.h,t:r.t||'',p:r.p||'',m,mSrc:my?'user':m?(r.own?'user':(r.src||'m')):'none',k:r.ekey||'',en:r.en||'',d:r.d||tg,s:'new',due:false,hsk:r.hsk!=null?!!r.hsk:!!(window.EDict&&EDict.isHsk(r.h))};});""")
rep("""      rows.push({key,h:e.h,t:e.t,p:e.p,m:it.m||e.m||'',en:e.en,hsk:e.hsk,lv:e.lv,ekey:e.key,kind:have.has(e.h)?'have':'ok',d:it.d,alts:L.length,ai});};""",
    """      rows.push({key,h:e.h,t:e.t,p:e.p,m:it.m||e.m||'',own:!!it.m,src:e.src,en:e.en,hsk:e.hsk,lv:e.lv,ekey:e.key,kind:have.has(e.h)?'have':'ok',d:it.d,alts:L.length,ai});};""")
rep("""rows.push({key,h:it.q,p:toMarks(it.p||'')||p,m:it.m||'',kind:have.has(it.q)?'have':'nodict',d:it.d,alts:0,ai:0});}""",
    """rows.push({key,h:it.q,p:toMarks(it.p||'')||p,m:it.m||'',own:!!it.m,kind:have.has(it.q)?'have':'nodict',d:it.d,alts:0,ai:0});}""")
rep("""return {id:id++,h:String(o.h),p:toMarks(String(o.p||''))||(e&&e.p)||'',m:String(o.m||o.ru||(e&&e.m)||o.en||(e&&e.en)||''),d:""",
    """const own=String(o.m||o.ru||'');const ok=/[а-яё]/i.test(own);return {id:id++,h:String(o.h),p:toMarks(String(o.p||''))||(e&&e.p)||'',m:ok?own:((e&&e.m)||''),mSrc:ok?'user':(e&&e.m?(e.src||'m'):'none'),k:e?e.key:'',d:""")

# editing: draft while typing, nothing empty is kept; the user's translation is remembered for the word
rep("""  deWord(id,f,v){this.upd({words:this.state.words.map(w=>w.id===id?{...w,[f]:v,...(f==='m'?{mEdited:true,mSrc:null}:{})}:w)});}""",
    """  deWord(id,f,v){const w0=this.W(id);const de=this.state.de||{};const orig={...(de.orig||{})};if(w0&&!orig[id])orig[id]={p:w0.p,m:w0.m,mSrc:w0.mSrc,mEdited:w0.mEdited};
    this.setState({de:{...de,orig}});this.upd({words:this.state.words.map(w=>w.id===id?{...w,[f]:v,...(f==='m'?{mEdited:true,mSrc:'user'}:{})}:w)});}
  // leaving the lesson editor: an emptied field goes back to what it was; a new translation is remembered for this word
  deCommit(){const s=this.state,de=s.de;if(!de)return;const orig=de.orig||{};let back=0;const my={...(s.myRu||{})};
    const words=s.words.map(w=>{if(!orig[w.id])return w;let x=w;if(!String(x.p||'').trim()){x={...x,p:orig[w.id].p};back++;}
      if(!String(x.m||'').trim()){const o=orig[w.id];x={...x,m:o.m,mSrc:o.mSrc,mEdited:o.mEdited};back++;}
      else if(x.m!==orig[w.id].m&&x.mSrc==='user')my[x.k||x.h]=x.m.trim();return x;});
    const L=s.lessons.find(l=>l.n===de.n);let lessons=s.lessons;if(L&&!String(L.t||'').trim()){lessons=s.lessons.map(l=>l.n===de.n?{...l,t:de.t0||'Урок '+de.n}:l);back++;}
    this.upd({words,lessons,myRu:my});if(back)this.toast('Пустые поля не сохраняются — вернула прежние значения');}""")

# ---------- learning only words with a Russian meaning (the snowball and fast lesson themselves are unchanged) ----------
rep("""    const ids=this.dw(day).filter(w=>w.s==='new').map(w=>w.id);
    if(!ids.length)return this.startTest('lesson',day);""",
    """    const nw=this.dw(day).filter(w=>w.s==='new');const ids=nw.filter(w=>this.mOk(w)).map(w=>w.id);
    if(!ids.length&&nw.length){this.setState({screen:'dayEdit',de:{n:day,t0:(this.state.lessons.find(l=>l.n===day)||{}).t}});return this.toast('У этих слов нет русского перевода — впишите его, и урок начнётся');}
    if(!ids.length)return this.startTest('lesson',day);""")
rep("""    if(!list.length)return this.toast(kind==='write'||kind==='quick'?'Пока нет выученных слов — начните с урока':'Пока нечего проверять');
    const ids=list.map(w=>w.id);""",
    """    list=list.filter(w=>this.mOk(w));
    if(!list.length)return this.toast(kind==='write'||kind==='quick'?'Пока нет выученных слов — начните с урока':'Пока нечего проверять');
    const ids=list.map(w=>w.id);""")
rep("""shuffle(this.state.words.filter(x=>x.id!==it.id&&x.m&&!this.ruNeed(x.m)&&!/^нет перевода/.test(x.m))).slice(0,6).forEach(add);""",
    """shuffle(this.state.words.filter(x=>x.id!==it.id&&this.mOk(x))).slice(0,6).forEach(add);""")

# ---------- goal: no zero, not below what is already known ----------
rep("""  saveGoal(gd){const n=+gd.n||0;if(n<1)return this.toast('Укажите, сколько слов хотите выучить');const p=this.goalPlan(gd,this.state.words.filter(w=>w.s!=='new').length);if(!p.days)return this.toast('Дата должна быть позже сегодняшней');""",
    """  saveGoal(gd){const n=+gd.n||0;const kn=this.state.words.filter(w=>w.s!=='new').length;if(n<1)return this.toast('Укажите, сколько слов хотите выучить');if(n<=kn)return this.toast('Вы уже знаете '+kn+' '+pl(kn,WF)+' — поставьте цель больше');const p=this.goalPlan(gd,kn);if(!p.days)return this.toast('Дата должна быть позже сегодняшней');""")

# ---------- streak shown as it is today ----------
rep("""  goalDraft(){""", """  // the streak as of today: a missed study day (weekends off are not missed) means it has ended
  streakNow(){const s=this.state;if(!s.lastActive||!s.streak)return 0;const today=dk(new Date());if(s.lastActive===today||s.lastActive===dk(ago(1)))return s.streak;
    const g=s.goal;if(g&&g.offOn){for(let i=1;i<30;i++){const d=ago(i);if(dk(d)===s.lastActive)return s.streak;if(!(g.off||[6,0]).includes(d.getDay()))return 0;}}return 0;}
  goalDraft(){""")

# ---------- toasts: belong to the screen they were shown on ----------
rep("""  toast(msg,act,actL){clearTimeout(this.tt);this.setState({toast:{msg,act:typeof act==='function'?act:null,actL:actL||'Вернуть'}});""",
    """  toast(msg,act,actL){clearTimeout(this.tt);this.setState({toast:{msg,act:typeof act==='function'?act:null,actL:actL||'Вернуть',scr:this.state.screen==='tab'?'tab:'+this.state.tab:this.state.screen}});""")

# backup: keys stay on this phone only
rep("""  restoreText(t){let o=null;try{o=JSON.parse(t);}catch(e){}this.setState({sheet:null});
    if(o&&!Array.isArray(o)&&Array.isArray(o.words)&&Array.isArray(o.lessons)){const prev=this.pkData();this.upd({...migrate(o),onboarded:true,screen:'tab',study:null,quiz:null,mc:null});""",
    """  backupText(){this.save();let o={};try{o=JSON.parse(localStorage.getItem(KEY)||'{}');}catch(e){}delete o.aiKeys;o.backupOf='Mao '+APPV;o.backupAt=new Date().toISOString();return JSON.stringify(o);}
  restoreText(t){let o=null;try{o=JSON.parse(t);}catch(e){}this.setState({sheet:null});
    if(o&&!Array.isArray(o)&&Array.isArray(o.words)&&Array.isArray(o.lessons)){const prev=this.pkData();const keep={aiKeys:this.state.aiKeys,aiProv:this.state.aiProv};delete o.aiKeys;this.upd({...this.defaults(),...migrate(o),...keep,onboarded:true,screen:'tab',study:o.study||null,quiz:null,mc:null},()=>this.fixRu());""")

# ---------- day plan on Today (K2), learning any lesson (K1) ----------
rep("""    const curW=this.dw(cur),newW=curW.filter(w=>w.s==='new'),hasCur=!!cur&&s.lessons.some(l=>l.n===cur);""",
    """    const curW=this.dw(cur),newW=curW.filter(w=>w.s==='new'&&this.mOk(w)),hasCur=!!cur&&s.lessons.some(l=>l.n===cur);
    const today0=iso(new Date());const nextDay=hasCur&&!newW.length&&curW.length&&(L.date||'')<today0;
    const other=s.lessons.filter(l=>l.n!==cur).map(l=>({l,n:this.dw(l.n).filter(w=>w.s==='new'&&this.mOk(w)).length})).find(x=>x.n>0);""")
rep("""    else if(isWkOff)hero=""", """    else if(other&&!dueN)hero={t:'Урок '+other.l.n+' · '+other.l.t,sub:other.n+' '+pl(other.n,['новое слово','новых слова','новых слов'])+' ещё не выучено',btn:'Учить',go:()=>this.startStudy(other.l.n),chips:this.dw(other.l.n).filter(w=>w.s==='new'&&this.mOk(w)).slice(0,12).map(w=>({h:w.h})),done:false};
    else if(nextDay&&!isWkOff)hero={t:'Урок '+(cur+1)+' · '+topic,sub:'Новый урок на сегодня · '+daily+' '+pl(daily,WF)+' · Mao подберёт их из словаря',btn:s.clBusy?'Подбираю слова…':'Учить',go:()=>!s.clBusy&&this.moreLesson(),chips:[],done:false,link:true,linkL:'Другая тема'};
    else if(isWkOff)hero=""")
rep("""    const lessonState=!hasCur?'later':newW.length?(dueN&&!stIn?'later':'now'):curW.length?'done':'now';
    const steps=[stp(dueN?(stIn?'later':'now'):'done','Повторение',dueN?dueN+' '+pl(dueN,WF):'готово'),
      stp(lessonState,hasCur?lessonL(cur):'Урок 1 · '+topic,hasCur?(newW.length?newW.length+' '+pl(newW.length,['новое','новых','новых']):curW.length?'выучен':'пуст'):daily+' '+pl(daily,['новое','новых','новых']))];""",
    """    const lessonState=!hasCur?'later':newW.length?(dueN&&!stIn?'later':'now'):nextDay?(dueN?'later':'now'):curW.length?'done':'now';
    const steps=[stp(dueN?(stIn?'later':'now'):'done','Повторение',dueN?dueN+' '+pl(dueN,WF):'готово'),
      nextDay?stp(lessonState,'Урок '+(cur+1)+' · '+topic,daily+' '+pl(daily,['новое','новых','новых'])):
      stp(lessonState,hasCur?lessonL(cur):'Урок 1 · '+topic,hasCur?(newW.length?newW.length+' '+pl(newW.length,['новое','новых','новых']):curW.length?'выучен':'пуст'):daily+' '+pl(daily,['новое','новых','новых']))];""")
rep("""    const days=[...s.lessons].reverse().map(l=>{const lw=this.dw(l.n),k=lw.filter(w=>w.s!=='new').length;return {title:'Урок '+l.n+' · '+l.t,stat:k+' из '+lw.length,empty:!lw.length,add:()=>this.openAdd(l.n,'one'),""",
    """    const days=[...s.lessons].reverse().map(l=>{const lw=this.dw(l.n),k=lw.filter(w=>w.s!=='new').length,hd=lw.filter(w=>w.s==='hard').length,nn=lw.filter(w=>w.s==='new'&&this.mOk(w)).length,nt=lw.filter(w=>!this.mOk(w)).length;
      const stat=lw.length?[k?(k-hd)+' '+pl(k-hd,['выучено','выучено','выучено']):'',hd?hd+' '+pl(hd,['трудное','трудных','трудных']):'',nn?nn+' '+pl(nn,['новое','новых','новых']):'',nt?nt+' без перевода':''].filter(Boolean).join(' · '):'пусто';
      return {title:'Урок '+l.n+' · '+l.t,stat,empty:!lw.length,add:()=>this.openAdd(l.n,'one'),canLearn:nn>0,learnL:'Учить · '+nn,learn:()=>this.startStudy(l.n),""")
rep("""      edit:()=>this.setState({screen:'dayEdit',de:{n:l.n}}),canRep:k>0,rep:()=>this.startTest('lesson',l.n)};});""",
    """      edit:()=>this.setState({screen:'dayEdit',de:{n:l.n,t0:l.t}}),canRep:k>0&&!nn,rep:()=>this.startTest('lesson',l.n),
      ws:lw.map(w=>({h:w.h,p:w.p,open:openW(w.id),dot:!this.mOk(w)?'var(--ac)':w.s==='hard'?'var(--bad)':w.s==='new'?'transparent':'var(--ok)'}))};});""")
rep("""      ws:lw.map(w=>({h:w.h,p:w.p,open:openW(w.id),dot:w.s==='hard'?'var(--bad)':w.s==='new'?'transparent':'var(--ok)'})),
""", "")

# tiles: say what each training does
rep("""{zh:'考',c:'var(--pr)',l:'Тест',sub:'по прошлым урокам',go:()=>this.startTest('quick')},""",
    """{zh:'考',c:'var(--pr)',l:'Тест',sub:'10 выученных слов',go:()=>this.startTest('quick')},""")
rep("""{zh:'写',c:'var(--ac)',l:'Прописи',sub:'5 знаков',go:()=>this.startTest('write')}];""",
    """{zh:'写',c:'var(--ac)',l:'Прописи',sub:'5 слов от руки',go:()=>this.startTest('write')}];""")

# streak, goal texts
rep("""      streakL:s.streak+' '+pl(s.streak,['день','дня','дней'])+' подряд',""",
    """      streakL:(()=>{const k=this.streakNow();return k?k+' '+pl(k,['день','дня','дней'])+' подряд':(s.lastActive?'новая серия':'первый день');})(),""")
rep("""      gPer,gSub:gp.days?gp.days+' учебных '+pl(gp.days,DF)+' · осталось выучить '+gp.left+(gp.raw>20?'. Это много — лучше отодвинуть дату':''):'',
      gBtn:firstRun?'Начать учиться':'Сохранить цель',""",
    """      gPer:(+gd.n||0)<1?'Укажите число слов':(+gd.n<=knownN?'Цель уже достигнута':gPer),gSub:(+gd.n||0)<1?'':+gd.n<=knownN?'Вы уже знаете '+knownN+' '+pl(knownN,WF)+' — поставьте больше':gp.days?gp.days+' учебных '+pl(gp.days,DF)+' · осталось выучить '+gp.left+(gp.raw>20?'. Это много — лучше отодвинуть дату':''):'',
      gBtn:(firstRun?'Начать':'Сохранить')+(gp.days&&+gd.n>knownN?' · '+gp.per+' '+pl(gp.per,WF)+' в день':''),""")
# settings: the day norm and the goal stay in sync visibly
rep("""      daily,dailyDn:()=>this.upd({dailyNew:Math.max(3,daily-1)}),dailyUp:()=>this.upd({dailyNew:Math.min(20,daily+1)}),""",
    """      daily,dailyDn:()=>this.upd({dailyNew:Math.max(3,daily-1)}),dailyUp:()=>this.upd({dailyNew:Math.min(30,daily+1)}),
      dailyWarn:!!(g&&GL.days&&GL.per>daily),dailyWarnL:g&&GL.days&&GL.per>daily?'Для цели к '+fmtD(pISO(g.date))+' нужно '+GL.per+' '+pl(GL.per,WF)+' в день. С нормой '+daily+' вы успеете примерно к '+fmtD(this.finishDate(g,knownN,daily)):'',""")
rep("""  goalDraft(){""", """  finishDate(g,known,per){const left=Math.max(0,(+g.n||0)-known);let need=Math.ceil(left/Math.max(1,per));const d=day0(new Date());while(need>0){d.setDate(d.getDate()+1);const wd=d.getDay();if(!g.offOn||(wd!==0&&wd!==6))need--;}return d;}
  goalDraft(){""")

# backup export without keys
rep("""      exportJson:()=>{this.save();const name='mao-backup-'+iso(new Date())+'.json';const ok=window.EVINE?EVINE.saveFile(name,localStorage.getItem(KEY)||'{}'):false;""",
    """      exportJson:()=>{const name='mao-backup-'+iso(new Date())+'.json';const txt=this.backupText();let ok=false;if(window.EVINE&&EVINE.native)ok=EVINE.saveFile(name,txt);else{try{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([txt],{type:'application/json'}));a.download=name;a.click();ok=true;}catch(e){}}""")

# day editor: commit on leaving
rep("""deBack:()=>this.setState({screen:'tab',tab:'words',de:null}),""",
    """deBack:()=>{this.deCommit();this.setState({screen:'tab',tab:'words',de:null});},deNeed:lw.filter(w=>!this.mOk(w)).length,""")
rep("""deRows:lw.map(w=>({h:w.h,p:w.p||'',m:w.m||'',mbd:w.mSrc==='ai'?'var(--bad)':'var(--ln)',""",
    """deRows:lw.map(w=>({h:w.h,p:w.p||'',m:w.m||'',mph:this.mOk(w)?'':'русского перевода в словаре нет — впишите',mbd:!this.mOk(w)?'var(--ac)':'var(--ln)',""")
rep("""deWarn:lw.some(w=>w.mSrc==='ai'),""", """deWarn:lw.some(w=>!this.mOk(w)),""")

# add: choose the lesson from a list
rep("""      cycleAddDay:()=>{const ns=[...s.lessons.map(l=>l.n)];const nw=(ns.length?Math.max(...ns):0)+1;ns.push(nw);const i=ns.indexOf(addDay);this.setState({addDay:ns[(i+1)%ns.length]});},""",
    """      cycleAddDay:()=>this.setState({sheet:'pickDay'}),sheetPickDay:s.sheet==='pickDay',
      pickDays:[...[...s.lessons].reverse().map(l=>({l:'Урок '+l.n+' · '+l.t,sub:this.dw(l.n).length+' '+pl(this.dw(l.n).length,WF),on:l.n===addDay,go:()=>this.setState({addDay:l.n,sheet:null})})),{l:'Новый урок',sub:'тема «'+topic+'»',on:!s.lessons.some(l=>l.n===addDay),go:()=>this.setState({addDay:(s.lessons.reduce((a,l)=>Math.max(a,l.n),0))+1,sheet:null})}].map(x=>({...x,bd:x.on?'var(--pr)':'var(--ln)',bg:x.on?'var(--prs)':'transparent'})),""")

# toasts: only on their screen; on the writing screen at the top, away from the cell
rep("""    const toastBottom=scr==='tab'?84:(scr==='learn'||scr==='quiz')?150:(scr==='add'||scr==='dayEdit'||scr==='goal'||scr==='result')?96:20;""",
    """    const scrKey=scr==='tab'?'tab:'+tab:scr;const toastOn=!!s.toast&&(!s.toast.scr||s.toast.scr===scrKey);const toastUp=scr==='quiz'||scr==='mc'||scr==='learn';
    const toastBottom=scr==='tab'?84:(scr==='add'||scr==='dayEdit'||scr==='goal'||scr==='result')?96:20;""")
rep("""      hasToast:!!s.toast,""", """      hasToast:toastOn,toastPos:toastUp?'top:64px':'bottom:'+toastBottom+'px',""")

# ---------- template ----------
rep("""<div style="position:absolute;left:16px;right:16px;bottom:{{ toastBottom }}px;z-index:30;""",
    """<div style="position:absolute;left:16px;right:16px;{{ toastPos }};z-index:30;""")
# lesson card: Учить
rep("""<span style="flex:1;min-width:0;display:flex;flex-direction:column;gap:1px"><span style="font-size:15px;font-weight:600">{{ d.title }}</span><span style="font-size:13px;color:var(--mu)">{{ d.stat }}</span></span>""",
    """<span style="flex:1;min-width:0;display:flex;flex-direction:column;gap:1px"><span style="font-size:15px;font-weight:600;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical">{{ d.title }}</span><span style="font-size:12.5px;color:var(--mu)">{{ d.stat }}</span></span><sc-if value="{{ d.canLearn }}" hint-placeholder-val="{{ false }}"><button onClick="{{ d.learn }}" style="height:36px;padding:0 12px;border-radius:10px;border:0;background:var(--pr);color:var(--onpr);font-size:13px;font-weight:600;cursor:pointer;flex:none">{{ d.learnL }}</button></sc-if>""")
# hero title: at most 3 lines
rep("""        <span style="font:700 27px/1.2 'Noto Serif','Noto Serif SC',serif">{{ hero.t }}</span>""",
    """        <span style="font:700 27px/1.2 'Noto Serif','Noto Serif SC',serif;overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical">{{ hero.t }}</span>""")
# settings warning under the day norm
rep("""<span style="font-size:12.5px;color:var(--mu);line-height:1.4">Это один урок. Хочется больше — «Ещё урок» на главной</span></div>""",
    """<span style="font-size:12.5px;color:var(--mu);line-height:1.4">Это один урок. Хочется больше — «Ещё урок» на главной</span><sc-if value="{{ dailyWarn }}" hint-placeholder-val="{{ false }}"><span style="font-size:12.5px;color:var(--ac);line-height:1.4">{{ dailyWarnL }}</span></sc-if></div>""")
# day editor: placeholder for a missing translation
rep("""<input value="{{ r.m }}" onChange="{{ r.onM }}" aria-label="Перевод" style=""", """<input value="{{ r.m }}" onChange="{{ r.onM }}" placeholder="{{ r.mph }}" aria-label="Перевод" style=""")
rep("""Перевод с красной рамкой не из словаря — проверьте его.""", """У слов с оранжевой рамкой нет русского перевода в словаре. Впишите свой — после этого слово можно учить.""")
# writing cell: fits short screens, tabs wrap
rep("""<div style="position:relative;width:min(288px,calc(100vw - 48px));aspect-ratio:1;flex:none;border-radius:14px;""",
    """<div style="position:relative;width:min(288px,calc(100vw - 48px),calc(100dvh - 330px));min-width:200px;aspect-ratio:1;flex:none;border-radius:14px;""")
rep("""<sc-if value="{{ wTabsShow }}" hint-placeholder-val="{{ false }}"><div style="display:flex;gap:8px">""",
    """<sc-if value="{{ wTabsShow }}" hint-placeholder-val="{{ false }}"><div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center">""")
# lesson picker sheet
rep("""      <sc-if value="{{ sheetBackup }}" hint-placeholder-val="{{ false }}">""",
    """      <sc-if value="{{ sheetPickDay }}" hint-placeholder-val="{{ false }}">
        <div class="scr" style="padding:8px 20px 20px;display:flex;flex-direction:column;gap:8px;overflow-y:auto">
          <span style="font:700 20px 'Noto Serif',serif">В какой урок добавить</span>
          <sc-for list="{{ pickDays }}" as="d" hint-placeholder-count="3"><button onClick="{{ d.go }}" style="display:flex;flex-direction:column;align-items:flex-start;gap:2px;padding:12px 16px;border-radius:14px;border:1.5px solid {{ d.bd }};background:{{ d.bg }};color:var(--ink);text-align:left;cursor:pointer"><span style="font-size:15px;font-weight:600">{{ d.l }}</span><span style="font-size:12.5px;color:var(--mu)">{{ d.sub }}</span></button></sc-for>
        </div>
      </sc-if>
      <sc-if value="{{ sheetBackup }}" hint-placeholder-val="{{ false }}">""")
open(P, 'w', encoding='utf-8').write(s)
print('ok')
s = open(P, encoding='utf-8').read()
# the saved lesson and the chosen next topic were reset by the initial state on every start
rep(",view:null,study:null,quiz:null,result:null,", ",view:null,quiz:null,result:null,")
rep(",manOpen:false,topicSel:null,clBusy:false};", ",manOpen:false,clBusy:false};")
open(P, 'w', encoding='utf-8').write(s)
print('ok2')
