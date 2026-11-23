"""Fetch the latest GTA 6 headlines (free Google News RSS, no API key, no AI) into gta6-site/headlines.json.
The News page shows them under "Around the web", each linking to the original article.
  python tools/news_feed.py gta6-site
Exit code 0 always; prints "changed" when the file content changed (used by the GitHub workflow).
"""
import json, os, re, sys, urllib.request, html
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET

SITE = sys.argv[1] if len(sys.argv) > 1 else "gta6-site"
FEEDS = ["https://news.google.com/rss/search?q=%22GTA+6%22+OR+%22GTA+VI%22+when:7d&hl=en-US&gl=US&ceid=US:en"]
BLOCK = re.compile(r"leak|nude|nsfw|torrent|crack|free download|apk|mod menu", re.I)   # keep the page clean & safe

items, seen = [], set()
for url in FEEDS:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (GamerBhai news bot)"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
    except Exception as e:
        print("feed error:", e); continue
    for it in root.iter("item"):
        title = html.unescape((it.findtext("title") or "").strip())
        src = (it.find("source").text if it.find("source") is not None else "") or ""
        if src and title.endswith(" - " + src): title = title[: -len(" - " + src)]
        link = (it.findtext("link") or "").strip()
        try: when = parsedate_to_datetime(it.findtext("pubDate")).astimezone(timezone.utc)
        except Exception: continue
        key = re.sub(r"\W+", "", title.lower())[:60]
        if not title or not link or key in seen or BLOCK.search(title): continue
        if not re.search(r"gta ?(6|vi)|grand theft auto (6|vi)", title, re.I): continue
        if when < datetime.now(timezone.utc) - timedelta(days=7): continue
        seen.add(key); items.append({"t": title[:140], "s": src[:40], "u": link, "d": when.strftime("%Y-%m-%d")})
items.sort(key=lambda x: x["d"], reverse=True)
out = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "items": items[:20]}
path = os.path.join(SITE, "headlines.json")
old = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
oldi = json.loads(old)["items"] if old else None
if items and oldi != out["items"]:
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=0); print("changed", len(items))
else:
    print("unchanged", len(items))
