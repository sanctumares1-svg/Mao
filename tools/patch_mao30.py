#!/usr/bin/env python3
"""Mao 3.0: design v8 on top of the 2.9 engine. Builds www/index.html from index_v29 + v30_* parts."""
import re, sys, shutil
D = '/tmp/claude-0/scripts/'
src = open('/tmp/claude-0/mao/www/index.html', encoding='utf-8').read()
shutil.copy('/tmp/claude-0/mao/www/index.html', D + 'index_v29.html')

def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, n, a[:90])
    return s.replace(a, b)

head = src[:src.index('<x-dc>')]
script = src[src.index('<script type="text/x-dc" data-dc-script>'):]
tail = script[script.index('</script>'):]
body = script[len('<script type="text/x-dc" data-dc-script>'):script.index('</script>')]

# ---- split class into method blocks ----
cls_i = body.index('class Component extends DCLogic {')
pre = body[:cls_i]
cls = body[cls_i:]
rv_i = cls.index('  renderVals(){')
cls_head, cls_rest = cls[:rv_i], cls[rv_i:]
lines = cls_head.split('\n')
blocks = []  # (name, text)
name_re = re.compile(r'^  (?:async )?([A-Za-z_$][\w$]*)\s*(?:\(|=)')
cur = ['__start__', []]
for ln in lines:
    m = name_re.match(ln)
    if m and not ln.startswith('   '):
        blocks.append(cur)
        cur = [m.group(1), [ln]]
    else:
        cur[1].append(ln)
blocks.append(cur)
names = [b[0] for b in blocks]

# new methods
newm = {}
txt = open(D + 'v30_methods.js', encoding='utf-8').read()
for part in txt.split('//@@ ')[1:]:
    nm, code = part.split('\n', 1)
    newm[nm.strip()] = code.rstrip('\n')

REMOVE = {'catPlace', 'catWalk', 'catMood', 'catTips', 'catDown', 'catUp', 'catClick', 'catAsk', 'meow', 'CATPOS', 'SAYS', 'demoCheck', 'cardAnimRun', 'claudeFill'}
out = []
done = set()
for nm, ls in blocks:
    if nm in REMOVE:
        continue
    if nm in newm:
        assert nm not in done, nm
        out.append(newm[nm]); done.add(nm)
        continue
    out.append('\n'.join(ls))
missing = set(newm) - done
assert not missing, missing
cls_head = '\n'.join(out) + '\n'

# ---- small edits in kept methods ----
E = cls_head
E = rep(E, "PK=['m29fix',", "PK=['m30','aiProv','aiKeys','topicSel','m29fix',")
E = rep(E, "defaults(){return {m28:1,lessonSize:20,dailyNew:20,", "defaults(){return {m30:1,m28:1,lessonSize:20,dailyNew:10,aiProv:'free',aiKeys:{},topicSel:null,srs:'on',")
E = rep(E, "hint:'ru',rate:0.8,", "hint:'ru',rate:0.85,")
E = rep(E, "chat:[{r:'cat',t:'Мяу! Я Мао 猫 māo. Спроси про любое слово, грамматику — или попроси составить фразы со словами дня.'}]", "chat:[],sheet:null,addMode:'one',aq:'',addDay:null,addFrom:'tab',partsOpen:false,calM:null,more1:false,upd:null,wPeekS:false")
E = rep(E, "goTab(tab){this.setState({tab,screen:'tab',q:'',ex:null,edit:null,manOpen:false});}", "goTab(tab){this.setState({tab,screen:'tab',q:'',ex:null,edit:null,manOpen:false,sheet:null,result:null});}")
# writing: keep drawing the user's strokes after the answer is shown; outline in --ol
E = rep(E, "wRender(){const c=this.wcEl();if(!c)return;const s=this.state,qz=s.quiz;if(!qz||qz.rev)return;", "wRender(){const c=this.wcEl();if(!c)return;const s=this.state,qz=s.quiz;if(!qz)return;")
E = rep(E, "const gm=s.wGhost||'first';if(R&&(this.wPeek||gm==='on'||(gm==='first'&&qz.kind==='trace'))){if(OP){g.fillStyle=mu;g.globalAlpha=.15;", "const ol=css.getPropertyValue('--ol').trim()||'#D2D2DC';const gm=s.wGhost||'first';if(R&&!qz.rev&&(this.wPeek||gm==='on'||(gm==='first'&&qz.kind==='trace'))){if(OP){g.fillStyle=ol;g.globalAlpha=1;")
E = rep(E, "if(exp!=null&&(this.wHint||", "if(exp!=null&&!qz.rev&&(this.wHint||")
E = rep(E, "wReset(){clearTimeout(this.wAutoT);clearTimeout(this.wNextT);this.wCells=[];", "wReset(){clearTimeout(this.wAutoT);clearTimeout(this.wNextT);if(this.state.wPeekS)this.setState({wPeekS:false});this.wCells=[];")
E = rep(E, "wGo(k){clearTimeout(this.wAutoT);clearInterval(this.wAnimT);this.wSave();", "wGo(k){clearTimeout(this.wAutoT);clearInterval(this.wAnimT);if(!(this.state.quiz&&this.state.quiz.rev))this.wSave();")
# offline answers without the cat voice
E = E.replace("'Мяу, словарь ещё загружается — спросите через пару секунд.'", "'Словарь ещё загружается — спросите через пару секунд.'")
E = rep(E, "'Мяу! На какую тему подобрать слова? Например: «подбери слова про еду».'", "'На какую тему подобрать слова? Например: «подбери слова про еду».'")
E = rep(E, "'Мяу… на тему «'+topic+'» я ничего не нашла. Попробуйте другое слово: «еда», «семья», «работа», «погода».'", "'На тему «'+topic+'» в словаре ничего не нашлось. Попробуйте другое слово: «еда», «семья», «работа», «погода».'")
E = rep(E, "'\\n\\nЧтобы учить их, на главной впишите тему «'+topic+'» и нажмите «Мао подберёт».'", "'\\n\\nЧтобы учить их: «Слова» → «Следующий урок» → своя тема «'+topic+'».'")
E = rep(E, "return 'Мяу! Я работаю без интернета и умею:\\n• разобрать иероглиф — пришлите его, например 饭\\n• подобрать слова по теме — «подбери слова про еду»\\n• найти слово — «как сказать кошка»';", "return 'Без нейросети я понимаю иероглиф (饭), русское слово («как сказать кошка») или «подбери слова про еду». Для свободных вопросов включите нейросеть в Настройках.';")
# pickWords: neutral wording; a topic without words opens «Добавить слова» in a new lesson instead of a dead end
E = rep(E, "return this.toast('Мао не смогла ответить — проверьте интернет или добавьте слова поиском');", "return this.toast('Нейросеть не ответила — добавьте слова поиском');")
E = rep(E, "if(!list.length)return this.toast(ai?'Мао не нашла новых слов на эту тему — добавьте их поиском':'Мао не нашла в словаре слов на тему «'+topic+'». Попробуйте другое слово — например «еда», «работа», «погода» — или добавьте слова поиском');",
        "if(!list.length){const go=()=>{this.openAdd(this.state.cur,'one');this.toast('В теме «'+topic+'» нет готовых слов — добавьте свои');};if(newTopic&&!(s.cur&&L0.t===newTopic&&!this.dw(s.cur).length))return this.startLesson(newTopic,go);return go();}")
