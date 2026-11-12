const { chromium } = require('playwright'); const { prepara } = require('./mock_nuovo');
(async () => {
  const b = await chromium.launch();
  const W = +process.argv[2] || 390;
  const ctx = await b.newContext({ viewport: { width: W, height: Math.round(W / 0.48872) }, deviceScaleFactor: 1, serviceWorkers: 'block', permissions: ['clipboard-read', 'clipboard-write', 'notifications'] });
  await prepara(ctx, { log: true });
  const p = await ctx.newPage();
  await p.clock.install({ time: new Date('2026-11-12T11:00:00+01:00') });
  p.on('console', m => { if (m.type() === 'error') console.log('ERR', m.text().slice(0, 200)); });
  p.on('popup', () => console.log('POPUP!'));
  await p.goto('http://localhost:8765/'); await p.waitForTimeout(3500);
  let i = 10; const sh = async () => { await p.waitForTimeout(700); await p.screenshot({ path: `e${i++}.png` }); };
  await p.getByPlaceholder('Studio…').fill('Studio Ferri Architetti');
  await p.getByPlaceholder('Nome e cognome').fill('Giulia Ferri');
  await p.getByText('4 – 6', { exact: true }).click();
  await p.getByText('Avanti', { exact: true }).click(); await p.waitForTimeout(1500);
  const inputs = p.locator('input:visible');
  await inputs.nth(0).fill('Casa sul lago'); await inputs.nth(1).fill('38000');
  await p.getByText('A metà', { exact: true }).click();
  await p.getByText('Avanti', { exact: true }).click(); await p.waitForTimeout(1500);
  await sh();
  await p.getByText('Link', { exact: true }).click();
  const nome = p.getByPlaceholder('Nome di chi lavora con te');
  await nome.fill('Paolo Neri'); await p.getByText('Aggiungi', { exact: true }).click(); await sh();
  await nome.fill('Sara Conti'); await p.getByText('Aggiungi', { exact: true }).click(); await sh();
  console.log('--- \n' + (await p.locator('body').innerText()).slice(0, 900));
  const copia = p.getByText('Copia', { exact: true });
  console.log('copia', await copia.count());
  if (await copia.count()) { await copia.first().click(); await p.waitForTimeout(1000); await sh(); }
  if (await copia.count()) { await copia.first().click(); await p.waitForTimeout(1000); await sh(); }
  await p.getByText('Continua', { exact: true }).click(); await p.waitForTimeout(2000); await sh();
  console.log('--- fine\n' + (await p.locator('body').innerText()).slice(0, 900));
  await b.close();
})();
