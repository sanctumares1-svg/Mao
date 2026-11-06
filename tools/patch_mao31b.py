#!/usr/bin/env python3
"""Mao 3.1, stage 3: finger writing.
 - canvas at the screen's pixel density; all points of a fast stroke (coalesced events)
 - a wrong stroke is removed at once and only flashes red; the counter counts accepted strokes
 - the next character is ready immediately (no lost first stroke)
 - feedback in words: wrong order / wrong direction / wrong shape
 - a character written smaller or shifted is matched after the first strokes (scale and offset fitted)
 - the finger line fades into the calligraphic stroke instead of jumping
 - wide touches are no longer ignored silently
 Order of strokes and their direction are still required; thresholds of the snowball are not touched."""
import re
P = '/tmp/claude-0/mao/www/index.html'
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, n, a[:100])
    s = s.replace(a, b)


def method(name, new):
    """replace a whole class method «  name(…){…}» (up to the next method at the same indent)"""
    global s
    i = s.find('\n  ' + name + '(')
    assert i >= 0, name
    j = s.find('\n  ', i + 3)
    while s[j + 3] == ' ':
        j = s.find('\n  ', j + 3)
    s = s[:i] + '\n' + new.rstrip('\n') + s[j:]


method('wDown', r"""  // canvas size follows the screen's pixel density (sharp lines on 2.75–3× screens); points are kept in 0..1
  wFit(c){c=c||this.wcEl();if(!c)return 1;const r=Math.min(3,window.devicePixelRatio||1),w=Math.round((c.clientWidth||288)*r);if(w>0&&c.width!==w){c.width=w;c.height=w;}return c.width/576;}
  wDown(e){const c=e.currentTarget||this.wcEl();if(!c)return;e.preventDefault();
    if(this.state.wDone||(this.state.quiz&&this.state.quiz.rev))return;
    // a second finger while drawing is ignored; a very wide touch (palm) too, but with a hint
    if(this.drw&&this.pid!=null&&e.pointerId!==this.pid)return;
    if(e.pointerType==='touch'&&((e.width||0)>90||(e.height||0)>90)){if(!this.wPalmT||Date.now()-this.wPalmT>4000){this.wPalmT=Date.now();this.wSay('Касание слишком широкое — ведите кончиком пальца');}return;}
    this.wcCanvas=c;const k=this.wFit(c);this.pid=e.pointerId;clearTimeout(this.wAutoT);try{c.setPointerCapture(e.pointerId);}catch(_){}this.drw=true;const [x,y]=this.wPt(e),g=c.getContext('2d');
    this.wK=k;this.wBase={thin:6,mid:9,bold:14}[this.state.wWidth||'mid']*k;this.wf=1;this.lt=performance.now();g.strokeStyle=this.wInkC||(this.wInkC=getComputedStyle(c).color);g.lineWidth=this.wBase;g.lineCap='round';g.lineJoin='round';g.beginPath();g.moveTo(x,y);g.lineTo(x+.1,y+.1);g.stroke();this.lp0=[x,y];this.lm=[x,y];this.wS=this.wS||[];this.wS.push([[x/c.width,y/c.height,1]]);if(this.state.wMsg)this.setState({wMsg:null});if(!this.state.wHas)this.setState({wHas:true});}""")
method('wMove', r"""  wMove(e){if(!this.drw||(this.pid!=null&&e.pointerId!==this.pid))return;const c=this.wcEl();if(!c)return;const g=c.getContext('2d');
    // Android sends one event per frame; the points in between are in getCoalescedEvents()
    const evs=(e.getCoalescedEvents&&e.getCoalescedEvents())||[];const list=evs.length?evs:[e];const S=this.wS&&this.wS[this.wS.length-1];
    for(const ev of list){const [x,y]=this.wPt(ev),[px,py]=this.lp0;
      const now=ev.timeStamp||performance.now(),dt=Math.max(1,now-this.lt),v=Math.hypot(x-px,y-py)/dt/(this.wK||1);this.lt=now;
      if((this.state.wWidth||'mid')==='bold'){const f=Math.max(.5,Math.min(1.4,1.4-v/2.2));this.wf=this.wf*.7+f*.3;}else this.wf=1;
      const mx=(x+px)/2,my=(y+py)/2;g.lineWidth=this.wBase*this.wf;g.beginPath();g.moveTo(this.lm[0],this.lm[1]);g.quadraticCurveTo(px,py,mx,my);g.stroke();this.lm=[mx,my];this.lp0=[x,y];
      if(S)S.push([x/c.width,y/c.height,this.wf]);}}""")
