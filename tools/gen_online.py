"""GTA Online pages - data only.
  python -I tools/gen_online.py <folder with o_*.json> gta6-site
Data: GTA Wiki (CC BY-SA, credited on every page), saved by the browser.
Builds: gta-online (hub), gta-online-heists, gta-online-contact-missions + gta-online-<contact>-missions, gta-online-ranks, gta-online-adversary-modes.
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = sys.argv[1]; SITE = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "gta6-site"))
BASE = "https://gamerbhai.com/"; TODAY = "2026-11-29"
e = lambda s: html.escape(s, quote=True)
asrc = open(os.path.join(HERE, "gen_articles.py"), encoding="utf-8").read()
A = {}; exec(asrc[asrc.index("HEAD ="):asrc.index("def fmt")], A); HEAD, FOOT = A["HEAD"], A["FOOT"]
sys.path.insert(0, HERE); from wiki_clean import fix
def slugify(s): return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower().replace("'", "").replace("&", "and").replace("$", "").replace(",", "").replace(".", ""))).strip("-")
def clip(t, n=158): return t if len(t) <= n else t[:t.rfind(' ', 0, n - 1)].rstrip(' ,.:;') + '…'
def sec(n, h, inner): return f'  <section class="reveal"><h2><span class="n">{n:02d}</span>{h}</h2><div class="glass">{inner}</div></section>\n'
def tbl(head, rows): return '<div class="gtable"><table class="cheats cw"><thead><tr>' + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>"
load = lambda f: json.loads(fix(open(os.path.join(SRC, f + ".json"), encoding="utf-8").read())) if os.path.exists(os.path.join(SRC, f + ".json")) else []
def credit(pg): return f'  <p class="note">Data from the <a href="https://gta.fandom.com/wiki/{pg}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). GTA Online changes with every update, so payouts can differ from what you see in game. Unofficial fan guide, not affiliated with Rockstar Games.</p>\n'
MORE = '  <p class="note">More GTA Online: <a href="gta-online">GTA Online hub</a> · <a href="gta-online-heists">heists</a> · <a href="gta-online-contact-missions">contact missions</a> · <a href="gta-online-ranks">ranks &amp; RP</a> · <a href="gta-online-adversary-modes">adversary modes</a> · <a href="gta-5-cheats">GTA 5 story cheats</a> (cheats do not work in Online)</p>\n'
pages = []
def write(slug, title, desc, kicker, h1, lead, body, crumbs):
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(crumbs)]}]
    open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(
        HEAD.format(lang="en", stitle=e(title), title=e(title), desc=e(desc), url=BASE + slug, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
        + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
        + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)
    pages.append(slug)
def table_rows(t, drop=("Image",)):
    hd = t[0]; keep = [j for j, h in enumerate(hd) if h not in drop and any(j < len(r) and r[j] for r in t[1:])]
    return [hd[j] for j in keep], [[e(r[j]) if j < len(r) else "" for j in keep] for r in t[1:] if r and r[0] != hd[0]]

# ---------- heists
d = load("o_heists"); body, i, top, heists, cur = "", 1, None, [], None
SKIP = ("Heists", "Doomsday Heists", "Approaches", "Targets", "Bonus Rewards", "Elite Challenges", "Primary Targets", "Secondary Targets")
for x in d:
    if "h" in x:
        h = x["h"]
        if h in ("Original Heists", "The Doomsday Heist") or (h.startswith("The ") and h.endswith("Heist") and (cur is None or cur["name"] != h)):
            cur = {"name": h if h != "Original Heists" else "The Original Heists", "parts": []}; heists.append(cur); sub = None; continue
        sub = h;
        if cur: cur["parts"].append(("h", h))
        continue
    if cur is None: continue
    if "table" in x:
        hd, rows = table_rows(x["table"])
        if hd == ["Description"]: cur["parts"].append(("ul", [r[0] for r in rows]))
        elif rows: cur["parts"].append(("t", hd, rows))
    elif "p" in x: cur["parts"].append(("p", x["p"]))
    elif "li" in x: cur["parts"].append(("li", x["li"]))
for hst in heists:
    inner, ul, seen_h = "", [], set()
    for prt in hst["parts"]:
        if prt[0] != "li" and ul: inner += "<ul>" + "".join(f"<li>{e(t)}</li>" for t in ul) + "</ul>"; ul = []
        if prt[0] == "h":
            if prt[1] not in (hst["name"],): inner += f"<h3>{e(prt[1])}</h3>"
        elif prt[0] == "p": inner += f"<p>{e(prt[1])}</p>"
        elif prt[0] == "li": ul.append(prt[1])
        elif prt[0] == "ul": inner += "<ul>" + "".join(f"<li>{t}</li>" for t in prt[1]) + "</ul>"
        else: inner += tbl(prt[1], prt[2])
    if ul: inner += "<ul>" + "".join(f"<li>{e(t)}</li>" for t in ul) + "</ul>"
    inner = re.sub(r"(<h3>[^<]*</h3>)+(?=<h3>)", "", inner)  # drop empty sub-headings
    body += sec(i, e(hst["name"]), inner); i += 1
if heists:
    body += MORE + credit("Heists_in_GTA_Online")
    write("gta-online-heists", "All GTA Online Heists: Payouts, Setup Costs & Bonuses", "Every GTA Online heist – Fleeca to Pacific Standard, Doomsday, Diamond Casino, Cayo Perico and more – with setup costs, potential take by difficulty and bonus challenges.",
          "GTA ONLINE · HEISTS", "GTA Online Heists", f"💰 {len(heists)} heist series with setup costs, potential takes and bonus rewards.", body, [("Home", ""), ("GTA Online", "gta-online"), ("Heists", "gta-online-heists")])
    print("heists", len(heists))

# ---------- contact missions
d = load("o_contact"); contacts, h, intro = [], None, []
for x in d:
    if "h" in x: h = x["h"]; continue
    if h == "Description" and "p" in x: intro.append(x["p"])
    if "table" in x and h and x["table"] and x["table"][0] and x["table"][0][0] == "Mission":
        hd, rows = table_rows(x["table"])
        hd = [re.sub(r"\s*\(.*", "", c).replace("RP Reward 16+ Mins", "RP (16+ min)").replace("Money Reward 16+ Mins", "Cash (16+ min)") for c in hd]
        contacts.append({"name": h, "slug": f"gta-online-{slugify(h)}-missions", "hd": hd, "rows": rows})
seen = set(); contacts = [c for c in contacts if not (c["slug"] in seen or seen.add(c["slug"]))]
for c in contacts:
    others = " · ".join(f'<a href="{o["slug"]}">{e(o["name"])}</a>' for o in contacts if o is not c)
    body = sec(1, f"{e(c['name'])} missions ({len(c['rows'])})", tbl(c["hd"], c["rows"]))
    body += sec(2, "Tips", "<ul><li>💵 Contact mission pay scales with how long the mission took: finishing in under ~4 minutes pays much less than taking 15+ minutes.</li><li>👥 Most can be played solo, but some need 2 or more players – check the Players column.</li><li>📱 Missions unlock as your rank goes up; call the contact or use the Quick Job menu to start one.</li></ul>")
    body += f'  <p class="note"><a href="gta-online-contact-missions">All GTA Online contact missions →</a></p>\n  <p class="note">Other contacts: {others}</p>\n' + MORE + credit("Contact_Missions")
    n = len(c["rows"])
    write(c["slug"], f"GTA Online {c['name']} Missions: Full List & Rewards", clip(f"All {n} GTA Online {c['name']} missions with unlock rank, number of players and RP/cash reward: " + ", ".join(r[0] for r in c["rows"][:4]) + "…"),
          "GTA ONLINE · CONTACT MISSIONS", f"{c['name']} Missions", f"📱 {n} missions · unlock rank, players and rewards.", body, [("Home", ""), ("GTA Online", "gta-online"), ("Contact missions", "gta-online-contact-missions"), (c["name"], c["slug"])])
if contacts:
    rows = [[f'<a href="{c["slug"]}">{e(c["name"])}</a>', str(len(c["rows"])), e(", ".join(r[0] for r in c["rows"][:3]))] for c in contacts]
    body = (sec(1, "How contact missions work", "".join(f"<p>{e(p)}</p>" for p in intro[:2]) or "<p>Contact missions are jobs given by characters on your phone.</p>")
            + sec(2, f"All {len(contacts)} contacts", tbl(["Contact", "Missions", "First missions"], rows)) + MORE + credit("Contact_Missions"))
    tot = sum(len(c["rows"]) for c in contacts)
    write("gta-online-contact-missions", f"All GTA Online Contact Missions ({tot}) by Contact", clip(f"Every GTA Online contact mission ({tot}) grouped by contact – Lamar, Gerald, Simeon, Lester, Martin Madrazo, Trevor and more – with rank, players and rewards."),
          "GTA ONLINE · CONTACT MISSIONS", "GTA Online Contact Missions", f"📱 {tot} missions from {len(contacts)} contacts.", body, [("Home", ""), ("GTA Online", "gta-online"), ("Contact missions", "gta-online-contact-missions")])
    print("contacts", len(contacts), tot)

# ---------- ranks
d = load("o_ranks"); rp, unl, h = [], {}, None
for x in d:
    if "h" in x: h = x["h"]; continue
    if "table" in x and x["table"] and x["table"][0][:2] == ["Rank", "Rep Points Required"]:
        rp = [r for r in x["table"][1:] if r[0].isdigit()]
    m = re.match(r"GTA Online Rank (\d+)$", h or "")
    if m and "li" in x: unl.setdefault(int(m.group(1)), []).append(x["li"])
if rp:
    rows = [[e(r[0]), e(f"{int(r[1]):,}"), e(r[2])] + ([e("; ".join(unl.get(int(r[0]), [])[:6]))] if unl else []) for r in rp]
    body = sec(1, "How ranking works", "<p>You earn RP (Reputation Points) for almost everything in GTA Online: missions, races, heists, stunts, even driving against traffic. Each rank needs more RP than the last. Ranking up unlocks new weapons, clothes, tattoos, vehicle mods and jobs.</p>")
    body += sec(2, f"RP needed for ranks 1–{rp[-1][0]}", tbl(["Rank", "Total RP", "RP from previous"] + (["Unlocks (first few)"] if unl else []), rows))
    body += MORE + credit("Rank")
    write("gta-online-ranks", "GTA Online Rank RP Chart (1–120) & Unlocks", "How much RP every GTA Online rank needs, from rank 1 to 120, and what each rank unlocks – weapons, clothes, mods and jobs.",
          "GTA ONLINE · RANKS", "GTA Online Ranks & RP", f"⭐ RP for ranks 1–{rp[-1][0]} and what each one unlocks.", body, [("Home", ""), ("GTA Online", "gta-online"), ("Ranks", "gta-online-ranks")])
    print("ranks", len(rp), len(unl))

# ---------- adversary modes
d = load("o_adv"); groups = []
for x in d:
    if "table" in x and len(x["table"]) > 2 and x["table"][1][:2] == ["Image", "Name"]:
        upd = re.sub(r"^(Added in|Relased during|Released during)\s+(the\s+)?", "", x["table"][0][0]).strip()
        groups.append((upd, [(r[1], r[2]) for r in x["table"][2:] if len(r) > 2 and r[1]]))
if groups:
    body, i = "", 1
    for upd, ms in groups:
        body += sec(i, e(upd), tbl(["Mode", "How it plays"], [[f"<b>{e(n)}</b>", e(clip(dsc, 400))] for n, dsc in ms])); i += 1
    tot = sum(len(m) for _, m in groups)
    body += MORE + credit("Adversary_Modes")
    write("gta-online-adversary-modes", f"All GTA Online Adversary Modes ({tot}) by Update", clip(f"Every GTA Online Adversary Mode ({tot}) – Come Out to Play, Slasher, Sumo, Turf Wars, Hunting Pack and more – with how each one plays, grouped by update."),
          "GTA ONLINE · ADVERSARY MODES", "GTA Online Adversary Modes", f"🎯 {tot} modes from {len(groups)} updates.", body, [("Home", ""), ("GTA Online", "gta-online"), ("Adversary modes", "gta-online-adversary-modes")])
    print("adversary", tot)

# ---------- hub
cards = "".join(f'<a class="glass tilt area" href="{s}"><div class="pop"><div class="ic">{ic}</div><h3>{t}</h3><p>{p}</p></div></a>' for s, ic, t, p in (
    ("gta-online-heists", "💰", "Heists", "Payouts, setup costs and bonus challenges"), ("gta-online-contact-missions", "📱", "Contact missions", "Every job by contact, with rewards"),
    ("gta-online-ranks", "⭐", "Ranks &amp; RP", "RP needed for every rank and unlocks"), ("gta-online-adversary-modes", "🎯", "Adversary modes", "Every mode by update")) if s in pages)
body = sec(1, "What is GTA Online?", "<p>GTA Online is the multiplayer world of GTA 5: build a criminal empire in Los Santos with friends, run businesses, pull heists and race. It launched in 2013 and keeps getting free updates. Story-mode cheats do not work here.</p>")
body += sec(2, "Guides", f'<div class="grid">{cards}</div>') + MORE + credit("GTA_Online")
write("gta-online", "GTA Online Guide: Heists, Missions, Ranks & Modes", "GTA Online guides: every heist with payouts, all contact missions, the full rank RP chart and every adversary mode.",
      "GTA ONLINE", "GTA Online", "🌐 Heists, contact missions, ranks and modes – all in one place.", body, [("Home", ""), ("GTA Online", "gta-online")])

sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(len(pages), "pages; sitemap", sm.count("<url>"), "urls")
