"""Reel "Come funziona Clepsi": l'app vera, registrata dal telefono di Stefano nello "Studio di esempio".

Uso:
  python3 strumenti/reel_app.py [registrazione_A.mp4 registrazione_B.mp4]

A = registrazione del 28/10 19:27 (domanda della sera, settimana dello studio)
B = registrazione del 28/10 22:54 (schermata del titolare, scheda Uffici Lambrate)
Se non si passano, usa i pezzi già tagliati in sorgenti/app/.
Esce lavoro/reel-app-come-funziona.mp4 (1080x1920, 30 fps, senza musica: la aggiunge Stefano su Instagram).
"""
import sys, subprocess, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from reel_lib import render_pngs, overlay

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / 'sorgenti' / 'app'
AUD = ROOT / 'sorgenti' / 'audio'
W = ROOT / 'lavoro' / 'reel_app'
W.mkdir(parents=True, exist_ok=True)
PW, PH, PX, PY = 700, 1432, 190, 398       # schermo del telefono nel reel
CROP_TOP = 140                              # barra di stato dell'iPhone (ora, registrazione)

# pezzi: (sorgente, inizio, fine, velocità)
PEZZI = {
    'domanda': [('A', 11.0, 13.8, 1), ('A', 14.6, 16.4, 1), ('A', 18.3, 20.8, 1), ('A', 22.4, 23.2, 1), ('A', 23.4, 26.4, 1)],
    'titolare': [('B', 0.0, 4.0, 1), ('B', 5.0, 12.0, 1)],
    'commessa': [('B', 24.3, 28.0, 1), ('B', 28.0, 33.0, 1)],
    'settimana': [('A', 91.6, 96.0, 1)],
}
NOTIFICA, BRAND_D = 3.0, 3.5
# tocchi nella domanda, in secondi dall'inizio dei pezzi della domanda
TOCCO_MATTINA, TOCCO_POMERIGGIO, TOCCO_FATTO = 1.3, 2.8 + 1.8 + 0.7, 2.8 + 1.8 + 2.5 + 0.55

def taglia(src, a, b, vel, out):
    vf = f"crop=1170:{2532 - CROP_TOP}:0:{CROP_TOP},scale={PW}:{PH},setpts=(PTS-STARTPTS)/{vel},fps=30,format=yuv420p,setsar=1"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(b - a), '-i', src, '-vf', vf, '-an',
                    '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', str(out)], check=True)

