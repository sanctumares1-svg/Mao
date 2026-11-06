//@@ toast
  toast(msg,act,actL){clearTimeout(this.tt);this.setState({toast:{msg,act:typeof act==='function'?act:null,actL:actL||'Вернуть'}});this.tt=setTimeout(()=>this.setState({toast:null}),act?5200:3800);}
//@@ componentDidMount
  componentDidMount(){window.__app=this;setTimeout(()=>{if(window.WCheck&&WCheck.loadOutlines)WCheck.loadOutlines().then(()=>this.wRender());},1500);if(window.Explain)Explain.load().then(()=>this.forceUpdate());if(window.__updQ){window.__updQ.forEach(u=>this.onUpdate(u));window.__updQ=null;}setTimeout(()=>this.fixRu(),2500);window.EDict&&EDict.onReady(()=>setTimeout(()=>this.fixRu(),800));window.EDict&&EDict.onReady(()=>this.forceUpdate());window.WCheck&&setTimeout(()=>WCheck.load(),1500);this.mq=window.matchMedia('(prefers-color-scheme: dark)');this.mqh=()=>this.forceUpdate();this.mq.addEventListener?.('change',this.mqh);}
//@@ componentWillUnmount
  componentWillUnmount(){this.mq?.removeEventListener?.('change',this.mqh);clearInterval(this.si);clearTimeout(this.tt);}
//@@ componentDidUpdate
  componentDidUpdate(pp,ps){const st0=this.state;ps=this._ps||{};this._ps={chat:st0.chat,screen:st0.screen,tab:st0.tab};const b=st0.quiz,a=this._pq;this._pq=b?{i:b.i,round:b.round,ids:b.ids}:null;if((b&&(!a||a.i!==b.i||a.round!==b.round||a.ids!==b.ids))||(a&&!b))this.wReset();if((ps.chat!==st0.chat||ps.tab!==st0.tab)&&this.chatRef.current)this.chatRef.current.scrollTop=1e6;
    if(st0.screen==='tab'&&this.updToast&&st0.onboarded){const u=this.updToast;this.updToast=null;setTimeout(()=>{if(this.state.screen==='tab')this.toast(u.type==='web'?'Обновление загружено':'Доступна версия '+(u.name||''),()=>this.applyUpd(),u.type==='web'?'Перезапустить':'Обновить');},1200);}}
//@@ aiOn
  // the neural network is optional (Settings → Нейросеть). Off = everything works offline.
  aiOn(){const s=this.state;if(s.aiOn!==true)return false;const P=PROV[s.aiProv||'free']||PROV.free;if(!P.key)return !!(window.claude&&window.claude.complete);return !!((s.aiKeys||{})[s.aiProv]);}
//@@ ask
  async ask(p){if(!this.aiOn())throw 0;return await this.aiChat([{role:'system',content:AISYS},{role:'user',content:p}],null);}
  // one client for every provider: free (no key) or an OpenAI-compatible chat/completions with the user's key; the answer streams in
  aiChat(msgs,onChunk){const s=this.state,prov=s.aiProv||'free',P=PROV[prov]||PROV.free;
    if(!P.key){const flat=msgs.map(m=>(m.role==='system'?'':m.role==='user'?'Ученик: ':'Учитель: ')+m.content).join('\n')+'\nУчитель:';
      return Promise.race([window.claude.complete(flat),new Promise((_,r)=>setTimeout(()=>r(Object.assign(new Error('timeout'),{code:0})),60000))]).then(t=>{t=String(t);onChunk&&onChunk(t);return t;});}
    const key=(s.aiKeys||{})[prov]||'';
    return new Promise((res,rej)=>{const id='a'+(++AISEQ);const T0=setTimeout(()=>{delete AIP[id];rej(Object.assign(new Error('timeout'),{code:0}));},90000);
      AIP[id]={on:t=>onChunk&&onChunk(t),res:t=>{clearTimeout(T0);res(t);},rej:e=>{clearTimeout(T0);rej(e);}};
      try{if(window.EvineNative&&EvineNative.chat)EvineNative.chat(id,prov,key,JSON.stringify({messages:msgs}));else aiFetch(id,P,key,msgs);}catch(e){delete AIP[id];clearTimeout(T0);rej(e);}});}
  checkApi(){const s=this.state;if(s.aiOn!==true)return;const P=PROV[s.aiProv||'free']||PROV.free;if(P.key&&!(s.aiKeys||{})[s.aiProv])return this.setState({apiOk:false,apiMs:'Вставьте ключ '+P.n});if(!P.key&&!(window.claude&&claude.complete))return this.setState({apiOk:false,apiMs:'Проверка работает в приложении на телефоне'});
    const t0=Date.now();this.setState({clBusy:true,apiMs:''});this.ask('Ответь одним словом по-китайски: привет').then(()=>{const sec=((Date.now()-t0)/1000).toFixed(1).replace('.',',');this.setState({apiOk:true,clBusy:false,apiMs:'Работает · ответ за '+sec+' с'});if(window.EDict)EDict.retry();this.fixRu();}).catch(er=>this.setState({apiOk:false,clBusy:false,apiMs:aiErr(er)}));}
