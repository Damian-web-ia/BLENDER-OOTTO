/* Galaxia: nebulosas y estrellas del fondo, disco con brazos espirales, y posición de Claude, las fases y las herramientas en órbita. */
/* fondo: nebulosas y estrellas */
function buildSky(){neb=document.createElement('canvas');neb.width=Math.ceil(mW*1.4*mDpr);neb.height=Math.ceil(mH*1.4*mDpr);const n=neb.getContext('2d');n.scale(mDpr,mDpr);const w=mW*1.4,h=mH*1.4;
  const blobs=[[.28,.35,.42,'58,44,88',.22],[.74,.3,.36,'44,66,82',.2],[.62,.72,.46,'96,58,30',.2],[.2,.78,.32,'60,74,60',.14],[.5,.5,.3,'120,70,36',.16],[.86,.66,.26,'70,60,100',.13]];
  for(const[x,y,r,c,a]of blobs){for(let i=0;i<5;i++){const cx=(x+gauss()*.05)*w,cy=(y+gauss()*.05)*h,rr=r*Math.min(w,h)*(.6+mRnd()*.6);const gr=n.createRadialGradient(cx,cy,0,cx,cy,rr);gr.addColorStop(0,`rgba(${c},${a*.55})`);gr.addColorStop(.5,`rgba(${c},${a*.22})`);gr.addColorStop(1,`rgba(${c},0)`);n.fillStyle=gr;n.fillRect(0,0,w,h);}}
  for(let i=0;i<260;i++){const x=mRnd()*w,y=mRnd()*h,r=mRnd()*1.6;n.fillStyle=`rgba(255,${200+mRnd()*55|0},${170+mRnd()*85|0},${.04+mRnd()*.08})`;n.beginPath();n.arc(x,y,r*3,0,7);n.fill();}
  stars=[];for(let i=0;i<Math.round(mW*mH/2600);i++){const l=mRnd();stars.push({x:mRnd(),y:mRnd(),l,s:.35+l*1.3,tw:mRnd()*6.28,sp:.5+mRnd()*2,c:mRnd()<.12?'255,214,170':mRnd()<.2?'190,205,255':'245,240,232'});}}
function mSize(){mDpr=Math.min(devicePixelRatio||1,2);mW=mCv.clientWidth;mH=mCv.clientHeight;mCv.width=mW*mDpr;mCv.height=mH*mDpr;if(mW&&mH)buildSky();}
addEventListener('resize',mSize);
/* galaxia: disco con brazos espirales */
const disk=[];for(let i=0;i<2600;i++){const arm=i%2,r=.18+Math.pow(mRnd(),.75)*2.25;const a=arm*Math.PI+r*2.1+gauss()*.42;
  const warm=Math.max(0,1-r/1.3);disk.push({r,a,y:gauss()*.05*(1.3-r*.3),s:.5+mRnd()*1.1,w:warm,b:.25+mRnd()*.75});}
/* nodos */
const nodes=[];const C={x:0,y:0,z:0,col:OR,kind:'core',name:'Claude',desc:'El director: elige la idea, escribe el guion, revisa, publica y aprende de los resultados. Todo pasa por aquí.'};nodes.push(C);
const R0=1.3;
FASES.forEach((p,k)=>{const a=k*Math.PI/2+Math.PI/4;const hub={a,x:Math.cos(a)*R0,y:0,z:Math.sin(a)*R0,col:p.col,kind:'hub',name:p.name,num:p.n,desc:p.sub,ph:k,list:p.tools.map(t=>t[0])};nodes.push(hub);p.hub=hub;
  p.items=p.tools.map((t,j)=>{const o={b:j/p.tools.length*Math.PI*2,rr:.46+(j%2)*.1,tilt:.3,x:0,y:0,z:0,col:p.col,kind:'tool',name:t[0],desc:t[1],via:t[2],ph:k,hub};nodes.push(o);return o;});});
function place(){FASES.forEach((p,k)=>{const h=p.hub;h.a=k*Math.PI/2+Math.PI/4+T/90000;h.x=Math.cos(h.a)*R0;h.z=Math.sin(h.a)*R0;
  p.items.forEach(o=>{const b=o.b+T/14000*(1/(o.rr*2));o.x=h.x+Math.cos(b)*o.rr;o.z=h.z+Math.sin(b)*o.rr;o.y=Math.sin(b)*o.rr*o.tilt;});});}
const links=[];FASES.forEach(p=>{links.push([C,p.hub,3]);p.items.forEach(t=>links.push([p.hub,t,2]));});
