"""Weapons + safehouses pages for the older GTA games - data only.
  python -I tools/gen_weapons.py <folder with w_*2.json s_*.json> gta6-site
Data: GTA Wiki "Weapons in ..." / "Safehouses in ..." tables (CC BY-SA, credited on every page), saved by the browser.
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
def sec(n, h, inner): return f'  <section class="reveal"><h2><span class="n">{n:02d}</span>{h}</h2><div class="glass">{inner}</div></section>\n'
def tbl(head, rows): return '<div class="gtable"><table class="cheats cw"><thead><tr>' + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
GAMES = [("gta-5", "v", "GTA 5", "GTA_V"), ("gta-san-andreas", "sa", "GTA San Andreas", "GTA_San_Andreas"), ("gta-vice-city", "vc", "GTA Vice City", "GTA_Vice_City"), ("gta-3", "3", "GTA 3", "GTA_III"),
         ("gta-4", "4", "GTA 4", "GTA_IV"), ("gta-liberty-city-stories", "lcs", "GTA Liberty City Stories", "GTA_Liberty_City_Stories"),
         ("gta-vice-city-stories", "vcs", "GTA Vice City Stories", "GTA_Vice_City_Stories"), ("gta-chinatown-wars", "ctw", "GTA Chinatown Wars", "GTA_Chinatown_Wars")]
pages = []
def write(slug, title, desc, kicker, h1, lead, body, gk, label):
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
          {"@type": "ListItem", "position": 2, "name": label, "item": BASE + slug}]}]
    open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(
        HEAD.format(lang="en", stitle=e(title), title=e(title), desc=e(desc), url=BASE + slug, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
        + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
        + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)
    pages.append(slug)

for gk, k, name, wk in GAMES:
    mslug = {m["name"].lower(): f"{gk}-{slugify(m['name'])}-mission" for m in MIS.get(gk, [])}
    def ml(t):
        s = mslug.get(t.lower()); return f'<a href="{s}">{e(t)}</a>' if s and os.path.exists(os.path.join(SITE, s + ".html")) else e(t)
    more = lambda: f'  <p class="note">More {e(name)}: <a href="{gk}-cheats">cheats</a> (weapon cheats included) · <a href="{gk}-missions">missions</a> · <a href="{gk}-100-percent-completion">100% checklist</a> · <a href="{gk}-weapons">weapons</a> · <a href="{gk}-safehouses">safehouses</a></p>\n'
    # ---------- weapons
    p = os.path.join(SRC, f"w_{k}2.json")
    if os.path.exists(p):
        d = json.loads(fix(open(p, encoding="utf-8").read())); cats, given, picks = [], [], []
        for t in d["tables"]:
            if t and t[0] and t[0][0]["t"] in ("Mission",):
                hd = [c["t"] for c in t[0]]
                rows = [[c["t"] for c in r] for r in t[1:] if len(r) >= 2]
                (given if "Given" in " ".join(hd) else picks if "Pickup" in " ".join(hd) else []).extend(rows); continue
            if cats or any("v • e" in c["t"] or c["t"] in ("Meaning", "Reference") for r in t[:1] for c in r): continue
            for i in range(len(t) - 1):
                a, b = t[i], t[i + 1]
                if len(a) == len(b) and sum(len(c["links"]) for c in b) > sum(len(c["links"]) for c in a) + 1 and all(len(c["links"]) <= 1 for c in a):
                    for ca, cb in zip(a, b):
                        ws = [w for w in dict.fromkeys(cb["links"]) if w not in ("DLC", "MOD", "CE", "EV")]
                        if ws: cats.append((ca["t"], ws))
        if cats:
            n = sum(len(w) for _, w in cats); body, i = "", 1
            body += sec(i, f"All {n} weapons by type", tbl(["Type", "Weapons"], [f"<tr><td><b>{e(c)}</b></td><td>{e(' · '.join(ws))}</td></tr>" for c, ws in cats])); i += 1
            if given: body += sec(i, "Weapons the story gives you", tbl(["Mission", "Weapon(s) given"], [f"<tr><td>{ml(r[0])}</td><td>{e(r[1])}</td></tr>" for r in given])); i += 1
            if picks: body += sec(i, "Weapon pickups during missions", tbl(["Mission", "Pickup"], [f"<tr><td>{ml(r[0])}</td><td>{e(r[1])}</td></tr>" for r in picks])); i += 1
            body += more() + f'  <p class="note">Data from the <a href="https://gta.fandom.com/wiki/Weapons_in_{wk}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). Unofficial fan guide, not affiliated with Rockstar Games.</p>\n'
            write(f"{gk}-weapons", f"All {n} {name} Weapons (Full List by Type)", f"Every weapon in {name} ({n}), sorted by type: " + ", ".join(c for c, _ in cats[:6]) + ". Plus which story missions give you weapons.",
                  f"{e(name.upper())} · WEAPONS", f"{name} Weapons", f"🔫 {n} weapons in {len(cats)} groups" + (f" · {len(given)} missions that hand you a weapon" if given else ""), body, gk, f"{name} weapons")
            print(gk, "weapons", n, len(given), len(picks))
    # ---------- safehouses
    p = os.path.join(SRC, f"s_{k}.json")
    if os.path.exists(p):
        raw = json.loads(fix(open(p, encoding="utf-8").read())); body, i, total, cur = "", 1, 0, None
        for x in raw:
            if "h" in x: cur = x["h"]; continue
            if "table" not in x or len(x["table"]) < 2: continue
            t = [list(r) for r in x["table"]]
            hd = t[0]; start = 1
            if len(t) > 2 and t[1][:2] == hd[:2]: hd = [b if a != b and b else a for a, b in zip(hd, t[1])]; start = 2
            hd = ["Safehouse" if h == "Image" else "Area" if h == "Map" else h for h in hd]
            data = [r + [""] * (len(hd) - len(r)) for r in t[start:]]
            keep = [j for j in range(len(hd)) if any(r[j] for r in data if len(set(r)) > 1)]
            if not keep or "Meaning" in hd: continue
            rows = []
            for r in data:
                if len(set(r)) == 1: rows.append(f'<tr><td colspan="{len(keep)}"><b>📍 {e(r[0])}</b></td></tr>'); continue
                rows.append("<tr>" + "".join(f"<td>{ml(r[j]) if 'nlock' in hd[j] else e(r[j])}</td>" for j in keep) + "</tr>"); total += 1
            h = cur if cur and cur not in ("Contents", "Description", "List of Save Points", "Safehouses") else "Safehouses"
            body += sec(i, e(h), tbl([hd[j] for j in keep], rows)); i += 1
        if total:
            body += more() + f'  <p class="note">Data from the <a href="https://gta.fandom.com/wiki/Safehouses_in_{wk}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). Unofficial fan guide, not affiliated with Rockstar Games.</p>\n'
            write(f"{gk}-safehouses", f"All {name} Safehouses: Locations, Prices & Unlocks", f"Every safehouse in {name} ({total}): where it is, how to unlock it and what it costs, with garage and save point details.",
                  f"{e(name.upper())} · SAFEHOUSES", f"{name} Safehouses", f"🏠 {total} places to save, where they are and how to get them.", body, gk, f"{name} safehouses")
            print(gk, "safehouses", total)

sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
json.dump(pages, open(os.path.join(HERE, "weapons_pages.json"), "w"))
print(len(pages), "pages; sitemap", sm.count("<url>"), "urls")
