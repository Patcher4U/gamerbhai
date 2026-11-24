"""Build article pages from tools/articles.json (no AI at build time).
  python -I tools/gen_articles.py gta6-site
Writes <slug>.html at the site root, the hub page articles.html, and adds them to sitemap.xml and indexnow.json.
"""
import html, json, os, re, sys
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__)); SITE = sys.argv[1] if len(sys.argv) > 1 else "gta6-site"
ROOT = os.path.dirname(HERE); BASE = "https://gamerbhai.com/"
arts = json.load(open(os.path.join(HERE, "articles.json"), encoding="utf-8"))
arts.sort(key=lambda a: a["date"], reverse=True)
e = lambda s: html.escape(s, quote=True)
strip = lambda s: re.sub(r"<[^>]+>", "", s)

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | GamerBhai</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="{ogtype}">
<meta property="og:image" content="https://gamerbhai.com/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="GamerBhai">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="/img/icons/icon-192.png">
<link rel="apple-touch-icon" href="/img/icons/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#12061f">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@400;600;700&family=Noto+Sans+Arabic:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css?v=1">
<script type="application/ld+json">{ld}</script>
</head>
<body data-page="{page}" data-seo="1">
<canvas id="bg" aria-hidden="true"></canvas>
<div class="scrim"></div>
"""
FOOT = """<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="data.js?v=1"></script>
<script src="scene.js?v=1"></script>
<script src="app.js?v=1"></script>
</body>
</html>
"""
def fmt(d): return date.fromisoformat(d).strftime("%d %B %Y").lstrip("0")

for i, a in enumerate(arts):
    url = BASE + a["slug"]
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["desc"],
          "datePublished": a["date"], "dateModified": a["date"], "image": "https://gamerbhai.com/img/og.jpg",
          "author": {"@type": "Organization", "name": "GamerBhai"},
          "publisher": {"@type": "Organization", "name": "GamerBhai", "logo": {"@type": "ImageObject", "url": "https://gamerbhai.com/img/icons/icon-512.png"}},
          "mainEntityOfPage": url}
    body = [HEAD.format(title=e(a["title"]), desc=e(a["desc"]), url=url, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")]
    body.append(f'<header class="wrap phero reveal">\n  <div class="kicker">GTA 6 · {e(fmt(a["date"]).upper())}</div>\n  <h1><span class="g">{e(a["title"])}</span></h1>\n  <p class="lead">{e(a["lead"])}</p>\n</header>\n<main class="wrap article">\n')
    for n, (h, p) in enumerate(a["sections"], 1):
        body.append(f'  <section class="reveal"><h2><span class="n">{n:02d}</span>{e(h)}</h2><div class="glass"><p>{p}</p></div></section>\n')
    src = " · ".join(f'<a href="{e(u)}" target="_blank" rel="noopener nofollow">{e(t)}</a>' for t, u in a["sources"])
    body.append(f'  <section class="reveal"><div class="glass"><p class="note">Sources: {src}. Facts checked {e(fmt(a["date"]))}; details can change with updates. GamerBhai is an unofficial fan site, not affiliated with Rockstar Games.</p></div></section>\n')
    more = [b for b in arts if b["slug"] != a["slug"]][:4]
    body.append('  <section class="reveal"><h2><span class="n">📝</span>More GTA 6 articles</h2><div class="grid">' +
                "".join(f'<a class="glass tilt area" href="{b["slug"]}"><div class="pop"><div class="ic">{b["emoji"]}</div><h3>{e(b["title"])}</h3><p>{e(b["desc"][:110])}…</p></div></a>' for b in more) +
                '</div><p class="note"><a href="articles">All articles →</a></p></section>\n  <div class="ad reveal">Ad</div>\n</main>\n')
    body.append(FOOT)
    open(os.path.join(SITE, a["slug"] + ".html"), "w", encoding="utf-8").write("".join(body))

# hub page
ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "GTA 6 Articles", "url": BASE + "articles"}
hub = [HEAD.format(title="GTA 6 Articles – News, Guides & Explainers", desc="Original GTA 6 articles: reviews, sales, Easter eggs, fastest cars, radio, performance, patches, map size, PC and Online news.",
                   url=BASE + "articles", ogtype="website", ld=json.dumps(ld), page="articles")]
hub.append('<header class="wrap phero reveal">\n  <div class="kicker">GAMERBHAI ARTICLES</div>\n  <h1><span class="g">GTA 6 Articles</span></h1>\n  <p class="lead">Short, fact-checked explainers on everything people are asking about GTA 6. New ones every week.</p>\n</header>\n<main class="wrap">\n  <section class="reveal"><div class="grid">')
hub.append("".join(f'<a class="glass tilt area" href="{a["slug"]}"><div class="pop"><div class="ic">{a["emoji"]}</div><h3>{e(a["title"])}</h3><p>{e(a["desc"][:120])}…</p><div class="go">{e(fmt(a["date"]))}</div></div></a>' for a in arts))
hub.append('</div></section>\n  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)
open(os.path.join(SITE, "articles.html"), "w", encoding="utf-8").write("".join(hub))

# sitemap + indexnow
sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for slug, d in [("articles", arts[0]["date"])] + [(a["slug"], a["date"]) for a in arts]:
    loc = f"<loc>{BASE}{slug}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{d}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(f"{len(arts)} articles + hub written; sitemap has {sm.count('<url>')} urls")
