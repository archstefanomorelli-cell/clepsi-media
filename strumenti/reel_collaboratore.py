"""Reel "Il collaboratore, la prima sera" (12/11): l'invito con il link, l'email, la notifica delle 19 e i due tap.

Stesso formato e stesso montaggio del reel "4 cose" (reel_quattro.py): un'unica ripresa fotogramma per fotogramma,
transizioni come nell'app, camera che segue il dito, finestra grande dentro la zona sicura di Instagram.
Tutto finto e in locale (strumenti/registra/mock_nuovo.js); la schermata di blocco è disegnata, con il testo vero della notifica.

Uso: node strumenti/registra/riprese_collaboratore.js lavoro/collaboratore/riprese   (con la build dell'app servita su :8765)
     python3 strumenti/reel_collaboratore.py
"""
import reel_quattro as q

q.W = q.ROOT / 'lavoro' / 'collaboratore'; q.W.mkdir(parents=True, exist_ok=True)
q.RIP = q.W / 'riprese'
q.NOME = 'reel-collaboratore'
q.SW, q.SH, q.STRISCIA = 828, 1694, 0          # 414x847 css a 2x
q.CH = q.PH * q.SW / q.PW
T, P, F = 'clepsi_tocco_mattina', 'clepsi_tocco_pomeriggio', 'clepsi_giornata_registrata'
N = 'clepsi_notifica'
q.PUNTI = [
    ('Il collaboratore?', 'Un link e la sua email.', [T, P, T, P]),
    ('Alle 19?', 'Gli arriva la domanda.', [N]),
    ('Ogni sera?', 'Due tap e ha finito.', [T, T, P, P]),
    ('Fatto.', 'A domani alle 19.', [F]),
]
q.ETICHETTE = ['Invito con un link', 'La domanda alle 19', 'Due tap, ogni sera']
q.COPERTINA = ('Il collaboratore,', 'la prima sera.', 1, 2.9)

def titolo(i, d, r):
    pill = f'{i} / 3' if i <= 3 else '✓'
    return (f"<div style='position:absolute;left:{q.PX}px;top:178px;width:930px'>"
            f"<span style='display:inline-block;font-size:26px;font-weight:700;letter-spacing:.12em;color:{q.LIME};border:2px solid {q.LIME};"
            f"border-radius:999px;padding:6px 16px'>{pill}</span>"
            f"<div class='b' style='font-size:74px;line-height:1.0;letter-spacing:-.04em;margin-top:22px'>{d}<br>"
            f"<span style='color:{q.LIME}'>{r}</span></div></div>")

def apertura():
    return (f"<div style='position:absolute;inset:0;background:{q.NERO}'></div>"
            "<div style='position:absolute;left:80px;top:560px;width:920px'>"
            f"<div style='display:flex;align-items:center;gap:16px'>{q.LOGO.format(s=54, c=q.LIME)}"
            "<span class='b' style='font-size:46px;letter-spacing:-.03em'>Clepsi</span></div>"
            "<div class='b' style='font-size:112px;line-height:.96;letter-spacing:-.045em;margin-top:36px'>Il collaboratore,<br>"
            f"<span style='color:{q.LIME}'>la prima sera.</span></div>"
            "<div style='font-size:36px;color:#C9C8D0;margin-top:34px'>Cosa deve fare chi lavora con te. Tutto qui.</div></div>")

def chiusura():
    chips = ''.join(f"<span style='font-size:30px;padding:12px 22px;border:2px solid #3A3A42;border-radius:999px;color:#E8E7EC'>"
                    f"<span style='color:{q.LIME}'>✓</span> {e}</span>" for e in q.ETICHETTE)
    return (f"<div style='position:absolute;inset:0;background:{q.NERO}'></div>"
            "<div style='position:absolute;left:0;right:0;top:400px;display:flex;flex-direction:column;align-items:center;text-align:center'>"
            f"{q.LOGO.format(s=120, c=q.LIME)}"
            "<div class='b' style='font-size:96px;line-height:.98;letter-spacing:-.045em;margin-top:40px'>Niente timesheet.<br>"
            f"<span style='color:{q.LIME}'>Ogni sera, due tap.</span></div>"
            f"<div style='display:flex;flex-wrap:wrap;justify-content:center;gap:14px;width:900px;margin-top:48px'>{chips}</div>"
            f"<div style='margin-top:56px;background:{q.LIME};color:{q.NERO};font-weight:700;font-size:40px;padding:22px 48px;border-radius:999px'>Prova l'app gratis</div>"
            "<div style='font-size:32px;color:#A9A8B2;margin-top:22px'>clepsi.it · Nomi e dati di esempio</div></div>")

q.titolo, q.apertura, q.chiusura = titolo, apertura, chiusura
if __name__ == '__main__':
    q.main()
