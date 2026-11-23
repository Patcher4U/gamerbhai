"""Render GamerBhai Shorts from tools/shorts_bank.json - no AI, runs on Windows or Linux (GitHub Actions).

  python tools/render_short.py --next 7 --out promo/queue      # render the next 7 not-yet-rendered Shorts
  python tools/render_short.py --id cheats-player --out promo/queue

Writes <id>.mp4 plus <id>.txt (title / description ready to paste) and records ids in tools/shorts_state.json.
Needs Pillow and ffmpeg (FFMPEG env var, C:/ffmpeg/bin/ffmpeg.exe, or ffmpeg on PATH).
"""
import argparse, json, os, random, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "shorts_bank.json")
STATE = os.path.join(HERE, "shorts_state.json")
C = {"pink": (255, 63, 164), "cyan": (41, 240, 255), "orange": (255, 178, 59), "green": (109, 255, 154), "white": (246, 240, 255)}
BG = (18, 6, 31); SW, SH = 1080, 1920

def font_path(bold):
    for p in (["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
              ["C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]):
        if os.path.exists(p): return p
    raise SystemExit("no font found")
def F(sz, b=True): return ImageFont.truetype(font_path(b), sz)
def fit(d, txt, size, maxw, bold=True):
    while size > 20 and d.textlength(txt, font=F(size, bold)) > maxw: size -= 4
    return F(size, bold)

def bg(seed):
    im = Image.new("RGB", (SW, SH), BG); d = ImageDraw.Draw(im)
    for y in range(SH):
        t = y / SH; d.line([(0, y), (SW, y)], fill=(int(18 + 70 * t), int(6 + 8 * t), int(31 + 45 * (1 - t))))
    random.seed(seed); x = 0
    while x < SW:
        w = random.randint(50, 110); h = random.randint(110, 330); d.rectangle([x, SH - h, x + w, SH], fill=(12, 4, 24))
        for wy in range(SH - h + 14, SH - 10, 22):
            for wx in range(x + 8, x + w - 8, 16):
                if random.random() < .3: d.rectangle([wx, wy, wx + 6, wy + 8], fill=random.choice([C["pink"], C["cyan"], C["orange"]]))
        x += w + 4
    return im
def glow(im, xy, txt, size, col):
    d = ImageDraw.Draw(im); f = fit(d, txt, size, SW - 100)
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text(xy, txt, font=f, fill=col + (255,), anchor="mm")
    g = g.filter(ImageFilter.GaussianBlur(12)); im.paste(g, (0, 0), g); d.text(xy, txt, font=f, fill=C["white"], anchor="mm")
def brand(im):
    d = ImageDraw.Draw(im); f = F(40); w = d.textlength("gamerbhai.com", font=f); y = SH - 260
    d.rounded_rectangle([(SW - w) / 2 - 34, y, (SW + w) / 2 + 34, y + 76], radius=38, fill=C["pink"]); d.text((SW / 2, y + 38), "gamerbhai.com", font=f, fill=C["white"], anchor="mm")

def slide(s, seed):
    kind = s[0]; im = bg(seed); d = ImageDraw.Draw(im)
    if kind == "title":
        y = 700
        for txt, size, col in s[1]: glow(im, (SW / 2, y), txt, size, C[col]); y += size + 40
        d.text((SW / 2, y + 40), s[2], font=fit(d, s[2], 48, SW - 120, False), fill=C["white"], anchor="mm")
        return im, 2.8
    if kind == "rows":
        glow(im, (SW / 2, 300), s[1], 84, C["pink"]); y = 520
        for a, b in s[2]:
            d.rounded_rectangle([60, y - 60, SW - 60, y + 90], radius=22, fill=(40, 18, 64))
            d.text((SW / 2, y - 18), a, font=fit(d, a, 46, SW - 160), fill=C["white"], anchor="mm")
            d.text((SW / 2, y + 42), b, font=fit(d, b, 50, SW - 160), fill=C["orange"], anchor="mm"); y += 190
        brand(im); return im, 2.2 + 1.2 * len(s[2])
    if kind == "text":
        glow(im, (SW / 2, 620), s[1], 110, C["cyan"])
        for i, t in enumerate(s[2]): d.text((SW / 2, 840 + i * 105), t, font=fit(d, t, 52, SW - 120), fill=C["white"], anchor="mm")
        brand(im); return im, 2.0 + 0.8 * len(s[2])
    # cta
    glow(im, (SW / 2, 640), "FULL GUIDE", 110, C["cyan"]); glow(im, (SW / 2, 790), "FREE ON", 90, C["orange"])
    glow(im, (SW / 2, 1000), "gamerbhai.com", 110, C["pink"])
    for i, t in enumerate(["Cheats • Money • 100% tracker", "119 mission videos • Free racing game"]):
        d.text((SW / 2, 1180 + i * 80), t, font=F(44, False), fill=C["white"], anchor="mm")
    return im, 3.5

def ffmpeg():
    return os.environ.get("FFMPEG") or ("C:/ffmpeg/bin/ffmpeg.exe" if os.path.exists("C:/ffmpeg/bin/ffmpeg.exe") else "ffmpeg")

def render(item, out):
    slides = [slide(s, hash(item["id"] + str(i)) % 1000) for i, s in enumerate(item["slides"])]
    frames = os.path.join(out, "_f_" + item["id"]); os.makedirs(frames, exist_ok=True); fps = 30; n = 0
    for i, (s, dur) in enumerate(slides):
        nxt = slides[i + 1][0] if i + 1 < len(slides) else None; total = int(dur * fps)
        for f in range(total):
            z = 1 + 0.04 * f / total; fr = s.resize((int(SW * z), int(SH * z))); l = (fr.size[0] - SW) // 2; t = (fr.size[1] - SH) // 2
            fr = fr.crop((l, t, l + SW, t + SH))
            if nxt is not None and f > total - 8: fr = Image.blend(fr, nxt, (f - (total - 8)) / 8)
            fr.save(os.path.join(frames, f"{n:05d}.jpg"), quality=88); n += 1
    mp4 = os.path.join(out, item["id"] + ".mp4")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-framerate", str(fps), "-i", os.path.join(frames, "%05d.jpg"), "-f", "lavfi", "-t", str(n / fps),
                    "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:v", "libx264", "-crf", "27", "-preset", "slow", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "64k", mp4], check=True)
    shutil.rmtree(frames)
    desc = f"{item['title'].replace(' #shorts', '')}.\n\nFree on GamerBhai: {item['link']}\n\n{item['tags']}"
    open(os.path.join(out, item["id"] + ".txt"), "w", encoding="utf-8").write(f"TITLE: {item['title']}\n\nDESCRIPTION:\n{desc}\n")
    print(f"{item['id']}: {round(n / fps, 1)} s, {os.path.getsize(mp4) // 1024} KB")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--next", type=int, default=0); ap.add_argument("--id"); ap.add_argument("--out", default="promo/queue")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    bank = json.load(open(BANK, encoding="utf-8"))
    state = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {"rendered": []}
    todo = [b for b in bank if b["id"] == a.id] if a.id else [b for b in bank if b["id"] not in state["rendered"]][:a.next]
    if not todo: print("nothing left to render - add more items to shorts_bank.json"); return
    for item in todo:
        render(item, a.out)
        if item["id"] not in state["rendered"]: state["rendered"].append(item["id"])
    json.dump(state, open(STATE, "w", encoding="utf-8"), indent=1)
    print("left in bank:", len([b for b in bank if b["id"] not in state["rendered"]]))

if __name__ == "__main__": main()
