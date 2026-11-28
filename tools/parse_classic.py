"""One-off: turn the GTA Wiki cheat tables (saved as text by the browser) into tools/classic_cheats.json.
Usage: python -I tools/parse_classic.py <folder with gta5.txt gtasa.txt gtavc.txt gta3.txt gta4.txt>
Codes are facts cross-checked with well-known lists; names/effects are shortened in our own words."""
import json, os, re, sys

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "classic_cheats.json")

def rows(fn):
    sec = ""
    for l in open(os.path.join(SRC, fn), encoding="utf-8").read().split("\n"):
        if l.startswith("###"):
            sec = l[4:].strip(); continue
        if "|" not in l or l.split("|")[0] in ("Effect", "Cheat") or sec in ("Navigation", "Video", "Videos", "Trivia", "References", "See Also", "Oversights", "Notes"):
            continue
        yield sec, [c.strip() for c in l.split("|")]

def btn(s):
    if "not available" in s.lower() or s.strip().lower() in ("n/a", "-"): return ""
    s = re.sub(r"\s*\((?:PlayStation|Xbox)\)", "", s)
    s = re.sub(r"(Right|Left) (Trigger|Bumper) \((RT|LT|RB|LB)\)", r"\3", s)
    s = re.sub(r"D-Pad (\w+)", lambda m: m.group(1).capitalize(), s)
    s = re.sub(r"\s*,\s*", ", ", s).strip(" ,")
    return s

def clean_name(s):
    s = re.split(r" / | Note:", s)[0]
    s = re.sub(r"\[\d+\]", "", s)
    return re.sub(r"\s+", " ", s).strip(" .;")

def short(s):
    s = clean_name(s)
    s = re.sub(r"\s*\(.*?\)", "", s)
    s = s.split(";")[0].strip()
    return s[:1].upper() + s[1:]

SKIP_WORDS = ("IWANTBIGTITS", "WELOVEOURDICK", "Prostitutes pay", "Kinky theme")
games = {}

# ---------- GTA V (four tables merged by name)
ALIAS = {"change weather": "Change Weather", "fast running": "Fast Run", "fast run": "Fast Run",
         "slidey cars": "Slippery Cars", "slippery car tires": "Slippery Cars", "slippery cars": "Slippery Cars",
         "low gravity": "Moon Gravity", "moon gravity": "Moon Gravity", "weapons & ammo": "Weapons & Ammo",
         "weapons": "Weapons & Ammo", "give all weapons": "Weapons & Ammo", "explosive bullets": "Explosive Bullets",
         "explosive ammo rounds": "Explosive Bullets", "give parachute": "Parachute", "parachute": "Parachute",
         "slow motion aiming": "Slow Motion Aim", "slow motion aim": "Slow Motion Aim", "spawn bmx": "Spawn BMX", "spawn": "Spawn BMX"}
v = {}
for sec, c in rows("gta5.txt"):
    key = re.sub(r"\s*\(.*?\)", "", re.sub(r"\[\d+\]", "", c[0])).strip()
    canon = ALIAS.get(key.lower(), key[:1].upper() + key[1:])
    d = v.setdefault(canon, {"name": canon, "effect": clean_name(c[0])})
    val = c[1] if len(c) > 1 else ""
    if sec.startswith("Xbox"): d["xbox"] = btn(val)
    elif sec.startswith("PS3"): d["ps"] = btn(val)
    elif sec == "PC": d["pc"] = val.split()[0] if val else ""
    elif sec.startswith("Phone"): d["phone"] = re.sub(r"\(.*", "", val).strip()
games["gta-5"] = list(v.values())

# ---------- San Andreas (PS2 | PC | Xbox | Xbox 360 | Android)
sa, seen = [], set()
for sec, c in rows("gtasa.txt"):
    if len(c) < 5 or any(w in c[0] or w in c[2] for w in SKIP_WORDS): continue
    pcs = [p.strip() for p in c[2].split(" / ") if p.strip()]
    if any("not available" in p for p in pcs): pcs = []
    plain = [p for p in pcs if not p.endswith("*")]
    star = [p.rstrip("*") for p in pcs if p.endswith("*")]
    pc = (plain or star or [""])[0]
    name = short(c[0])
    if pc and pc in seen: continue
    seen.add(pc or name)
    sa.append({"name": name, "effect": clean_name(c[0]), "group": sec, "ps": btn(c[1]), "pc": pc,
               "pc_alt": star[0] if star and star[0] != pc else "", "xbox": btn(c[4])})
