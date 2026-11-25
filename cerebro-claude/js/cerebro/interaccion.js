/* Interacción: tocar neuronas, ficha del recuerdo, trazar camino, ratón y dedos, línea de tiempo, buscador, leyenda y botones. */
function pick(mx,my){let best=-1,bd=20;S.forEach(([x,y,k],i)=>{if(!vis(i))return;const d=Math.hypot(x-mx,y-my)-5*k;if(d<bd){bd=d;best=i;}});return best;}
function fmt(n){const[m,d]=n.date.split('-');return d+'/'+m+'/2026';}
function chip(j){const b=document.createElement('button');const e=document.createElement('span');e.className='sw';e.style.background=TY[N[j].type][1];b.append(e,document.createTextNode(N[j].label.length>40?N[j].label.slice(0,38)+'…':N[j].label));b.onclick=()=>open(j);return b;}
function focusOn(i){const[x,,z]=P[i];aim={rotY:i===0?rotY:Math.atan2(x,-z),rotX:-.25,zoom:i===0?1:1.3};}
function open(i){if(pathFrom>=0&&i>=0&&i!==pathFrom){showPath(pathFrom,i);return;}
  sel=i;pathSet=null;pathList=null;$('cpath').textContent='';
  if(i<0){$('card').classList.remove('on');aim={...V0,rotY};return;}
  const n=N[i],col=TY[n.type][1];$('cbar').style.background=col;$('ct').textContent=n.label;
  $('cy').textContent='';const e=document.createElement('span');e.className='sw';e.style.background=col;$('cy').append(e,document.createTextNode(TY[n.type][0]+' · '+fmt(n)));
  $('cd').textContent=n.desc;const cl=$('cl');cl.textContent='';const ns=[...nb[i]].filter(vis).sort((a,b)=>N[a].type.localeCompare(N[b].type));
  ns.slice(0,24).forEach(j=>cl.appendChild(chip(j)));$('ch').style.display=ns.length?'':'none';
  $('bPath').textContent='Trazar camino';$('card').classList.add('on');focusOn(i);}
function bfs(a,b){const prev=new Map([[a,-1]]),q=[a];const G=N.map((_,i)=>new Set([...nb[i]].filter(vis)));
  while(q.length){const u=q.shift();if(u===b)break;for(const v of G[u])if(!prev.has(v)){prev.set(v,u);q.push(v);}}
  if(!prev.has(b))return null;const p=[];for(let u=b;u!==-1;u=prev.get(u))p.unshift(u);return p;}
function showPath(a,b){const p=bfs(a,b);pathFrom=-1;cv.classList.remove('pathing');sel=b;pathList=p;pathSet=p?new Set(p):null;
  const n=N[b];$('cbar').style.background=TY[n.type][1];$('ct').textContent=p?'Camino en '+(p.length-1)+' pasos':'Sin camino';$('cy').textContent=N[a].label.slice(0,30)+' → '+n.label.slice(0,30);
  $('cd').textContent=p?'Así se conectan estos dos recuerdos:':'Con los filtros actuales no hay relación entre ellos.';
  const ol=document.createElement('ol');ol.className='path';(p||[]).forEach(j=>{const li=document.createElement('li');li.appendChild(chip(j));ol.appendChild(li);});const cp=$('cpath');cp.textContent='';cp.appendChild(ol);
  $('cl').textContent='';$('ch').style.display='none';$('card').classList.add('on');aim={rotY,rotX:-.3,zoom:1};}
$('bPath').onclick=()=>{if(sel<0)return;pathFrom=sel;cv.classList.add('pathing');toast('Toca otra neurona para trazar el camino desde <b>'+esc(N[sel].label.slice(0,40))+'</b>');$('card').classList.remove('on');};
$('bCopy').onclick=e=>{if(sel<0)return;const n=N[sel];const txt=n.label+' ('+TY[n.type][0].toLowerCase()+', '+fmt(n)+'): '+n.desc;try{navigator.clipboard.writeText(txt).then(()=>toast('Recuerdo copiado'),()=>toast('No se pudo copiar'));}catch(err){toast('No se pudo copiar');}};
$('close').onclick=()=>open(-1);
const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let tt=null;function toast(h){const t=$('toast');t.innerHTML=h;t.classList.add('on');clearTimeout(tt);tt=setTimeout(()=>t.classList.remove('on'),2800);}
const lg=$('legend');
Object.keys(LBL).forEach(k=>{const b=document.createElement('button');b.dataset.k=k;b.setAttribute('aria-pressed',String(off[k]));const e=document.createElement('em');e.style.background=TY[k][1];const c=document.createElement('b');
  b.append(e,document.createTextNode(LBL[k].toUpperCase()),c);b.onclick=ev=>{if(ev.altKey||ev.detail===2){Object.keys(LBL).forEach(x=>off[x]=x===k);}else off[k]=!off[k];document.querySelectorAll('.legend button').forEach(x=>x.setAttribute('aria-pressed',String(off[x.dataset.k])));store.set('off',off);if(sel>=0&&!vis(sel))open(-1);stats();};b.title='Doble clic: ver solo esta';lg.appendChild(b);});
