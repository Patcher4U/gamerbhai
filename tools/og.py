from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys
W,H=1200,630
im=Image.new("RGB",(W,H),"#12061f"); d=ImageDraw.Draw(im)
# sunset gradient sky
for y in range(H):
    t=y/H; r=int(18+(255-18)*max(0,1-abs(t-.62)*2.2)*.9); g=int(6+60*max(0,1-abs(t-.62)*3)); b=int(31+90*(1-t))
    d.line([(0,y),(W,y)],fill=(min(r,255),g,b))
# sun
sun=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sun)
sd.ellipse([780,170,1100,490],fill=(255,120,60,255))
for i,y in enumerate(range(340,490,18)): sd.rectangle([770,y,1110,y+4+i],fill=(0,0,0,0))
im.paste(sun,(0,0),sun)
# skyline
import random; random.seed(6)
x=0
while x<W:
    w=random.randint(40,90); h=random.randint(80,260)
    d.rectangle([x,H-h,x+w,H],fill=(14,6,30))
    for wy in range(H-h+12,H-10,18):
        for wx in range(x+8,x+w-8,14):
            if random.random()<.35: d.rectangle([wx,wy,wx+5,wy+7],fill=random.choice([(255,63,164),(41,240,255),(255,178,59)]))
    x+=w+random.randint(0,6)
def font(sz,bold=True):
    for f in ["C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf","C:/Windows/Fonts/segoeuib.ttf"]:
        if os.path.exists(f): return ImageFont.truetype(f,sz)
    return ImageFont.load_default()
glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
gd.text((70,90),"GAMERBHAI",font=font(118),fill=(255,63,164,255))
glow=glow.filter(ImageFilter.GaussianBlur(14)); im.paste(glow,(0,0),glow)
d.text((70,90),"GAMERBHAI",font=font(118),fill=(255,255,255))
d.text((74,232),"GTA 6 GUIDES • MAP • CHEATS • COMMUNITY",font=font(34),fill=(41,240,255))
d.text((74,292),"Free mini-game  •  Leaderboard  •  $100 lucky draw",font=font(30,False),fill=(246,240,255))
d.rounded_rectangle([70,360,420,425],radius=32,fill=(255,63,164))
d.text((100,372),"gamerbhai.com",font=font(36),fill=(255,255,255))
im.save(sys.argv[1],"JPEG",quality=86); print(os.path.getsize(sys.argv[1]))
