"""Musica elettronica leggera per i reel di Clepsi, generata da codice (nessun diritto di terzi).

Uso:
  python3 strumenti/musica.py lavoro/musica.wav 15          # solo il brano, 15 s
  python3 strumenti/musica.py --mix reel/x.mp4 out.mp4      # aggiunge il brano sotto l'audio del reel

Carattere: 100 bpm, la minore, accordi Am9 · Fmaj7 · Cmaj7 · G6, pad morbido con leggero "respiro",
arpeggio pizzicato con eco, cassa morbida e charleston discreti, basso sub. Entra piano, finale in dissolvenza.
"""
import sys, subprocess, pathlib
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)

def hz(n):  # nota MIDI -> Hz
    return 440 * 2 ** ((n - 69) / 12)

CHORDS = [  # (basso, note del pad, arpeggio)
    (45, [57, 60, 64, 67, 71], [69, 72, 76, 79, 76, 72, 71, 72]),   # Am9
    (41, [57, 60, 64, 65, 69], [69, 72, 76, 77, 76, 72, 69, 72]),   # Fmaj7
    (48, [55, 60, 64, 67, 71], [67, 72, 76, 79, 76, 72, 71, 72]),   # Cmaj7
    (43, [55, 59, 62, 64, 67], [67, 71, 74, 76, 74, 71, 67, 71]),   # G6
]

def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)

def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)

def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e

def add(buf, x, t):
    i = int(t * SR)
    if i >= len(buf): return
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += x

def brano(durata):
    n = int(durata * SR) + SR
    pad, arp, bass, kick, hat = (np.zeros(n) for _ in range(5))
    bars = int(np.ceil(durata / BAR)) + 1
    for b in range(bars):
        root, notes, ar = CHORDS[b % 4]
        t0 = b * BAR
        m = int(BAR * SR * 1.05)
        tt = np.arange(m) / SR
        # pad: tre sinusoidi leggermente stonate per nota
        p = sum(np.sin(2 * np.pi * hz(k) * (1 + d) * tt + rng.uniform(0, 6)) for k in notes for d in (-0.003, 0, 0.003))
        add(pad, p * env(m, 0.6, 0.6) / 15, t0)
        # basso sub, nota tenuta con attacco morbido
        bb = np.sin(2 * np.pi * hz(root - 12) * tt) * env(m, 0.05, 0.3)
        add(bass, bb, t0)
        # arpeggio a ottavi: pizzicato (sinusoide + seconda armonica) con decadimento
        for i, k in enumerate(ar):
            q = int(0.45 * SR)
            tq = np.arange(q) / SR
            pl = (np.sin(2 * np.pi * hz(k) * tq) + 0.3 * np.sin(4 * np.pi * hz(k) * tq)) * np.exp(-tq * 9)
            add(arp, pl * (0.9 if i % 2 == 0 else 0.6), t0 + i * BEAT / 2)
        # ritmica dalla seconda battuta
        if b >= 1:
            for i in range(4):
                q = int(0.35 * SR); tq = np.arange(q) / SR
                f = 52 + 70 * np.exp(-tq * 30)
                k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tq * 11)
                add(kick, k * (1.0 if i in (0, 2) else 0.55), t0 + i * BEAT)
                h = hp(rng.standard_normal(int(0.06 * SR)), 7000) * np.exp(-np.arange(int(0.06 * SR)) / SR * 70)
                add(hat, h, t0 + i * BEAT + BEAT / 2)
    pad = lp(pad, 2200)
    # "respiro" del pad sui tempi (sidechain leggero)
    t = np.arange(n) / SR
    pump = 1 - 0.35 * np.exp(-((t % BEAT)) * 9) * (t > BAR)
    pad *= pump
    # eco sull'arpeggio (3/8 di battuta)
    d = int(BEAT * 0.75 * SR)
    eco = np.zeros(n); eco[d:] = arp[:-d] * 0.35; eco[2 * d:] += arp[:-2 * d] * 0.15
    arp = lp(arp + eco, 4500)
    mix = 0.55 * pad + 0.32 * arp + 0.45 * lp(bass, 180) + 0.5 * kick + 0.06 * hat
    mix = mix[: int(durata * SR)]
    mix *= env(len(mix), 0.8, 1.6)
    # stereo: arpeggio e charleston leggermente aperti
    L = mix + 0.04 * arp[: len(mix)]
    R = mix - 0.04 * arp[: len(mix)]
    st = np.stack([L, R], 1)
    return st / np.abs(st).max() * 0.85

def scrivi(path, x):
    import scipy.io.wavfile as w
    w.write(path, SR, (x * 32767).astype(np.int16))

def durata(video):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video]))

def mix(video, out, vol_musica=0.55):
    d = durata(video)
    wav = pathlib.Path(out).with_suffix('.musica.wav')
    scrivi(str(wav), brano(d))
    fc = (f"[0:a]aformat=channel_layouts=stereo,volume=1.0[v];[1:a]volume={vol_musica}[m];"
          "[v][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', str(wav), '-filter_complex', fc,
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out], check=True)
    wav.unlink()

if __name__ == '__main__':
    if sys.argv[1] == '--mix':
        mix(sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 0.55)
    else:
        scrivi(sys.argv[1], brano(float(sys.argv[2])))
