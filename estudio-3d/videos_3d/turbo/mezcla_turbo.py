# MEZCLA DE SONIDO · EL TURBO POR DENTRO (se ejecuta en el espacio de Ootto: python3 mezcla_turbo.py ...)
# Voz de Maite (Renata) frase a frase, música electrónica suave con ducking y efectos en cada momento:
# apertura, soplido de Clod (y su "ay"), gases de escape, silbido del turbo que sube, aire que entra, rampa de vueltas,
# despiece y montaje, ralentí y cierre. Máster a -14 LUFS.
# Uso: python3 mezcla_turbo.py <voces.json> <anclas.json> <carpeta_voces> <musica.mp3> <carpeta_sfx> <salida.ogg>
import json, subprocess, sys, os
VOZ, ANC, CLIPS, MUS, SFXD, OUT = sys.argv[1:7]
vz = json.load(open(VOZ, encoding="utf-8")); A = json.load(open(ANC)); ev = A["eventos"]; FIN = A["fin"]
def T(f): return (f - 1) / 30.0
DUR = T(FIN) + 0.4
TMP = "/tmp/sfx_turbo"; os.makedirs(TMP, exist_ok=True)
def sfx(nombre, expr):
    p = f"{TMP}/{nombre}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", expr, "-ac", "2", "-ar", "48000", p], check=True)
    return p
def lib(nombre):
    p = os.path.join(SFXD, nombre); q = f"{TMP}/lib_{nombre}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p, "-ac", "2", "-ar", "48000", q], check=True); return q
d_esc = max(1.5, T(ev["EXP0"]) - T(ev["L2_ESC"]) - 0.5)
S = {
 "soplido": sfx("soplido", "anoisesrc=d=1.1:c=pink:a=0.5,bandpass=f=1400:w=1600,afade=t=in:d=0.08,afade=t=out:st=0.6:d=0.5"),
 "triste": sfx("triste", "aevalsrc='0.30*sin(2*PI*(420-180*t)*t)*exp(-1.6*t)':d=0.9"),
 "escape": sfx("escape", f"anoisesrc=d={d_esc:.2f}:c=brown:a=0.40,lowpass=f=900,tremolo=f=9:d=0.35,afade=t=in:d=0.4,afade=t=out:st={d_esc - 1.0:.2f}:d=1.0"),
 # silbido del turbo: tono que sube de 700 a 3.600 Hz con su armónico, y luego se queda
 "silbido_sube": sfx("silbido_sube", "aevalsrc='0.10*sin(2*PI*(700*t+480*t*t))+0.04*sin(2*PI*(1400*t+960*t*t))':d=3.0,afade=t=in:d=0.5"),
 "silbido": sfx("silbido", "aevalsrc='0.10*sin(2*PI*3580*t)*(0.85+0.15*sin(2*PI*5*t))+0.035*sin(2*PI*7160*t)':d=6.5,afade=t=in:d=0.1,afade=t=out:st=5.5:d=1.0"),
 "silbido_baja": sfx("silbido_baja", "aevalsrc='0.10*sin(2*PI*(3600*t-520*t*t))':d=2.6,afade=t=out:st=1.4:d=1.2"),
 "aire": sfx("aire", "anoisesrc=d=2.6:c=pink:a=0.32,bandpass=f=1100:w=900,afade=t=in:d=0.3,afade=t=out:st=1.8:d=0.8"),
 "clac": sfx("clac", "aevalsrc='0.5*sin(2*PI*2600*t)*exp(-38*t)+0.4*sin(2*PI*1350*t)*exp(-30*t)+0.3*(random(0)-0.5)*exp(-60*t)':d=0.25"),
 "clic": sfx("clic", "aevalsrc='0.55*sin(2*PI*2100*t)*exp(-80*t)+0.35*sin(2*PI*900*t)*exp(-50*t)':d=0.14"),
 "ralenti": sfx("ralenti", "aevalsrc='0.10*sin(2*PI*1200*t)*(0.7+0.3*sin(2*PI*3*t))+0.05*sin(2*PI*26*t)':d=8,lowpass=f=2600"),
 "boing": sfx("boing", "aevalsrc='0.45*sin(2*PI*(260+500*t+60*sin(2*PI*14*t))*t)*exp(-3.5*t)':d=0.55"),
}
for nm in ("whoosh.wav", "reveal_swoosh.wav", "reveal_big.wav", "ding.wav", "sub_thump.wav", "pop.wav"):
    try: S[nm[:-4]] = lib(nm)
    except Exception as e: print("sin", nm, e)
