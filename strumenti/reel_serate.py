import subprocess, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from reel_lib import render_pngs, overlay, LOGO
ROOT = pathlib.Path(__file__).resolve().parents[1]
W = ROOT / 'lavoro' / 'reel' / 'serate'; W.mkdir(parents=True, exist_ok=True)
AUD = ROOT / 'sorgenti' / 'audio'
V169 = ROOT / 'sorgenti/serate/dopo-le-19-16x9.mp4'
COL = {'Villa Rossi': '#D4FF3A', 'Scuola Brera': '#9B8CFF', 'Uffici Lambrate': '#6FD3FF', 'Loft Navigli': '#FF9ECF'}
BASE = {'Villa Rossi': 18.0, 'Scuola Brera': 11.5, 'Uffici Lambrate': 9.0, 'Loft Navigli': 3.0}
GIORNI = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì']
PRIMA = [('Villa Rossi', 'Villa Rossi'), ('Scuola Brera', 'Uffici Lambrate'), ('Villa Rossi', 'Loft Navigli'), ('Scuola Brera', 'Scuola Brera')]
SERE = [  # slug, ora, dove, am, pm, tm, crop x, giorno
    ('aperitivo', '19:05', 'Un aperitivo con gli amici', 'Villa Rossi', 'Scuola Brera', [1.1, 3.7, 4.7, 5.1, 6.3], 656, 1),
    ('tennis', '19:40', 'Lo spogliatoio dopo il tennis', 'Scuola Brera', 'Villa Rossi', [1.4, 4.35, 5.6, 6.1, 6.6], 700, 2),
    ('cena', '20:30', 'Una cena in famiglia', 'Villa Rossi', 'Uffici Lambrate', [1.1, 3.65, 4.6, 5.3, 6.6], 720, 3),
    ('divano', '21:15', 'Una serie sul divano', 'Villa Rossi', 'Loft Navigli', [0.55, 3.1, 4.1, 4.6, 5.5], 836, 4)]
STEP = 7.2; XF = 0.6; TAB = 4.6; BR = 3.4
num = lambda v: (f'{v:.1f}'.replace('.', ',')).replace(',0', '')
def tile(lbl, val, on, col):
    bg = col if on else '#26262C'; fg = '#0B0B0D' if on else '#8E8D96'
    return f"<span style='flex:1 1 0;display:flex;flex-direction:column;gap:6px;padding:24px 26px;border-radius:28px;background:{bg};color:{fg}'><span style='font-size:22px;font-weight:700;letter-spacing:.08em;text-transform:uppercase'>{lbl}</span><span class='b' style='font-size:38px;white-space:nowrap'>{val}</span></span>"
def card(ora, am, pm, st):
    reg = 'visible' if st >= 3 else 'hidden'
    return (f"<div style='position:absolute;left:70px;top:560px;width:820px;border-radius:52px;background:rgba(18,18,20,.94);padding:44px;display:flex;flex-direction:column;gap:28px;box-shadow:0 30px 80px rgba(0,0,0,.45)'>"
            f"<span style='display:flex;align-items:center;justify-content:space-between;font-size:32px;color:#D8D7DE'><span style='display:flex;align-items:center;gap:16px'>{LOGO('#D4FF3A').replace('44','36')}Com'è andata oggi?</span><span class='b' style='font-weight:700;color:#D4FF3A'>{ora}</span></span>"
            f"<div style='display:flex;gap:18px'>{tile('Mattina', am, st >= 1, COL[am])}{tile('Pomeriggio', pm, st >= 2, COL[pm])}</div>"
            f"<span class='b' style='visibility:{reg};display:flex;align-items:center;gap:12px;font-weight:700;font-size:32px;color:#D4FF3A'><svg width='34' height='34' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'><path d='M5 12.5l4.5 4.5L19 7.5'/></svg>Giornata registrata</span></div>")
def cella(nome, nuovo=False):
    if not nome: return "<span style='flex:1 1 0;height:92px;border-radius:22px;border:2px dashed #3A3A42'></span>"
    ring = 'box-shadow:0 0 0 4px #F6F5F1;' if nuovo else ''
    return f"<span class='b' style='flex:1 1 0;height:92px;border-radius:22px;background:{COL[nome]};color:#0B0B0D;font-size:32px;display:flex;align-items:center;padding:0 24px;white-space:nowrap;{ring}'>{nome}</span>"
