/* Recuerdos automáticos: lee los recuerdos que Claude guarda cada noche en la base de datos (solo dentro de Claude). */
/* ---------- recuerdos guardados ---------- */
let db=null,dbIds=new Set();
const today=()=>{const d=new Date();return String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
function addMem(id,m){if(idx[id]!=null||!m||!TY[m.type]||m.type==='hub'||m.type==='zona')return;const d=/^\d\d-\d\d$/.test(m.date||'')?m.date:today();const[mm,dd]=d.split('-').map(Number);
  const n={id,label:String(m.label||'Recuerdo').slice(0,80),type:m.type,desc:String(m.desc||'').slice(0,400),day:Math.max(0,Math.round((new Date(2026,mm-1,dd)-D0)/864e5)),date:d,user:true};
  const i=N.length;N.push(n);idx[id]=i;nb.push(new Set());const r=idx[m.rel];if(r!=null){nb[i].add(r);nb[r].add(i);SL.push([i,r]);}
  const an=r!=null?P[r]:[0,.2,.2];let best=-1,bd=1e9;free.forEach(j=>{const p=pts[j];const dd2=(p[0]-an[0])**2+(p[1]-an[1])**2+(p[2]-an[2])**2;if(dd2<bd){bd=dd2;best=j;}});
  if(best<0){P.push([an[0]+(Math.random()-.5)*.1,an[1]+(Math.random()-.5)*.1,an[2]+(Math.random()-.5)*.1]);}else{free.delete(best);P.push(pts[best]);}
  return i;}
use('db').then(x=>{db=x;if(!x)return;const timer=setTimeout(()=>{},10000);
  x.collection('recuerdos').onSnapshot(snap=>{clearTimeout(timer);let added=0;snap.docs.forEach(d=>{if(!d.exists||dbIds.has(d.id))return;dbIds.add(d.id);if(addMem(d.id,d.data())!=null)added++;});if(added){stats();if(!snap.metadata.fromCache)toast('+'+added+' recuerdos nuevos');}},()=>clearTimeout(timer));}).catch(()=>{});
