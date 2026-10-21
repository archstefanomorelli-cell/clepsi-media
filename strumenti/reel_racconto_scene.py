import subprocess, sys, pathlib, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from reel_lib import render_pngs, overlay, LOGO
from reel_serate import BRAND, gancio
ROOT = pathlib.Path(__file__).resolve().parents[1]
R = ROOT / 'sorgenti' / 'racconto'
W = ROOT / 'lavoro' / 'reel' / 'racconto'; W.mkdir(parents=True, exist_ok=True)
N = 'fps=30,settb=1/30,format=yuv420p,setsar=1'; SC = 'scale=1080:1920:flags=lanczos'; XF = 0.6; BR = 3.4
SCENE = [  # slug, input args, filter, durata, ticks
 ('meridiana', ['-i', str(R / 's1-meridiana-ombra.mp4')], f"trim=0:6.5,setpts=PTS-STARTPTS,crop=608:1080:1010:0,{SC},{N}", 6.5, []),
 ('strappo', ['-i', str(R / 's2-strappo-volto-sfocato.mp4')], f"setpts=(PTS-STARTPTS)/0.8,fps=30,trim=0:6.0,setpts=PTS-STARTPTS,crop=2160:3840:0:0,{SC},{N}", 6.0, []),
 ('porta', ['-i', str(R / 's3-porta.mp4')], f"trim=0:5.79,setpts=PTS-STARTPTS,crop=608:1080:640:0,{SC},{N}", 5.79, []),
 ('sabbia', ['-ss', '1.5', '-i', str(R / 's4-sabbia.mp4')], f"setpts=PTS-STARTPTS,fps=30,trim=0:6.75,setpts=PTS-STARTPTS,crop=608:1080:620:0,{SC},{N}", 6.75, []),
 ('orologio', ['-t', '2.1', '-i', str(R / 's5-orologio.mp4')], f"setpts=(PTS-STARTPTS)*2.76,fps=30,trim=0:5.79,setpts=PTS-STARTPTS,crop=608:1080:1312:0,{SC},{N}", 5.79, [1.38, 4.14]),
 ('tavole', ['-ss', '0.12', '-i', str(R / 's6-tavole.mp4')], f"trim=0:5.88,setpts=PTS-STARTPTS,crop=608:1080:560:0,{SC},{N}", 5.88, []),
]
GR = "<div style='position:absolute;inset:auto 0 0 0;height:1100px;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.66) 55%,rgba(0,0,0,.7))'></div>"
def frase(txt, top=1060, size=92, col='#F6F5F1'):
    return f"<div class='b' style='position:absolute;left:80px;top:{top}px;width:880px;font-size:{size}px;line-height:.98;letter-spacing:-.035em;color:{col};text-shadow:0 2px 24px rgba(0,0,0,.35)'>{txt}</div>"
def sotto(txt, top=1330):
    return f"<div style='position:absolute;left:80px;top:{top}px;width:860px;font-size:42px;line-height:1.3;color:#E8E7EE;text-shadow:0 2px 18px rgba(0,0,0,.5)'>{txt}</div>"
GANCI = {'meridiana': 'Il tempo è l’unica cosa che vendi. | Lo conti?', 'strappo': 'Quanto ti è costata | l’ultima «cosa veloce»?',
         'porta': 'La riunione di mezz’ora. | Durata: un pomeriggio.', 'sabbia': 'Dove sono finite | le giornate di questa settimana?',
         'orologio': 'Contare le ore non ti dice | quale commessa guadagna.', 'tavole': 'Questa commessa | ti ha fatto guadagnare?'}
TXT = [('meridiana', 'Omnia, Lucili, aliena sunt, tempus tantum nostrum est.', 'Tutto è d’altri. Solo il tempo è nostro.'), ('strappo', 'Quaedam tempora eripiuntur nobis.', 'Una parte di tempo ce la strappano.'), ('porta', 'Quaedam tempora subducuntur.', 'Una parte di tempo ce la sottraggono.'), ('sabbia', 'Quaedam tempora effluunt.', 'Una parte di tempo scivola via.'), ('orologio', 'Omnes horas complectere.', 'Tieni strette tutte le ore.'), ('tavole', 'Tempus collige et serva.', 'Raccogli il tuo tempo e custodiscilo.')]
def latino(t):
    return f"<div lang='la' style=\"position:absolute;left:80px;top:1080px;width:900px;font-family:'Instrument Serif',serif;font-style:italic;font-size:88px;line-height:1.02;text-shadow:0 2px 24px rgba(0,0,0,.35)\">{t}</div>"
