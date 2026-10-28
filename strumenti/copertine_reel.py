"""Copertine dei reel per la griglia del profilo: fondo nero, titolo grande, immagine sotto.

Uso: python3 strumenti/copertine_reel.py
Esce in copertine/<reel>.jpg (1080x1920). Instagram nella griglia mostra la parte centrale 1080x1440
(da y=240 a y=1680): testi e immagine stanno lì dentro.
"""
import base64, subprocess, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from reel_lib import render_pngs

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'copertine'; OUT.mkdir(exist_ok=True)
W = ROOT / 'lavoro' / 'copertine'; W.mkdir(parents=True, exist_ok=True)
PX, PY, PW, PH = 190, 398, 700, 1432   # schermo del telefono nei reel dell'app

# reel: (sopra, titolo con *parola in lime*, tipo immagine, sorgente, secondo)
COPERTINE = {
    'reel-app-come-funziona': ('Come funziona', 'Clepsi in *40 secondi*.', 'app', 'reel/reel-app-come-funziona.mp4', 9.4),
    'reel-app-1-ore-19': ('Ogni sera alle 19', 'Due tap e *hai finito*.', 'app', 'reel/reel-app-1-ore-19.mp4', 2.2),
    'reel-app-2-la-mattina-dopo': ('La mattina dopo', 'Come chiuderà *ogni commessa*?', 'app', 'reel/reel-app-2-la-mattina-dopo.mp4', 1.5),
    'reel-app-3-la-settimana': ('La settimana dello studio', 'Dove sono andate *le giornate*?', 'app', 'reel/reel-app-3-la-settimana.mp4', 2.5),
    'reel-racconto-1-meridiana': ('Seneca · Lettere a Lucilio', 'Solo il tempo *è nostro*.', 'scena', 'sorgenti/racconto/s1-meridiana-ombra.mp4', 3.0),
    'reel-racconto-2-strappo': ('La variante del venerdì', '«Tanto è una *cosa veloce*.»', 'scena', 'sorgenti/racconto/s2-strappo-volto-sfocato.mp4', 0.8),
    'reel-sera-1-aperitivo': ('Martedì, ore 19:05', 'Due tap *all\'aperitivo*.', 'scena', 'sorgenti/serate/dopo-le-19-4x5.mp4', 3.5),
    'reel-sera-2-tennis': ('Mercoledì, ore 19:40', 'Due tap *dopo il tennis*.', 'scena', 'sorgenti/serate/dopo-le-19-4x5.mp4', 10.7),
    'reel-sera-3-cena': ('Giovedì, ore 20:30', 'Due tap *prima di cena*.', 'scena', 'sorgenti/serate/dopo-le-19-4x5.mp4', 17.9),
    'reel-sera-4-divano': ('Venerdì, ore 21:15', 'Due tap *dal divano*.', 'scena', 'sorgenti/serate/dopo-le-19-4x5.mp4', 25.1),
}
LOGO = ("<svg width='46' height='46' viewBox='0 0 22 22'><circle cx='11' cy='11' r='9.5' fill='none' stroke='#D4FF3A' stroke-width='1.6'/>"
        "<path d='M11 1.5 A9.5 9.5 0 0 0 11 20.5 Z' fill='#D4FF3A'/></svg>")

def fotogramma(nome, tipo, src, t):
    f = W / f'{nome}.jpg'
    vf = f'crop={PW}:{PH}:{PX}:{PY}' if tipo == 'app' else 'null'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', str(ROOT / src), '-frames:v', '1', '-vf', vf, '-q:v', '2', str(f)], check=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(f.read_bytes()).decode()

def html(sopra, titolo, tipo, img):
    parti = titolo.split('*')
    tit = ''.join(f"<span style='color:#D4FF3A'>{p}</span>" if i % 2 else p for i, p in enumerate(parti))
    if tipo == 'app':
        box = (f"<div style='position:absolute;left:{(1080 - 508) // 2}px;top:620px;width:508px;height:1040px;border-radius:44px;overflow:hidden;"
               f"box-shadow:0 0 0 3px #2E2E34'><img src='{img}' style='width:100%;height:100%;object-fit:cover;object-position:top'></div>")
    else:
        pos = 'center top' if 'strappo' in img[:0] + sopra.lower() or sopra.startswith('La variante') else 'center'
        box = (f"<div style='position:absolute;left:90px;top:620px;width:900px;height:1040px;border-radius:44px;overflow:hidden'>"
               f"<img src='{img}' style='width:100%;height:100%;object-fit:cover;object-position:{pos}'></div>")
    return (f"<div style='position:absolute;inset:0;background:#0B0B0D'></div>"
            f"<div style='position:absolute;left:90px;top:300px;width:900px'>"
            f"<div style='display:flex;align-items:center;justify-content:space-between'>"
            f"<span style='font-size:32px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#D4FF3A'>{sopra}</span>{LOGO}</div>"
            f"<div class='b' style='font-size:96px;line-height:.98;letter-spacing:-.04em;margin-top:22px'>{tit}</div></div>{box}")

if __name__ == '__main__':
    voci = {n: html(s, ti, tp, fotogramma(n, tp, src, t)) for n, (s, ti, tp, src, t) in COPERTINE.items()}
    render_pngs(voci, W)
    for n in voci:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(W / f'{n}.png'), '-q:v', '2', str(OUT / f'{n}.jpg')], check=True)
        print(OUT / f'{n}.jpg')
