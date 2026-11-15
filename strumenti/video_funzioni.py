"""Video delle pagine "funzioni" del sito (clepsi.it/funzioni/…), 15/11/2026.

Stesso stile dei reel dell'app (fondo nero, titolo su due righe bianco + lime con il contatore, l'app vera dentro
una finestra arrotondata, puntatore e tocchi visibili, dissolvenze), negli stessi formati del video della home:
1080x1080 (computer) e 864x1080 (telefono, 4:5). Niente audio: sul sito i video partono muti.

Le riprese sono fatte fotogramma per fotogramma con strumenti/registra/ (riprese_f_<pagina>.js, finto backend in
locale con lo studio di esempio del sito): l'app in modalità desktop (1280 px), tranne "senza timesheet" (telefono).
Una "camera" inquadra un rettangolo della schermata (eventi 'vista' di desk.js) e lo porta a riempire la finestra.

Uso: node strumenti/registra/riprese_f_<pagina>.js lavoro/funzioni/<pagina>/riprese   (build dell'app su :8765)
     python3 strumenti/video_funzioni.py <pagina>
Esce in lavoro/funzioni/<pagina>/ : <pagina>-1x1.mp4, <pagina>-4x5.mp4 e i poster .jpg
"""
import subprocess, sys, pathlib, json, base64
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
FPS = 30
LIME, NERO = '#D4FF3A', '#0B0B0D'
CHIUSURA, ENTRA = 2.8, 0.35
LOGO = ("<svg width='{s}' height='{s}' viewBox='0 0 22 22'><circle cx='11' cy='11' r='9.5' fill='none' stroke='{c}' stroke-width='1.5'/>"
        "<path d='M11 1.5 A9.5 9.5 0 0 0 11 20.5 Z' fill='{c}'/></svg>")

# i sei video: titoli dei passaggi (segni p1..pN della ripresa), frase di chiusura, secondo del poster
VIDEO = {
    'previsione-margine-commessa': dict(viewport=(1280, 960), titoli=[
        ('Come chiuderà ogni commessa?', 'Lo vedi ogni mattina.'),
        ('Margine stretto?', 'Sai quale fase sfora.'),
        ('Una commessa in perdita?', 'Lo sai quando c’è tempo.'),
        ('Giornate usate e lavoro fatto.', 'La previsione si ricalcola.')],
        chiusura=('Il margine,', 'prima della fine.'), poster=1.6),
    'budget-commessa-giornate': dict(viewport=(1280, 1200), titoli=[
        ('18.000 € di compenso?', 'Diventano giornate.'),
        ('Vuoi tenere più margine?', 'Le giornate si ricalcolano.'),
        ('Fase per fase,', 'vedi quando sfora.')],
        chiusura=('Il compenso,', 'in giornate.'), poster=11.8),
    'varianti-commessa': dict(viewport=(1280, 960), titoli=[
        ('Venerdì, un minuto:', 'a che punto è la commessa?'),
        ('Lavoro in più del cliente?', 'Lo segni qui.'),
        ('Ha un valore.', 'Da chiedere al cliente.')],
        chiusura=('Il lavoro in più,', 'da far pagare.'), poster=7.2),
    'settimana-studio': dict(viewport=(1280, 960), titoli=[
        ('Chi ha lavorato su cosa?', 'In una griglia.'),
        ('Quale commessa pesa di più?', 'Lo vedi in un attimo.'),
        ('Una risposta sbagliata?', 'La correggi con un clic.')],
        chiusura=('La settimana', 'dello studio.'), poster=2.0),
    'bilancio-commessa': dict(viewport=(1280, 960), titoli=[
        ('Commessa finita?', 'La chiudi.'),
        ('Quanto rende ogni giornata?', 'Il bilancio è pronto.'),
        ('Il prossimo preventivo?', 'Lo fai sui numeri.')],
        chiusura=('Quanto ti ha reso', 'ogni giornata.'), poster=9.0),
    'senza-timesheet': dict(viewport=(414, 847), telefono=True, titoli=[
        ('Alle 19,', 'una domanda sola.'),
        ('Mattina e pomeriggio.', 'Due tap.'),
        ('Dieci secondi.', 'Niente ore da segnare.'),
        ('Ti sei dimenticato?', 'Promemoria alle 21.')],
        chiusura=('Niente timesheet.', 'Due tap la sera.'), poster=3.4),
}