E = rep(E, "this.toast('Мао подобрала '+add.length+' '+pl(add.length,WF)+(add.length<N?' (больше на эту тему не нашлось)':''));", "if(add.length<N)this.toast('Подобрано '+add.length+' '+pl(add.length,WF)+' — больше на эту тему не нашлось');")
E = rep(E, "(flag?', проверьте вручную '+flag+' (✎ Править в «Словах»)':'')", "(flag?', проверьте вручную '+flag+' («Слова» → кнопка правки у урока)':'')")
E = rep(E, "upd.push([w.id,'нет перевода — нажмите ✎, чтобы вписать'])", "upd.push([w.id,'нет перевода — впишите в «Править урок»'])")
E = rep(E, "else{const lat=rest.replace(/[—–:=|\\-]+/g,' ').trim();if(lat)items.push({q:lat,m:ru});}};", "else{const lat=rest.replace(/[—–:=|\\-]+/g,' ').trim();if(lat)items.push({q:lat,m:ru});else if(ru)items.push({q:ru,ru:1});}};")
E = rep(E, "const res=it=>{const L=isHan(it.q)?exact(it.q):E.best(it.q);", "const res=it=>{const L=isHan(it.q)?exact(it.q):it.ru?E.byRu(it.q,6):E.best(it.q);")
assert 'catMood' not in E and 'meow' not in E, 'cat left'

# ---- migration ----
pre = rep(pre, "function migrate(d){if(!d)return d;", "function migrate(d){if(!d)return d;if(!d.m30){const ls=+(d.lessonSize||d.dailyNew||10);d={...d,m30:1,method:d.method==='snow'?'snow':'fast',dailyNew:Math.max(3,Math.min(30,ls)),hint:'ru',writeMode:d.writeMode==='paper'?'paper':'screen',srs:'on',aiProv:d.aiProv||'free',aiKeys:d.aiKeys||{},wGrid:d.wGrid==='mi'?'mi':'on'};}")
pre = pre.replace("const DOW=", open(D + 'v30_helpers.js', encoding='utf-8').read() + "\nconst DOW=", 1)

rv = open(D + 'v30_rv.js', encoding='utf-8').read()
cls_rest = rv + '\n}\n'

tpl = open(D + 'v30_tpl.html', encoding='utf-8').read()
head = rep(head, '<link rel="stylesheet" href="fonts.css">\n', '')
newsrc = head + tpl + '\n<script type="text/x-dc" data-dc-script>' + pre + E + cls_rest + tail
for bad in ['catPlace', 'catVis', 'Мяу']:
    assert bad not in newsrc, bad
open('/tmp/claude-0/mao/www/index.html', 'w', encoding='utf-8').write(newsrc)
print('ok', len(newsrc))
