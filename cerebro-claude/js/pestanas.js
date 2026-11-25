/* Pestañas: cambia entre Cerebro y Mapa del sistema y recuerda la última que abriste. */
/* pestañas */
const brandB=document.querySelector('.brand b'),brandS=document.querySelector('.brand small');const B0=[brandB.textContent,brandS.textContent];
function tab(map){window.MAPON=map;document.body.classList.toggle('map',map);$m('tabB').setAttribute('aria-selected',String(!map));$m('tabM').setAttribute('aria-selected',String(map));
  brandB.textContent=map?'MAPA DEL SISTEMA':B0[0];brandS.textContent=map?'Cómo trabaja Claude cada noche':B0[1];if(map)mSize();try{localStorage.setItem('cerebro.tab',map?'m':'b');}catch(e){}}
$m('tabB').onclick=()=>tab(false);$m('tabM').onclick=()=>tab(true);
addEventListener('keydown',e=>{if(window.MAPON&&e.key==='Escape')close();});
let t0='b';try{t0=localStorage.getItem('cerebro.tab')||'b';}catch(e){}
if(location.hash==='#mapa')t0='m';tab(t0==='m');
