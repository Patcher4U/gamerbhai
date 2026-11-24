import sys, os, html, json
out = sys.argv[1]
e = html.escape
U = lambda pid, w: f"https://images.unsplash.com/photo-{pid}?auto=format&fit=crop&w={w}&q=80"
CH = [
 dict(n="Prologue", t="Breaking Out", area="Leonida Penitentiary", who="Lucia", pid="1554896593-e7f761a681f9",
      intro="A short tutorial chapter that introduces Lucia and her life behind bars before the main story begins.",
      ms=["Prologue"], spoil=False),
 dict(n="Chapter 1", t="Just Like Paradise", area="Leonida Keys", who="Jason, then Lucia", pid="1740989972940-3570cf86d902",
      intro="Jason earns his keep in the Keys doing odd jobs for Brian, from smuggling runs to rent collection. Lucia joins the story after her release.",
      ms=["Gone Fishing","Gear Up","Lab Fees","Just a Scratch","Unwanted Attention","Pipework","Hey Arnold!","Island Dreams","Feng Shui","Coming Home","Clean Up After Donnie","Buck Me","Down to Earth","Deposit Cash Into BuckMe","Save for the Future","Day Release","Clear Skies","Building a Life","Swamped","Don Gone","Recalibration","Tourist Trap","Home Sweet Home","Discharge Time"], spoil=False),
 dict(n="Chapter 2", t="Paradise Lost", area="Port Gellhorn", who="Mostly Lucia", pid="1644685127243-ff740286cf0c",
      intro="The couple lies low in Port Gellhorn. Lucia takes on a string of jobs to keep them afloat while Jason recovers.",
      ms=["What's in the Bag?","Take Care of Jason","Overnight Charges","Just Moved In","Girl's Trip","Moses","New Look","How Do I Look?","Painkiller Supplier","Ambulance Chaser","Behind on Payments","Slam Dunk","Daily Driver","Breakfast Run","Coffee Break","Prepare for Vice City","Afternoon Delight","Checking Out"], spoil=True),
 dict(n="Chapter 3", t="T*ts, A** &amp; Drug Money", area="Vice City", who="Jason &amp; Lucia (some solo missions)", pid="1533106497176-45ae19e68ba2",
      intro="The big move to Vice City. New crews, car thefts, the music scene and the first serious heist planning.",
      ms=["Welcome to Vice City","Dealer's Choice","Dubious Provenance","Mami Knows Best","Here, Kitty Kitty","Send Money to Lorena","Encrypted Hard Drive","Boobie Time","Meet the Heders","Yasmani's Jewelry Jobs","Car Service","Send More Money to Lorena","Top Billing","First Impressions","Crosstown Traffic","Credit Check","Clonin' Keys","Makin' GS","Ride or Die","Raul's Next Job","Sinfrontera National Bank","Security Expert","Caught Slipping","Heist Planning","Company Property","Safe Word","The Missing Link","Cooties","Hidden Charges","Bricked Up","South Leonida Real Estate","The Cartel Heist"], spoil=True),
 dict(n="Chapter 4", t="Vice City, Baby", area="Vice City", who="Jason &amp; Lucia (many solo missions)", pid="1513735539099-cf6e5d559d82",
      intro="The longest chapter. Bigger scores, more enemies and a lot of preparation for the endgame.",
      ms=["Ocean Beach","Another Life","Pool Day","Company Cars","Lawyer Up","Heavy Lifting","Party Hard","Pay Abe's Fee","Photo/Shoot","Making Gainz","Blood Sweat and Gear","Too Much Baggage","Watch It","Amateur Hour","Call Nate","Cash Injections","Dirty Work","Nate Will Be in Touch","Adventures in Babysitting","Rafa's Kidnapping","Fresh Evidence","Child's Play","Power Play","Close Surveillance","Delivery Method","Team Building","Fully Catered","Heist Plans in Place","Headliners","VCIA Takedown","Tie Up Loose Ends","Call Valentina Back","Sunset","Starting From Zero"], spoil=True),
 dict(n="Chapter 5", t="Top of the World, Ma", area="Leonida (final chapter)", who="Jason &amp; Lucia", pid="1530686577637-0ccce382b327",
      intro="The finale. Ten missions that wrap up Jason and Lucia's story.",
      ms=["Bird in the Hand","Taking Liberties","Doggie Bag","VC Baby","Operation Savage Glory","Honest Abe","Unfinished Business","Pay Abe's Fee","Protective Custody","The End of the Road"], spoil=True),
]
FIRST = {
 "Gone Fishing":"Pick up the packages dropped from Donnie's plane, get him out of trouble with a rival crew, then fly back to Brian's marina.",
 "Gear Up":"Buy a long gun so Jason is ready for tougher work.",
 "Lab Fees":"Drop in on one of Brian's tenants and collect the rent they owe.",
 "Just a Scratch":"Take Jason's damaged Ganado to a body shop for repairs.",
 "Unwanted Attention":"Meet up with Cal and follow his tip.",
 "Pipework":"Help Mandy with a plumbing job and pick up rent while you're there.",
 "Hey Arnold!":"Join Brian and Cal and help find a broker.",
 "Island Dreams":"Start working for Kenton and complete his first diving job.",
}
VIDEOS = {"Prologue":"Zh6VrJuW_i8","Gone Fishing":"ejIdp8axfhY","Gear Up":"Lb6JyzX5gho","Lab Fees":"IcmQT-rZoIw","Just a Scratch":"A_UeksX3Is0",
 "Unwanted Attention":"m2APlrqUlqY","Pipework":"gyGEkYIcpYY","Hey Arnold!":"eFMv_LH_k8M","Island Dreams":"Sv1_DptbiYE","Feng Shui":"n05E916smas",
 "Coming Home":"DBI371PR9Us","Buck Me":"QDgttkhvNGY","Clean Up After Donnie":"XYMogXWZuUk","Down to Earth":"Se-zLoWvB68","Clear Skies":"HKvWN48ln8A",
 "Day Release":"slPlJaZG8ww","Swamped":"EEtt8Zrwb6k","Don Gone":"9KwTkHEm28o","Recalibration":"1w11tH5tUVU","Tourist Trap":"K24cuLXKr5c"}
