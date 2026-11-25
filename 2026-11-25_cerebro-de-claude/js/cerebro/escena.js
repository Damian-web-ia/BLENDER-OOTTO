/* Escena 3D: lienzo, brillos, cámara y proyección, hilos que ondulan como pelo, impulsos y el bucle de animación. */
const cv=document.getElementById('c'),cx=cv.getContext('2d'),tip=document.getElementById('tip');
function sprite(rgb,core,soft){const c=document.createElement('canvas');c.width=c.height=96;const g=c.getContext('2d');const r=g.createRadialGradient(48,48,0,48,48,48);
  r.addColorStop(0,'rgba(255,255,255,1)');r.addColorStop(core,`rgba(${rgb},1)`);r.addColorStop(soft,`rgba(${rgb},.28)`);r.addColorStop(1,`rgba(${rgb},0)`);g.fillStyle=r;g.fillRect(0,0,96,96);return c;}
const rgbOf=h=>[1,3,5].map(k=>parseInt(h.slice(k,k+2),16)).join(',');
const SO=sprite('255,122,26',.12,.34),SH=sprite('255,140,50',.06,.3),SP={},PH={},RGB={};
Object.keys(TY).forEach(k=>{RGB[k]='255,150,70';SP[k]=sprite(rgbOf(TY[k][1]),.22,.4);PH[k]=sprite(RGB[k],.06,.3);});
const calm=false;
const V0={rotY:.85,rotX:-.38,zoom:1};
let W=0,H=0,dpr=1,rotY=V0.rotY,rotX=V0.rotX,zoom=V0.zoom,drag=null,sel=-1,hov=-1,hits=new Set(),burst=0,auto=2,last=performance.now(),flash=0;
let threads=true,spin=true,labels=store.get('labels',false),aim=null,pathFrom=-1,pathSet=null,pathList=null,cap=70,fireUntil=0;
function size(){dpr=Math.min(devicePixelRatio||1,2);W=cv.clientWidth;H=cv.clientHeight;cv.width=W*dpr;cv.height=H*dpr;}
new ResizeObserver(size).observe(cv);size();
let S=[];
function project(){const s=Math.min(W*(W<760?.44:.47),H*.36)*zoom,cy=Math.cos(rotY),sy=Math.sin(rotY),cxr=Math.cos(rotX),sx=Math.sin(rotX),f=3.2,oy=H*(W<760?.5:.47);
  S=P.map(([x,y,z])=>{const x1=x*cy+z*sy,z1=-x*sy+z*cy;const y2=y*cxr-z1*sx,z2=y*sx+z1*cxr;const k=f/(f+z2);return[W/2+x1*s*k,oy-y2*s*k,k,z2];});}
const pulses=[];
function newPulse(a){if(a==null){const V=N.map((_,i)=>i).filter(i=>vis(i)&&adj[i].length);a=V.length?V[Math.floor(rnd()*V.length)]:0;}const n=adj[a];return{a,b:n.length?n[Math.floor(rnd()*n.length)]:a,t:0,v:.9+rnd()*1.4,life:3+Math.floor(rnd()*6),c:N[a].type};}
const $=id=>document.getElementById(id);
function stats(){rebuild();let f=0,l=0;N.forEach((n,i)=>{if(vis(i))f++;});ML.forEach(([a,b])=>{if(vis(a)&&vis(b))l++;});SL.forEach(([a,b])=>{if(vis(a)&&vis(b))l++;});
  cap=Math.round(Math.min(70,f*.4));$('sF').textContent=f;$('sL').textContent=l;$('sD').textContent=maxDay+1;
  document.querySelectorAll('.legend button').forEach(b=>{const k=b.dataset.k;b.querySelector('b').textContent=N.filter(n=>n.type===k&&n.day<=maxDay).length;});}
let NOW=0;
function ctl(a,b){const A=S[a],B=S[b];const dx=B[0]-A[0],dy=B[1]-A[1],L=Math.hypot(dx,dy)||1;const lo=Math.min(a,b),hi=Math.max(a,b);const ph=((lo*7919+hi*104729)%997)/997*6.283;
  const sw=Math.sin(NOW/1300+ph)*.55+Math.sin(NOW/2900+ph*1.7)*.45;const amp=L*(.12+.07*Math.sin(ph*3))*(threads?1:0)*sw+L*.06*Math.cos(ph)*(threads?1:0);const s2=a<b?1:-1;
  return[(A[0]+B[0])/2-dy/L*amp*s2,(A[1]+B[1])/2+dx/L*amp*s2];}
