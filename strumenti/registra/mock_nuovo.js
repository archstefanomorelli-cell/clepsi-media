// Finto backend per un account nuovo (nessuno studio): serve a riprendere la creazione di studio, commessa e team.
// Niente esce dal computer: create_studio, inviti e notifiche rispondono qui.
const B64 = s => Buffer.from(JSON.stringify(s)).toString('base64url');
const UID = '00000000-0000-4000-8000-0000000000aa';
const JWT = B64({ alg: 'HS256', typ: 'JWT' }) + '.' + B64({ sub: UID, role: 'authenticated', aud: 'authenticated', exp: 4102444800 }) + '.x';
const USER = { id: UID, aud: 'authenticated', role: 'authenticated', email: 'titolare@studio.it', app_metadata: { provider: 'email' }, user_metadata: {}, identities: [], created_at: '2026-11-12T08:00:00Z' };
const SESSION = { access_token: JWT, token_type: 'bearer', expires_in: 31536000, expires_at: 4102444800, refresh_token: 'nuovo', user: USER };
const CORS = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*', 'access-control-expose-headers': '*' };
async function prepara(ctx, { log = false, studio = null, invito = null, commesse = [], giorniFatti = [], giorniLavoro = null, sono = null, resaPerTipo = null } = {}) {
  await ctx.addInitScript(([k, v]) => { if (!sessionStorage.getItem('__ok')) { localStorage.clear(); if (v) localStorage.setItem(k, v); sessionStorage.setItem('__ok', '1'); } }, ['sb-pabxblvvikxgrvigxsfv-auth-token', invito ? '' : JSON.stringify(SESSION)]);
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
    if (log) console.log(m, p.slice(0, 160), body ? JSON.stringify(body).slice(0, 700) : '');
    if (u.pathname.startsWith('/auth/v1/user')) return ok(USER);
    if (u.pathname.startsWith('/auth/v1/otp')) return ok({});
    if (u.pathname.startsWith('/auth/v1/verify')) return ok(SESSION);
    if (p.includes('/rpc/invite_preview')) return ok({ status: 'valid', studio_name: S.nome, member_name: invito.nome, role: 'collaborator', email: null });
    if (p.includes('/rpc/accept_invite')) { const x = S.persone.find(q => q.name === invito.nome); x.user_id = UID; S.persone.forEach(q => { if (q !== x && q.user_id === UID) q.user_id = null; }); return ok(null); }
    if (p.includes('/functions/v1/conti-commesse') && body && body.commessa) return ok(conti(body.commessa));
    if (p.includes('/functions/v1/conti-commesse') && S.progetti.some(q => q.dati)) return ok({ costoMedioCent: S.costoGiornataCent || 32000, resaPerTipo: null, commesse: S.progetti.map(contiDi) });
    if (p.includes('/functions/v1/parcella-apri')) { S.datiParcella = body && body.dati; return ok({ link: 'http://localhost:8765/parcella/K7M2Q9' }); }
    if (u.pathname.startsWith('/functions/v1/')) return ok({});
    if (p.includes('/rpc/create_studio')) { S.studio = id('51d10000'); S.nome = body.p_name; S.persone.push({ id: id('aaaa0000'), name: body.p_my_name, role: 'admin', user_id: UID, status: 'active' }); return ok(S.studio); }
    if (p.includes('/rpc/create_project')) { const x = id('c0c00000'); S.progetti.push({ id: x, ...body }); return ok(x); }
    if (p.includes('/rpc/parcel_preview')) return ok(S.parcella ? { total_cents: S.parcella.totaleCent, days: S.parcella.giornate, phases: S.parcella.fasi.map(f => ({ name: f.nome, fee_cents: f.cent })) } : null);
    if (p.includes('/rpc/claim_parcel')) { const x = id('c0c00000'); S.progetti.push({ id: x, name: body.p_name, code: body.p_project_code, color: body.p_color, parcella: true }); return ok(x); }
    if (p.includes('/rpc/save_half_day')) { S.salvate = (S.salvate || 0) + 1; if (body && body.p_day && body.p_half) { const it = (body.p_items || [])[0] || {}; S.mezze = S.mezze.filter(x => !(x.day === body.p_day && x.half === body.p_half)); S.mezze.push({ day: body.p_day, half: body.p_half, kind: it.kind || 'project', project_id: it.project_id || null, phase_id: it.phase_id || null }); } return ok(null); }
    if (p.includes('/rpc/save_friday')) { for (const f of body.p_phases || []) { const x = S.fasi.find(q => q.id === f.id); if (x) x.status = f.status; } S.varianti = S.varianti || {}; S.varianti[body.p_project] = body.p_variants || 0; S.venerdiAlle = S.oraVenerdi || '2026-11-13T16:32:00+00:00'; return ok(null); }
    if (p.includes('/rpc/close_project')) { const x = S.progetti.find(q => q.id === body.p_project); if (x) { x.status = 'closed'; x.chiusaIl = '2026-11-12'; } return ok(null); }
    if (p.includes('/rpc/create_invite')) return ok('INVITO' + S.n);
    if (u.pathname.startsWith('/rest/v1/rpc/')) return ok(null);
    if (m === 'POST' && p.includes('/rest/v1/members')) { const x = { id: id('bbbb0000'), ...body }; S.persone.push(x); return ok(single ? { id: x.id } : [{ id: x.id }]); }
    if (m === 'PATCH') return ok(single ? {} : []);
    if (m === 'HEAD') return route.fulfill({ status: 200, headers: { ...CORS, 'content-range': '*/0' }, body: '' });
    if (p.includes('/rest/v1/members') && p.includes(`user_id=eq.${UID}`)) {
      const me = S.persone.find(x => x.user_id === UID);
      if (!me) return ok(single ? null : []);
      const row = { id: me.id, name: me.name, role: me.role, studio_id: S.studio, studios: { name: S.nome } };
      return ok(single ? row : [row]);
    }
    const pr = p.match(/projects\?select=name.*id=eq\.([0-9a-f-]+)/);
    if (pr) { const x = S.progetti.find(q => q.id === pr[1]) || {}; const me = S.persone.find(q => q.user_id === UID); return ok({ name: x.name, code: x.code, color: x.color, assignment_type: (x.dati && x.dati.tipo) || null, lead_member_id: me.id, status: x.status || 'active', parcel_id: x.parcella ? 'a1b2c3d4-0000-4000-8000-000000000001' : null }); }
    if (giorniLavoro && p.includes('/rest/v1/members?select=work_days')) return ok({ work_days: giorniLavoro, evening_time: null });
    if (p.includes('/rest/v1/members?select=sounds_enabled')) return ok({ sounds_enabled: true });
    if (p.includes('/rest/v1/members?select=id,name&studio_id')) return ok(S.persone.map(q => ({ id: q.id, name: q.name })));
    const admin = () => S.persone.find(q => q.role === 'admin');
    if (m === 'GET' && p.includes('/rest/v1/phases?select=') && !single) { const pr = (p.match(/project_id=eq\.([0-9a-f-]+)/) || [])[1]; return ok(S.fasi.filter(f => !pr || f.project_id === pr)); }
    if (p.includes('/rest/v1/projects?select=id,name,color')) return ok(S.progetti.map(q => ({ id: q.id, name: q.name, color: q.color })));
    if (p.includes('/rest/v1/projects?select=id,name,code,color')) return ok(S.progetti.map(q => ({ id: q.id, name: q.name, code: q.code, color: q.color, lead_member_id: admin().id })));
    if (p.includes('/rest/v1/project_members?select=project_id')) return ok(S.progetti.map(q => ({ project_id: q.id })));
    if (p.includes('/rest/v1/half_days?select=day,half,kind')) { const pr = S.progetti[0]; return ok([...S.mezze, ...giorniFatti.flatMap(d => ['am', 'pm'].map(h => ({ day: d, half: h, kind: 'project', project_id: pr.id, phase_id: null })))]); }
    if (p.includes('/rest/v1/half_days?select=half&')) { const d = (p.match(/day=eq\.([\d-]+)/) || [])[1]; return ok(S.mezze.filter(m => m.day === d).map(m => ({ half: m.half }))); }
    if (p.includes('/rest/v1/studios')) { const row = { id: S.studio, name: S.nome, timezone: 'Europe/Rome', evening_time: '19:00:00', evening_days: [1, 2, 3, 4, 5], reminder_enabled: true, reminder_delay_minutes: 120, currency: 'EUR' }; return ok(single ? row : [row]); }
    if (p.includes('/rest/v1/phases') && single) return ok({ id: id('fa5e0000') });
    if (single) return ok({});
    return ok([], { 'content-range': '*/0' });
  });
  // i conti di una commessa appena nata: nessuna giornata ancora, budget delle fasi dal compenso
  function conti(cid) {
    const x = S.progetti.find(q => q.id === cid);
    if (x && x.dati) return { costoMedioCent: S.costoGiornataCent || 32000, resaPerTipo: x.status === 'closed' ? resaPerTipo : null, commesse: [contiDi(x)] };
    const costo = S.costoGiornataCent || 32000, margine = S.margine ?? 0.25;
    const fasi = (x && x.parcella ? S.parcella.fasi : []).map((f, i) => ({ id: `fa5e${i}000-0000-4000-8000-${cid.slice(-12)}`, compensoCent: f.cent, stato: 'todo', giornateBudget: Math.round(f.cent * (1 - margine) / costo * 2) / 2, giornateUsate: 0, oltreBudget: false, nome: f.nome }));
    const tot = fasi.reduce((a, f) => a + f.compensoCent, 0); const me = S.persone.find(q => q.user_id === UID);
    return { costoMedioCent: costo, resaPerTipo: null, commesse: [{ id: cid, compensoCent: tot, variantiPagateCent: 0, giornateUsate: 0, costoMezzeCent: 0, costiFinoraCent: 0, mezzeSenzaCosto: 0, lavoroFatto: 0, costiPrevistiCent: null, marginePrevistoCent: null, stato: 'iniziata', costoGiornataCommessaCent: costo, giornateCoperte: tot / costo, giornateServono: null, resaGiornataCent: null, fasi, persone: [], variantiMezze: 0, variantiValoreCent: 0, settimana: { lunedi: '2026-11-09', mezze: 0, costoMezzaCent: 0, varianti: 0 }, responsabileId: me.id, venerdi: { settimana: '2026-11-09', rispostaAlle: null, rispostaDa: null }, previsioneFerma: false, chiusura: null }] };
  }
  // i conti di una commessa già avviata, come li fa conti-commesse (margine.ts): lavoro fatto dagli stati delle fasi,
  // costi finora dalle giornate usate, previsione = costi finora ÷ lavoro fatto
  function contiDi(x) {
    const costo = S.costoGiornataCent || 32000, margine = S.margine ?? 0.25, d = x.dati || {};
    const PESO = { todo: 0, started: 0.2, half: 0.5, almost: 0.85, done: 1 };
    const fp = S.fasi.filter(f => f.project_id === x.id);
    const tot = fp.reduce((a, f) => a + f.fee_cents, 0);
    const fatto = tot > 0 ? fp.reduce((a, f) => a + f.fee_cents * PESO[f.status], 0) / tot : 0;
    const usate = d.giornate || 0, costoMezze = Math.round(usate * costo);
    let costiPrev = null, margPrev = null;
    if (fatto >= 0.05 && costoMezze > 0) { costiPrev = Math.round(costoMezze / fatto); margPrev = tot - costiPrev; }
    const stato = margPrev == null ? 'iniziata' : margPrev < 0 ? 'perdita' : margPrev < tot * 0.15 ? 'guardare' : 'bene';
    const var_ = (S.varianti || {})[x.id] || 0, varTot = (d.variantiPrima || 0) + var_;
    const me = S.persone.find(q => q.user_id === UID);
    const out = { id: x.id, compensoCent: tot, variantiPagateCent: 0, giornateUsate: usate, costoMezzeCent: costoMezze, costiFinoraCent: costoMezze, mezzeSenzaCosto: 0, lavoroFatto: fatto,
      costiPrevistiCent: costiPrev, marginePrevistoCent: margPrev, stato, costoGiornataCommessaCent: costo, giornateCoperte: (tot - costoMezze) / costo,
      giornateServono: costiPrev ? usate / fatto - usate : null, resaGiornataCent: costiPrev ? Math.round(tot / (usate / fatto)) : null,
      fasi: fp.map((f, j) => { const b = Math.round(f.fee_cents * (1 - margine) / costo * 2) / 2, u = (d.giornateFasi || [])[j] || 0; return { id: f.id, compensoCent: f.fee_cents, stato: f.status, giornateBudget: b, giornateUsate: u, oltreBudget: u > b, nome: f.name }; }),
      persone: (d.persone || []).map(([n, g]) => { const q = S.persone.find(z => z.name === n); return { personaId: q ? q.id : n, giornate: g, nome: n }; }),
      variantiMezze: varTot, variantiValoreCent: Math.round(varTot * costo / 2),
      settimana: { lunedi: '2026-11-09', mezze: d.mezzeSettimana || 0, costoMezzaCent: Math.round(costo / 2), varianti: var_ },
      responsabileId: me ? me.id : null, venerdi: { settimana: '2026-11-09', rispostaAlle: S.venerdiAlle || null, rispostaDa: S.venerdiAlle && me ? { id: me.id, nome: me.name } : null },
      previsioneFerma: false, chiusura: null };
    if (x.status === 'closed') {          // il bilancio come bilancioChiusura (chiusura.ts)
      const c = out, budget = c.fasi.reduce((a, f) => a + f.giornateBudget, 0), guadagno = c.compensoCent - c.costiFinoraCent;
      c.chiusura = { stato: 'closed', chiusaIl: x.chiusaIl, tipo: d.tipo || null,
        bilancio: { compensoCent: c.compensoCent, variantiPagateCent: 0, costiCent: c.costiFinoraCent, speseCent: 0, guadagnoCent: guadagno, margine: c.compensoCent > 0 ? guadagno / c.compensoCent : null,
          margineDesiderato: margine, giornateUsate: usate, giornateBudget: budget, giornateOltre: usate - budget, resaGiornataCent: usate > 0 ? Math.round(c.compensoCent / usate) : null,
          fasi: c.fasi.map(f => ({ id: f.id, giornateUsate: f.giornateUsate, giornateBudget: f.giornateBudget, scarto: f.giornateUsate - f.giornateBudget })), variantiMezze: c.variantiMezze, variantiValoreCent: c.variantiValoreCent },
        varianti: (d.variantiSettimane || []).map(([settimana, mezze]) => ({ settimana, mezze })) };
    }
    return out;
  }
  // commesse già avviate dello studio (per le riprese del collaboratore e del venerdì)
  const COLORI = ['#D4FF3A', '#9B8CFF', '#FF9ECF', '#6FD3FF', '#FFB86B'];
  S.fasi = [];
  commesse.forEach((c, i) => {
    const pid = id('c0c00000');
    S.progetti.push({ id: pid, name: c.nome, code: c.sigla, color: c.colore || COLORI[i % COLORI.length], dati: c });
    (c.fasi || []).forEach((f, j) => S.fasi.push({ id: id('fa5e0000'), project_id: pid, name: f.nome, position: j + 1, status: f.stato || 'todo', fee_cents: f.cent || 0 }));
  });
  S.mezze = [];
  // entrare come un collaboratore dello studio invece che come titolare
  if (sono) S.persone.forEach(q => { q.user_id = q.name === sono ? UID : (q.user_id === UID ? null : q.user_id); });
  return S;
}
module.exports = { prepara, UID };
