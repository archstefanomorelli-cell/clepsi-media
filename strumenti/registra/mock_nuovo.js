// Finto backend per un account nuovo (nessuno studio): serve a riprendere la creazione di studio, commessa e team.
// Niente esce dal computer: create_studio, inviti e notifiche rispondono qui.
const B64 = s => Buffer.from(JSON.stringify(s)).toString('base64url');
const UID = '00000000-0000-4000-8000-0000000000aa';
const JWT = B64({ alg: 'HS256', typ: 'JWT' }) + '.' + B64({ sub: UID, role: 'authenticated', aud: 'authenticated', exp: 4102444800 }) + '.x';
const USER = { id: UID, aud: 'authenticated', role: 'authenticated', email: 'titolare@studio.it', app_metadata: { provider: 'email' }, user_metadata: {}, identities: [], created_at: '2026-11-12T08:00:00Z' };
const SESSION = { access_token: JWT, token_type: 'bearer', expires_in: 31536000, expires_at: 4102444800, refresh_token: 'nuovo', user: USER };
const CORS = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*', 'access-control-expose-headers': '*' };
async function prepara(ctx, { log = false, studio = null } = {}) {
  await ctx.addInitScript(([k, v]) => { if (!sessionStorage.getItem('__ok')) { localStorage.clear(); localStorage.setItem(k, v); sessionStorage.setItem('__ok', '1'); } }, ['sb-pabxblvvikxgrvigxsfv-auth-token', JSON.stringify(SESSION)]);
  // notifiche già attive, come su un telefono dove l'utente ha detto sì
  await ctx.addInitScript(() => { try { Object.defineProperty(Notification, 'permission', { get: () => 'granted' }); } catch {} });
  const S = { studio: null, nome: '', persone: [], progetti: [], n: 0 };
  const id = p => `${p}-0000-4000-8000-${String(++S.n).padStart(12, '0')}`;
  // studio già avviato (per le riprese che partono da un titolare con lo studio pronto)
  if (studio) { S.studio = id('51d10000'); S.nome = studio.nome; S.persone.push({ id: id('aaaa0000'), name: studio.io, role: 'admin', user_id: UID, status: 'active' }); for (const n of studio.persone || []) S.persone.push({ id: id('bbbb0000'), name: n, role: 'collaborator', status: 'active' }); }
  await ctx.route('https://pabxblvvikxgrvigxsfv.supabase.co/**', async route => {
    const r = route.request(); const u = new URL(r.url()); const p = decodeURIComponent(u.pathname + u.search); const m = r.method();
    if (m === 'OPTIONS') return route.fulfill({ status: 200, headers: CORS, body: '' });
    let body = null; try { body = r.postDataJSON(); } catch {}
    const single = (r.headers()['accept'] || '').includes('vnd.pgrst.object');
    const ok = (x, extra = {}) => route.fulfill({ status: 200, headers: { ...CORS, 'content-type': 'application/json', ...extra }, body: JSON.stringify(x) });
    if (log) console.log(m, p.slice(0, 160), body ? JSON.stringify(body).slice(0, 160) : '');
    if (u.pathname.startsWith('/auth/v1/user')) return ok(USER);
    if (p.includes('/functions/v1/conti-commesse') && body && body.commessa) return ok(conti(body.commessa));
    if (p.includes('/functions/v1/parcella-apri')) { S.datiParcella = body && body.dati; return ok({ link: 'http://localhost:8765/parcella/K7M2Q9' }); }
    if (u.pathname.startsWith('/functions/v1/')) return ok({});
    if (p.includes('/rpc/create_studio')) { S.studio = id('51d10000'); S.nome = body.p_name; S.persone.push({ id: id('aaaa0000'), name: body.p_my_name, role: 'admin', user_id: UID, status: 'active' }); return ok(S.studio); }
    if (p.includes('/rpc/create_project')) { const x = id('c0c00000'); S.progetti.push({ id: x, ...body }); return ok(x); }
    if (p.includes('/rpc/parcel_preview')) return ok(S.parcella ? { total_cents: S.parcella.totaleCent, days: S.parcella.giornate, phases: S.parcella.fasi.map(f => ({ name: f.nome, fee_cents: f.cent })) } : null);
    if (p.includes('/rpc/claim_parcel')) { const x = id('c0c00000'); S.progetti.push({ id: x, name: body.p_name, code: body.p_project_code, color: body.p_color, parcella: true }); return ok(x); }
    if (p.includes('/rpc/create_invite')) return ok('INVITO' + S.n);
    if (u.pathname.startsWith('/rest/v1/rpc/')) return ok(null);
    if (m === 'POST' && p.includes('/rest/v1/members')) { const x = { id: id('bbbb0000'), ...body }; S.persone.push(x); return ok(single ? { id: x.id } : [{ id: x.id }]); }
    if (m === 'PATCH') return ok(single ? {} : []);
    if (m === 'HEAD') return route.fulfill({ status: 200, headers: { ...CORS, 'content-range': '*/0' }, body: '' });
    if (p.includes('/rest/v1/members') && p.includes(`user_id=eq.${UID}`)) {
      const me = S.persone.find(x => x.user_id === UID);
      if (!me) return ok(single ? null : []);
      const row = { id: me.id, name: me.name, role: 'admin', studio_id: S.studio, studios: { name: S.nome } };
      return ok(single ? row : [row]);
    }
    const pr = p.match(/projects\?select=name.*id=eq\.([0-9a-f-]+)/);
    if (pr) { const x = S.progetti.find(q => q.id === pr[1]) || {}; const me = S.persone.find(q => q.user_id === UID); return ok({ name: x.name, code: x.code, color: x.color, assignment_type: null, lead_member_id: me.id, status: 'active', parcel_id: x.parcella ? 'a1b2c3d4-0000-4000-8000-000000000001' : null }); }
    if (p.includes('/rest/v1/members?select=sounds_enabled')) return ok({ sounds_enabled: true });
    if (p.includes('/rest/v1/members?select=id,name&studio_id')) return ok(S.persone.map(q => ({ id: q.id, name: q.name })));
    if (p.includes('/rest/v1/studios')) { const row = { id: S.studio, name: S.nome, timezone: 'Europe/Rome', evening_time: '19:00:00', evening_days: [1, 2, 3, 4, 5], reminder_enabled: true, reminder_delay_minutes: 120, currency: 'EUR' }; return ok(single ? row : [row]); }
    if (p.includes('/rest/v1/phases') && single) return ok({ id: id('fa5e0000') });
    if (single) return ok({});
    return ok([], { 'content-range': '*/0' });
  });
  // i conti di una commessa appena nata: nessuna giornata ancora, budget delle fasi dal compenso
  function conti(cid) {
    const x = S.progetti.find(q => q.id === cid); const costo = S.costoGiornataCent || 32000, margine = S.margine ?? 0.25;
    const fasi = (x && x.parcella ? S.parcella.fasi : []).map((f, i) => ({ id: `fa5e${i}000-0000-4000-8000-${cid.slice(-12)}`, compensoCent: f.cent, stato: 'todo', giornateBudget: Math.round(f.cent * (1 - margine) / costo * 2) / 2, giornateUsate: 0, oltreBudget: false, nome: f.nome }));
    const tot = fasi.reduce((a, f) => a + f.compensoCent, 0); const me = S.persone.find(q => q.user_id === UID);
    return { costoMedioCent: costo, resaPerTipo: null, commesse: [{ id: cid, compensoCent: tot, variantiPagateCent: 0, giornateUsate: 0, costoMezzeCent: 0, costiFinoraCent: 0, mezzeSenzaCosto: 0, lavoroFatto: 0, costiPrevistiCent: null, marginePrevistoCent: null, stato: 'iniziata', costoGiornataCommessaCent: costo, giornateCoperte: tot / costo, giornateServono: null, resaGiornataCent: null, fasi, persone: [], variantiMezze: 0, variantiValoreCent: 0, settimana: { lunedi: '2026-11-09', mezze: 0, costoMezzaCent: 0, varianti: 0 }, responsabileId: me.id, venerdi: { settimana: '2026-11-09', rispostaAlle: null, rispostaDa: null }, previsioneFerma: false, chiusura: null }] };
  }
  return S;
}
module.exports = { prepara, UID };