function qpt(A,C,B,t){const u=1-t;return[u*u*A[0]+2*u*t*C[0]+t*t*B[0],u*u*A[1]+2*u*t*C[1]+t*t*B[1]];}
function qseg(A,C,B,t0,t1){const p0=qpt(A,C,B,t0),p1=qpt(A,C,B,t1);const tm=(t0+t1)/2,pm=qpt(A,C,B,tm);const c=[2*pm[0]-(p0[0]+p1[0])/2,2*pm[1]-(p0[1]+p1[1])/2];cx.moveTo(p0[0],p0[1]);cx.quadraticCurveTo(c[0],c[1],p1[0],p1[1]);}
let fire=function(){flash=1;fireUntil=performance.now()+2600;for(let k=0;k<Math.round(cap/2);k++){const p=newPulse(0);pulses.push(p);}};
function frame(now){if(window.MAPON){last=now;requestAnimationFrame(frame);return;}const dt=Math.min(.05,(now-last)/1000);last=now;NOW=calm?0:now;
  if(aim){let d=((aim.rotY-rotY+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI;rotY+=d*Math.min(1,dt*4);rotX+=(aim.rotX-rotX)*Math.min(1,dt*4);zoom+=(aim.zoom-zoom)*Math.min(1,dt*4);if(Math.abs(d)<.002&&Math.abs(aim.zoom-zoom)<.002)aim=null;}
  else if(spin&&!drag&&sel<0)rotY+=dt*.15;
  if(!calm&&sel<0&&spin){auto+=dt;if(auto>11)auto=0;if(auto>6&&auto-dt<=6)fire();}
  const target=(sel>=0||pathSet)?1:(now<fireUntil?1:0);burst+=(target-burst)*Math.min(1,dt*6);flash*=Math.pow(.2,dt);
  project();cx.setTransform(dpr,0,0,dpr,0,0);cx.clearRect(0,0,W,H);
  const src=sel>=0?sel:0;
  const lit=pathSet?pathSet:(sel>0?new Set([sel,...nb[sel],...[...nb[sel]].flatMap(j=>N[j].type==='zona'||j===0?[]:[...nb[j]])]):null);
  cx.globalCompositeOperation='source-over';cx.lineWidth=.6;
  for(const[a,b]of ML){const k=(S[a][2]+S[b][2])/2;const ba=born.has(a)?Math.max(0,Math.min(1,(now-born.get(a))/2200)):1,bb=born.has(b)?Math.max(0,Math.min(1,(now-born.get(b))/2200)):1;let al=Math.max(.05,(k-.68)*.85)*Math.min(1,Math.min(ba,bb)*1.5);if(hits.size&&!(hits.has(a)||hits.has(b)))al*=.3;if(lit&&!(lit.has(a)&&lit.has(b)))al*=.3;
    const g=Math.min(ba,bb);if(g<=0)continue;const C=ctl(a,b);const from=ba<bb?b:a,to=from===a?b:a;cx.strokeStyle=`rgba(236,226,216,${al})`;cx.beginPath();
    if(g<1){const A=S[from],B=S[to],Cc=from===a?C:C;qseg(A,Cc,B,0,1-Math.pow(1-g,2));}else{cx.moveTo(S[a][0],S[a][1]);cx.quadraticCurveTo(C[0],C[1],S[b][0],S[b][1]);}cx.stroke();}
  cx.globalCompositeOperation='lighter';
  if(pathList){cx.lineWidth=2.4;for(let k=1;k<pathList.length;k++){const A=S[pathList[k-1]],B=S[pathList[k]];const g=cx.createLinearGradient(A[0],A[1],B[0],B[1]);g.addColorStop(0,TY[N[pathList[k-1]].type][1]);g.addColorStop(1,TY[N[pathList[k]].type][1]);cx.strokeStyle=g;cx.globalAlpha=.85;const C=ctl(pathList[k-1],pathList[k]);cx.beginPath();cx.moveTo(A[0],A[1]);cx.quadraticCurveTo(C[0],C[1],B[0],B[1]);cx.stroke();}cx.globalAlpha=1;}
  else if(burst>.01){const targets=lit?[...lit]:N.map((_,i)=>i);cx.lineWidth=lit?1:.7;const rgb=sel>0?rgbOf(TY[N[sel].type][1]==='#ffffff'||TY[N[sel].type][1]==='#f5f0ea'?'#ff7a1a':TY[N[sel].type][1]):'255,118,30';
    for(const j of targets){if(j===src||!vis(j))continue;const al=burst*(lit?.55:.26)*Math.min(1,S[j][2]*.95);cx.strokeStyle=`rgba(${rgb},${al})`;cx.beginPath();cx.moveTo(S[src][0],S[src][1]);cx.lineTo(S[j][0],S[j][1]);cx.stroke();}}
  for(let pi=pulses.length-1;pi>=0;pi--){const p=pulses[pi];if(pulses.length>cap*1.6&&p.a!==0){pulses.splice(pi,1);continue;}p.t+=dt*p.v;
    if(p.t>=1){p.life--;if(p.life<=0||!adj[p.b].length||!vis(p.b)){if(pulses.length>cap){pulses.splice(pi,1);continue;}Object.assign(p,newPulse());continue;}p.t=0;p.a=p.b;p.c=N[p.a].type;const n=adj[p.a];p.b=n[Math.floor(rnd()*n.length)];}
    if(!vis(p.a)||!vis(p.b))continue;const A=S[p.a],B=S[p.b],C=ctl(p.a,p.b);const[x,y]=qpt(A,C,B,p.t),k=(A[2]+B[2])/2;
    const t0=Math.max(0,p.t-.45),[tx,ty]=qpt(A,C,B,t0);const gr=cx.createLinearGradient(tx,ty,x,y);gr.addColorStop(0,`rgba(${RGB[p.c]},0)`);gr.addColorStop(1,`rgba(${RGB[p.c]},${.85*k})`);
    cx.strokeStyle=gr;cx.lineWidth=1.6*k;cx.beginPath();qseg(A,C,B,t0,p.t);cx.stroke();const r=10*k;cx.globalAlpha=.95;cx.drawImage(PH[p.c],x-r,y-r,r*2,r*2);cx.globalAlpha=1;}
  cx.globalCompositeOperation='source-over';
  const ord=N.map((_,i)=>i).filter(vis).sort((a,b)=>S[b][3]-S[a][3]);
  const lab=[];
  for(const i of ord){const[nm,col,r0]=TY[N[i].type];const[x,y,k]=S[i];const far=Math.max(0,1-k);const bt=born.has(i)?Math.max(0,Math.min(1,(now-born.get(i))/1600)):1;const ez=1-Math.pow(1-bt,3);if(bt<=0)continue;let r=r0*k*(1+far*1.3)*Math.sqrt(zoom)*3*(.2+.8*ez);let al=Math.min(1,.3+(k-.7)*1.7)*Math.max(.05,ez);if(bt<1){const h=r*(1+2*(1-ez));cx.globalCompositeOperation='lighter';cx.globalAlpha=(1-ez)*.7;cx.drawImage(SO,x-h,y-h,h*2,h*2);cx.globalCompositeOperation='source-over';}
    if(lit&&!lit.has(i))al*=.2;if(hits.size&&!hits.has(i))al*=.2;if(hits.has(i)||i===sel||i===hov||i===pathFrom||(pathSet&&pathSet.has(i))){al=1;r*=1.5;}
    const ty=N[i].type,glow=ty==='publicado'||ty==='pendiente'||ty==='programado';
    cx.globalAlpha=Math.max(.05,al);cx.globalCompositeOperation=glow?'lighter':'source-over';cx.drawImage(SP[ty],x-r,y-r,r*2,r*2);
    if(ty==='zona'){cx.globalCompositeOperation='lighter';cx.globalAlpha=Math.max(.05,al)*.6;const z=r*1.9;cx.drawImage(SO,x-z,y-z,z*2,z*2);}
    if(i===0){cx.globalCompositeOperation='lighter';const Rr=r*(2.4+Math.sin(now/500)*.3+flash*3);cx.globalAlpha=.55+flash*.4;cx.drawImage(SH,x-Rr,y-Rr,Rr*2,Rr*2);}
    if(i===sel){cx.globalCompositeOperation='source-over';cx.globalAlpha=.9;cx.strokeStyle=col==='#ffffff'?'#ff7a1a':col;cx.lineWidth=1.5;cx.beginPath();cx.arc(x,y,r*.75+4+Math.sin(now/250)*2,0,7);cx.stroke();}
    cx.globalCompositeOperation='source-over';
    const show=i===sel||i===hov||hits.has(i)||i===pathFrom||(pathSet&&pathSet.has(i))||ty==='zona'||i===0||(labels&&ty!=='guion'&&ty!=='dato'&&k>.98&&(!lit||lit.has(i)));
    if(show)lab.push([i,x,y,r,al,ty==='zona'||i===0]);}
  cx.textAlign='center';const boxes=[];
  for(const[i,x,y,r,al,big]of lab.sort((a,b)=>(b[0]===sel)-(a[0]===sel)||b[5]-a[5])){let t=N[i].label;if(t.length>38)t=t.slice(0,36)+'…';cx.font=big?'800 11px Montserrat':'500 12px Inter';
    const w=cx.measureText(t).width,yy=y-r/2-9;if(boxes.some(([bx,by,bw])=>Math.abs(bx-x)<(bw+w)/2+4&&Math.abs(by-yy)<14))continue;boxes.push([x,yy,w]);
    cx.globalAlpha=big?.75:Math.max(.85,al);cx.fillStyle=big?'#ffd2b0':'#f5f0ea';cx.fillText(big?t.toUpperCase():t,x,yy);}
  cx.globalAlpha=1;requestAnimationFrame(frame);}
