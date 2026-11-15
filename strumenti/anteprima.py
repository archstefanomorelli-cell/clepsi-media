# griglia di fotogrammi per controllare un video: python3 strumenti/anteprima.py <pagina> <formato> t1 t2 ...
import subprocess, sys, pathlib
from PIL import Image
n, f, ts = sys.argv[1], sys.argv[2], sys.argv[3:]
d = pathlib.Path(__file__).resolve().parents[1] / 'lavoro' / 'funzioni' / n
sc = 540 if f == '1x1' else 432; ims = []
for t in ts:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', t, '-i', str(d / f'{n}-{f}.mp4'), '-frames:v', '1', '-vf', f'scale={sc}:-1', str(d / 'x.jpg')]); ims.append(Image.open(d / 'x.jpg').copy())
W, H = ims[0].size; c = 3; g = Image.new('RGB', (W * c, H * ((len(ims) + c - 1) // c)))
for i, im in enumerate(ims): g.paste(im, ((i % c) * W, (i // c) * H))
g.save(d / f'griglia-{f}.jpg', quality=85); print(d / f'griglia-{f}.jpg')
