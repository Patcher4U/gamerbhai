"""Build one page per story mission and per confirmed cheat (no AI, data only).
  python -I tools/gen_pages.py gta6-site
Mission data comes from gen_walk.py (CH, VIDEOS, FIRST, SIDE...), cheats from the table in guides.html.
Re-runs gen_walk.py first, then links every mission/cheat name to its page and updates sitemap + indexnow.
Only missions with a video or a written tip get a page (no empty pages).
"""
import html, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SITE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "gta6-site"))
BASE = "https://gamerbhai.com/"; TODAY = "2026-11-24"
e = lambda s: html.escape(s, quote=True)
def slugify(s): return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower().replace("'", "").replace("&", "and"))).strip("-")

# --- data from gen_walk.py (exec only the data part, not the page writer) and gen_articles.py (HEAD/FOOT)
src = open(os.path.join(ROOT, "gen_walk.py"), encoding="utf-8").read()
W = {"__builtins__": __builtins__}; exec(src.split("\ntotal =")[0], W)
CH, VIDEOS, FIRST, PHONE, AGE, SIDE, PLAYLIST = (W[k] for k in ("CH", "VIDEOS", "FIRST", "PHONE", "AGE", "SIDE", "PLAYLIST"))
asrc = open(os.path.join(HERE, "gen_articles.py"), encoding="utf-8").read()
A = {}; exec(asrc[asrc.index("HEAD ="):asrc.index("def fmt")], A); HEAD, FOOT = A["HEAD"], A["FOOT"]
subprocess.run([sys.executable, "-I", os.path.join(ROOT, "gen_walk.py"), SITE], check=True)
unesc = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s))

