"""Section pages from GTA Wiki articles: gangs per game, GTA Online businesses/properties, GTA Advance cheats - data only.
  python -I tools/gen_prose.py <folder with gang_*.json o_*.json ch_adv2.json> gta6-site
Data: GTA Wiki (CC BY-SA, credited on every page), saved by the browser.
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = sys.argv[1]; SITE = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "gta6-site"))
BASE = "https://gamerbhai.com/"; TODAY = "2026-11-29"
e = lambda s: html.escape(s, quote=True)
asrc = open(os.path.join(HERE, "gen_articles.py"), encoding="utf-8").read()
A = {}; exec(asrc[asrc.index("HEAD ="):asrc.index("def fmt")], A); HEAD, FOOT = A["HEAD"], A["FOOT"]
sys.path.insert(0, HERE); from wiki_clean import fix
def clip(t, n=158): return t if len(t) <= n else t[:t.rfind(' ', 0, n - 1)].rstrip(' ,.:;') + '…'
def sec(n, h, inner): return f'  <section class="reveal"><h2><span class="n">{n:02d}</span>{h}</h2><div class="glass">{inner}</div></section>\n'
def tbl(head, rows): return '<div class="gtable"><table class="cheats cw"><thead><tr>' + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>"
load = lambda f: json.loads(fix(open(os.path.join(SRC, f + ".json"), encoding="utf-8").read())) if os.path.exists(os.path.join(SRC, f + ".json")) else []
pages = []
def write(slug, title, desc, kicker, h1, lead, body, crumbs):
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(crumbs)]}]
    open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(
        HEAD.format(lang="en", stitle=e(title), title=e(title), desc=e(desc), url=BASE + slug, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
        + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
        + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)
    pages.append(slug)
def render(d, maxp=3, skip=("Contents",)):
    out, k, cur, pc, buf = "", 1, None, 0, ""
    def flush():
        nonlocal out, k, buf
        if buf.strip() and cur and cur not in skip: out += sec(k, e(cur), buf); k += 1
        buf = ""
    for x in d:
        if "h" in x: flush(); cur = x["h"]; pc = 0; continue
        if cur is None: cur = "Overview"
        if "p" in x and pc < maxp and len(x["p"]) > 40: buf += f"<p>{e(x['p'])}</p>"; pc += 1
        elif "li" in x and len(x["li"]) < 400 and not re.match(r"^\d+(\.\d+)* ", x["li"]): buf += f"<ul><li>{e(x['li'])}</li></ul>"
        elif "table" in x and len(x["table"]) > 1:
            t = [list(r) for r in x["table"]]
            if len(set(t[0])) == 1 and len(t) > 2: t = t[1:]
            hd = t[0]; data = [r + [""] * (len(hd) - len(r)) for r in t[1:] if r != hd]
            keep = [j for j, h in enumerate(hd) if h not in ("Image", "Map", "Icon") and any(r[j] for r in data)]
            if keep and data: buf += tbl([hd[j] for j in keep], [[e(r[j]) for j in keep] for r in data])
    flush()
    return out.replace("</ul><ul>", "")
cred = lambda pg, extra="": f'  <p class="note">From the <a href="https://gta.fandom.com/wiki/{pg}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0).{extra} Unofficial fan guide, not affiliated with Rockstar Games.</p>\n'

# ---------- gangs
GAMES = [("gta-5", "v", "GTA 5", "GTA_V"), ("gta-san-andreas", "sa", "GTA San Andreas", "GTA_San_Andreas"), ("gta-vice-city", "vc", "GTA Vice City", "GTA_Vice_City"), ("gta-3", "3", "GTA 3", "GTA_III"),
         ("gta-4", "4", "GTA 4", "GTA_IV"), ("gta-liberty-city-stories", "lcs", "GTA Liberty City Stories", "GTA_Liberty_City_Stories"),
         ("gta-vice-city-stories", "vcs", "GTA Vice City Stories", "GTA_Vice_City_Stories"), ("gta-chinatown-wars", "ctw", "GTA Chinatown Wars", "GTA_Chinatown_Wars")]
for gk, k, name, wk in GAMES:
    d = load(f"gang_{k}")
    if not d: continue
    body = render(d, maxp=4)
    n = body.count("<section")
    if n < 2: continue
    gangs = [re.sub(r"<.*?>", "", h) for h in re.findall(r'</span>(.*?)</h2>', body)][1:9]
    body += (f'  <p class="note">More {e(name)}: <a href="{gk}-characters">characters</a> · <a href="{gk}-missions">missions</a> · <a href="{gk}-weapons">weapons</a> · <a href="{gk}-cheats">cheats</a> (gang cheats included)</p>\n' + cred(f"Gangs_in_{wk}"))
    write(f"{gk}-gangs", f"{name} Gangs: Every Gang, Colours & Territory", clip(f"Every gang in {name}: " + ", ".join(html.unescape(g) for g in gangs) + " – who they are, where they rule and what they drive."),
          f"{e(name.upper())} · GANGS", f"{name} Gangs", f"🔫 Every gang in {e(name)}, where they hang out and how they fight.", body, [("Home", ""), (f"{name} gangs", f"{gk}-gangs")])
    print(gk, "gangs", n)

# ---------- GTA Online businesses and properties
OB = [("o_nc", "gta-online-nightclubs", "Nightclubs", "🪩", "Nightclubs"), ("o_agency", "gta-online-agency", "Agency", "🕵️", "Agency"), ("o_acid", "gta-online-acid-lab", "Acid Lab", "🧪", "Acid_Lab"),
      ("o_arcade", "gta-online-arcades", "Arcades", "🕹️", "Arcade"), ("o_auto", "gta-online-auto-shops", "Auto Shops", "🔧", "Auto_Shop"), ("o_hangar", "gta-online-hangars", "Hangars", "✈️", "Hangar"),
      ("o_vw", "gta-online-vehicle-warehouses", "Vehicle Warehouses", "🚚", "Vehicle_Warehouse"), ("o_club", "gta-online-clubhouses", "Clubhouses", "🏍️", "Clubhouses"),
      ("o_yacht", "gta-online-super-yacht", "Super Yacht", "🛥️", "Super_Yacht"), ("o_kosatka", "gta-online-kosatka", "Kosatka Submarine", "🚢", "Kosatka"),
      ("o_salv", "gta-online-salvage-yards", "Salvage Yards", "🏗️", "Salvage_Yard"), ("o_bail", "gta-online-bail-office", "Bail Office", "⚖️", "Bail_Office"),
      ("o_garment", "gta-online-garment-factory", "Garment Factory", "🧵", "Garment_Factory"), ("o_apts", "gta-online-apartments", "Apartments", "🏢", "Apartments")]
made = []
for f, slug, nm, ic, wk in OB:
    d = load(f)
    if not d: continue
    body = render(d)
    if body.count("<section") < 2: continue
    first = next((x["p"] for x in d if "p" in x and len(x["p"]) > 60), "")
    body += ('  <p class="note">More GTA Online: <a href="gta-online">GTA Online hub</a> · <a href="gta-online-mc-businesses">MC businesses</a> · <a href="gta-online-bunkers">bunkers</a> · <a href="gta-online-heists">heists</a> · '
             + " · ".join(f'<a href="{s2}">{n2}</a>' for f2, s2, n2, _, _ in OB if s2 != slug and os.path.exists(os.path.join(SRC, f2 + ".json"))) + '</p>\n'
             + cred(wk, " GTA Online prices change with updates and sales."))
    write(slug, f"GTA Online {nm}: Locations, Prices & How It Works", clip(f"GTA Online {nm} guide: " + first), "GTA ONLINE", f"GTA Online {nm}", f"{ic} " + e(clip(first, 150)), body,
          [("Home", ""), ("GTA Online", "gta-online"), (nm, slug)])
    made.append((slug, nm, ic)); print(slug, body.count("<section"))
json.dump(made, open(os.path.join(HERE, "online_extra.json"), "w", encoding="utf-8"), ensure_ascii=False)

# ---------- GTA Advance cheats
rows = json.load(open(os.path.join(SRC, "ch_adv2.json"), encoding="utf-8"))
body = '  <div class="warnbox">⌨️ <b>How to enter:</b> pause the game and press the buttons in order on the Game Boy Advance. Save before using cheats.</div>\n'
body += sec(1, f"All {len(rows)} GTA Advance cheats", tbl(["Effect", "Buttons"], [[e(a), f'<span class="code">{e(b)}</span>'] for a, b in rows]))
body += '  <p class="note">More: <a href="gta-advance-missions">GTA Advance missions</a> · <a href="gta-cheats">cheats for every GTA game</a> · <a href="gta-3-cheats">GTA 3 cheats</a></p>\n' + cred("Cheats_in_GTA_Advance")
write("gta-advance-cheats", f"All {len(rows)} GTA Advance Cheats (Game Boy Advance)", "Every GTA Advance cheat for the Game Boy Advance: all weapons, $15,000, health, armor, wanted level and the Mission Select menu, with the exact buttons.",
      "GTA ADVANCE · CHEATS", "GTA Advance Cheats", f"🎮 {len(rows)} button codes for GTA Advance (2004).", body, [("Home", ""), ("GTA Advance cheats", "gta-advance-cheats")])

sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(len(pages), "pages; sitemap", sm.count("<url>"), "urls")