//@@ sendChat
  async sendChat(txt){txt=(txt||'').trim();if(!txt||this.state.chatBusy)return;const chat=[...this.state.chat,{r:'me',t:txt}];this.setState({chat,chatQ:'',chatBusy:true});const seq=this.chatSeq||0;
    const put=(m)=>{if((this.chatSeq||0)!==seq)return;const c=[...this.state.chat];const i=c.findIndex(x=>x.live);if(i>=0)c[i]=m;else c.push(m);this.setState({chat:c});};
    if(!this.aiOn()){const ans=this.offlineMao(txt);setTimeout(()=>{put({r:'ai',t:ans});this.setState({chatBusy:false});},250);return;}
    const msgs=[{role:'system',content:AISYS},...chat.slice(-10).map(m=>({role:m.r==='me'?'user':'assistant',content:m.t}))];
    try{const full=await this.aiChat(msgs,t=>put({r:'ai',t:clean(t),live:true}));put({r:'ai',t:clean(full)||'…'});}
    catch(e){put({r:'ai',t:this.offlineMao(txt),note:aiErr(e)+' — ответ из словаря'});}
    if((this.chatSeq||0)===seq)this.setState({chatBusy:false});}
//@@ startTest
  startTest(kind,arg,title){const s=this.state,ws=s.words,isRv=w=>this.isDue(w);let list;
    if(kind==='review'){list=ws.filter(isRv);title='Повторение';}
    else if(kind==='quick'){const pool=ws.filter(w=>w.s!=='new');list=[...shuffle(pool.filter(isRv)),...shuffle(pool.filter(w=>!isRv(w)))].slice(0,10);title='Тест';}
    else if(kind==='write'){const pool=ws.filter(w=>w.s!=='new');list=[...shuffle(pool.filter(isRv)),...shuffle(pool.filter(w=>!isRv(w)))].slice(0,5);title='Прописи';}
    else if(kind==='hard'){list=ws.filter(w=>w.s==='hard');title='Трудные слова';}
    else if(kind==='ids'){list=(arg||[]).map(id=>this.W(id)).filter(Boolean);title=title||'Повторение';}
    else{const l=this.dw(arg);list=l.filter(w=>w.s!=='new');if(!list.length)list=l;title='Урок '+arg;}
    if(!list.length)return this.toast(kind==='write'||kind==='quick'?'Пока нет выученных слов — начните с урока':'Пока нечего проверять');
    const ids=list.map(w=>w.id);
    if(kind==='write'){const qz=this.mkQuiz(ids,title,'test');qz.write=true;return this.setState({screen:'quiz',quiz:qz,sheet:null,q:''});}
    this.setState({screen:'mc',mc:{...this.mkMc(ids,'alt'),kind:'test',title,t0:Date.now()},sheet:null,q:''});}
//@@ mkQuiz
  mkQuiz(ids,title,kind){return {ids:shuffle(ids),ids0:ids.slice(),i:0,rev:false,round:1,miss:[],first:[],ever:[],total:ids.length,title,kind,t0:Date.now()};}