def tabella(giorno, ora, am, pm, st):
    rows = ''
    for g in range(5):
        if g < giorno: c1, c2, n1, n2 = PRIMA[g][0], PRIMA[g][1], False, False
        elif g == giorno: c1, c2, n1, n2 = (am if st >= 1 else None), (pm if st >= 2 else None), st == 1, st == 2
        else: c1 = c2 = None; n1 = n2 = False
        lc = '#D4FF3A' if g == giorno else '#A9A8B2'
        rows += f"<div style='display:flex;align-items:center;gap:18px'><span style='width:170px;font-size:32px;font-weight:700;color:{lc}'>{GIORNI[g][:3]}</span>{cella(c1, n1)}{cella(c2, n2)}</div>"
    tot = dict(BASE)
    for g in range(giorno): tot[PRIMA[g][0]] += .5; tot[PRIMA[g][1]] += .5
    agg = {}
    if st >= 1: tot[am] += .5; agg[am] = True
    if st >= 2: tot[pm] += .5; agg[pm] = True
    tl = ''
    for n, v in tot.items():
        hi = n in agg
        tl += (f"<div style='display:flex;align-items:center;gap:20px;padding:20px 0;border-bottom:2px solid #24242A'><span style='width:14px;height:44px;border-radius:7px;background:{COL[n]}'></span>"
               f"<span class='b' style='flex:1;font-size:38px;font-weight:700'>{n}</span><span class='b' style='font-size:44px;color:{'#D4FF3A' if hi else '#F6F5F1'}'>{num(v)}</span><span style='width:130px;font-size:26px;color:#A9A8B2'>giornate</span></div>")
    return (f"<div style='position:absolute;inset:0;background:#0B0B0D'></div>"
            f"<div style='position:absolute;left:80px;top:200px;width:840px;display:flex;flex-direction:column;gap:16px'><span style='font-size:30px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#D4FF3A'>{GIORNI[giorno]}, ore {ora}</span>"
            f"<span class='b' style='font-size:80px;line-height:.98;letter-spacing:-.035em'>Mezza giornata alla volta.</span></div>"
            f"<div style='position:absolute;left:80px;top:500px;width:840px;display:flex;flex-direction:column;gap:16px'>"
            f"<div style='display:flex;gap:18px;font-size:22px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#8E8D96'><span style='width:170px'></span><span style='flex:1'>Mattina</span><span style='flex:1'>Pomeriggio</span></div>{rows}</div>"
            f"<div style='position:absolute;left:80px;top:1200px;width:840px'><div style='font-size:26px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#8E8D96;margin-bottom:8px'>Giornate per commessa</div>{tl}</div>")
GANCI = {'aperitivo': 'Sono le 19. | Sai dove sono finite | le giornate di oggi?',
         'tennis': 'Segnare le ore ti ruba tempo? | Qui bastano 10 secondi.',
         'cena': 'A cena. | E sa già quale | commessa guadagna.',
         'divano': 'Niente timesheet. | Due tap dal divano.'}
def gancio(txt):
    righe = ''.join(f"<span class='b' style='display:inline-block;background:#D4FF3A;color:#0B0B0D;font-size:70px;line-height:1.08;letter-spacing:-.03em;padding:4px 22px 10px;border-radius:18px;margin:0 0 10px'>{r}</span><br>" for r in txt.split(' | '))
    return f"<div style='position:absolute;inset:0 0 auto 0;height:760px;background:linear-gradient(rgba(0,0,0,.55),rgba(0,0,0,0))'></div><div style='position:absolute;left:70px;top:220px;width:900px'>{righe}</div>"
BRAND = (f"<div style='position:absolute;inset:0;background:#0B0B0D'></div>"
         f"<div style='position:absolute;left:0;right:0;top:560px;display:flex;flex-direction:column;align-items:center;gap:56px;text-align:center'>"
         f"<span class='b' style='font-size:104px;line-height:.98;letter-spacing:-.04em;width:860px'>Ogni sera<br>due tap.</span>"
         f"<svg width='230' height='230' viewBox='0 0 22 22'><circle cx='11' cy='11' r='9.5' fill='none' stroke='#D4FF3A' stroke-width='1.2'></circle><path d='M11 1.5 A9.5 9.5 0 0 0 11 20.5 Z' fill='#D4FF3A'></path></svg>"
         f"<span class='b' style='font-size:130px;line-height:1;letter-spacing:-.04em;margin-top:-16px'>Clepsi</span>"
         f"<span style='font-size:40px;color:#A9A8B2'>clepsi.it</span></div>")