let moved=0;const touch=new Map();
cv.addEventListener('pointerdown',e=>{cv.setPointerCapture(e.pointerId);touch.set(e.pointerId,[e.clientX,e.clientY]);drag=[e.clientX,e.clientY,rotY,rotX];moved=0;aim=null;cv.classList.add('drag');});
cv.addEventListener('pointermove',e=>{const r=cv.getBoundingClientRect();
  if(touch.has(e.pointerId)&&touch.size===2){const a=[...touch.values()];const d0=Math.hypot(a[0][0]-a[1][0],a[0][1]-a[1][1]);touch.set(e.pointerId,[e.clientX,e.clientY]);const b=[...touch.values()];const d1=Math.hypot(b[0][0]-b[1][0],b[0][1]-b[1][1]);zoom=Math.max(.6,Math.min(4,zoom*d1/(d0||d1)));moved=99;return;}
  if(drag){const dx=e.clientX-drag[0],dy=e.clientY-drag[1];moved=Math.max(moved,Math.abs(dx)+Math.abs(dy));rotY=drag[2]+dx*.006;rotX=Math.max(-1.3,Math.min(1.3,drag[3]-dy*.006));return;}
  hov=pick(e.clientX-r.left,e.clientY-r.top);if(hov>=0){tip.style.display='block';tip.textContent=LBL[N[hov].type]?N[hov].label:N[hov].label;tip.style.left=Math.min(e.clientX+12,W-280)+'px';tip.style.top=(e.clientY+14)+'px';}else tip.style.display='none';});
cv.addEventListener('pointerup',e=>{touch.delete(e.pointerId);cv.classList.remove('drag');const r=cv.getBoundingClientRect();if(moved<6){const i=pick(e.clientX-r.left,e.clientY-r.top);if(i>=0||pathFrom<0)open(i);}drag=null;});
cv.addEventListener('pointercancel',e=>{touch.delete(e.pointerId);drag=null;cv.classList.remove('drag');});
cv.addEventListener('pointerleave',()=>{hov=-1;tip.style.display='none';});
cv.addEventListener('wheel',e=>{e.preventDefault();aim=null;zoom=Math.max(.6,Math.min(4,zoom*(e.deltaY<0?1.1:.9)));},{passive:false});
const t=$('t'),day=$('day');
function setDay(v,announce){const prev=maxDay;const before=new Set(N.map((_,i)=>i).filter(vis));maxDay=v;const nowT=performance.now();N.forEach((_,i)=>{if(vis(i)&&!before.has(i))born.set(i,nowT+Math.random()*900);});t.value=v;const d=new Date(D0);d.setDate(d.getDate()+v);const lbl=d.toLocaleDateString('es-ES',{day:'numeric',month:'short'});day.textContent=v===TODAY?'HOY':lbl.toUpperCase();
  if(sel>=0&&!vis(sel))open(-1);stats();
  if(announce){const nw=N.filter(n=>n.day===v&&off[n.type]);if(nw.length){const top=nw.filter(n=>n.type!=='guion'&&n.type!=='dato').slice(0,3).map(n=>esc(n.label.slice(0,34))).join(' · ');toast('<b>'+lbl+'</b> · +'+nw.length+' recuerdos'+(top?'<br>'+top:''));if(v>prev)for(const n of nw.slice(0,12)){const p=newPulse(idx[n.id]);pulses.push(p);}}}}
