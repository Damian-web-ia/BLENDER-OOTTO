/* Interacción: arrastrar para girar, rueda para acercar, tocar una herramienta, ficha y botones de fase. */
/* interacción */
mCv.addEventListener('pointerdown',e=>{mDrag={x:e.clientX,y:e.clientY,rx:mRotX,ry:mRotY,m:0};mCv.setPointerCapture(e.pointerId);mCv.style.cursor='grabbing';});
mCv.addEventListener('pointermove',e=>{if(mDrag){const dx=e.clientX-mDrag.x,dy=e.clientY-mDrag.y;mDrag.m=Math.max(mDrag.m,Math.abs(dx)+Math.abs(dy));mRotY=mDrag.ry+dx*.006;mRotX=Math.max(-.5,Math.min(1.2,mDrag.rx+dy*.004));mAim=null;}else{mCv.style.cursor=hit(e)?'pointer':'grab';}});
mCv.addEventListener('pointerup',e=>{const was=mDrag&&mDrag.m<6;mDrag=null;mCv.style.cursor='grab';if(was){const h=hit(e);h?abrirFicha(h):close();}});
mCv.addEventListener('wheel',e=>{e.preventDefault();mZoom=Math.max(.6,Math.min(1.9,mZoom*(e.deltaY>0?.92:1.08)));},{passive:false});
function hit(e){const r=mCv.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;let best=null,bd=1e9;for(const n of nodes){const p=mS.get(n);if(!p)continue;const rad=(n.kind==='core'?50:n.kind==='hub'?26:18)*p[2]*SK;const d=Math.hypot(p[0]-x,p[1]-y);if(d<rad+12&&d<bd){bd=d;best=n;}}return best;}
const $m=id=>document.getElementById(id);
function abrirFicha(n){mSel=n;focus=n.ph>=0?n.ph:-1;legendSync();
  $m('mbar').style.background=n.col;$m('mbar').style.boxShadow='0 0 12px '+n.col;$m('mph').textContent=n.kind==='core'?'EL CENTRO':n.kind==='hub'?'FASE '+n.num:'FASE '+(n.ph+1)+' · '+FASES[n.ph].name.toUpperCase();
  $m('mt').textContent=n.name;$m('md').textContent=n.desc;$m('mvia').textContent=n.via||'';$m('mvia').hidden=!n.via;
  const L=n.kind==='hub'?n.list:n.kind==='core'?FASES.map(p=>p.n+'. '+p.name):[];$m('mlist').innerHTML=L.map(x=>'<li>'+x+'</li>').join('');
  $m('mcard').hidden=false;const h=n.kind==='tool'?n.hub:n.kind==='hub'?n:null;if(h)mAim=-h.a-Math.PI/2;
  for(let i=0;i<8;i++)setTimeout(()=>{if(n.kind==='tool')mPulses.push({path:[C,n.hub,n],seg:0,t:0,v:.85,st:i%3});else if(n.kind==='hub'){const p=FASES[n.ph];mPulses.push({path:[C,n,p.items[i%p.items.length]],seg:0,t:0,v:.85,st:i%3});}else spawn(i%4);},i*150);}
function close(){mSel=null;focus=-1;$m('mcard').hidden=true;legendSync();}
$m('mclose').onclick=close;
const leg=$m('mleg');leg.innerHTML=FASES.map((p,k)=>`<button data-k="${k}" style="color:${p.col}" aria-pressed="false"><i style="background:${p.col}">${p.n}</i><span>${p.name}</span></button>`).join('');
leg.querySelectorAll('button').forEach(b=>b.onclick=()=>{const k=+b.dataset.k;if(focus===k)close();else abrirFicha(FASES[k].hub);});
function legendSync(){leg.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.k===focus)));}
function label(txt,x,y,f,al,mSize,bold,col){if(al<=.02)return;g.globalAlpha=al;g.font=`${bold?'700':'500'} ${Math.round(mSize*Math.max(.85,Math.min(1.12,f)))}px ${bold?'Montserrat':'Inter'},sans-serif`;g.textAlign='center';g.textBaseline='middle';
  g.lineWidth=4;g.strokeStyle='rgba(8,7,10,.8)';g.strokeText(txt,x,y);g.fillStyle=col||'#f5f0ea';g.fillText(txt,x,y);g.globalAlpha=1;}