method('wPt', r"""  wPt(e){const c=this.wcEl();if(!this.wRect||this.wRectC!==c||performance.now()-this.wRectT>500){this.wRect=c.getBoundingClientRect();this.wRectC=c;this.wRectT=performance.now();}const r=this.wRect,k=c.width/r.width;return [(e.clientX-r.left)*k,(e.clientY-r.top)*k];}""")
method('wSnapLast', r"""  // a short message under the cell (not a toast: nothing covers the cell)
  wSay(msg,bad){clearTimeout(this.wSayT);this.setState({wMsg:{t:msg,bad:!!bad}});this.wSayT=setTimeout(()=>this.setState({wMsg:null}),3200);}
  // scale and offset of the user's writing, from strokes already accepted (a smaller or shifted character still matches)
  wFitXf(R){const M=this.wMeta||[],raw=this.wRaw||[];const U=[],F=[];M.forEach((m,j)=>{if(m&&m.k>=0&&raw[j]&&!m.help){U.push(...raw[j]);F.push(...R[m.k]);}});
    if(U.length<6)return null;const bb=a=>{let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;a.forEach(p=>{x0=Math.min(x0,p[0]);y0=Math.min(y0,p[1]);x1=Math.max(x1,p[0]);y1=Math.max(y1,p[1]);});return [x0,y0,x1,y1];};
    const u=bb(U),f=bb(F);const su=Math.max(u[2]-u[0],u[3]-u[1]),sf=Math.max(f[2]-f[0],f[3]-f[1]);if(su<.05||sf<.05)return null;const k=Math.max(.45,Math.min(1.6,sf/su));
    return {k,ux:(u[0]+u[2])/2,uy:(u[1]+u[3])/2,fx:(f[0]+f[2])/2,fy:(f[1]+f[3])/2};}
  wSnapLast(){const s=this.state;this.wS=this.wS||[];this.wMeta=this.wMeta||[];this.wMiss=this.wMiss||{};this.wRaw=this.wRaw||[];const j=this.wS.length-1;const S=this.wS[j];if(!S)return;
    const R=this.wCurRef();if(!R){this.wMeta[j]={k:-1};this.setState({wN:this.wS.length});return;}const thr={soft:.21,normal:.17,strict:.12}[s.wMatch||'normal'];
    const used=new Set(this.wMeta.filter(m=>m&&m.k>=0).map(m=>m.k));const exp=[...Array(R.length).keys()].find(i=>!used.has(i));if(exp==null)return;
    const xf=this.wFitXf(R);const T=xf?S.map(p=>[(p[0]-xf.ux)*xf.k+xf.fx,(p[1]-xf.uy)*xf.k+xf.fy]):S;
    const d0=WCheck.strokeDist(S,R[exp],false),d1=xf?WCheck.strokeDist(T,R[exp],false):1,best=Math.min(d0,d1);
    const lenU=S.length>1?S.reduce((a,p,i)=>i?a+Math.hypot(p[0]-S[i-1][0],p[1]-S[i-1][1]):0,0):0;
    if(best<thr&&(lenU>0.02||R[exp].length<4)){this.wRaw[j]=S.slice();this.wS[j]=R[exp].map(p=>[p[0],p[1]]);this.wMeta[j]={k:exp};this.wSnapAn={j,t0:performance.now()};this.wHint=false;}
    else{// why it is wrong: direction, order or shape — said in words, the stroke flashes red and is removed
      const U=xf?T:S;const rev=WCheck.strokeDist([...U].reverse(),R[exp],false);let other=-1;for(let i=0;i<R.length;i++){if(i===exp||used.has(i))continue;if(WCheck.strokeDist(U,R[i],false)<thr){other=i;break;}}
      const dirOf=st=>{const a=st[0],b=st[st.length-1],dx=b[0]-a[0],dy=b[1]-a[1];if(Math.abs(dx)>Math.abs(dy)*1.7)return dx>0?'слева направо':'справа налево';if(Math.abs(dy)>Math.abs(dx)*1.7)return dy>0?'сверху вниз':'снизу вверх';return (dy>0?'сверху вниз':'снизу вверх')+(dx>0?' и вправо':' и влево');};
      const msg=rev<thr&&lenU>0.02?'Не то направление: эта черта пишется '+dirOf(R[exp]):other>=0?'Не тот порядок: сейчас черта '+(exp+1)+', а эта — '+(other+1):'Не похоже на черту '+(exp+1)+' — посмотрите подсказку';
      this.wMiss[exp]=(this.wMiss[exp]||0)+1;this.wMist=(this.wMist||0)+1;this.wS.pop();this.wMeta.length=Math.min(this.wMeta.length,this.wS.length);
      this.wBad={pts:S,t0:performance.now()};
      if(this.wMiss[exp]>=3){const k=this.wS.length;this.wS.push(R[exp].map(p=>[p[0],p[1]]));this.wMeta[k]={k:exp,help:1};this.wHelped=(this.wHelped||0)+1;this.wMiss[exp]=0;this.wSnapAn={j:k,t0:performance.now()};this.wSay('Черту '+(exp+1)+' дорисовала подсказка — запомните её',true);}
      else this.wSay(msg,true);}
    this.setState({wN:this.wS.length,wHas:this.wS.length>0});this.wRender();
    const done=new Set(this.wMeta.filter(m=>m&&m.k>=0).map(m=>m.k)).size;if(done>=R.length)this.wCharDone();}""")