E = [(T(ev["E_ABRE"]), "whoosh", 0.9), (T(ev["E_ABRE"] + 4), "reveal_big", 0.5),
     (T(ev["SOPLA0"] + 4), "soplido", 0.9), (T(ev["SOPLA0"] + 30), "clic", 0.4), (T(ev["SOPLA1"]) + 0.1, "triste", 0.7),
     (T(ev["L2_ESC"]), "sub_thump", 0.7), (T(ev["L2_ESC"]), "escape", 0.8), (T(ev["L2_ESC"] + 8), "boing", 0.7),
     (T(ev["L2_ESC"] + 4), "silbido_sube", 0.8), (T(ev["L2_ESC"] + 4) + 2.9, "silbido", 0.75),
     (T(ev["L3_AIRE"]), "aire", 0.9), (T(ev["L3_MAS"]), "silbido_sube", 0.55), (T(ev["L3_POT"]), "sub_thump", 0.6),
     (T(ev["EXP0"] - 30), "silbido_baja", 0.7),
     (T(ev["EXP0"] + 16), "reveal_swoosh", 0.8), (T(ev["EXP3"] - 8), "whoosh", 0.6), (T(ev["EXP3"]), "clac", 0.9),
     (T(ev["L5_QUE"]), "pop", 0.6), (T(ev["CTA"] + 6), "ding", 0.6)]
E = [e for e in E if e[1] in S]
ins = ["-stream_loop", "-1", "-i", MUS]; filt = []; n = 1; voz_lbl = []
for k, l in enumerate(vz["lineas"]):
    ins += ["-i", os.path.join(CLIPS, l["clip"] + ".wav")]
    ms = int(l["at"] * 1000); filt.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms},volume=1.0[v{k}]"); voz_lbl.append(f"[v{k}]"); n += 1
sfx_lbl = []
for k, (t, nm, vol) in enumerate(E):
    ins += ["-i", S[nm]]; ms = int(t * 1000)
    filt.append(f"[{n}:a]adelay={ms}|{ms},volume={vol}[s{k}]"); sfx_lbl.append(f"[s{k}]"); n += 1
ins += ["-i", S["ralenti"]]; t0 = T(ev["EXP3"] + 14); ms = int(t0 * 1000)
filt.append(f"[{n}:a]afade=t=in:d=0.8,afade=t=out:st=6.0:d=2.0,adelay={ms}|{ms},volume=0.45[rr]"); sfx_lbl.append("[rr]"); n += 1
filt.append("".join(voz_lbl) + f"amix=inputs={len(voz_lbl)}:normalize=0[voz]")
filt.append("[voz]asplit=2[voz1][vozsc]")
filt.append(f"[0:a]atrim=0:{DUR:.2f},aresample=48000,aformat=channel_layouts=stereo,volume=0.17,afade=t=in:d=0.4,afade=t=out:st={DUR - 1.2:.2f}:d=1.2[mus]")
filt.append("[mus][vozsc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[musd]")
filt.append("".join(sfx_lbl) + f"amix=inputs={len(sfx_lbl)}:normalize=0,volume=0.75[fx]")
filt.append(f"[voz1][musd][fx]amix=inputs=3:normalize=0,atrim=0:{DUR:.2f},loudnorm=I=-14:TP=-1.0:LRA=11[out]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(filt), "-map", "[out]", "-ar", "48000", "-c:a", "libvorbis", "-q:a", "6", OUT], check=True)
print("mezcla", OUT, f"{DUR:.2f} s", len(E), "efectos")