if __name__ == '__main__':
    items = {'brand': BRAND}
    for i, (slug, ora, dove, am, pm, tm, x, g) in enumerate(SERE):
        items[f'titolo_{slug}'] = (f"<div style='position:absolute;inset:0 0 auto 0;height:640px;background:linear-gradient(rgba(0,0,0,.62),rgba(0,0,0,0))'></div>"
            f"<div style='position:absolute;left:80px;top:230px;width:840px;display:flex;flex-direction:column;gap:14px;text-shadow:0 2px 18px rgba(0,0,0,.5)'>"
            f"<span class='b' style='font-size:40px;color:#D4FF3A'>{GIORNI[g]}, ore {ora}</span><span class='b' style='font-size:76px;line-height:1;letter-spacing:-.03em'>{dove}</span></div>")
        items[f'gancio_{slug}'] = gancio(GANCI[slug])
        for st in range(4): items[f'card_{slug}_{st}'] = card(ora, am, pm, st)
        for st in range(3): items[f'tab_{slug}_{st}'] = tabella(g, ora, am, pm, st)
    render_pngs(items, W / 'png')
    P = lambda n: str(W / 'png' / f'{n}.png')
    for i, (slug, ora, dove, am, pm, tm, x, g) in enumerate(SERE):
        t0 = i * STEP
        sc = W / f'scena_{slug}.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-t', str(STEP), '-i', str(V169), '-vf', f'crop=608:1080:{x}:0,scale=1080:1920:flags=lanczos,fps=30,setsar=1',
                        '-c:v', 'libx264', '-crf', '16', '-c:a', 'aac', '-b:a', '192k', str(W / f'raw_{slug}.mp4')], check=True)
        ovs = [(P(f'titolo_{slug}'), 0.2, 6.4, 0.6, 0.4)]
        for st in range(4):
            end = tm[4] if st == 3 else tm[st + 1] + 0.15
            ovs.append((P(f'card_{slug}_{st}'), tm[st], end, 0.35 if st == 0 else 0.12, 0.45 if st == 3 else 0))
        overlay(str(W / f'raw_{slug}.mp4'), ovs, str(sc), audio=str(W / f'raw_{slug}.mp4'))
        # tabella: tre stati con dissolvenze brevi
        tb = W / f'tab_{slug}.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', '30', '-t', str(TAB), '-i', P(f'tab_{slug}_0'), '-loop', '1', '-framerate', '30', '-t', str(TAB), '-i', P(f'tab_{slug}_1'),
                        '-loop', '1', '-framerate', '30', '-t', str(TAB), '-i', P(f'tab_{slug}_2'), '-filter_complex',
                        '[1]format=rgba,fade=t=in:st=1.2:d=0.25:alpha=1[b];[2]format=rgba,fade=t=in:st=2.1:d=0.25:alpha=1[c];[0][b]overlay[ab];[ab][c]overlay,format=yuv420p,setsar=1[v]',
                        '-map', '[v]', '-c:v', 'libx264', '-crf', '16', '-r', '30', str(tb)], check=True)
        br = W / 'brand.mp4'
        if not br.exists():
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', '30', '-t', str(BR), '-i', P('brand'), '-vf', 'format=yuv420p,setsar=1', '-c:v', 'libx264', '-crf', '16', str(br)], check=True)
        o1 = STEP - XF; o2 = o1 + TAB - XF; tot = o2 + BR
        tb0 = o1  # inizio tabella nel reel
        fc = (f'[0:v]settb=1/30,fps=30[a];[1:v]settb=1/30,fps=30[b];[2:v]settb=1/30,fps=30[c];[a][b]xfade=fade:{XF}:{o1:.3f}[ab];[ab][c]xfade=fade:{XF}:{o2:.3f},format=yuv420p[v];'
              f'[0:a]afade=t=out:st={STEP - 1.0}:d=1.0,apad=whole_dur={tot:.3f}[s];'
              f'[3:a]aresample=48000,adelay={int((tb0 + 1.2) * 1000)}:all=1,volume=0.7[m];[4:a]aresample=48000,adelay={int((tb0 + 2.1) * 1000)}:all=1,volume=0.7[p];'
              f'[5:a]aresample=48000,adelay={int((o2 + 0.4) * 1000)}:all=1,volume=0.6[r];'
              f'[s][m][p][r]amix=inputs=4:normalize=0:duration=first,atrim=0:{tot:.3f},loudnorm=I=-16:TP=-1.5:LRA=11[aout]')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(sc), '-i', str(tb), '-i', str(br), '-i', str(AUD / 'clepsi_tocco_mattina.wav'),
                        '-i', str(AUD / 'clepsi_tocco_pomeriggio.wav'), '-i', str(AUD / 'clepsi_giornata_registrata.wav'), '-filter_complex', fc,
                        '-map', '[v]', '-map', '[aout]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                        '-movflags', '+faststart', str(W / f'reel-sera-{i+1}-{slug}.mp4')], check=True)
        print(slug, round(tot, 2))
