"""Reel "4 cose che Clepsi fa al posto tuo" (formato a elenco numerato, idea di Stefano dell'11/11 da una pubblicità di Magisterut).

Apertura con la promessa numerata, poi un punto per schermata: contatore "1 / 4", titolo su due righe (bianco + lime)
e sotto l'app vera; chiusura con le etichette dei punti e "Prova l'app gratis".
Le riprese (12/11) sono fatte fotogramma per fotogramma con strumenti/registra/ (Studio di esempio, 30 fps, scorrimenti
con accelerazione morbida, tocco visibile): tra una ripresa e l'altra una dissolvenza incrociata, mai un taglio secco.
Telefono dentro la zona sicura di Instagram. Solo i suoni dell'app: la musica la aggiunge Stefano.

Uso: node strumenti/registra/riprese_quattro.js lavoro/quattro/riprese   (con la build dell'app servita su :8765)
     python3 strumenti/reel_quattro.py
Esce in lavoro/quattro/reel-quattro-cose.mp4 e copertine/reel-quattro-cose.jpg
"""
import subprocess, sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from reel_lib import render_pngs, overlay

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP, AUD = ROOT / 'sorgenti' / 'app', ROOT / 'sorgenti' / 'audio'
W = ROOT / 'lavoro' / 'quattro'; W.mkdir(parents=True, exist_ok=True)
NOME = 'reel-quattro-cose'
FPS = 30
PW, PH, PX, PY = 860, 1100, 110, 440          # finestra centrata; a destra le icone sfiorano solo il margine bianco dell'app (x 940-970), sotto lascia 380 px a nome, didascalia e audio
SW, SH = 780, 1596                             # schermo intero della ripresa (390x798 css a 2x, senza la striscia "Studio di esempio")
CH = SH * 0 + PH * SW / PW                     # altezza di schermo che entra nella finestra: il resto lo mostra la camera
LIME, NERO = '#D4FF3A', '#0B0B0D'
APERTURA, CHIUSURA, DISS = 1.8, 3.4, 0.3
ENTRA = 0.35                                   # il telefono entra ed esce sfumando, mai sovrapposto ai cartelli
RIP = W / 'riprese'
SCALA = 2                                      # le riprese sono a 2x: 780x1684, la striscia "Studio di esempio" (44 px css) si taglia

# punti: (domanda, risposta in lime, suoni dei tocchi nell'ordine). La ripresa è una sola (riprese/unica):
# i segni p1..p4 in eventi.json dicono dove cambia il titolo.
PUNTI = [
    ('Il timesheet?', 'Due tap, la sera.', ['clepsi_tocco_mattina', 'clepsi_tocco_mattina', 'clepsi_tocco_pomeriggio', 'clepsi_tocco_pomeriggio', 'clepsi_giornata_registrata']),
    ('Come chiuderà?', 'Lo sai la mattina dopo.', ['clepsi_tocco_mattina']),
    ('Una commessa in perdita?', 'La vedi quando c’è tempo.', ['clepsi_tocco_mattina']),
    ('Chi ha lavorato su cosa?', 'Senza chiederlo a nessuno.', ['clepsi_tocco_mattina', 'clepsi_tocco_pomeriggio']),
]
ETICHETTE = ['Due tap la sera', 'Come chiuderà ogni commessa', 'Perdite viste in tempo', 'La settimana dello studio']

LOGO = ("<svg width='{s}' height='{s}' viewBox='0 0 22 22'><circle cx='11' cy='11' r='9.5' fill='none' stroke='{c}' stroke-width='1.5'/>"
        "<path d='M11 1.5 A9.5 9.5 0 0 0 11 20.5 Z' fill='{c}'/></svg>")

