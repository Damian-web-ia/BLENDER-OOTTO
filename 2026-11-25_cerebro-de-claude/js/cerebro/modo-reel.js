/* Modo reel, atajos de teclado y arranque del cerebro. */
/* ---------- modo reel ---------- */
let reelT=null;
function reel(on){document.body.classList.toggle('reel',on);open(-1);panel('',null,false);clearInterval(reelT);if(!on){aim={...V0};return;}
  setSpin(true);setLabels(false);aim={rotY:rotY,rotX:-.35,zoom:1.15};let v=0;setDay(0,false);
  reelT=setInterval(()=>{if(v<TODAY){v++;setDay(v,false);for(const n of N.filter(n=>n.day===v).slice(0,10)){const p=newPulse(idx[n.id]);pulses.push(p);}tone(330+v*30,.4,.03);}else{fire();clearInterval(reelT);reelT=setInterval(()=>fire(),5000);}},3000);}
$('bReel').onclick=()=>reel(true);$('exitReel').onclick=()=>reel(false);
document.addEventListener('keydown',e=>{if(document.body.classList.contains('reel')&&e.key==='Escape')reel(false);if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA'||e.target.tagName==='SELECT')return;if(e.key==='?')$('bAsk').click();});

stats();
for(let i=0;i<(calm?0:cap);i++){const p=newPulse();p.t=rnd();pulses.push(p);}
requestAnimationFrame(frame);