//@@ answer
  answer(ok){const s=this.state,q=s.quiz;if(!q)return;const id=q.ids[q.i];if(q.kind==='trace')return this.fastAfter(s.study,{quiz:null});
    const words=s.words.map(w=>w.id===id?{...w,s:ok?'know':'hard',due:ok?false:w.due,...(ok&&w.s==='new'?{lt:Date.now()}:{}),...this.srsNext(w,ok)}:w);
    const nq={...q,rev:false,i:q.i+1,first:ok&&q.round===1?[...q.first,id]:q.first,miss:ok?q.miss:[...q.miss,id],ever:ok||q.ever.includes(id)?q.ever:[...q.ever,id]};
    if(nq.i<nq.ids.length)return this.upd({words,quiz:nq});
    if(nq.miss.length)return this.upd({words,quiz:{...nq,ids:shuffle(nq.miss),miss:[],i:0,round:nq.round+1}});
    const r={first:nq.first.length,total:nq.total,rounds:nq.round,ids:q.ids0||nq.first};
    if(q.kind==='check'){const st=s.study,hard=uniq([...st.hard,...nq.ever]);
      if(st.li<st.ids.length)return this.upd({words,quiz:null,study:{...st,hard,phase:'learn'},screen:'learn'});
      const L=s.lessons.find(l=>l.n===st.day)||{};const w2=words.map(w=>hard.includes(w.id)?{...w,due:true,s:'hard',box:0,next:iso(new Date(Date.now()+864e5))}:w);
      return this.upd({words:w2,quiz:null,study:null,screen:'result',result:{...r,title:'Урок '+st.day+' · '+(L.t||''),sub:'Новые слова выучены',hard},...this.touch({min:this.mins(st.t0)})});}
    this.upd({words,quiz:null,screen:'result',result:{...r,title:q.title==='Прописи'?'Прописи готовы':q.title+' — готово',sub:'',hard:nq.ever},...this.touch({min:this.mins(q.t0),rv:nq.total})});}
//@@ exit
  exit(){const s=this.state;const p={screen:'tab',ex:null,edit:null,sheet:null};let t0=null;
    if(s.screen==='mc'&&s.mc&&s.mc.kind==='test'){t0=s.mc.t0;p.mc=null;}
    else if(s.screen==='quiz'&&s.quiz&&s.quiz.kind==='test'){t0=s.quiz.t0;p.quiz=null;}
    else if(s.study&&(s.screen==='learn'||s.screen==='quiz'||s.screen==='mc')){t0=s.study.t0;p.study={...s.study,t0:Date.now(),check:s.quiz&&s.quiz.kind==='check'?s.quiz:s.study.check,mcSave:s.mc&&s.mc.kind!=='test'?s.mc:s.study.mcSave};if(s.quiz&&s.quiz.kind!=='test')p.quiz=null;if(s.mc&&s.mc.kind!=='test')p.mc=null;}
    if(t0)Object.assign(p,this.touch({min:this.mins(t0)}));this.upd(p);}
//@@ startStudy
  startStudy(day){const s=this.state;day=day??s.cur;
    if(s.study&&s.study.day===day){const st=s.study;const go=p=>this.setState({q:'',ex:null,sheet:null,...p});
      if(st.phase==='mc'){const mc=st.mcSave||(s.mc&&s.mc.kind!=='test'?s.mc:null)||this.mkMc((st.batch&&st.batch.length?st.batch:(st.done||[]).slice(-5)),(s.method||'fast')==='snow'?'alt':'both');return go({screen:'mc',mc,study:{...st,mcSave:null}});}
      if(st.phase==='trace'){const id=(st.batch||[])[st.batch.length-1];if(id)return go({screen:'quiz',quiz:this.mkQuiz([id],'Обведите знак','trace')});return this.fastAfter(st,{quiz:null});}
      if(st.phase==='quiz'){const chk=s.quiz&&s.quiz.kind==='check'?s.quiz:st.check;if(chk)return go({screen:'quiz',quiz:{...chk,rev:false},study:{...st,check:null}});if(st.li<st.ids.length)return go({screen:'learn',study:{...st,phase:'learn'},quiz:null});return this.fastFinal(st,{});}
      if(st.li<st.ids.length)return go({screen:'learn'});}
    const ids=this.dw(day).filter(w=>w.s==='new').map(w=>w.id);
    if(!ids.length)return this.startTest('lesson',day);
    this.setState({screen:'learn',q:'',ex:null,edit:null,quiz:null,mc:null,sheet:null,partsOpen:false,study:{day,ids,li:0,since:0,skip:[],hard:[],batch:[],done:[],phase:'learn',t0:Date.now()}});}
