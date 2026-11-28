"""Radio station pages (tracklists) for the older GTA games - data only.
  python -I tools/gen_radio.py <folder with rad_*.json> gta6-site
Data: GTA Wiki "Radio Stations in ..." (CC BY-SA, credited on every page), saved by the browser.
Builds <game>-radio-stations (all stations) + <game>-<station>-radio (tracklist) pages.
"""
import html, json, os, re, sys, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = sys.argv[1]; SITE = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "gta6-site"))
BASE = "https://gamerbhai.com/"; TODAY = "2026-11-28"
e = lambda s: html.escape(s, quote=True)
asrc = open(os.path.join(HERE, "gen_articles.py"), encoding="utf-8").read()
A = {}; exec(asrc[asrc.index("HEAD ="):asrc.index("def fmt")], A); HEAD, FOOT = A["HEAD"], A["FOOT"]
sys.path.insert(0, HERE); from wiki_clean import fix
def slugify(s): return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower().replace("'", "").replace("&", "and").replace("$", "").replace(",", "").replace(".", ""))).strip("-")
def clip(t, n=158): return t if len(t) <= n else t[:t.rfind(' ', 0, n - 1)].rstrip(' ,.:;') + '…'
def sec(n, h, inner): return f'  <section class="reveal"><h2><span class="n">{n:02d}</span>{h}</h2><div class="glass">{inner}</div></section>\n'
GAMES = [("gta-5", "v", "GTA 5", "GTA_V"), ("gta-san-andreas", "sa", "GTA San Andreas", "GTA_San_Andreas"), ("gta-vice-city", "vc", "GTA Vice City", "GTA_Vice_City"), ("gta-3", "3", "GTA 3", "GTA_III"),
         ("gta-4", "4", "GTA 4", "GTA_IV"), ("gta-liberty-city-stories", "lcs", "GTA Liberty City Stories", "GTA_Liberty_City_Stories"),
         ("gta-vice-city-stories", "vcs", "GTA Vice City Stories", "GTA_Vice_City_Stories"), ("gta-chinatown-wars", "ctw", "GTA Chinatown Wars", "GTA_Chinatown_Wars")]
START = ("Radio Stations", "Stations", "Available On All Versions")
STOP = ("Other Songs", "Commercials", "Non-Selectable", "Cut Radio", "Soundtrack", "Vehicle Default", "MP3 Player", "Background Music", "See also", "See Also")
pages = []
def write(slug, title, desc, kicker, h1, lead, body, crumbs):
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(crumbs)]}]
    open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(
        HEAD.format(lang="en", stitle=e(title), title=e(title), desc=e(desc), url=BASE + slug, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
        + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
        + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)
    pages.append(slug)

for gk, k, name, wk in GAMES:
    p = os.path.join(SRC, f"rad_{k}.json")
    if not os.path.exists(p): continue
    raw = json.loads(fix(open(p, encoding="utf-8").read()))
    st, on, cur = [], False, None
    for x in raw:
        if "h" in x:
            h = x["h"]
            if h in START: on = True; cur = None; continue
            if not on: continue
            if h.startswith(STOP): break
            if h.startswith(("Original", "Exclusive", "iOS", "Available", "Description")): cur = None; continue
            cur = dict(name=h, desc=[], songs=[]); st.append(cur); continue
        if not on or cur is None: continue
        if "p" in x: cur["desc"].append(x["p"])
        elif "li" in x:
            t = re.sub(r"\s*[*†‡§]+\s*$", "", x["li"]).strip()
            if t and "\n" not in t: cur["songs"].append(t)
    st = [s for s in st if s["desc"] or s["songs"]]
    if not st: continue
    hub = f"{gk}-radio-stations"
    for s in st: b = slugify(s["name"]); s["slug"] = f"{gk}-{b}" + ("" if b.endswith("radio") else "-radio")
    credit = f'<p class="note">Station info and tracklists from the <a href="https://gta.fandom.com/wiki/Radio_Stations_in_{wk}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). Some songs differ between versions of the game. Unofficial fan guide, not affiliated with Rockstar Games.</p>'
    for i, s in enumerate(st):
        body, n = "", 1
        if s["desc"]: body += sec(n, f"About {e(s['name'])}", "".join(f"<p>{e(d)}</p>" for d in s["desc"][:3])); n += 1
        if s["songs"]:
            body += sec(n, f"Full tracklist ({len(s['songs'])} songs)", '<ol class="tracks">' + "".join(f"<li>{e(t)}</li>" for t in s["songs"]) + "</ol>"); n += 1
        yt = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(f"{name} {s['name']} radio full")
        nav = " · ".join(f'<a href="{o["slug"]}">{lab} {e(o["name"])}</a>' for lab, o in (("⬅️", st[i - 1] if i else None), ("➡️", st[i + 1] if i + 1 < len(st) else None)) if o)
        body += f'  <p class="note">▶️ <a href="{yt}" rel="nofollow noopener" target="_blank">Listen to {e(s["name"])} on YouTube</a> · {nav}</p>\n  <p class="note"><a href="{hub}">All {len(st)} {e(name)} radio stations →</a> · <a href="{gk}-cheats">{e(name)} cheats</a> · <a href="{gk}-missions">missions</a></p>\n  {credit}\n'
        first = s["songs"][0] if s["songs"] else ""
        desc = clip(f"{name} {s['name']} radio station" + (f": full tracklist of {len(s['songs'])} songs, starting with {first}." if s["songs"] else ". ") + (" " + s["desc"][0] if s["desc"] else ""))
        write(s["slug"], f"{name} {s['name']} Radio: Full Song List", desc, f"{e(name.upper())} · RADIO", f"{s['name']}", f"📻 {e(name)} radio station" + (f" · {len(s['songs'])} songs" if s["songs"] else " · talk radio"),
              body, [("Home", ""), (f"{name} radio", hub), (s["name"], s["slug"])])
    rows = "".join(f'<tr><td><a href="{s["slug"]}">{e(s["name"])}</a></td><td>{len(s["songs"]) or "talk"}</td><td><small>{e(clip(s["desc"][0], 120) if s["desc"] else "")}</small></td></tr>' for s in st)
    tot = sum(len(s["songs"]) for s in st)
    body = sec(1, f"All {len(st)} stations", f'<div class="gtable"><table class="cheats cw"><thead><tr><th>Station</th><th>Songs</th><th>About</th></tr></thead><tbody>{rows}</tbody></table></div>')
    body += f'  <p class="note">Other games: ' + " · ".join(f'<a href="{o}-radio-stations">{e(n2)} radio</a>' for o, k2, n2, _ in GAMES if o != gk and os.path.exists(os.path.join(SRC, f"rad_{k2}.json"))) + f'</p>\n  {credit}\n'
    write(hub, f"All {name} Radio Stations & Songs ({tot} tracks)", clip(f"Every {name} radio station ({len(st)}) with its full song list – {tot} tracks in total: " + ", ".join(s["name"] for s in st[:6]) + "…"),
          f"{e(name.upper())} · RADIO", f"{name} Radio Stations", f"📻 {len(st)} stations · {tot} songs. Tap a station for its full tracklist.", body, [("Home", ""), (f"{name} radio", hub)])
    print(gk, len(st), "stations", tot, "songs")

sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(len(pages), "pages; sitemap", sm.count("<url>"), "urls")
