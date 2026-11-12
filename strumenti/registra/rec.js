// Registrazione fotogramma per fotogramma dell'app (studio di esempio, dati finti serviti in locale).
const { chromium } = require('playwright'); const { prepara } = require('./mock'); const fs = require('fs');
const FPS = 30, DT = 1000 / FPS;
const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
class Rec {
  constructor(page, dir) { this.p = page; this.dir = dir; this.n = 0; this.acc = 0; this.taps = []; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true }); }
  async frame() {
    this.acc += DT; const step = Math.floor(this.acc); this.acc -= step;
    await this.p.clock.runFor(step);
    await this.p.screenshot({ path: `${this.dir}/${String(this.n++).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 93 });
  }
  async hold(s) { for (let i = 0; i < Math.round(s * FPS); i++) await this.frame(); }
  async ripple(x, y, k, scuro) { // k: 0..1 fase del tocco
    await this.p.evaluate(([x, y, k, scuro]) => {
      let d = document.getElementById('__tap');
      if (!d) { d = document.createElement('div'); d.id = '__tap'; d.style.cssText = 'position:fixed;width:56px;height:56px;margin:-28px 0 0 -28px;border-radius:50%;pointer-events:none;z-index:999999'; document.body.appendChild(d); }
      d.style.left = x + 'px'; d.style.top = y + 'px';
      d.style.background = scuro ? 'rgba(255,255,255,.55)' : 'rgba(20,20,24,.28)';
      let sc, op;
      if (k < 0) { sc = 0; op = 0; }
      else if (k < .3) { const t = k / .3; sc = .55 + .35 * t; op = t; }       // il dito scende
      else { const t = (k - .3) / .7; sc = .9 + .9 * (1 - Math.pow(1 - t, 2)); op = 1 - t; } // e si allarga sfumando
      d.style.transform = `scale(${sc})`; d.style.opacity = op;
    }, [x, y, k, scuro]);
  }
  // tocco: 0.15 s di avvicinamento, poi il click, poi 0.35 s di sfumatura (la UI risponde intanto)
  async tap(x, y, { scuro = false, attesa = 0, stacco = false } = {}) {
    // stacco: il tocco chiude la ripresa (cambia schermata): resta il dito premuto, il resto lo fa la dissolvenza
    const n1 = Math.round(.18 * FPS), n2 = Math.round(.3 * FPS);
    for (let i = 0; i < n1; i++) { await this.ripple(x, y, .3 * (i + 1) / n1, scuro); await this.frame(); }
    this.taps.push(this.n); fs.writeFileSync(`${this.dir}/tocchi.json`, JSON.stringify(this.taps));
    await this.p.mouse.click(x, y); await this.p.mouse.move(2, 2);
    if (attesa) await this.p.waitForTimeout(attesa);
    if (!stacco) for (let i = 0; i < n2; i++) { await this.ripple(x, y, .3 + .7 * (i + 1) / n2, scuro); await this.frame(); }
    await this.ripple(x, y, -1, scuro);
  }
  async scroller() {
    return this.p.evaluateHandle(() => { let e = document.elementFromPoint(195, 420); while (e && !(e.scrollHeight > e.clientHeight + 20 && /auto|scroll/.test(getComputedStyle(e).overflowY))) e = e.parentElement; if (e) return e; const c = [...document.querySelectorAll('div')].filter(d => d.scrollHeight > d.clientHeight + 20 && /auto|scroll/.test(getComputedStyle(d).overflowY) && d.getClientRects().length && d.getBoundingClientRect().width > 0); return c[0]; });
  }
  async scroll(to, s) {
    let h = await this.scroller();
    for (let k = 0; k < 20 && !(await h.evaluate(e => !!e)); k++) { await this.p.waitForTimeout(250); h = await this.scroller(); }
    const from = await h.evaluate(e => e.scrollTop);
    const max = await h.evaluate(e => e.scrollHeight - e.clientHeight); to = Math.min(to, max);
    const n = Math.max(1, Math.round(s * FPS));
    for (let i = 1; i <= n; i++) { await h.evaluate((e, y) => { e.scrollTop = y; }, from + (to - from) * ease(i / n)); await this.frame(); }
  }
  async box(loc) { const b = await loc.boundingBox(); return [b.x + b.width / 2, b.y + b.height / 2]; }
}
async function apri(browser, ora) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 842 }, deviceScaleFactor: 2, serviceWorkers: 'block' });
  await prepara(ctx);
  const p = await ctx.newPage();
  const t0 = new Date(ora);
  await p.clock.install({ time: t0 });
  await p.goto('http://localhost:8765/'); await p.waitForTimeout(3500);
  await p.clock.pauseAt(new Date(t0.getTime() + 8000));
  await p.waitForTimeout(300);
  return p;
}
module.exports = { Rec, apri, FPS };
