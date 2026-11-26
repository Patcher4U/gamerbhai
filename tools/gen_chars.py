"""Character pages (one per officially introduced character) built from gta6-site/story.html.
Images: Rockstar's official screenshots already self-hosted in img/chars (fan-content policy, no hotlinking).
Called from gen_pages.py: build(SITE, page, sec, crumbs, e, made, BASE) -> list of slugs.
Pages use data-page="char" so app.js keeps ads and buy boxes off them (Rockstar images).
"""
import html, os, re

# Missions that clearly involve each character (curated; avoids false name matches)
MISSIONS = {
    "Jason Duval": ["Gone Fishing", "Gear Up", "Lab Fees", "Just a Scratch", "Take Care of Jason"],
    "Lucia Caminos": ["Prologue"],
    "Brian Heder": ["Gone Fishing", "Lab Fees", "Hey Arnold!", "Meet the Heders"],
    "Cal Hampton": ["Unwanted Attention", "Hey Arnold!"],
    "Boobie Ike": ["Boobie Time"],
    "Raul Bautista": ["Raul's Next Job"],
}
WHERE = {   # region info only from the story page / chapter data
    "Jason Duval": "Starts in the Leonida Keys (Chapter 1), then Port Gellhorn and Vice City.",
    "Lucia Caminos": "Starts in Leonida Penitentiary (Prologue); Chapter 2 is mostly played as Lucia.",
    "Brian Heder": "The Leonida Keys, where he runs a boat yard.",
    "Cal Hampton": "The Leonida Keys, mostly at home.",
    "Boobie Ike": "Vice City.", "Dre'Quan Priest": "Vice City.", "Real Dimez": "Vice City.",
}

def slug_of(name): return "gta-6-" + re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.lower().replace("'", ""))).strip("-")

def build(SITE, page, sec, crumbs, e, made, BASE):
    s = open(os.path.join(SITE, "story.html"), encoding="utf-8").read()
    chars = []
    for a in re.findall(r'<article class="glass tilt char">(.*?)</article>', s, re.S):
        un = lambda x: html.unescape(re.sub(r"<[^>]+>", "", x)).strip()
        name = un(re.search(r"<h3[^>]*>(.*?)</h3>", a, re.S)[1]).replace("⇄", "").strip()
        chars.append(dict(
            name=name, tag=un(re.search(r'class="ctag[^"]*">(.*?)<', a)[1]),
            imgs=re.findall(r'(img/chars/[a-z_0-9]+\.webp)', a),
            role=un((re.search(r'<p class="role">(.*?)</p>', a, re.S) or [None, ""])[1]),
            facts=[un(x) for x in re.findall(r"<li>(.*?)</li>", a, re.S)],
            yt=(re.search(r'data-yt="([\w-]+)"', a) or [None, ""])[1], start=(re.search(r'data-start="(\d+)"', a) or [None, ""])[1],
            rs=(re.search(r'href="(https://www\.rockstargames\.com/[^"]+)"', a) or [None, ""])[1]))
    out = []
    for c in chars:
        slug = slug_of(c["name"]); url = BASE + slug; out.append(slug); n = c["name"]
        title = f"{n} in GTA 6: Character Guide"
        desc = f"Who is {n} in GTA 6? {c['role']}. Official background, where they appear, missions and official screenshots. No spoilers."[:158]
        imgs = "".join(f'<img src="{i}" alt="{e(n)} in an official GTA 6 screenshot" width="900" height="506" loading="{"eager" if k == 0 else "lazy"}">' for k, i in enumerate(c["imgs"][:2]))
        body = f'  <section class="reveal"><figure class="pphoto wide">{imgs}<figcaption class="note">© Rockstar Games. Official screenshots, used under Rockstar\'s fan content policy.</figcaption></figure></section>\n'
        body += sec("01", f"Who is {e(n)}?", f'<p><b>{e(c["role"])}.</b> {e(c["tag"].title())}.</p><ul>' + "".join(f"<li>{e(f)}</li>" for f in c["facts"]) + '</ul>')
        if WHERE.get(n): body += sec("02", "Where you meet them", f"<p>{e(WHERE[n])}</p>")
        ms = [m for m in MISSIONS.get(n, [])]
        if ms:
            body += sec("03", "Missions with " + e(n.split()[0]), "<p>" + " · ".join(f'<a href="{made[m]}">{e(m)}</a>' if m in made else e(m) for m in ms) + "</p><p class=\"note\">Mission names from player guides; later-chapter names may hint at story events.</p>")
        btns = ""
        if c["yt"]: btns += f'<button type="button" class="btn mvid" data-yt="{c["yt"]}"' + (f' data-start="{c["start"]}"' if c["start"] else "") + '>▶ See in the official trailer</button> '
        if c["rs"]: btns += f'<a class="btn" href="{c["rs"]}" target="_blank" rel="noopener">📸 Rockstar\'s official page ↗</a>'
        if btns: body += sec("04", "Watch &amp; official info", f'<div class="vbar">{btns}</div>')
        others = [o for o in chars if o is not c]
        body += ('  <section class="reveal"><h2><span class="n">05</span>Other characters</h2><div class="grid">' +
                 "".join(f'<a class="glass tilt area" href="{slug_of(o["name"])}"><div class="pop"><h3>{e(o["name"])}</h3><p>{e(o["role"])}</p></div></a>' for o in others) + '</div></section>\n')
        body += sec("★", "More", '<p><a href="story">👥 All characters &amp; Leonida map</a> · <a href="walkthrough">📖 Walkthrough</a> · <a href="guides#cheats">🎮 Cheats</a></p><p class="note">Facts from Rockstar\'s official character introductions. Unofficial fan guide, not affiliated with Rockstar Games.</p>')
        ld = [crumbs([("Home", ""), ("Characters", "story"), (n, slug)]),
              {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "image": BASE + c["imgs"][0] if c["imgs"] else BASE + "img/og.jpg",
               "author": {"@type": "Organization", "name": "GamerBhai"}, "mainEntityOfPage": url, "about": {"@type": "Person", "name": n}}]
        doc = page(title, desc, url, f"GTA 6 CHARACTERS · {e(c['tag'])}", n, e(c["role"]), body, ld)
        doc = doc.replace('data-page="article"', 'data-page="char"', 1).replace('<div class="ad reveal">Ad</div>\n', "", 1)
        open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(doc)
    # add a "Full character guide" link to each card on the story page (idempotent)
    def addlink(m):
        a = m.group(0); nm = html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h3[^>]*>(.*?)</h3>", a, re.S)[1])).replace("⇄", "").strip()
        sl = slug_of(nm)
        if f'href="{sl}"' in a: return a
        return a.replace("</article>", f'  <a class="olink" href="{sl}">📖 Full character guide</a>\n      </article>', 1)
    s2 = re.sub(r'<article class="glass tilt char">.*?</article>', addlink, s, flags=re.S)
    if s2 != s: open(os.path.join(SITE, "story.html"), "w", encoding="utf-8").write(s2)
    return out
