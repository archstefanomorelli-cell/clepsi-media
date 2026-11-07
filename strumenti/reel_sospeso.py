"""Reel in sospeso (regola del 5/11 in PIANO.md): domanda in apertura, tensione che sale, rivelazione negli ultimi
2-3 secondi, ultimo fotogramma uguale al primo così il reel riparte in loop.

Uso: python3 strumenti/reel_sospeso.py [reel ...]      (senza argomenti: tutti)
Esce in lavoro/sospeso/<reel>.mp4 (1080x1920, 30 fps, solo i suoni dell'app: la musica la aggiunge Stefano).

Due tipi:
- 'scena': una clip del racconto (sorgenti/racconto/) rallentata, frase fissa in alto, contatore che avanza,
  rivelazione su fondo scurito. Clip generate con l'IA: su Instagram etichetta "creato con IA".
- 'app': carte coperte, pezzi dell'app vera (sorgenti/app/, Studio di esempio), rivelazione sulla schermata
  del titolare, carte scoperte alla fine.
"""
import subprocess, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from reel_lib import render_pngs, overlay

ROOT = pathlib.Path(__file__).resolve().parents[1]
R, APP, AUD = ROOT / 'sorgenti' / 'racconto', ROOT / 'sorgenti' / 'app', ROOT / 'sorgenti' / 'audio'
W = ROOT / 'lavoro' / 'sospeso'; W.mkdir(parents=True, exist_ok=True)
FPS, GANCIO, LOOP = 30, 1.6, 0.4
LIME, NERO, ROSSO = '#D4FF3A', '#0B0B0D', '#FF8A7A'
PX, PY, PW, PH = 190, 398, 700, 1432

REEL = {
    # lunedì 9/11 · È proprio così
    'reel-sospeso-1-cantiere': {
        'tipo': 'scena', 'clip': ('s3-porta.mp4', 0, 5.79, 640), 'lento': 2.0,
        'gancio': '*«Passo un attimo»* in cantiere.',
        'passi': [('14:00', 'parto'), ('14:50', 'arrivo'), ('15:40', '«due parole» con l’impresa'), ('17:10', 'si riparte'), ('18:30', 'di nuovo in studio')],
        'passo': 2.0, 'rivela': ('Mezza giornata.', 'Su nessuna commessa.', 'Esempio con tempi tipici.'), 'rivela_d': 2.8,
    },
    # mercoledì 11/11 · È proprio così
    'reel-sospeso-2-modifica': {
        'tipo': 'scena', 'clip': ('s6-tavole.mp4', 0.12, 5.88, 560), 'lento': 2.0,
        'gancio': 'Il cliente: *«è solo una piccola modifica»*.',
        'passi': [('1', 'lunedì sera · mezza giornata'), ('2', 'martedì sera · mezze giornate'), ('3', 'mercoledì sera · mezze giornate')],
        'passo': 2.6, 'rivela': ('480 € di lavoro.', 'Fatturati: 0 €.', 'Esempio: 320 € a giornata.'), 'rivela_d': 3.4,
    },
    # venerdì 13/11 · Due tap
    'reel-sospeso-3-quale': {
        'tipo': 'app',
        'gancio': 'Una di queste quattro commesse è *in perdita*. Quale?',
    },
}

def tit(t):
    p = t.split('*')
    return ''.join(f"<span style='color:{LIME}'>{x}</span>" if i % 2 else x for i, x in enumerate(p))

def png_gancio(testo, top=560, size=120):
    return ("<div style='position:absolute;inset:0;background:rgba(11,11,13,.86)'></div>"
            f"<div class='b' style='position:absolute;left:80px;top:{top}px;width:920px;font-size:{size}px;line-height:.98;letter-spacing:-.045em'>{tit(testo)}</div>")

