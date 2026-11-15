// Video della pagina /funzioni/senza-timesheet (telefono): la notifica delle 19, mattina e pomeriggio con due tap,
// fatto in dieci secondi; poi il promemoria delle 21 per chi se ne dimentica.
// Paolo Greco, collaboratore dello studio di esempio. Tutto finto e in locale (mock_nuovo.js); la schermata di blocco è disegnata (blocco.js).
// Uso: app servita su :8765, poi: node riprese_f_senza-timesheet.js <cartella>
const { chromium } = require('playwright'); const { Rec, apri } = require('./rec'); const mock = require('./mock_nuovo'); const blocco = require('./blocco'); const studio = require('./studio_sito');
const OUT = process.argv[2] || 'riprese';
(async () => {
  const b = await chromium.launch(); const t = Date.now();
  const p = await apri(b, '2026-11-12T19:00:20+01:00', {
    viewport: { width: 414, height: 847 }, url: 'http://localhost:8765/sera',
    prepara: ctx => mock.prepara(ctx, studio.opzioni({ sono: 'Paolo Greco', giorniFatti: ['2026-11-09', '2026-11-10', '2026-11-11'] })),
  });
  await r0(p);
  const r = new Rec(p, `${OUT}/unica`);
  const tocca = async (loc, o = {}) => r.tap(...await r.box(loc), { scuro: true, ...o });
  // 1 · alle 19 la domanda
  r.segna('p1');
  await blocco.mostra(p, { data: 'giovedì 12 novembre', ora: '18:59', titolo: "Com'è andata oggi, Paolo?", testo: 'Due tap: mattina e pomeriggio.' });
  await r.hold(1.2); await blocco.cambiaOra(p, '19:00'); await r.hold(0.4);
  await blocco.arriva(p, r); await r.hold(1.6);
  await tocca(p.locator('#__notifica'), { stacco: true });
  await blocco.togli(p); await p.clock.runFor(300); await r.passa('dissolve', 0.5);
  // 2 · due tap
  r.segna('p2'); await r.hold(1.1);
  await tocca(p.getByText('Villa Rossi', { exact: true }).first()); await r.hold(0.7);
  await tocca(p.getByText('Pomeriggio', { exact: true })); await r.hold(0.6);
  await tocca(p.getByText('Uffici Lambrate', { exact: true }).first()); await r.hold(0.9);
  await tocca(p.getByText('Fatto', { exact: true }), { scuro: false, stacco: true, attesa: 1500 }); await r.passa('dissolve', 0.45);
  // 3 · fatto
  r.segna('p3'); await r.hold(2.8);
  // 4 · chi se ne dimentica: il promemoria delle 21
  await blocco.mostra(p, { data: 'venerdì 13 novembre', ora: '20:59', titolo: 'Paolo, manca solo la tua giornata', testo: 'Due tap e hai finito.' });
  await r.passa('dissolve', 0.6);
  r.segna('p4'); await r.hold(1.0); await blocco.cambiaOra(p, '21:00'); await r.hold(0.4);
  await blocco.arriva(p, r); await r.hold(2.6);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
// aspetta che la domanda della sera sia pronta
async function r0(p) { for (let k = 0; k < 60; k++) { await p.clock.runFor(100); await p.waitForTimeout(80); if (await p.getByText('Pomeriggio', { exact: true }).isVisible().catch(() => false)) break; } await p.clock.runFor(600); }
