"""Animate one of OUR images into a short clip with a public Hugging Face Wan 2.2 Space (free, ZeroGPU quota).
  python -I tools/hfvideo.py <image.jpg> <out.mp4> "<motion prompt>" [seconds]
Only feed it original GamerBhai art (tools/bg, promo/ai) - never Rockstar screenshots.
"""
import base64, json, os, sys, urllib.request
BASE = "https://prithivmlmods-wan2-2-fast.hf.space/gradio_api"
TOK = os.environ.get("HF_TOKEN")  # set by the owner on this PC (never commit it); gives far more free ZeroGPU quota
AUTH = {"Authorization": "Bearer " + TOK} if TOK else {}
img, out, prompt = sys.argv[1], sys.argv[2], sys.argv[3]
secs = float(sys.argv[4]) if len(sys.argv) > 4 else 4.0
b64 = base64.b64encode(open(img, "rb").read()).decode()
neg = "blurry, low quality, deformed, watermark, text, logo, people, faces, shaky camera"
body = json.dumps({"data": [b64, prompt, 6, neg, secs, 1.0, 1.0, 42, True]}).encode()
req = urllib.request.Request(BASE + "/call/generate_video", data=body, headers={"Content-Type": "application/json", **AUTH})
ev = json.load(urllib.request.urlopen(req, timeout=120))["event_id"]
stream = urllib.request.urlopen(urllib.request.Request(BASE + "/call/generate_video/" + ev, headers=AUTH), timeout=600).read().decode()
data = None; last = ""
for line in stream.splitlines():
    if line.startswith("event:"): last = line[6:].strip()
    if line.startswith("data:") and last == "complete": data = json.loads(line[5:])
if not data:
    print("FAILED", stream[-500:]); sys.exit(1)
v = data[0]
if isinstance(v, dict) and "video" in v: v = v["video"]
url = v.get("url") if isinstance(v, dict) else None
if not url and isinstance(v, dict) and v.get("path"): url = BASE + "/file=" + v["path"]
open(out, "wb").write(urllib.request.urlopen(url, timeout=300).read()); print("saved", out)
