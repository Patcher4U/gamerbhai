"""Collectible location checklists (GTA 5, San Andreas, Vice City, GTA III) - data only.
  python -I tools/gen_collect.py <folder with sp_v.json ...> gta6-site
Data: GTA Wiki collectible pages (CC BY-SA, credited on every page), saved by the browser with rowspans expanded.
Each page: what it is / how to unlock / reward, then every location as a tick-box table (ticks saved in the visitor's browser).
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = sys.argv[1]; SITE = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "gta6-site"))
BASE = "https://gamerbhai.com/"; TODAY = "2026-11-28"
e = lambda s: html.escape(s, quote=True)
asrc = open(os.path.join(HERE, "gen_articles.py"), encoding="utf-8").read()
A = {}; exec(asrc[asrc.index("HEAD ="):asrc.index("def fmt")], A); HEAD, FOOT = A["HEAD"], A["FOOT"]
sys.path.insert(0, HERE); from wiki_clean import fix
csrc = open(os.path.join(HERE, "gen_completion.py"), encoding="utf-8").read()
JS = re.search(r'JS = \((.*?)\)\n', csrc, re.S).group(1); JS = eval("(" + JS + ")").replace(".chk input", ".chk input")
def clip(t, n=158): return t if len(t) <= n else t[:t.rfind(' ', 0, n - 1)].rstrip(' ,.:;') + '…'
def sec(n, h, inner): return f'  <section class="reveal"><h2><span class="n">{n:02d}</span>{h}</h2><div class="glass">{inner}</div></section>\n'

# key, file, game, game slug, emoji, collectible, wiki page
C = [("gta-5-spaceship-parts", "sp_v", "GTA 5", "gta-5", "🛸", "Spaceship Parts", "Spaceship_Parts"),
     ("gta-5-letter-scraps", "ls_v", "GTA 5", "gta-5", "✉️", "Letter Scraps", "Letter_Scraps"),
     ("gta-5-stunt-jumps", "sj_v", "GTA 5", "gta-5", "🏍️", "Stunt Jumps", "Stunt_Jumps_in_GTA_V"),
     ("gta-san-andreas-oysters", "sp_sa", "GTA San Andreas", "gta-san-andreas", "🦪", "Oysters", "Oysters"),
     ("gta-san-andreas-horseshoes", "hs_sa", "GTA San Andreas", "gta-san-andreas", "🧲", "Horseshoes", "Horseshoes"),
     ("gta-san-andreas-snapshots", "sn_sa", "GTA San Andreas", "gta-san-andreas", "📷", "Snapshots", "Snapshots"),
     ("gta-san-andreas-tags", "tg_sa", "GTA San Andreas", "gta-san-andreas", "🎨", "Gang Tags", "Tags"),
     ("gta-vice-city-hidden-packages", "pk_vc", "GTA Vice City", "gta-vice-city", "📦", "Hidden Packages", "Hidden_Packages_in_GTA_Vice_City"),
     ("gta-3-hidden-packages", "pk_3", "GTA 3", "gta-3", "📦", "Hidden Packages", "Hidden_Packages_in_GTA_III"),
     ("gta-liberty-city-stories-hidden-packages", "pk_lcs", "GTA Liberty City Stories", "gta-liberty-city-stories", "📦", "Hidden Packages", "Hidden_Packages_in_GTA_Liberty_City_Stories"),
     ("gta-vice-city-stories-red-balloons", "rb_vcs", "GTA Vice City Stories", "gta-vice-city-stories", "🎈", "Red Balloons", "Red_Balloons"),
     ("gta-san-andreas-unique-stunt-jumps", "uj_sa", "GTA San Andreas", "gta-san-andreas", "🏍️", "Unique Stunt Jumps", "Unique_Stunt_Jumps_in_GTA_San_Andreas"),
     ("gta-vice-city-unique-stunt-jumps", "uj_vc", "GTA Vice City", "gta-vice-city", "🏍️", "Unique Stunt Jumps", "Unique_Stunt_Jumps_in_GTA_Vice_City"),
     ("gta-4-unique-stunt-jumps", "sj_4", "GTA 4", "gta-4", "🏍️", "Unique Stunt Jumps", "Unique_Stunt_Jumps_in_GTA_IV"),
     ("gta-vice-city-rampages", "rp_vc", "GTA Vice City", "gta-vice-city", "💀", "Rampages", "Rampages_in_GTA_Vice_City"),
     ("gta-3-rampages", "rp_3", "GTA 3", "gta-3", "💀", "Rampages", "Rampages_in_GTA_III"),
     ("gta-online-signal-jammers", "oc_jam", "GTA Online", "gta-online", "📡", "Signal Jammers", "Signal_Jammers"),
     ("gta-online-playing-cards", "oc_cards", "GTA Online", "gta-online", "🃏", "Playing Cards", "Playing_Cards"),
     ("gta-online-action-figures", "oc_fig", "GTA Online", "gta-online", "🧸", "Action Figures", "Action_Figures"),
     ("gta-online-ld-organics", "oc_ld", "GTA Online", "gta-online", "🌿", "LD Organics Product", "LD_Organics_Product"),
     ("gta-online-shipwrecks", "oc_wreck", "GTA Online", "gta-online", "⚓", "Shipwrecks", "Shipwrecks"),
     ("gta-online-media-sticks", "oc_media", "GTA Online", "gta-online", "💾", "Media Sticks", "Media_Sticks"),
     ("gta-online-junk-energy-skydives", "oc_sky", "GTA Online", "gta-online", "🪂", "Junk Energy Skydives", "Junk_Energy_Skydives"),
     ("gta-liberty-city-stories-rampages", "rp_lcs", "GTA Liberty City Stories", "gta-liberty-city-stories", "💀", "Rampages", "Rampages_in_GTA_Liberty_City_Stories")]
SKIPH = ("Contents", "Version Changes", "Interactive Map", "Beta Content", "Complete Letter", "Exploits", "Fail Safe")
pages, made = [], []
for slug, fn, game, gk, emo, what, wiki in C:
    p = os.path.join(SRC, fn + ".json")
    if not os.path.exists(p): continue
    raw = json.loads(fix(open(p, encoding="utf-8").read()))
    intro, secs, cur, table = [], [], None, None
    for x in raw:
        if "h" in x:
            cur = None if x["h"] in SKIPH or x["h"] == "Locations" or x["h"] in ("Stunt Jump Locations", "List of Stunt Jumps", "Jumps") else {"h": x["h"], "t": []}
            if cur: secs.append(cur)
            continue
        if "table" in x:
            if table is None and len(x["table"]) > 10: table = x["table"]
            continue
        t = x.get("p") or x.get("li")
        if not t or re.match(r"^\d+(\.\d+)* ", t) or "map of stunt jumps" in t: continue
        if cur is None and not secs: intro.append(t)
        elif cur is not None: cur["t"].append(("li" if "li" in x else "p", t))
    if not table: print("no table", slug); continue
    hd = [h.lower() for h in table[0]]
    def ci(*names):
        for i, h in enumerate(hd):
            if any(h.startswith(n) for n in names): return i
        return None
    i_n, i_d, i_a, i_l = ci("ref number", "#", "jump #", "map number"), ci("location description", "description", "jump description", "location/info", "location"), ci("area"), ci("landing")
    i_w, i_o, i_m = ci("weapon"), ci("objective"), ci("mix")
    for r in table:
        for j, c in enumerate(r): r[j] = re.sub(r"\s*/\s*$", "", re.sub(r"\s*(Original|Alternative) location:\s*", lambda m: (" / " if m.group(1) == "Alternative" else "") + m.group(1) + ": ", c).strip()).strip(" /")
    rows = [r for r in table[1:] if i_d is not None and i_d < len(r) and r[i_d]]
    extra = [("Area", i_a), ("To pass", i_l), ("Weapon", i_w), ("Objective", i_o), ("Mix", i_m)]
    extra = [(n, i) for n, i in extra if i is not None]
    th = "<thead><tr><th>✔</th><th>#</th><th>Where</th>" + "".join(f"<th>{n}</th>" for n, _ in extra) + "</tr></thead>"
    trs = "".join(f'<tr><td class="chk"><input type="checkbox" aria-label="found {j + 1}"></td><td>{e(r[i_n]) if i_n is not None and r[i_n] else j + 1}</td><td>{e(r[i_d])}</td>'
                  + "".join(f"<td>{e(r[i]) if i < len(r) else ''}</td>" for _, i in extra) + "</tr>" for j, r in enumerate(rows))
    N = len(rows)
    body, k = f'  <div class="warnbox">✅ Tick each one as you find it – ticks are saved in this browser only. <b id="chkc"></b></div>\n', 1
    for s in secs:
        if not s["t"]: continue
        inner = "".join(f"<p>{e(t)}</p>" if kind == "p" else f"<ul><li>{e(t)}</li></ul>" for kind, t in s["t"]).replace("</ul><ul>", "")
        body += sec(k, e(s["h"]), inner); k += 1
    body += sec(k, f"All {N} {e(what.lower())} locations", f'<div class="gtable"><table class="cheats cw">{th}<tbody>{trs}</tbody></table></div>'); k += 1
    sib = " · ".join(f'<a href="{o[0]}">{e(o[5])}</a>' for o in C if o[3] == gk and o[0] != slug and os.path.exists(os.path.join(SRC, o[1] + ".json")))
    hub_links = (f'<a href="{gk}-100-percent-completion">100% checklist</a> · <a href="{gk}-missions">missions</a> · <a href="{gk}-cheats">cheats</a>' if gk != "gta-online"
                 else '<a href="gta-online">GTA Online hub</a> · <a href="gta-online-heists">heists</a>')
    hub_url, hub_name = (f"{gk}-100-percent-completion", f"{game} 100%") if gk != "gta-online" else ("gta-online", "GTA Online")
    body += (f'  <p class="note">More {e(game)}: ' + (sib + " · " if sib else "") + hub_links + '</p>\n'
             f'  <p class="note">Locations from the <a href="https://gta.fandom.com/wiki/{wiki}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). Unofficial fan guide, not affiliated with Rockstar Games.</p>\n')
    reward = next((t for s in secs if s["h"] == "Rewards" for _, t in s["t"]), "")
    title = f"All {N} {game} {what} Locations (Checklist)"
    desc = clip(f"Where to find all {N} {what.lower()} in {game}, with a tick-box checklist. " + (reward or (intro[0] if intro else "")))
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
          {"@type": "ListItem", "position": 2, "name": hub_name, "item": BASE + hub_url}, {"@type": "ListItem", "position": 3, "name": what, "item": BASE + slug}]}]
    doc = (HEAD.format(lang="en", stitle=e(title), title=e(title), desc=e(desc), url=BASE + slug, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
           + f'<header class="wrap phero reveal">\n  <div class="kicker">{e(game.upper())} · COLLECTIBLES</div>\n  <h1><span class="g">{e(game)} {e(what)}</span></h1>\n  <p class="lead">{emo} All {N} locations, one line each. ' + e(clip(intro[0], 140) if intro else "") + '</p>\n</header>\n<main class="wrap article">\n'
           + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + JS.replace("'.chk input'", "'.chk input, td.chk input'") + FOOT)
    open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(doc)
    pages.append(slug); made.append((gk, slug, what)); print(slug, N)

json.dump(made, open(os.path.join(HERE, "collectibles.json"), "w", encoding="utf-8"))  # read by gen_completion.py for links
sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(len(pages), "pages; sitemap", sm.count("<url>"), "urls")
