// Reel "Il venerdì, un minuto": la notifica delle 18, la fase andata avanti, le varianti del cliente, le previsioni aggiornate.
// Uso: app servita su :8765 (python3 serve.py <app.clepsi.it> 8765 spa), poi: node riprese_venerdi.js <cartella>
// Titolare finto con due commesse avviate (mock_nuovo.js): i conti li rifà il mock come conti-commesse (margine.ts).
const { chromium } = require('playwright'); const { Rec, apri } = require('./rec'); const mock = require('./mock_nuovo'); const blocco = require('./blocco');
const OUT = process.argv[2] || 'riprese';
(async () => {
  const b = await chromium.launch(); const t = Date.now();
  const p = await apri(b, '2026-11-13T18:00:10+01:00', {
    viewport: { width: 414, height: 847 }, url: 'http://localhost:8765/venerdi',
    prepara: ctx => mock.prepara(ctx, {
      studio: { nome: 'Studio Ferri Architetti', io: 'Giulia Ferri', persone: ['Paolo Neri', 'Sara Conti'] },
      commesse: [
        { nome: 'Casa sul lago', sigla: 'CSL', giornate: 48, mezzeSettimana: 6, persone: [['Paolo Neri', 26], ['Sara Conti', 14], ['Giulia Ferri', 8]],
          fasi: [{ nome: 'Progetto preliminare', cent: 900000, stato: 'done' }, { nome: 'Progetto definitivo', cent: 1500000, stato: 'half' }, { nome: 'Progetto esecutivo', cent: 1400000 }] },
        { nome: 'Scuola di Lodi', sigla: 'SDL', giornate: 26, mezzeSettimana: 4, persone: [['Sara Conti', 14], ['Giulia Ferri', 12]],
          fasi: [{ nome: 'Rilievo', cent: 500000, stato: 'done' }, { nome: 'Progetto definitivo', cent: 2200000, stato: 'started' }, { nome: 'Direzione lavori', cent: 1800000 }] },
      ],
    }),
  });
  const r = new Rec(p, `${OUT}/unica`);
  const tocca = async (loc, o = {}) => r.tap(...await r.box(loc), { scuro: true, ...o });
  // 1 · Venerdì alle 18: una domanda sola
  await blocco.mostra(p, { data: 'venerdì 13 novembre', ora: '17:59', titolo: 'Giulia, a che punto sono le tue commesse?', testo: 'Un minuto per aggiornare le previsioni.' });
  r.segna('p1'); r.camera(0, 0.01); await r.hold(1.3);
  await blocco.cambiaOra(p, '18:00'); await r.hold(0.4);
  await blocco.arriva(p, r); await r.hold(1.9);
  await tocca(p.locator('#__notifica'), { stacco: true });
  await blocco.togli(p); await p.clock.runFor(300); await r.passa('dissolve', 0.5);
  await r.hold(1.8);
  // 2 · La fase è andata avanti: un tocco
  r.segna('p2');
  await tocca(p.getByText('Cambia', { exact: true }).first()); await r.hold(0.9);
  await tocca(p.getByText('In chiusura', { exact: true })); await r.hold(2.2);   // il margine previsto si aggiorna nella scheda
  // 3 · Le varianti del cliente
  r.segna('p3'); r.camera(0.45, 0.8); await r.hold(0.9);
  const piu = p.getByText('+', { exact: true });
  await tocca(piu); await r.hold(0.5); await tocca(piu); await r.hold(1.8);
  r.camera(1, 0.7); await r.hold(0.6);
  await tocca(p.getByText('Aggiorna le previsioni', { exact: true }), { scuro: false, stacco: true, attesa: 1500 }); await r.passa('dissolve', 0.45); r.camera(0.42, 0.01);
  // fatto · il riepilogo
  r.segna('p4'); await r.hold(4.2);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
