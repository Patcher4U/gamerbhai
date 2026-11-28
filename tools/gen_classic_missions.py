"""Mission pages for GTA III, Vice City, San Andreas, GTA IV and GTA V - data only.
  python -I tools/gen_classic_missions.py gta6-site
Data: tools/classic_missions.json (tools/parse_missions.py, from the GTA Wiki mission tables, CC BY-SA - credited on every page).
Builds one page per story mission + a full mission list per game (<game>-missions), updates sitemap + indexnow.
"""
import html, json, os, re, sys, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SITE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "gta6-site"))
BASE = "https://gamerbhai.com/"; TODAY = "2026-11-28"
e = lambda s: html.escape(s, quote=True)
asrc = open(os.path.join(HERE, "gen_articles.py"), encoding="utf-8").read()
A = {}; exec(asrc[asrc.index("HEAD ="):asrc.index("def fmt")], A); HEAD, FOOT = A["HEAD"], A["FOOT"]
DATA = json.load(open(os.path.join(HERE, "classic_missions.json"), encoding="utf-8"))

def slugify(s): return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower().replace("'", "").replace("&", "and").replace("$", "").replace(",", "").replace(".", ""))).strip("-")
def clip(t, n=158): return t if len(t) <= n else t[:t.rfind(' ', 0, n - 1)].rstrip(' ,.:;') + '…'
def sec(n, h, inner): return f'  <section class="reveal"><h2><span class="n">{n}</span>{h}</h2><div class="glass">{inner}</div></section>\n'
def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement":
            [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}
