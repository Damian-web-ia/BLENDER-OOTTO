/* Pregúntale: Claude responde con los recuerdos, lee en voz alta y dicta (solo funciona dentro de Claude). */
/* ---------- paneles ---------- */
function panel(id,btn,on){['pAsk'].forEach(p=>{const o=p===id&&on;$(p).classList.toggle('on',o);});['bAsk'].forEach(b=>$(b).setAttribute('aria-expanded',String(b===btn&&on)));$('how').classList.remove('on');}
$('bAsk').onclick=()=>{const on=!$('pAsk').classList.contains('on');panel('pAsk','bAsk',on);if(on)setTimeout(()=>$('qa').focus(),30);};
/* ---------- pregúntale ---------- */
const SUG=['¿Qué vídeo ha funcionado mejor?','¿Qué tengo pendiente?','¿Qué reglas tienen mis vídeos?','¿Qué aprendimos de los errores?','¿Qué sale esta semana?'];
SUG.forEach(t=>{const b=document.createElement('button');b.type='button';b.textContent=t;b.onclick=()=>{$('qa').value=t;ask();};$('sugs').appendChild(b);});
let sample=null,tts=null,dict=null,lastAns='',askCtl=null;
use('sample').then(x=>{sample=x;if(!x){$('bAsk').hidden=true;}}).catch(()=>{$('bAsk').hidden=true;});
use('tts').then(x=>{tts=x;if(x)x.onState(({state})=>{$('bSpeak').textContent=state==='speaking'?'■ Parar':'🔊 Escuchar';});}).catch(()=>{});
use('dictation').then(x=>{dict=x;if(x){$('bMic').hidden=false;x.onPartial(({text})=>{$('qa').value=micBase+text;});x.onFinal(({text})=>{micBase+=text+' ';$('qa').value=micBase;});x.onState(({state})=>{$('bMic').setAttribute('aria-pressed',String(state==='listening'));$('bMic').textContent=state==='listening'?'■':'🎙';if(state==='idle'&&micBase.trim())ask();});}}).catch(()=>{});
if(!window.claude){$('bAsk').hidden=true;}
let micBase='';
$('bMic').onclick=()=>{if(!dict)return;if($('bMic').getAttribute('aria-pressed')==='true'){dict.stop().catch(()=>{});return;}micBase='';$('qa').value='';dict.start().catch(e=>{if(e&&e.code==='not_granted')$('bMic').hidden=true;});};
$('fAsk').addEventListener('submit',e=>{e.preventDefault();ask();});
function memText(){return N.map(n=>n.id+' | '+TY[n.type][0]+' | '+fmt(n)+' | '+n.label+' | '+n.desc).join('\n');}
async function ask(){const qq=$('qa').value.trim();if(!qq||!sample)return;if(askCtl)askCtl.abort();askCtl=new AbortController();
  const a=$('ans'),l=$('ansl');a.className='ans wait';a.textContent='Pensando…';l.textContent='';$('bSpeak').hidden=true;$('bSend').disabled=true;
  const prompt='Eres el cerebro de Claude sobre el taller EKORUEDAS de Damián. Hoy es 25/11/2026. Responde en español de España, cercano y breve (máximo 4 frases), usando SOLO estos recuerdos. Si la respuesta no está en ellos, dilo claramente. No inventes datos.\nDevuelve SOLO un JSON así: {"respuesta":"...","ids":["id1","id2"]} con hasta 8 ids de los recuerdos que has usado.\n\nRECUERDOS (id | categoría | fecha | título | detalle):\n'+memText()+'\n\nPREGUNTA: '+qq;
  try{let r=null;try{r=await sample.json(prompt,{signal:askCtl.signal,modelTier:'quick',cache:false});}catch(e){if(e&&e.code)throw e;const t=await sample(prompt,{signal:askCtl.signal,modelTier:'quick',cache:false});const m=(t.text||'').match(/\{[\s\S]*\}/);r=m?JSON.parse(m[0]):{respuesta:t.text,ids:[]};}
    const txt=String(r&&r.respuesta||'No he encontrado nada sobre eso.');lastAns=txt;a.className='ans';a.textContent=txt;
    const ids=(Array.isArray(r&&r.ids)?r.ids:[]).map(String).filter(x=>idx[x]!=null);hits=new Set(ids.map(x=>idx[x]));ids.forEach(x=>l.appendChild(chip(idx[x])));
    if(ids.length){sel=-1;$('card').classList.remove('on');for(const x of ids.slice(0,6)){const p=newPulse(0);p.b=adj[0].includes(idx[x])?idx[x]:p.b;pulses.push(p);}fire();}
    $('bSpeak').hidden=!tts;
  }catch(e){a.className='ans';a.textContent=e&&e.code==='rate_limited'?'Demasiadas preguntas seguidas. Espera un momento.':e&&e.code==='not_granted'?'Esta vista no permite preguntar a Claude.':'No he podido responder ahora. Inténtalo de nuevo.';}
  finally{$('bSend').disabled=false;}}
$('bSpeak').onclick=()=>{if(!tts)return;if($('bSpeak').textContent.startsWith('■')){tts.stop();return;}tts.speak(lastAns,{voice:'rounded',language:'es'}).catch(()=>{});};