def suoni_wav(nome, suoni, tot):
    aud = W / f'{nome}-audio.wav'
    args = ['ffmpeg', '-v', 'error', '-y']
    for s, _, _ in suoni: args += ['-i', str(AUD / f'{s}.wav')]
    fc = ';'.join(f'[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(t * 1000)}|{int(t * 1000)}[s{i}]'
                  for i, (_, t, v) in enumerate(suoni))
    fc += ';' + ''.join(f'[s{i}]' for i in range(len(suoni))) + f'amix=inputs={len(suoni)}:normalize=0,apad,atrim=0:{tot:.3f},loudnorm=I=-16:TP=-1.5[a]'
    subprocess.run(args + ['-filter_complex', fc, '-map', '[a]', '-ar', '48000', str(aud)], check=True)
    return aud

def scena(nome, r):
    f, a, b, x = r['clip']
    n = len(r['passi'])
    t_riv = GANCIO + n * r['passo']
    tot = t_riv + r['rivela_d'] + LOOP
    raw = W / f'{nome}-raw.mp4'
    vf = (f"trim={a}:{b},setpts=(PTS-STARTPTS)*{r['lento']},crop=608:1080:{x}:0,scale=1080:1920:flags=lanczos,"
          f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,tpad=stop_mode=clone:stop_duration=10,trim=0:{tot:.3f},format=yuv420p,setsar=1")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(R / f), '-vf', vf, '-an', '-c:v', 'libx264', '-crf', '16', str(raw)], check=True)
    alto = ("<div style='position:absolute;inset:0 0 auto 0;height:760px;background:linear-gradient(rgba(11,11,13,.82),rgba(11,11,13,0))'></div>"
            f"<div class='b' style='position:absolute;left:80px;top:200px;width:920px;font-size:84px;line-height:1;letter-spacing:-.04em;text-shadow:0 2px 24px rgba(0,0,0,.4)'>{tit(r['gancio'])}</div>")
    basso = "<div style='position:absolute;inset:auto 0 0 0;height:1150px;background:linear-gradient(rgba(11,11,13,0),rgba(11,11,13,.72) 50%,rgba(11,11,13,.8))'></div>"
    def passo(num, label):
        return (f"<div class='b' style='position:absolute;left:80px;top:1060px;width:920px;font-size:260px;line-height:.85;letter-spacing:-.05em;color:{LIME}'>{num}</div>"
                f"<div style='position:absolute;left:84px;top:1310px;width:900px;font-size:56px;font-weight:700;line-height:1.15'>{label}</div>")
    u1, u2, nota = r['rivela']
    riv = ("<div style='position:absolute;inset:0;background:rgba(11,11,13,.88)'></div>"
           f"<div style='position:absolute;left:80px;top:640px;width:920px;display:flex;flex-direction:column;gap:18px'>"
           f"<span class='b' style='font-size:124px;line-height:.96;letter-spacing:-.045em'>{u1}</span>"
           f"<span class='b' style='font-size:124px;line-height:.96;letter-spacing:-.045em;color:{LIME}'>{u2}</span>"
           f"<span style='font-size:36px;color:#A9A8B2;margin-top:40px'>{nota}</span></div>")
    items = {f'{nome}-g': png_gancio(r['gancio']), f'{nome}-alto': alto, f'{nome}-basso': basso, f'{nome}-riv': riv,
             **{f'{nome}-p{i}': passo(*p) for i, p in enumerate(r['passi'])}}
    render_pngs(items, W / 'png'); P = lambda k: str(W / 'png' / f'{nome}-{k}.png')
    ovs = [(P('g'), 0, GANCIO, 0, 0.25), (P('alto'), GANCIO - 0.25, t_riv, 0.25, 0.3), (P('basso'), GANCIO - 0.25, t_riv, 0.3, 0.3)]
    for i in range(n):
        s = GANCIO + i * r['passo']
        ovs.append((P(f'p{i}'), s, s + r['passo'], 0.2 if i else 0.3, 0.15))
    ovs += [(P('riv'), t_riv, tot - LOOP, 0.35, 0), (P('g'), tot - LOOP, tot, 0.15, 0)]
    suoni = [('clepsi_tocco_mattina', GANCIO + i * r['passo'], 0.6) for i in range(n)] + [('clepsi_giornata_registrata', t_riv + 0.1, 0.9)]
    out = W / f'{nome}.mp4'
    overlay(str(raw), ovs, str(out), audio=str(suoni_wav(nome, suoni, tot)))
    return out, tot

# pezzi dell'app: (file, da, a)
DOMANDA = [('domanda_c-0', 0.2, 1.8), ('domanda_c-1', 0.6, 1.333), ('domanda_c-2', 0.2, 1.4), ('domanda_c-3', 0.0, 0.7), ('domanda_c-4', 0.0, 1.3)]
TOCCHI_D = [('clepsi_tocco_mattina', 0.8), ('clepsi_tocco_pomeriggio', 1.6 + 0.733 + 0.4), ('clepsi_giornata_registrata', 1.6 + 0.733 + 1.2 + 0.55)]
TITOLARE = [('titolare_g-0', 0.0, 2.5), ('titolare_g-1', 0.0, 1.8)]
COMMESSE = [('Villa Rossi', '#D4FF3A', 'In attivo', '#D4FF3A'), ('Scuola Brera', '#9B8CFF', 'Margine stretto', '#FFC46B'),
            ('Uffici Lambrate', '#6FD3FF', 'In perdita', ROSSO), ('Loft Navigli', '#FF9ECF', 'Appena iniziata', '#C9C8D0')]

def carte(top, scoperta=None):
    h = ''
    for i, (n, c, st, sc) in enumerate(COMMESSE):
        y = top + i * 150
        if scoperta == n:
            dx = f"<span style='padding:10px 22px;border-radius:30px;background:{sc};color:{NERO};font-size:30px;font-weight:800'>{st}</span>"
            bg, bd = '#1d1d22', f'3px solid {sc}'
        else:
            dx = "<span class='b' style='font-size:52px;color:#55545C'>?</span>"
            bg, bd = '#16161a', '3px solid #2E2E34'
        h += (f"<div style='position:absolute;left:80px;top:{y}px;width:920px;height:124px;border-radius:30px;background:{bg};border:{bd};"
              f"display:flex;align-items:center;justify-content:space-between;padding:0 34px'>"
              f"<span style='display:flex;align-items:center;gap:22px;font-size:44px;font-weight:700'><i style='width:22px;height:22px;border-radius:50%;background:{c}'></i>{n}</span>{dx}</div>")
    return h

def app(nome, r):
    pezzi, durate = [], {}
    for gruppo, lista in (('d', DOMANDA), ('t', TITOLARE)):
        tot = 0
        for i, (f, a, b) in enumerate(lista):
            o = W / f'{nome}-{gruppo}{i}.mp4'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(APP / f'{f}.mp4'), '-vf', f'trim={a}:{b},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p,setsar=1',
                            '-an', '-c:v', 'libx264', '-crf', '16', str(o)], check=True)
            pezzi.append(o); tot += b - a
        durate[gruppo] = tot
    lista = W / f'{nome}.txt'; lista.write_text(''.join(f"file '{p}'\n" for p in pezzi))
    tel = W / f'{nome}-telefono.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lista), '-c', 'copy', str(tel)], check=True)
    t_tel, FINE = GANCIO, 2.0
    t_tit = t_tel + durate['d']; t_fine = t_tit + durate['t']; tot = t_fine + FINE
    base = W / f'{nome}-base.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c=0x0B0B0D:s=1080x1920:r={FPS}:d={tot:.3f}', '-itsoffset', f'{t_tel}', '-i', str(tel),
                    '-filter_complex', f'[0:v][1:v]overlay={PX}:{PY}:eof_action=pass,format=yuv420p,setsar=1', '-t', f'{tot:.3f}',
                    '-c:v', 'libx264', '-crf', '16', str(base)], check=True)
    cornice = ("<svg width='1080' height='1920' style='position:absolute;inset:0'><defs><mask id='m'><rect width='1080' height='1920' fill='white'/>"
               f"<rect x='{PX}' y='{PY}' width='{PW}' height='{PH}' rx='54' fill='black'/></mask></defs>"
               "<rect width='1080' height='1920' fill='#0B0B0D' mask='url(#m)'/>"
               f"<rect x='{PX - 3}' y='{PY - 3}' width='{PW + 6}' height='{PH + 6}' rx='57' fill='none' stroke='#2E2E34' stroke-width='3'/></svg>"
               f"<div style='position:absolute;left:0;right:0;top:{PY + PH + 26}px;text-align:center;font-size:24px;color:#8E8D96'>Studio e dati di esempio</div>")
    def did(sopra, titolo):
        return (f"<div style='position:absolute;left:80px;top:118px;width:920px'>"
                f"<div style='font-size:30px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:{LIME}'>{sopra}</div>"
                f"<div class='b' style='font-size:66px;line-height:1.02;letter-spacing:-.035em;margin-top:14px'>{tit(titolo)}</div></div>")
    LOGO = (f"<svg width='72' height='72' viewBox='0 0 22 22'><circle cx='11' cy='11' r='9.5' fill='none' stroke='{LIME}' stroke-width='1.5'/>"
            f"<path d='M11 1.5 A9.5 9.5 0 0 0 11 20.5 Z' fill='{LIME}'/></svg>")
    g = (f"<div style='position:absolute;inset:0;background:{NERO}'></div>"
         f"<div class='b' style='position:absolute;left:80px;top:300px;width:920px;font-size:104px;line-height:.98;letter-spacing:-.045em'>{tit(r['gancio'])}</div>"
         + carte(1000))
    fine = (f"<div style='position:absolute;inset:0;background:{NERO}'></div>"
            f"<div class='b' style='position:absolute;left:80px;top:300px;width:920px;font-size:104px;line-height:.98;letter-spacing:-.045em'>Ogni sera<br><span style='color:{LIME}'>due tap.</span></div>"
            + carte(1000, scoperta='Uffici Lambrate')
            + f"<div style='position:absolute;left:0;right:0;top:1640px;display:flex;justify-content:center;align-items:center;gap:20px'>{LOGO}"
              "<span class='b' style='font-size:64px;letter-spacing:-.04em'>Clepsi</span><span style='font-size:36px;color:#A9A8B2;margin-left:16px'>clepsi.it</span></div>")
    items = {f'{nome}-g': g, f'{nome}-fine': fine, f'{nome}-cornice': cornice,
             f'{nome}-d1': did('Indizio', 'Lo dicono le sere: *due tap alle 19.*'),
             f'{nome}-d2': did('La mattina dopo', 'Uffici Lambrate: *−667 €.* E c’è ancora tempo.')}
    render_pngs(items, W / 'png'); P = lambda k: str(W / 'png' / f'{nome}-{k}.png')
    ovs = [(P('cornice'), t_tel - 0.3, t_fine + 0.3, 0, 0), (P('d1'), t_tel, t_tit, 0.3, 0.25), (P('d2'), t_tit, t_fine + 0.3, 0.3, 0),
           (P('g'), 0, t_tel, 0, 0.3), (P('fine'), t_fine, tot - LOOP, 0.35, 0.3), (P('g'), tot - LOOP, tot, 0.3, 0)]
    suoni = [(s, t_tel + t, 1.0) for s, t in TOCCHI_D] + [('clepsi_notifica', t_tit + 0.2, 0.7)]
    out = W / f'{nome}.mp4'
    overlay(str(base), ovs, str(out), audio=str(suoni_wav(nome, suoni, tot)))
    return out, tot

if __name__ == '__main__':
    for n in (sys.argv[1:] or list(REEL)):
        r = REEL[n]
        out, tot = (scena if r['tipo'] == 'scena' else app)(n, r)
        print(out, round(tot, 2))
