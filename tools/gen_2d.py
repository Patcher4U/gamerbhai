"""Mission lists for GTA 2 and GTA Advance - data only.
  python -I tools/gen_2d.py <folder with mi_2.json mi_adv.json> gta6-site
Data: GTA Wiki "Missions in GTA 2" / "Missions in GTA Advance" (CC BY-SA, credited on every page), saved by the browser.
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = sys.argv[1]; SITE = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "gta6-site"))
BASE = "https://gamerbhai.com/"; TODAY = "2026-11-28"
e = lambda s: html.escape(s, quote=True)
asrc = open(os.path.join(HERE, "gen_articles.py"), encoding="utf-8").read()
A = {}; exec(asrc[asrc.index("HEAD ="):asrc.index("def fmt")], A); HEAD, FOOT = A["HEAD"], A["FOOT"]
sys.path.insert(0, HERE); from wiki_clean import fix
def sec(n, h, inner): return f'  <section class="reveal"><h2><span class="n">{n:02d}</span>{h}</h2><div class="glass">{inner}</div></section>\n'
def tbl(head, rows): return '<div class="gtable"><table class="cheats cw"><thead><tr>' + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
pages = []
def write(slug, title, desc, kicker, h1, lead, body):
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE}, {"@type": "ListItem", "position": 2, "name": h1, "item": BASE + slug}]}]
    open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(
        HEAD.format(lang="en", stitle=e(title), title=e(title), desc=e(desc), url=BASE + slug, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
        + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
        + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)
    pages.append(slug)
load = lambda f: json.loads(fix(open(os.path.join(SRC, f), encoding="utf-8").read()))
clean = lambda t: re.sub(r"!1$", "!", t.strip())

# ---------- GTA 2: three areas, each with three gangs; phones are green (easy), yellow, red (hard)
d = load("mi_2.json"); body, i, total, area = "", 1, 0, None
for x in d:
    if "h" in x: area = x["h"]; continue
    t = x["rows"]
    if not t or t[0][0]["t"] != "Phone": continue
    gangs = [c["t"] for c in t[0][2:]]; rows, phone, award = [], "", ""
    for r in t[1:]:
        c = [y["t"] for y in r]
        if len(c) == len(gangs) + 2: phone, award, c = c[0], c[1], c[2:]
        if len(c) != len(gangs): continue
        rows.append(f"<tr><td><b>{e(phone)}</b><br><small>${e(award)}</small></td>" + "".join(f"<td>{e(clean(m))}</td>" for m in c) + "</tr>")
        total += sum(1 for m in c if m.strip())
    body += sec(i, e(area), tbl(["Phone (reward)"] + gangs, rows)); i += 1
intro = sec(0, "How GTA 2 missions work", "<p>GTA 2 (1999) is split into three areas: Downtown, Residential and Industrial. In each area three gangs give jobs from coloured payphones: <b>green</b> phones are the easiest, <b>yellow</b> are harder and <b>red</b> are the hardest. Working for a gang raises your respect with it and lowers it with its rivals – and a gang that hates you shoots on sight. Earn the points target for the area to unlock the next one. Names with a slash are the mission’s two titles (in-game name / alternative name).</p>").replace('<span class="n">00</span>', '<span class="n">★</span>')
body = intro + body + ('  <p class="note">More: <a href="gta-2-cheats">GTA 2 cheats</a> · <a href="gta-cheats">cheats for every GTA game</a> · <a href="gta-advance-missions">GTA Advance missions</a></p>\n'
                       '  <p class="note">Mission list from the <a href="https://gta.fandom.com/wiki/Missions_in_GTA_2" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). Unofficial fan guide, not affiliated with Rockstar Games.</p>\n')
write("gta-2-missions", f"All GTA 2 Missions: Every Phone Job by Gang & Area", "Every GTA 2 mission by area and gang – Yakuza, Loonies, Zaibatsu, Rednecks, Scientists, Russian Mafia and Hare Krishna – from green, yellow and red phones.",
      "GTA 2 · MISSIONS", "GTA 2 Missions", f"🕹️ {total} phone jobs across 3 areas and 7 gangs.", body)
print("gta-2", total)

# ---------- GTA Advance: missions by giver (from the wiki's mission navigation box)
d = load("mi_adv.json"); giv = []
for x in d:
    if "rows" in x and x["rows"] and "Missions in Grand Theft Auto Advance" in x["rows"][0][0]["t"]:
        for r in x["rows"][1:]:
            if len(r) != 2 or r[0]["t"].startswith(("Side", "Missions in")): continue
            t = re.sub(r"\s*Part \d+\s*", " | ", r[1]["t"]).strip(" |")
            giv.append((r[0]["t"], [clean(m).rstrip("*").strip() for m in t.split("|") if m.strip()]))
rows, n = [], 0
for g, ms in giv:
    for m in ms: n += 1; rows.append(f"<tr><td>{n}</td><td>{e(m)}</td><td>{e(g)}</td></tr>")
body = sec(1, "How GTA Advance works", "<p>GTA Advance (2004, Game Boy Advance) is a top-down GTA set in Liberty City a year before GTA III. You play as Mike, who is out for revenge after his partner Vinnie is apparently killed. The story moves from Portland to Staunton Island and Shoreside Vale, with jobs from Vinnie, 8-Ball, Jonnie, King Courtney, Cisco, Asuka Kasen and others.</p>")
body += sec(2, f"All {n} story missions", tbl(["#", "Mission", "Given by"], rows))
body += sec(3, "Side missions", "<p>Paramedic, Firefighter, Vigilante and Taxi Driver, plus street races in Portland, Staunton Island and Shoreside Vale, and Demolition Football.</p>")
body += ('  <p class="note">More: <a href="gta-3-missions">GTA 3 missions</a> (same city, a year later) · <a href="gta-liberty-city-stories-missions">Liberty City Stories missions</a> · <a href="gta-2-missions">GTA 2 missions</a> · <a href="gta-cheats">cheats for every GTA game</a></p>\n'
         '  <p class="note">Mission list from the <a href="https://gta.fandom.com/wiki/Missions_in_GTA_Advance" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). Unofficial fan guide, not affiliated with Rockstar Games.</p>\n')
write("gta-advance-missions", f"All {n} GTA Advance Missions (Full List)", f"Every GTA Advance story mission ({n}) in order with who gives it – Vinnie, 8-Ball, Jonnie, King Courtney, Cisco, Asuka and Mike – plus the side missions.",
      "GTA ADVANCE · MISSIONS", "GTA Advance Missions", f"🎮 {n} story missions on the Game Boy Advance, in order.", body)
print("gta-advance", n)

sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(len(pages), "pages; sitemap", sm.count("<url>"), "urls")
