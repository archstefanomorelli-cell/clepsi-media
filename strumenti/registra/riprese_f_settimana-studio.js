// Video della pagina /funzioni/settimana-studio: la griglia delle mezze giornate (settimana 46 del sito),
// il filtro su Uffici Lambrate con i totali per commessa, la correzione di una casella.
// Uso: app servita su :8765, poi: node riprese_f_settimana-studio.js <cartella>
const { chromium } = require('playwright'); const { Desk, apri } = require('./desk'); const mock = require('./mock_nuovo'); const studio = require('./studio_sito');
const OUT = process.argv[2] || 'riprese';
(async () => {
  const b = await chromium.launch(); const t = Date.now();
  const p = await apri(b, '2026-11-13T17:05:00+01:00', { viewport: { width: 1280, height: 960 }, url: 'http://localhost:8765/settimana',
    prepara: ctx => mock.prepara(ctx, studio.opzioni({ griglia: studio.GRIGLIA })) });
  const r = new Desk(p, `${OUT}/unica`);
  const titolo = p.getByText('Mezze giornate del team', { exact: true });
  // 1 · la griglia
  r.segna('p1'); await r.guarda(titolo, 980, 300, 0.01); await r.cursore(1100, 760, 0); await r.hold(1.4);
  await r.guarda(p.getByText('Luca', { exact: true }).first(), 700, 150, 1.1); await r.hold(0.4);
  await r.cursore(820, 640, 1);
  const celle = p.getByText('SBR', { exact: true });
  await r.punta(celle.nth(0), 0.6); await r.punta(p.getByText('ULA', { exact: true }).nth(0), 0.5); await r.punta(p.getByText('VRO', { exact: true }).nth(0), 0.6); await r.hold(0.8);
  // 2 · quale commessa si prende il tempo delle altre
  r.segna('p2');
  await r.guarda(titolo, 860, 260, 0.8);
  await r.clic(p.getByText('Uffici Lambrate', { exact: true }).first(), { scuro: false, attesa: 500 }); await r.hold(1.4);
  await r.guarda(p.getByText('La settimana per commessa', { exact: true }), 680, 60, 1.0); await r.hold(2.2);
  // 3 · una casella da correggere
  r.segna('p3');
  await r.guarda(titolo, 1000, 330, 0.9);
  await r.clic(p.getByText('Tutte', { exact: true }).first(), { attesa: 400 }); await r.hold(0.4);
  await r.clic(p.getByText('ASS', { exact: true }).first(), { attesa: 700 }); await r.hold(0.4);
  const pannello = p.getByText(/Paolo Greco · mercoledì/).first();
  await r.guarda(pannello, 620, 200, 0.9); await r.hold(0.9);
  await r.clic(p.getByText('Loft Navigli', { exact: true }).last(), { attesa: 300 }); await r.hold(0.6);
  await r.clic(p.getByText('Salva la correzione', { exact: true }), { scuro: true, attesa: 900 }); await r.hold(0.4);
  await r.guarda(p.getByText('Paolo', { exact: true }).first(), 760, 40, 1.0); await r.hold(2.4);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
