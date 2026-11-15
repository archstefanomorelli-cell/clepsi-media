// Video della pagina /funzioni/varianti-commessa: il venerdì su Villa Rossi, la fase fatta, 4 mezze giornate
// di varianti del cliente, il riepilogo con il valore, poi le varianti nella scheda della commessa.
// Uso: app servita su :8765, poi: node riprese_f_varianti-commessa.js <cartella>
const { chromium } = require('playwright'); const { Desk, apri } = require('./desk'); const mock = require('./mock_nuovo'); const studio = require('./studio_sito');
const OUT = process.argv[2] || 'riprese';
(async () => {
  const b = await chromium.launch(); const t = Date.now(); let S;
  const opz = studio.opzioni();
  const p = await apri(b, '2026-11-13T17:05:00+01:00', { viewport: { width: 1280, height: 960 }, url: 'http://localhost:8765/',
    prepara: async ctx => { S = await mock.prepara(ctx, opz); } });
  await p.goto(`http://localhost:8765/?commessa=${S.progetti[0].id}`);
  const r = new Desk(p, `${OUT}/unica`);
  await r.avanza(() => p.getByText('Aggiorna fasi e varianti', { exact: true }).first().isVisible()); await p.clock.runFor(800); await p.waitForTimeout(300);
  // 1 · venerdì: a che punto è la commessa
  r.segna('p1'); await r.guarda(p.getByText('Aggiorna fasi e varianti', { exact: true }).first(), 700, 60, 0.01, 40); await r.cursore(1100, 700, 0); await r.hold(1.0);
  await r.cursore(1000, 620, 1);
  await r.clic(p.getByText('Aggiorna fasi e varianti', { exact: true }).first(), { attesa: 800 }); await r.hold(0.3);
  await r.guarda(p.getByText(/A che punto è Villa Rossi/).first(), 700, 170, 0.9); await r.hold(1.2);
  await r.clic(p.getByText('Fatta', { exact: true }).last(), { attesa: 300 }); await r.hold(0.9);
  // 2 · le varianti della settimana
  r.segna('p2');
  await r.guarda(p.getByText('Varianti del cliente', { exact: true }).last(), 700, 40, 0.8); await r.hold(0.5);
  const piu = p.getByText('+', { exact: true }).last();
  for (let i = 0; i < 4; i++) { await r.clic(piu, { attesa: 200, s: i ? 0.35 : 0.7 }); await r.hold(0.25); }
  await r.hold(0.6);
  await r.clic(p.getByText('Aggiorna le previsioni', { exact: true }), { scuro: true, attesa: 1500 }); await r.hold(0.2);
  await r.guarda(p.getByText(/Previsioni aggiornate/).first(), 700, 90, 0.9); await r.hold(2.6);
  // 3 · nella scheda della commessa, con il valore
  r.segna('p3');
  await r.clic(p.getByText('Villa Rossi', { exact: true }).first(), { attesa: 900 }); await r.hold(0.3);
  await r.nascondi();
  const sez = p.getByText('Varianti del cliente', { exact: true }).last();
  await r.portaA(sez, 420, 1.4);
  await r.guarda(sez, 700, 40, 0.9); await r.hold(2.6);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