def titolo(i, d, r):
    return (f"<div style='position:absolute;left:{PX}px;top:178px;width:930px'>"
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

def ease(t):
    return 4 * t * t * t if t < .5 else 1 - (-2 * t + 2) ** 3 / 2

def transizione(A, B, come, n):
    """Fotogrammi tra A (prima) e B (dopo), come nell'app vera: la sera sale dal basso, la scheda entra da destra."""
    from PIL import Image
    w, h = A.size; nero = Image.new('RGB', (w, h), (11, 11, 13)); out = []
    ombra = Image.new('L', (40, h))
    for x in range(40): ombra.paste(int(70 * (1 - x / 40) ** 2), (x, 0, x + 1, h))
    for i in range(1, n + 1):
        e = ease(i / (n + 1))
        if come == 'dissolve':                      # passa per il colore di fondo: mai due schermate sovrapposte
            fondo = Image.new('RGB', (w, h), B.getpixel((6, h // 2)))
            f = Image.blend(A, fondo, ease(min(1, 2 * i / (n + 1)))) if i <= n / 2 else Image.blend(fondo, B, ease(max(0, 2 * i / (n + 1) - 1)))
        elif come == 'sale':
            f = Image.blend(A, nero, .35 * e); f.paste(B, (0, round(h * (1 - e))))
        elif come == 'scende':
            f = Image.blend(B, nero, .35 * (1 - e)); f.paste(A, (0, round(h * e)))
        elif come in ('entra', 'esce'):
            k = e if come == 'entra' else 1 - e            # quanto è entrata la schermata nuova (B per entra, A per esce)
            sotto, sopra = (A, B) if come == 'entra' else (B, A)
            f = Image.blend(sotto, nero, .25 * k).copy()
            f = f.crop((round(.28 * w * k), 0, w, h)); g = Image.new('RGB', (w, h)); g.paste(f, (0, 0)); f = g
            xs = round(w * (1 - k)); f.paste(sopra.crop((0, 0, w - xs, h)), (xs, 0))
            if xs > 0: f.paste((0, 0, 0), (xs - 40, 0, xs, h), ombra.transpose(Image.FLIP_LEFT_RIGHT)) if xs >= 40 else None
        out.append(f)
    return out

def main():
    from PIL import Image
    d = RIP / 'unica'; ev = json.loads((d / 'eventi.json').read_text())
    fot = sorted(d.glob('*.jpg'))
    passaggi = {e['f']: e for e in ev['eventi'] if e['tipo'] == 'passaggio'}
    segni = {e['nome']: e['f'] for e in ev['eventi'] if e['tipo'] == 'segno'}
    taglio = (0, 44 * SCALA, SW, 44 * SCALA + SH)
    carica = lambda i: Image.open(fot[i]).convert('RGB').crop(taglio)
    T = W / 'telefono'; T.mkdir(exist_ok=True)
    for x in T.glob('*.jpg'): x.unlink()
    # 1) scaletta del video: fotogrammi della ripresa e transizioni in mezzo
    voci, mappa, k = [], {}, 0
    for i in range(len(fot)):
        if i in passaggi and i > 0:
            n = round(passaggi[i]['durata'] * FPS)
            voci.append(('tr', i, n)); k += n
        mappa[i] = k; voci.append(('f', i, 0)); k += 1
    inizio = {i: mappa[i] - (round(passaggi[i]['durata'] * FPS) if i in passaggi and i > 0 else 0) for i in mappa}
    # 2) camera: si sposta con un'accelerazione morbida da un'inquadratura all'altra
    cam = [0.0] * k; pos = 0.0; mosse = sorted((inizio[e['f']], e['pos'], e['durata']) for e in ev['eventi'] if e['tipo'] == 'camera')
    for j, (a, dove, dur) in enumerate(mosse):
        n = max(1, round(dur * FPS)); b = mosse[j + 1][0] if j + 1 < len(mosse) else k
        da = cam[a - 1] if a > 0 else dove
        for t in range(a, b): cam[t] = da + (dove - da) * ease(min(1, (t - a + 1) / n))
    def inquadra(im, t):
        y = cam[t] * (SH - CH)
        return im.resize((PW, round(PW * SH / SW)), Image.LANCZOS, box=None).crop((0, round(y * PW / SW), PW, round(y * PW / SW) + PH))
    # 3) fotogrammi
    k, prima = 0, None
    for tipo, i, n in voci:
        im = carica(i)
        if tipo == 'tr':
            for f in transizione(prima, im, passaggi[i]['come'], n):
                inquadra(f, k).save(T / f'{k:05d}.jpg', quality=94); k += 1
        else:
            inquadra(im, k).save(T / f'{k:05d}.jpg', quality=94); k += 1; prima = im
    durata = k / FPS
    t0 = APERTURA + DISS                              # il telefono entra quando l'apertura è sparita del tutto
    fine = t0 + durata; tot = fine + CHIUSURA
    inizi = [t0 + mappa[segni[f'p{j + 1}']] / FPS for j in range(len(PUNTI))]
    # suoni: i tocchi di ciascun punto, nell'ordine
    suoni = []
    for j in range(len(PUNTI)):
        a = segni[f'p{j + 1}']; b = segni.get(f'p{j + 2}', segni['fine'])
        for nome, f in zip(PUNTI[j][2], [f for f in ev['tocchi'] if a <= f < b]):
            suoni.append((nome, t0 + mappa[f] / FPS + (0.25 if nome == 'clepsi_giornata_registrata' else 0)))
    tel = W / 'telefono.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', str(T / '%05d.jpg'),
                    '-vf', f'fade=t=in:st=0:d={ENTRA},fade=t=out:st={durata - ENTRA:.3f}:d={ENTRA},format=yuv420p',
                    '-c:v', 'libx264', '-crf', '14', str(tel)], check=True)
    base = W / 'base.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c={NERO[1:]}:s=1080x1920:r={FPS}:d={tot:.3f}',
                    '-itsoffset', f'{t0:.3f}', '-i', str(tel), '-filter_complex',
                    f'[0:v][1:v]overlay={PX}:{PY}:eof_action=pass,format=yuv420p,setsar=1',
                    '-t', f'{tot:.3f}', '-c:v', 'libx264', '-crf', '16', str(base)], check=True)
    voci = {'apertura': apertura(), 'cornice': cornice(), 'chiusura': chiusura()}
    for k, (d, r, _) in enumerate(PUNTI):
        voci[f't{k}'] = titolo(k + 1, d, r)
    render_pngs(voci, W)
    P = lambda n: str(W / f'{n}.png')
    ovs = [(P('cornice'), t0, fine, ENTRA, ENTRA)]
    for k in range(len(PUNTI)):
        a = inizi[k]; b = inizi[k + 1] if k + 1 < len(PUNTI) else fine
        ovs.append((P(f't{k}'), a, b, ENTRA if k == 0 else 0.3, ENTRA if k == len(PUNTI) - 1 else 0.25))
    ovs.insert(0, (P('apertura'), 0, APERTURA + DISS, 0, DISS))
    ovs.append((P('chiusura'), fine, tot, 0.4, 0))
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
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{inizi[2] + 2.1:.2f}', '-i', str(out), '-frames:v', '1',
                    '-vf', f'crop={PW}:{PH}:{PX}:{PY}', '-q:v', '2', str(fr)], check=True)
    import base64
    img = 'data:image/jpeg;base64,' + base64.b64encode(fr.read_bytes()).decode()
    cop = (f"<div style='position:absolute;inset:0;background:{NERO}'></div>"
           "<div style='position:absolute;left:90px;top:300px;width:900px'>"
           f"<div style='display:flex;align-items:center;justify-content:space-between'><span style='font-size:32px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:{LIME}'>Clepsi</span>{LOGO.format(s=46, c=LIME)}</div>"
           f"<div class='b' style='font-size:96px;line-height:.98;letter-spacing:-.04em;margin-top:22px'>4 cose che fa<br><span style='color:{LIME}'>al posto tuo.</span></div></div>"
           f"<div style='position:absolute;left:{(1080 - PW) // 2}px;top:600px;width:{PW}px;height:{PH}px;border-radius:46px;overflow:hidden;box-shadow:0 0 0 3px #2E2E34'>"
           f"<img src='{img}' style='width:100%;height:100%;object-fit:cover;object-position:top'></div>")
    render_pngs({'copertina': cop}, W)
    (ROOT / 'copertine').mkdir(exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(W / 'copertina.png'), '-q:v', '2', str(ROOT / 'copertine' / f'{NOME}.jpg')], check=True)
    print(out, round(tot, 2))

if __name__ == '__main__':
    main()
