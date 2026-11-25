/* Cámara 3D (proyección), curvas de los hilos y creación de impulsos. */
/* proyección */
let mS=new Map();const cyc={};
function rot(){cyc.cy=Math.cos(mRotY);cyc.sy=Math.sin(mRotY);cyc.cx=Math.cos(mRotX);cyc.sx=Math.sin(mRotX);cyc.s=Math.min(mW*(mW<700?.2:.24),mH*.27)*mZoom;SK=Math.max(.62,Math.min(1.15,cyc.s/200));cyc.oy=mH*(mW<700?.5:.52);}
function pr(x,y,z){const X=x*cyc.cy-z*cyc.sy,Z=x*cyc.sy+z*cyc.cy;const y2=y*cyc.cx-Z*cyc.sx,z2=y*cyc.sx+Z*cyc.cx;const f=8/(8+z2*1.3);return[mW/2+X*cyc.s*f,cyc.oy+y2*cyc.s*f,f,z2];}
const proj=n=>pr(n.x,n.y,n.z);
function mCtl(A,B,ph){const dx=B[0]-A[0],dy=B[1]-A[1],L=Math.hypot(dx,dy)||1;const sw=Math.sin(T/1300+ph)*.55+Math.sin(T/2900+ph*1.7)*.45;const amp=L*(.12+.06*Math.sin(ph*3))*sw+L*.05*Math.cos(ph);return[(A[0]+B[0])/2-dy/L*amp,(A[1]+B[1])/2+dx/L*amp];}
function qp(A,Cc,B,t){const u=1-t;return[u*u*A[0]+2*u*t*Cc[0]+t*t*B[0],u*u*A[1]+2*u*t*Cc[1]+t*t*B[1]];}
/* impulsos */
const mPulses=[];
function spawn(k){k=k??Math.floor(Math.random()*4);const p=FASES[k],t=p.items[Math.floor(Math.random()*p.items.length)];const back=Math.random()<.35;mPulses.push({path:back?[t,p.hub,C]:[C,p.hub,t],seg:0,t:0,v:.5+Math.random()*.45,st:Math.floor(Math.random()*3)});}
