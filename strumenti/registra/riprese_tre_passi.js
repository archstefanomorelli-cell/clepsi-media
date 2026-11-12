// Reel "Tre passi e lo studio è pronto": la creazione di studio, commessa e team su un account nuovo (finto, mock_nuovo.js).
// Uso: build di app.clepsi.it servita su localhost:8765, poi: node riprese_tre_passi.js <cartella>
// Larghezza 414: a 390 il pulsante "Aggiungi" del passo 3 esce dallo schermo (da sistemare nell'app).
const { chromium } = require('playwright'); const { Rec, apri } = require('./rec'); const mock = require('./mock_nuovo');
const OUT = process.argv[2] || 'riprese';
(async () => {
  const b = await chromium.launch(); const t = Date.now();
  const p = await apri(b, '2026-11-12T11:00:00+01:00', { prepara: mock.prepara, viewport: { width: 414, height: 847 } });
  const r = new Rec(p, `${OUT}/unica`);
  const tocca = async (loc, o = {}) => r.tap(...await r.box(loc), { scuro: true, ...o });
  // 1 · Lo studio
  r.segna('p1'); r.camera(0, 0.01); await r.hold(1.0);
  await tocca(p.getByPlaceholder('Studio…')); await r.scrivi('Studio Ferri Architetti'); await r.hold(0.4);
  r.camera(0.35, 0.7);
  await tocca(p.getByPlaceholder('Nome e cognome')); await r.scrivi('Giulia Ferri'); await r.hold(0.4);
  r.camera(0.8, 0.8); await r.hold(0.6);
  await tocca(p.getByText('4 – 6', { exact: true })); await r.hold(1.6);
  r.camera(1, 0.6); await r.hold(0.6);
  await tocca(p.getByText('Avanti', { exact: true }), { stacco: true, attesa: 1300 }); await r.passa('entra', 0.5); r.camera(0, 0.6);
  // 2 · La commessa
  r.segna('p2'); await r.hold(1.0);
  await tocca(p.locator('input:visible').nth(0)); await r.scrivi('Casa sul lago'); await r.hold(0.4);
  await tocca(p.locator('input:visible').nth(1)); await r.scrivi('38000'); await r.hold(0.4);
  r.camera(0.5, 0.7); await r.hold(1.4);           // "A metà" è già scelto: basta lasciarlo
  r.camera(1, 0.7); await r.hold(0.6);
  await tocca(p.getByText('Avanti', { exact: true }), { stacco: true, attesa: 1300 }); await r.passa('entra', 0.5); r.camera(0, 0.6);
  // 3 · Il team
  r.segna('p3'); await r.hold(1.0);
  await tocca(p.getByText('Link', { exact: true })); await r.hold(0.7);
  const nome = p.getByPlaceholder('Nome di chi lavora con te');
  for (const persona of ['Paolo Neri', 'Sara Conti']) {
    await tocca(nome); await r.scrivi(persona); await r.hold(0.3);
    await tocca(p.getByText('Aggiungi', { exact: true }), { attesa: 300 }); await r.hold(0.6);
    await tocca(p.getByText('Copia', { exact: true }).first(), { attesa: 900 }); await r.hold(0.7);
  }
  r.camera(1, 0.8); await r.hold(1.0);
  await tocca(p.getByText('Continua', { exact: true }), { stacco: true, attesa: 1500 }); await r.passa('dissolve', 0.5); r.camera(0, 0.5);
  // fine · stasera la prima domanda
  r.segna('p4'); await r.hold(3.6);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
