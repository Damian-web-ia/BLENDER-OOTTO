/* Datos del mapa: las 4 fases, sus colores y sus herramientas. Aquí se cambian textos y colores del mapa. */
const FASES=[
 {n:1,name:'Ideas',sub:'Qué vídeo hacemos hoy',col:'#a9a4c4',tools:[
   ['ChatGPT','Cada día entrevista a Claude con 30-40 preguntas y escribe el prompt del vídeo y la skill maestra (Blender, portada, voces, todo). También propone ideas.','vía Zapier'],
   ['vidIQ','Tendencias, vídeos virales de motor y sonidos de moda: con esto Claude responde a ChatGPT.',''],
   ['Búsqueda web','Lo que pega ahora en España: series, juegos, memes y fechas de temporada.','']]},
 {n:2,name:'Producción',sub:'Cómo se fabrica el vídeo',col:'#8fb3a0',tools:[
   ['Ootto','Monta el reel: voces de Alex (Carlos) y Clod (Diego), música, efectos y subtítulos.',''],
   ['Blender','Anima el reel 3D y la portada cada día a las 19:30, en tu PC.','en tu PC'],
   ['GitHub','Lleva los vídeos del PC a Ootto y guarda los prompts, la skill maestra y las lecciones de cada día.',''],
   ['Canva','Miniaturas para YouTube.','']]},
 {n:3,name:'Publicación',sub:'Sale a las 19:00, siempre en público',col:'#8ea6c4',tools:[
   ['Instagram','Reel diario a las 19:00, en público.','vía Ootto'],
   ['YouTube Shorts','Reel diario a las 19:00, en público.','vía Ootto'],
   ['TikTok','Reel diario a las 19:00, en público, con comentarios.','vía vidIQ']]},
 {n:4,name:'Memoria y datos',sub:'Qué aprendemos para mañana',col:'#cfae68',tools:[
   ['Cerebro de Claude','Los recuerdos que se añaden solos cada noche (la otra pestaña).',''],
   ['Windsor.ai','Estadísticas de Instagram, TikTok y YouTube.',''],
   ['Notion','Banco de ideas.',''],
   ['Drive y Docs','Guiones y documentos del proyecto.','']]}];
const mCv=document.getElementById('m'),g=mCv.getContext('2d');
let mW=0,mH=0,mDpr=1,mRotY=.5,mRotX=.62,mZoom=1,mDrag=null,focus=-1,mSel=null,mAim=null,mLast=0,T=0,SK=1,neb=null,stars=[];
const rgb=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)).join(',');
let mSeed=7;const mRnd=()=>((mSeed=mSeed*16807%2147483647)/2147483647);
function gauss(){return(mRnd()+mRnd()+mRnd()-1.5)/1.5;}
function spr(col,core){const c=document.createElement('canvas');c.width=c.height=128;const x=c.getContext('2d');const gr=x.createRadialGradient(64,64,0,64,64,64);const k=rgb(col);
  gr.addColorStop(0,'rgba(255,255,255,1)');gr.addColorStop(core,`rgba(${k},.95)`);gr.addColorStop(core+.14,`rgba(${k},.32)`);gr.addColorStop(1,`rgba(${k},0)`);x.fillStyle=gr;x.fillRect(0,0,128,128);return c;}
const OR='#ff8a2a',BONE='#efe7dd',PULSE='#ff9646';const SC={};[OR,BONE,PULSE,...FASES.map(p=>p.col)].forEach(c=>SC[c]=spr(c,.16));