//@@ mkMc
  // both = every word asked twice (character → meaning, meaning → character); alt = once, direction alternates
  mkMc(ids,mode){const sh=shuffle(ids);const items=mode==='alt'?sh.map((id,i)=>({id,dir:i%2?'m2h':'h2m'})):[...sh.map(id=>({id,dir:'h2m'})),...shuffle(ids).map(id=>({id,dir:'m2h'}))];return {kind:'lesson',items,i:0,pick:null,ever:[],total:items.length,opts:this.mcOpts(items[0])};}
//@@ mcDone
  mcDone(){const s=this.state,mc=s.mc,st=s.study;if(mc&&mc.kind==='test')return this.mcTestDone();if(!st)return this.setState({mc:null,screen:'tab'});
    const st2={...st,done:uniq([...(st.done||[]),...(st.batch||[])]),batch:[],hard:uniq([...st.hard,...(mc?mc.ever:[])])};
    if(st2.li<st2.ids.length)return this.upd({mc:null,study:{...st2,phase:'learn'},screen:'learn'});
    this.fastFinal(st2,{mc:null});}
  // a test by choice: a word answered right the first time goes up the interval ladder, a mistake brings it back tomorrow
  mcTestDone(){const s=this.state,mc=s.mc;const ids=uniq(mc.items.map(it=>it.id));const bad=new Set(mc.ever);
    const words=s.words.map(w=>{if(!ids.includes(w.id))return w;const ok=!bad.has(w.id);return {...w,s:ok?(w.s==='new'?'know':w.s==='hard'?'know':w.s):'hard',due:ok?false:w.due,...this.srsNext(w,ok)};});
    this.upd({words,mc:null,screen:'result',result:{title:mc.title+' — готово',sub:'',first:ids.length-bad.size,total:ids.length,rounds:1,ids,hard:[...bad]},...this.touch({min:this.mins(mc.t0||Date.now()),rv:ids.length})});}
//@@ learnNext
  learnNext(known){const s=this.state,st=s.study;if(!st)return;const id=st.ids[st.li];const snap={words:s.words,study:st,quiz:s.quiz,mc:s.mc,screen:s.screen};let words=s.words;
    if(known){words=words.map(w=>w.id===id?{...w,s:'know',lt:Date.now()}:w);const w0=this.W(id);setTimeout(()=>this.toast((w0?w0.h:'')+' — уже знаю',()=>this.upd(snap)),30);}
    const li=st.li+1,skip=known?[...st.skip,id]:st.skip;
    const base={words,ex:null,edit:null,partsOpen:false,...this.touch({nw:known?0:1})};
    if((s.method||'fast')==='snow'){const done=known?(st.done||[]):[...(st.done||[]),id];const st2={...st,li,skip,since:0,done,batch:[]};
      if(!known&&done.length>=2){const set=done.length<=5?done:[...done.slice(-5),...shuffle(done.slice(0,-5)).slice(0,2)];return this.upd({...base,study:{...st2,phase:'mc'},mc:this.mkMc(set,'alt'),screen:'mc'});}
      if(li>=st.ids.length)return this.fastFinal(st2,base);
      return this.upd({...base,study:{...st2,phase:'learn'}});}
    const batch=known?(st.batch||[]):[...(st.batch||[]),id];const st2={...st,li,skip,since:0,batch};const w=this.W(id);
    if(!known&&this.wOn()&&WCheck.ready()&&w&&[...w.h].some(ch=>WCheck.has(ch)))return this.upd({...base,study:{...st2,phase:'trace'},quiz:this.mkQuiz([id],'Обведите знак','trace'),screen:'quiz'});
    return this.fastAfter(st2,base);}
