"""GTA 5 random events + GTA San Andreas girlfriends pages - data only.
  python -I tools/gen_side.py <folder with re_v.json gf_sa.json> gta6-site
Data: GTA Wiki "Random Events in GTA V" and "Girlfriends in GTA San Andreas" (CC BY-SA, credited on every page), saved by the browser.
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
def tbl(rows, head=None):
    th = "<thead><tr>" + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr></thead>" if head else ""
    return f'<div class="gtable"><table class="cheats cw">{th}<tbody>' + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>"
def credit(page): return f'<p class="note">Data from the <a href="https://gta.fandom.com/wiki/{page}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). Unofficial fan guide, not affiliated with Rockstar Games.</p>'
def page(title, desc, url, kicker, h1, lead, body, crumbs):
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(crumbs)]}]
    open(os.path.join(SITE, url + ".html"), "w", encoding="utf-8").write(
        HEAD.format(lang="en", stitle=e(title), title=e(title), desc=e(desc), url=BASE + url, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
        + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
        + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)
    pages.append(url)
load = lambda f: json.loads(fix(open(os.path.join(SRC, f), encoding="utf-8").read()))
pages = []

# ---------------- GTA 5 random events
raw = load("re_v.json"); ev, cur, on, excl = [], None, False, False
for x in raw:
    if "h" in x:
        h = x["h"]
        if h == "Events": on = True; continue
        if not on: continue
        if h in ("Videos", "Oversights", "Trivia"): break
        if h.startswith("Exclusive"): excl = True; continue
        cur = dict(name=h, slug=f"gta-5-{slugify(h)}-random-event", spawns=[], notes=[], excl=excl); ev.append(cur); continue
    if not cur: continue
    if "table" in x:
        hd = [c.lower() for c in x["table"][0]]
        for r in x["table"][1:]:
            g = lambda n: r[hd.index(n)] if n in hd and hd.index(n) < len(r) else ""
            loc = g("location/characters") or g("location"); who = ""
            m = re.match(r"(.*?)\s*-\s*((?:All characters|Michael|Franklin|Trevor)[^-]*)$", loc)
            if m: loc, who = m.group(1).strip(), m.group(2).strip().rstrip(".")
            cur["spawns"].append(dict(loc=loc, who=who, desc=g("description"), rew=g("reward")))
    elif "li" in x: cur["notes"].append(re.sub(r"^Note:\s*", "", x["li"]))
    elif "p" in x and "checklist map" not in x["p"]: cur["notes"].append(x["p"])
ev = [v for v in ev if v["spawns"]]
REH = "gta-5-random-events"; NS = sum(len(v["spawns"]) for v in ev)
for i, v in enumerate(ev):
    body, k = "", 1
    if v["excl"]: body += '  <div class="warnbox">⭐ This event is only for returning players on the enhanced PS5 / Xbox Series X|S / PC version.</div>\n'
    for j, s in enumerate(v["spawns"]):
        rows = [[f"<b>Where</b>", e(s["loc"])]] + ([[f"<b>Who can get it</b>", e(s["who"])]] if s["who"] else []) + [[f"<b>What happens</b>", e(s["desc"])], [f"<b>Reward</b>", e(s["rew"] or "No reward")]]
        body += sec(k, f"{e(v['name'])}" + (f" – location {j + 1}" if len(v["spawns"]) > 1 else ""), tbl(rows)); k += 1
    if v["notes"]: body += sec(k, "Tips &amp; notes", "<ul>" + "".join(f"<li>{e(n)}</li>" for n in v["notes"]) + "</ul>"); k += 1
    yt = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(f"GTA 5 {v['name']} random event")
    nav = " · ".join(f'<a href="{o["slug"]}">{lab} {e(o["name"])}</a>' for lab, o in (("⬅️", ev[i - 1] if i else None), ("➡️", ev[i + 1] if i + 1 < len(ev) else None)) if o)
    body += f'  <p class="note">▶️ <a href="{yt}" rel="nofollow noopener" target="_blank">Watch “{e(v["name"])}” on YouTube</a> · {nav}</p>\n  <p class="note"><a href="{REH}">All GTA 5 random events →</a> · <a href="gta-5-100-percent-completion">GTA 5 100% checklist</a> (14 random events count) · <a href="gta-5-strangers-and-freaks">Strangers and Freaks</a> · <a href="gta-5-cheats">GTA 5 cheats</a></p>\n  {credit("Random_Events_in_GTA_V")}\n'
    n = len(v["spawns"]); rew = v["spawns"][0]["rew"]
    page(f"GTA 5 “{v['name']}” Random Event: Locations & Reward", clip(f"GTA 5 {v['name']} random event: {n} location{'s' if n > 1 else ''} – {v['spawns'][0]['loc']}. {v['spawns'][0]['desc']} Reward: {rew or 'none'}."),
         v["slug"], "GTA 5 · RANDOM EVENT", f"GTA 5: {v['name']}", f"🌴 {n} location{'s' if n > 1 else ''} · " + e(clip(v['spawns'][0]['desc'], 120)), body,
         [("Home", ""), ("Random events", REH), (v["name"], v["slug"])])
body = sec(1, "How random events work", "<p>Random events are short encounters that pop up while you explore Los Santos and Blaine County: a robbery, a car crash, a hitchhiker. A <b>light blue dot</b> on the minimap means someone needs help; a <b>red dot</b> means trouble. Help (or rob) them for cash, stat boosts and sometimes a new contact. "
             '<b>14 random events</b> are needed for <a href="gta-5-100-percent-completion">100% completion</a>. Many only appear once, and some are limited to one character or need the story to reach a certain point.</p>')
body += sec(2, f"All {len(ev)} random events", tbl([[f'<a href="{v["slug"]}">{e(v["name"])}</a>' + (" ⭐" if v["excl"] else ""), str(len(v["spawns"])), e(clip(v["spawns"][0]["rew"] or "No reward", 90))] for v in ev], ["Event", "Locations", "Reward (first location)"])
             + '<p class="note">⭐ = enhanced version, returning players only.</p>')
body += f'  <p class="note">More: <a href="gta-5-strangers-and-freaks">Strangers and Freaks</a> · <a href="gta-5-missions">GTA 5 story missions</a> · <a href="gta-5-cheats">GTA 5 cheats</a></p>\n  {credit("Random_Events_in_GTA_V")}\n'
page(f"All GTA 5 Random Events: Locations & Rewards ({NS} spawns)", clip(f"Every GTA 5 random event ({len(ev)} types, {NS} locations) with where it spawns, which character can get it and the reward. 14 count for 100%."),
     REH, "GTA 5 · RANDOM EVENTS", "GTA 5 Random Events", f"🌴 {len(ev)} event types · {NS} locations · 14 needed for 100%", body, [("Home", ""), ("Random events", REH)])

# ---------------- GTA San Andreas girlfriends (one guide page)
raw = load("gf_sa.json"); T = {}; h = None
for x in raw:
    if "h" in x: h = x["h"]
    elif "table" in x and h not in T: T[h] = x["table"]
gfs = {}
for r in T["Overview"][1:]:
    g = gfs.setdefault(r[0], {"met": r[2], "stats": []})
    if r[4] != "No requirements": g["stats"].append(f"{r[3]} {r[4]}")
def cols(t):
    hd = t[0]; return {hd[c]: {r[0]: r[c] for r in t[1:]} for c in range(1, len(hd))}
avail, food, rew = cols(T["Availability"]), cols(T["Restaurant Preferences"]), cols(T["Progress Rewards"])
body, k = sec(1, "How dating works", "<p>CJ can date six girlfriends. Only <b>Millie</b> matters for the story: you need her keycard for the casino heist (<a href=\"gta-san-andreas-key-to-her-heart-mission\">Key to Her Heart</a>). Denise and Millie are met in missions; Helena, Katie, Michelle and Barbara become available after <a href=\"gta-san-andreas-the-green-sabre-mission\">The Green Sabre</a> or as the map opens up.</p>"
                 "<p>A good date raises her relationship meter by 5%, a bad one lowers it by 5%. Take her to the kind of place she likes, drive carefully, and bring her home on time. Gifts (like flowers) and a successful kiss add 1%. If you stop calling, the meter slowly drops and she may dump CJ.</p>"), 2
for name, g in gfs.items():
    short = name.split()[0]
    rows = [["<b>Where to meet her</b>", e(g["met"])], ["<b>Stats she wants</b>", e(", ".join(g["stats"]) or "No requirements")]]
    if short in avail: rows.append(["<b>Date times</b>", e(re.sub(r"(\d\d:\d\d)(\d\d:\d\d)", r"\1, \2", avail[short].get("Time of day", "")))])
    if short in food:
        good = [p for p, v in food[short].items() if "Success" in v]
        if good: rows.append(["<b>Favourite place to eat</b>", e(", ".join(good))])
    if short in rew:
        for lvl, v in rew[short].items():
            if v and v != "N/A": rows.append([f"<b>Reward ({e(lvl)})</b>", e(v)])
    body += sec(k, e(name), tbl(rows)); k += 1
body += f'  <p class="note">More: <a href="gta-san-andreas-100-percent-completion">San Andreas 100% checklist</a> · <a href="gta-san-andreas-missions">San Andreas missions</a> · <a href="gta-san-andreas-cheats">San Andreas cheats</a></p>\n  {credit("Girlfriends_in_GTA_San_Andreas")}\n'
page("GTA San Andreas Girlfriends: Where to Find All 6 & Rewards", "All 6 GTA San Andreas girlfriends: where to meet each one, the stats she wants, date times, her favourite place to eat and the car and outfit rewards.",
     "gta-san-andreas-girlfriends", "GTA SAN ANDREAS · GIRLFRIENDS", "San Andreas Girlfriends", "🏜️ Where to meet all six, what they like, and what CJ gets at 50% and 100%.", body,
     [("Home", ""), ("GTA San Andreas missions", "gta-san-andreas-missions"), ("Girlfriends", "gta-san-andreas-girlfriends")])

sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(len(pages), "pages;", len(ev), "events,", NS, "spawns,", len(gfs), "girlfriends; sitemap", sm.count("<url>"), "urls")