t.addEventListener('input',()=>setDay(+t.value,true));
let playing=null;const pb=$('play');
function togglePlay(){if(playing){clearInterval(playing);playing=null;pb.textContent='▶';return;}let v=0;setDay(0,true);pb.textContent='❚❚';playing=setInterval(()=>{v++;setDay(v,true);if(v>=TODAY){clearInterval(playing);playing=null;pb.textContent='▶';}},3000);}
pb.onclick=togglePlay;
const q=$('q'),res=$('res');const norm=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');let ri=0,rl=[];
function search(){const s=norm(q.value.trim());hits=new Set();res.textContent='';ri=0;rl=[];if(s.length<2){res.classList.remove('on');return;}
  N.forEach((n,i)=>{if(vis(i)&&norm(n.label+' '+n.desc+' '+TY[n.type][0]).includes(s))hits.add(i);});rl=[...hits].sort((a,b)=>(norm(N[b].label).includes(s))-(norm(N[a].label).includes(s))).slice(0,8);
  if(!rl.length){const li=document.createElement('li');li.className='empty';li.textContent='Nada con "'+q.value.trim()+'"';res.appendChild(li);}
  rl.forEach((j,k)=>{const li=document.createElement('li');const b=document.createElement('button');b.setAttribute('role','option');const e=document.createElement('span');e.className='sw';e.style.background=TY[N[j].type][1];const sm=document.createElement('small');sm.textContent=fmt(N[j]).slice(0,5);
    b.append(e,document.createTextNode(N[j].label.length>44?N[j].label.slice(0,42)+'…':N[j].label),sm);b.onclick=()=>{open(j);res.classList.remove('on');};if(k===0)b.classList.add('act');li.appendChild(b);res.appendChild(li);});res.classList.add('on');}
q.addEventListener('input',search);q.addEventListener('focus',search);
q.addEventListener('keydown',e=>{const bs=res.querySelectorAll('button');if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();if(!bs.length)return;bs[ri]?.classList.remove('act');ri=(ri+(e.key==='ArrowDown'?1:-1)+bs.length)%bs.length;bs[ri].classList.add('act');bs[ri].scrollIntoView({block:'nearest'});}
  else if(e.key==='Enter'&&rl.length){open(rl[ri]);res.classList.remove('on');q.blur();}else if(e.key==='Escape'){q.value='';search();q.blur();}});
document.addEventListener('click',e=>{if(!e.target.closest('.dock'))res.classList.remove('on');});
function setSpin(v){spin=true;}
function setLabels(v){labels=v;$('bLabels').setAttribute('aria-pressed',String(v));store.set('labels',v);}
setSpin(spin);setLabels(labels);
$('bLabels').onclick=()=>setLabels(!labels);
$('bReset').onclick=()=>{open(-1);hits=new Set();q.value='';res.classList.remove('on');aim={...V0};};
$('bFire').onclick=()=>{if(sel>=0)open(-1);fire();};
$('bRand').onclick=()=>{const V=N.map((_,i)=>i).filter(i=>vis(i)&&N[i].type!=='zona'&&i!==0);open(V[Math.floor(Math.random()*V.length)]);};
$('bHow').onclick=()=>{const o=$('how').classList.toggle('on');$('bHow').setAttribute('aria-expanded',String(o));};
document.addEventListener('keydown',e=>{if(['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName))return;
  const k=e.key;if(k==='/'){e.preventDefault();q.focus();}else if(k==='Escape'){if(pathFrom>=0){pathFrom=-1;cv.classList.remove('pathing');}open(-1);$('how').classList.remove('on');}
  else if(k==='ArrowLeft'){aim=null;rotY-=.15;}else if(k==='ArrowRight'){aim=null;rotY+=.15;}else if(k==='ArrowUp'){rotX=Math.max(-1.3,rotX-.12);}else if(k==='ArrowDown'){rotX=Math.min(1.3,rotX+.12);}
  else if(k==='+'||k==='='){aim=null;zoom=Math.min(4,zoom*1.12);}else if(k==='-'){aim=null;zoom=Math.max(.6,zoom/1.12);}
  else if(k===' '&&e.target.tagName!=='BUTTON'){e.preventDefault();togglePlay();}else if(k==='n'||k==='N')setLabels(!labels);else if(k==='f'||k==='F')$('bFire').click();else if(k==='a'||k==='A')$('bRand').click();else if(k==='r'||k==='R')$('bReset').click();});

const use=n=>{try{return window.claude&&window.claude.use?Promise.resolve(window.claude.use(n)):Promise.resolve(null);}catch(e){return Promise.resolve(null);}};
$('t').max=TODAY;$('t').value=TODAY;
