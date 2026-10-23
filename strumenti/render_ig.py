import re, sys, pathlib
from playwright.sync_api import sync_playwright
SRC = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2])
def c(nome, col, stato, k, scol): return dict(nome=nome, col=col, stato=stato, scol=scol, ok=k=='ok', warn=k=='warn', loss=k=='loss', nuova=k=='new')
DATA = {
 'cosa-4': {'commesse': [c('Villa Rossi','#D4FF3A','In attivo','ok','#D4FF3A'), c('Scuola Brera','#9B8CFF','Margine stretto','warn','#FFC46B'),
                         c('Uffici Lambrate','#6FD3FF','In perdita','loss','#FF8A7A'), c('Loft Navigli','#FF9ECF','Appena iniziata','new','#C9C8D0')]},
 'primi100': {'fasce': [dict(chi='Da 1 a 3 persone', pieno='19 €', meta='9,50 €'), dict(chi='Da 4 a 10 persone', pieno='29 €', meta='14,50 €'),
                        dict(chi='Da 11 a 25 persone', pieno='59 €', meta='29,50 €')]},
}
def get(path, scope):
    v = scope
    for p in path.strip().split('.'): v = v[p] if isinstance(v, dict) else getattr(v, p)
    return v
def expand(html, scope):
    # sc-for (non annidati)
    def rfor(m):
        lst = get(m.group(1), scope); var = m.group(2); body = m.group(3)
        return ''.join(expand(body, {**scope, var: item}) for item in lst)
    html = re.sub(r'<sc-for list="\{\{([^}]+)\}\}" as="(\w+)"[^>]*>(.*?)</sc-for>', rfor, html, flags=re.S)
    def rif(m): return m.group(2) if get(m.group(1), scope) else ''
    html = re.sub(r'<sc-if value="\{\{([^}]+)\}\}"[^>]*>(.*?)</sc-if>', rif, html, flags=re.S)
    html = re.sub(r'\{\{\s*([\w.]+)\s*\}\}', lambda m: str(get(m.group(1), scope)), html)
    return html
names = sys.argv[3].split(',') if len(sys.argv) > 3 else ['Main','cosa-2','cosa-3','cosa-4','seneca','le19','primi100','varianti-1','varianti-2','autopsia-1','autopsia-2','autopsia-3','autopsia-4']
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width':1080,'height':1350}, device_scale_factor=1)
    for n in names:
        s = (SRC/f'{n}.dc.html').read_text()
        body = s.split('</helmet>',1)[1].split('</x-dc>',1)[0]
        body = expand(body, DATA.get(n, {}))
        assert '{{' not in body and 'sc-' not in body, n
        pg.set_content(f'<!doctype html><html lang="it"><head><meta charset="utf-8"><style>body{{margin:0}}</style></head><body>{body}</body></html>')
        pg.evaluate('document.fonts.ready')
        fams = pg.evaluate("[...new Set([...document.querySelectorAll('*')].map(e=>getComputedStyle(e).fontFamily))]")
        pg.screenshot(path=str(OUT/f'{n}.png'), clip={'x':0,'y':0,'width':1080,'height':1350})
        print(n, 'ok')
    b.close()
