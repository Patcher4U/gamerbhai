"""One-off: GTA Wiki "Missions in ..." tables (saved as text by the browser) -> tools/classic_missions.json
Usage: python -I tools/parse_missions.py <folder with m_v.txt m_sa.txt m_vc.txt m_3.txt m_4.txt>
Keeps story missions (plus VC asset missions, GTA III phone missions, GTA IV optional story missions)."""
import json, os, re, sys
SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "classic_missions.json")
FILES = {"gta-5": "m_v.txt", "gta-san-andreas": "m_sa.txt", "gta-vice-city": "m_vc.txt", "gta-3": "m_3.txt", "gta-4": "m_4.txt"}
STOP = ("Side Missions", "Vehicle Missions", "Notes", "Navigation", "Trivia", "See Also", "Vice Street Racer", "Hyman Memorial",
        "Sparrow Missions", "Off-Road Missions", "Remote Controlled", "Other Missions", "Mission Tree", "Family Missions")
SKIPHEAD = ("You shouldn't see this", "Label", "Story Missions", "Main Story Missions", "Phone Missions", "Pay Phone Missions", "Final Missions",
            "Asset Missions", "Optional Missions", "Whiz Cellphone", "Finale", "Middle Park East Safehouse Required")

def region_like(h):
    return bool(re.search(r"Missions\b|^Los Santos, Part|^Blaine County, Part|^Ludendorff|^Portland$|^Staunton Island$|^Shoreside Vale$|^Search for|^Endings$", h)) and not h.startswith(("Whiz", "Phone", "Pay Phone", "Asset", "Optional", "Final"))

data = {}
for g, fn in FILES.items():
    lines = open(os.path.join(SRC, fn), encoding="utf-8").read().split("\n")
    region = {"gta-vice-city": "Vice City", "gta-3": "Portland"}.get(g, ""); giver = ""; started = False; ms = []; phone = False
    for l in lines:
        if l.startswith("### "):
            h = l[4:].strip()
            if started and h.startswith(STOP): break
            if h in ("Story Missions", "Main Story Missions"): started = True; phone = False; continue
            if g == "gta-3" and h in ("Portland", "Staunton Island", "Shoreside Vale"): region = h; started = True; continue
            if not started and g != "gta-san-andreas": continue
            if h in ("Asset Missions", "Pay Phone Missions", "Final Missions", "Optional Missions") and g in ("gta-vice-city", "gta-4"):
                region = {"Asset Missions": "Asset missions", "Pay Phone Missions": "Phone missions", "Final Missions": "Final missions", "Optional Missions": "Optional missions"}[h]; giver = ""; continue
            if h == "Phone Missions" and g == "gta-3": phone = True; continue
            if h == "Story Missions": phone = False
            if h in SKIPHEAD: continue
            if region_like(h):
                region = re.sub(r"\s*Missions\b.*", "", h).strip() or h
                if g == "gta-5" or h == "Endings": giver = ""
                started = True
                if g == "gta-4": region = {"Broker-Dukes-Bohan": "Broker, Dukes & Bohan", "Post-Algonquin Unlocked": "Algonquin"}.get(region, "Alderney" if "Florian" in h else ("Search for Darko Brevic" if "Darko" in h else region))
                continue
            giver = h; continue
        if "|" not in l or l.startswith("Title|") or not (started or g == "gta-san-andreas"): continue
        c = [x.strip() for x in l.split("|")]
        if len(c) < 2 or not c[0] or c[0].startswith("Title"): continue
        name = re.sub(r"\[\d+\]", "", c[0]).strip()
        desc = re.sub(r"\[\d+\]", "", c[1]).strip()
        rew = re.sub(r"\[\d+\]", "", c[2]).strip() if len(c) > 2 else ""
        if rew.upper() in ("N/A", "NONE", "-"): rew = ""
        gv = giver if giver != region else ""
        if g == "gta-3" and phone and gv: gv += " (phone)"
        rg = "Finale" if gv in ("Deal Ending", "Revenge Ending") else region
        ms.append({"name": name, "region": rg, "giver": gv, "desc": desc, "reward": rew})
    data[g] = ms
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from wiki_clean import fix
data = json.loads(fix(json.dumps(data, ensure_ascii=False)))
json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for g, ms in data.items():
    print(g, len(ms), "| first:", ms[0]["name"], "| last:", ms[-1]["name"], "| regions:", sorted({m["region"] for m in ms})[:12])