games["gta-san-andreas"] = sa

# ---------- Vice City and GTA III (PS2 | PC | Xbox)
for fn, slug in (("gtavc.txt", "gta-vice-city"), ("gta3.txt", "gta-3")):
    out = []
    for sec, c in rows(fn):
        if len(c) < 4 or any(w in c[0] or w in c[2] for w in SKIP_WORDS): continue
        pc = c[2] if c[2].lower() not in ("n/a", "") else ""
        pc = re.sub(r"\s*\(1\.0 version\)\s*/\s*", " / ", pc).replace(" (1.1 version)", "")
        out.append({"name": short(c[0]), "effect": clean_name(c[0]), "ps": btn(c[1]), "pc": pc, "xbox": btn(c[3])})
    games[slug] = out

# ---------- GTA IV (+ episodes) phone numbers
iv = []
for sec, c in rows("gta4.txt"):
    if len(c) < 2: continue
    num = re.sub(r"\(.*", "", c[1]).strip()
    ep = {"The Lost and Damned": "The Lost and Damned", "The Ballad of Gay Tony": "The Ballad of Gay Tony"}.get(sec, "")
    nm = short(c[0])
    if sec in ("Vehicles", "The Lost and Damned") or (ep and len(nm.split()) <= 2 and nm[0].isupper() and "throws" not in nm):
        nm = "Spawn " + nm
    iv.append({"name": nm, "effect": clean_name(c[0]), "phone": num, "episode": ep})
games["gta-4"] = iv

