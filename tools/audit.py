import os, re, sys, glob, json
root = sys.argv[1]
os.chdir(root)
pages = sorted(f for f in glob.glob("*.html") if f != "404.html")
problems = []
clean = lambda u: u.split("#")[0].split("?")[0]
for p in pages:
    s = open(p, encoding="utf-8").read()
    if "<title>" not in s: problems.append((p, "no <title>"))
    if 'name="description"' not in s: problems.append((p, "no meta description"))
    if 'rel="canonical"' not in s and p not in ("index.html",): problems.append((p, "no canonical"))
    for m in re.finditer(r'(?:href|src)="([^"]+)"', s):
        u = m.group(1)
        if u.startswith(("http", "mailto:", "#", "data:", "javascript:", "tel:")) or "${" in u: continue
        f = clean(u).lstrip("/")
        if not f: continue
        cands = [f, f + ".html", os.path.join(f, "index.html")]
        if not any(os.path.exists(c) for c in cands): problems.append((p, "broken link: " + u))
    ids = re.findall(r'\sid="([^"]+)"', s)
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: problems.append((p, "duplicate ids: " + ",".join(sorted(dup))))
    for m in re.finditer(r'<img\b[^>]*>', s):
        if 'alt=' not in m.group(0): problems.append((p, "img without alt"))
# JS-referenced local assets
for js in ("app.js", "data.js", "scene.js"):
    s = open(js, encoding="utf-8").read()
    for m in re.finditer(r'["\'`](/?(?:img|models)/[^"\'`$]+)["\'`]', s):
        f = m.group(1).lstrip("/")
        if not os.path.exists(f): problems.append((js, "missing asset: " + f))
    for m in re.finditer(r'href:"([a-z0-9-]+\.html)"', s):
        if not os.path.exists(m.group(1)): problems.append((js, "missing page: " + m.group(1)))
# sitemap vs pages
sm = open("sitemap.xml", encoding="utf-8").read()
locs = re.findall(r"<loc>https://gamerbhai.com/?([^<]*)</loc>", sm)
for l in locs:
    f = (l or "index") + ".html"
    if not os.path.exists(f): problems.append(("sitemap.xml", "page missing: " + l))
listed = {(l or "index") + ".html" for l in locs}
for p in pages:
    if p not in listed: problems.append(("sitemap.xml", "not listed: " + p))
print(len(pages), "pages checked")
for a, b in problems: print(a, "|", b)
