from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
SRC="/mnt/user-data/uploads/Desktop/EKORUEDAS_ESTUDIO_3D/disenos/frames/"
FONT="/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf"
def F(sz,w="ExtraBold"):
    f=ImageFont.truetype(FONT,sz)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
W,H=540,960
def texto_borde(d,xy,t,f,fill=(255,255,255),stroke=(0,0,0),sw=6,anchor="mm"):
    d.text(xy,t,font=f,fill=fill,stroke_width=sw,stroke_fill=stroke,anchor=anchor,align="center")
def pastilla(d,cx,cy,t,f,bg=(255,214,0),fg=(10,10,10),pad=18):
    b=d.textbbox((cx,cy),t,font=f,anchor="mm")
    d.rounded_rectangle((b[0]-pad,b[1]-pad*0.6,b[2]+pad,b[3]+pad*0.6),radius=14,fill=bg)
    d.text((cx,cy),t,font=f,fill=fg,anchor="mm",align="center")
def fr(n): return Image.open(SRC+f"f_{n:04d}.png").convert("RGB").resize((W,H),Image.LANCZOS)
paneles=[]
# 1 revelación macro
im=fr(1); d=ImageDraw.Draw(im)
texto_borde(d,(W/2,190),"ESTA RAYITA\nTE PUEDE\nMULTAR",F(52),sw=7)
d.ellipse((215,560,325,670),outline=(255,40,40),width=7)
pastilla(d,W/2,850,"1,6 mm",F(46))
paneles.append((im,"1. Revelación 3D en macro","La pieza en 3D se transforma"))
# 2 sketch
im=fr(2); d=ImageDraw.Draw(im)
texto_borde(d,(W/2,150),"CLOD NO SABÍA\nESTO DE LAS RUEDAS",F(46),sw=7)
pastilla(d,W/2,860,"¿Y tú lo sabías?",F(38),bg=(255,255,255))
paneles.append((im,"2. Sketch de Alex y Clod","Clod se equivoca, Alex explica"))
# 3 reto
im=fr(3); d=ImageDraw.Draw(im)
texto_borde(d,(W/2,140),"¿CUÁL PASA\nLA ITV?",F(60),sw=8)
pastilla(d,105,800,"A",F(64),bg=(255,214,0)); pastilla(d,435,800,"B",F(64),bg=(255,214,0))
texto_borde(d,(W/2,905),"Responde en comentarios",F(30),sw=5)
paneles.append((im,"3. Reto: ¿cuál pasa la ITV?","El público adivina y comenta"))
# 4 POV
im=fr(4); d=ImageDraw.Draw(im)
texto_borde(d,(W/2,150),"POV: ERES UNA\nRUEDA LISA",F(54),sw=7)
texto_borde(d,(W/2,880),"y el mecánico te mira así",F(32),sw=5)
paneles.append((im,"4. POV: eres una rueda lisa","Cámara desde la rueda"))
# 5 antes/después (5 arriba, 9 abajo)
a=fr(5).crop((0,H//4,W,H//4+H//2)); b=fr(9).crop((0,H//4,W,H//4+H//2))
im=Image.new("RGB",(W,H)); im.paste(a,(0,0)); im.paste(b,(0,H//2)); d=ImageDraw.Draw(im)
d.rectangle((0,H//2-4,W,H//2+4),fill=(255,255,255))
pastilla(d,W/2,60,"NUEVO · 8 mm",F(40),bg=(40,200,90),fg=(255,255,255))
pastilla(d,W/2,H//2+60,"GASTADO · 1,6 mm",F(40),bg=(230,40,40),fg=(255,255,255))
paneles.append((im,"5. Antes y después","Pantalla partida: nuevo contra gastado"))
# 6 noticias
im=fr(6); d=ImageDraw.Draw(im)
d.rectangle((0,760,W,860),fill=(200,20,20)); d.rectangle((0,860,W,915),fill=(15,15,20))
d.text((24,810),"ÚLTIMA HORA",font=F(44),fill=(255,255,255),anchor="lm")
d.text((24,888),"Multa de 200 € por rueda lisa",font=F(26,"Bold"),fill=(255,255,255),anchor="lm")
paneles.append((im,"6. Clod presenta las noticias","Formato telediario con rótulos"))
# 7 top 3
im=fr(7); d=ImageDraw.Draw(im)
texto_borde(d,(110,230),"3",F(200,"Black"),fill=(255,214,0),sw=10)
texto_borde(d,(W/2,120),"SEÑALES DE QUE\nTOCA CAMBIAR",F(40),sw=6)
pastilla(d,W/2,880,"Dibujo a 1,6 mm",F(38))
paneles.append((im,"7. Top 3 con número grande","Lista rápida, un dato por golpe"))
# 8 cinemático
im=fr(8).filter(ImageFilter.GaussianBlur(0.4)); d=ImageDraw.Draw(im)
d.rectangle((0,0,W,70),fill=(0,0,0)); d.rectangle((0,H-70,W,H),fill=(0,0,0))
texto_borde(d,(W/2,800),"Cada milímetro cuenta.",F(36,"SemiBold"),sw=0)
paneles.append((im,"8. Cinemático sin palabras","Luz dramática y música, sin voz"))
# hoja
PW,PH=360,640; gap=26; cols=4; top=150; cap=110
SW=cols*PW+(cols+1)*gap; SH=top+2*(PH+cap)+3*gap
hoja=Image.new("RGB",(SW,SH),(18,19,22)); d=ImageDraw.Draw(hoja)
d.text((gap,52),"8 diseños de vídeo · testigo de desgaste 1,6 mm",font=F(46),fill=(255,255,255),anchor="lm")
d.text((gap,108),"Taller 3D nuevo + Alex + Clod · fotogramas reales de Blender · 26-11-2026",font=F(26,"Medium"),fill=(170,175,185),anchor="lm")
for i,(im,t,s) in enumerate(paneles):
    c,r=i%cols,i//cols; x=gap+c*(PW+gap); y=top+r*(PH+cap+gap)
    hoja.paste(im.resize((PW,PH),Image.LANCZOS),(x,y))
    col=(60,210,110) if i==0 else (70,72,78)
    d.rectangle((x-4,y-4,x+PW+3,y+PH+3),outline=col,width=5 if i==0 else 2)
    d.text((x,y+PH+30),t,font=F(25),fill=(255,255,255),anchor="lm")
    d.text((x,y+PH+66),s,font=F(18,"Medium"),fill=(170,175,185),anchor="lm")
    if i==0: pastilla(d,x+PW-95,y+28,"RECOMENDADO",F(20),bg=(60,210,110),fg=(0,0,0),pad=10)
hoja.save("disenos_8_hoja.png")
for i,(im,t,s) in enumerate(paneles): im.save(f"diseno_{i+1}.png")
print(hoja.size)