# the next character is ready at once, so its first stroke is never lost
rep("""    if(idx<n-1){this.wNextT=setTimeout(()=>{if(this.state.quiz===qz&&(this.state.wIdx||0)===idx)this.wGo(idx+1);},300);return;}""",
    """    if(idx<n-1){this.wSay('Знак '+(idx+1)+' готов');this.wGo(idx+1);return;}""")
rep("""  wGo(k){clearTimeout(this.wAutoT);clearInterval(this.wAnimT);if(!(this.state.quiz&&this.state.quiz.rev))this.wSave();const c=(this.wCells||[])[k]||{S:[],M:[]};this.wS=c.S.slice();this.wMeta=c.M.slice();this.wMiss={};this.wHint=false;""",
    """  wGo(k){clearTimeout(this.wAutoT);clearInterval(this.wAnimT);if(!(this.state.quiz&&this.state.quiz.rev))this.wSave();const c=(this.wCells||[])[k]||{S:[],M:[],W:[]};this.wS=c.S.slice();this.wMeta=c.M.slice();this.wRaw=(c.W||[]).slice();this.wMiss={};this.wHint=false;this.wBad=null;this.wSnapAn=null;this.drw=false;""")
rep("""  wSave(){const i=this.state.wIdx||0;this.wCells=this.wCells||[];this.wCells[i]={S:(this.wS||[]).slice(),M:(this.wMeta||[]).slice()};}""",
    """  wSave(){const i=this.state.wIdx||0;this.wCells=this.wCells||[];this.wCells[i]={S:(this.wS||[]).slice(),M:(this.wMeta||[]).slice(),W:(this.wRaw||[]).slice()};}""")
rep("""  wUndo(){clearTimeout(this.wAutoT);if(this.wS&&this.wS.length){this.wS.pop();if(this.wMeta)this.wMeta.length=Math.min(this.wMeta.length,this.wS.length);this.wMiss={};""",
    """  wUndo(){clearTimeout(this.wAutoT);if(this.state.wMsg)this.setState({wMsg:null});if(this.wS&&this.wS.length){this.wS.pop();if(this.wMeta)this.wMeta.length=Math.min(this.wMeta.length,this.wS.length);if(this.wRaw)this.wRaw.length=Math.min(this.wRaw.length,this.wS.length);this.wMiss={};""")