//@@ fastFinal
  fastFinal(st,extra){const s=this.state;const learned=uniq(st.done||[]).filter(id=>!st.skip.includes(id));const L=s.lessons.find(l=>l.n===st.day)||{};
    if(!learned.length)return this.upd({...extra,study:null,screen:'result',result:{first:0,total:0,rounds:1,title:'Урок '+st.day+' · '+(L.t||''),sub:'Все слова урока уже знакомы',hard:[],ids:[]}});
    this.upd({...extra,study:{...st,phase:'quiz'},quiz:this.mkQuiz(learned,'Письмо по памяти','check'),screen:'quiz'});}
//@@ onUpdate
  onUpdate(u){if(!u)return;if(u.type==='web'||u.type==='app'){this.setState({upd:{type:u.type,name:u.name||'',notes:u.notes||''}});this.updToast=u;this.forceUpdate();}else if(u.notes)this.toast(u.notes);}
  applyUpd(){const u=this.state.upd;if(!u)return;try{if(u.type==='web')EvineNative.updateApply();else EvineNative.updateInstall();}catch(e){this.toast('Обновление работает в приложении на телефоне');}}
  appVer(){try{const i=JSON.parse(EvineNative.appInfo());return i.app+(i.web?' · экраны '+i.web:'');}catch(e){return APPV;}}
  pkData(){const o={};this.PK.forEach(k=>{o[k]=this.state[k];});return o;}
  // a full backup (words + lessons + settings) replaces everything; a plain word list is added to the current lesson
  restoreText(t){let o=null;try{o=JSON.parse(t);}catch(e){}this.setState({sheet:null});
    if(o&&!Array.isArray(o)&&Array.isArray(o.words)&&Array.isArray(o.lessons)){const prev=this.pkData();this.upd({...migrate(o),onboarded:true,screen:'tab',study:null,quiz:null,mc:null});this.toast('Копия восстановлена: '+o.words.length+' '+pl(o.words.length,WF),()=>this.upd(prev));return;}
    this.importText(t);}
//@@ quota
  quota(){return this.state.dailyNew||10;}
//@@ topicName
  topicName(){const s=this.state;const used={};s.lessons.forEach(l=>{used[l.t]=l.n;});const free=T.filter(x=>!used[x[2]]);return (s.topicSel||'').trim()||(free[0]||T[0])[2];}
  goalDraft(){const g=this.state.goal;return g?{n:+g.n||1000,date:g.date,offOn:!!g.offOn}:{n:1000,date:iso(addM(day0(new Date()),6)),offOn:false};}
  // study days from tomorrow to the date (without Sat/Sun when weekends are off); words per day = left / days, kept within 3…30
  goalPlan(g,known){if(!g)return {days:0,left:0,raw:0,per:0};const end=pISO(g.date);let days=0;if(end){const d=day0(new Date());d.setDate(d.getDate()+1);while(d<=end&&days<5000){const wd=d.getDay();if(!g.offOn||(wd!==0&&wd!==6))days++;d.setDate(d.getDate()+1);}}
    const left=Math.max(0,(+g.n||0)-known);const raw=days?Math.ceil(left/days):0;return {days,left,raw,per:days?Math.min(30,Math.max(3,raw)):0};}
  saveGoal(gd){const n=+gd.n||0;if(n<1)return this.toast('Укажите, сколько слов хотите выучить');const p=this.goalPlan(gd,this.state.words.filter(w=>w.s!=='new').length);if(!p.days)return this.toast('Дата должна быть позже сегодняшней');
    const first=!this.state.onboarded;this.upd({goal:{n,date:gd.date,offOn:!!gd.offOn,off:[6,0],set:iso(new Date())},dailyNew:p.per,gd:null,onboarded:true,screen:'tab',tab:first?'home':this.state.tab,sheet:null});this.toast('Норма: '+p.per+' '+pl(p.per,WF)+' в день');}
  openAdd(day,mode,aq,from){this.setState({screen:'add',addMode:mode||'one',addDay:day||null,aq:aq||'',addFrom:from||'tab',sheet:null});}
  moreLesson(){const t=this.topicName();this.pickWords(this.state.dailyNew||10,t);}
