"""Serie "Niente": reel tipografici come l'intestazione della home di clepsi.it (fondo nero, NIENTE bianco, parole lime).

"NIENTE" fermo al centro, sotto le parole che salgono e cambiano con la fascia lime (stessa animazione del sito),
poi due tap nell'app vera e la chiusura con il titolo del sito.

Uso: python3 strumenti/reel_niente.py [episodio ...]      (senza argomenti: tutti)
Esce in lavoro/niente/<episodio>.mp4 e copertine/<episodio>.jpg (1080x1920). Serve sorgenti/app/domanda_c-*.mp4
(li crea strumenti/reel_app.py dalle registrazioni).
"""
import json, math, subprocess, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from reel_lib import render_pngs
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / 'sorgenti' / 'app'
AUD = ROOT / 'sorgenti' / 'audio'
W = ROOT / 'lavoro' / 'niente'; W.mkdir(parents=True, exist_ok=True)
FPS = 30
CREMA, INCH, LIME, NERO, BIANCO = '#F6F5F1', '#121214', '#D4FF3A', '#0B0B0D', '#F6F5F1'
PX, PY, PW, PH = 190, 398, 700, 1432

# episodi della serie: parole in ordine, l'ultima è la battuta e resta più a lungo
EPISODI = {
    'reel-niente-1-timer': {
        'parole': ['timer', 'timesheet', 'ore da segnare', 'fogli Excel', 'scuse'],
        'copertina': 'scuse',
    },
}
PASSO = 1.2          # secondi per parola
ULTIMA = 1.8         # la battuta finale
DISSOLVENZA = 0.35

# pezzi dell'app: (file, da, a) · tap mattina, cambio, tap pomeriggio, Fatto, schermata finale
PEZZI_APP = [('domanda_c-0', 0.2, 1.8), ('domanda_c-1', 0.6, 1.333), ('domanda_c-2', 0.2, 1.4), ('domanda_c-3', 0.0, 0.7), ('domanda_c-4', 0.0, 1.3)]
TOCCHI_APP = [('clepsi_tocco_mattina', 0.8), ('clepsi_tocco_pomeriggio', 1.6 + 0.733 + 0.4), ('clepsi_giornata_registrata', 1.6 + 0.733 + 1.2 + 0.55)]
CHIUSURA = 2.8

LOGO = ("<svg width='{s}' height='{s}' viewBox='0 0 22 22'><circle cx='11' cy='11' r='9.5' fill='none' stroke='{c}' stroke-width='{w}'/>"
        "<path d='M11 1.5 A9.5 9.5 0 0 0 11 20.5 Z' fill='{c}'/></svg>")

PAGINA = """<!doctype html><html lang='it'><head><meta charset='utf-8'><style>
html,body{margin:0}*{box-sizing:border-box}
body{width:1080px;height:1920px;position:relative;overflow:hidden;background:%(nero)s;color:%(bianco)s;font-family:'Bricolage Grotesque',sans-serif}
.niente{position:absolute;left:0;right:0;top:700px;text-align:center;font-weight:800;font-size:%(fs)spx;letter-spacing:.04em;text-transform:uppercase;line-height:1}
.giro{position:absolute;left:0;right:0;top:%(top2)spx;height:%(fs2h)spx;display:grid;place-items:center;overflow:hidden}
.parola{grid-area:1/1;white-space:nowrap;color:%(lime)s;font-weight:800;font-size:%(fs)spx;letter-spacing:.04em;text-transform:uppercase;line-height:1;will-change:transform,opacity}
.parola>span{position:relative;padding:0 8px;display:inline-block}
.parola>span>i{display:none;position:absolute;left:0;right:0;top:58%%;height:34%%;background:%(lime)s;transform-origin:left center;z-index:-1}
.parola>span{z-index:0;isolation:isolate}
.marchio{position:absolute;left:0;right:0;top:1400px;display:flex;justify-content:center;align-items:center;gap:18px;font-weight:800;font-size:52px;letter-spacing:-.03em}
</style></head><body>
<div class='niente'>Niente</div>
<div class='giro'>%(parole)s</div>
<div class='marchio'>%(logo)s<span>Clepsi</span></div>
</body></html>"""

def ease_out(p):  # simile a "ease" del sito
    p = min(1, max(0, p)); return 1 - (1 - p) ** 3

