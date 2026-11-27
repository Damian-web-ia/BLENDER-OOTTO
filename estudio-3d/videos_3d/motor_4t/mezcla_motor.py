# MEZCLA DE SONIDO · EL MOTOR POR DENTRO (se ejecuta en el espacio de trabajo de Ootto: python3 mezcla_motor.py ...)
# Voz de Maite (Renata) frase a frase, música electrónica suave con ducking, efectos en cada momento del ciclo:
# apertura del motor, clics de válvulas, aire entrando, chispa, explosión, gases saliendo, despiece y montaje,
# motor que acelera y decelera, el susto de Clod y el cierre. Máster a -14 LUFS.
# Uso: python3 mezcla_motor.py <voces.json> <anclas.json> <carpeta_voces> <musica.mp3> <carpeta_sfx> <salida.ogg>
import json, subprocess, sys, os
VOZ, ANC, CLIPS, MUS, SFXD, OUT = sys.argv[1:7]
vz = json.load(open(VOZ, encoding="utf-8")); A = json.load(open(ANC)); ev = A["eventos"]; FIN = A["fin"]
def T(f): return (f - 1) / 30.0
DUR = T(FIN) + 0.4
TMP = "/tmp/sfx_motor"; os.makedirs(TMP, exist_ok=True)
def sfx(nombre, expr):
    p = f"{TMP}/{nombre}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", expr, "-ac", "2", "-ar", "48000", p], check=True)
    return p
def lib(nombre):
    p = os.path.join(SFXD, nombre); q = f"{TMP}/lib_{nombre}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p, "-ac", "2", "-ar", "48000", q], check=True); return q
S = {
 "clic": sfx("clic", "aevalsrc='0.55*sin(2*PI*2100*t)*exp(-80*t)+0.35*sin(2*PI*900*t)*exp(-50*t)+0.25*(random(0)-0.5)*exp(-90*t)':d=0.14"),
 "aire": sfx("aire", "anoisesrc=d=2.4:c=pink:a=0.33,bandpass=f=900:w=700,afade=t=in:d=0.3,afade=t=out:st=1.7:d=0.7"),
 "sube": sfx("sube", "aevalsrc='0.16*sin(2*PI*(110+160*t)*t)+0.05*(random(0)-0.5)':d=1.9,lowpass=f=1800,afade=t=in:d=0.3,afade=t=out:st=1.6:d=0.3"),
 "chispa": sfx("chispa", "anoisesrc=d=0.12:c=white:a=0.8,highpass=f=2500,tremolo=f=90:d=0.9,afade=t=out:st=0.05:d=0.07"),
 "explosion": sfx("explosion", "aevalsrc='0.95*sin(2*PI*48*t)*exp(-4.5*t)+0.6*(random(0)-0.5)*exp(-6*t)+0.3*sin(2*PI*96*t)*exp(-8*t)':d=1.6,lowpass=f=2600"),
 "escape": sfx("escape", "anoisesrc=d=2.0:c=brown:a=0.45,lowpass=f=1100,tremolo=f=7:d=0.4,afade=t=in:d=0.2,afade=t=out:st=1.3:d=0.7"),
 "clac": sfx("clac", "aevalsrc='0.5*sin(2*PI*2600*t)*exp(-38*t)+0.4*sin(2*PI*1350*t)*exp(-30*t)+0.3*(random(0)-0.5)*exp(-60*t)':d=0.25"),
 "acelera": sfx("acelera", "aevalsrc='0.30*sin(2*PI*(24*t+16*t*t))+0.16*sin(2*PI*(48*t+32*t*t))+0.08*sin(2*PI*(96*t+64*t*t))+0.06*(random(0)-0.5)':d=4.2,lowpass=f=3000,afade=t=in:d=0.4"),
 "decelera": sfx("decelera", "aevalsrc='0.30*sin(2*PI*(158*t-30*t*t))+0.16*sin(2*PI*(316*t-60*t*t))+0.06*(random(0)-0.5)':d=2.2,lowpass=f=3000,afade=t=out:st=1.2:d=1.0"),
 "ralenti": sfx("ralenti", "aevalsrc='0.18*sin(2*PI*26*t)*(0.6+0.4*sin(2*PI*6.5*t))+0.08*sin(2*PI*52*t)':d=7,lowpass=f=600"),
 "boing": sfx("boing", "aevalsrc='0.45*sin(2*PI*(260+500*t+60*sin(2*PI*14*t))*t)*exp(-3.5*t)':d=0.55"),
 "pitido": sfx("pitido", "sine=f=1480:d=0.14,volume=0.35,afade=t=out:st=0.09:d=0.05"),
}
for nm in ("whoosh.wav", "reveal_swoosh.wav", "reveal_big.wav", "ding.wav", "sub_thump.wav", "pop.wav"):
    try: S[nm[:-4]] = lib(nm)
    except Exception as e: print("sin", nm, e)
