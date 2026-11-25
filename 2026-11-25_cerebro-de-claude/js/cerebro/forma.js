/* Forma del cerebro: convierte los recuerdos en neuronas, calcula la forma (hemisferios, lóbulos, cerebelo), coloca cada neurona en su zona y une cada una con sus 6 vecinas. */
const N=R.map(([id,label,type,d,desc])=>{const[m,dd]=d.split('-').map(Number);return{id,label,type,desc,day:Math.round((new Date(2026,m-1,dd)-D0)/864e5),date:d};});
const idx={};N.forEach((n,i)=>idx[n.id]=i);
const SL=[];R.forEach(([id,,,,,ls])=>ls.forEach(l=>{if(idx[l]!=null)SL.push([idx[id],idx[l]]);}));
const nb=N.map(()=>new Set());SL.forEach(([a,b])=>{nb[a].add(b);nb[b].add(a);});
let seed=17;const rnd=()=>((seed=seed*16807%2147483647)/2147483647);
const parts=[[-.34,.16,.02,.4,.58,.92],[.34,.16,.02,.4,.58,.92],[-.42,-.2,.22,.26,.26,.5],[.42,-.2,.22,.26,.26,.5],[0,-.4,-.62,.5,.22,.3]];
function fn(x,y,z){let d=9;for(const[a,b,c,rx,ry,rz]of parts){const v=Math.hypot((x-a)/rx,(y-b)/ry,(z-c)/rz);if(v<d)d=v;}
  if(Math.abs(x)<.035&&y>-.05)d=Math.max(d,1.01);
  const st=Math.hypot(x/.11,(z+.28)/.13);if(y<-.35&&y>-.95&&st<1)d=Math.min(d,st);
  if(y<-.12&&Math.abs(z+.66)>.32)d*=1+(-.12-y)*1.6;
  return d*(1+.07*Math.sin(13*x+2*y)*Math.sin(11*y)*Math.sin(9*z+1));}
const EXTRA=120;const pts=[];while(pts.length<N.length-1){const x=rnd()*2-1,y=rnd()*2-1,z=rnd()*2-1,d=fn(x,y,z);if(d<1&&(d>.78||rnd()<.07))pts.push([x,y,z]);}
const anchor={z_marca:[-.3,.25,.75],z_videos:[.1,.6,.2],z_herr:[-.35,.4,-.55],z_jesko:[.5,-.05,.0],z_pend:[0,-.42,-.62]};
const zoneOf=N.map(()=>null);
Object.keys(anchor).forEach(z=>{const q=[idx[z]];zoneOf[idx[z]]=z;while(q.length){const u=q.shift();nb[u].forEach(v=>{if(v!==0&&zoneOf[v]==null&&N[v].type!=='zona'){zoneOf[v]=z;q.push(v);}});}});
const P=N.map(()=>null);P[0]=[0,.1,0];const free=new Set(pts.map((_,i)=>i));
N.map((_,i)=>i).filter(i=>i).sort((a,b)=>(N[a].type==='zona'?-1:0)-(N[b].type==='zona'?-1:0)||nb[b].size-nb[a].size).forEach(i=>{
  const an=anchor[zoneOf[i]]||[0,.2,.2];let best=-1,bd=1e9;
  free.forEach(j=>{const p=pts[j];const d=(p[0]-an[0])**2+(p[1]-an[1])**2+(p[2]-an[2])**2+(N[i].type==='zona'?0:rnd()*.05);if(d<bd){bd=d;best=j;}});free.delete(best);P[i]=pts[best];});
{const base=pts.length;let s2=99;const r2=()=>((s2=s2*16807%2147483647)/2147483647);while(pts.length<base+EXTRA){const x=r2()*2-1,y=r2()*2-1,z=r2()*2-1,d=fn(x,y,z);if(d<1&&d>.7){pts.push([x,y,z]);free.add(pts.length-1);}}}
const store={get(k,d){try{const v=localStorage.getItem('cerebro.'+k);return v==null?d:JSON.parse(v);}catch(e){return d;}},set(k,v){try{localStorage.setItem('cerebro.'+k,JSON.stringify(v));}catch(e){}}};
const off={};Object.keys(TY).forEach(k=>off[k]=true);const saved=store.get('off',{});Object.keys(saved).forEach(k=>{if(k in off&&k!=='hub'&&k!=='zona')off[k]=saved[k];});
let maxDay=TODAY;const born=new Map();
const vis=i=>N[i].day<=maxDay&&off[N[i].type];
let ML=[],adj=N.map(()=>[]);
function rebuild(){ML=[];adj=N.map(()=>[]);const ms=new Set();const V=N.map((_,i)=>i).filter(vis);
  for(const i of V){const ds=[];for(const j of V)if(j!==i)ds.push([(P[i][0]-P[j][0])**2+(P[i][1]-P[j][1])**2+(P[i][2]-P[j][2])**2,j]);ds.sort((a,b)=>a[0]-b[0]);
    for(let k=0;k<Math.min(6,ds.length);k++){const j=ds[k][1],key=i<j?i+'_'+j:j+'_'+i;if(!ms.has(key)){ms.add(key);ML.push([i,j]);adj[i].push(j);adj[j].push(i);}}}}