# formati come il video della home: finestra (x, y, w, h), titolo (x, y, larghezza, corpo)
FORMATI = {
    '1x1': dict(W=1080, H=1080, win=(60, 290, 960, 730), tit=(60, 52, 960, 60)),
    '4x5': dict(W=864, H=1080, win=(48, 262, 768, 770), tit=(48, 46, 768, 52)),
}
FORMATI_TEL = {
    '1x1': dict(W=1080, H=1080, win=(566, 50, 482, 980), tit=(64, 360, 460, 66)),
    '4x5': dict(W=864, H=1080, win=(254, 236, 380, 794), tit=(48, 46, 768, 52)),
}

def ease(t):
    return 4 * t * t * t if t < .5 else 1 - (-2 * t + 2) ** 3 / 2

def render(items, outdir, W, H):
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': W, 'height': H})
        for name, body in items.items():
            pg.set_content(f"<!doctype html><html lang='it'><head><meta charset='utf-8'><style>html,body{{margin:0;background:transparent}}*{{box-sizing:border-box}}"
                           f"body{{width:{W}px;height:{H}px;position:relative;font-family:'DM Sans',sans-serif;color:#F6F5F1}}"
                           ".b{font-family:'Bricolage Grotesque',sans-serif;font-weight:800}</style></head><body>" + body + "</body></html>")
            pg.evaluate('document.fonts.ready')
            pg.screenshot(path=str(outdir / f'{name}.png'), omit_background=True)
        b.close()

def titolo(F, i, n, d, r, tel):
    x, y, w, s = F['tit']
    pill = f'{i} / {n}'
    return (f"<div style='position:absolute;left:{x}px;top:{y}px;width:{w}px'>"
            f"<span style='display:inline-block;font-size:{round(s * .36)}px;font-weight:700;letter-spacing:.12em;color:{LIME};border:2px solid {LIME};"
            f"border-radius:999px;padding:5px 14px'>{pill}</span>"
            f"<div class='b' style='font-size:{s}px;line-height:1.02;letter-spacing:-.04em;margin-top:{round(s * .32)}px'>{d}<br>"
            f"<span style='color:{LIME}'>{r}</span></div></div>")

def cornice(F):
    W, H = F['W'], F['H']; x, y, w, h = F['win']; rr = 34 if w > 600 else 40
    return (f"<svg width='{W}' height='{H}' style='position:absolute;inset:0'><defs><mask id='m'><rect width='{W}' height='{H}' fill='white'/>"
            f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rr}' fill='black'/></mask></defs>"
            f"<rect width='{W}' height='{H}' fill='{NERO}' mask='url(#m)'/>"
            f"<rect x='{x - 2}' y='{y - 2}' width='{w + 4}' height='{h + 4}' rx='{rr + 2}' fill='none' stroke='#2E2E34' stroke-width='3'/></svg>")

def chiusura(F, a, b):
    W, H = F['W'], F['H']; s = round(W * .105)
    return (f"<div style='position:absolute;inset:0;background:{NERO}'></div>"
            f"<div style='position:absolute;left:0;right:0;top:0;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center'>"
            f"{LOGO.format(s=round(W * .1), c=LIME)}"
            f"<div class='b' style='font-size:{s}px;line-height:.98;letter-spacing:-.045em;margin-top:{round(H * .04)}px'>{a}<br><span style='color:{LIME}'>{b}</span></div>"
            f"<div style='margin-top:{round(H * .05)}px;background:{LIME};color:{NERO};font-weight:700;font-size:{round(W * .034)}px;padding:{round(W * .018)}px {round(W * .045)}px;border-radius:999px'>Prova l'app gratis</div>"
            f"<div style='font-size:{round(W * .026)}px;color:#A9A8B2;margin-top:{round(H * .022)}px'>clepsi.it · Studio e dati di esempio</div></div>")

