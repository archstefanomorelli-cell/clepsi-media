import subprocess, sys, numpy as np, cv2
src, out = sys.argv[1], sys.argv[2]
W, H, FPS, DUR = 2160, 4096, 25, 4.8
# keyframes: t, cx, cy, rx, ry  (source pixels)
K = np.array([[1.9, 150, 700, 330, 480], [2.4, 260, 720, 420, 540], [3.2, 400, 800, 520, 640],
              [4.0, 500, 880, 600, 700], [4.6, 600, 920, 600, 720], [4.8, 640, 930, 600, 720]])
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-t', str(DUR), '-i', src, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
    t = n / FPS
    if t >= K[0, 0] - 0.1:
        tt = min(max(t, K[0, 0]), K[-1, 0])
        cx, cy, rx, ry = [np.interp(tt, K[:, 0], K[:, i]) for i in range(1, 5)]
        x0, x1 = 0, int(min(W, cx + rx + 80)); y0, y1 = int(max(0, cy - ry - 80)), int(min(H, cy + ry + 80))
        reg = f[y0:y1, x0:x1].astype(np.float32)
        small = cv2.resize(reg, (max(1, (x1 - x0) // 28), max(1, (y1 - y0) // 28)), interpolation=cv2.INTER_AREA)
        bl = cv2.GaussianBlur(cv2.resize(small, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR), (0, 0), 25)
        m = np.zeros((y1 - y0, x1 - x0), np.float32)
        cv2.ellipse(m, (int(cx - x0), int(cy - y0)), (int(rx), int(ry)), 0, 0, 360, 1.0, -1)
        lum = cv2.cvtColor(reg.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
        m *= np.clip((222 - lum) / 20, 0, 1)          # niente sfocatura sul foglio bianco
        m = cv2.GaussianBlur(m, (0, 0), 18)
        fade = np.clip((t - (K[0, 0] - 0.1)) / 0.2, 0, 1)
        m = (m * fade)[..., None]
        f[y0:y1, x0:x1] = (reg * (1 - m) + bl * m).astype(np.uint8)
    enc.stdin.write(f.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print('frames', n)
