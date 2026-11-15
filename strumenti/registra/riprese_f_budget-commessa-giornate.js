// Video della pagina /funzioni/budget-commessa-giornate: una commessa nuova da 18.000 € diventa giornate fase per fase,
// il margine che vuoi tenere le ricalcola, poi le fasi di Scuola Brera con i quadratini (usate, oltre budget, libere).
// Uso: app servita su :8765 (python3 serve.py <app.clepsi.it> 8765 spa), poi: node riprese_f_budget-commessa-giornate.js <cartella>
const { chromium } = require('playwright'); const { Desk, apri } = require('./desk'); const mock = require('./mock_nuovo'); const studio = require('./studio_sito');
const OUT = process.argv[2] || 'riprese';
(async () => {
  const b = await chromium.launch(); const t = Date.now(); let S;
  const p = await apri(b, '2026-11-16T09:10:00+01:00', { viewport: { width: 1280, height: 1200 }, url: 'http://localhost:8765/modifica-commessa/nuova',
    prepara: async ctx => { S = await mock.prepara(ctx, studio.opzioni()); } });
  const r = new Desk(p, `${OUT}/unica`);
  const c = async loc => { const bb = await loc.boundingBox(); return [bb.x + bb.width / 2, bb.y + bb.height / 2, bb]; };
  // 1 · nome, tipo di incarico, compenso totale: le fasi diventano giornate
  r.segna('p1'); await r.guarda(p.getByText('Nuova commessa', { exact: true }).first(), 760, 190, 0.01, 30); await r.cursore(900, 520, 0); await r.hold(0.8);
  await r.cursore(820, 420, 1);
  await r.clic(p.getByPlaceholder('Es. 24-031 Villa Rossi')); await r.scrivi('Casa Verdi', 12); await r.hold(0.3);
  await r.clic(p.getByText('Nuova costruzione', { exact: true })); await r.hold(0.4);
  await r.guarda(p.getByText('Fasi', { exact: true }).first(), 760, 250, 1.0, 30); await r.hold(0.5);
  await r.clic(p.getByText('Ho solo il totale', { exact: true }), { attesa: 300 }); await r.hold(0.4);
  const tot = p.locator('input:visible').nth(11);
  await r.guarda(p.getByText('Compenso totale, in euro', { exact: true }), 760, -60, 0.8, 30);
  await r.clic(tot); await r.scrivi('18000', 6); await r.hold(0.5);
  await r.nascondi();
  await r.portaA(p.getByText('Nuova commessa', { exact: true }).first(), 20, 1.0);
  await r.guarda(p.getByText('Fasi', { exact: true }).first(), 760, 230, 1.0, 30); await r.hold(1.4);
  r.vista(930, 420, 760, 1.1, 'c'); await r.hold(2.0);
  // 2 · il margine che vuoi tenere: le giornate si ricalcolano
  r.segna('p2');
  const piu = p.getByText('+', { exact: true }).first();
  await r.cursore(1150, 420, 1);
  await r.clic(piu, { scuro: true, attesa: 300 }); await r.hold(0.9);
  await r.clic(piu, { scuro: true, attesa: 300 }); await r.hold(0.6);
  await r.hold(1.6);
  // 3 · le fasi di una commessa avviata: Scuola Brera
  await r.nascondi();
  await p.goto(`http://localhost:8765/?commessa=${S.progetti[1].id}`);
  await r.avanza(() => p.getByText(/Di questo passo/).first().isVisible()); await p.clock.runFor(800); await p.waitForTimeout(300);
  const fasi = p.getByText('Fasi', { exact: true }).first();
  await fasi.evaluate(e => { let a = e.parentElement; while (a && !(a.scrollHeight > a.clientHeight + 4 && /auto|scroll/.test(getComputedStyle(a).overflowY))) a = a.parentElement; (a || document.scrollingElement).scrollTop += e.getBoundingClientRect().top - 260; });
  await p.clock.runFor(300); await p.waitForTimeout(200);
  await r.guarda(fasi, 780, 200, 0.01);
  await r.passa('dissolve', 0.5);
  r.segna('p3'); await r.hold(1.2);
  await r.cursore(1150, 700, 1);
  await r.punta(p.getByText('12 di 10', { exact: true }).first(), 0.8); await r.hold(2.4);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
