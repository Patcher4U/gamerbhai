from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, random, sys, subprocess, shutil
OUT = sys.argv[1]
def F(sz, b=True):
    return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if b else "C:/Windows/Fonts/arial.ttf", sz)
PINK=(255,63,164); CYAN=(41,240,255); ORANGE=(255,178,59); WHITE=(246,240,255); MUTED=(195,180,217); BG=(18,6,31)
CHEATS=[("$250,000","↑ → ↓ ← ↑ ← ↓ →","Finish the story"),("Unlimited Focus","↓ ↑ ↑ ↓ ↑ ↓ ↑ ↓ ↑ →","Finish the story"),("Attack Force","↓ ↑ ← ← → ↓ ↓ ↑ ↓","Finish the story"),("Cycle Weather","↓ → ↑ ↓ → ↑ →","Finish the story"),
 ("Body Armor","↓ ↑ ← ↑ ↑ ↑ ↑ ↑ ↓ ↓","100 workouts"),("Raise Heat","← ↓ → ↓ ↑ ↓ ↑","Lose 3 stars x25"),("Exploding Balls","↓ ↑ ← ← → ↓ ↓ ↑ →","20 explosive hits"),("Vehicle Force","↓ ↑ ← ← → ↓ ← ↑ ↓","25 vehicle kills"),
 ("Max Ammo","↓ ↑ → ↓ ← ← ↑ ↑ ↓ ←","25 bronze medals"),("Infinite Ammo","↓ ↑ → ↓ ← ← ↑ ↓ ↓ ↓","25 silver medals"),("No Reload","↓ ↑ → ↓ ← ← ↑ ↓ ↓ ↑","25 gold medals"),("Boomazoom","← ↑ → ↓ ← ← ↑ ←","5 shopping challenges"),
 ("Fire Truck","← ↑ → ↓ ← → → ↑","Discover it"),("Bulldozer","← ↑ → ↓ ← → → ↓","Discover it"),("Cataclysm","↓ ↓ ↑ → → ↑ ← ← → →","Discover Martha's Vamos"),("Dollhouse","↓ ↓ ↑ → → ↑ ← ← ↓ →","8 hrs with partner"),("Faded Glory","↓ ↓ ↑ → → ↑ ← ← ← →","Rob 50 stores w/ partner")]
def bg(W,H,seed=3):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=(int(18+70*t),int(6+8*t),int(31+45*(1-t))))
    random.seed(seed); x=0
    while x<W:
        w=random.randint(50,110); h=random.randint(int(H*.06),int(H*.18)); d.rectangle([x,H-h,x+w,H],fill=(12,4,24))
        for wy in range(H-h+14,H-10,22):
            for wx in range(x+8,x+w-8,16):
                if random.random()<.3: d.rectangle([wx,wy,wx+6,wy+8],fill=random.choice([PINK,CYAN,ORANGE]))
        x+=w+4
    return im
def glow_text(im,xy,txt,f,col,anchor="la",blur=12):
    g=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(g).text(xy,txt,font=f,fill=col+(255,),anchor=anchor)
    g=g.filter(ImageFilter.GaussianBlur(blur)); im.paste(g,(0,0),g); ImageDraw.Draw(im).text(xy,txt,font=f,fill=WHITE,anchor=anchor)
def brand(im,y):
    d=ImageDraw.Draw(im); W=im.size[0]; f=F(40)
    w=d.textlength("gamerbhai.com",font=f); d.rounded_rectangle([(W-w)/2-34,y,(W+w)/2+34,y+76],radius=38,fill=PINK); d.text((W/2,y+38),"gamerbhai.com",font=f,fill=WHITE,anchor="mm")

def foot(im,y,txt):
    d=ImageDraw.Draw(im); f=F(26,False); W=im.size[0]; w=d.textlength(txt,font=f)
    d.rounded_rectangle([(W-w)/2-24,y-10,(W+w)/2+24,y+44],radius=20,fill=(12,4,24)); d.text((W/2,y),txt,font=f,fill=WHITE,anchor="mt")

# 1) cheat card
W,H=1080,1350; im=bg(W,H); d=ImageDraw.Draw(im)
glow_text(im,(W/2,70),"GTA 6 CHEAT CODES",F(70),PINK,"mt")
d.text((W/2,160),"17 confirmed  •  PS5: hold L1+R1  •  Xbox: hold LB+RB",font=F(30,False),fill=CYAN,anchor="mt")
y=212
for i,(n,c,u) in enumerate(CHEATS):
    if i%2==0: d.rounded_rectangle([40,y-6,W-40,y+52],radius=12,fill=(40,18,64))
    d.text((60,y+23),n,font=F(29),fill=WHITE,anchor="lm"); d.text((395,y+23),c,font=F(30),fill=ORANGE,anchor="lm"); d.text((W-60,y+23),u,font=F(22,False),fill=MUTED,anchor="rm")
    y+=58
foot(im,y+14,"Phone up (D-pad ↑) first. Cheats turn off trophies & saving.")
brand(im,H-100); im.save(os.path.join(OUT,"gta6-cheats-card.png"))

