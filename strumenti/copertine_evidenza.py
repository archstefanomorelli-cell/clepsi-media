"""Copertine delle storie in evidenza (12/11): fondo nero, al centro un segno lime che regge il ritaglio a cerchio di Instagram.
Il nome della raccolta lo scrive Instagram sotto il cerchio. Uso: python3 strumenti/copertine_evidenza.py → evidenza/*.png (1080x1920)."""
import pathlib, sys, subprocess
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from reel_lib import render_pngs
import reel_quattro as q
OUT = pathlib.Path(__file__).resolve().parent.parent / 'evidenza'
L, N = q.LIME, q.NERO
def segno(interno):
    return (f"<div style='position:absolute;inset:0;background:{N}'></div>"
            f"<div style='position:absolute;left:240px;top:660px;width:600px;height:600px;border-radius:50%;border:6px solid #2E2E34;"
            f"display:flex;align-items:center;justify-content:center'>{interno}</div>")
DOC = (f"<svg width='230' height='290' viewBox='0 0 46 58'><path d='M4 2h26l12 12v42H4z' fill='none' stroke='{L}' stroke-width='3' stroke-linejoin='round'/>"
       f"<path d='M30 2v12h12' fill='none' stroke='{L}' stroke-width='3' stroke-linejoin='round'/>"
       f"<path d='M11 26h24M11 34h24M11 42h15' stroke='{L}' stroke-width='3' stroke-linecap='round'/></svg>")
VOCI = {
    'come-funziona': segno(q.LOGO.format(s=300, c=L)),
    'la-sera': segno(f"<span class='b' style='font-size:300px;letter-spacing:-.06em;color:{L};line-height:1'>19</span>"),
    'margini': segno(f"<span class='b' style='font-size:330px;color:{L};line-height:1;margin-top:-20px'>€</span>"),
    'parcella': segno(DOC),
}
render_pngs(VOCI, OUT)
for n in VOCI:   # PNG trasparenti → JPG pieni per Instagram
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(OUT / f'{n}.png'), '-vf', f'format=rgb24', '-q:v', '2', str(OUT / f'evidenza-{n}.jpg')], check=True)
    (OUT / f'{n}.png').unlink()
print(sorted(p.name for p in OUT.glob('*.jpg')))
