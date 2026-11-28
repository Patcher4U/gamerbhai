"""GTA 5 Strangers and Freaks pages - data only.
  python -I tools/gen_sf.py <sf_v.json> gta6-site
Data: GTA Wiki "Strangers and Freaks" tables (CC BY-SA, credited on every page), saved by the browser with rowspans expanded.
Builds gta-5-strangers-and-freaks (all) + gta-5-<character>-strangers-and-freaks pages, updates sitemap + indexnow.
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
CREDIT = '<p class="note">Mission data from the <a href="https://gta.fandom.com/wiki/Strangers_and_Freaks" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). Unofficial fan guide, not affiliated with Rockstar Games.</p>'

raw = json.loads(fix(open(SRC, encoding="utf-8").read()))
MIS = json.load(open(os.path.join(HERE, "classic_missions.json"), encoding="utf-8"))["gta-5"]
STORY = {m["name"].lower(): f"gta-5-{slugify(m['name'])}-mission" for m in MIS}

chars, cur = [], None
for x in raw:
    if "h" in x: cur = x["h"]; continue
    t = x["table"]
    if not cur or not t or len(t) < 2: continue
    hd = [c.lower() for c in t[0]]
    def col(r, *names):
        for n in names:
            if n in hd and hd.index(n) < len(r): return r[hd.index(n)]
        return ""
    ms, seen = [], set()
    for r in t[1:]:
        name = col(r, "missions", "rampage")
        if not name: continue
        target = col(r, "target")
        key = name + target
        if key in seen: continue
        seen.add(key)
        if target: name = f"{name}: {target}"
        desc = col(r, "description") or (f"Track down and bring in {target}." if target else (f"Kill the {name} gang members within the time limit." if "rampage" in hd else ""))
        note = col(r, "notes")
        ms.append(dict(name=name, desc=desc, unl=col(r, "unlocked"), loc=col(r, "locations", "location"),
                       req="Yes" if "Required for 100%" in note else ("No" if "Not required" in note else ""), note=re.sub(r"(Not )?[Rr]equired for 100%\.?\s*", "", note).strip()))
    if ms: chars.append(dict(name=cur, slug=f"gta-5-{slugify(cur)}-strangers-and-freaks", ms=ms))

def unlock(u):  # link story missions named in "After X"
    out = e(u)
    for nm in sorted({n for n in STORY if n in u.lower()}, key=len, reverse=True):
        if len(nm) < 5 or not os.path.exists(os.path.join(SITE, STORY[nm] + ".html")): continue
        out = re.sub(r"(?i)(?<![\w>])(" + re.escape(e(nm)) + r")(?![\w<])", lambda m: f'<a href="{STORY[nm]}">{m.group(1)}</a>', out, count=1)
    return out

def page(title, desc, url, kicker, h1, lead, body, crumbs):
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(crumbs)]}]
    return (HEAD.format(lang="en", stitle=e(title), title=e(title), desc=e(desc), url=BASE + url, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
            + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
            + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + FOOT)

HUB = "gta-5-strangers-and-freaks"; total = sum(len(c["ms"]) for c in chars); req = sum(m["req"] == "Yes" for c in chars for m in c["ms"])
pages = []
for c in chars:
    body, k = "", 1
    for m in c["ms"]:
        rows = f'<tr><td><b>What to do</b></td><td>{e(m["desc"])}</td></tr>' if m["desc"] else ""
        if m["unl"]: rows += f'<tr><td><b>Unlocked</b></td><td>{unlock(m["unl"])}</td></tr>'
        if m["loc"]: rows += f'<tr><td><b>Where</b></td><td>{e(m["loc"])}</td></tr>'
        if m["req"]: rows += f'<tr><td><b>Counts for 100%</b></td><td>{"✅ Yes" if m["req"] == "Yes" else "No"}</td></tr>'
        if m["note"]: rows += f'<tr><td><b>Note</b></td><td>{e(m["note"])}</td></tr>'
        yt = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(f"GTA 5 {m['name']} mission")
        body += sec(k, e(m["name"]), f'<div class="gtable"><table class="cheats cw"><tbody>{rows}</tbody></table></div><p class="note">▶️ <a href="{yt}" rel="nofollow noopener" target="_blank">Watch “{e(m["name"])}” on YouTube</a></p>'); k += 1
    others = " · ".join(f'<a href="{o["slug"]}">{e(o["name"])}</a>' for o in chars if o is not c)
    body += f'  <p class="note"><a href="{HUB}">All {total} Strangers and Freaks missions →</a> · <a href="gta-5-100-percent-completion">GTA 5 100% checklist</a> · <a href="gta-5-missions">GTA 5 story missions</a> · <a href="gta-5-cheats">GTA 5 cheats</a></p>\n  <p class="note">Other characters: {others}</p>\n  {CREDIT}\n'
    n = len(c["ms"]); r = sum(m["req"] == "Yes" for m in c["ms"])
    title = f"GTA 5 {c['name']} Missions (Strangers and Freaks)"
    desc = clip(f"All {n} GTA 5 {c['name']} Strangers and Freaks mission{'s' if n > 1 else ''}: " + ", ".join(m["name"] for m in c["ms"]) + ". How to unlock, where to go and which count for 100%.")
    lead = f'🌴 {n} mission{"s" if n > 1 else ""}' + (f' · {r} count for 100%' if r else "") + " · how to unlock each one and where to find it."
    open(os.path.join(SITE, c["slug"] + ".html"), "w", encoding="utf-8").write(
        page(title, desc, c["slug"], "GTA 5 · STRANGERS AND FREAKS", f"GTA 5: {c['name']}", lead, body, [("Home", ""), ("Strangers and Freaks", HUB), (c["name"], c["slug"])]))
    pages.append(c["slug"])
# hub
body = sec(1, "How Strangers and Freaks work", f'<p>Strangers and Freaks are side missions given by odd characters you meet around Los Santos and Blaine County. They show up on the map as a <b>?</b> icon in the colour of the character who can start them (blue for Michael, green for Franklin, orange for Trevor). There are {total} listed here; {req} of them count towards <a href="gta-5-100-percent-completion">100% completion</a>.</p>')
k = 2
for c in chars:
    rows = "".join(f'<tr><td>{e(m["name"])}</td><td>{unlock(m["unl"])}</td><td>{"✅" if m["req"] == "Yes" else ""}</td></tr>' for m in c["ms"])
    body += sec(k, f'<a href="{c["slug"]}">{e(c["name"])}</a>', f'<div class="gtable"><table class="cheats cw"><thead><tr><th>Mission</th><th>Unlocked</th><th>100%</th></tr></thead><tbody>{rows}</tbody></table></div><p class="note"><a href="{c["slug"]}">{e(c["name"])} mission guide →</a></p>'); k += 1
body += f'  <p class="note">More: <a href="gta-5-missions">GTA 5 story missions</a> · <a href="gta-5-100-percent-completion">GTA 5 100% checklist</a> · <a href="gta-5-cheats">GTA 5 cheats</a> · <a href="gta-cheats">every GTA game</a></p>\n  {CREDIT}\n'
open(os.path.join(SITE, HUB + ".html"), "w", encoding="utf-8").write(
    page(f"All {total} GTA 5 Strangers and Freaks Missions (Full List)", clip(f"Every GTA 5 Strangers and Freaks side mission ({total}) by character, how to unlock each one, and the {req} that count for 100% completion."),
         HUB, "GTA 5 · SIDE MISSIONS", "GTA 5 Strangers and Freaks", f"🌴 {total} side missions from {len(chars)} characters · ✅ = counts for 100%", body, [("Home", ""), ("Strangers and Freaks", HUB)]))
pages.insert(0, HUB)

sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(len(pages), "pages,", total, "missions,", req, "for 100%; sitemap", sm.count("<url>"), "urls")
