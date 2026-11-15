"""Copertina della pagina LinkedIn di Clepsi (15/11): 1128x191, la misura consigliata per le pagine aziendali.
Il logo della pagina copre l'angolo in basso a sinistra: testi da circa un terzo verso destra.
Uso: python3 strumenti/copertina_linkedin.py → linkedin/copertina-linkedin.png"""
import pathlib
from playwright.sync_api import sync_playwright
OUT = pathlib.Path(__file__).resolve().parent.parent / 'linkedin'; OUT.mkdir(exist_ok=True)
LIME, NERO = '#D4FF3A', '#0B0B0D'
HTML = f"""<!doctype html><html lang='it'><head><meta charset='utf-8'><style>
html,body{{margin:0}} body{{width:1128px;height:191px;position:relative;overflow:hidden;background:{NERO};font-family:'DM Sans',sans-serif;color:#F6F5F1}}
.b{{font-family:'Bricolage Grotesque',sans-serif;font-weight:800}}
</style></head><body>
<div style='position:absolute;right:-120px;top:-170px;width:420px;height:420px;border-radius:50%;border:2px solid #24242A'></div>
<div style='position:absolute;left:280px;top:0;bottom:0;display:flex;align-items:center;gap:28px;white-space:nowrap'>
  <div class='b' style='font-size:60px;line-height:.95;letter-spacing:-.045em'>Ogni sera<br><span style='color:{LIME}'>due tap.</span></div>
  <div style='border-left:2px solid #2A2A30;padding-left:26px'>
    <div style='font-size:24px;color:#E4E3E8;line-height:1.25'>Sai quanto ti rende ogni commessa.<br>Mentre la fai.</div>
    <div style='font-size:12px;color:#8E8D96;margin-top:12px;letter-spacing:.04em'>GESTIONE DEL TEMPO PER STUDI DI ARCHITETTURA E INGEGNERIA · CLEPSI.IT</div>
  </div>
</div></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1128, 'height': 191}, device_scale_factor=1)
    pg.set_content(HTML); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / 'copertina-linkedin.png')); b.close()
print(OUT / 'copertina-linkedin.png')
