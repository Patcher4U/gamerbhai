# Builds gta6-site-upload.zip for Cloudflare Pages.
# Stamps a fresh version on app.js / data.js / scene.js / style.css in every HTML page
# so browsers always load the newest code after a deploy (fixes "I still see the old site").
import os, re, time, zipfile, sys
root = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(root, "gta6-site")
ver = time.strftime("%Y%m%d%H%M")
pat = re.compile(r'(src|href)="(/?(?:app\.js|data\.js|scene\.js|style\.css))(\?v=[^"]*)?"')
n = 0
for fn in os.listdir(src):
    if fn.endswith(".html"):
        p = os.path.join(src, fn)
        s = open(p, encoding="utf-8").read()
        t = pat.sub(lambda m: f'{m.group(1)}="{m.group(2)}?v={ver}"', s)
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
