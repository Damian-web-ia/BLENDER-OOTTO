# MEZCLA DE SONIDO DEL DESPIECE DEL EMBRAGUE (se ejecuta en el espacio de trabajo de Ootto: python3 mezcla_embrague.py)
# Voz de Alex frase a frase en su momento, música suave con ducking bajo la voz, efectos sintetizados en cada evento
# (golpecitos de Clod, pitido, rayos X, golpe al salir, clacs de las capas, zumbido del giro, clic del collarín, aire al soltar,
# roce del patinazo, siseo del quemado, boing de Clod pillado) y máster a -14 LUFS.
# Uso: python3 mezcla_embrague.py <voces.json> <anclas.json> <carpeta_voces (clip_x.wav)> <musica.mp3> <salida.ogg>
import json, subprocess, sys, os
VOZ, ANC, CLIPS, MUS, OUT = sys.argv[1:6]
vz = json.load(open(VOZ, encoding="utf-8")); ev = json.load(open(ANC))["eventos"]; FIN = json.load(open(ANC))["fin"]
def T(f): return (f - 1) / 30.0
def FW(i, j): l = vz["lineas"][i]; return 1 + round((l["at"] + l["words"][j][1]) * 30)
DUR = T(FIN) + 0.4
TMP = "/tmp/sfx_emb"; os.makedirs(TMP, exist_ok=True)
def sfx(nombre, expr):
    p = f"{TMP}/{nombre}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", expr, "-ac", "2", "-ar", "48000", p], check=True)
    return p
S = {
 "tic": sfx("tic", "anoisesrc=d=0.05:c=brown:a=0.9,lowpass=f=900,afade=t=out:st=0.01:d=0.04"),
 "pitido": sfx("pitido", "sine=f=1480:d=0.14,volume=0.35,afade=t=out:st=0.09:d=0.05"),
 "rayos": sfx("rayos", "aevalsrc='0.25*sin(2*PI*(300+900*t)*t)':d=0.7,afade=t=in:d=0.1,afade=t=out:st=0.45:d=0.25"),
 "golpe": sfx("golpe", "aevalsrc='0.9*sin(2*PI*55*t)*exp(-7*t)+0.25*(random(0)-0.5)*exp(-18*t)':d=0.6"),
 "clac": sfx("clac", "aevalsrc='0.5*sin(2*PI*2600*t)*exp(-38*t)+0.4*sin(2*PI*1350*t)*exp(-30*t)+0.3*(random(0)-0.5)*exp(-60*t)':d=0.25"),
 "zumbido": sfx("zumbido", "aevalsrc='0.22*sin(2*PI*92*t)+0.12*sin(2*PI*184*t)+0.05*sin(2*PI*368*t)':d=8"),
 "clic": sfx("clic", "aevalsrc='0.6*sin(2*PI*1900*t)*exp(-70*t)+0.3*(random(0)-0.5)*exp(-90*t)':d=0.12"),
 "aire": sfx("aire", "anoisesrc=d=0.5:c=pink:a=0.35,highpass=f=1500,afade=t=in:d=0.08,afade=t=out:st=0.2:d=0.3"),
 "roce": sfx("roce", "anoisesrc=d=1.2:c=white:a=0.25,bandpass=f=2300:w=900,tremolo=f=11:d=0.6,afade=t=in:d=0.1,afade=t=out:st=0.8:d=0.4"),
 "siseo": sfx("siseo", "anoisesrc=d=0.8:c=white:a=0.22,highpass=f=3000,afade=t=in:d=0.15,afade=t=out:st=0.4:d=0.4"),
 "boing": sfx("boing", "aevalsrc='0.45*sin(2*PI*(260+500*t+60*sin(2*PI*14*t))*t)*exp(-3.5*t)':d=0.55"),
 "salto": sfx("salto", "aevalsrc='0.35*sin(2*PI*(400+700*t)*t)*exp(-5*t)':d=0.35"),
}
E = []                                        # (segundo, efecto, volumen)
f = 1
while f + 8 <= FW(0, 8) - 4:                  # golpecitos de Clod (se oyen bajos también en el plano de Alex)
    E.append((T(f + 4), "tic", 0.5 if f < FW(0, 4) else 0.9)); f += 8
E.append((T(FW(0, 8)), "pitido", 0.9))
E.append((T(ev["XR0"]), "rayos", 0.8)); E.append((T(ev["EST"]), "golpe", 1.0))
for d in (6, 9, 12): E.append((T(ev["F_DIS"] + d), "clac", 0.7))
E.append((T(ev["F_APR"] + 8), "clac", 0.9))
E.append((T(ev["F_EMP"] + 5), "clic", 0.9)); E.append((T(ev["F_SEP"] + 2), "aire", 0.8))
E.append((T(ev["F_PAT"]), "roce", 0.8)); E.append((T(FW(3, 8)), "siseo", 0.7))
f = ev["A3"]
while f + 8 <= ev["F_VER"] - 2: E.append((T(f + 4), "tic", 0.45)); f += 8
E.append((T(FW(4, 10)), "boing", 0.9)); E.append((T(FW(4, 10)) + 0.05, "pitido", 0.6))
E.append((T(ev["CTA"] + 8), "salto", 0.7))
# entradas: música, voces, efectos, zumbido (giro de F_GIRO a A2)
ins = ["-stream_loop", "-1", "-i", MUS]; filt = []; n = 1; voz_lbl = []
for k, l in enumerate(vz["lineas"]):
    ins += ["-i", os.path.join(CLIPS, l["clip"] + ".wav")]
    ms = int(l["at"] * 1000); filt.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms},volume=1.0[v{k}]"); voz_lbl.append(f"[v{k}]"); n += 1
sfx_lbl = []
for k, (t, nm, vol) in enumerate(E):
    ins += ["-i", S[nm]]; ms = int(t * 1000)
    filt.append(f"[{n}:a]adelay={ms}|{ms},volume={vol}[s{k}]"); sfx_lbl.append(f"[s{k}]"); n += 1
ins += ["-i", S["zumbido"]]
t0, t1 = T(ev["F_GIRO"]), T(ev["A2"]); ms = int(t0 * 1000)
filt.append(f"[{n}:a]atrim=0:{t1 - t0:.3f},afade=t=in:d=0.3,afade=t=out:st={max(0.0, t1 - t0 - 0.5):.3f}:d=0.5,adelay={ms}|{ms},volume=0.8[zz]"); sfx_lbl.append("[zz]"); n += 1
filt.append("".join(voz_lbl) + f"amix=inputs={len(voz_lbl)}:normalize=0[voz]")
filt.append("[voz]asplit=2[voz1][vozsc]")
filt.append(f"[0:a]atrim=0:{DUR:.2f},aresample=48000,aformat=channel_layouts=stereo,volume=0.18,afade=t=in:d=0.4,afade=t=out:st={DUR - 1.2:.2f}:d=1.2[mus]")
filt.append("[mus][vozsc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[musd]")
filt.append("".join(sfx_lbl) + f"amix=inputs={len(sfx_lbl)}:normalize=0,volume=0.8[fx]")
filt.append(f"[voz1][musd][fx]amix=inputs=3:normalize=0,atrim=0:{DUR:.2f},loudnorm=I=-14:TP=-1.0:LRA=11[out]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(filt), "-map", "[out]", "-ar", "48000", "-c:a", "libvorbis", "-q:a", "6", OUT], check=True)
print("mezcla", OUT, f"{DUR:.2f} s", len(E), "efectos")
