"""Call a public Hugging Face Gradio Space over HTTP (no extra packages) and save the image."""
import json, sys, urllib.request
BASE = "https://mcp-tools-qwen-image.hf.space/gradio_api"
def call(prompt, ratio, out, neg="watermark, blurry, low resolution, misspelled text, extra text, real brand logos, people, faces"):
    body = json.dumps({"data": [prompt, 0, True, ratio, neg, 4, 16]}).encode()
    req = urllib.request.Request(BASE + "/call/generate_image", data=body, headers={"Content-Type": "application/json"})
    ev = json.load(urllib.request.urlopen(req, timeout=60))["event_id"]
    stream = urllib.request.urlopen(BASE + "/call/generate_image/" + ev, timeout=300).read().decode()
    data = None; last_event = ""
    for line in stream.splitlines():
        if line.startswith("event:"): last_event = line[6:].strip()
        if line.startswith("data:") and last_event == "complete": data = json.loads(line[5:])
    if not data:
        print("FAILED", stream[-400:]); return False
    img = data[0]
    url = img.get("url") if isinstance(img, dict) else None
    if not url and isinstance(img, dict) and img.get("path"): url = BASE.replace("/gradio_api", "") + "/gradio_api/file=" + img["path"]
    open(out, "wb").write(urllib.request.urlopen(url, timeout=120).read()); print("saved", out); return True

jobs = json.loads(open(sys.argv[1], encoding="utf-8").read())
for j in jobs: call(j["prompt"], j["ratio"], j["out"])
