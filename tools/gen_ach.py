"""Achievements/trophies checklists (GTA 5, GTA 4, San Andreas) + cheat pages for the 2D games (GTA 1, London 1969, GTA 2) - data only.
  python -I tools/gen_ach.py <folder with ach_*.json ch_*.json> gta6-site
Data: GTA Wiki (CC BY-SA, credited on every page), saved by the browser.
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
JS = eval("(" + re.search(r'JS = \((.*?)\)\n', csrc, re.S).group(1) + ")")
MIS = json.load(open(os.path.join(HERE, "classic_missions.json"), encoding="utf-8"))
def slugify(s): return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower().replace("'", "").replace("&", "and").replace("$", "").replace(",", "").replace(".", ""))).strip("-")
def clip(t, n=158): return t if len(t) <= n else t[:t.rfind(' ', 0, n - 1)].rstrip(' ,.:;') + '…'
def sec(n, h, inner): return f'  <section class="reveal"><h2><span class="n">{n:02d}</span>{h}</h2><div class="glass">{inner}</div></section>\n'
def tbl(head, rows): return '<div class="gtable"><table class="cheats cw"><thead><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
pages = []
def write(slug, title, desc, kicker, h1, lead, body, label, js=""):
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE}, {"@type": "ListItem", "position": 2, "name": label, "item": BASE + slug}]}]
    open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(
        HEAD.format(lang="en", stitle=e(title), title=e(title), desc=e(desc), url=BASE + slug, ogtype="article", ld=json.dumps(ld, ensure_ascii=False), page="article")
        + f'<header class="wrap phero reveal">\n  <div class="kicker">{kicker}</div>\n  <h1><span class="g">{e(h1)}</span></h1>\n  <p class="lead">{lead}</p>\n</header>\n<main class="wrap article">\n'
        + body + '  <div class="ad reveal">Ad</div>\n</main>\n' + js + FOOT)
    pages.append(slug)
load = lambda f: json.loads(fix(open(os.path.join(SRC, f), encoding="utf-8").read())) if os.path.exists(os.path.join(SRC, f)) else None

# ---------- achievements
for gk, k, name, wk in [("gta-5", "v", "GTA 5", "GTA_V"), ("gta-4", "4", "GTA 4", "GTA_IV"), ("gta-san-andreas", "sa", "GTA San Andreas", "GTA_San_Andreas")]:
    d = load(f"ach_{k}.json")
    if not d: continue
    mslug = {m["name"].lower(): f"{gk}-{slugify(m['name'])}-mission" for m in MIS.get(gk, [])}
    def req(t):
        out = e(t)
        for nm in sorted((n for n in mslug if len(n) > 5 and n in t.lower()), key=len, reverse=True)[:2]:
            if os.path.exists(os.path.join(SITE, mslug[nm] + ".html")):
                out = re.sub(r"(?i)(?<![\w>])(" + re.escape(e(nm)) + r")(?![\w<])", lambda m: f'<a href="{mslug[nm]}">{m.group(1)}</a>', out, count=1)
        return out
    h, body, i, total, seen, parent = None, "", 1, 0, set(), None
    for x in d:
        if "h" in x:
            h = x["h"]
            if h in ("Normal Achievements and Trophies", "Hidden Achievements and Trophies"): parent = h.split()[0]
            continue
        t = x["rows"]
        if not t: continue
        hd = [c["t"].lower() for c in t[0]]
        ni = next((j for j, c in enumerate(hd) if "name" in c), None); ri = next((j for j, c in enumerate(hd) if c.startswith("requirement")), None)
        gi = next((j for j, c in enumerate(hd) if c.startswith("gamerscore")), None)
        if ni is None or ri is None: continue
        rows = []
        for r in t[1:]:
            c = [x2["t"] for x2 in r]
            if len(c) <= max(ni, ri) or not c[ni] or c[ni] in seen: continue
            seen.add(c[ni])
            rows.append(f'<tr><td class="chk"><input type="checkbox" aria-label="unlocked"></td><td><b>{e(c[ni])}</b></td><td>{req(c[ri])}</td><td>{e(c[gi]) if gi is not None and gi < len(c) else ""}</td></tr>'); total += 1
        if rows:
            title = (f"{parent} – {h}" if parent and h in ("Original and Enhanced Editions", "Enhanced Edition only") else h)
            title = title.replace("Normal –", "Main achievements –").replace("Hidden –", "Secret achievements –")
            body += sec(i, e(title), tbl(["✔", "Achievement / trophy", "How to unlock", "G"], rows)); i += 1
    if not total: continue
    body = f'  <div class="warnbox">✅ Tick each one you have unlocked – ticks are saved in this browser only. <b id="chkc"></b> Cheats can block achievements/trophies.</div>\n' + body
    body += (f'  <p class="note">More {e(name)}: <a href="{gk}-100-percent-completion">100% checklist</a> · <a href="{gk}-missions">missions</a> · <a href="{gk}-cheats">cheats</a></p>\n'
             f'  <p class="note">List from the <a href="https://gta.fandom.com/wiki/Achievements_in_{wk}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). G = Xbox Gamerscore. Unofficial fan guide, not affiliated with Rockstar Games.</p>\n')
    write(f"{gk}-achievements", f"All {total} {name} Achievements & Trophies (Checklist)", clip(f"Every {name} achievement and trophy ({total}) with how to unlock it and its Gamerscore, as a tick-box checklist – including the secret ones."),
          f"{e(name.upper())} · ACHIEVEMENTS", f"{name} Achievements", f"🏆 {total} achievements and trophies, with how to unlock each one.", body, f"{name} achievements", JS)
    print(gk, "achievements", total)

# ---------- 2D-era cheats
for gk, k, name, wk, year in [("gta-1", "1", "GTA 1", "GTA_1", 1997), ("gta-london-1969", "lon", "GTA London 1969", "GTA_London_1969", 1999), ("gta-2", "2", "GTA 2", "GTA_2", 1999)]:
    d = load(f"ch_{k}.json")
    if not d: continue
    h, body, i, total = None, "", 1, 0
    for x in d:
        if "h" in x: h = x["h"]; continue
        t = x["rows"]
        if not t or not t[0] or t[0][0]["t"] in ("Navigation",) or any("v • e" in c["t"] or "Protagonists" in c["t"] for r in t[:2] for c in r): continue
        hd = [c["t"] for c in t[0]]
        if len(hd) < 2: continue
        rows = ["<tr>" + "".join(f'<td>{"<span class=code>" + e(c["t"]) + "</span>" if j and hd[j] in ("PlayStation", "PC", "Dreamcast", "Code") or (j == 0 and hd[0] in ("Code", "Key")) else e(c["t"])}</td>' for j, c in enumerate(r)) + "</tr>" for r in t[1:] if len(r) == len(hd)]
        if rows:
            body += sec(i, e(h or "Cheats"), tbl([e(c) for c in hd], rows)); i += 1; total += len(rows)
    if not total: continue
    how = {"gta-1": "On PC, type the code as your player name on the name screen. On PlayStation, enter it as your name.",
           "gta-london-1969": "Type the code as your player name before starting a game (PC), or enter it as your name on PlayStation.",
           "gta-2": "Enter the code as your player name on the name entry screen. Some codes only work on one platform."}[gk]
    body = f'  <div class="warnbox">⌨️ <b>How to enter the codes:</b> {e(how)}</div>\n' + body
    body += (f'  <p class="note">More: <a href="gta-cheats">cheats for every GTA game</a>' + (' · <a href="gta-2-missions">GTA 2 missions</a>' if gk == "gta-2" else '') + ' · <a href="gta-3-cheats">GTA 3 cheats</a> · <a href="gta-vice-city-cheats">Vice City cheats</a></p>\n'
             f'  <p class="note">Codes from the <a href="https://gta.fandom.com/wiki/Cheats_in_{wk}" rel="nofollow noopener" target="_blank">GTA Wiki</a> (CC BY-SA 3.0). Unofficial fan guide, not affiliated with Rockstar Games.</p>\n')
    write(f"{gk}-cheats", f"All {name} Cheats & Codes ({year})", clip(f"Every {name} ({year}) cheat code ({total}) for PC and PlayStation: all weapons, lives, levels, points and debug keys, with how to enter them."),
          f"{e(name.upper())} · CHEATS", f"{name} Cheats", f"🕹️ {total} codes for the original top-down {e(name)} ({year}).", body, f"{name} cheats")
    print(gk, "cheats", total)

sm_path = os.path.join(SITE, "sitemap.xml"); sm = open(sm_path, encoding="utf-8").read()
for s in pages:
    loc = f"<loc>{BASE}{s}</loc>"
    if loc not in sm: sm = sm.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod></url>\n</urlset>")
open(sm_path, "w", encoding="utf-8").write(sm)
inx = os.path.join(ROOT, "indexnow.json")
if os.path.exists(inx):
    j = json.load(open(inx, encoding="utf-8")); j["urlList"] = re.findall(r"<loc>(.*?)</loc>", sm); json.dump(j, open(inx, "w", encoding="utf-8"))
print(len(pages), "pages; sitemap", sm.count("<url>"), "urls")
