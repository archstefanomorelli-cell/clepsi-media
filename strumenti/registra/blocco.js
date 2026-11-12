// La schermata di blocco del telefono con la notifica di Clepsi, disegnata dentro la pagina (il browser non mostra
// notifiche vere). I testi delle notifiche sono quelli veri di invia-domande (supabase/functions/invia-domande/testi.ts).
const LOGO = "<svg width='24' height='24' viewBox='0 0 22 22'><circle cx='11' cy='11' r='9.5' fill='none' stroke='#D4FF3A' stroke-width='1.5'/><path d='M11 1.5 A9.5 9.5 0 0 0 11 20.5 Z' fill='#D4FF3A'/></svg>";
async function mostra(p, { data, ora, titolo, testo }) {
  await p.evaluate(([LOGO, data, ora, titolo, testo]) => {
    const d = document.createElement('div'); d.id = '__blocco';
    d.style.cssText = "position:fixed;inset:0;z-index:99990;color:#fff;font-family:'DMSans_400Regular',sans-serif;" +
      'background:radial-gradient(circle at 75% 18%,rgba(212,255,58,.10),transparent 55%),linear-gradient(180deg,#1E2130 0%,#14151B 55%,#0B0B0D 100%)';
    d.innerHTML = `
      <svg width="14" height="18" viewBox="0 0 14 18" style="position:absolute;left:200px;top:52px;opacity:.9"><rect x="1" y="8" width="12" height="9" rx="2" fill="#fff"/><path d="M3.5 8V5.5a3.5 3.5 0 0 1 7 0V8" stroke="#fff" stroke-width="1.8" fill="none"/></svg>
      <div style="position:absolute;left:0;right:0;top:86px;text-align:center;font-size:20px;opacity:.85">${data}</div>
      <div id="__ora" style="position:absolute;left:0;right:0;top:106px;text-align:center;font-size:96px;letter-spacing:-3px;font-family:'BricolageGrotesque_800ExtraBold',sans-serif">${ora}</div>
      <div id="__notifica" style="position:absolute;left:12px;right:12px;top:268px;border-radius:22px;padding:14px;display:flex;gap:12px;background:rgba(58,58,66,.78);opacity:0">
        <div style="width:40px;height:40px;border-radius:10px;background:#0B0B0D;display:flex;align-items:center;justify-content:center;flex:none">${LOGO}</div>
        <div style="flex:1;min-width:0">
          <div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px"><span style="font-size:16px;font-weight:700">${titolo}</span><span style="font-size:13px;opacity:.55">ora</span></div>
          <div style="font-size:16px;opacity:.9;margin-top:3px">${testo}</div>
        </div>
      </div>
      <div style="position:absolute;left:44px;bottom:58px;width:50px;height:50px;border-radius:50%;background:rgba(255,255,255,.14)"></div>
      <div style="position:absolute;right:44px;bottom:58px;width:50px;height:50px;border-radius:50%;background:rgba(255,255,255,.14)"></div>
      <div style="position:absolute;left:140px;right:140px;bottom:9px;height:5px;border-radius:3px;background:#fff"></div>`;
    document.body.appendChild(d);
  }, [LOGO, data, ora, titolo, testo]);
}
const cambiaOra = (p, ora) => p.evaluate(o => { document.getElementById('__ora').textContent = o; }, ora);
// la notifica scende dall'alto (0,4 s); il suono parte con lei (un tocco senza dito, per il composer)
async function arriva(p, r) {
  r.taps.push(r.n); r.salva();
  const n = 12;
  for (let i = 1; i <= n; i++) {
    const k = i / n, e = 1 - Math.pow(1 - k, 3);
    await p.evaluate(([e, k]) => { const c = document.getElementById('__notifica'); c.style.opacity = Math.min(1, k * 1.6); c.style.transform = `translateY(${-70 * (1 - e)}px) scale(${0.93 + 0.07 * e})`; }, [e, k]);
    await r.frame();
  }
}
const togli = p => p.evaluate(() => document.getElementById('__blocco').remove());
module.exports = { mostra, cambiaOra, arriva, togli };
