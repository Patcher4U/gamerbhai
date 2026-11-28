"""100% completion checklist pages for the older GTA games - data only.
  python -I tools/gen_completion.py <folder with c_sa.txt c_vc.txt ...> gta6-site
Data: GTA Wiki "100% Completion in ..." pages (CC BY-SA, credited on every page), saved as text by the browser.
Builds <game>-100-percent-completion pages with tick boxes (saved in the visitor's browser), updates sitemap + indexnow.
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
GAMES = [("gta-5", "c_v", "GTA 5", "🌴"), ("gta-san-andreas", "c_sa", "GTA San Andreas", "🏜️"), ("gta-vice-city", "c_vc", "GTA Vice City", "🌆"),
         ("gta-3", "c_3", "GTA 3", "🌃"), ("gta-4", "c_4", "GTA 4", "🗽"), ("gta-liberty-city-stories", "c_lcs", "GTA Liberty City Stories", "🎰"),
         ("gta-vice-city-stories", "c_vcs", "GTA Vice City Stories", "🌴"), ("gta-chinatown-wars", "c_ctw", "GTA Chinatown Wars", "🐉")]
STORY = ("Main missions", "Story missions", "Story Missions")
RESUME = ("Side missions", "Side Missions/Challenges", "Asset missions", "Assets missions")
STOP = ("Video", "Video Walkthrough", "Notes", "Trivia", "Navigation", "Oversights", "See Also")
HEADERS = {"Mission", "Race", "Car", "School", "Collectible", "Property", "Gym", "Event", "Challenge", "Vehicle", "Task", "Name"}
ICON = re.compile(r"\b(?:Radar|Blips|HUD|Icon)[-\w]*-\S*\s*|\S+-GTA(?:SA|VC|III|LCS|VCS|CW|IV|V)\S*\s*")
JS = ("<script>(function(){var k='gb-100-'+location.pathname,s={};try{s=JSON.parse(localStorage.getItem(k)||'{}')}catch(x){}"
      "var b=document.querySelectorAll('.chk input'),c=document.getElementById('chkc');function u(){var n=0;b.forEach(function(i){if(i.checked)n++});if(c)c.textContent=n+' / '+b.length+' ticked'}"
      "b.forEach(function(i,j){i.checked=!!s[j];i.onchange=function(){s[j]=i.checked;try{localStorage.setItem(k,JSON.stringify(s))}catch(x){}u()}});u()})();</script>\n")

def clean(t): return re.sub(r"\s+", " ", ICON.sub("", t)).strip(" |")

pages = []
for gk, fn, name, emoji in GAMES:
    p = os.path.join(SRC, fn + ".txt")
    if not os.path.exists(p): continue
    lines = fix(open(p, encoding="utf-8").read()).split("\n")
    mslug = {m["name"].lower(): f"{gk}-{slugify(m['name'])}-mission" for m in MIS.get(gk, [])}
    def link(t):
        s = mslug.get(t.lower())
        return f'<a href="{s}">{e(t)}</a>' if s and os.path.exists(os.path.join(SITE, s + ".html")) else e(t)
    secs, cur, intro, skip, n_items = [], None, [], False, 0
    for l in lines:
        if l.startswith("### "):
            h = l[4:].strip()
            if h.startswith(STOP): break
            if h == "Platforms Checklists": skip = True; continue
            if h in STORY:
                skip = True; cur = {"h": "Story missions", "items": [("story", "")]}; secs.append(cur); continue
            if skip and h not in RESUME and not (h in ("Rewards", "Non-Required Tasks") and gk == "gta-5"): continue
            skip = False
            if h in ("Side missions",) and "Assets missions" in "".join(lines): continue
            cur = {"h": h, "items": []}; secs.append(cur); continue
        if skip or not l.strip(): continue
        if l.startswith("P: "):
            t = clean(l[3:])
            if cur is None: intro.append(t)
            elif t: cur["items"].append(("p", t))
            continue
        if cur is None: cur = {"h": "Required tasks", "items": []}; secs.append(cur)
        if l.startswith("- "):
            t = clean(l[2:])
            if t: cur["items"].append(("li", t))
            continue
        if l.startswith("TH|"): continue
        cells = [clean(c) for c in l.split("|")]; cells = [c for c in cells if c]
        if not cells: continue
        if len(cells) == 1:
            if cells[0] in HEADERS: continue
            cur["items"].append(("trow", cells[0], bool(ICON.search(l))))
        else:
            cur["items"].append(("row", cells))
    for s_ in secs:  # in icon tables, rows without an icon are group labels
        it, res, j = s_["items"], [], 0
        while j < len(it):
            if it[j][0] != "trow": res.append(it[j]); j += 1; continue
            run = []
            while j < len(it) and it[j][0] == "trow": run.append(it[j]); j += 1
            icons = any(x[2] for x in run)
            res += [("li", x[1] + (":" if icons and not x[2] else "")) for x in run]
        s_["items"] = res
    # merge headings that repeat (e.g. "Collectibles" twice) and drop empty sections
    out = []
    for s in secs:
        if out and out[-1]["h"] == s["h"]: out[-1]["items"] += s["items"]
        elif s["items"]: out.append(s)
    body, k = "", 1
    for s in out:
        ul, rows = [], []
        parts = []
        for kind, v in s["items"]:
            if kind != "li" and ul: parts.append('<ul class="chk">' + "".join(ul) + "</ul>"); ul = []
            if kind != "row" and rows: parts.append('<div class="gtable"><table class="cheats cw"><tbody>' + "".join(rows) + "</tbody></table></div>"); rows = []
            if kind == "story":
                parts.append(f'<ul class="chk"><li><label><input type="checkbox"> Finish every story mission – see the <a href="{gk}-missions">full {e(name)} mission list</a> (one page per mission)</label></li></ul>'); n_items += 1
            elif kind == "p": parts.append(f"<p>{e(v)}</p>")
            elif kind == "li":
                if v.endswith(":"): ul.append(f"<li class=\"grp\"><b>{e(v[:-1])}</b></li>")
                else: ul.append(f'<li><label><input type="checkbox"> {link(v)}</label></li>'); n_items += 1
            else:
                rows.append("<tr>" + "".join(f"<td>{link(c) if j == 0 else e(c)}</td>" for j, c in enumerate(v)) + "</tr>")
        if ul: parts.append('<ul class="chk">' + "".join(ul) + "</ul>")
        if rows: parts.append('<div class="gtable"><table class="cheats cw"><tbody>' + "".join(rows) + "</tbody></table></div>")
        body += f'  <section class="reveal"><h2><span class="n">{k:02d}</span>{e(s["h"])}</h2><div class="glass">{"".join(parts)}</div></section>\n'; k += 1
    slug = f"{gk}-100-percent-completion"
    wiki = "https://gta.fandom.com/wiki/100%25_Completion_in_" + {"gta-5": "GTA_V", "gta-san-andreas": "GTA_San_Andreas", "gta-vice-city": "GTA_Vice_City", "gta-3": "GTA_III", "gta-4": "GTA_IV",
        "gta-liberty-city-stories": "GTA_Liberty_City_Stories", "gta-vice-city-stories": "GTA_Vice_City_Stories", "gta-chinatown-wars": "GTA_Chinatown_Wars"}[gk]
    top = (f'  <div class="warnbox">✅ Tick each task as you finish it – your ticks are saved in this browser only. <b id="chkc"></b></div>\n')
    body = top + body + (f'  <p class="note">More: <a href="{gk}-missions">{e(name)} missions</a> · <a href="{gk}-cheats">{e(name)} cheats</a> (cheats can block achievements/trophies) · ' + ('<a href="gta-5-strangers-and-freaks">Strangers and Freaks missions</a> · <a href="gta-5-random-events">random events</a> · ' if gk == "gta-5" else '') + ('<a href="gta-san-andreas-girlfriends">girlfriends guide</a> · ' if gk == "gta-san-andreas" else '')
             + " · ".join(f'<a href="{o}-100-percent-completion">{e(n2)} 100%</a>' for o, f2, n2, _ in GAMES if o != gk and os.path.exists(os.path.join(SRC, f2 + ".txt")))
             + f'. Checklist from the <a href="{wiki}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). Unofficial fan guide, not affiliated with Rockstar Games.</p>\n')
    lead_txt = intro[0] if intro else f"Everything you need to do for 100% completion in {name}."
    title = f"{name} 100% Completion Checklist (Every Task)"
    desc = lead_txt if len(lead_txt) <= 158 else lead_txt[:lead_txt.rfind(" ", 0, 157)].rstrip(" ,.:;") + "…"
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE}, {"@type": "ListItem", "position": 2, "name": f"{name} missions", "item": BASE + f"{gk}-missions"},
        {"@type": "ListItem", "position": 3, "name": "100% completion", "item": BASE + slug}]}]
    doc = (HEAD.format(lang="en", stitle=e(title), title=e(title), desc=e(desc), url=BASE + slug, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
           + f'<header class="wrap phero reveal">\n  <div class="kicker">{e(name.upper())} · 100% COMPLETION</div>\n  <h1><span class="g">{e(name)} 100% Checklist</span></h1>\n  <p class="lead">{emoji} {e(lead_txt)}</p>\n</header>\n<main class="wrap article">\n'
           + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + JS + FOOT)
    open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(doc)
    pages.append(slug); print(slug, n_items, "tick boxes,", len(out), "sections")

sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(len(pages), "pages; sitemap", sm.count("<url>"), "urls")