//@@ addWord
  addWord(e,day){let s=this.state;const n=day||s.cur;if(!n||!s.lessons.some(l=>l.n===n)){return this.startLesson(this.topicName(),()=>{this.setState({addDay:this.state.cur});this.addWord(e,this.state.cur);});}const prev=s.words;const ru=(e.m&&/[а-яё]/i.test(e.m)?e.m:'')||(window.EDict&&e.key?EDict.ru(e.key):'');
    const w={id:s.nextId,h:e.h,t:e.t,p:e.p,m:ru||'перевод загружается…',en:e.en||'',d:n,s:'new',due:false,hsk:e.hsk!=null?!!e.hsk:!!(window.EDict&&EDict.isHsk(e.h))};
    if(!ru&&window.EDict&&this.aiOn())EDict.translate([{...e,key:e.key||('w|'+e.h),en:e.en||'?'}],()=>{const r2=EDict.ru(e.key||('w|'+e.h));if(r2)this.upd({words:this.state.words.map(x=>x.id===w.id&&this.ruNeed(x.m)?{...x,m:r2}:x)});});
    this.upd({words:[...prev,w],nextId:s.nextId+1},()=>this.fixRu());
    this.toast(e.h+' → урок '+n,()=>this.upd({words:prev}));}
//@@ bulkTarget
  bulkTarget(){const s=this.state;if(s.addDay&&s.lessons.some(l=>l.n===s.addDay))return s.addDay;return s.cur&&s.lessons.some(l=>l.n===s.cur)?s.cur:(s.lessons.reduce((a,l)=>Math.max(a,l.n),0)+1);}
//@@ bulkAdd
  bulkAdd(){const R=this.bulkRows().filter(r=>r.add);if(!R.length)return this.toast('Вставьте слова — по одному в строке или через запятую');
    const s0=this.state,tg0=s0.addDay||this.bulkTarget();if(!s0.lessons.some(l=>l.n===tg0))return this.startLesson('Мои слова',()=>{this.setState({addDay:this.state.cur},()=>this.bulkAdd());});
    const s=this.state;let id=s.nextId;const tg=s.addDay||this.bulkTarget();const ls=[...s.lessons];const prev=s.words;
    const add=R.map(r=>({id:id++,h:r.h,t:r.t||'',p:r.p||'',m:r.m||'перевод загружается…',en:r.en||'',d:r.d||tg,s:'new',due:false,hsk:r.hsk!=null?!!r.hsk:!!(window.EDict&&EDict.isHsk(r.h))}));
    add.forEach(w=>{if(!ls.some(l=>l.n===w.d))ls.push({n:w.d,zh:'新',py:'xīn',t:'Импорт',date:iso(new Date())});});ls.sort((a,b)=>a.n-b.n);
    const days=[...new Set(add.map(w=>w.d))];this._bk=null;const back=s.addFrom==='dayEdit'&&s.de?{screen:'dayEdit'}:{screen:'tab',tab:'words'};
    this.upd({words:[...prev,...add],nextId:id,lessons:ls,cur:s.cur||(ls[ls.length-1]||{}).n||0,bulkT:'',bulkAlt:{},bulkSkip:{},q:'',...back},()=>this.fixRu());
    this.toast('Добавлено '+add.length+' '+pl(add.length,WF)+' в урок '+days.join(', '),()=>this.upd({words:prev}));}
//@@ deDel
  deDel(id){const prev=this.state.words;const w=prev.find(x=>x.id===id);this.upd({words:prev.filter(x=>x.id!==id)});this.toast('Удалено: '+(w?w.h:''),()=>this.upd({words:prev}));}
//@@ startLesson
  startLesson(name,cb){const s=this.state,n=(s.lessons.reduce((a,l)=>Math.max(a,l.n),0))+1,tp=T.find(x=>x[2]===name)||['新','xīn',name];this.upd({lessons:[...s.lessons,{n,zh:tp[0],py:tp[1],t:name,date:iso(new Date())}],cur:n,topicSel:null,topicOwn:''},cb);}
