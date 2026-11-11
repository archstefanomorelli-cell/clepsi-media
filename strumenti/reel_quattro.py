"""Reel "4 cose che Clepsi fa al posto tuo" (formato a elenco numerato, idea di Stefano dell'11/11 da una pubblicità di Magisterut).

Apertura con la promessa numerata, poi un punto per schermata: contatore "1 / 4", titolo su due righe (bianco + lime)
e sotto l'app vera (pezzi in sorgenti/app/, Studio di esempio); chiusura con le etichette dei punti e "Prova l'app gratis".
Telefono dentro la zona sicura di Instagram. Solo i suoni dell'app: la musica la aggiunge Stefano.

Uso: python3 strumenti/reel_quattro.py
Esce in lavoro/quattro/reel-quattro-cose.mp4 e copertine/reel-quattro-cose.jpg
"""
import subprocess, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from reel_lib import render_pngs, overlay

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP, AUD = ROOT / 'sorgenti' / 'app', ROOT / 'sorgenti' / 'audio'
W = ROOT / 'lavoro' / 'quattro'; W.mkdir(parents=True, exist_ok=True)
NOME = 'reel-quattro-cose'
FPS = 30
PW, PH, PX, PY = 520, 1064, 280, 432          # telefono (zona sicura: sotto 1500 copre la didascalia)
LIME, NERO = '#D4FF3A', '#0B0B0D'
APERTURA, CHIUSURA, DISS = 1.8, 3.4, 0.3

# punti: (domanda, risposta in lime, pezzi [(file, da, a)], suoni [(suono, secondi dall'inizio del punto)])
PUNTI = [
    ('Il timesheet?', 'Due tap, la sera.',
     [('domanda_c-0', 0.6, 2.4), ('domanda_c-2', 0.2, 1.4), ('domanda_c-3', 0.0, 0.7)],
     [('clepsi_tocco_mattina', 0.4), ('clepsi_tocco_pomeriggio', 1.8 + 0.4), ('clepsi_giornata_registrata', 3.0 + 0.55)]),
    ('Come chiuderà?', 'Lo sai la mattina dopo.',
     [('titolare_g-0', 0.0, 2.5), ('titolare_g-1', 0.0, 1.5)], []),
    ('Una commessa in perdita?', 'La vedi quando c’è tempo.',
     [('commessa_c-0', 0.0, 3.2), ('commessa_c-1', 0.0, 0.8)], []),
    ('Chi ha lavorato su cosa?', 'Senza chiederlo a nessuno.',
     [('settimana-0', 0.5, 4.5)], []),
]
ETICHETTE = ['Due tap la sera', 'Come chiuderà ogni commessa', 'Perdite viste in tempo', 'La settimana dello studio']

LOGO = ("<svg width='{s}' height='{s}' viewBox='0 0 22 22'><circle cx='11' cy='11' r='9.5' fill='none' stroke='{c}' stroke-width='1.5'/>"
        "<path d='M11 1.5 A9.5 9.5 0 0 0 11 20.5 Z' fill='{c}'/></svg>")

def titolo(i, d, r):
    return ("<div style='position:absolute;left:80px;top:178px;width:920px'>"
            f"<span style='display:inline-block;font-size:26px;font-weight:700;letter-spacing:.12em;color:{LIME};border:2px solid {LIME};"
            f"border-radius:999px;padding:6px 16px'>{i} / {len(PUNTI)}</span>"
            f"<div class='b' style='font-size:74px;line-height:1.0;letter-spacing:-.04em;margin-top:22px'>{d}<br>"
            f"<span style='color:{LIME}'>{r}</span></div></div>")

def cornice():
    return ("<svg width='1080' height='1920' style='position:absolute;inset:0'><defs><mask id='m'><rect width='1080' height='1920' fill='white'/>"
            f"<rect x='{PX}' y='{PY}' width='{PW}' height='{PH}' rx='46' fill='black'/></mask></defs>"
            f"<rect width='1080' height='1920' fill='{NERO}' mask='url(#m)'/>"
            f"<rect x='{PX - 3}' y='{PY - 3}' width='{PW + 6}' height='{PH + 6}' rx='49' fill='none' stroke='#2E2E34' stroke-width='3'/></svg>")

def apertura():
    return (f"<div style='position:absolute;inset:0;background:{NERO}'></div>"
            "<div style='position:absolute;left:80px;top:560px;width:920px'>"
            f"<div style='display:flex;align-items:center;gap:16px'>{LOGO.format(s=54, c=LIME)}"
            "<span class='b' style='font-size:46px;letter-spacing:-.03em'>Clepsi</span></div>"
            "<div class='b' style='font-size:122px;line-height:.96;letter-spacing:-.045em;margin-top:36px'>4 cose che fa<br>"
            f"<span style='color:{LIME}'>al posto tuo.</span></div>"
            "<div style='font-size:36px;color:#C9C8D0;margin-top:34px'>Per studi di architettura e ingegneria</div></div>")

