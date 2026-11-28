# Builds gta6-site-upload.zip for Cloudflare Pages.
# Stamps a fresh version on app.js / data.js / scene.js / style.css in every HTML page
# so browsers always load the newest code after a deploy (fixes "I still see the old site").
import os, re, time, zipfile, sys
root = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(root, "gta6-site")
ver = time.strftime("%Y%m%d%H%M")
pat = re.compile(r'(src|href)="(/?(?:app\.js|data\.js|scene\.js|style\.css))(\?v=[^"]*)?"')
n = 0
# speed (LCP): static copy of the header bar (logo + English menu) so it paints before app.js runs; app.js replaces #ssrBar
_data = open(os.path.join(src, "data.js"), encoding="utf-8").read()
_pages = re.findall(r'\{ id:"([a-z]+)",\s*href:"([^"]+)",\s*icon:"[^"]*",\s*nav:"(\w+)"', _data)
_label = {}
for k, v in re.findall(r'(nav[A-Z]\w*):"([^"]*)"', _data): _label.setdefault(k, v)   # first = English
def ssr_bar(fn):
    links = "".join(f'<a href="{h}" class="{"cur" if h == fn else ""}">{_label.get(k, "")}</a>' for i, h, k in _pages if i != "home")
    return ('<div class="bar" id="ssrBar"><div class="wrap"><a class="brand" href="index.html" aria-label="GamerBhai home">'
            '<img src="img/icons/icon-192.png" alt="" width="30" height="30"><span>GAMER<b>BHAI</b></span></a>'
            f'<nav class="links">{links}</nav></div></div>')
for fn in os.listdir(src):
    if fn.endswith(".html"):
        p = os.path.join(src, fn)
        s = open(p, encoding="utf-8").read()
        t = pat.sub(lambda m: f'{m.group(1)}="{m.group(2)}?v={ver}"', s)
        # speed: Google Fonts must not block rendering (slow/blocked in some countries) -> load async, show fallback font first
        t = re.sub(r'<link href="(https://fonts\.googleapis\.com/css2\?[^"]+)" rel="stylesheet">',
                   lambda m: '<link rel="preload" as="style" href="' + m.group(1) + '" onload="this.onload=null;this.rel=\'stylesheet\'"><noscript><link rel="stylesheet" href="' + m.group(1) + '"></noscript>', t)
        if 'id="ssrBar"' not in t and _pages:
            t = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + "\n" + ssr_bar(fn), t, count=1)
        if fn == "index.html":  # speed: self-host three.js (cdnjs is slow/blocked in some countries) and let all scripts load without blocking first paint
            t = re.sub(r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/three\.js/r128/three\.min\.js"></script>', '<script defer src="/js/three.min.js"></script>', t)
            t = re.sub(r'<script src="((?:data|scene|app)\.js[^"]*)"></script>', lambda m: '<script defer src="' + m.group(1) + '"></script>', t)
        if fn != "index.html":  # speed: the ~600 KB 3D library only runs on the homepage; other pages use the CSS gradient fallback (body.no-webgl)
            t = re.sub(r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/three\.js/[^"]*"></script>\n?', "", t)
        if t != s:
            open(p, "w", encoding="utf-8").write(t); n += 1
out = os.path.join(root, "gta6-site-upload.zip")
if os.path.exists(out): os.remove(out)
z = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED); count = 0
for r, dirs, files in os.walk(src):
    dirs[:] = [d for d in dirs if d != ".claude"]
    for f in files:
        p = os.path.join(r, f); z.write(p, os.path.relpath(p, src).replace(os.sep, "/")); count += 1
z.close()
print(f"version {ver}: stamped {n} pages, zipped {count} files")
