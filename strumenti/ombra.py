# Fa ruotare l'ombra dello gnomone su un'immagine ferma della meridiana, con un lento avvicinamento.
import sys, subprocess, numpy as np, cv2
img, out, fps, dur, zmax, a0, a1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7])
I = cv2.imread(img).astype(np.float32); H, W = I.shape[:2]
L = cv2.cvtColor(I.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) + 1
B = cv2.morphologyEx(L, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61)))
B = cv2.GaussianBlur(B, (0, 0), 6)
D = np.clip(1 - L / B, 0, 1)                       # quanto è scuro rispetto al fondo
poly = np.array([[1095, 527], [1245, 482], [1500, 560], [1630, 640], [1610, 700], [1300, 650], [1095, 560]], np.int32)
reg = np.zeros((H, W), np.uint8); cv2.fillPoly(reg, [poly], 1)
m = ((D > 0.32) & (reg > 0)).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))   # via i solchi sottili
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.zeros_like(m)
for k in range(1, n):
    if st[k, cv2.CC_STAT_AREA] > 1500: keep[lab == k] = 1
keep = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
soft = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 2.5)
M = np.clip(D * soft, 0, 0.92)                     # ombra da spostare
hole = (cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))) * 255).astype(np.uint8)
Free = cv2.inpaint(I.astype(np.uint8), hole, 9, cv2.INPAINT_TELEA).astype(np.float32)   # quadrante senza ombra
tex = I - cv2.GaussianBlur(I, (0, 0), 3)                                     # grana della pietra
Free = np.clip(Free + np.where(hole[..., None] > 0, cv2.GaussianBlur(np.roll(tex, 40, axis=0), (0,0), 0.6) * 0.6, 0), 0, 255)
cv2.imwrite(out + '.mask.png', (M * 255).astype(np.uint8)); cv2.imwrite(out + '.free.jpg', Free.astype(np.uint8))
piv = (1118.0, 527.0)
nf = int(round(fps * dur))
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for i in range(nf):
    u = i / (nf - 1); e = u * u * (3 - 2 * u) * 0.35 + u * 0.65
    R = cv2.getRotationMatrix2D(piv, a0 + (a1 - a0) * u, 1.0)
    Mt = cv2.warpAffine(M, R, (W, H), flags=cv2.INTER_LINEAR)
    F = Free * (1 - Mt[..., None])
    z = 1 + (zmax - 1) * e
    Z = np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H / 2]])
    F = cv2.warpAffine(F, Z, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    enc.stdin.write(np.clip(F, 0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait()