def chiusura():
    chips = ''.join(f"<span style='font-size:30px;padding:12px 22px;border:2px solid #3A3A42;border-radius:999px;color:#E8E7EC'>"
                    f"<span style='color:{LIME}'>✓</span> {e}</span>" for e in ETICHETTE)
    return (f"<div style='position:absolute;inset:0;background:{NERO}'></div>"
            "<div style='position:absolute;left:0;right:0;top:400px;display:flex;flex-direction:column;align-items:center;text-align:center'>"
            f"{LOGO.format(s=120, c=LIME)}"
            "<div class='b' style='font-size:116px;line-height:.96;letter-spacing:-.045em;margin-top:40px'>Ogni sera,<br>"
            f"<span style='color:{LIME}'>due tap.</span></div>"
            f"<div style='display:flex;flex-wrap:wrap;justify-content:center;gap:14px;width:900px;margin-top:48px'>{chips}</div>"
            f"<div style='margin-top:56px;background:{LIME};color:{NERO};font-weight:700;font-size:40px;padding:22px 48px;border-radius:999px'>Prova l'app gratis</div>"
            "<div style='font-size:32px;color:#A9A8B2;margin-top:22px'>clepsi.it · Studio e dati di esempio</div></div>")

def main():
    # traccia del telefono: tutti i pezzi in fila
    pezzi, inizi, t = [], [], APERTURA
    for k, (_, _, lista, _) in enumerate(PUNTI):
        inizi.append(t)
        for j, (f, a, b) in enumerate(lista):
            o = W / f'p{k}-{j}.mp4'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(APP / f'{f}.mp4'), '-vf', f'trim={a}:{b},setpts=PTS-STARTPTS,fps={FPS}',
                            '-an', '-c:v', 'libx264', '-crf', '16', str(o)], check=True)
            pezzi.append(o); t += b - a
    fine = t; tot = fine + CHIUSURA
    lista = W / 'telefono.txt'; lista.write_text(''.join(f"file '{p}'\n" for p in pezzi))
    tel = W / 'telefono.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lista), '-c', 'copy', str(tel)], check=True)
    base = W / 'base.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c={NERO[1:]}:s=1080x1920:r={FPS}:d={tot:.3f}',
                    '-itsoffset', f'{APERTURA}', '-i', str(tel), '-filter_complex',
                    f'[1:v]scale={PW}:{PH}[t];[0:v][t]overlay={PX}:{PY}:eof_action=pass,format=yuv420p,setsar=1',
                    '-t', f'{tot:.3f}', '-c:v', 'libx264', '-crf', '16', str(base)], check=True)
    voci = {'apertura': apertura(), 'cornice': cornice(), 'chiusura': chiusura()}
    for k, (d, r, _, _) in enumerate(PUNTI):
        voci[f't{k}'] = titolo(k + 1, d, r)
    render_pngs(voci, W)
    P = lambda n: str(W / f'{n}.png')
    ovs = [(P('cornice'), APERTURA, fine, 0, 0)]
    for k in range(len(PUNTI)):
        a = inizi[k]; b = inizi[k + 1] if k + 1 < len(PUNTI) else fine
        ovs.append((P(f't{k}'), a, b, 0.25 if k else 0, 0.2))
    ovs.insert(0, (P('apertura'), 0, APERTURA + DISS, 0, DISS))
    ovs.append((P('chiusura'), fine - DISS, tot, DISS, 0))
    # suoni
    suoni = [(s, inizi[k] + o) for k, p in enumerate(PUNTI) for s, o in p[3]]
    aud = W / 'audio.wav'
    args = ['ffmpeg', '-v', 'error', '-y']
    for s, _ in suoni: args += ['-i', str(AUD / f'{s}.wav')]
    fc = ';'.join(f'[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={int(x * 1000)}|{int(x * 1000)}[s{i}]' for i, (_, x) in enumerate(suoni))
    fc += ';' + ''.join(f'[s{i}]' for i in range(len(suoni))) + f'amix=inputs={len(suoni)}:normalize=0,apad,atrim=0:{tot:.3f},loudnorm=I=-16:TP=-1.5[a]'
    subprocess.run(args + ['-filter_complex', fc, '-map', '[a]', '-ar', '48000', str(aud)], check=True)
    out = W / f'{NOME}.mp4'
    overlay(str(base), ovs, str(out), audio=str(aud))
    # copertina: l'apertura con sotto la schermata del titolare
    fr = W / 'fr.jpg'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{inizi[1] + 1.0:.2f}', '-i', str(out), '-frames:v', '1',
                    '-vf', f'crop={PW}:{PH}:{PX}:{PY}', '-q:v', '2', str(fr)], check=True)
    import base64
    img = 'data:image/jpeg;base64,' + base64.b64encode(fr.read_bytes()).decode()
    cop = (f"<div style='position:absolute;inset:0;background:{NERO}'></div>"
           "<div style='position:absolute;left:90px;top:300px;width:900px'>"
           f"<div style='display:flex;align-items:center;justify-content:space-between'><span style='font-size:32px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:{LIME}'>Clepsi</span>{LOGO.format(s=46, c=LIME)}</div>"
           f"<div class='b' style='font-size:96px;line-height:.98;letter-spacing:-.04em;margin-top:22px'>4 cose che fa<br><span style='color:{LIME}'>al posto tuo.</span></div></div>"
           f"<div style='position:absolute;left:{(1080 - 508) // 2}px;top:640px;width:508px;height:1020px;border-radius:44px;overflow:hidden;box-shadow:0 0 0 3px #2E2E34'>"
           f"<img src='{img}' style='width:100%;height:100%;object-fit:cover;object-position:top'></div>")
    render_pngs({'copertina': cop}, W)
    (ROOT / 'copertine').mkdir(exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(W / 'copertina.png'), '-q:v', '2', str(ROOT / 'copertine' / f'{NOME}.jpg')], check=True)
    print(out, round(tot, 2))

if __name__ == '__main__':
    main()
