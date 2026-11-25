/* Sonido: notas en cada disparo y música ambiental de fondo siempre activa. */
/* ---------- sonido ---------- */
let snd=false,ac=null;
function tone(f,d,v){if(!snd)return;try{ac=ac||new (window.AudioContext||window.webkitAudioContext)();const o=ac.createOscillator(),g=ac.createGain();o.type='sine';o.frequency.value=f;g.gain.setValueAtTime(0,ac.currentTime);g.gain.linearRampToValueAtTime(v,ac.currentTime+.02);g.gain.exponentialRampToValueAtTime(.0001,ac.currentTime+d);o.connect(g).connect(ac.destination);o.start();o.stop(ac.currentTime+d+.05);}catch(e){}}
const fire0=fire;fire=function(){fire0();[220,277,330,440].forEach((f,k)=>setTimeout(()=>tone(f,1.4,.05),k*70));};
/* música ambiental generativa, siempre activa */
let music=null;
function startMusic(){snd=true;try{ac=ac||new (window.AudioContext||window.webkitAudioContext)();if(ac.state==='suspended')ac.resume();if(music)return;
  const out=ac.createGain();out.gain.value=0;out.gain.linearRampToValueAtTime(.085,ac.currentTime+4);
  const lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.value=900;lp.Q.value=.4;
  const dl=ac.createDelay(2);dl.delayTime.value=.62;const fb=ac.createGain();fb.gain.value=.38;const wet=ac.createGain();wet.gain.value=.35;
  lp.connect(out);lp.connect(dl);dl.connect(fb).connect(dl);dl.connect(wet).connect(out);out.connect(ac.destination);
  const lfo=ac.createOscillator(),lg=ac.createGain();lfo.frequency.value=.05;lg.gain.value=350;lfo.connect(lg).connect(lp.frequency);lfo.start();
  const CH=[[110,220,261.6,329.6],[87.3,174.6,261.6,349.2],[130.8,196,261.6,329.6],[98,196,246.9,293.7]];let ci=0;
  function chord(){const t=ac.currentTime,c=CH[ci++%CH.length];c.forEach((f,k)=>{[0,4].forEach(dt=>{const o=ac.createOscillator(),g=ac.createGain();o.type=k?'sine':'triangle';o.frequency.value=f;o.detune.value=dt*(k%2?1:-1);
    g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(k?.11:.16,t+2.6);g.gain.setValueAtTime(k?.11:.16,t+6);g.gain.linearRampToValueAtTime(0,t+9.5);o.connect(g).connect(lp);o.start(t);o.stop(t+9.7);});});
    const sc=[523.3,587.3,659.3,784,880];for(let n=0;n<3;n++){const tt=t+1.5+n*2.2+Math.random()*.8,o=ac.createOscillator(),g=ac.createGain();o.type='sine';o.frequency.value=sc[Math.floor(Math.random()*sc.length)];g.gain.setValueAtTime(0,tt);g.gain.linearRampToValueAtTime(.05,tt+.05);g.gain.exponentialRampToValueAtTime(.0001,tt+2.4);o.connect(g).connect(lp);o.start(tt);o.stop(tt+2.5);}}
  chord();music=setInterval(chord,8000);}catch(e){}}
['pointerdown','keydown','touchstart','wheel'].forEach(ev=>addEventListener(ev,startMusic,{passive:true}));
document.addEventListener('visibilitychange',()=>{if(!ac)return;if(document.hidden)ac.suspend();else ac.resume();});
startMusic();