def main(nome):
    cfg = VIDEO[nome]; tel = cfg.get('telefono', False); FMT = FORMATI_TEL if tel else FORMATI
    W_ = ROOT / 'lavoro' / 'funzioni' / nome; d = W_ / 'riprese' / 'unica'
    ev = json.loads((d / 'eventi.json').read_text()); fot = sorted(d.glob('*.jpg'))
    VW, VH = cfg['viewport']; K = Image.open(fot[0]).size[0] / VW            # 2 se ripreso a 2x
    passaggi = {e['f']: e for e in ev['eventi'] if e['tipo'] == 'passaggio'}
    segni = {e['nome']: e['f'] for e in ev['eventi'] if e['tipo'] == 'segno'}
    # 1) scaletta: fotogrammi della ripresa, con le dissolvenze in mezzo
    voci, mappa, k = [], {}, 0
    for i in range(len(fot)):
        if i in passaggi and i > 0:
            n = round(passaggi[i]['durata'] * FPS); voci.append(('tr', i, n)); k += n
        mappa[i] = k; voci.append(('f', i, 0)); k += 1
    tot_f = k
    inizio = {i: mappa[i] - (round(passaggi[i]['durata'] * FPS) if i in passaggi and i > 0 else 0) for i in mappa}
    # 2) camera: (x, y, w) del rettangolo da inquadrare, in px css, interpolato con accelerazione morbida
    # la vista è pensata per il 1x1; negli altri formati stessa altezza (stesso zoom) e stesso bordo sinistro
    # ('ancora' = 'l', il testo dell'app è allineato a sinistra) oppure stesso centro ('c')
    A1 = FMT['1x1']['win'][2] / FMT['1x1']['win'][3]
    viste = sorted((inizio.get(e['f'], tot_f - 1), e['x'], e['y'], e['w'], e['durata'], e.get('ancora', 'l')) for e in ev['eventi'] if e['tipo'] == 'vista')
    if not viste: viste = [(0, VW / 2, VH / 2, VW, 0.01, 'c')]
    cams = {}
    for f, F in FMT.items():
        af = F['win'][2] / F['win'][3]; cam = [None] * tot_f
        for j, (a, x, y, w, dur, an) in enumerate(viste):
            wf = w / A1 * af; xf = x - w / 2 + wf / 2 if an == 'l' else x
            n = max(1, round(dur * FPS)); b = viste[j + 1][0] if j + 1 < len(viste) else tot_f
            da = cam[a - 1] if a > 0 and cam[a - 1] else (xf, y, wf)
            for t in range(a, b):
                e = ease(min(1, (t - a + 1) / n)); cam[t] = tuple(da[q] + ((xf, y, wf)[q] - da[q]) * e for q in range(3))
        for t in range(tot_f):
            if cam[t] is None: cam[t] = cam[t - 1] if t else cam[next(i for i in range(tot_f) if cam[i])]
        cams[f] = cam
    def rett(t, F):
        f = next(k for k, v in FMT.items() if v is F)
        x, y, w = cams[f][t]; a = F['win'][2] / F['win'][3]
        h = w / a
        if h > VH: h = VH; w = h * a
        if w > VW: w = VW; h = w / a
        x = min(max(x, w / 2), VW - w / 2); y = min(max(y, h / 2), VH - h / 2)
        return (K * (x - w / 2), K * (y - h / 2), K * (x + w / 2), K * (y + h / 2))
    out = {}
    for f, F in FMT.items():
        T = W_ / f'fin-{f}'; T.mkdir(exist_ok=True)
        for x in T.glob('*.jpg'): x.unlink()
        out[f] = T
    # 3) fotogrammi della finestra, per i due formati in una passata
    k, prima = 0, None
    def scrivi(im, t):
        for f, F in FMT.items():
            ww, hh = F['win'][2], F['win'][3]
            im.resize((ww, hh), Image.LANCZOS, box=rett(t, F)).save(out[f] / f'{t:05d}.jpg', quality=93)
    for tipo, i, n in voci:
        im = Image.open(fot[i]).convert('RGB')
        if tipo == 'tr':
            for j in range(1, n + 1):
                e = ease(j / (n + 1))
                for f, F in FMT.items():
                    ww, hh = F['win'][2], F['win'][3]; bx = rett(k, F)
                    Image.blend(prima.resize((ww, hh), Image.LANCZOS, box=bx), im.resize((ww, hh), Image.LANCZOS, box=bx), e).save(out[f] / f'{k:05d}.jpg', quality=93)
                k += 1
        else:
            scrivi(im, k); k += 1; prima = im
    durata = k / FPS; tot = durata + CHIUSURA
    inizi = [mappa[segni[f'p{j + 1}']] / FPS for j in range(len(cfg['titoli']))]
    for f, F in FMT.items():
        W, H = F['W'], F['H']; x, y, w, h = F['win']
        win = W_ / f'finestra-{f}.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', str(out[f] / '%05d.jpg'),
                        '-vf', f'fade=t=in:st=0:d={ENTRA},fade=t=out:st={durata - ENTRA:.3f}:d={ENTRA},format=yuv420p',
                        '-c:v', 'libx264', '-crf', '14', str(win)], check=True)
        items = {f'cornice-{f}': cornice(F), f'chiusura-{f}': chiusura(F, *cfg['chiusura'])}
        for j, (a, b) in enumerate(cfg['titoli']): items[f't{j}-{f}'] = titolo(F, j + 1, len(cfg['titoli']), a, b, tel)
        render(items, W_, W, H)
        P = lambda n: str(W_ / f'{n}-{f}.png')
        ovs = [(P('cornice'), 0, durata, ENTRA, ENTRA)]
        for j in range(len(cfg['titoli'])):
            a = inizi[j]; b = inizi[j + 1] if j + 1 < len(cfg['titoli']) else durata
            ovs.append((P(f't{j}'), a, b, ENTRA if j == 0 else 0.3, ENTRA if j == len(cfg['titoli']) - 1 else 0.25))
        ovs.append((P('chiusura'), durata, tot, 0.45, 0.3))
        args = ['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c={NERO[1:]}:s={W}x{H}:r={FPS}:d={tot:.3f}', '-i', str(win)]
        for png, s, e, fi, fo in ovs: args += ['-loop', '1', '-t', f'{e - s:.3f}', '-i', png]
        fc = [f'[0:v][1:v]overlay={x}:{y}:eof_action=pass[b0]']; last = 'b0'
        for q, (png, s, e, fi, fo) in enumerate(ovs):
            dd = e - s; flt = 'format=rgba'
            if fi > 0: flt += f',fade=t=in:st=0:d={fi}:alpha=1'
            if fo > 0: flt += f',fade=t=out:st={max(0, dd - fo):.3f}:d={fo}:alpha=1'
            fc.append(f'[{q + 2}:v]{flt},setpts=PTS-STARTPTS+{s:.3f}/TB[o{q}]')
            fc.append(f"[{last}][o{q}]overlay=0:0:eof_action=pass:enable='between(t,{s:.3f},{e:.3f})'[v{q}]"); last = f'v{q}'
        mp4 = W_ / f'{nome}-{f}.mp4'
        args += ['-filter_complex', ';'.join(fc), '-map', f'[{last}]', '-t', f'{tot:.3f}', '-c:v', 'libx264', '-crf', '21', '-preset', 'slow',
                 '-pix_fmt', 'yuv420p', '-r', str(FPS), '-movflags', '+faststart', '-an', str(mp4)]
        subprocess.run(args, check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{cfg['poster']:.2f}", '-i', str(mp4), '-frames:v', '1', '-q:v', '3',
                        str(W_ / f'{nome}-{f}-poster.jpg')], check=True)
        print(mp4, round(tot, 2), 's')

if __name__ == '__main__':
    main(sys.argv[1])