VIDEOS.update({"Deposit Cash Into BuckMe": "xkXWTn3uV3M", "Save for the Future": "w3ZSinDqFok", "Building a Life": "x-rEd6H-4jY", "Home Sweet Home": "vR6V5zHFHRw", "Discharge Time": "waTQZs5Tx34", "What's in the Bag?": "0FmfgiOo_cU", "Take Care of Jason": "40r1qkLqJHE", "Overnight Charges": "MAjq6Xzu740", "Just Moved In": "MAjq6Xzu740", "Girl's Trip": "LrCH4W8bsgY", "Moses": "rqsFjvfL41c", "New Look": "EQLNQwK7mRE", "How Do I Look?": "hjYhnLLgjgo", "Painkiller Supplier": "LFa8U4yS2Kk", "Ambulance Chaser": "_c_9JKtI3YI", "Behind on Payments": "G7j-BmK8idU", "Slam Dunk": "46hMImFnTPY", "Daily Driver": "rvdiXu3rG5k", "Breakfast Run": "wQbWc9_X5O8", "Coffee Break": "lDrlv6Vcv6c", "Prepare for Vice City": "bSkDxKrunSw", "Afternoon Delight": "rkwmcjJmjOI", "Checking Out": "K7lEEKKxFFw", "Welcome to Vice City": "kAcSTf-Tcg8", "Dealer's Choice": "NSMOq_BJbBU", "Dubious Provenance": "SixlDJBEHzs", "Mami Knows Best": "7uEz-Q8n48M", "Here, Kitty Kitty": "b78Xa-Jlsts", "Encrypted Hard Drive": "yhyepsimLNI", "Boobie Time": "-BWqzOICZqQ", "Meet the Heders": "uEIO0X1O_vs", "Yasmani's Jewelry Jobs": "2s4JufdNNHw", "Car Service": "-zsWbj9VJIU", "Top Billing": "WQVNZe7fTuY", "First Impressions": "ECk0VuRa7p0", "Crosstown Traffic": "EDfkvvpSACs", "Credit Check": "_chFhSky3x4", "Clonin' Keys": "rm8Qy9KRbTw", "Makin' GS": "fMpfD8M5Tj8", "Ride or Die": "-uVKD075Zb4", "Sinfrontera National Bank": "nvoYJtvCRUs", "Security Expert": "5ctGFp_zOKo", "Caught Slipping": "uxoOymNZBaw", "Company Property": "KwdZlanNH4w", "Safe Word": "szgOCuBpb2c", "The Missing Link": "CLwU7K03tNI", "Cooties": "76bTG83T8Qk", "Hidden Charges": "pyt1SuBVCHc", "Bricked Up": "7We35bOoNWw", "South Leonida Real Estate": "CghnJ-t8I8E", "The Cartel Heist": "KUYCq2P2biU", "Ocean Beach": "2BiQ0w0YiJs", "Another Life": "yqe8ckcY1fM", "Pool Day": "CcAuWAMLtnk", "Company Cars": "5OoyV6Adu04", "Lawyer Up": "GGRKxvxhQ8c", "Heavy Lifting": "AU3U0p1-GjQ", "Party Hard": "FHmgkHSRaU8", "Photo/Shoot": "IDCAvXSSBmQ", "Making Gainz": "zxyusGaiBy4", "Too Much Baggage": "0h91zo5nhF8", "Watch It": "y8x_pvmOPg4", "Amateur Hour": "nRHXcj3gfP0", "Cash Injections": "wFuj8A_nQ2w", "Dirty Work": "mUR56H7d5vg", "Adventures in Babysitting": "pbk_PuLy1dc", "Fresh Evidence": "yJGde39buyw", "Child's Play": "a3WqQnHoT4s", "Power Play": "lgjlnKYSxQM", "Close Surveillance": "4HN3Z7Aet6o", "Delivery Method": "SGWqV-kQLEo", "Team Building": "4ncAHRIH3hs", "Fully Catered": "ogaJTdevvno", "Headliners": "IohTQf1O_1c", "VCIA Takedown": "j_qEirg9uwE", "Sunset": "SZCo8FpDKwY", "Starting From Zero": "62Tg0kF7qBs", "Bird in the Hand": "jWXVtFlAamY", "Taking Liberties": "Qa9Vu479imc", "VC Baby": "tbgWFly5Tog", "Honest Abe": "csXOTbprdPc", "Protective Custody": "ELbE-w73oVk", "The End of the Road": "23tN6iTs7fc"})
VIDEOS.update({"Send Money to Lorena": "Ljo3sfwv6EI", "Send More Money to Lorena": "Ljo3sfwv6EI", "Heist Planning": "zp1-8v1HtO8", "Pay Abe's Fee": "u8UbN4gpRNY", "Blood Sweat and Gear": "algcH5RhQYs", "Tie Up Loose Ends": "dUJtD48ya5Q", "Doggie Bag": "oa9CI5miCg8", "Operation Savage Glory": "nIWz0Ac3zJY", "Rafa's Kidnapping": "9UMOj9We4bw"})
PHONE = {"Call Nate","Nate Will Be in Touch","Call Valentina Back"}   # in-game phone calls, nothing to film
PLAYLIST = "PLPb0S9KmRWMY"
AGE = {"Gone Fishing"}   # age-restricted on YouTube: cannot play inside other sites
SIDE = [
 ("⚠️ Missable","Get Shirley's Rum &amp; Steal the Scooter","Chapter 1","Finish these before the story moves you out of the Leonida Keys, or they're gone."),
 ("🏁 Questline","Thrillbillies (Billy)","Chapter 2","Starts with a visit to the Mud Club. Next job: Twist Wrist, Smash, Grab."),
 ("🎯 Jason only","Veteran Hunted (Bret)","Chapter 2","Optional side job for Jason."),
 ("🚜 Questline","Check Out McKittrick Farm (Kyle)","Chapter 2","Side story that starts on a farm outside town."),
 ("⚠️ Missable","Join a Street Race (Yago)","Chapter 3","Race Against Yago is time-limited. The chain ends with Brother to Brother."),
 ("🏦 Unlock","That's Where The Money Is...","Chapter 4","Opens up bigger bank vault robberies."),
 ("⚠️ Missable","This Is a Free Call From... (Shayna)","Chapter 4","Lucia-only, time-limited pickup."),
]
total = sum(len(c["ms"]) for c in CH)
def chapter(i, c):
    rows = []
    for k, m in enumerate(c["ms"], 1):
        tip = FIRST.get(m) if c["n"] == "Chapter 1" else None
        vid = VIDEOS.get(m)
        btn = (f'<a class="mvid" href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener" aria-label="Watch {e(m)} walkthrough on YouTube">▶ Watch ↗</a>' if m in AGE else f'<button class="mvid" data-yt="{vid}" aria-label="Watch {e(m)} walkthrough video">▶ Watch</button>') if vid else ('<span class="mtag">📞 Phone call</span>' if m in PHONE else '<span class="mtag soon">🎬 Video soon</span>')
        rows.append(f'<li><span class="mn">{k:02d}</span><div><b>{e(m)}</b>' + (f'<p>{e(tip)}</p>' if tip else '') + f'</div>{btn}</li>')
    lst = f'<ol class="mlist">{"".join(rows)}</ol>'
    extra = ''
    if c["n"] == "Chapter 1":
        extra = '<div class="vbar"><button class="btn mvid wide" data-yt="VitS3_-HmBQ">▶ Watch all Chapter 1 optional missions</button></div>'
    elif c["spoil"]:
        extra = f'<div class="vbar"><button class="btn mvid wide" data-ytlist="{PLAYLIST}">▶ Video walkthrough playlist (new missions added as they are recorded)</button></div>'
    lst = extra + lst if not c["spoil"] else lst
    if c["spoil"]:
        lst = extra + f'<details class="spoil"><summary>Show {len(c["ms"])} missions (mission names may hint at story events)</summary>{lst}</details>'
    return f'''
  <section class="reveal chap" id="ch{i}">
    <div class="glass">
      <figure class="pphoto wide"><img src="{U(c['pid'],1400)}" srcset="{U(c['pid'],800)} 800w, {U(c['pid'],1600)} 1600w" sizes="(max-width:900px) 100vw, 1100px" alt="{e(c['area'])}" loading="lazy" width="1400" height="600"><div class="chapover"><span class="ctag lead">{e(c['n']).upper()}</span><h2>{c['t']}</h2></div></figure>
      <div class="chapmeta"><span>📍 {e(c['area'])}</span><span>🎮 {c['who']}</span><span>🧾 {len(c['ms'])} mission{'s' if len(c['ms'])>1 else ''}</span></div>
      <p>{c['intro']}</p>
      {lst}
    </div>
  </section>'''
