// Reel "Ti sei dimenticato ieri?": il promemoria delle 21, il recupero di mercoledì con un tocco, oggi «Come mercoledì».
// Uso: app servita su :8765 (python3 serve.py <app.clepsi.it> 8765 spa), poi: node riprese_recupero.js <cartella>
// Paolo (collaboratore finto, mock_nuovo.js) ha segnato lunedì e martedì; mercoledì gli è sfuggito.
const { chromium } = require('playwright'); const { Rec, apri } = require('./rec'); const mock = require('./mock_nuovo'); const blocco = require('./blocco');
const OUT = process.argv[2] || 'riprese';
(async () => {
  const b = await chromium.launch(); const t = Date.now();
  const p = await apri(b, '2026-11-12T21:00:10+01:00', {
    viewport: { width: 414, height: 847 }, url: 'http://localhost:8765/sera',
    prepara: ctx => mock.prepara(ctx, {
      sono: 'Paolo Neri', giorniFatti: ['2026-11-09', '2026-11-10'],
      studio: { nome: 'Studio Ferri Architetti', io: 'Giulia Ferri', persone: ['Paolo Neri', 'Sara Conti'] },
      commesse: [{ nome: 'Casa sul lago', sigla: 'CSL' }, { nome: 'Scuola di Lodi', sigla: 'SDL' }, { nome: 'Villa Rossi', sigla: 'VRO' }],
    }),
  });
  const r = new Rec(p, `${OUT}/unica`);
  const tocca = async (loc, o = {}) => r.tap(...await r.box(loc), { scuro: true, ...o });
  // 1 · Il promemoria delle 21 (la domanda delle 19 è rimasta senza risposta)
  await blocco.mostra(p, { data: 'giovedì 12 novembre', ora: '20:59', titolo: 'Paolo, manca solo la tua giornata', testo: 'Due tap e hai finito.' });
  r.segna('p1'); r.camera(0, 0.01); await r.hold(1.3);
  await blocco.cambiaOra(p, '21:00'); await r.hold(0.4);
  await blocco.arriva(p, r); await r.hold(1.9);
  await tocca(p.locator('#__notifica'), { stacco: true });
  await blocco.togli(p); await p.clock.runFor(300); await r.passa('dissolve', 0.5);
  await r.hold(2.2);                                   // "Mercoledì ti è sfuggito. Com'è andato?"
  // 2 · Mercoledì: tutto il giorno sulla stessa commessa, un tocco
  r.segna('p2'); r.camera(0.3, 0.8); await r.hold(0.6);
  await tocca(p.getByText('Tutto il giorno su Casa sul lago', { exact: true })); await r.hold(1.4);
  r.camera(1, 0.7); await r.hold(0.5);
  await tocca(p.getByText('Avanti', { exact: true }), { scuro: false, stacco: true, attesa: 900 }); await r.passa('entra', 0.45); r.camera(0, 0.5);
  await r.hold(1.6);                                   // "Com'è andata oggi, Paolo?"
  // 3 · Oggi come mercoledì
  r.segna('p3'); r.camera(0.3, 0.8); await r.hold(0.6);
  await tocca(p.getByText('Come mercoledì', { exact: true })); await r.hold(1.4);
  r.camera(1, 0.7); await r.hold(0.5);
  await tocca(p.getByText('Fatto', { exact: true }), { scuro: false, stacco: true, attesa: 1500 }); await r.passa('dissolve', 0.45); r.camera(0.3, 0.01);
  // fatto · la settimana completa
  r.segna('p4'); await r.hold(3.4);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
