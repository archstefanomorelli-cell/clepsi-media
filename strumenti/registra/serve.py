# Server statico per le riprese: serve una build in locale con i rimandi giusti.
# Uso: python3 serve.py <cartella> <porta> spa|html
#   spa  -> ogni percorso che non è un file torna index.html (app Expo: /parcella/CODICE, /commessa/ID)
#   html -> /calcola-parcella serve calcola-parcella.html (sito Astro)
import http.server, os, sys
root, port, modo = sys.argv[1], int(sys.argv[2]), sys.argv[3]
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=root, **k)
    def log_message(self, *a): pass
    def send_head(self):
        p = self.path.split('?')[0].split('#')[0]
        f = os.path.join(root, p.lstrip('/'))
        if not os.path.exists(f) or (os.path.isdir(f) and not os.path.exists(os.path.join(f, 'index.html'))):
            if modo == 'html' and os.path.exists(f.rstrip('/') + '.html'): self.path = p.rstrip('/') + '.html'
            elif modo == 'spa': self.path = '/index.html'
        return super().send_head()
http.server.ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