# ---------- short, search-friendly names (lists = used in order for duplicate rows); None = drop the row
REN = {
 "gta-san-andreas": {"Adrenaline effects": "Adrenaline Mode", "Armor, health and $250,000 in money": "Health, Armor & $250,000 (HESOYAM)",
  "CJ jumps 10 times higher": "Super Jump", "Commit suicide": "Suicide", "Hitman level for all weapons": "Hitman Weapon Skills",
  "Lock wanted level": "Never Wanted", "Raise wanted level by two stars": "Raise Wanted Level", "Remove wanted level": "Remove Wanted Level",
  "Six-star wanted level": "Six-Star Wanted Level", "Maximum fat": "Max Fat", "Infinite Lung capacity": "Infinite Lung Capacity",
  "Maximum muscle": "Max Muscle", "Maximum respect": "Max Respect", "Maximum sex appeal": "Max Sex Appeal", "Maximum stamina": "Max Stamina",
  "Maximum vehicle skills": "Max Driving Skills", "Minimum fat and muscle": "Skinny CJ", "CJ never gets hungry": "Never Hungry",
  "Super punches": "Super Punch", "Unlimited ammunition with no reload for all weapons": "Infinite Ammo", "Unlimited health": "Infinite Health",
  "Weapons, tier 1": "Weapon Set 1", "Weapons, tier 2": "Weapon Set 2", "Weapons, tier 3": "Weapon Set 3", "Weapons, tier 4": "Weapon Set 4",
  "Complete invulnerability": "Invincibility", "All cars have nitrous": "Nitro on All Cars", "Cars drive on water": "Drive on Water",
  "Flying boats": "Flying Boats", "Flying cars": "Flying Cars", "Spawn sport cars": "Sports Car Traffic (Console)", "Improved suspensions": "Perfect Handling",
  "Full weapon aiming in vehicles + Micro SMG": "Full Aim While Driving", "Massive bicycle bunny hops": "Mega Bike Jump",
  "Spawn Hotring Racer": ["Spawn Hotring Racer", "Spawn Hotring Racer 2"], "Spawn Rancher": "Spawn Rancher",
  "Spawn Tanker with attached tanker trailer": "Spawn Tanker Truck", "Taxi missions completed": "Taxi Nitro (Taxi Missions Done)",
  "Carl's car is invincible and can instantly destroy other vehicles": "Destroy Cars on Touch", "Aggressive drivers": "Aggressive Traffic",
  "Beach party theme": "Beach Party Theme", "Beater/cheap traffic": "Cheap Cars Traffic", "Black traffic": "Black Traffic",
  "Carnival/funhouse theme": "Funhouse Theme", "Cars float away when hit": "Cars Fly Away When Hit", "Pedestrians riot": ["Riot Mode", "Riot with Golf Clubs"],
  "Explode all vehicles": "Blow Up All Cars", "Invisible cars": "Invisible Cars", "No pedestrians/reduced traffic": "Empty Streets",
  "Pedestrians are Elvis": "Elvis Everywhere", "Pedestrians attack Carl": "Peds Attack CJ", "Pedestrians attack Carl with guns": "Peds Attack CJ with Guns",
  "Pedestrians have weapons": "Armed Pedestrians", "Pink traffic": "Pink Traffic", "Rural traffic": "Farm Vehicle Traffic", "Rural theme": "Country Theme",
  "Traffic lights always green": "Always Green Lights", "Triad theme": "Ninja Theme", "Gang members spawn much faster": "More Gang Members",
  "Gang wars break out all over San Andreas": "Gang Wars Everywhere", "No citizens or cops, only gang members having gunfights": "Gangs Control the Streets",
  "Recruit anyone into gang with Pistols": "Recruit Anyone (Pistols)", "Recruit anyone into gang with rocket launchers": "Recruit Anyone (Rockets)",
  "Recruit anyone into gang with AK47s": "Recruit Anyone (AK-47s)", "Always midnight": "Always Midnight", "Always 21:00 with orange sky": "Orange Sky (Always 9 PM)",
  "Cloudy weather": "Cloudy Weather", "Fast gameplay": "Faster Gameplay", "Slow gameplay": "Slow Motion", "Speed up time": "Faster Clock",
  "Foggy weather": "Foggy Weather", "Rainy weather": "Rainy Weather", "Stormy weather": "Stormy Weather", "Sunny weather": "Sunny Weather",
  "Very sunny weather": "Very Sunny Weather", "Advance 4 hours": "Skip 4 Hours (Console)"},
 "gta-vice-city": {"Replenish player health": "Full Health", "Replenish player armor": "Full Armor", "Basic weapons set": "Weapon Set 1",
  "Intermediate weapons set": "Weapon Set 2", "Advanced weapons set": "Weapon Set 3", "Spawn a Sabre Turbo": "Spawn Sabre Turbo", "Spawn a Caddy": "Spawn Caddy",
  "Spawn a Romero's Hearse": "Spawn Romero's Hearse", "Spawn a Trashmaster": "Spawn Trashmaster", "Spawn Love Fist": "Spawn Love Fist Limo", "Spawn a Rhino": "Spawn Rhino Tank",
  "Spawn a Hotring Racer": ["Spawn Hotring Racer", "Spawn Hotring Racer 2"], "Spawn a Bloodring Banger": ["Spawn Bloodring Banger", "Spawn Bloodring Banger 2"],
  "Aggressive drivers": "Aggressive Traffic", "All traffic cars are black": "Black Traffic", "All traffic cars are pink": "Pink Traffic",
  "All traffic lights are green": "Always Green Lights", "Blow up/explode/destroy all vehicles, excluding police-controlled helicopters": "Blow Up All Cars",
  "Cars can drive/hover over water": "Drive on Water", "Low gravity for cars, cars control like plane in air": "Flying Cars",
  "Low gravity for boats, boats control like plane in air": "Flying Boats", "Only the wheels of cars are visible": "Invisible Cars",
  "Various changes to vehicle properties, including wheel size, top speed, colors, and others": "Vehicle Changes",
  "Increase grip on ground, boost jump ability in all cars, disables unique handling": "Better Handling", "Commit suicide or, with sufficiently high health, suffer major loss of health": "Suicide",
  "Increase wanted level by two stars": "Raise Wanted Level", "Remove all wanted level": "Remove Wanted Level", "Police come back to life after being killed": None,
  "Sunny/clear weather": "Sunny Weather", "Light clouds": "Cloudy Weather", "Stormy weather": "Stormy Weather", "Foggy weather": "Foggy Weather", "Overcast weather": "Overcast Weather",
  "Vercetti Gang will become girls in bikinis with M4s": None, "Gives Tommy thin arms/legs": "Skinny Tommy", "Gives Tommy thick arms/legs": "Fat Tommy",
  "Women will be attracted to and follow Tommy": "Women Follow Tommy", "Nearby pedestrians will enter Tommy's vehicle": "Peds Get in Your Car",
  "Increase game speed by 2, up to x4 normal speed": "Faster Gameplay", "Decrease game speed by half, down to x0.25 normal speed": "Slow Motion",
  "Speed up game clock": "Faster Clock", "Makes Tommy smoke a cigarette": "Tommy Smokes", "Pedestrians carry weapons": "Armed Pedestrians",
  "Pedestrians hate Tommy": "Peds Attack Tommy", "Pedestrian riot": "Riot Mode", "Shows media level when previous media level is beaten": "Show Media Level",
  "Play as a pedestrian": "Play as Random Ped", "Play as Love Fist character Jezz Torrent": "Play as Jezz Torrent"},
 "gta-3": {"Replenish player health": "Full Health", "Replenish player armor": "Full Armor", "Acquire all weapons": "All Weapons", "Acquire $250,000 in cash": "$250,000 Money",
  "Spawn a Rhino": "Spawn Rhino Tank", "Blow up/explode/destroy all vehicles, excluding police-controlled helicopters": "Blow Up All Cars",
  "Low gravity for cars, cars control like airborne planes": "Flying Cars", "Only the wheels of cars are visible": "Invisible Cars",
  "Increase grip on ground, boost jump ability in all cars, disables unique handling": "Better Handling", "Increase wanted level by two stars": "Raise Wanted Level",
  "Remove all wanted level": "Remove Wanted Level", "Light clouds": "Cloudy Weather", "Stormy weather": "Stormy Weather", "Foggy weather": "Foggy Weather",
  "Overcast weather": "Overcast Weather", "Increase game speed by 2, up to x4 normal speed": "Faster Gameplay", "Decrease game speed by half, down to x0.25 normal speed": "Slow Motion",
  "Speed up game clock": "Faster Clock", "Pedestrian riot": "Riot Mode", "Pedestrians attack Claude": "Peds Attack Claude", "Pedestrians carry weapons": "Armed Pedestrians",
  "Play as pedestrian": "Play as Random Ped", "Gore mode": "Gore Mode"},
 "gta-4": {"Refill health and ammo, repair vehicle": "Health, Armor & Ammo", "Refill health and armor, repair vehicle": "Health & Armor",
  "Advanced weapons set and refill ammo": ["Weapon Set 1", "TBoGT Weapon Set"], "Poor weapons set and refill ammo": "Weapon Set 2",
  "Cycles weather sequentially to the next condition in the same order as the weather cheats in GTA III and GTA Vice City": "Change Weather",
  "Clear wanted level": "Remove Wanted Level", "Increase wanted level by one star": "Raise Wanted Level", "Luis throws explosive punches": "Explosive Punches",
  "Explosive sniper rounds": "Explosive Sniper Rounds"},
}
for g, m in REN.items():
    keep = []
    for c in games[g]:
        k = c["name"]
        if k not in m:
            k2 = next((x for x in m if c["effect"].startswith(x)), None)
            if k2: k = k2
        r = m.get(k, c["name"])
        if isinstance(r, list): r = r.pop(0) if len(r) > 1 else r[0]
        if r is None: continue
        c["name"] = r.replace("Sports car trafficNote: Random vehicle", "Sports Car Traffic")
        keep.append(c)
    games[g] = keep
FIX = [("Sports Car Traffic spawn", "Sports Car Traffic"), ("Various changes to vehicle", "Vehicle Changes"),
       ("Increase grip on ground", "Better Handling"), ("Cycles weather", "Change Weather")]
for g in games.values():
    for c in g:
        for pre, nm in FIX:
            if c["name"].startswith(pre): c["name"] = nm

# The wiki's Xbox columns for the 3D-era games are unreliable (Right shown as Left, buttons missing), so Xbox codes
# are derived from the PS2 sequence with the standard 360 / Definitive Edition mapping (R1=RT, R2=RB, L1=LT, L2=LB).
XMAP = {"R1": "RT", "R2": "RB", "L1": "LT", "L2": "LB", "Cross": "A", "Circle": "B", "Square": "X", "Triangle": "Y"}
for g in ("gta-san-andreas", "gta-vice-city", "gta-3"):
    for c in games[g]:
        c["xbox"] = ", ".join(XMAP.get(b.strip(), b.strip()) for b in c["ps"].split(",")) if c.get("ps") else ""
json.dump(games, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, l in games.items():
    print(k, len(l))
