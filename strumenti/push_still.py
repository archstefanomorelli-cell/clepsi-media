# avvicinamento lento e senza scatti su un'immagine ferma (interpolazione sub-pixel)
import sys, subprocess, numpy as np, cv2
img, out, fps, dur, zmax = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
src = cv2.imread(img).astype(np.float32); H, W = src.shape[:2]
n = int(round(fps * dur))
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for i in range(n):
    u = i / (n - 1); e = u * u * (3 - 2 * u) * 0.35 + u * 0.65   # avvio morbido
    z = 1 + (zmax - 1) * e
    M = np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H / 2]])
    f = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    enc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait()
