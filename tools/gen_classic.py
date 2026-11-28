"""Cheat pages for the older GTA games (GTA III, Vice City, San Andreas, GTA IV, GTA V) - data only.
  python -I tools/gen_classic.py gta6-site
Data: tools/classic_cheats.json (built by tools/parse_classic.py from the GTA Wiki tables, cross-checked).
Builds one page per cheat, one hub per game (gta-5-cheats ...) and an all-games hub (gta-cheats),
then adds them to sitemap.xml and indexnow.json.
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SITE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "gta6-site"))
BASE = "https://gamerbhai.com/"; TODAY = "2026-11-28"
e = lambda s: html.escape(s, quote=True)
asrc = open(os.path.join(HERE, "gen_articles.py"), encoding="utf-8").read()
A = {}; exec(asrc[asrc.index("HEAD ="):asrc.index("def fmt")], A); HEAD, FOOT = A["HEAD"], A["FOOT"]
DATA = json.load(open(os.path.join(HERE, "classic_cheats.json"), encoding="utf-8"))

def slugify(s): return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower().replace("'", "").replace("&", "and").replace("$", "").replace(",", ""))).strip("-")
def clip(t, n=158): return t if len(t) <= n else t[:t.rfind(' ', 0, n - 1)].rstrip(' ,.:;') + '…'
def sec(n, h, inner): return f'  <section class="reveal"><h2><span class="n">{n}</span>{h}</h2><div class="glass">{inner}</div></section>\n'
def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement":
            [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}
def page(title, desc, url, kicker, h1, lead, body, ld):
    return (HEAD.format(lang="en", stitle=e(title + " | GamerBhai" if len(title) <= 48 else title), title=e(title), desc=e(desc), url=url, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
            + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
            + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)

# platform label, key, how to enter (facts about each game's cheat system)
G = {
 "gta-5": dict(name="GTA 5", full="Grand Theft Auto V", year=2013, city="Los Santos and Blaine County", hero="Michael, Franklin and Trevor", emoji="🌴",
   plats=[("PS3 / PS4 / PS5", "ps"), ("Xbox 360 / One / Series", "xbox"), ("PC", "pc"), ("Phone (all versions)", "phone")],
   how='<ol><li><b>PlayStation / Xbox:</b> press the buttons quickly during gameplay (not in the pause menu). A message confirms the cheat.</li>'
       '<li><b>PC:</b> press <b>~</b> (tilde) to open the cheat box, type the code and press Enter.</li>'
       '<li><b>Phone:</b> press <b>Up</b> on the D-pad to take out the phone, open the keypad and dial the number.</li></ol>'
       '<div class="warnbox">⚠️ Cheats turn off trophies/achievements for that play session only. They don\'t work in GTA Online, and some are blocked during missions.</div>'),
 "gta-san-andreas": dict(name="GTA San Andreas", full="Grand Theft Auto: San Andreas", year=2004, city="Los Santos, San Fierro and Las Venturas", hero="Carl \"CJ\" Johnson", emoji="🏜️",
   plats=[("PS2 / PS4 / PS5", "ps"), ("Xbox 360 / One / Series", "xbox"), ("PC", "pc"), ("PC – Definitive Edition", "pc_alt")],
   how='<ol><li><b>PC:</b> just type the code on the keyboard during gameplay. No box opens; "Cheat activated" appears in the corner.</li>'
       '<li><b>PlayStation / Xbox:</b> press the button sequence quickly during gameplay. The same sequences work in The Trilogy – Definitive Edition.</li>'
       '<li><b>Definitive Edition on PC:</b> use the full-word code (for example <span class="code">INEEDSOMEHELP</span>) shown in the table.</li></ol>'
       '<div class="warnbox">⚠️ Save before using cheats. Some cheats (like the gang and traffic ones) stay on in your save and can break missions. On the Definitive Edition, cheats disable trophies/achievements.</div>'),
 "gta-vice-city": dict(name="GTA Vice City", full="Grand Theft Auto: Vice City", year=2002, city="Vice City", hero="Tommy Vercetti", emoji="🌆",
   plats=[("PS2 / PS4 / PS5", "ps"), ("Xbox 360 / One / Series", "xbox"), ("PC", "pc")],
   how='<ol><li><b>PC:</b> type the code during gameplay. "Cheat activated" appears on screen.</li>'
       '<li><b>PlayStation / Xbox:</b> press the button sequence quickly during gameplay. The same sequences work in The Trilogy – Definitive Edition.</li></ol>'
       '<div class="warnbox">⚠️ Save before using cheats. Saving with some cheats on (like traffic or ped changes) keeps them in your save. The Definitive Edition disables trophies/achievements for cheats.</div>'),
 "gta-3": dict(name="GTA 3", full="Grand Theft Auto III", year=2001, city="Liberty City", hero="Claude", emoji="🌃",
   plats=[("PS2 / PS4 / PS5", "ps"), ("Xbox 360 / One / Series", "xbox"), ("PC", "pc")],
   how='<ol><li><b>PC:</b> type the code during gameplay. "Cheat activated" appears on screen.</li>'
       '<li><b>PlayStation / Xbox:</b> press the button sequence quickly during gameplay. The same sequences work in The Trilogy – Definitive Edition.</li></ol>'
       '<div class="warnbox">⚠️ Save before using cheats. Using the money or weapon cheats too often can lower your criminal rating.</div>'),
 "gta-4": dict(name="GTA 4", full="Grand Theft Auto IV", year=2008, city="Liberty City", hero="Niko Bellic", emoji="🗽",
   plats=[("Phone (PS3 / Xbox 360 / PC)", "phone")],
   how='<ol><li>Press <b>Up</b> on the D-pad (or the phone key on PC) to take out Niko\'s phone.</li><li>Open the keypad, dial the number and press call.</li>'
       '<li>After the first use, the cheat is saved in the phone\'s <b>Cheats</b> menu so you can turn it on again quickly.</li></ol>'
       '<div class="warnbox">⚠️ Using cheats blocks some achievements/trophies (for example "One Man Army" and "Cleaned the Mean Streets"), even after you save.</div>'),
}
G.update({
 "gta-liberty-city-stories": dict(name="GTA Liberty City Stories", full="Grand Theft Auto: Liberty City Stories", year=2005, city="Liberty City", hero="Toni Cipriani", emoji="🎰",
   plats=[("PSP / PS2", "ps")],
   how='<ol><li>Enter the button sequence quickly during gameplay (not in a menu). A message confirms the cheat.</li><li>On PSP, <b>L1/R1</b> are the <b>L</b> and <b>R</b> shoulder buttons. The same codes work on PS2.</li></ol>'
       '<div class="warnbox">⚠️ Save before using cheats. Some cheats are counted in your stats, and a few (traffic, peds) stay on after saving.</div>'),
 "gta-vice-city-stories": dict(name="GTA Vice City Stories", full="Grand Theft Auto: Vice City Stories", year=2006, city="Vice City", hero="Victor Vance", emoji="🌴",
   plats=[("PS2 / PSP", "ps")],
   how='<ol><li>Enter the button sequence quickly during gameplay (not in a menu). A message confirms the cheat.</li><li>On PSP, <b>L1/R1</b> are the <b>L</b> and <b>R</b> shoulder buttons.</li></ol>'
       '<div class="warnbox">⚠️ Save before using cheats. Some cheats stay on after saving and can change your stats.</div>'),
 "gta-chinatown-wars": dict(name="GTA Chinatown Wars", full="Grand Theft Auto: Chinatown Wars", year=2009, city="Liberty City", hero="Huang Lee", emoji="🐉",
   plats=[("Nintendo DS", "ds"), ("PSP", "psp"), ("iPhone / Android (whiteboard)", "phone")],
   how='<ol><li><b>DS / PSP:</b> enter the button sequence during gameplay (on PSP, L1/R1 = the L and R buttons).</li><li><b>iPhone / Android:</b> go to any safehouse and arrange the letters on the <b>whiteboard</b> to spell the code (not in the free "Lite" version).</li></ol>'
       '<div class="warnbox">⚠️ Save first. Cheats can be counted in your stats.</div>'),
})
MISSIONS = {"gta-5", "gta-san-andreas", "gta-vice-city", "gta-3", "gta-4", "gta-liberty-city-stories", "gta-vice-city-stories", "gta-chinatown-wars"}
ORDER = ["gta-5", "gta-san-andreas", "gta-vice-city", "gta-3", "gta-4", "gta-liberty-city-stories", "gta-vice-city-stories", "gta-chinatown-wars"]

def group(n):
    l = n.lower()
    if l.startswith("spawn") or "parachute" in l: return "Vehicles & items"
    if any(w in l for w in ("weather", "sunny", "cloud", "fog", "storm", "rain", "sandstorm", "midnight", "clock", "sky", "hours", "gameplay", "slow motion")): return "Weather & time"
    if "wanted" in l: return "Police"
    if any(w in l for w in ("health", "armor", "weapon", "ammo", "money", "$", "invincib", "hesoyam", "hitman", "bullets", "punch")): return "Health, weapons & money"
    if l.startswith(("max", "skinny", "never hungry", "infinite lung", "super jump", "fast", "adrenaline", "suicide", "fat ", "tommy", "skinny tommy", "play as", "recharge", "moon", "drunk", "skyfall", "explosive")): return "Player"
    return "World & traffic"
GROUPS = ["Health, weapons & money", "Police", "Vehicles & items", "Player", "Weather & time", "World & traffic"]

def code_html(c, k):
    v = c.get(k, "")
    if not v: return '<span class="note">Not on this platform</span>'
    return f'<span class="code">{e(v)}</span>'

pages, hubs = [], []
for gk in ORDER:
    g, cheats = G[gk], DATA[gk]
    for c in cheats:
        c["slug"] = f"{gk}-{slugify(c['name'])}-cheat"; c["grp"] = group(c["name"])
        if gk == "gta-4" and c.get("episode"): c["grp"] = c["episode"]
    keys = [k for _, k in g["plats"] if any(c.get(k) for c in cheats)]
    plats = [(lab, k) for lab, k in g["plats"] if k in keys]
    for c in cheats:
        n, url = c["name"], BASE + c["slug"]
        main = [(lab, c[k]) for lab, k in plats if c.get(k)]
        rows = "".join(f'<tr><td><b>{e(lab)}</b></td><td>{code_html(c, k)}</td></tr>' for lab, k in plats)
        title = f"{g['name']} {n} Cheat"
        desc = clip(f"{g['name']} {n} cheat code: " + "; ".join(f"{lab.split(' (')[0]}: {v}" for lab, v in main) + ". How to enter it, plus related cheats.")
        body = sec("01", "The code", f'<div class="gtable"><table class="cheats cw"><tbody>{rows}</tbody></table></div>')
        eff = c.get("effect", n)
        ep = f' This cheat is from the <b>{e(c["episode"])}</b> episode (Episodes from Liberty City).' if c.get("episode") else ""
        body += sec("02", "What it does", f'<p>{e(eff[:1].upper() + eff[1:])}.{ep}</p>')
        body += sec("03", "How to enter it", g["how"])
        rel = [x for x in cheats if x is not c and x["grp"] == c["grp"]][:8] or [x for x in cheats if x is not c][:6]
        body += (f'  <section class="reveal"><h2><span class="n">04</span>More {e(g["name"])} cheats</h2><div class="grid">'
                 + "".join(f'<a class="glass tilt area" href="{x["slug"]}"><div class="pop"><div class="ic">{g["emoji"]}</div><h3>{e(x["name"])}</h3><p class="code">{e(x.get("pc") or x.get("phone") or x.get("ps") or x.get("ds",""))[:60]}</p></div></a>' for x in rel)
                 + f'</div><p class="note"><a href="{gk}-cheats">All {len(cheats)} {e(g["name"])} cheats →</a> · <a href="gta-cheats">Cheats for every GTA →</a> · <a href="guides#cheats">GTA 6 cheats →</a></p></section>\n')
        body += '  <p class="note">Codes are cross-checked with the GTA Wiki (CC BY-SA) and long-standing community lists. Unofficial fan guide, not affiliated with Rockstar Games.</p>\n'
        first = main[0][1] if main else ""
        ld = [crumbs([("Home", ""), ("GTA cheats", "gta-cheats"), (f"{g['name']} cheats", f"{gk}-cheats"), (n, c["slug"])]),
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                  {"@type": "Question", "name": f"What is the {n} cheat in {g['name']}?", "acceptedAnswer": {"@type": "Answer", "text": "; ".join(f"{lab}: {v}" for lab, v in main) + "."}}]}]
        lead = f'{g["emoji"]} ' + " · ".join(f'{e(lab.split(" (")[0].split(" – ")[0])}: <b class="code">{e(v)}</b>' for lab, v in main[:3])
        open(os.path.join(SITE, c["slug"] + ".html"), "w", encoding="utf-8").write(
            page(title, desc, url, f"{e(g['name'].upper())} CHEATS · {e(c['grp'].upper())}", title, lead, body, ld))
        pages.append(c["slug"])
    # ---- game hub
    head = "".join(f"<th>{e(lab)}</th>" for lab, _ in plats)
    body = sec("01", "How to use cheats", g["how"])
    n = 2
    grps = [x for x in GROUPS if any(c["grp"] == x for c in cheats)] + sorted({c["grp"] for c in cheats} - set(GROUPS))
    for gr in grps:
        rows = "".join(f'<tr><td><a href="{c["slug"]}">{e(c["name"])}</a></td>' + "".join(f'<td>{code_html(c, k)}</td>' for _, k in plats) + '</tr>' for c in cheats if c["grp"] == gr)
        body += sec(f"{n:02d}", e(gr), f'<div class="gtable"><table class="cheats cw"><thead><tr><th>Cheat</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>'); n += 1
    body += f'  <p class="note">' + (f'📖 <a href="{gk}-missions">All {e(g["name"])} missions (walkthrough)</a> · ✅ <a href="{gk}-100-percent-completion">100% checklist</a> · ' if gk in MISSIONS else '') + 'Other games: ' + " · ".join(f'<a href="{o}-cheats">{e(G[o]["name"])} cheats</a>' for o in ORDER if o != gk) + ' · <a href="guides#cheats">GTA 6 cheats</a>. Codes cross-checked with the GTA Wiki (CC BY-SA). Unofficial fan guide.</p>\n'
    top = ", ".join(f'{c["name"]} ({c.get("pc") or c.get("phone")})' for c in cheats[:3] if c.get("pc") or c.get("phone"))
    title = f"All {g['name']} Cheats ({len(cheats)} Codes)"
    desc = clip(f"Every {g['name']} cheat code for " + ", ".join(lab for lab, _ in plats) + f": {top} and more. How to enter them, one page per cheat.")
    ld = [crumbs([("Home", ""), ("GTA cheats", "gta-cheats"), (f"{g['name']} cheats", f"{gk}-cheats")])]
    open(os.path.join(SITE, f"{gk}-cheats.html"), "w", encoding="utf-8").write(
        page(title, desc, BASE + f"{gk}-cheats", f"{e(g['full'].upper())} · {g['year']}", f"{g['name']} Cheats", f'{g["emoji"]} All {len(cheats)} cheat codes for {e(g["full"])} ({g["year"]}) – {e(g["city"])}, playing as {e(g["hero"])}.', body, ld))
    hubs.append(f"{gk}-cheats")

# ---- all-games hub
cards = '<div class="grid"><a class="glass tilt area" href="guides#cheats"><div class="pop"><div class="ic">🌴</div><h3>GTA 6 cheats</h3><p>17 confirmed codes for PS5 &amp; Xbox Series X|S (2026)</p></div></a>' + "".join(
    f'<a class="glass tilt area" href="{gk}-cheats"><div class="pop"><div class="ic">{G[gk]["emoji"]}</div><h3>{e(G[gk]["name"])} cheats</h3><p>{len(DATA[gk])} codes · {G[gk]["year"]} · {e(", ".join(l for l, _ in G[gk]["plats"]))}</p></div></a>' for gk in ORDER) + '</div><p class="note">📖 Mission walkthroughs: <a href="walkthrough">GTA 6</a> · ' + " · ".join(f'<a href="{gk}-missions">{e(G[gk]["name"])}</a>' for gk in ORDER if gk in MISSIONS) + '</p>'
pop = ""
for gk, nm in (("gta-san-andreas", "Health, Armor & $250,000 (HESOYAM)"), ("gta-san-andreas", "Never Wanted"), ("gta-5", "Invincibility"), ("gta-5", "Max Health & Armor"), ("gta-vice-city", "Full Health"), ("gta-4", "Health, Armor & Ammo")):
    c = next((x for x in DATA[gk] if x["name"] == nm), None)
    if c: pop += f'<tr><td><a href="{c["slug"]}">{e(G[gk]["name"])} – {e(nm)}</a></td><td><span class="code">{e(c.get("pc") or c.get("phone"))}</span></td></tr>'
body = sec("01", "Pick your game", cards) + sec("02", "Most searched cheats", f'<div class="gtable"><table class="cheats cw"><thead><tr><th>Cheat</th><th>PC / phone code</th></tr></thead><tbody>{pop}</tbody></table></div>')
total = sum(len(DATA[g]) for g in ORDER)
open(os.path.join(SITE, "gta-cheats.html"), "w", encoding="utf-8").write(
    page("All GTA Cheats & Missions: GTA 6, 5, San Andreas, Vice City, 4, 3", clip(f"Cheat codes for every Grand Theft Auto: GTA 6, GTA 5, San Andreas, Vice City, GTA 4, GTA 3, Liberty City Stories, Vice City Stories and Chinatown Wars – {total}+ codes for PC, PlayStation, Xbox and phone."),
         BASE + "gta-cheats", "GTA CHEATS · EVERY GAME", "GTA Cheats for Every Game", f"🎮 {total}+ cheat codes across 9 Grand Theft Auto games – one page per cheat.", body,
         [crumbs([("Home", ""), ("GTA cheats", "gta-cheats")])]))
hubs.append("gta-cheats")

# ---- sitemap + indexnow
sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in hubs + pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(f"{len(pages)} cheat pages + {len(hubs)} hubs; sitemap {sm.count('<url>')} urls")