def main(argv):
    SRC.mkdir(parents=True, exist_ok=True)
    reg = {'A': argv[0], 'B': argv[1]} if len(argv) >= 2 else None
    clips, durate = [], {}
    for nome, lista in PEZZI.items():
        tot = 0
        for i, (k, a, b, v) in enumerate(lista):
            f = SRC / f'{nome}-{i}.mp4'
            if reg: taglia(reg[k], a, b, v, f)
            clips.append(f); tot += (b - a) / v
        durate[nome] = tot

    # grafiche: notifica (dentro lo schermo), cornice, didascalie, chiusura
    LOGO = ("<svg width='{s}' height='{s}' viewBox='0 0 22 22'><circle cx='11' cy='11' r='9.5' fill='none' stroke='#D4FF3A' stroke-width='1.6'/>"
            "<path d='M11 1.5 A9.5 9.5 0 0 0 11 20.5 Z' fill='#D4FF3A'/></svg>")
    sfondo = (f"<div style='position:absolute;left:{PX}px;top:{PY}px;width:{PW}px;height:{PH}px;"
              "background:radial-gradient(120% 80% at 30% 20%,#2a2a33,#0B0B0D 70%)'></div>"
              f"<div style='position:absolute;left:{PX}px;top:{PY + 150}px;width:{PW}px;text-align:center'>"
              "<div style='font-size:28px;color:#D8D7DE'>mercoledì 28 ottobre</div>"
              "<div class='b' style='font-size:150px;letter-spacing:-.04em;line-height:1;margin-top:6px'>19:00</div></div>")
    notifica = (f"<div style='position:absolute;left:{PX + 24}px;top:{PY + 520}px;width:{PW - 48}px;padding:22px 24px;border-radius:30px;"
                "background:rgba(246,245,241,.16);backdrop-filter:blur(10px);display:flex;gap:18px;align-items:flex-start'>"
                f"<div style='width:64px;height:64px;border-radius:16px;background:#0B0B0D;display:flex;align-items:center;justify-content:center;flex:none'>{LOGO.format(s=44)}</div>"
                "<div style='flex:1'><div style='display:flex;justify-content:space-between;font-size:22px;color:#D8D7DE;letter-spacing:.06em'>"
                "<span>CLEPSI</span><span style='letter-spacing:0'>adesso</span></div>"
                "<div style='font-size:30px;font-weight:700;margin-top:4px'>Com'è andata oggi?</div>"
                "<div style='font-size:27px;color:#E8E7EC;margin-top:2px'>Mattina e pomeriggio, due tap.</div></div></div>")
    cornice = ("<svg width='1080' height='1920' style='position:absolute;inset:0'><defs><mask id='m'><rect width='1080' height='1920' fill='white'/>"
               f"<rect x='{PX}' y='{PY}' width='{PW}' height='{PH}' rx='54' fill='black'/></mask></defs>"
               "<rect width='1080' height='1920' fill='#0B0B0D' mask='url(#m)'/>"
               f"<rect x='{PX - 3}' y='{PY - 3}' width='{PW + 6}' height='{PH + 6}' rx='57' fill='none' stroke='#2E2E34' stroke-width='3'/></svg>"
               f"<div style='position:absolute;left:0;right:0;top:{PY + PH + 26}px;text-align:center;font-size:24px;color:#8E8D96'>Studio e dati di esempio</div>")
    def didascalia(sopra, titolo):
        return (f"<div style='position:absolute;left:80px;top:118px;width:920px'>"
                f"<div style='font-size:30px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#D4FF3A'>{sopra}</div>"
                f"<div class='b' style='font-size:66px;line-height:1.02;letter-spacing:-.035em;margin-top:14px'>{titolo}</div></div>")
    DID = {
        'd0': didascalia('Ore 19:00', 'Arriva una domanda sola.'),
        'd1': didascalia('Ogni sera', 'Due tap: mattina e pomeriggio.'),
        'd2': didascalia('La mattina dopo', 'Il titolare vede come chiuderà ogni commessa.'),
        'd3': didascalia('Uffici Lambrate · in perdita', 'Lo sai quando c’è ancora tempo.'),
        'd4': didascalia('La settimana dello studio', 'Dove sono andate le giornate.'),
    }
    BRAND = (f"<div style='position:absolute;inset:0;background:#0B0B0D'></div>"
             f"<div style='position:absolute;left:0;right:0;top:560px;display:flex;flex-direction:column;align-items:center;gap:56px;text-align:center'>"
             f"<span class='b' style='font-size:104px;line-height:.98;letter-spacing:-.04em;width:860px'>Ogni sera<br>due tap.</span>"
             f"{LOGO.format(s=230).replace(chr(39) + '1.6' + chr(39), chr(39) + '1.2' + chr(39))}"
             f"<span class='b' style='font-size:130px;line-height:1;letter-spacing:-.04em;margin-top:-16px'>Clepsi</span>"
             f"<span style='font-size:40px;color:#A9A8B2'>clepsi.it</span></div>")
    render_pngs({'sfondo': sfondo, 'notifica': notifica, 'cornice': cornice, 'brand': BRAND, **DID}, W)
    P = lambda n: str(W / f'{n}.png')

    # traccia del telefono: notifica (immagine) + pezzi dell'app, uno dopo l'altro
    lista = W / 'lista.txt'
    nota = W / 'notifica.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c=0x0B0B0D:s={PW}x{PH}:r=30:d={NOTIFICA}',
                    '-vf', 'format=yuv420p,setsar=1', '-c:v', 'libx264', '-crf', '17', str(nota)], check=True)
    lista.write_text(''.join(f"file '{c}'\n" for c in [nota, *clips]))
    tel = W / 'telefono.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lista), '-c', 'copy', str(tel)], check=True)

    t1 = NOTIFICA; t2 = t1 + durate['domanda']; t3 = t2 + durate['titolare']; t4 = t3 + durate['commessa']; t5 = t4 + durate['settimana']
    TOT = t5 + BRAND_D
    base = W / 'base.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c=0x0B0B0D:s=1080x1920:r=30:d={TOT:.3f}', '-i', str(tel),
                    '-filter_complex', f'[0:v][1:v]overlay={PX}:{PY}:eof_action=pass,format=yuv420p,setsar=1',
                    '-c:v', 'libx264', '-crf', '16', str(base)], check=True)

    # suoni dell'app nei momenti dei tocchi
    suoni = [('clepsi_notifica', 0.75), ('clepsi_tocco_mattina', t1 + TOCCO_MATTINA), ('clepsi_tocco_pomeriggio', t1 + TOCCO_POMERIGGIO),
             ('clepsi_giornata_registrata', t1 + TOCCO_FATTO)]
    aud = W / 'audio.wav'
    args = ['ffmpeg', '-v', 'error', '-y']
    for s, _ in suoni: args += ['-i', str(AUD / f'{s}.wav')]
    fc = ';'.join(f'[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={int(t * 1000)}|{int(t * 1000)}[s{i}]' for i, (_, t) in enumerate(suoni))
    fc += ';' + ''.join(f'[s{i}]' for i in range(len(suoni))) + f'amix=inputs={len(suoni)}:normalize=0,apad,atrim=0:{TOT:.3f},loudnorm=I=-16:TP=-1.5[a]'
    subprocess.run(args + ['-filter_complex', fc, '-map', '[a]', '-ar', '48000', str(aud)], check=True)

    ovs = [(P('sfondo'), 0, t1, 0, 0.15), (P('notifica'), 0.6, t1, 0.4, 0.2), (P('cornice'), 0, t5, 0, 0),
           (P('d0'), 0, t1, 0.5, 0.3), (P('d1'), t1, t2, 0.5, 0.3), (P('d2'), t2, t3, 0.5, 0.3),
           (P('d3'), t3, t4, 0.5, 0.3), (P('d4'), t4, t5, 0.5, 0.3), (P('brand'), t5 - 0.5, TOT, 0.5, 0)]
    out = ROOT / 'lavoro' / 'reel-app-come-funziona.mp4'
    overlay(str(base), ovs, str(out), audio=str(aud))
    print(out, round(TOT, 2), {k: round(v, 2) for k, v in durate.items()})

if __name__ == '__main__':
    main(sys.argv[1:])
