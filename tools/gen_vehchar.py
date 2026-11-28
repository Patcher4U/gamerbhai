"""Vehicles + characters pages for the older GTA games - data only.
  python -I tools/gen_vehchar.py <folder with veh2_*.json chr_*.json> gta6-site
Data: GTA Wiki "Vehicles in ..." / "Characters in ..." tables (CC BY-SA, credited on every page), saved by the browser.
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = sys.argv[1]; SITE = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "gta6-site"))
BASE = "https://gamerbhai.com/"; TODAY = "2026-11-28"
e = lambda s: html.escape(s, quote=True)
asrc = open(os.path.join(HERE, "gen_articles.py"), encoding="utf-8").read()
A = {}; exec(asrc[asrc.index("HEAD ="):asrc.index("def fmt")], A); HEAD, FOOT = A["HEAD"], A["FOOT"]
sys.path.insert(0, HERE); from wiki_clean import fix
MIS = json.load(open(os.path.join(HERE, "classic_missions.json"), encoding="utf-8"))
def slugify(s): return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower().replace("'", "").replace("&", "and").replace("$", "").replace(",", "").replace(".", ""))).strip("-")
def clip(t, n=158): return t if len(t) <= n else t[:t.rfind(' ', 0, n - 1)].rstrip(' ,.:;') + '…'
def sec(n, h, inner): return f'  <section class="reveal"><h2><span class="n">{n:02d}</span>{h}</h2><div class="glass">{inner}</div></section>\n'
def tbl(head, rows): return '<div class="gtable"><table class="cheats cw"><thead><tr>' + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
GAMES = [("gta-5", "v", "GTA 5", "GTA_V"), ("gta-san-andreas", "sa", "GTA San Andreas", "GTA_San_Andreas"), ("gta-vice-city", "vc", "GTA Vice City", "GTA_Vice_City"), ("gta-3", "3", "GTA 3", "GTA_III"),
         ("gta-4", "4", "GTA 4", "GTA_IV"), ("gta-liberty-city-stories", "lcs", "GTA Liberty City Stories", "GTA_Liberty_City_Stories"),
         ("gta-vice-city-stories", "vcs", "GTA Vice City Stories", "GTA_Vice_City_Stories"), ("gta-chinatown-wars", "ctw", "GTA Chinatown Wars", "GTA_Chinatown_Wars")]
TAGS = {"DLC", "MOD", "CE", "EV", "E&E", "EV/E&E", "R*", "PS", "XB", "PC"}
pages = []
def write(slug, title, desc, kicker, h1, lead, body, label):
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE}, {"@type": "ListItem", "position": 2, "name": label, "item": BASE + slug}]}]
    open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(
        HEAD.format(lang="en", stitle=e(title), title=e(title), desc=e(desc), url=BASE + slug, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
        + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
        + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)
    pages.append(slug)

for gk, k, name, wk in GAMES:
    more = (f'  <p class="note">More {e(name)}: <a href="{gk}-cheats">cheats</a> · <a href="{gk}-missions">missions</a> · <a href="{gk}-vehicles">vehicles</a> · <a href="{gk}-characters">characters</a> · '
            f'<a href="{gk}-weapons">weapons</a> · <a href="{gk}-radio-stations">radio</a> · <a href="{gk}-100-percent-completion">100% checklist</a></p>\n')
    cred = lambda pg: f'  <p class="note">Data from the <a href="https://gta.fandom.com/wiki/{pg}_in_{wk}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). Unofficial fan guide, not affiliated with Rockstar Games.</p>\n'
    # ---------- vehicles
    p = os.path.join(SRC, f"veh2_{k}.json")
    if os.path.exists(p):
        d = json.loads(fix(open(p, encoding="utf-8").read())); cats = []
        for x in d:
            if "rows" not in x or cats: continue
            t = x["rows"]
            if not t or any("v • e" in c["t"] or c["t"] in ("Reference", "Navigation") for c in t[0]): continue
            for i in range(len(t) - 1):
                a, b = t[i], t[i + 1]
                if len(a) == len(b) and sum(len(c["links"]) for c in b) > sum(len(c["links"]) for c in a) + 1 and all(len(c["links"]) <= 2 for c in a):
                    for ca, cb in zip(a, b):
                        vs = [v for v in dict.fromkeys(cb["links"]) if v not in TAGS and not re.fullmatch(r"\[?\w{1,4}\]?", v)]
                        if vs and ca["t"]: cats.append((ca["t"], vs))
        if cats:
            n = sum(len(v) for _, v in cats)
            body = sec(1, f"All {n} vehicles by class", tbl(["Class", "Vehicles"], [f"<tr><td><b>{e(c)}</b></td><td>{e(' · '.join(v))}</td></tr>" for c, v in cats]))
            body += more + cred("Vehicles")
            write(f"{gk}-vehicles", f"All {n} {name} Vehicles (Full List by Class)", clip(f"Every vehicle in {name} ({n}) sorted by class: " + ", ".join(c for c, _ in cats[:8]) + "."),
                  f"{e(name.upper())} · VEHICLES", f"{name} Vehicles", f"🚗 {n} vehicles in {len(cats)} classes.", body, f"{name} vehicles")
            print(gk, "vehicles", n, len(cats))
    # ---------- characters
    p = os.path.join(SRC, f"chr_{k}.json")
    if os.path.exists(p):
        d = json.loads(fix(open(p, encoding="utf-8").read())); h, body, i, total = None, "", 1, 0
        mslug = {m["name"].lower(): f"{gk}-{slugify(m['name'])}-mission" for m in MIS.get(gk, [])}
        def ml(t):
            parts = re.split(r"\s+[–-]\s+", t)
            return " – ".join(f'<a href="{mslug[x.lower()]}">{e(x)}</a>' if x.lower() in mslug and os.path.exists(os.path.join(SITE, mslug[x.lower()] + ".html")) else e(x) for x in parts)
        for x in d:
            if "h" in x: h = x["h"]; continue
            t = x["rows"]
            if not t or h in (None, "Contents", "Navigation", "References", "See also") or any("v • e" in c["t"] for c in t[0]): continue
            hd = [c["t"] for c in t[0]] if all(c["th"] for c in t[0]) else None
            data = t[1:] if hd else t
            rows = []
            for r in data:
                c = [x2["t"] for x2 in r]
                if len(c) < 2 or not c[0] or len(c[-1]) < 20: continue
                nm = re.sub(r"\((.+?)\)$", r" (\1)", c[0]).replace("  ", " ")
                rng = ml(c[1]) if len(c) >= 3 else ""
                rows.append(f"<tr><td><b>{e(nm)}</b></td>" + (f"<td><small>{rng}</small></td>" if len(c) >= 3 else "") + f"<td>{e(clip(c[-1], 420))}</td></tr>"); total += 1
            if rows:
                body += sec(i, e(h), tbl(["Character", "Missions", "Who they are"] if "<small>" in rows[0] else ["Character", "Who they are"], rows)); i += 1
        if total:
            body += more + cred("Characters")
            write(f"{gk}-characters", f"{name} Characters: Full Cast List ({total})", clip(f"Every important {name} character ({total}): who they are and which missions they appear in, from the protagonist and villains to minor characters."),
                  f"{e(name.upper())} · CHARACTERS", f"{name} Characters", f"👥 {total} characters, from the main cast to minor faces.", body, f"{name} characters")
            print(gk, "characters", total)

sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(len(pages), "pages; sitemap", sm.count("<url>"), "urls")
