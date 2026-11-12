// Uso: servire la build di app.clepsi.it su localhost:8765 (python3 -m http.server 8765 dentro il clone), poi: node riprese_quattro.js <cartella>
// I dati sono quelli dello Studio di esempio (catturati dalla demo pubblica), serviti da mock.js: niente rete, niente account.
const { chromium } = require('playwright'); const { Rec, apri } = require('./rec');
const OUT = process.argv[2] || 'riprese';
(async () => {
  const b = await chromium.launch();
  const t = Date.now();
  // 1 · Due tap, la sera
  let p = await apri(b, '2026-11-12T19:03:00+01:00');
  let r = new Rec(p, `${OUT}/1a`);
  await r.hold(0.6); await r.tap(...await r.box(p.getByText("Com'è andata oggi?")), { stacco: true, attesa: 1000 });
  r = new Rec(p, `${OUT}/1b`);
  await r.hold(0.7);
  await r.tap(...await r.box(p.getByText('Tutto il giorno su', { exact: false })), { scuro: true });
  await r.hold(0.6);
  await r.tap(...await r.box(p.getByRole('button', { name: /Fatto/ }).last()), { scuro: true, stacco: true, attesa: 1000 });
  r = new Rec(p, `${OUT}/1c`); await r.hold(1.5);
  await p.context().close();
  // 2 · Come chiuderà: la home la mattina, scorrendo le commesse
  p = await apri(b, '2026-11-12T09:20:00+01:00');
  r = new Rec(p, `${OUT}/2a`); await r.hold(0.5); await r.scroll(560, 2.8); await r.hold(0.8);
  await p.context().close();
  // 3 · La perdita: tocco su Uffici Lambrate, poi la scheda
  p = await apri(b, '2026-11-12T09:20:00+01:00');
  r = new Rec(p, `${OUT}/3a`); await r.hold(0.6);
  await r.tap(...await r.box(p.getByText('Uffici Lambrate').first()), { stacco: true, attesa: 1200 });
  r = new Rec(p, `${OUT}/3b`); await r.hold(1.2); await r.scroll(330, 1.8); await r.hold(0.9);
  await p.context().close();
  // 4 · La settimana
  p = await apri(b, '2026-11-12T09:20:00+01:00');
  r = new Rec(p, `${OUT}/4a`); await r.hold(0.5);
  await r.tap(...await r.box(p.getByText('Settimana', { exact: true }).last()), { stacco: true, attesa: 1200 });
  r = new Rec(p, `${OUT}/4b`); await r.hold(1.6); await r.scroll(330, 1.8); await r.hold(0.8);
  await b.close();
  console.log('ok', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
