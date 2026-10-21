import subprocess, pathlib
from playwright.sync_api import sync_playwright
LOGO = lambda col: f'<svg width="44" height="44" viewBox="0 0 22 22"><circle cx="11" cy="11" r="9.5" fill="none" stroke="{col}" stroke-width="1.6"></circle><path d="M11 1.5 A9.5 9.5 0 0 0 11 20.5 Z" fill="{col}"></path></svg>'
def render_pngs(items, outdir):
    """items: {name: html_body} → PNG 1080x1920 trasparenti"""
    outdir = pathlib.Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        for name, body in items.items():
            pg.set_content(f"<!doctype html><html lang='it'><head><meta charset='utf-8'><style>html,body{{margin:0;background:transparent}}*{{box-sizing:border-box}}body{{width:1080px;height:1920px;position:relative;font-family:'DM Sans',sans-serif;color:#F6F5F1}}.b{{font-family:'Bricolage Grotesque',sans-serif;font-weight:800}}</style></head><body>{body}</body></html>")
            pg.evaluate('document.fonts.ready')
            pg.screenshot(path=str(outdir / f'{name}.png'), omit_background=True)
        b.close()
def overlay(base, ovs, out, audio=None, extra_audio_filter=''):
    """ovs: list of (png, start, end, fin, fout)"""
    args = ['ffmpeg', '-v', 'error', '-y', '-i', base]
    for png, s, e, fi, fo in ovs: args += ['-loop', '1', '-t', f'{e - s:.3f}', '-i', png]
    if audio: args += ['-i', audio]
    fc = []; last = '0:v'
    for k, (png, s, e, fi, fo) in enumerate(ovs):
        d = e - s
        f = 'format=rgba'
        if fi > 0: f += f',fade=t=in:st=0:d={fi}:alpha=1'
        if fo > 0: f += f',fade=t=out:st={max(0, d - fo):.3f}:d={fo}:alpha=1'
        fc.append(f'[{k+1}:v]{f},setpts=PTS-STARTPTS+{s:.3f}/TB[o{k}]')
        fc.append(f'[{last}][o{k}]overlay=0:0:eof_action=pass:enable=\'between(t,{s:.3f},{e:.3f})\'[v{k}]'); last = f'v{k}'
    args += ['-filter_complex', ';'.join(fc), '-map', f'[{last}]']
    if audio: args += ['-map', f'{len(ovs)+1}:a', '-c:a', 'aac', '-b:a', '192k']
    args += ['-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart', '-shortest', out]
    subprocess.run(args, check=True)