faq = [
 ("How many missions are in GTA 6?", f"Guides count about {total} main story missions across a prologue and five chapters. Exact totals differ between guides because some count optional or repeated missions."),
 ("How many chapters does GTA 6 have?", "A prologue plus five chapters: Just Like Paradise, Paradise Lost, a Vice City chapter, Vice City Baby, and Top of the World, Ma."),
 ("Are there missable missions in GTA 6?", "Yes. Some side missions in Chapters 1, 3 and 4 disappear if you move on in the story. See the side missions section."),
]
ld = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}, ensure_ascii=False)
toc = "".join(f'<a class="pc" href="#ch{i}"><div class="c">{e(c["n"])}</div><div class="p">{c["t"]}</div></a>' for i,c in enumerate(CH))
side = "".join(f'<article class="glass place"><div class="ctag">{a}</div><h3>{b}</h3><p><b>{c}</b> · {d}</p></article>' for a,b,c,d in SIDE)
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GTA 6 Walkthrough: All {total} Missions in Order | GamerBhai</title>
<meta name="description" content="Full GTA 6 mission list in order: Prologue and Chapters 1–5, where each chapter happens, who you play, first-mission tips and every missable side mission.">
<link rel="canonical" href="https://gamerbhai.com/walkthrough">
<meta property="og:title" content="GTA 6 Walkthrough – All Story Missions in Order">
<meta property="og:description" content="Every GTA 6 chapter and mission in order, with missable side missions flagged.">
<meta property="og:type" content="article">
<meta name="theme-color" content="#12061f">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@400;600;700&family=Noto+Sans+Arabic:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<script type="application/ld+json">{ld}</script>
</head>
<body data-page="walkthrough" data-seo="1">
<canvas id="bg" aria-hidden="true"></canvas>
<div class="scrim"></div>
<header class="wrap phero reveal">
  <div class="kicker">GTA 6 GUIDE · WALKTHROUGH</div>
  <h1><span class="g">GTA 6 Walkthrough: Every Mission in Order</span></h1>
  <p class="lead">All {total} story missions across the Prologue and five chapters, where each chapter takes place, who you play, and the side missions you can miss. Later chapters are hidden behind spoiler buttons.</p>
  <div class="pops wtoc">{toc}</div>
</header>
<main class="wrap">
{"".join(chapter(i,c) for i,c in enumerate(CH))}
  <div class="ad reveal">Ad</div>
  <section class="reveal">
    <h2><span class="n">★</span>Side missions &amp; missables</h2>
    <div class="grid places">{side}</div>
  </section>
  <section class="reveal">
    <h2><span class="n">?</span>Quick answers</h2>
    {"".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q,a in faq)}
  </section>
  <section class="reveal"><div class="glass"><p class="note">Mission names and order are matched across several player guides and may be updated as more players finish the game. Unofficial fan guide, not affiliated with Rockstar Games.</p><p><a class="btn primary" href="story.html">👥 Meet the characters</a> <a class="btn" href="trailers.html">▶ Watch the trailers</a></p></div></section>
</main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="data.js"></script>
<script src="scene.js"></script>
<script src="app.js"></script>
</body>
</html>
'''
open(os.path.join(out, "walkthrough.html"), "w", encoding="utf-8").write(page)
print("missions", total)
