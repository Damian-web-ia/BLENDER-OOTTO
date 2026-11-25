/* Dibujo de cada fotograma: cielo, disco, órbita y cometa, hilos tipo pelo, impulsos, estrellas y nombres sin solaparse. */
/* bucle */
function draw(now){const dt=Math.min(.05,(now-mLast)/1000||0);mLast=now;
  if(!window.MAPON){requestAnimationFrame(draw);return;}
  T=now;
  if(mAim!=null){let d=((mAim-mRotY+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI;mRotY+=d*Math.min(1,dt*3);mRotX+=(.6-mRotX)*Math.min(1,dt*3);if(Math.abs(d)<.003)mAim=null;}
  else if(!mDrag&&!mSel)mRotY+=dt*.07;
  place();rot();
  g.setTransform(mDpr,0,0,mDpr,0,0);g.clearRect(0,0,mW,mH);
  /* cielo con paralaje */
  if(neb){const ox=((mRotY*60)%(mW*.4)+mW*.4)%(mW*.4),oy=(mRotX-.4)*40;g.globalAlpha=1;g.drawImage(neb,-ox-mW*.0,-mH*.2+oy,mW*1.4,mH*1.4);}
  g.globalCompositeOperation='lighter';
  for(const s of stars){const px=((s.x*mW-mRotY*(8+s.l*30))%mW+mW)%mW,py=((s.y*mH+(mRotX-.4)*(6+s.l*20))%mH+mH)%mH;const tw=.55+.45*Math.sin(now/1000*s.sp+s.tw);g.fillStyle=`rgba(${s.c},${(.25+s.l*.6)*tw})`;
    if(s.s>1.25){g.globalAlpha=.25*tw;g.drawImage(SC[BONE],px-s.s*3,py-s.s*3,s.s*6,s.s*6);g.globalAlpha=1;}g.fillRect(px-s.s/2,py-s.s/2,s.s,s.s);}
  mS=new Map();nodes.forEach(n=>mS.set(n,proj(n)));
  const dim=n=>focus<0?1:(n.ph===focus||n.kind==='core')?1:.15;
  /* disco galáctico */
  const tg=now/1000;for(const p of disk){const a=p.a+tg*.05/(p.r+.35);const P=pr(Math.cos(a)*p.r,p.y,Math.sin(a)*p.r);const al=p.b*(.3+.3*(P[2]-.75))*(focus<0?1:.45);if(al<=0)continue;
    const c=p.w>.4?`255,${190+p.w*40|0},${140+p.w*50|0}`:p.r>1.6?'170,184,210':'220,212,200';g.fillStyle=`rgba(${c},${al})`;const s=p.s*P[2]*1.25;g.fillRect(P[0]-s/2,P[1]-s/2,s,s);}
  /* anillo del ciclo y cometa */
  g.lineWidth=1;g.setLineDash([1,7]);g.strokeStyle=`rgba(239,231,221,${focus<0?.16:.07})`;g.beginPath();for(let i=0;i<=120;i++){const a=i/120*Math.PI*2+T/90000;const P=pr(Math.cos(a)*R0,0,Math.sin(a)*R0);i?g.lineTo(P[0],P[1]):g.moveTo(P[0],P[1]);}g.stroke();g.setLineDash([]);
  const ca=(now/9000)%1*Math.PI*2;for(let s=0;s<26;s++){const a=ca-s*.022;const P=pr(Math.cos(a)*R0,0,Math.sin(a)*R0);const r=(7-s*.24)*P[2]*SK;g.globalAlpha=(1-s/26)*.85;g.drawImage(SC[PULSE],P[0]-r,P[1]-r,r*2,r*2);}g.globalAlpha=1;
  /* hilos como pelo */
  for(const[a,b,nS]of links){const A=mS.get(a),B=mS.get(b);const k=dim(b);const z=(A[3]+B[3])/2;const base=Math.max(.08,(.7-z*.35)*.6)*k;
    for(let s=0;s<nS;s++){const ph=(b.b??b.a??0)*3+s*1.9+(b.ph||0);const Cc=mCtl(A,B,ph);g.strokeStyle=`rgba(236,226,216,${base*(s?.55:1)})`;g.lineWidth=(s?.6:1)*(a===C?1.1:.9);g.beginPath();g.moveTo(A[0],A[1]);g.quadraticCurveTo(Cc[0],Cc[1],B[0],B[1]);g.stroke();}}
  /* impulsos */
  if(Math.random()<dt*(mSel?1.5:4)&&mPulses.length<36)spawn();
  for(let i=mPulses.length-1;i>=0;i--){const p=mPulses[i];p.t+=dt*p.v*1.3;if(p.t>=1){p.t=0;p.seg++;if(p.seg>=p.path.length-1){mPulses.splice(i,1);continue;}}
    const a=p.path[p.seg],b=p.path[p.seg+1],A=mS.get(a),B=mS.get(b);const far=a===C||(b===C)?(b===C?a:b):(a.kind==='tool'?a:b);const ph=(far.b??far.a??0)*3+p.st*1.9+(far.ph||0);const Cc=mCtl(A,B,ph);
    const k=focus<0||(a.ph===focus||b.ph===focus)?1:.15;const t0=Math.max(0,p.t-.4),P=qp(A,Cc,B,p.t);
    g.strokeStyle=`rgba(255,150,70,${.5*k})`;g.lineWidth=1.4;g.beginPath();for(let s=0;s<=10;s++){const q=qp(A,Cc,B,t0+(p.t-t0)*s/10);s?g.lineTo(q[0],q[1]):g.moveTo(q[0],q[1]);}g.stroke();
    const r=9*Math.min(A[2],B[2])*SK;g.globalAlpha=k;g.drawImage(SC[PULSE],P[0]-r,P[1]-r,r*2,r*2);g.globalAlpha=1;}
  /* nodos */
  const LB=[];const order=[...nodes].sort((a,b)=>mS.get(b)[3]-mS.get(a)[3]);
  for(const n of order){const P=mS.get(n),f=P[2],k=dim(n);
    if(n.kind==='core'){const pul=1+.035*Math.sin(now/700);const r=78*f*pul*SK;
      g.globalAlpha=.32;g.drawImage(SC[OR],P[0]-r*3.2,P[1]-r*3.2,r*6.4,r*6.4);g.globalAlpha=.85;g.drawImage(SC[OR],P[0]-r*1.4,P[1]-r*1.4,r*2.8,r*2.8);
      g.globalAlpha=1;g.drawImage(SC[BONE],P[0]-r*.55,P[1]-r*.55,r*1.1,r*1.1);
      g.strokeStyle='rgba(255,180,130,.22)';g.lineWidth=1;g.beginPath();g.ellipse(P[0],P[1],r*1.25,r*1.25*Math.max(.2,Math.abs(Math.sin(mRotX))),0,0,7);g.stroke();
      g.globalCompositeOperation='source-over';LB.push(['Claude',P[0],P[1]+r*1.2+6*SK,f,1,22*SK,true,'#fff',9]);LB.push(['el director',P[0],P[1]+r*1.2+26*SK,f,.85,Math.max(11,12*SK),false,'#e9c7b2',9]);g.globalCompositeOperation='lighter';continue;}
    if(n.kind==='hub'){const r=24*f*SK*(mSel===n?1.3:1);g.globalAlpha=k*.6;g.drawImage(SC[n.col],P[0]-r*2.6,P[1]-r*2.6,r*5.2,r*5.2);g.globalAlpha=k;g.drawImage(SC[n.col],P[0]-r,P[1]-r,r*2,r*2);
      /* órbita de sus herramientas */
      g.strokeStyle=`rgba(${rgb(n.col)},${.18*k})`;g.lineWidth=.8;g.beginPath();for(let i=0;i<=48;i++){const b=i/48*Math.PI*2;const Q=pr(n.x+Math.cos(b)*.51,Math.sin(b)*.51*.3,n.z+Math.sin(b)*.51);i?g.lineTo(Q[0],Q[1]):g.moveTo(Q[0],Q[1]);}g.stroke();
      g.globalCompositeOperation='source-over';g.globalAlpha=k;g.fillStyle='rgba(12,10,9,.75)';g.beginPath();g.arc(P[0],P[1]-r*1.55,9*SK+2,0,7);g.fill();g.strokeStyle=n.col;g.lineWidth=1;g.stroke();
      g.fillStyle=n.col;g.font=`700 ${Math.round(11*SK+2)}px Montserrat`;g.textAlign='center';g.textBaseline='middle';g.fillText(n.num,P[0],P[1]-r*1.55+1);
      LB.push([n.name.toUpperCase(),P[0],P[1]+r+14,f,k,Math.max(11.5,13.5*SK),true,n.col,7]);g.globalCompositeOperation='lighter';g.globalAlpha=1;continue;}
    const r=12*f*SK*(mSel===n?1.5:1);const tw=.85+.15*Math.sin(now/600+n.b*5);g.globalAlpha=k*tw;g.drawImage(SC[n.col],P[0]-r*1.6,P[1]-r*1.6,r*3.2,r*3.2);g.globalAlpha=k;g.drawImage(SC[BONE],P[0]-r*.45,P[1]-r*.45,r*.9,r*.9);
    const al=k*(mW<700&&focus<0&&mSel!==n?0:Math.max(.3,Math.min(1,(f-.72)*2.4)));g.globalCompositeOperation='source-over';
    LB.push([n.name,P[0],P[1]-r-10,f,al,Math.max(11,12.5*SK),false,'#efe7dd',(mSel===n?8:4)]);if(n.via&&(mSel===n||focus===n.ph))LB.push([n.via,P[0],P[1]+r+11,f,al*.8,10.5,false,'#a39a90',3]);
    g.globalCompositeOperation='lighter';g.globalAlpha=1;}
  g.globalCompositeOperation='source-over';
  LB.sort((a,b)=>(b[8]+b[3])-(a[8]+a[3]));const used=[];
  for(const l of LB){const[txt,x,y,f,al,mSize,bold]=l;if(al<=.02)continue;g.font=`${bold?'700':'500'} ${Math.round(mSize*Math.max(.85,Math.min(1.12,f)))}px ${bold?'Montserrat':'Inter'},sans-serif`;
    const w=g.measureText(txt).width/2+4,h=mSize*.65;const bx=[x-w,y-h,x+w,y+h];if(l[8]<9&&used.some(u=>bx[0]<u[2]&&bx[2]>u[0]&&bx[1]<u[3]&&bx[3]>u[1]))continue;used.push(bx);label(...l.slice(0,8));}
  requestAnimationFrame(draw);}
mSize();requestAnimationFrame(draw);