def page(title, desc, url, kicker, h1, lead, body, ld):
    return (HEAD.format(lang="en", stitle=e(title + " | GamerBhai" if len(title) <= 48 else title), title=e(title), desc=e(desc), url=url, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
            + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
            + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)

G = {"gta-5": dict(name="GTA 5", emoji="🌴", area="Chapter", heal=("Max Health & Armor", "TURTLE (PC) or call 1-999-887-853", "gta-5-max-health-and-armor-cheat")),
     "gta-san-andreas": dict(name="GTA San Andreas", emoji="🏜️", area="Area", heal=("Health, Armor & $250,000", "HESOYAM (PC)", "gta-san-andreas-health-armor-and-250000-hesoyam-cheat")),
     "gta-vice-city": dict(name="GTA Vice City", emoji="🌆", area="Section", heal=("Full Health", "ASPIRINE (PC)", "gta-vice-city-full-health-cheat")),
     "gta-3": dict(name="GTA 3", emoji="🌃", area="Island", heal=("Full Health", "GESUNDHEIT (PC)", "gta-3-full-health-cheat")),
     "gta-4": dict(name="GTA 4", emoji="🗽", area="Part", heal=("Health & Armor", "call 362-555-0100", "gta-4-health-and-armor-cheat"))}
G["gta-liberty-city-stories"] = dict(name="GTA Liberty City Stories", emoji="🎰", area="Island", heal=("Full Health", "L1, R1, X, L1, R1, Square, L1, R1", "gta-liberty-city-stories-full-health-cheat"))
G["gta-vice-city-stories"] = dict(name="GTA Vice City Stories", emoji="🌴", area="Area", heal=("Full Health", "Up, Down, Left, Right, Circle, Circle, L1, R1", "gta-vice-city-stories-full-health-cheat"))
G["gta-the-lost-and-damned"] = dict(name="GTA The Lost and Damned", emoji="🏍️", area="Part", cheats="gta-4-cheats", heal=("Health & Armor", "call 362-555-0100", "gta-4-health-and-armor-cheat"))
G["gta-the-ballad-of-gay-tony"] = dict(name="GTA The Ballad of Gay Tony", emoji="🪩", area="Part", cheats="gta-4-cheats", heal=("Health & Armor", "call 362-555-0100", "gta-4-health-and-armor-cheat"))
G["gta-chinatown-wars"] = dict(name="GTA Chinatown Wars", emoji="🐉", area="City", heal=("Full Health", "L, L, R, A, A, B, B, R on DS or LIFEUP on the mobile whiteboard", "gta-chinatown-wars-full-health-cheat"))
ORDER = [g for g in ["gta-5", "gta-san-andreas", "gta-vice-city", "gta-3", "gta-4", "gta-liberty-city-stories", "gta-vice-city-stories", "gta-chinatown-wars", "gta-the-lost-and-damned", "gta-the-ballad-of-gay-tony"] if g in DATA and g in G]

pages, hubs = [], []
for gk in ORDER:
    g, ms = G[gk], DATA[gk]
    used = set()
    for m in ms:
        s = f"{gk}-{slugify(m['name'])}-mission"
        if s in used: s = s.replace("-mission", f"-{slugify(m['giver'] or m['region'])}-mission")
        used.add(s); m["slug"] = s
    N = len(ms)
    for i, m in enumerate(ms):
        n, prev, nxt = m["name"], ms[i - 1] if i else None, ms[i + 1] if i + 1 < N else None
        wiki = "https://gta.fandom.com/wiki/" + urllib.parse.quote(n.replace(" ", "_"))
        yt = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(f"{g['name']} {n} mission walkthrough")
        rows = f'<tr><td><b>Mission</b></td><td>{i + 1} of {N} in the story list</td></tr>'
        if m["region"]: rows += f'<tr><td><b>{g["area"]}</b></td><td>{e(m["region"])}</td></tr>'
        if m["giver"]: rows += f'<tr><td><b>Given by</b></td><td>{e(m["giver"])}</td></tr>'
        rows += f'<tr><td><b>Reward</b></td><td>{e(m["reward"]) if m["reward"] else "No cash reward (story progress)"}</td></tr>'
        if prev: rows += f'<tr><td><b>Before</b></td><td><a href="{prev["slug"]}">{e(prev["name"])}</a></td></tr>'
        if nxt: rows += f'<tr><td><b>After</b></td><td><a href="{nxt["slug"]}">{e(nxt["name"])}</a></td></tr>'
        body = sec("01", "Mission at a glance", f'<div class="gtable"><table class="cheats cw"><tbody>{rows}</tbody></table></div>')
        body += sec("02", "What happens", f'<p>{e(m["desc"])}</p><p class="note">Summary from the <a href="{wiki}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0).</p>')
        hn, hc, hs = g["heal"]
        body += sec("03", "Tips", f'<ul><li>💾 Save at a safehouse before starting – if you fail, you restart with full health and your weapons.</li>'
                    f'<li>❤️ Low on health? The <a href="{hs}">{e(hn)} cheat</a> is {e(hc)}. See <a href="{g.get("cheats", gk + "-cheats")}">all {e(g["name"])} cheats</a> (cheats can block achievements/trophies).</li>'
                    f'<li>▶️ Stuck? <a href="{yt}" rel="nofollow noopener" target="_blank">Watch a video walkthrough of “{e(n)}” on YouTube</a>.</li></ul>')
        nav = "".join(f'<a class="glass tilt area" href="{x["slug"]}"><div class="pop"><div class="ic">{lab}</div><h3>{e(x["name"])}</h3><p>{e(x["giver"] or x["region"])}</p></div></a>' for lab, x in (("⬅️", prev), ("➡️", nxt)) if x)
        body += f'  <section class="reveal"><h2><span class="n">04</span>Previous &amp; next mission</h2><div class="grid">{nav}</div><p class="note"><a href="{gk}-missions">All {N} {e(g["name"])} missions →</a> · <a href="{g.get("cheats", gk + "-cheats")}">{e(g["name"])} cheats →</a> · <a href="gta-cheats">Every GTA game →</a></p></section>\n'
        body += '  <p class="note">Unofficial fan guide, not affiliated with Rockstar Games.</p>\n'
        title = f"{g['name']} “{n}” Mission Walkthrough"
        bits = [f"mission {i + 1} of {N}"] + ([f"given by {m['giver']}"] if m["giver"] else []) + ([f"reward: {m['reward']}"] if m["reward"] else [])
        desc = clip(f"{g['name']} “{n}” ({', '.join(bits)}). {m['desc']}")
        lead = f'{g["emoji"]} Mission {i + 1} of {N}' + (f' · {e(m["region"])}' if m["region"] else "") + (f' · Given by <b>{e(m["giver"])}</b>' if m["giver"] else "")
        ld = [crumbs([("Home", ""), (f"{g['name']} missions", f"{gk}-missions"), (n, m["slug"])])]
        open(os.path.join(SITE, m["slug"] + ".html"), "w", encoding="utf-8").write(
            page(title, desc, BASE + m["slug"], f"{e(g['name'].upper())} · MISSION {i + 1}", f"{g['name']}: {n}", lead, body, ld))
        pages.append(m["slug"])
    # ---- mission list hub
    body, k, cur, rows = "", 1, None, []
    def flush():
        global body, k
        if rows:
            body += sec(f"{k:02d}", e(cur or "Missions"), '<div class="gtable"><table class="cheats cw"><thead><tr><th>#</th><th>Mission</th><th>Given by</th><th>Reward</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>'); k += 1
    for i, m in enumerate(ms):
        if m["region"] != cur:
            flush(); rows = []; cur = m["region"]
        rows.append(f'<tr><td>{i + 1}</td><td><a href="{m["slug"]}">{e(m["name"])}</a></td><td>{e(m["giver"])}</td><td><small>{e(m["reward"])}</small></td></tr>')
    flush()
    extra = [(f"{gk}-{s2}", lab) for s2, lab in (("100-percent-completion", f"✅ {e(g['name'])} 100% completion checklist"), ("weapons", "🔫 weapons"), ("safehouses", "🏠 safehouses"), ("radio-stations", "📻 radio stations"), ("vehicles", "🚗 vehicles"), ("characters", "👥 characters"), ("achievements", "🏆 achievements")) if os.path.exists(os.path.join(SITE, f"{gk}-{s2}.html"))]
    body += f'  <p class="note">' + " · ".join(f'<a href="{u}">{lab}</a>' for u, lab in extra) + (' · 🃏 <a href="gta-5-strangers-and-freaks">Strangers and Freaks side missions</a> · 🎲 <a href="gta-5-random-events">random events</a>' if gk == "gta-5" else '') + (' · 💘 <a href="gta-san-andreas-girlfriends">girlfriends guide</a>' if gk == "gta-san-andreas" else '') + '. Other games: ' + " · ".join(f'<a href="{o}-missions">{e(G[o]["name"])} missions</a>' for o in ORDER if o != gk) + f' · <a href="{g.get("cheats", gk + "-cheats")}">{e(g["name"])} cheats</a> · <a href="walkthrough">GTA 6 walkthrough</a>. Mission data from the GTA Wiki (CC BY-SA 3.0). Unofficial fan guide.</p>\n'
    title = f"All {N} {g['name']} Missions: Full List & Walkthrough"
    desc = clip(f"Every {g['name']} story mission in order ({N} missions), from “{ms[0]['name']}” to “{ms[-1]['name']}”, with who gives each mission and the reward.")
    open(os.path.join(SITE, f"{gk}-missions.html"), "w", encoding="utf-8").write(
        page(title, desc, BASE + f"{gk}-missions", f"{e(g['name'].upper())} · WALKTHROUGH", f"{g['name']} Missions", f'{g["emoji"]} All {N} story missions in order, with mission giver and reward. Tap a mission for its page.', body,
             [crumbs([("Home", ""), (f"{g['name']} missions", f"{gk}-missions")])]))
    hubs.append(f"{gk}-missions")

sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in hubs + pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(f"{len(pages)} mission pages + {len(hubs)} hubs; sitemap {sm.count('<url>')} urls")
