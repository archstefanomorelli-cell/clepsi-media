// Reel "Il collaboratore, la prima sera": l'invito, l'email, la notifica delle 19 e i due tap.
// Uso: app servita su :8765 (python3 serve.py <app.clepsi.it> 8765 spa), poi: node riprese_collaboratore.js <cartella>
// Tutto finto e in locale (mock_nuovo.js): nessuna email, nessun codice vero, nessuna notifica spedita.
// La notifica sulla schermata di blocco è disegnata (blocco.js), con il testo vero di invia-domande.
// Giorni di lavoro giovedì e venerdì: così la sera non chiede di recuperare giorni di prima dell'iscrizione
// (nell'app vera a un collaboratore appena entrato lo chiede: da sistemare).
const { chromium } = require('playwright'); const { Rec, apri } = require('./rec'); const mock = require('./mock_nuovo'); const blocco = require('./blocco');
const OUT = process.argv[2] || 'riprese';
(async () => {
  const b = await chromium.launch(); const t = Date.now();
  const p = await apri(b, '2026-11-12T17:40:00+01:00', {
    viewport: { width: 414, height: 847 }, url: 'http://localhost:8765/invito/INV123',
    prepara: ctx => mock.prepara(ctx, {
      invito: { nome: 'Paolo Neri' }, giorniFatti: ['2026-11-05', '2026-11-06'], giorniLavoro: [4, 5],
      studio: { nome: 'Studio Ferri Architetti', io: 'Giulia Ferri', persone: ['Paolo Neri', 'Sara Conti'] },
      commesse: [{ nome: 'Casa sul lago', sigla: 'CSL' }, { nome: 'Scuola di Lodi', sigla: 'SDL' }, { nome: 'Villa Rossi', sigla: 'VRO' }],
    }),
  });
  const r = new Rec(p, `${OUT}/unica`);
  const tocca = async (loc, o = {}) => r.tap(...await r.box(loc), { scuro: true, ...o });
  // 1 · L'invito: il link, l'email, il codice
  r.segna('p1'); r.camera(0, 0.01); await r.hold(1.6);
  await tocca(p.locator('input:visible').first()); await r.scrivi('paolo.neri@studioferri.it', 16); await r.hold(0.5);
  r.camera(1, 0.7); await r.hold(0.6);
  await tocca(p.getByText('Mandami il codice', { exact: true }), { stacco: true, attesa: 900 }); await r.passa('entra', 0.45); r.camera(0, 0.5);
  await r.hold(1.2);
  await tocca(p.locator('input:visible').first()); await r.scrivi('482913', 7); await r.hold(0.5);
  r.camera(1, 0.7); await r.hold(0.5);
  await tocca(p.getByText('Entra', { exact: true }), { stacco: true, attesa: 1800 }); await r.passa('dissolve', 0.5); r.camera(0, 0.01);
  await r.hold(2.0);
  // 2 · Alle 19: la notifica sulla schermata di blocco
  r.segna('p2');
  await blocco.mostra(p, { data: 'giovedì 12 novembre', ora: '18:59', titolo: "Com'è andata oggi, Paolo?", testo: 'Due tap: mattina e pomeriggio.' });
  await r.passa('dissolve', 0.7); await r.hold(1.1);
  await blocco.cambiaOra(p, '19:00'); await r.hold(0.4);
  await blocco.arriva(p, r);
  await r.hold(1.8);
  await tocca(p.locator('#__notifica'), { stacco: true });
  // si apre l'app sulla domanda della sera
  await p.clock.setSystemTime(new Date('2026-11-12T19:00:20+01:00'));
  await p.goto('http://localhost:8765/sera');
  await r.avanza(() => p.getByText('Com’è andata oggi, Paolo?').or(p.getByText("Com'è andata oggi, Paolo?")).first().isVisible()); await p.clock.runFor(800); await p.waitForTimeout(300);
  await r.passa('dissolve', 0.5);
  // 3 · Due tap
  r.segna('p3'); await r.hold(1.3);
  await tocca(p.getByText('Villa Rossi', { exact: true }).first()); await r.hold(0.7);
  await tocca(p.getByText('Pomeriggio', { exact: true })); await r.hold(0.6);
  await tocca(p.getByText('Scuola di Lodi', { exact: true }).first()); await r.hold(0.9);
  r.camera(1, 0.7); await r.hold(0.5);
  await tocca(p.getByText('Fatto', { exact: true }), { scuro: false, stacco: true, attesa: 1500 }); await r.passa('dissolve', 0.45); r.camera(0.3, 0.01);
  // fatto
  r.segna('p4'); await r.hold(3.2);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