E = [(T(ev["F_ABRE"]), "whoosh", 0.9), (T(ev["F_ABRE"] + 4), "reveal_big", 0.5),
     (T(ev["L1_BAJA"]), "clic", 0.9), (T(ev["L1_BAJA"] + 2), "aire", 0.9), (T(ev["L1_ADM"] - 4), "clic", 0.7),
     (T(ev["L1_SUBE"]), "sube", 0.9),
     (T(ev["L2_CHISPA"]), "chispa", 0.9), (T(ev["L2_CHISPA"] + 6), "chispa", 0.7), (T(ev["L2_EXPLOTA"] - 6), "chispa", 0.9),
     (T(ev["L2_EXPLOTA"]), "explosion", 1.0), (T(ev["L2_EXPLOTA"]), "sub_thump", 0.8),
     (T(ev["L2_SUBIR"]), "clic", 0.8), (T(ev["L2_SUBIR"] + 2), "escape", 0.9), (T(ev["L2_ESCAPE"] - 3), "clic", 0.6),
     (T(ev["EXP0"]), "reveal_swoosh", 0.8), (T(ev["EXP3"] - 6), "whoosh", 0.6), (T(ev["EXP3"]), "clac", 0.9),
     (T(ev["RAMPA0"]), "acelera", 0.9), (T(ev["L4_SEG"]), "decelera", 0.8),
     (T(ev["L4_CLOD"]), "boing", 0.9), (T(ev["L4_CLOD"]) + 0.05, "pitido", 0.6),
     (T(ev["L5_QUE"]), "pop", 0.6), (T(ev["CTA"] + 6), "ding", 0.6)]
f = ev["L3_CUATRO"]
while f < ev["L3_VUELTAS"]: E.append((T(f), "clac", 0.35)); f += 7
E = [e for e in E if e[1] in S]
ins = ["-stream_loop", "-1", "-i", MUS]; filt = []; n = 1; voz_lbl = []
for k, l in enumerate(vz["lineas"]):
    ins += ["-i", os.path.join(CLIPS, l["clip"] + ".wav")]
    ms = int(l["at"] * 1000); filt.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms},volume=1.0[v{k}]"); voz_lbl.append(f"[v{k}]"); n += 1
sfx_lbl = []
for k, (t, nm, vol) in enumerate(E):
    ins += ["-i", S[nm]]; ms = int(t * 1000)
    filt.append(f"[{n}:a]adelay={ms}|{ms},volume={vol}[s{k}]"); sfx_lbl.append(f"[s{k}]"); n += 1
ins += ["-i", S["ralenti"]]; t0 = T(ev["A2"]); ms = int(t0 * 1000)
filt.append(f"[{n}:a]afade=t=in:d=0.6,afade=t=out:st=5.0:d=2.0,adelay={ms}|{ms},volume=0.55[rr]"); sfx_lbl.append("[rr]"); n += 1
filt.append("".join(voz_lbl) + f"amix=inputs={len(voz_lbl)}:normalize=0[voz]")
filt.append("[voz]asplit=2[voz1][vozsc]")
filt.append(f"[0:a]atrim=0:{DUR:.2f},aresample=48000,aformat=channel_layouts=stereo,volume=0.17,afade=t=in:d=0.4,afade=t=out:st={DUR - 1.2:.2f}:d=1.2[mus]")
filt.append("[mus][vozsc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[musd]")
filt.append("".join(sfx_lbl) + f"amix=inputs={len(sfx_lbl)}:normalize=0,volume=0.75[fx]")
filt.append(f"[voz1][musd][fx]amix=inputs=3:normalize=0,atrim=0:{DUR:.2f},loudnorm=I=-14:TP=-1.0:LRA=11[out]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(filt), "-map", "[out]", "-ar", "48000", "-c:a", "libvorbis", "-q:a", "6", OUT], check=True)
print("mezcla", OUT, f"{DUR:.2f} s", len(E), "efectos")
