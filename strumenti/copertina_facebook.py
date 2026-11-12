"""Copertina della pagina Facebook di Clepsi (12/11): 1640x624 (Facebook la mostra 820x312 da computer).
Testi al centro, dentro i 1100 px che si vedono anche dal telefono (ritaglio 16:9 ai lati); niente in basso a sinistra,
dove sta la foto del profilo. Uso: python3 strumenti/copertina_facebook.py → facebook/copertina-facebook.png"""
import pathlib
from playwright.sync_api import sync_playwright
OUT = pathlib.Path(__file__).resolve().parent.parent / 'facebook'; OUT.mkdir(exist_ok=True)
LIME, NERO = '#D4FF3A', '#0B0B0D'
LOGO = f"<svg width='46' height='46' viewBox='0 0 22 22'><circle cx='11' cy='11' r='9.5' fill='none' stroke='{LIME}' stroke-width='1.5'/><path d='M11 1.5 A9.5 9.5 0 0 0 11 20.5 Z' fill='{LIME}'/></svg>"
HTML = f"""<!doctype html><html lang='it'><head><meta charset='utf-8'><style>
html,body{{margin:0}} body{{width:1640px;height:624px;position:relative;overflow:hidden;background:{NERO};font-family:'DM Sans',sans-serif;color:#F6F5F1}}
.b{{font-family:'Bricolage Grotesque',sans-serif;font-weight:800}}
</style></head><body>
<div style='position:absolute;right:-230px;top:-200px;width:760px;height:760px;border-radius:50%;border:2px solid #24242A'></div>
<div style='position:absolute;left:-180px;bottom:-260px;width:520px;height:520px;border-radius:50%;border:2px solid #1C1C21'></div>
<div style='position:absolute;left:0;right:0;top:0;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center'>
  <div style='display:flex;align-items:center;gap:14px'>{LOGO}<span class='b' style='font-size:38px;letter-spacing:-.03em'>Clepsi</span></div>
  <div class='b' style='font-size:104px;line-height:.98;letter-spacing:-.045em;margin-top:18px'>Ogni sera<br><span style='color:{LIME}'>due tap.</span></div>
  <div style='font-size:32px;color:#C9C8D0;margin-top:20px'>Sai quanto ti rende ogni commessa. Mentre la fai.</div>
  <div style='font-size:22px;color:#8E8D96;margin-top:16px;letter-spacing:.06em'>GESTIONE DEL TEMPO PER STUDI DI ARCHITETTURA E INGEGNERIA · CLEPSI.IT</div>
</div></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1640, 'height': 624}, device_scale_factor=1)
    pg.set_content(HTML); pg.evaluate('document.fonts.ready'); pg.screenshot(path=str(OUT / 'copertina-facebook.png')); b.close()
print(OUT / 'copertina-facebook.png')