def italiano(t):
    return (f"<div style='position:absolute;left:80px;top:1360px;width:880px;display:flex;flex-direction:column;gap:22px'>"
            f"<span class='b' style='font-size:62px;line-height:1.02;letter-spacing:-.03em;color:#D4FF3A'>{t}</span>"
            f"<span style='font-size:30px;color:#C9C8D0'>Seneca, Lettere a Lucilio</span></div>")
CASI = {'meridiana': 'In uno studio il tempo è l’unica cosa che vendi.',
        'strappo': 'La variante chiesta il venerdì sera. «Tanto è una cosa veloce.»',
        'porta': 'Il sopralluogo in più. La riunione che doveva durare mezz’ora.',
        'sabbia': 'Le giornate che nessuno guarda, mezza alla volta.',
        'orologio': 'Ogni sera alle 19: su cosa hai lavorato la mattina? E il pomeriggio?',
        'tavole': 'A fine commessa: quante giornate ci sono andate davvero?'}
def caso(t):
    return ("<div style='position:absolute;inset:0 0 auto 0;height:720px;background:linear-gradient(rgba(0,0,0,.6),rgba(0,0,0,0))'></div>"
            f"<div class='b' style='position:absolute;left:80px;top:230px;width:900px;font-size:60px;line-height:1.06;letter-spacing:-.03em;text-shadow:0 2px 20px rgba(0,0,0,.45)'>{t}</div>")
items = {'g': GR, 'brand': BRAND, **{f'c_{k}': caso(v) for k, v in CASI.items()}}
for k, la, it in TXT: items[f'f_{k}'] = latino(la); items[f's_{k}'] = italiano(it)
render_pngs(items, W / 'png'); P = lambda n: str(W / 'png' / f'{n}.png')
br = W / 'brand.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', '30', '-t', str(BR), '-i', P('brand'), '-vf', 'format=yuv420p,setsar=1', '-c:v', 'libx264', '-crf', '16', str(br)], check=True)
sr = 48000
for k, (slug, inp, filt, L, ticks) in enumerate(SCENE, 1):
    raw = W / f'raw_{slug}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inp, '-filter_complex', f'[0:v]{filt}[v]', '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '16', str(raw)], check=True)
    ovs = [(P('g'), 0, L, 0.6, 0), (P(f'c_{slug}'), 0.2, L - XF, 0.6, 0.4), (P(f'f_{slug}'), 0.2, L, 0.8, 0), (P(f's_{slug}'), 0.9, L, 0.8, 0)]
    sc = W / f'scena_{slug}.mp4'
    overlay(str(raw), ovs, str(sc))
    tot = L - XF + BR
    t = np.arange(int(sr * tot)) / sr
    pad = sum(a * np.sin(2 * np.pi * f * t + p) for f, a, p in [(110, .5, 0), (164.81, .32, 1), (220, .22, 2), (277.18, .1, .5), (329.63, .08, 3)])
    pad *= 0.75 + 0.25 * np.sin(2 * np.pi * t / 7.0)
    x = pad * .5 + sosfilt(butter(2, [80, 900], 'bandpass', fs=sr, output='sos'), np.random.default_rng(k).normal(0, 1, t.size)) * .35
    x *= np.clip(t / 1.2, 0, 1) * np.clip((tot - t) / 2.0, 0, 1)
    for tt in ticks:
        n = int(sr * .06); kk = np.arange(n) / sr
        i = int(tt * sr); x[i:i + n] += (np.sin(2 * np.pi * 2900 * kk) * .7 + np.sin(2 * np.pi * 820 * kk)) * np.exp(-kk / .008) * 1.6
    wavfile.write(str(W / f'a_{slug}.wav'), sr, (x / np.max(np.abs(x)) * .8).astype(np.float32))
    fc = (f'[0:v]settb=1/30,fps=30[a];[1:v]settb=1/30,fps=30[b];[a][b]xfade=fade:{XF}:{L - XF:.3f},format=yuv420p[v];'
          f'[2:a]loudnorm=I=-18:TP=-1.5:LRA=11[aout]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(sc), '-i', str(br), '-i', str(W / f'a_{slug}.wav'), '-filter_complex', fc, '-map', '[v]', '-map', '[aout]',
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-shortest',
                    str(W / f'reel-racconto-{k}-{slug}.mp4')], check=True)
    print(slug, round(tot, 2))
