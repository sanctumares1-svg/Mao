// ---- Mao 3.0 (design v8) ----
const APPV='3.0';
const MNAME=['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'];
// Material Symbols Rounded, bundled offline as fonts/icons.woff (only these glyphs)
const ICONS={check:'',today:'',book:'',forum:'',settings:'',more:'',less:'',cat:'',list:'',tr:'',help:''};
const PROV={free:{n:'без ключа',l:'Без ключа · бесплатно',d:'Pollinations: ничего вводить не нужно, но бывает медленно',key:false},
  gemini:{n:'Gemini Flash',l:'Gemini Flash · бесплатно',d:'Рекомендую. Быстрый, хороший русский и китайский. Ключ в Google AI Studio, без карты',key:true,help:'Ключ: aistudio.google.com → Get API key. Хранится только на телефоне.'},
  glm:{n:'GLM Flash',l:'GLM Flash · бесплатно',d:'Z.ai (Zhipu), китайская компания, сильный китайский. Ключ без карты',key:true,help:'Ключ: z.ai → API Keys. Хранится только на телефоне.'},
  openrouter:{n:'OpenRouter free',l:'OpenRouter · бесплатные модели',d:'DeepSeek и другие с пометкой :free, около 50 запросов в день',key:true,help:'Ключ: openrouter.ai → Keys. Хранится только на телефоне.'}};
const AISYS='Ты учитель китайского для русскоязычного взрослого, уровень HSK 1–3. Всегда пиши иероглифы с пиньинем с тоновыми знаками. Отвечай кратко, по-русски. Без markdown.';
const PURL={gemini:'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions',glm:'https://api.z.ai/api/paas/v4/chat/completions',openrouter:'https://openrouter.ai/api/v1/chat/completions'};
const PMOD={gemini:['gemini-flash-latest','gemini-2.5-flash'],glm:['glm-4.7-flash','glm-4.5-flash'],openrouter:['openrouter/free']};
let AISEQ=0;const AIP={};
window.__aiChunk=(id,t)=>{const p=AIP[id];if(p)p.on(String(t||''));};
window.__aiDone=(id,ok,t,code)=>{const p=AIP[id];if(!p)return;delete AIP[id];if(ok)p.res(String(t||''));else p.rej(Object.assign(new Error(t||'error'),{code:+code||0}));};
// in a browser without the Android shell: a plain request (the phone app streams through EvineNative.chat)
async function aiFetch(id,P,key,msgs){const prov=Object.keys(PROV).find(k=>PROV[k]===P);try{const r=await fetch(PURL[prov],{method:'POST',headers:{'content-type':'application/json',authorization:'Bearer '+key},body:JSON.stringify({model:PMOD[prov][0],messages:msgs})});if(!r.ok)return window.__aiDone(id,false,'HTTP '+r.status,r.status);const j=await r.json();const t=(j.choices&&j.choices[0].message.content)||'';window.__aiChunk(id,t);window.__aiDone(id,true,t,200);}catch(e){window.__aiDone(id,false,String(e),0);}}
const aiErr=e=>{const c=e&&e.code;return c===429?'Лимит на сегодня исчерпан':c===401||c===403?'Ключ не подошёл':/timeout/.test((e&&e.message)||'')?'Нейросеть не ответила вовремя':'Нет связи с нейросетью';};
const clean=t=>String(t||'').replace(/^#+\s*/gm,'').replace(/\*\*|__/g,'').replace(/[*#]/g,'').trim();
const shortM=m=>{m=String(m||'');const a=m.split(/;\s*/)[0];return a.length>42?a.slice(0,40)+'…':a;};
const matchW=(w,q)=>{const t=q.trim().toLowerCase();if(!t)return false;const sp=strip(t);return w.h.includes(q.trim())||(!!sp&&/^[a-z]+$/.test(sp)&&strip(w.p).startsWith(sp))||(w.m||'').toLowerCase().includes(t);};