def stati(parole, t):
    """stato (opacità, spostamento in %, fascia 0-1) di ogni parola al tempo t"""
    out = []
    for i, _ in enumerate(parole):
        s = i * PASSO; e = s + PASSO if i < len(parole) - 1 else None
        if i == 0 and t < (e or 1e9):
            op, y, f = 1, 0, 1
        elif t < s:
            op, y, f = 0, 70, 0
        elif e is None or t < e:
            s2 = s + 0.12          # entra appena dopo che la precedente ha iniziato a uscire
            p = (t - s2) / 0.45
            op, y = min(1, max(0, (t - s2) / 0.35)), 70 * (1 - ease_out(p))
            f = ease_out((t - s2 - 0.2) / (0.5 if e is None else 0.35))
        else:
            p = (t - e) / 0.3
            op, y, f = max(0, 1 - (t - e) / 0.25), -70 * ease_out(p), 1
        out.append((op, y, f))
    return out

def misura_font(pg, parole):
    """dimensione del carattere tale che la parola più lunga stia in 940 px"""
    html = PAGINA % dict(nero=NERO, bianco=BIANCO, lime=LIME, fs=150, top2=860, fs2h=170, logo='', parole=''.join(
        f"<span class='parola'><span>{p}<i></i></span></span>" for p in parole))
    pg.set_content(html); pg.evaluate('document.fonts.ready')
    larg = max(pg.evaluate("[...document.querySelectorAll('.parola>span')].map(e=>e.getBoundingClientRect().width)"))
    return min(150, math.floor(150 * 1000 / larg))

def parte_parole(nome, parole):
    durata = PASSO * (len(parole) - 1) + ULTIMA
    cartella = W / f'{nome}-fotogrammi'; cartella.mkdir(exist_ok=True)
    for f in cartella.glob('*.png'): f.unlink()
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        fs = misura_font(pg, parole)
        top2 = 700 + int(fs * 1.12)
        html = PAGINA % dict(nero=NERO, bianco=BIANCO, lime=LIME, fs=fs, top2=top2, fs2h=int(fs * 1.3),
                             logo=LOGO.format(s=56, c=LIME, w=1.6),
                             parole=''.join(f"<span class='parola'><span>{w}<i></i></span></span>" for w in parole))
        pg.set_content(html); pg.evaluate('document.fonts.ready')
        n = round(durata * FPS)
        for k in range(n):
            st = stati(parole, k / FPS)
            pg.evaluate("s=>{const ps=[...document.querySelectorAll('.parola')];s.forEach(([o,y,f],i)=>{ps[i].style.opacity=o;ps[i].style.transform=`translateY(${y}%)`;ps[i].querySelector('i').style.transform=`scaleX(${f})`})}", st)
            pg.screenshot(path=str(cartella / f'{k:04d}.png'))
        b.close()
    out = W / f'{nome}-parole.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', str(cartella / '%04d.png'),
                    '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', str(out)], check=True)
    return out, durata

def parte_app(nome):
    pezzi = []
    for i, (f, a, b) in enumerate(PEZZI_APP):
        o = W / f'app-{i}.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(APP / f'{f}.mp4'), '-vf', f'trim={a}:{b},setpts=PTS-STARTPTS,fps={FPS}',
                        '-an', '-c:v', 'libx264', '-crf', '16', str(o)], check=True)
        pezzi.append(o)
    lista = W / 'app.txt'; lista.write_text(''.join(f"file '{p}'\n" for p in pezzi))
    tel = W / 'app-telefono.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lista), '-c', 'copy', str(tel)], check=True)
    durata = sum(b - a for _, a, b in PEZZI_APP)
    cornice = ("<svg width='1080' height='1920' style='position:absolute;inset:0'><defs><mask id='m'><rect width='1080' height='1920' fill='white'/>"
               f"<rect x='{PX}' y='{PY}' width='{PW}' height='{PH}' rx='54' fill='black'/></mask></defs>"
               f"<rect width='1080' height='1920' fill='{NERO}' mask='url(#m)'/>"
               f"<rect x='{PX - 3}' y='{PY - 3}' width='{PW + 6}' height='{PH + 6}' rx='57' fill='none' stroke='#2E2E34' stroke-width='3'/></svg>"
               f"<div style='position:absolute;left:0;right:0;top:{PY + PH + 26}px;text-align:center;font-size:24px;color:#8E8D96'>Studio e dati di esempio</div>"
               "<div style='position:absolute;left:0;right:0;top:118px;text-align:center'>"
               f"<div style='font-size:30px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:{LIME}'>Ogni sera alle 19</div>"
               "<div class='b' style='font-size:84px;line-height:1.02;letter-spacing:-.035em;margin-top:14px'>Solo due tap.</div></div>")
    render_pngs({'app-cornice': cornice}, W)
    out = W / 'app.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c={NERO[1:]}:s=1080x1920:r={FPS}:d={durata:.3f}', '-i', str(tel),
                    '-i', str(W / 'app-cornice.png'), '-filter_complex',
                    f'[0:v][1:v]overlay={PX}:{PY}:eof_action=pass[a];[a][2:v]overlay=0:0,format=yuv420p,setsar=1',
                    '-t', f'{durata:.3f}', '-c:v', 'libx264', '-crf', '16', str(out)], check=True)
    return out, durata