rep("""this.wCells=[];this.wHelped=0;this.wMist=0;this.wPeek=false;""", """this.wCells=[];this.wRaw=[];this.wBad=null;this.wSnapAn=null;this.wRect=null;this.wHelped=0;this.wMist=0;this.wPeek=false;if(this.state.wMsg)this.setState({wMsg:null});""")

# rendering: density-aware widths; the finger line fades into the calligraphic stroke; the wrong one flashes and fades
rep("""  wRender(){const c=this.wcEl();if(!c)return;const s=this.state,qz=s.quiz;if(!qz)return;const g=c.getContext('2d'),W=c.width,H=c.height;""",
    """  wRender(){const c=this.wcEl();if(!c)return;const s=this.state,qz=s.quiz;if(!qz)return;const KZ=this.wFit(c);this.wInkC=getComputedStyle(c).color;const g=c.getContext('2d'),W=c.width,H=c.height;""")
rep("""    const lw={thin:7,mid:12,bold:20}[s.wWidth||'mid'];""", """    const lw={thin:7,mid:12,bold:20}[s.wWidth||'mid']*KZ;""")
rep("""      if(snapped&&OP&&OP[m.k]){g.fillStyle=ink;g.strokeStyle=ink;const pr=an&&an.j===j?Math.min(1,(now-an.t0)/170):1;if(pr<1){anim=true;this.wInk(g,OP[m.k],R[m.k],W,H,pr);}else g.fill(OP[m.k]);return;}""",
    """      if(snapped&&OP&&OP[m.k]){g.fillStyle=ink;g.strokeStyle=ink;const pr=an&&an.j===j?Math.min(1,(now-an.t0)/240):1;if(pr<1){anim=true;const raw=(this.wRaw||[])[j];if(raw&&raw.length>1){g.save();g.globalAlpha=.55*(1-pr);g.lineCap='round';g.lineJoin='round';g.lineWidth=lw*.75;g.beginPath();raw.forEach((p,i)=>{if(i)g.lineTo(p[0]*W,p[1]*H);else g.moveTo(p[0]*W,p[1]*H);});g.stroke();g.restore();g.strokeStyle=ink;}this.wInk(g,OP[m.k],R[m.k],W,H,pr);}else g.fill(OP[m.k]);return;}""")
rep("""    if(anim){cancelAnimationFrame(this.wRaf);this.wRaf=requestAnimationFrame(()=>this.wRender());}""",
    """    const bd=this.wBad;if(bd){const pr=(now-bd.t0)/450;if(pr<1){anim=true;g.save();g.globalAlpha=.85*(1-pr);g.strokeStyle=red;g.lineCap='round';g.lineJoin='round';g.lineWidth=lw*.75;g.beginPath();bd.pts.forEach((p,i)=>{if(i)g.lineTo(p[0]*W,p[1]*H);else g.moveTo(p[0]*W,p[1]*H);});g.stroke();g.restore();}else this.wBad=null;}
    if(anim){cancelAnimationFrame(this.wRaf);this.wRaf=requestAnimationFrame(()=>this.wRender());}""")
rep("""const st=R[exp];if(OP&&OP[exp]){g.fillStyle=prc;g.globalAlpha=.25;g.fill(OP[exp]);}g.strokeStyle=prc;g.globalAlpha=.85;g.lineWidth=OP?3:5;g.setLineDash([12,10]);""",
    """const st=R[exp];if(OP&&OP[exp]){g.fillStyle=prc;g.globalAlpha=.25;g.fill(OP[exp]);}g.strokeStyle=prc;g.globalAlpha=.85;g.lineWidth=(OP?3:5)*KZ;g.setLineDash([12*KZ,10*KZ]);""")
rep("""        const a=P(st[0]);g.fillStyle=prc;g.beginPath();g.arc(a[0],a[1],11,0,7);g.fill();g.fillStyle='#fff';g.font='600 13px sans-serif';""",
    """        const a=P(st[0]);g.fillStyle=prc;g.beginPath();g.arc(a[0],a[1],11*KZ,0,7);g.fill();g.fillStyle='#fff';g.font='600 '+Math.round(13*KZ)+'px sans-serif';""")
