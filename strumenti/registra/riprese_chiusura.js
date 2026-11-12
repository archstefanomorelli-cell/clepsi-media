// Reel "La commessa chiusa": chiudi Casa sul lago, il bilancio vero, il riepilogo delle varianti per il cliente,
// quanto rende una giornata per tipo di incarico.
// Uso: app servita su :8765 (python3 serve.py <app.clepsi.it> 8765 spa), poi: node riprese_chiusura.js <cartella>
// Titolare finto (mock_nuovo.js): il bilancio lo rifà il mock come bilancioChiusura (chiusura.ts).
const { chromium } = require('playwright'); const { Rec, apri } = require('./rec'); const mock = require('./mock_nuovo');
const OUT = process.argv[2] || 'riprese';
const PID = 'c0c00000-0000-4000-8000-000000000005';   // la prima commessa che crea il mock (studio 1, persone 2-4)
(async () => {
  const b = await chromium.launch(); const t = Date.now(); let S;
  const p = await apri(b, '2026-11-12T11:00:00+01:00', {
    viewport: { width: 414, height: 847 }, url: `http://localhost:8765/commessa/${PID}`,
    prepara: async ctx => { S = await mock.prepara(ctx, {
      studio: { nome: 'Studio Ferri Architetti', io: 'Giulia Ferri', persone: ['Paolo Neri', 'Sara Conti'] },
      resaPerTipo: [{ tipo: 'nuovaCostruzione', commesse: 1, giornate: 140, resaGiornataCent: 45200 }, { tipo: 'ristrutturazione', commesse: 3, giornate: 268, resaGiornataCent: 39100 }, { tipo: 'interni', commesse: 2, giornate: 84, resaGiornataCent: 26800 }],
      commesse: [{ nome: 'Casa sul lago', sigla: 'CSL', tipo: 'ristrutturazione', giornate: 96, mezzeSettimana: 2, variantiPrima: 9,
        variantiSettimane: [['2026-09-14', 2], ['2026-10-05', 4], ['2026-10-26', 3]], persone: [['Paolo Neri', 52], ['Sara Conti', 30], ['Giulia Ferri', 14]], giornateFasi: [21, 40, 35],
        fasi: [{ nome: 'Progetto preliminare', cent: 900000, stato: 'done' }, { nome: 'Progetto definitivo', cent: 1500000, stato: 'done' }, { nome: 'Progetto esecutivo', cent: 1400000, stato: 'done' }] }],
    }); },
  });
  if (S.progetti[0].id !== PID) throw new Error('id della commessa cambiato: ' + S.progetti[0].id);
  const r = new Rec(p, `${OUT}/unica`);
  const tocca = async (loc, o = {}) => r.tap(...await r.box(loc), o);
  // dove scorrere perché l'elemento stia a 'y' nello schermo
  const verso = async (loc, y) => { const h = await r.scroller(); const st = await h.evaluate(e => e.scrollTop); return st + await loc.evaluate(e => e.getBoundingClientRect().top) - y; };
  // 1 · Commessa finita: la chiudi
  r.segna('p1'); r.camera(0, 0.01); await r.hold(2.4);
  const chiudi = p.getByText('Chiudi la commessa', { exact: true });
  await r.scroll(await verso(chiudi, 700), 2.6); r.camera(1, 0.7); await r.hold(0.8);
  await tocca(chiudi); await r.hold(0.6);
  const si = p.getByText('Sì, chiudila', { exact: true });
  await r.scroll(await verso(si, 720), 0.9); await r.hold(1.6);   // "Vedrai il bilancio finale…"
  await tocca(si, { stacco: true, attesa: 1500 });
  await (await r.scroller()).evaluate(e => { e.scrollTop = 0; }); await p.clock.runFor(300); await p.waitForTimeout(200);
  await r.passa('dissolve', 0.5); r.camera(0, 0.01);
  // 2 · Il bilancio
  r.segna('p2'); await r.hold(2.8);
  r.camera(0.75, 1.0); await r.hold(2.4);
  // 3 · Le varianti: il riepilogo per il cliente
  r.segna('p3'); r.camera(0.4, 0.9);
  const copia = p.getByText('Copia il riepilogo per il cliente', { exact: true });
  await r.scroll(await verso(p.getByText('Varianti chieste dal cliente', { exact: true }), 250), 1.4); await r.hold(1.4);
  await tocca(copia, { attesa: 300 }); await r.hold(1.8);
  console.log('copia a', await copia.or(p.getByText('Riepilogo copiato')).first().evaluate(e => e.getBoundingClientRect().top));
  // fatto · quanto rende una giornata, per tipo di incarico
  r.segna('p4'); r.camera(0.4, 0.9);
  await r.scroll(await verso(p.getByText('Quanto ti rende una giornata', { exact: true }), 230), 1.2); await r.hold(4.0);
  console.log('resa a', await p.getByText('Quanto ti rende una giornata', { exact: true }).evaluate(e => e.getBoundingClientRect().top));
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