# 2) money card
MONEY=[("CH 1","Raid illegal operations","Best early cash"),("CH 1","Kenton's treasure dives","~$1,000+ / wreck"),("CH 1-2","Sell cars to Moses","~$1,000 / car"),("CH 2","Hunting for Bret Vogel","$500 - few $K"),
 ("ANY","Demolition derby","$3.8K - $6.3K"),("CH 2-3","Yasmani jewelry jobs","$10K - $25K"),("CH 3","Randy's car thefts","$30K+ / car"),("CH 3","Small banks","$5K - $45K"),("CH 4","Pilot Pete air drops","$10K - $20K"),("LATE CH 4","Big bank vaults","up to $205K")]
im=bg(W,H,9); d=ImageDraw.Draw(im)
glow_text(im,(W/2,70),"GTA 6 MONEY GUIDE",F(72),ORANGE,"mt"); d.text((W/2,165),"Fastest cash in every chapter",font=F(34,False),fill=CYAN,anchor="mt")
y=225
for i,(c,m,p) in enumerate(MONEY):
    d.rounded_rectangle([40,y,W-40,y+80],radius=14,fill=(40,18,64) if i%2==0 else (30,12,50))
    d.text((70,y+40),c,font=F(24),fill=PINK,anchor="lm"); d.text((250,y+40),m,font=F(33),fill=WHITE,anchor="lm"); d.text((W-70,y+40),p,font=F(28),fill=ORANGE,anchor="rm"); y+=90
foot(im,y+12,"Tip: bank your cash (ATM / BuckMe) - you lose pocket cash if busted.")
brand(im,H-100); im.save(os.path.join(OUT,"gta6-money-card.png"))

import sys as _s
if len(_s.argv)>2: raise SystemExit(0)
# 3) vertical short
SW,SH=1080,1920
def slide(title, lines, col=PINK, seed=1):
    im=bg(SW,SH,seed); d=ImageDraw.Draw(im)
    glow_text(im,(SW/2,300),title,F(86),col,"mm")
    y=560
    for a,b in lines:
        d.rounded_rectangle([60,y-60,SW-60,y+90],radius=22,fill=(40,18,64))
        d.text((SW/2,y-18),a,font=F(44),fill=WHITE,anchor="mm"); d.text((SW/2,y+42),b,font=F(50),fill=ORANGE,anchor="mm"); y+=200
    brand(im,SH-260); return im
slides=[]
im=bg(SW,SH,5); glow_text(im,(SW/2,700),"17 GTA 6",F(150),PINK,"mm"); glow_text(im,(SW/2,880),"CHEATS",F(170),ORANGE,"mm"); glow_text(im,(SW/2,1060),"THAT WORK",F(110),CYAN,"mm")
ImageDraw.Draw(im).text((SW/2,1220),"PS5 + Xbox Series X|S",font=F(48,False),fill=WHITE,anchor="mm"); slides.append((im,2.8))
slides.append((slide("HOW TO ENTER",[("1. D-pad UP","open the phone"),("2. Hold L1 + R1","Xbox: LB + RB"),("3. Type the code","on the D-pad")],col=CYAN,seed=2),4))
for k,grp in [(1,CHEATS[0:4]),(5,CHEATS[4:8]),(9,CHEATS[8:12]),(13,CHEATS[12:17])]:
    slides.append((slide(f"CHEATS {k}-{k+len(grp)-1}",[(n+"  ("+u+")",c) for n,c,u in grp],seed=10+k),5.5))
im=bg(SW,SH,7); d=ImageDraw.Draw(im); glow_text(im,(SW/2,640),"WARNING",F(120),PINK,"mm")
for i,t in enumerate(["Cheats turn OFF trophies","You can't save while active","Save first, then reload"]): d.text((SW/2,860+i*110),t,font=F(54),fill=WHITE,anchor="mm")
brand(im,SH-260); slides.append((im,3.2))
im=bg(SW,SH,8); d=ImageDraw.Draw(im); glow_text(im,(SW/2,640),"FULL LIST +",F(100),CYAN,"mm"); glow_text(im,(SW/2,780),"MONEY GUIDE",F(100),ORANGE,"mm")
for i,t in enumerate(["100% tracker  •  119 mission videos","Free racing game  •  $100 lucky draw"]): d.text((SW/2,960+i*90),t,font=F(46,False),fill=WHITE,anchor="mm")
glow_text(im,(SW/2,1250),"gamerbhai.com",F(110),PINK,"mm"); slides.append((im,4))
frames=os.path.join(OUT,"_frames"); os.makedirs(frames,exist_ok=True)
fps=30; n=0
for idx,(s,dur) in enumerate(slides):
    nxt=slides[idx+1][0] if idx+1<len(slides) else None
    total=int(dur*fps)
    for f in range(total):
        z=1+0.04*f/total
        fr=s.resize((int(SW*z),int(SH*z))); l=(fr.size[0]-SW)//2; t=(fr.size[1]-SH)//2; fr=fr.crop((l,t,l+SW,t+SH))
        if nxt is not None and f>total-8: fr=Image.blend(fr,nxt,(f-(total-8))/8)
        fr.save(os.path.join(frames,f"{n:05d}.jpg"),quality=90); n+=1
mp4=os.path.join(OUT,"gta6-cheats-short.mp4")
subprocess.run(["C:/ffmpeg/bin/ffmpeg.exe","-y","-loglevel","error","-framerate",str(fps),"-i",os.path.join(frames,"%05d.jpg"),
  "-f","lavfi","-t",str(n/fps),"-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-crf","22","-c:a","aac",mp4],check=True)
shutil.rmtree(frames)
print("frames",n,"secs",round(n/fps,1),"mp4",os.path.getsize(mp4))