rep("""const an=Math.atan2(e[1]-f[1],e[0]-f[0]);g.fillStyle=prc;g.beginPath();g.moveTo(e[0]+Math.cos(an)*14,e[1]+Math.sin(an)*14);g.lineTo(e[0]+Math.cos(an+2.5)*14,e[1]+Math.sin(an+2.5)*14);g.lineTo(e[0]+Math.cos(an-2.5)*14,e[1]+Math.sin(an-2.5)*14);""",
    """const an=Math.atan2(e[1]-f[1],e[0]-f[0]),A=14*KZ;g.fillStyle=prc;g.beginPath();g.moveTo(e[0]+Math.cos(an)*A,e[1]+Math.sin(an)*A);g.lineTo(e[0]+Math.cos(an+2.5)*A,e[1]+Math.sin(an+2.5)*A);g.lineTo(e[0]+Math.cos(an-2.5)*A,e[1]+Math.sin(an-2.5)*A);""")
# the order hint after a mistake also shows for the stroke that was just wrong
rep("""(oh!==off&&(this.wMiss||{})[exp]>=1)""", """(oh!=='off'&&(this.wMiss||{})[exp]>=1)""", 0) if False else None

# status line under the cell: the message, else accepted strokes (the total only when tracing)
rep("""    const wCount=!wScr||rev?'':R0?'черта '+Math.min((s.wN||0)+1,R0.length)+' из '+R0.length:'';""",
    """    const okN=((this.wMeta||[]).filter(m=>m&&m.k>=0).length);
    const wCount=!wScr||rev?'':s.wMsg?s.wMsg.t:R0?(trace?'черта '+Math.min(okN+1,R0.length)+' из '+R0.length:okN?'черт написано: '+okN:'начните с первой черты'):'';""")
rep("""      wAskL:trace?'Обведите знак':wScr?'Напишите по памяти':'Напишите на бумаге',wCount,""",
    """      wAskL:trace?'Обведите знак':wScr?'Напишите по памяти':'Напишите на бумаге',wCount,wCountC:s.wMsg&&s.wMsg.bad?'var(--bad)':'var(--mu)',wCountW:s.wMsg?600:400,""")
rep("""      <span style="font-size:12.5px;color:var(--mu);min-height:17px;text-align:center">{{ wCount }}</span>""",
    """      <span style="font-size:13px;color:{{ wCountC }};font-weight:{{ wCountW }};min-height:18px;text-align:center;line-height:1.35;padding:0 8px">{{ wCount }}</span>""")
open(P, 'w', encoding='utf-8').write(s)
print('ok')
s = open(P, encoding='utf-8').read()
# before anything is accepted: compare the shape of the stroke on its own (any size), if it is roughly in the right place
rep("""    const d0=WCheck.strokeDist(S,R[exp],false),d1=xf?WCheck.strokeDist(T,R[exp],false):1,best=Math.min(d0,d1);""",
    """    const nrm=a=>{let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;a.forEach(p=>{x0=Math.min(x0,p[0]);y0=Math.min(y0,p[1]);x1=Math.max(x1,p[0]);y1=Math.max(y1,p[1]);});const m=Math.max(x1-x0,y1-y0,.02);return {pts:a.map(p=>[(p[0]-(x0+x1)/2)/m,(p[1]-(y0+y1)/2)/m]),cx:(x0+x1)/2,cy:(y0+y1)/2,m};};
    const ang=st=>Math.atan2(st[st.length-1][1]-st[0][1],st[st.length-1][0]-st[0][0]);const dAng=(x,y)=>{let d=Math.abs(x-y);return d>Math.PI?2*Math.PI-d:d;};
    let d2=1;if(!xf){const a=nrm(S),b=nrm(R[exp]);if(Math.hypot(a.cx-b.cx,a.cy-b.cy)<.24&&a.m>b.m*.4&&a.m<b.m*1.8&&dAng(ang(S),ang(R[exp]))<.6)d2=WCheck.strokeDist(a.pts,b.pts,false)*.85;}
    const d0=WCheck.strokeDist(S,R[exp],false),d1=xf?WCheck.strokeDist(T,R[exp],false):1,best=Math.min(d0,d1,d2);""")
open(P, 'w', encoding='utf-8').write(s)
print('ok3')
