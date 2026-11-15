// Esplora l'app in modalità desktop con il finto backend (mock_nuovo.js) e lo studio di esempio del sito.
// Uso: node esplora_desktop.js <percorso> [larghezza] [altezza]
const { chromium } = require('playwright'); const mock = require('./mock_nuovo'); const studio = require('./studio_sito');
(async () => {
  const b = await chromium.launch();
  const W = +process.argv[3] || 1440, H = +process.argv[4] || 900;
  const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1, serviceWorkers: 'block' });
  const S = await mock.prepara(ctx, { log: !!process.env.LOG, ...studio.opzioni({ griglia: studio.GRIGLIA }) });
  const p = await ctx.newPage();
  await p.clock.install({ time: new Date('2026-11-13T11:00:00+01:00') });
  p.on('console', m => { if (m.type() === 'error') console.log('ERR', m.text().slice(0, 200)); });
  const path = (process.argv[2] || '/').replace('{ULA}', S.progetti[2].id).replace('{VRO}', S.progetti[0].id).replace('{SBR}', S.progetti[1].id).replace('{LNA}', S.progetti[3].id);
  await p.goto('http://localhost:8765' + path); await p.waitForTimeout(4000);
  const out = process.env.OUT || '/tmp/claude-0/-home-claude/44073820-df6b-565e-bcbb-9365e07a38d2/scratchpad/esplora.png';
  await p.screenshot({ path: out, fullPage: !!process.env.FULL });
  console.log((await p.locator('body').innerText()).slice(0, +process.env.N || 2500));
  await b.close();
})();