def page(title, desc, url, kicker, h1, lead, body, ld):
    return (HEAD.format(lang="en", stitle=e(title + " | GamerBhai" if len(title) <= 48 else title), title=e(title), desc=e(desc), url=url, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
            + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
            + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)
def chslug(c): return f"gta-6-{slugify(c['n'])}-walkthrough"
def clip(t, n=158):
    return t if len(t) <= n else t[:t.rfind(' ', 0, n - 1)].rstrip(' ,.:') + '…'
def sec(n, h, inner): return f'  <section class="reveal"><h2><span class="n">{n}</span>{h}</h2><div class="glass">{inner}</div></section>\n'
def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement":
            [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}

# ---------------- missions
seq = []  # (chapter_index, number_in_chapter, name)
for ci, c in enumerate(CH):
    for k, m in enumerate(c["ms"], 1): seq.append((ci, k, m))
made = {}  # name -> slug
for ci, k, m in seq:
    if m in PHONE or m in made or not (VIDEOS.get(m) or FIRST.get(m)): continue
    made[m] = f"gta-6-{slugify(m)}-mission"
def link(m): return f'<a href="{made[m]}">{e(m)}</a>' if m in made else e(m)

for idx, (ci, k, m) in enumerate(seq):
    if made.get(m) is None or any(s[2] == m for s in seq[:idx]): continue  # first occurrence builds the page
    c = CH[ci]; chap = unesc(c["t"]); slug = made[m]; url = BASE + slug
    where = [(CH[a]["n"], b) for a, b, n in seq if n == m]
    prev = seq[idx - 1][2] if idx else None; nxt = seq[idx + 1][2] if idx + 1 < len(seq) else None
    vid = VIDEOS.get(m)
    title = next(t for t in (f"GTA 6 {m} Mission Walkthrough", f"GTA 6 {m} Walkthrough", f"{m} - GTA 6 Walkthrough") if len(t) <= 48 or t.startswith(m))  # + " | GamerBhai" stays under ~60 chars
    desc = clip(f"GTA 6 {m} walkthrough" + (" with full video" if vid else "") + f": {c['n']} mission {k} of {len(c['ms'])} in {unesc(c['area'])}. Previous and next missions, tips and chapter guide.")
    lead = f"<b>{e(m)}</b> is mission {k} of {len(c['ms'])} in <b>{e(c['n'])}: {c['t']}</b>." + (" Watch the full mission below, then jump to the next one." if vid else "")
    body = ""
    if c["spoil"]: body += '  <div class="warnbox reveal">⚠️ Spoiler warning: this mission is from a later chapter. The video may show story events.</div>\n'
    facts = (f'<ul><li>📖 <b>Chapter:</b> {e(c["n"])} – {c["t"]}</li><li>📍 <b>Area:</b> {c["area"]}</li>'
             f'<li>🎮 <b>Playable in this chapter:</b> {c["who"]}</li><li>🧾 <b>Order:</b> mission {k} of {len(c["ms"])}'
             + (" (appears more than once: " + ", ".join(f"{a} #{b}" for a, b in where) + ")" if len(where) > 1 else "") + '</li></ul>'
             + (f'<p><b>Objective:</b> {e(FIRST[m])}</p>' if FIRST.get(m) else "") + f'<p>{c["intro"]}</p>')
    body += sec("01", "Mission overview", facts)
    if vid:
        btn = (f'<a class="btn primary" href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">▶ Watch on YouTube ↗</a> <span class="note">(age-restricted, opens on YouTube)</span>' if m in AGE
               else f'<button class="btn primary mvid wide" data-yt="{vid}">▶ Play the full {e(m)} walkthrough</button>')
        body += sec("02", "Video walkthrough", f'<p>Full gameplay of the mission from start to finish, recorded by a YouTube creator.</p><div class="vbar">{btn}</div>')
    nav = '<div class="grid">'
    if prev: nav += f'<a class="glass tilt area" href="{made.get(prev, "walkthrough")}"><div class="pop"><div class="ic">⬅️</div><h3>Previous: {e(prev)}</h3></div></a>'
    if nxt: nav += f'<a class="glass tilt area" href="{made.get(nxt, "walkthrough")}"><div class="pop"><div class="ic">➡️</div><h3>Next: {e(nxt)}</h3></div></a>'
    nav += '<a class="glass tilt area" href="walkthrough"><div class="pop"><div class="ic">📖</div><h3>All missions in order</h3></div></a></div>'
    body += f'  <section class="reveal"><h2><span class="n">03</span>Previous &amp; next mission</h2>{nav}</section>\n'
    others = [n for a, b, n in seq if a == ci and n != m]
    body += sec("04", f"Other <a href=\"{chslug(c)}\">{e(c['n'])}</a> missions", "<p>" + " · ".join(link(n) for n in dict.fromkeys(others)) + "</p>")
    side = [s for s in SIDE if s[2] == c["n"]]
    if side: body += sec("05", "Side missions in this chapter", "".join(f"<p>{a} <b>{b}</b>: {d}</p>" for a, b, cc, d in side))
    body += sec("★", "Helpful guides", '<p><a href="guides#money">💰 Make money fast</a> · <a href="guides#cheats">🎮 All cheat codes</a> · <a href="map">📍 100% tracker</a> · <a href="gta-6-hidden-controls">🕹️ Hidden controls</a></p><p class="note">Mission names and order are matched across several player guides. Videos belong to their YouTube creators. Unofficial fan guide, not affiliated with Rockstar Games.</p>')
    ld = [crumbs([("Home", ""), ("Walkthrough", "walkthrough"), (m, slug)]),
          {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "datePublished": TODAY, "dateModified": TODAY,
           "image": "https://gamerbhai.com/img/og.jpg", "author": {"@type": "Organization", "name": "GamerBhai"}, "mainEntityOfPage": url}]
    open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(
        page(title, desc, url, f"GTA 6 WALKTHROUGH · {e(c['n'].upper())}", f"GTA 6 {m} Walkthrough", lead, body, ld))

# link mission names on the walkthrough page
wp = os.path.join(SITE, "walkthrough.html"); w = open(wp, encoding="utf-8").read()
for m, s in made.items(): w = w.replace(f"<b>{e(m)}</b>", f'<b><a href="{s}">{e(m)}</a></b>')
open(wp, "w", encoding="utf-8").write(w)

# ---------------- chapter hub pages
chapters = []
for ci, c in enumerate(CH):
    slug = chslug(c); url = BASE + slug; chapters.append(slug); chap = unesc(c["t"]); ms = list(dict.fromkeys(c["ms"]))
    title = f"GTA 6 {c['n']} Walkthrough: All {len(c['ms'])} Missions" if len(c['ms']) > 1 else f"GTA 6 {c['n']} Walkthrough"
    desc = clip(f"GTA 6 {c['n']} walkthrough: every mission in order with video guides, set in {unesc(c['area'])}. Who you play, missable side missions and tips.")
    rows = []
    for k, m in enumerate(c["ms"], 1):
        tip = FIRST.get(m)
        tag = " <span class=\"note\">(phone call)</span>" if m in PHONE else (" ▶" if VIDEOS.get(m) else "")
        rows.append(f'<li><span class="mn">{k:02d}</span><div><b>{link(m)}</b>{tag}' + (f'<p>{e(tip)}</p>' if tip else '') + '</div></li>')
    body = ""
    if c["spoil"]: body += '  <div class="warnbox reveal">⚠️ Spoiler warning: mission names in this chapter may hint at story events.</div>\n'
    body += sec("01", "Chapter overview", f'<ul><li>📍 <b>Area:</b> {c["area"]}</li><li>🎮 <b>Playable:</b> {c["who"]}</li><li>🧾 <b>Missions:</b> {len(c["ms"])}</li></ul><p>{c["intro"]}</p>')
    body += sec("02", f"All {e(c['n'])} missions in order", f'<ol class="mlist">{"".join(rows)}</ol><p class="note">▶ = full video walkthrough on the mission page.</p>')
    side = [x for x in SIDE if x[2] == c["n"]]
    if side: body += sec("03", "Side missions &amp; missables", "".join(f"<p>{a} <b>{b}</b>: {d}</p>" for a, b, cc, d in side))
    nav = '<div class="grid">'
    if ci: nav += f'<a class="glass tilt area" href="{chslug(CH[ci-1])}"><div class="pop"><div class="ic">⬅️</div><h3>{e(CH[ci-1]["n"])}</h3></div></a>'
    if ci + 1 < len(CH): nav += f'<a class="glass tilt area" href="{chslug(CH[ci+1])}"><div class="pop"><div class="ic">➡️</div><h3>{e(CH[ci+1]["n"])}</h3></div></a>'
    nav += '<a class="glass tilt area" href="walkthrough"><div class="pop"><div class="ic">📖</div><h3>Full walkthrough</h3></div></a></div>'
    body += f'  <section class="reveal"><h2><span class="n">04</span>Other chapters</h2>{nav}</section>\n'
    body += sec("★", "Helpful guides", '<p><a href="guides#money">💰 Money guide</a> · <a href="gta-6-point-of-no-return-tourist-trap">⚠️ Point of no return</a> · <a href="guides#cheats">🎮 Cheats</a> · <a href="map">📍 100% tracker</a> · <a href="gta-6-saare-missions-urdu">🇵🇰 Urdu</a></p><p class="note">Mission names and order are matched across several player guides. Videos belong to their YouTube creators. Unofficial fan guide, not affiliated with Rockstar Games.</p>')
    ld = [crumbs([("Home", ""), ("Walkthrough", "walkthrough"), (c["n"], slug)]),
          {"@context": "https://schema.org", "@type": "ItemList", "name": title, "numberOfItems": len(c["ms"]),
           "itemListElement": [{"@type": "ListItem", "position": k, "name": m, **({"url": BASE + made[m]} if m in made else {})} for k, m in enumerate(c["ms"], 1)]}]
    open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(
        page(title, desc, url, f"GTA 6 WALKTHROUGH · {e(c['n'].upper())}", f"GTA 6 {c['n']}: {chap}", f"{len(c['ms'])} mission{'s' if len(c['ms']) > 1 else ''} · {c['area']} · {c['who']}", body, ld))
# link chapter pages from the walkthrough page (the "N missions" chip of each chapter)
w = open(wp, encoding="utf-8").read()
for c in CH:
    n = len(c["ms"]); chip = f'<span>🧾 {n} mission{"s" if n > 1 else ""}</span>'
    w = w.replace(chip, f'<span>🧾 <a href="{chslug(c)}">{n} mission{"s" if n > 1 else ""} - chapter guide</a></span>', 1)
open(wp, "w", encoding="utf-8").write(w)

# ---------------- character pages (tools/gen_chars.py, official self-hosted images, ad-free)
sys.path.insert(0, HERE)
import gen_chars
char_slugs = gen_chars.build(SITE, page, sec, crumbs, e, made, BASE)

# ---------------- cheats
gp = os.path.join(SITE, "guides.html"); g = open(gp, encoding="utf-8").read()
rows = re.findall(r'<tr><td>(.*?)</td><td class="code">(.*?)</td><td>(.*?)</td></tr>', g)
WHAT = {"$250,000": "Adds $250,000 to your cash. It doesn't carry over, because saving is blocked while a cheat is on.",
        "Unlimited Focus": "Your Focus meter never runs out.", "Body Armor": "Gives you full body armor.",
        "Cycle Weather": "Changes the weather each time you enter it.", "Raise Heat Level": "Raises your wanted (heat) level.",
        "Max Ammo": "Fills ammo for your weapons.", "Infinite Ammo": "Your ammo never runs out.", "No Reload": "Fire without reloading.",
        "Spawn Maibatsu Boomazoom": "Spawns a Maibatsu Boomazoom next to you.", "Spawn MTL Pumper (fire truck)": "Spawns an MTL Pumper fire truck next to you.",
        "Spawn HVY Bulldozer": "Spawns an HVY Bulldozer next to you.", "Cataclysm filter": "Puts the Cataclysm look filter over the screen.",
        "Dollhouse filter": "Puts the Dollhouse look filter over the screen.", "Faded Glory filter": "Puts the Faded Glory look filter over the screen."}
GROUP = lambda n: ("Vehicle" if "Spawn" in n else "Screen filter" if "filter" in n else "Weapon" if any(x in n for x in ("Ammo", "Reload"))
                   else "Player" if any(x in n for x in ("$", "Focus", "Armor")) else "World & chaos")
cheats = []
for name_cell, code, unlock in rows:
    emoji, name = name_cell.split(" ", 1); cheats.append(dict(emoji=emoji, name=unesc(name), code=code, unlock=unesc(unlock)))
for ch in cheats: ch["slug"] = "gta-6-" + slugify(ch["name"].replace("$250,000", "money 250000").replace(" (fire truck)", "")) + "-cheat"
for ch in cheats:
    n = ch["name"]; url = BASE + ch["slug"]; grp = GROUP(n)
    sn = n.replace(" (fire truck)", "")
    title = next(t for t in (f"GTA 6 {sn} Cheat Code (PS5 & Xbox)", f"GTA 6 {sn} Cheat Code") if len(t) <= 48 or t.endswith("Code"))
    desc = clip(f"GTA 6 {n} cheat code for PS5 and Xbox: {ch['code']}. Unlock: {ch['unlock']}. How to enter it, plus related cheats.")
    body = sec("01", "The code", f'<p class="code" style="font-size:1.6em;letter-spacing:.08em">{ch["code"]}</p><p>{e(WHAT.get(n, "A chaos cheat that changes how Leonida reacts. Try it on a fresh save first."))}</p>')
    body += sec("02", "How to unlock it", f'<p><b>{e(ch["unlock"])}.</b> Every GTA 6 cheat is locked until you finish its goal; you can check progress under <b>Progress → Cheats</b>.</p><p>See every goal in our <a href="how-to-unlock-gta-6-cheats">cheat unlock guide</a> and track them on the <a href="map">100% tracker</a>.</p>')
    body += sec("03", "How to enter it", '<ol><li>Press <b>Up</b> on the D-pad to pull out the phone.</li><li>Hold <b>L1 + R1</b> (PS5) or <b>LB + RB</b> (Xbox Series X|S).</li><li>Keep holding and type the D-pad code above.</li></ol><div class="warnbox">⚠️ While a cheat is on, <b>trophies/achievements are off and you can\'t save</b>. Save first, then reload your clean save.</div>')
    rel = [c for c in cheats if c is not ch and GROUP(c["name"]) == grp] or [c for c in cheats if c is not ch][:4]
    body += f'  <section class="reveal"><h2><span class="n">04</span>More {e(grp.lower())} cheats</h2><div class="grid">' + "".join(
        f'<a class="glass tilt area" href="{c["slug"]}"><div class="pop"><div class="ic">{c["emoji"]}</div><h3>{e(c["name"])}</h3><p class="code">{c["code"]}</p></div></a>' for c in rel[:6]) + '</div><p class="note"><a href="guides#cheats">All 17 confirmed cheats →</a></p></section>\n'
    body += sec("★", "Sources", '<p class="note">Codes are only listed when several guides give the identical sequence (Vice, GTABase, KeenGamer, GamerTweak, Beebom). Unofficial fan guide, not affiliated with Rockstar Games.</p>')
    ld = [crumbs([("Home", ""), ("Cheats", "guides#cheats"), (n, ch["slug"])]),
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": f"What is the {n} cheat code in GTA 6?", "acceptedAnswer": {"@type": "Answer", "text": f"Hold L1+R1 (PS5) or LB+RB (Xbox) with the phone out and enter {ch['code']}."}},
              {"@type": "Question", "name": f"How do you unlock the {n} cheat in GTA 6?", "acceptedAnswer": {"@type": "Answer", "text": ch["unlock"] + "."}}]}]
    open(os.path.join(SITE, ch["slug"] + ".html"), "w", encoding="utf-8").write(
        page(title, desc, url, f"GTA 6 CHEATS · {e(grp.upper())}", f"GTA 6 {n} Cheat", f'{ch["emoji"]} Code: <b class="code">{ch["code"]}</b> · Unlock: {e(ch["unlock"])}', body, ld))
    # link the name in the guides table (idempotent)
    cell = f'<tr><td>{ch["emoji"]} {e(n) if "$" not in n else n}</td>'
    g = g.replace(cell, f'<tr><td>{ch["emoji"]} <a href="{ch["slug"]}">{e(n) if "$" not in n else n}</a></td>')
open(gp, "w", encoding="utf-8").write(g)

# ---------------- sitemap + indexnow
sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in list(made.values()) + [c["slug"] for c in cheats] + chapters + char_slugs:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(f"{len(made)} mission pages, {len(chapters)} chapter pages, {len(cheats)} cheat pages; sitemap {sm.count('<url>')} urls")
