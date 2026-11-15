// Riprese dell'app in modalità desktop per i video delle pagine "funzioni" del sito (15/11).
// Come rec.js (fotogramma per fotogramma, orologio finto), ma con il puntatore del mouse al posto del dito
// e con una camera che inquadra un rettangolo della schermata: vista(x, y, larghezza) in px css, centro del rettangolo.
// L'altezza del rettangolo la decide il composer (strumenti/video_funzioni.py) dal formato della finestra.
const { Rec, apri, FPS } = require('./rec');
const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const FRECCIA = `<svg width="28" height="32" viewBox="0 0 28 32"><path d="M4 3 L4 25 L10 19.6 L14.2 28.6 L18.4 26.7 L14.3 17.9 L22.4 17.9 Z" fill="#141418" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/></svg>`;
class Desk extends Rec {
  constructor(page, dir) { super(page, dir); this.cx = null; this.cy = null; }
  vista(x, y, w, durata = 0.9, ancora = 'l') { this.eventi.push({ tipo: 'vista', x, y, w, durata, ancora, f: this.n }); this.salva(); }
  // inquadra a partire dal bordo sinistro dell'elemento: rettangolo largo w, centro verticale dy px sotto il bordo alto
  async guarda(loc, w, dy = 0, durata = 0.9, margine = 28) { const bb = await loc.boundingBox(); this.vista(bb.x - margine + w / 2, bb.y + dy, w, durata, 'l'); }
  async cursore(x, y, vis = 1) {
    await this.p.evaluate(([x, y, v, F]) => {
      let d = document.getElementById('__cur');
      if (!d) { d = document.createElement('div'); d.id = '__cur'; d.innerHTML = F; d.style.cssText = 'position:fixed;left:0;top:0;z-index:1000000;pointer-events:none;filter:drop-shadow(0 2px 4px rgba(0,0,0,.35))'; document.body.appendChild(d); }
      d.style.transform = `translate(${x - 4}px,${y - 3}px)`; d.style.opacity = v;
    }, [x, y, vis, FRECCIA]);
    this.cx = x; this.cy = y;
  }
  nascondi() { return this.p.evaluate(() => { const d = document.getElementById('__cur'); if (d) d.style.opacity = 0; }); }
  async punta(dove, s = 0.75) {
    const [x, y] = Array.isArray(dove) ? dove : await this.box(dove);
    if (this.cx == null) await this.cursore(x + 260, y + 180);
    const x0 = this.cx, y0 = this.cy, n = Math.max(1, Math.round(s * FPS));
    for (let i = 1; i <= n; i++) {
      const e = ease(i / n), xi = x0 + (x - x0) * e, yi = y0 + (y - y0) * e - Math.sin(Math.PI * e) * Math.min(60, Math.hypot(x - x0, y - y0) * .08);
      await this.cursore(xi, yi); await this.p.mouse.move(xi, yi); await this.frame();
    }
    return [x, y];
  }
  // clic: il puntatore arriva, un cerchio si allarga sotto la punta (chiaro sui fondi scuri)
  async clic(dove, { scuro = false, attesa = 0, stacco = false, s = 0.75 } = {}) {
    const [x, y] = await this.punta(dove, s);
    const n1 = Math.round(.2 * FPS), n2 = Math.round(.38 * FPS);
    for (let i = 0; i < n1; i++) { await this.ripple(x, y, .3 * (i + 1) / n1, scuro); await this.frame(); }
    this.taps.push(this.n); this.salva();
    await this.p.mouse.click(x, y);
    if (attesa) await this.p.waitForTimeout(attesa);
    if (!stacco) for (let i = 0; i < n2; i++) { await this.ripple(x, y, .3 + .7 * (i + 1) / n2, scuro); await this.frame(); }
    await this.ripple(x, y, -1, scuro);
  }
  // scorre il primo contenitore scorrevole che contiene l'elemento (o la pagina) finché l'elemento sta a 'y'
  async portaA(loc, y, s = 1.2) {
    const h = await loc.evaluateHandle(e => { let a = e.parentElement; while (a && !(a.scrollHeight > a.clientHeight + 4 && /auto|scroll/.test(getComputedStyle(a).overflowY))) a = a.parentElement; return a || document.scrollingElement; });
    const from = await h.evaluate(e => e.scrollTop), max = await h.evaluate(e => e.scrollHeight - e.clientHeight);
    const to = Math.max(0, Math.min(max, from + await loc.evaluate(e => e.getBoundingClientRect().top) - y));
    const n = Math.max(1, Math.round(s * FPS));
    for (let i = 1; i <= n; i++) { await h.evaluate((e, v) => { e.scrollTop = v; }, from + (to - from) * ease(i / n)); await this.frame(); }
    return to - from;
  }
}
module.exports = { Desk, apri, FPS };
