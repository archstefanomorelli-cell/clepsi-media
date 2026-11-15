// Video della pagina /funzioni/bilancio-commessa: si chiude Uffici Lambrate (i numeri del sito: 34 giornate su 27,
// 265 € a giornata contro 320 € di costo, 6 giornate di varianti non fatturate) e poi la resa media per tipo di incarico.
// Uso: app servita su :8765, poi: node riprese_f_bilancio-commessa.js <cartella>
const { chromium } = require('playwright'); const { Desk, apri } = require('./desk'); const mock = require('./mock_nuovo'); const studio = require('./studio_sito');
const OUT = process.argv[2] || 'riprese';
(async () => {
  const b = await chromium.launch(); const t = Date.now(); let S;
  const o = studio.opzioni();
  o.commesse[2] = { ...o.commesse[2], giornate: 34, giornateFasi: [8, 17, 9], variantiPrima: 12, fasi: o.commesse[2].fasi.map(f => ({ ...f, stato: 'done' })) };
  o.resaPerTipo = [{ tipo: 'ristrutturazione', commesse: 4, giornate: 310, resaGiornataCent: 34800 }, { tipo: 'nuovaCostruzione', commesse: 2, giornate: 190, resaGiornataCent: 41200 }, { tipo: 'interni', commesse: 3, giornate: 96, resaGiornataCent: 29500 }];
  const p = await apri(b, '2026-11-12T11:00:00+01:00', { viewport: { width: 1280, height: 960 }, url: 'http://localhost:8765/',
    prepara: async ctx => { S = await mock.prepara(ctx, o); } });
  await p.goto(`http://localhost:8765/?commessa=${S.progetti[2].id}`);
  const r = new Desk(p, `${OUT}/unica`);
  await r.avanza(() => p.getByText('Chiudi la commessa', { exact: true }).first().isVisible()); await p.clock.runFor(800); await p.waitForTimeout(300);
  // 1 · la commessa è finita: la chiudi
  r.segna('p1'); await r.guarda(p.getByText('Aggiorna fasi e varianti', { exact: true }).first(), 760, 80, 0.01); await r.cursore(1150, 700, 0); await r.hold(1.2);
  await r.cursore(1050, 600, 1);
  await r.clic(p.getByText('Chiudi la commessa', { exact: true }).first(), { attesa: 600 }); await r.hold(1.6);
  await r.clic(p.getByText('Sì, chiudila', { exact: true }), { scuro: true, attesa: 1500 }); await r.hold(0.2);
  await r.nascondi();
  // 2 · il bilancio: giornate, resa per giornata, varianti non fatturate
  r.segna('p2');
  await r.guarda(p.getByText('Il bilancio', { exact: true }), 680, 120, 0.9); await r.hold(2.2);
  await r.guarda(p.getByText('ti ha reso ogni giornata', { exact: false }).first(), 680, 20, 0.9); await r.hold(0.1);
  await r.guarda(p.getByText('giornate usate', { exact: false }).first(), 680, 30, 0.01); await r.hold(2.4);
  await r.guarda(p.getByText('Varianti chieste dal cliente', { exact: true }), 680, 70, 0.9); await r.hold(2.4);
  // 3 · quanto ti rende una giornata, per tipo di incarico
  r.segna('p3');
  const resa = p.getByText('Quanto ti rende una giornata', { exact: true });
  await r.portaA(resa, 300, 1.4);
  await r.guarda(resa, 700, 130, 0.9); await r.hold(2.8);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
