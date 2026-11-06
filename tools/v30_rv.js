  renderVals(){
    const s=this.state,th=this.thId(),scr=s.screen,tab=s.tab,cur=s.cur,L=s.lessons.find(l=>l.n===cur)||{t:''};
    const IC=ICONS;
    const seg=(list,val,pick)=>list.map(([k,l])=>{const on=k===val;return {l,bg:on?'var(--sf)':'transparent',fg:on?'var(--ink)':'var(--mu)',fw:on?600:500,sh:on?'0 1px 3px rgba(0,0,0,.12)':'none',pick:()=>pick(k)};});
    const tg=on=>({bg:on?'var(--pr)':'var(--ln)',x:on?'20px':'2px'});
    const ws=s.words,known=ws.filter(w=>w.s!=='new'),knownN=known.length;
    const due=ws.filter(w=>this.isDue(w)),dueN=due.length;
    const curW=this.dw(cur),newW=curW.filter(w=>w.s==='new'),hasCur=!!cur&&s.lessons.some(l=>l.n===cur);
    const stIn=!!(s.study&&s.study.day===cur&&(s.study.li>0||s.study.phase!=='learn'));
    const openW=id=>()=>this.setState({sheet:'word',wid:id,partsOpen:false});
    const lessonL=n=>{const l=s.lessons.find(x=>x.n===n);return 'Урок '+n+(l&&l.t?' · '+l.t:'');};
    const topic=this.topicName(),daily=this.state.dailyNew||10;
    const g=s.goal,GL=this.goalPlan(g,knownN);
    const goalN=g&&+g.n?+g.n:1000;
    const goalL=g?('к '+fmtD(pISO(g.date))+' · '+daily+' '+pl(daily,WF)+' в день'+(g.offOn?' · без выходных':'')):daily+' '+pl(daily,WF)+' в день · цель не задана';
    const isWkOff=!!(g&&g.offOn&&[0,6].includes(new Date().getDay()));

    // ---------- home ----------
    let hero;
    if(dueN&&!stIn)hero={t:dueN+' '+pl(dueN,WF)+' на сегодня',sub:'≈ '+Math.max(2,Math.ceil(dueN/2))+' мин'+(hasCur&&newW.length?' · потом урок '+cur+' · '+L.t:''),btn:'Повторить',go:()=>this.startTest('review'),chips:[],done:false};
    else if(hasCur&&newW.length)hero={t:lessonL(cur),sub:newW.length+' '+pl(newW.length,['новое слово','новых слова','новых слов'])+' · ≈ '+Math.max(3,Math.round(newW.length*1.3))+' мин · знакомство, выбор, письмо',btn:stIn?'Продолжить':'Учить',go:()=>this.startStudy(cur),chips:newW.slice(0,12).map(w=>({h:w.h})),done:false};
    else if(hasCur&&!curW.length)hero={t:'Урок '+cur+' пока пуст',sub:'В теме «'+L.t+'» пока нет слов. Найдите их в словаре или вставьте списком.',btn:'Добавить слова',go:()=>this.openAdd(cur,'one'),chips:[],done:false,link:true,linkL:'Выбрать другую тему'};
    else if(!hasCur)hero={t:'Первый урок',sub:'Тема «'+topic+'» · Mao подберёт '+daily+' '+pl(daily,WF)+' из словаря',btn:s.clBusy?'Подбираю слова…':'Начать: '+topic,go:()=>!s.clBusy&&this.moreLesson(),chips:[],done:false,link:true,linkL:'Другая тема'};
    else if(isWkOff)hero={t:'Сегодня выходной',sub:'Новые слова по плану — в будни. Хочется заниматься — можно начать урок сейчас.',btn:s.clBusy?'Подбираю слова…':'Ещё урок: '+topic,go:()=>!s.clBusy&&this.moreLesson(),chips:[],done:true,link:true,linkL:'Другая тема для следующего урока'};
    else hero={t:'На сегодня всё',sub:'Завтра — урок '+(cur+1)+' · '+topic+'. Хочется ещё — можно начать сейчас.',btn:s.clBusy?'Подбираю слова…':'Ещё урок: '+topic,go:()=>!s.clBusy&&this.moreLesson(),chips:[],done:true,link:true,linkL:'Другая тема для следующего урока'};
    const stp=(st,l,r)=>({l,r,mk:st==='done'?IC.check:'',dot:st==='now'?'block':'none',bg:st==='done'?'var(--oks)':st==='now'?'var(--pr)':'transparent',fg:'var(--ok)',bd:st==='done'?'var(--oks)':st==='now'?'var(--pr)':'var(--ln)',fw:st==='now'?600:500,tc:st==='later'?'var(--mu)':'var(--ink)'});
    const lessonState=!hasCur?'later':newW.length?(dueN&&!stIn?'later':'now'):curW.length?'done':'now';
    const steps=[stp(dueN?(stIn?'later':'now'):'done','Повторение',dueN?dueN+' '+pl(dueN,WF):'готово'),
      stp(lessonState,hasCur?lessonL(cur):'Урок 1 · '+topic,hasCur?(newW.length?newW.length+' '+pl(newW.length,['новое','новых','новых']):curW.length?'выучен':'пуст'):daily+' '+pl(daily,['новое','новых','новых']))];
    const hardW=ws.filter(w=>w.s==='hard');
    const tiles=[{zh:'难',c:'var(--bad)',l:'Трудные',sub:hardW.length?hardW.length+' '+pl(hardW.length,WF):'нет',go:()=>hardW.length?this.startTest('hard'):this.toast('Трудных слов нет — так держать')},
      {zh:'考',c:'var(--pr)',l:'Тест',sub:'по прошлым урокам',go:()=>this.startTest('quick')},
      {zh:'写',c:'var(--ac)',l:'Прописи',sub:'5 знаков',go:()=>this.startTest('write')}];
    const mon=(()=>{const d=day0(new Date());d.setDate(d.getDate()-((d.getDay()+6)%7));return d;})();const t0=day0(new Date());
    const week=['Пн','Вт','Ср','Чт','Пт','Сб','Вс'].map((l,i)=>{const d=new Date(mon);d.setDate(mon.getDate()+i);const e=s.log[dk(d)]||{};const done=(e.min||0)+(e.nw||0)+(e.rv||0)>0&&!e.fz;const now=+d===+t0;return {l,mk:done?IC.check:'',bg:done?'var(--prs)':'transparent',bd:now?'var(--pr)':done?'var(--prs)':'var(--ln)'};});
    const recent=[...known].sort((a,b)=>(b.lt||b.id)-(a.lt||a.id)).slice(0,10).map(w=>({h:w.h,p:w.p,m:shortM(w.m),open:openW(w.id)}));

    // ---------- words ----------
    const q=(s.q||'').trim();
    const found=q?ws.filter(w=>matchW(w,q)).slice(0,60).map(w=>({h:w.h,p:w.p,m:shortM(w.m),day:'Урок '+w.d,open:openW(w.id)})):[];
    const days=[...s.lessons].reverse().map(l=>{const lw=this.dw(l.n),k=lw.filter(w=>w.s!=='new').length;return {title:'Урок '+l.n+' · '+l.t,stat:k+' из '+lw.length,empty:!lw.length,add:()=>this.openAdd(l.n,'one'),
      ws:lw.map(w=>({h:w.h,p:w.p,open:openW(w.id),dot:w.s==='hard'?'var(--bad)':w.s==='new'?'transparent':'var(--ok)'})),
      edit:()=>this.setState({screen:'dayEdit',de:{n:l.n}}),canRep:k>0,rep:()=>this.startTest('lesson',l.n)};});
    const used={};s.lessons.forEach(l=>{used[l.t]=l.n;});const firstFree=(T.find(x=>!used[x[2]])||T[0])[2];
    const topics=T.map(x=>{const was=!!used[x[2]],sel=x[2]===topic;return {zh:x[0],l:x[2],tag:sel?'выбрана':was?'была':x[2]===firstFree?'по порядку':'',zc:was&&!sel?'var(--mu)':'var(--ac)',
      go:()=>{this.setState({topicSel:x[2],topicOwn:'',sheet:null});this.save();this.toast('Следующий урок: '+x[2]);},bd:sel?'var(--pr)':'var(--ln)',bg:sel?'var(--prs)':'transparent',fg:was&&!sel?'var(--mu)':'var(--ink)'};});

    // ---------- add ----------
    const addDay=s.addDay||this.bulkTarget();const E=window.EDict&&EDict.ready()?EDict:null;
    const aq=(s.aq||'').trim();let dictRes=[];
    if(aq&&E){dictRes=E.search(aq,24).slice(0,24).map(e=>{const ex=ws.find(x=>x.h===e.h);const ru=(e.m&&/[а-яё]/i.test(e.m)?e.m:'')||E.ru(e.key)||'';return {h:e.h,p:e.p,m:shortM(ru)||(e.en?e.en+' (англ.)':''),have:!!ex,can:!ex,dayL:ex?'Урок '+ex.d:'',add:()=>this.addWord(e,addDay)};});}
    const bulkR=scr==='add'&&s.addMode==='list'?this.bulkRows():[];const nAdd=bulkR.filter(r=>r.add).length;

    // ---------- run: card / mc / quiz ----------
    const st=s.study,les=!!st,snow=(s.method||'fast')==='snow';let runPct=0,runLabel='';
    let card={};const cw=scr==='learn'&&st?this.W(st.ids[st.li]):null;
    if(cw){const n=st.ids.length;runPct=Math.max(4,st.li/n*33);runLabel=(snow?'Снежный ком · слово ':'Знакомство · ')+(st.li+1)+' из '+n;
      const parts=cw.mn?(cw.mn.parts.map(x=>x[0]+' '+x[1]).join(' + ')+(cw.mn.note?'\n'+cw.mn.note:'')):(window.Explain&&Explain.ready()?Explain.partsShort(cw.h):'');
      card={h:cw.h,p:cw.p,m:cw.m,fs:cw.h.length>2?72:cw.h.length>1?92:120,mWarn:cw.mSrc==='ai',hasParts:!!parts,parts};}
    const mc=s.mc;let mcv={opts:[]};
    if(scr==='mc'&&mc&&mc.items[mc.i]){const it=mc.items[mc.i],w=this.W(it.id)||{h:'',p:'',m:''},pk=mc.pick,h2m=it.dir==='h2m';const left=mc.items.length-mc.i;const p=mc.i/mc.items.length;
      runPct=Math.max(4,les?33+p*33:p*100);runLabel=(snow&&les?'Снежный ком · проверка · осталось ':'Выбор · осталось ')+left;
      const wrong=pk!=null&&!mc.opts[pk].ok;
      mcv={ask:h2m?'Что значит?':'Какой иероглиф?',prompt:h2m?w.h:shortM(w.m),fs:h2m?(w.h.length>2?64:84):26,ff:h2m?"'Noto Serif SC',serif":"'Noto Sans',sans-serif",p:w.p,pOp:pk!=null?1:0,back:wrong,
        opts:mc.opts.map((o,k)=>{const isOk=o.ok,isPick=k===pk;let bg='var(--sf)',bd='var(--ln)',fg='var(--ink)';if(pk!=null){if(isOk){bg='var(--oks)';bd='var(--ok)';fg='var(--ok)';}else if(isPick){bg='var(--bads)';bd='var(--bad)';fg='var(--bad)';}else fg='var(--mu)';}
          return {t:o.t,go:()=>this.mcPick(k),bg,bd,fg,fs:h2m?15:30,ff:h2m?"'Noto Sans',sans-serif":"'Noto Serif SC',serif"};})};}
    const qz=s.quiz;let qv={};const wm=s.writeMode==='paper'?'paper':'screen';
    const wScr=!!qz&&(qz.write||wm==='screen')&&!!window.WCheck;
    if(scr==='quiz'&&qz){const w=this.W(qz.ids[Math.min(qz.i,qz.ids.length-1)])||{h:'',p:'',m:''};const n=qz.ids.length;
      qv={h:w.h,p:w.p,m:shortM(w.m),fs:w.h.length>2?72:w.h.length>1?96:130};
      if(qz.kind==='trace'){const b=st&&st.batch?st.batch.length:0;runPct=Math.max(4,(st?st.li/st.ids.length:0)*33);runLabel='Обводка · '+(st?st.li:1)+' из '+(st?st.ids.length:1);}
      else if(qz.kind==='check'){runPct=66+qz.i/n*34;runLabel='Письмо · '+Math.min(qz.i+1,n)+' из '+n+(qz.round>1?' · круг '+qz.round:'');}
      else{runPct=Math.max(4,qz.i/n*100);runLabel=qz.title+' · '+Math.min(qz.i+1,n)+' из '+n+(qz.round>1?' · круг '+qz.round:'');}}
    const runOn=(scr==='learn'&&!!cw)||(scr==='mc'&&!!mc)||(scr==='quiz'&&!!qz);

    // ---------- result ----------
    const R=s.result;let rs={list:[]};
    if(R){const hard=(R.hard||[]).map(id=>this.W(id)).filter(Boolean);const ids=R.ids||[];const nx=ids.map(id=>this.W(id)).filter(w=>w&&w.next).map(w=>w.next).sort()[0];
      rs={title:R.title,sub:R.sub||'',first:R.first,total:R.total,hasTotal:R.total>0,noTotal:!(R.total>0),hasHard:hard.length>0,hardN:hard.length,list:hard.map(w=>({h:w.h,p:w.p})),hasNext:!!nx,next:nx?fmtD(pISO(nx)).replace(/ \d{4}$/,''):''};}

    // ---------- goal ----------
    const gd=s.gd||this.goalDraft();const gp=this.goalPlan(gd,knownN);const setG=p=>this.setState({gd:{...gd,...p}});
    const tod=day0(new Date());const gEnd=pISO(gd.date)||tod;
    const cm=s.calM||gd.date.slice(0,7);const [cy,cmo]=cm.split('-').map(Number);const first=new Date(cy,cmo-1,1);const off=(first.getDay()+6)%7;const dim=new Date(cy,cmo,0).getDate();
    const shiftM=k=>{const d=new Date(cy,cmo-1+k,1);if(d<new Date(tod.getFullYear(),tod.getMonth(),1))return;this.setState({calM:iso(d).slice(0,7)});};
    const calDays=[];for(let i=0;i<off;i++)calDays.push({l:'',go:()=>{},bd:'transparent',bg:'transparent',fg:'var(--ink)',fw:400,cur:'default',op:1});
    for(let n=1;n<=dim;n++){const d=new Date(cy,cmo-1,n);const id=iso(d);const past=d<=tod;const sel=id===gd.date;const today=+d===+tod;const we=d.getDay()===0||d.getDay()===6;
      calDays.push({l:String(n),go:()=>{if(!past)setG({date:id});},bd:today?'var(--pr)':'transparent',bg:sel?'var(--pr)':'transparent',fg:sel?'var(--onpr)':past?'var(--mu)':(we&&gd.offOn?'var(--mu)':'var(--ink)'),fw:sel||today?700:500,cur:past?'default':'pointer',op:past?.4:1});}
    const gPer=gp.days?gp.per+' '+pl(gp.per,WF)+' в день':'Выберите дату позже сегодняшней';
    const firstRun=!s.onboarded;

    // ---------- chat ----------
    const prov=PROV[s.aiProv||'free']||PROV.free;const aiReady=this.aiOn();
    const toastBottom=scr==='tab'?84:(scr==='learn'||scr==='quiz')?150:(scr==='add'||scr==='dayEdit'||scr==='goal'||scr==='result')?96:20;

    return {
      th,phoneRef:this.phoneRef,chatRef:this.chatRef,
      isHome:scr==='tab'&&tab==='home',isWords:scr==='tab'&&tab==='words',isAsk:scr==='tab'&&tab==='ask',isSettings:scr==='tab'&&tab==='settings',
      isGoal:scr==='goal',isAdd:scr==='add',isEdit:scr==='dayEdit'&&!!s.de,isRun:runOn,isCard:scr==='learn'&&!!cw,isMc:scr==='mc'&&!!mc&&!!mc.items[mc.i],isQuiz:scr==='quiz'&&!!qz,isResult:scr==='result'&&!!R,
      showNav:scr==='tab',
      navs:[['home','Сегодня',IC.today],['words','Слова',IC.book],['ask','Вопросы',IC.forum],['settings','Настройки',IC.settings]].map(([k,l,ic])=>{const on=tab===k;return {l,ic,go:()=>this.goTab(k),c:on?'var(--pr)':'var(--mu)',fw:on?600:500,bar:on?'var(--prs)':'transparent'};}),
      // home
      streakL:s.streak+' '+pl(s.streak,['день','дня','дней'])+' подряд',hero,hasChips:hero.chips.length>0,heroBg:hero.done?'transparent':'var(--pr)',heroFg:hero.done?'var(--ink)':'var(--onpr)',heroBd:hero.done?'var(--ln)':'var(--pr)',
      steps,tiles,week,recent,hasRecent:recent.length>0,goWords:()=>this.goTab('words'),known:knownN,goalN,knownPct:Math.min(100,knownN/Math.max(1,goalN)*100),goalL,
      openTopics:()=>this.setState({sheet:'topic'}),openGoal:()=>this.setState({screen:'goal',gd:this.goalDraft(),calM:null}),
      // words
      q:s.q,onQ:e=>this.setState({q:e.target.value}),hasQ:!!q,noQ:!q,found,noFound:!!q&&!found.length,days,noLessons:!s.lessons.length,nextTopic:topic,
      openAdd:()=>this.openAdd(null,s.addMode||'one'),openAddQ:()=>this.openAdd(null,'one',q),
      // topics sheet
      topics,topicOwn:s.topicOwn||'',onTopicOwn:e=>this.setState({topicOwn:e.target.value}),
      addCustom:()=>{const t=(s.topicOwn||'').trim();if(!t)return this.toast('Напишите название темы');this.setState({topicSel:t,topicOwn:'',sheet:null},()=>this.save());this.toast('Следующий урок: '+t);},
      // add
      back:()=>this.setState({screen:s.addFrom==='dayEdit'&&s.de?'dayEdit':'tab'}),
      addModeOpts:seg([['one','Одно слово'],['list','Списком']],s.addMode||'one',k=>this.setState({addMode:k})),addOne:(s.addMode||'one')==='one',addList:s.addMode==='list',
      addDayL:(s.lessons.some(l=>l.n===addDay)?lessonL(addDay):'урок '+addDay+' · новый').replace(/^У/,'у'),
      cycleAddDay:()=>{const ns=[...s.lessons.map(l=>l.n)];const nw=(ns.length?Math.max(...ns):0)+1;ns.push(nw);const i=ns.indexOf(addDay);this.setState({addDay:ns[(i+1)%ns.length]});},
      aq:s.aq||'',onAq:e=>this.setState({aq:e.target.value}),dictRes,hasDictRes:dictRes.length>0,dictEmpty:!!aq&&!dictRes.length,dictEmptyL:E?'Ничего не нашлось. Попробуйте пиньинь без тонов: jiejie':'Загружаю словарь…',addHelp:!aq,
      bulkT:s.bulkT,onBulk:e=>this.setState({bulkT:e.target.value}),bulkWait:!!s.bulkT.trim()&&!E,bulkRef:this.bulkRef,
      bulkRows:bulkR.map(r=>({h:r.kind==='miss'?'?':r.h,p:r.kind==='miss'?r.h:r.p,m:r.kind==='miss'?'не нашлось — проверьте':r.kind==='have'?shortM(r.m)+' · уже есть':r.kind==='nodict'&&!r.m?'нет в словаре — впишите перевод потом':shortM(r.m||r.en||''),
        mc:r.kind==='miss'?'var(--bad)':r.kind==='have'?'var(--mu)':'var(--ink)',alt:r.alts>1,altL:(r.ai+1)+'/'+Math.min(r.alts,6),next:()=>this.setState({bulkAlt:{...this.state.bulkAlt,[r.key]:(r.ai+1)%Math.min(r.alts,6)}}),rm:()=>this.setState({bulkSkip:{...this.state.bulkSkip,[r.key]:1}})})),
      bulkBtn:nAdd?'Добавить '+nAdd+' '+pl(nAdd,WF):'Вставьте слова',bulkBg:nAdd?'var(--pr)':'var(--sf2)',bulkFg:nAdd?'var(--onpr)':'var(--mu)',bulkAddB:()=>this.bulkAdd(),
      bulkFile:()=>{if(!(window.EVINE&&EVINE.openFile(t=>t!=null&&this.setState({bulkT:String(t)}))))this.bulkRef.current?.click();},
      onBulkFile:e=>{const f=e.target.files[0];if(!f)return;e.target.value='';f.text().then(t=>this.setState({bulkT:t}));},
      // day editor
      ...(()=>{const de=s.de;if(!de)return {deRows:[]};const Ld=s.lessons.find(l=>l.n===de.n)||{};const lw=this.dw(de.n);
        return {deN:de.n,deT:Ld.t||'',onDeT:e=>this.deRename(de.n,e.target.value),deWarn:lw.some(w=>w.mSrc==='ai'),
          deRows:lw.map(w=>({h:w.h,p:w.p||'',m:w.m||'',mbd:w.mSrc==='ai'?'var(--bad)':'var(--ln)',onP:e=>this.deWord(w.id,'p',e.target.value),onM:e=>this.deWord(w.id,'m',e.target.value),del:()=>this.deDel(w.id)})),
          deBack:()=>this.setState({screen:'tab',tab:'words',de:null}),deAdd:()=>this.openAdd(de.n,'one',null,'dayEdit')};})(),
      // run
      runPct,runLabel,exitRun:()=>this.exit(),
      card,speakCard:()=>cw&&this.speak(cw.h),partsOpen:!!s.partsOpen,partsIc:s.partsOpen?IC.less:IC.more,tglParts:()=>this.setState({partsOpen:!s.partsOpen}),
      learnNextB:()=>this.learnNext(false),learnKnownB:()=>this.learnNext(true),
      mcv,
      qv,...this.writeVals(qv,wScr),
      speakQ:()=>qv.h&&this.speak(qv.h),ansYes:()=>this.answer(true),ansNo:()=>this.answer(false),
      reveal:()=>{if(!qz)return;if(qz.kind==='trace')return this.answer(true);this.setState({quiz:{...qz,rev:true}});},
      // result
      rs,resHard:()=>{const h=(R&&R.hard)||[];this.setState({result:null});this.startTest('ids',h,'Трудные слова');},resDone:()=>this.goTab('home'),
      // goal
      firstRun,goalBackShow:!firstRun,goalBack:()=>this.setState({screen:'tab',gd:null,sheet:null}),goalTitle:firstRun?'Какая у вас цель?':'Цель',
      gN:gd.n===''?'':String(gd.n),onGN:e=>{const v=e.target.value.replace(/\D/g,'');setG({n:v===''?'':Math.min(20000,parseInt(v,10)||0)});},
      gDn:()=>setG({n:Math.max(50,Math.ceil(((+gd.n||0)-50)/50)*50)}),gUp:()=>setG({n:Math.min(5000,Math.floor(((+gd.n||0)+50)/50)*50)}),
      gKnownL:knownN?'уже знаю '+knownN:'от 50 до 5000',
      openCal:()=>this.setState({sheet:'cal',calM:gd.date.slice(0,7)}),gDateL:fmtD(gEnd),gDateFull:'Цель — '+fmtD(gEnd),
      gLeftL:(()=>{const m=Math.round((gEnd-tod)/864e5/30.4);return gEnd>tod?(m>0?'через '+m+' '+pl(m,['месяц','месяца','месяцев']):'меньше месяца'):'выберите дату';})(),
      gQuick:[['3 мес',3],['6 мес',6],['1 год',12],['2 года',24]].map(([l,m])=>{const id=iso(addM(tod,m));return {l,go:()=>setG({date:id}),bd:gd.date===id?'var(--pr)':'var(--ln)',bg:gd.date===id?'var(--prs)':'transparent'};}),
      tglWk:()=>setG({offOn:!gd.offOn,off:[6,0]}),wkT:tg(!gd.offOn),wkD:gd.offOn?'Сб и Вс — отдых, норма в будни больше':'Каждый день',
      gPer,gSub:gp.days?gp.days+' учебных '+pl(gp.days,DF)+' · осталось выучить '+gp.left+(gp.raw>20?'. Это много — лучше отодвинуть дату':''):'',
      gBtn:firstRun?'Начать учиться':'Сохранить цель',gSave:()=>this.saveGoal(gd),
      sheetCal:s.sheet==='cal',calTitle:MNAME[cmo-1]+' '+cy,calPrev:()=>shiftM(-1),calNext:()=>shiftM(1),calPrevFg:new Date(cy,cmo-2,1)<new Date(tod.getFullYear(),tod.getMonth(),1)?'var(--ln)':'var(--ink)',
      calWd:['Пн','Вт','Ср','Чт','Пт','Сб','Вс'].map((l,i)=>({l,c:i>4?'var(--ac)':'var(--mu)'})),calDays,
      // settings
      goalShort:g?(+g.n)+' '+pl(+g.n,WF):'не задана',
      daily,dailyDn:()=>this.upd({dailyNew:Math.max(3,daily-1)}),dailyUp:()=>this.upd({dailyNew:Math.min(20,daily+1)}),
      more1:!!s.more1,more1Ic:s.more1?IC.less:IC.more,tglMore1:()=>this.setState({more1:!s.more1}),methodL:snow?'Снежный ком':'Быстрый урок',
      methodOpts:seg([['fast','Быстрый урок'],['snow','Снежный ком']],snow?'snow':'fast',k=>{this.upd({method:k});if(s.study)this.setState({study:null,mc:null,quiz:null});this.toast(k==='snow'?'Следующий урок — «Снежным комом»':'Следующий урок — быстрый');}),
      methodD:snow?'После каждого нового слова — проверка по всем выученным в уроке (последние 5 и ещё 2 из начала). В конце — письмо всех слов. Дольше, но крепче.':'Слова пачками по 5: карточка → обводка → выбор из 4. В конце — письмо всех слов по памяти. 15 слов ≈ 20 минут.',
      writeOpts:seg([['screen','На экране'],['paper','На бумаге']],wm,k=>this.upd({writeMode:k})),writeD:wm==='screen'?'Пишете пальцем черту за чертой: верная встаёт на место, неверная исчезает':'Пишете в тетради, потом сверяетесь с ответом и отмечаете сами',
      outlineT:tg((s.wGhost||'first')!=='off'),tglOutline:()=>this.upd({wGhost:(s.wGhost||'first')==='off'?'first':'off'}),
      gridOpts:seg([['on','田'],['mi','米']],s.wGrid==='mi'?'mi':'on',k=>this.upd({wGrid:k})),
      themeOpts:seg([['system','Как в системе'],['light','Светлая'],['dark','Тёмная']],s.th,k=>this.upd({th:k})),
      speedOpts:seg([['slow','Медленно'],['normal','Обычно']],s.rate<=0.65?'slow':'normal',k=>{this.upd({rate:k==='slow'?0.6:0.85});setTimeout(()=>this.speak('你好'),60);}),
      openBackup:()=>this.setState({sheet:'backup',resetAsk:false}),
      exportJson:()=>{this.save();const name='mao-backup-'+iso(new Date())+'.json';const ok=window.EVINE?EVINE.saveFile(name,localStorage.getItem(KEY)||'{}'):false;this.setState({sheet:null});if(!(window.EVINE&&EVINE.native))this.toast(ok?'Копия сохранена: '+name:'Не удалось сохранить');},
      pickJson:()=>{if(!(window.EVINE&&EVINE.openFile(t=>t!=null&&this.restoreText(t))))this.fileRef.current?.click();},fileRef:this.fileRef,
      onJson:e=>{const f=e.target.files[0];if(!f)return;e.target.value='';f.text().then(t=>this.restoreText(t));},
      resetL:s.resetAsk?'Точно стереть всё? Нажмите ещё раз':'Стереть все данные',
      askReset:()=>{if(!s.resetAsk)return this.setState({resetAsk:true});const prev=JSON.stringify(this.pkData());this.setState({resetAsk:false,sheet:null,study:null,quiz:null,mc:null,chat:[]});this.upd({...this.defaults(),screen:'goal',tab:'home',gd:null});this.toast('Данные стёрты','Вернуть',()=>this.upd({...JSON.parse(prev),screen:'tab'}));},
      updL:s.upd?(s.upd.type==='web'?'Обновление загружено — нажмите, чтобы перезапустить':'Доступна версия '+(s.upd.name||'')+' — нажмите, чтобы обновить'):'Последняя версия · '+this.appVer(),updC:s.upd?'var(--pr)':'var(--mu)',
      updGo:()=>{if(s.upd)return this.applyUpd();try{EvineNative.updateCheck();this.toast('Проверяю обновления…');}catch(e){this.toast('Проверка работает в приложении на телефоне');}},
      aiT:tg(s.aiOn===true),tglAi:()=>this.upd({aiOn:s.aiOn!==true}),aiOnS:s.aiOn===true,
      models:Object.keys(PROV).map(k=>{const P=PROV[k],on=(s.aiProv||'free')===k;return {l:P.l,d:P.d,pick:()=>this.upd({aiProv:k}),bd:on?'var(--pr)':'var(--ln)',bg:on?'var(--prs)':'transparent'};}),
      needKey:!!prov.key,apiKey:(s.aiKeys||{})[s.aiProv||'free']||'',keyPh:'Ключ '+prov.n,keyHelp:prov.help||'',
      onKey:e=>this.upd({aiKeys:{...(s.aiKeys||{}),[s.aiProv||'free']:e.target.value.trim()}}),
      checkApi:()=>this.checkApi(),checkL:s.clBusy?'Проверяю…':'Проверить связь',hasApiMs:!!s.apiMs,apiMs:s.apiMs||'',apiMsC:s.apiOk?'var(--ok)':'var(--bad)',
      footL:'Mao '+APPV+' · словарь CC-CEDICT, CC BY-SA 4.0',
      // chat
      aiL:aiReady?'нейросеть · '+prov.n:s.aiOn===true&&prov.key?'нет ключа · словарь':'без интернета · словарь',aiC:aiReady?'var(--ok)':'var(--mu)',
      clearChat:()=>{this.chatSeq=(this.chatSeq||0)+1;this.setState({chat:[],chatBusy:false,chatQ:''});},chatEmpty:!s.chat.length,chatFull:s.chat.length>0,thinking:!!s.chatBusy&&!(s.chat.length&&s.chat[s.chat.length-1].r==='ai'&&s.chat[s.chat.length-1].live),
      starters:[[IC.cat,'Из чего состоит 好?','Разбери 好'],[IC.list,'Подбери слова по теме','Подбери слова про '+topic.toLowerCase()],[IC.tr,'Как сказать «кошка»?','Как сказать кошка'],[IC.help,'Чем 他 отличается от 她?','Чем 他 отличается от 她?']].map(([ic,l,t])=>({ic,l,go:()=>this.sendChat(t)})),
      msgs:s.chat.map(m=>({t:m.t,al:m.r==='me'?'flex-end':'flex-start',bg:m.r==='me'?'var(--pr)':'var(--sf2)',fg:m.r==='me'?'var(--onpr)':'var(--ink)',note:m.note||'',noteD:m.note?'block':'none'})),
      quickQ:[['Разбери 好','Разбери 好'],['Слова: '+topic,'Подбери слова про '+topic.toLowerCase()],['Что значит 家?','家']].map(([l,t])=>({l,go:()=>this.sendChat(t)})),
      chatQ:s.chatQ,onChatQ:e=>this.setState({chatQ:e.target.value}),chatKey:e=>{if(e.key==='Enter')this.sendChat(this.state.chatQ);},sendChatB:()=>this.sendChat(s.chatQ),
      sendBg:s.chatQ.trim()?'var(--pr)':'var(--sf2)',sendFg:s.chatQ.trim()?'var(--onpr)':'var(--mu)',
      // sheets
      hasSheet:!!s.sheet,closeSheet:()=>this.setState({sheet:null,resetAsk:false}),stop:e=>e.stopPropagation(),sheetTopic:s.sheet==='topic',sheetWord:s.sheet==='word',sheetBackup:s.sheet==='backup',
      sw:(()=>{if(s.sheet!=='word')return {};const w=this.W(s.wid);if(!w)return {};const parts=w.mn?(w.mn.parts.map(x=>x[0]+' '+x[1]).join(' + ')+(w.mn.note?'\n'+w.mn.note:'')):(window.Explain&&Explain.ready()?Explain.partsShort(w.h):'');
        const stl=w.s==='new'?'новое':this.isDue(w)?'повторить сегодня':w.s==='hard'?'трудное':w.next?'повтор '+fmtD(pISO(w.next)).replace(/ \d{4}$/,''):'выучено';
        return {h:w.h,p:w.p,m:w.m,fs:w.h.length>2?64:88,meta:lessonL(w.d)+' · '+stl,hasParts:!!parts,parts,say:()=>this.speak(w.h),
          ask:()=>{this.setState({sheet:null,screen:'tab',tab:'ask'});this.sendChat('Разбери '+w.h);},edit:()=>this.setState({sheet:null,screen:'dayEdit',de:{n:w.d}})};})(),
      // toast
      hasToast:!!s.toast,toastMsg:s.toast?.msg,toastAct:!!s.toast?.act,toastActL:s.toast?.actL||'Вернуть',toastBottom,toastGo:()=>{const a=s.toast?.act;this.setState({toast:null});clearTimeout(this.tt);a&&a();}
    };
  }
  // ---- writing screen values (v8 layout, 2.9 stroke checking) ----
  writeVals(qv,wScr){const s=this.state,qz=s.quiz;if(!qz||s.screen!=='quiz')return {wTabs:[]};
    const n=[...(qv.h||'')].length,idx=s.wIdx||0,rev=!!qz.rev,trace=qz.kind==='trace';const D=s.wDone;
    const ghost=(s.wGhost||'first')!=='off'&&trace;
    const tabs=n>1?[...qv.h].map((c,i)=>{const done=i===idx?(s.wN||0)>0:!!((this.wCells||[])[i]&&this.wCells[i].S.length);const on=i===idx;const show=rev||trace;
      return {l:show?c:String(i+1),fs:show?20:15,al:'Знак '+(i+1),go:()=>i!==idx&&this.wGo(i),bg:on?'var(--prs)':'var(--sf)',bd:on?'var(--pr)':done?'var(--ok)':'var(--ln)',fg:on?'var(--pr)':'var(--ink)'};}):[];
    const has=(s.wN||0)>0;const last=idx>=n-1;
    const R0=wScr&&!rev?this.wCurRef():null;
    const wCount=!wScr||rev?'':R0?'черта '+Math.min((s.wN||0)+1,R0.length)+' из '+R0.length:'';
    const hintL=trace?'Пропустить':ghost||this.wPeek||s.wPeekS?'Ответ':'Подсказка';
    return {wTabs:tabs,wTabsShow:n>1&&wScr,wScreen:wScr,wPaper:!wScr&&!rev,wPaperRev:!wScr&&rev,wGridOn:s.wGrid!==false,wGridMi:s.wGrid==='mi',
      wcRef:el=>{this.wcCanvas=el;},wDown:e=>this.wDown(e),wMove:e=>this.wMove(e),wUp:e=>this.wUp(e),
      wRevOn:wScr&&rev,wCurCh:[...(qv.h||'')][Math.min(idx,Math.max(0,n-1))]||'',
      wOkOn:!!D&&!rev&&(D.ok||trace),wOkL:trace?'Прописано':D&&D.mist?'Верно · ошибок: '+D.mist:'Верно',
      wAskL:trace?'Обведите знак':wScr?'Напишите по памяти':'Напишите на бумаге',wCount,
      wBtns:wScr&&!rev,undoFg:has||idx>0?'var(--ink)':'var(--mu)',wUndoB:()=>this.wUndo(),
      hintL,hintGo:()=>{if(trace)return this.answer(true);if(hintL==='Подсказка'){this.wPeek=true;this.wHint=true;this.setState({wPeekS:true});this.wRender();return;}this.wSave();this.setState({quiz:{...qz,rev:true}},()=>this.wRender());},
      doneL:last?'Готово':'Знак '+(idx+2),doneBg:has?'var(--pr)':'var(--sf2)',doneFg:has?'var(--onpr)':'var(--mu)',
      wDoneB:()=>{if(!(this.wS||[]).length)return this.toast('Сначала напишите знак в клетке');if(!last)return this.wGo(idx+1);if(trace)return this.answer(true);this.wSave();this.setState({quiz:{...qz,rev:true}},()=>this.wRender());},
      qRev:rev,wHasRes:rev&&!!D,wResL:D?(D.ok?'Черты верные'+(D.mist?' · ошибок: '+D.mist:''):'Ошибок в чертах: '+D.mist+(D.help?' · с подсказкой':'')+' — слово вернётся на повторение'):'',wResC:D&&D.ok?'var(--ok)':'var(--bad)'};}
