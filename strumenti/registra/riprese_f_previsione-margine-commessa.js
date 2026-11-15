// Video della pagina /funzioni/previsione-margine-commessa: la Home dello studio con gli stati delle commesse,
// Scuola Brera con il margine stretto, Uffici Lambrate in perdita, giornate usate, lavoro fatto e fasi.
// Uso: app servita su :8765 (python3 serve.py <app.clepsi.it> 8765 spa), poi: node riprese_f_previsione-margine-commessa.js <cartella>
const { chromium } = require('playwright'); const { Desk, apri } = require('./desk'); const mock = require('./mock_nuovo'); const studio = require('./studio_sito');
const OUT = process.argv[2] || 'riprese';
(async () => {
  const b = await chromium.launch(); const t = Date.now();
  const p = await apri(b, '2026-11-16T09:10:00+01:00', { viewport: { width: 1280, height: 960 }, url: 'http://localhost:8765/', prepara: ctx => mock.prepara(ctx, studio.opzioni()) });
  const r = new Desk(p, `${OUT}/unica`);
  const c = async loc => { const bb = await loc.boundingBox(); return [bb.x + bb.width / 2, bb.y + bb.height / 2, bb]; };
  const card = n => p.locator('div').filter({ has: p.getByText(n, { exact: true }) }).filter({ hasText: 'margine previsto' }).last();
  // 1 · la Home: quattro commesse, quattro stati
  r.segna('p1'); r.vista(640, 470, 1180, 0.01); await r.cursore(1100, 760, 0); await r.hold(1.6);
  await r.guarda(p.getByText('Uffici Lambrate', { exact: true }).first(), 640, 210, 1.1, 44); await r.hold(1.0);
  await r.cursore(760, 700, 1); await r.punta(p.getByText('Uffici Lambrate', { exact: true }).first(), 0.6); await r.hold(0.4);
  await r.punta(p.getByText('Scuola Brera', { exact: true }).first(), 0.6); await r.hold(0.3);
  await r.punta(p.getByText('Loft Navigli', { exact: true }).first(), 0.6); await r.hold(0.6);
  // 2 · Scuola Brera: margine stretto, e perché
  r.segna('p2');
  await r.clic(p.getByText('Scuola Brera', { exact: true }).first(), { attesa: 700 }); await r.hold(0.3);
  await r.guarda(p.getByText(/Di questo passo/).first(), 700, 50, 1.0); await r.hold(2.4);
  // 3 · Uffici Lambrate: in perdita, quando c'è ancora tempo
  r.segna('p3'); r.vista(620, 470, 1000, 0.9); await r.hold(0.4);
  await r.clic(p.getByText('Uffici Lambrate', { exact: true }).first(), { attesa: 700 }); await r.hold(0.3);
  await r.guarda(p.getByText(/Di questo passo/).first(), 700, 50, 1.0); await r.hold(2.6);
  // 4 · giornate usate, lavoro fatto, fasi
  r.segna('p4');
  await r.guarda(p.getByText('giornate usate', { exact: true }).first(), 760, 90, 0.9); await r.hold(1.8);
  await r.nascondi();
  const fasi = p.getByText('Fasi', { exact: true }).first();
  await r.portaA(fasi, 230, 1.4);
  await r.guarda(fasi, 760, 200, 0.9); await r.hold(2.6);
  r.segna('fine');
  await b.close();
  console.log('ok', r.n, 'fotogrammi', ((Date.now() - t) / 1000).toFixed(0) + 's');
})();