def parte_chiusura():
    html = (f"<div style='position:absolute;inset:0;background:{NERO}'></div>"
            "<div style='position:absolute;left:0;right:0;top:470px;display:flex;flex-direction:column;align-items:center;text-align:center'>"
            "<span class='b' style='font-size:112px;line-height:.98;letter-spacing:-.045em;width:940px'>Sai quanto ti rende ogni commessa.</span>"
            f"<span class='b' style='font-size:112px;line-height:.98;letter-spacing:-.045em;color:{LIME};margin-top:10px'>Mentre la fai.</span>"
            f"<div style='display:flex;align-items:center;gap:22px;margin-top:150px'>{LOGO.format(s=96, c=LIME, w=1.4)}"
            "<span class='b' style='font-size:88px;letter-spacing:-.04em'>Clepsi</span></div>"
            "<span style='font-size:40px;color:#A9A8B2;margin-top:26px'>clepsi.it</span></div>")
    render_pngs({'chiusura': html}, W)
    out = W / 'chiusura.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', str(FPS), '-t', str(CHIUSURA), '-i', str(W / 'chiusura.png'),
                    '-vf', 'format=yuv420p,setsar=1', '-c:v', 'libx264', '-crf', '16', str(out)], check=True)
    return out, CHIUSURA

def copertina(nome, parole, parola):
    """uguale al reel: NIENTE bianco, la parola finale lime, logo sotto (stessa dimensione dei caratteri del reel)"""
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        fs = misura_font(pg, parole)
        html = PAGINA % dict(nero=NERO, bianco=BIANCO, lime=LIME, fs=fs, top2=700 + int(fs * 1.12), fs2h=int(fs * 1.3),
                             logo=LOGO.format(s=56, c=LIME, w=1.6), parole=f"<span class='parola'><span>{parola}<i></i></span></span>")
        pg.set_content(html); pg.evaluate('document.fonts.ready')
        (ROOT / 'copertine').mkdir(exist_ok=True)
        pg.screenshot(path=str(W / f'cop-{nome}.png'))
        b.close()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(W / f'cop-{nome}.png'), '-q:v', '2', str(ROOT / 'copertine' / f'{nome}.jpg')], check=True)

def audio(nome, parole, inizio_app, totale):
    suoni = [('clepsi_tocco_mattina', i * PASSO, 0.45) for i in range(1, len(parole))]
    suoni += [(s, inizio_app + t, 1.0) for s, t in TOCCHI_APP]
    args = ['ffmpeg', '-v', 'error', '-y']
    for s, _, _ in suoni: args += ['-i', str(AUD / f'{s}.wav')]
    fc = ';'.join(f'[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(t * 1000)}|{int(t * 1000)}[s{i}]'
                  for i, (_, t, v) in enumerate(suoni))
    fc += ';' + ''.join(f'[s{i}]' for i in range(len(suoni))) + f'amix=inputs={len(suoni)}:normalize=0,apad,atrim=0:{totale:.3f},loudnorm=I=-16:TP=-1.5[a]'
    out = W / f'{nome}-audio.wav'
    subprocess.run(args + ['-filter_complex', fc, '-map', '[a]', '-ar', '48000', str(out)], check=True)
    return out

def monta(nome):
    ep = EPISODI[nome]
    a, da = parte_parole(nome, ep['parole'])
    b, db = parte_app(nome)
    c, dc = parte_chiusura()
    x1 = da - DISSOLVENZA
    x2 = x1 + db - DISSOLVENZA
    totale = x2 + dc
    aud = audio(nome, ep['parole'], x1, totale)
    out = W / f'{nome}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(a), '-i', str(b), '-i', str(c), '-i', str(aud), '-filter_complex',
                    f'[0:v]settb=AVTB,fps={FPS}[a];[1:v]settb=AVTB,fps={FPS}[b];[2:v]settb=AVTB,fps={FPS}[c];'
                    f'[a][b]xfade=transition=fade:duration={DISSOLVENZA}:offset={x1:.3f}[ab];'
                    f'[ab][c]xfade=transition=fade:duration={DISSOLVENZA}:offset={x2:.3f},format=yuv420p[v]',
                    '-map', '[v]', '-map', '3:a', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-r', str(FPS),
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', str(out)], check=True)
    copertina(nome, ep['parole'], ep['copertina'])
    print(out, round(totale, 2))

if __name__ == '__main__':
    for n in (sys.argv[1:] or list(EPISODI)):
        monta(n)
