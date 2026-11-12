// Uso: servire la build di app.clepsi.it su localhost:8765 (python3 -m http.server 8765 dentro il clone), poi: node riprese_quattro.js <cartella>
// I dati sono quelli dello Studio di esempio (catturati dalla demo pubblica), serviti da mock.js: niente rete, niente account.
// Un'unica ripresa continua (piano sequenza): sera → home → scheda commessa → settimana. I cambi di schermata
// sono segnati in eventi.json e il composer li anima come nell'app vera (sale dal basso, entra da destra, ...).
const { chromium } = require('playwright'); const { Rec, apri } = require('./rec');
const OUT = process.argv[2] || 'riprese';
const DATI = require('./mock.json');
const MARTA = 'ce893d87-b0f6-4cb7-99d5-e394b5ad0572';
(async () => {
  const b = await chromium.launch(); const t = Date.now();
  let salvato = false;
  const extra = {
    'rpc/save_half_day': () => { salvato = true; return { t: 'null' }; },
    'half_days?select=member_id%2Chalf&studio_id=eq.5145620a-7b8f-4cfa-a730-74a78f571380&day=eq.2026-11-12': () => {
      const righe = JSON.parse(DATI.find(d => d.u.includes('half_days?select=member_id%2Chalf&studio_id') && d.u.includes('day=eq.2026-11-12')).t);
      return { t: JSON.stringify(salvato ? [...righe, { member_id: MARTA, half: 'am' }, { member_id: MARTA, half: 'pm' }] : righe) };
    },
    [`half_days?select=half&member_id=eq.${MARTA}&day=eq.2026-11-12`]: () => ({ t: salvato ? '[{"half":"am"},{"half":"pm"}]' : '[]' }),
  };
  const p = await apri(b, '2026-11-12T19:03:00+01:00', { extra });
  const r = new Rec(p, `${OUT}/unica`);
  const tocca = async (loc, o = {}) => r.tap(...await r.box(loc), o);
  // 1 · Due tap, la sera
  r.segna('p1'); r.camera(0, 0.01); await r.hold(1.3);
  await tocca(p.getByText("Com'è andata oggi?"), { stacco: true, attesa: 1100 }); await r.passa('sale', 0.55);
  await r.hold(1.4);
  // la mattina: Villa Rossi; il pomeriggio: Scuola Brera
  await tocca(p.getByRole('button', { name: 'Villa Rossi', exact: true }), { scuro: true });
  await r.hold(1.1);
  await tocca(p.getByText('Pomeriggio', { exact: true }).last(), { scuro: true });
  await r.hold(0.5);
  await tocca(p.getByRole('button', { name: 'Scuola Brera', exact: true }), { scuro: true });
  await r.hold(1.1); r.camera(1, 0.8); await r.hold(1.1);
  await tocca(p.getByRole('button', { name: /Fatto/ }).last(), { scuro: true, stacco: true, attesa: 1100 }); await r.passa('dissolve', 0.5); r.camera(0.5, 0.6);
  await r.hold(1.9);
  // 2 · Come chiuderà: si chiude la sera, si torna alla home e si scorrono le commesse
  r.segna('p2'); await r.hold(0.4); r.camera(0, 0.7); await r.hold(1.0);
  await tocca(p.locator('[aria-label="Chiudi"]:visible').first(), { scuro: true, stacco: true, attesa: 1100 }); await r.passa('scende', 0.55);
  await r.hold(1.0); await r.scroll(560, 3.6); await r.hold(1.6);
  // 3 · La perdita: si torna su e si apre Uffici Lambrate
  r.segna('p3'); await r.hold(0.6); await r.scroll(0, 1.0); await r.hold(0.8);
  await tocca(p.getByText('Uffici Lambrate').first(), { stacco: true, attesa: 1300 }); await r.passa('entra', 0.5);
  await r.hold(2.0); await r.scroll(330, 2.6); await r.hold(1.6);
  // 4 · La settimana: indietro e tab Settimana
  r.segna('p4'); await r.hold(0.5); await r.scroll(0, 0.8); await r.hold(0.4);
  await tocca(p.locator('[aria-label="Indietro"]:visible').first(), { stacco: true, attesa: 1100 }); await r.passa('esce', 0.5);
  await r.hold(0.4); r.camera(1, 0.8); await r.hold(1.1);
  await tocca(p.locator('a[href="/settimana"]:visible').first(), { stacco: true, attesa: 1300 }); await r.passa('dissolve', 0.4); r.camera(0, 0.7);
  await r.hold(1.8); await r.scroll(330, 2.4); await r.hold(2.0);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
