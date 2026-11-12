// Finto backend per un account nuovo (nessuno studio): serve a riprendere la creazione di studio, commessa e team.
// Niente esce dal computer: create_studio, inviti e notifiche rispondono qui.
const B64 = s => Buffer.from(JSON.stringify(s)).toString('base64url');
const UID = '00000000-0000-4000-8000-0000000000aa';
const JWT = B64({ alg: 'HS256', typ: 'JWT' }) + '.' + B64({ sub: UID, role: 'authenticated', aud: 'authenticated', exp: 4102444800 }) + '.x';
const USER = { id: UID, aud: 'authenticated', role: 'authenticated', email: 'titolare@studio.it', app_metadata: { provider: 'email' }, user_metadata: {}, identities: [], created_at: '2026-11-12T08:00:00Z' };
const SESSION = { access_token: JWT, token_type: 'bearer', expires_in: 31536000, expires_at: 4102444800, refresh_token: 'nuovo', user: USER };
const CORS = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*', 'access-control-expose-headers': '*' };
async function prepara(ctx, { log = false } = {}) {
  await ctx.addInitScript(([k, v]) => { if (!sessionStorage.getItem('__ok')) { localStorage.clear(); localStorage.setItem(k, v); sessionStorage.setItem('__ok', '1'); } }, ['sb-pabxblvvikxgrvigxsfv-auth-token', JSON.stringify(SESSION)]);
  // notifiche già attive, come su un telefono dove l'utente ha detto sì
  await ctx.addInitScript(() => { try { Object.defineProperty(Notification, 'permission', { get: () => 'granted' }); } catch {} });
  const S = { studio: null, nome: '', persone: [], progetti: [], n: 0 };
  const id = p => `${p}-0000-4000-8000-${String(++S.n).padStart(12, '0')}`;
  await ctx.route('https://pabxblvvikxgrvigxsfv.supabase.co/**', async route => {
    const r = route.request(); const u = new URL(r.url()); const p = decodeURIComponent(u.pathname + u.search); const m = r.method();
    if (m === 'OPTIONS') return route.fulfill({ status: 200, headers: CORS, body: '' });
    let body = null; try { body = r.postDataJSON(); } catch {}
    const single = (r.headers()['accept'] || '').includes('vnd.pgrst.object');
    const ok = (x, extra = {}) => route.fulfill({ status: 200, headers: { ...CORS, 'content-type': 'application/json', ...extra }, body: JSON.stringify(x) });
    if (log) console.log(m, p.slice(0, 160), body ? JSON.stringify(body).slice(0, 160) : '');
    if (u.pathname.startsWith('/auth/v1/user')) return ok(USER);
    if (u.pathname.startsWith('/functions/v1/')) return ok({});
    if (p.includes('/rpc/create_studio')) { S.studio = id('51d10000'); S.nome = body.p_name; S.persone.push({ id: id('aaaa0000'), name: body.p_my_name, role: 'admin', user_id: UID, status: 'active' }); return ok(S.studio); }
    if (p.includes('/rpc/create_project')) { const x = id('c0c00000'); S.progetti.push({ id: x, ...body }); return ok(x); }
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
    if (p.includes('/rest/v1/studios')) { const row = { id: S.studio, name: S.nome, timezone: 'Europe/Rome', evening_time: '19:00:00', evening_days: [1, 2, 3, 4, 5], reminder_enabled: true, reminder_delay_minutes: 120, currency: 'EUR' }; return ok(single ? row : [row]); }
    if (p.includes('/rest/v1/phases') && single) return ok({ id: id('fa5e0000') });
    if (single) return ok({});
    return ok([], { 'content-range': '*/0' });
  });
  return S;
}
module.exports = { prepara, UID };
