// Reel "Dalla parcella alla commessa": il calcolatore di clepsi.it e «Aprila in Clepsi», fino alla commessa pronta nell'app.
// Uso: sito servito su :8766 e app su :8765 (python3 serve.py ...), poi: node riprese_parcella.js <cartella>
// Il titolare e lo studio sono finti (mock_nuovo.js con uno studio già avviato): la parcella non va sul server, nessuna commessa vera.
const { chromium } = require('playwright'); const { Rec, apri } = require('./rec'); const mock = require('./mock_nuovo');
const OUT = process.argv[2] || 'riprese';
const euro = s => Math.round(Number(s.replace(/[^\d,]/g, '').replace(',', '.')) * 100);
(async () => {
  const b = await chromium.launch(); const t = Date.now(); let S;
  const p = await apri(b, '2026-11-12T11:00:00+01:00', {
    viewport: { width: 414, height: 847 }, url: 'http://localhost:8766/calcola-parcella',
    prepara: async ctx => { S = await mock.prepara(ctx, { studio: { nome: 'Studio Ferri Architetti', io: 'Giulia Ferri', persone: ['Paolo Neri', 'Sara Conti', 'Luca Bassi'] } }); },
  });
  const r = new Rec(p, `${OUT}/unica`);
  const tocca = async (loc, o = {}) => r.tap(...await r.box(loc), o);
  const yDoc = loc => loc.evaluate(e => e.getBoundingClientRect().top + scrollY);
  // 1 · La parcella, sul sito
  r.segna('p1'); r.camera(0, 0.01); await r.hold(1.4);
  const imp = p.locator('input').first();
  await r.scrollDoc(await yDoc(imp) - 330, 1.6); await r.hold(0.4);
  await tocca(imp); await p.keyboard.press('Control+A'); await r.scrivi('540000', 8); await r.hold(0.5);
  r.camera(1, 0.8); await r.hold(1.8);                 // in basso il totale si è già aggiornato
  // 2 · Le fasi: le voci scelte diventano le fasi
  r.segna('p2'); r.camera(0, 0.7);
  await r.scrollDoc(await yDoc(p.getByText('Le prestazioni', { exact: true })) - 110, 1.6); await r.hold(1.0);
  await tocca(p.getByRole('button', { name: /Progetto di fattibilità/ }).first()); await r.hold(0.5);
  r.camera(0.4, 0.8); await r.hold(2.0);
  // 3 · Le giornate che paga
  r.segna('p3'); r.camera(0, 0.6);
  await r.scrollDoc(await yDoc(p.getByText('La tua parcella', { exact: true })) - 120, 1.8); await r.hold(1.0);
  r.camera(0.75, 1.0); await r.hold(1.8);
  // 4 · In Clepsi: un tocco
  r.segna('p4'); await r.hold(0.8);
  // la parcella come la divide il server (parcel_phases): il totale in proporzione al compenso di ogni fase, a euro interi
  const righe = await p.evaluate(() => { const c = [...document.querySelectorAll('*')].find(e => e.textContent.trim() === 'La tua parcella' && e.children.length === 0).parentElement; return c.innerText; });
  const L = righe.split('\n').map(x => x.trim()).filter(Boolean);
  const fasi = []; for (let i = 1; i < L.length && !/^Compenso/.test(L[i]); i += 2) fasi.push({ nome: L[i], cp: euro(L[i + 1]) });
  const tot = euro(L[L.indexOf('Compenso, IVA e cassa escluse') + 1]); const somma = fasi.reduce((a, f) => a + f.cp, 0); let resto = tot;
  fasi.forEach((f, i) => { f.cent = i === fasi.length - 1 ? resto : Math.round(tot * f.cp / somma / 100) * 100; resto -= f.cent; });
  S.parcella = { totaleCent: tot, giornate: tot / 32000, fasi }; S.costoGiornataCent = 32000;
  console.log(JSON.stringify(S.parcella));
  await tocca(p.getByRole('button', { name: 'Aprila in Clepsi' }), { stacco: true, attesa: 200 });
  await r.avanza(() => p.getByText('Apri la parcella come commessa.').isVisible()); await p.clock.runFor(800); await p.waitForTimeout(300);
  await r.passa('dissolve', 0.5); r.camera(0, 0.01); await r.hold(1.8);
  r.camera(0.5, 0.8); await r.hold(0.6);
  await tocca(p.locator('input:visible').first(), { scuro: true }); await r.scrivi('Scuola di Lodi'); await r.hold(0.5);
  r.camera(1, 0.7); await r.hold(0.6);
  await tocca(p.getByText('Crea la commessa', { exact: true }), { scuro: true, stacco: true, attesa: 1500 });
  await r.passa('entra', 0.5); r.camera(0, 0.01);
  // fatto · la commessa con le fasi e i compensi
  r.segna('p5'); await r.hold(2.6);
  r.camera(1, 1.0); await r.hold(0.8);
  await r.scroll(470, 2.2); await r.hold(2.6);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
