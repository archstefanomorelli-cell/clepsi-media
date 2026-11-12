const fs = require('fs');
const DATA = JSON.parse(fs.readFileSync(__dirname + '/mock.json', 'utf8'));
const B64 = s => Buffer.from(JSON.stringify(s)).toString('base64url');
const JWT = B64({alg:'HS256',typ:'JWT'}) + '.' + B64({sub:'b3484d45-dc2c-4695-9d4e-8caa50a7b883',role:'authenticated',aud:'authenticated',exp:4102444800,is_anonymous:true}) + '.x';
const USER = {"app_metadata":{},"aud":"authenticated","created_at":"2026-11-12T07:32:06.948277Z","email":"","id":"b3484d45-dc2c-4695-9d4e-8caa50a7b883","identities":[],"is_anonymous":true,"phone":"","role":"authenticated","user_metadata":{}};
const SESSION = {access_token:JWT,token_type:'bearer',expires_in:3600*24*365,expires_at:4102444800,refresh_token:'demo',user:USER};
const LS = {
  'clepsi.modo':'esempio',
  'clepsi.appartenenza.esempio': JSON.stringify({utente:USER.id,appartenenza:{memberId:'ce893d87-b0f6-4cb7-99d5-e394b5ad0572',nome:'Marta Rossi',ruolo:'admin',studioId:'5145620a-7b8f-4cfa-a730-74a78f571380',nomeStudio:'Studio di esempio'}}),
  'sb-pabxblvvikxgrvigxsfv-esempio-auth-token': JSON.stringify(SESSION),
};
const CORS = {'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*','access-control-expose-headers':'*'};
async function prepara(ctx, opz = {}) {
  await ctx.addInitScript(ls => { for (const [k, v] of Object.entries(ls)) localStorage.setItem(k, v); }, LS);
  const extra = opz.extra || {};
  await ctx.route('https://pabxblvvikxgrvigxsfv.supabase.co/**', async route => {
    const r = route.request(); const u = new URL(r.url()); const p = u.pathname + u.search; const m = r.method();
    if (m === 'OPTIONS') return route.fulfill({status: 200, headers: CORS, body: ''});
    const body = r.postData() || null;
    for (const [k, f] of Object.entries(extra)) if (p.includes(k)) { const res = f(p, body); return route.fulfill({status: res.s || 200, headers: {...CORS, 'content-type': 'application/json'}, body: res.t}); }
    let hit = DATA.find(d => d.m === m && d.u === p && (m === 'GET' || m === 'HEAD' || (d.b || '') === (body || '')));
    if (!hit) hit = DATA.find(d => d.m === m && d.u === p);
    if (hit) return route.fulfill({status: hit.s, headers: {...CORS, 'content-type': hit.ct || 'application/json', ...(hit.cr ? {'content-range': hit.cr} : {})}, body: hit.t});
    if (u.pathname.startsWith('/auth/v1/user')) return route.fulfill({status: 200, headers: {...CORS, 'content-type': 'application/json'}, body: JSON.stringify(USER)});
    if (u.pathname.startsWith('/rest/v1/rpc/')) { console.log('RPC', m, p, body); return route.fulfill({status: 200, headers: {...CORS, 'content-type': 'application/json'}, body: 'null'}); }
    console.log('MISS', m, p, body);
    return route.fulfill({status: 200, headers: {...CORS, 'content-type': 'application/json', 'content-range': '*/0'}, body: m === 'HEAD' ? '' : '[]'});
  });
}
module.exports = { prepara };
