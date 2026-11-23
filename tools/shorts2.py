from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, random, sys, subprocess, shutil
OUT = sys.argv[1]
def F(sz, b=True): return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if b else "C:/Windows/Fonts/arial.ttf", sz)
PINK=(255,63,164); CYAN=(41,240,255); ORANGE=(255,178,59); WHITE=(246,240,255); MUTED=(195,180,217); BG=(18,6,31); GREEN=(109,255,154)
SW,SH=1080,1920
def bg(seed=3):
    im=Image.new("RGB",(SW,SH),BG); d=ImageDraw.Draw(im)
    for y in range(SH):
        t=y/SH; d.line([(0,y),(SW,y)],fill=(int(18+70*t),int(6+8*t),int(31+45*(1-t))))
    random.seed(seed); x=0
    while x<SW:
        w=random.randint(50,110); h=random.randint(110,330); d.rectangle([x,SH-h,x+w,SH],fill=(12,4,24))
        for wy in range(SH-h+14,SH-10,22):
            for wx in range(x+8,x+w-8,16):
                if random.random()<.3: d.rectangle([wx,wy,wx+6,wy+8],fill=random.choice([PINK,CYAN,ORANGE]))
        x+=w+4
    return im
def glow(im,xy,txt,f,col,anchor="mm",blur=12):
    g=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(g).text(xy,txt,font=f,fill=col+(255,),anchor=anchor)
    g=g.filter(ImageFilter.GaussianBlur(blur)); im.paste(g,(0,0),g); ImageDraw.Draw(im).text(xy,txt,font=f,fill=WHITE,anchor=anchor)
def brand(im):
    d=ImageDraw.Draw(im); f=F(40); w=d.textlength("gamerbhai.com",font=f); y=SH-260
    d.rounded_rectangle([(SW-w)/2-34,y,(SW+w)/2+34,y+76],radius=38,fill=PINK); d.text((SW/2,y+38),"gamerbhai.com",font=f,fill=WHITE,anchor="mm")
def title_slide(lines, sub, seed):
    im=bg(seed); y=700
    for txt,size,col in lines: glow(im,(SW/2,y),txt,F(size),col); y+=size+40
    ImageDraw.Draw(im).text((SW/2,y+40),sub,font=F(48,False),fill=WHITE,anchor="mm"); return im
def rows_slide(title, rows, seed, col=PINK):
    im=bg(seed); d=ImageDraw.Draw(im); glow(im,(SW/2,300),title,F(80),col); y=520
    for a,b in rows:
        d.rounded_rectangle([60,y-60,SW-60,y+90],radius=22,fill=(40,18,64))
        d.text((SW/2,y-18),a,font=F(46),fill=WHITE,anchor="mm"); d.text((SW/2,y+42),b,font=F(48),fill=ORANGE,anchor="mm"); y+=190
    brand(im); return im
def text_slide(title, lines, seed, col=PINK):
    im=bg(seed); d=ImageDraw.Draw(im); glow(im,(SW/2,620),title,F(110),col)
    for i,t in enumerate(lines): d.text((SW/2,840+i*105),t,font=F(52),fill=WHITE,anchor="mm")
    brand(im); return im
def cta(seed):
    im=bg(seed); d=ImageDraw.Draw(im); glow(im,(SW/2,640),"FULL GUIDE",F(110),CYAN); glow(im,(SW/2,790),"FREE ON",F(90),ORANGE)
    glow(im,(SW/2,1000),"gamerbhai.com",F(110),PINK)
    for i,t in enumerate(["Cheats • Money • 100% tracker","119 mission videos • Free racing game"]): d.text((SW/2,1180+i*80),t,font=F(44,False),fill=WHITE,anchor="mm")
    return im
def render(name, slides):
    frames=os.path.join(OUT,"_f"); os.makedirs(frames,exist_ok=True); fps=30; n=0
    for i,(s,dur) in enumerate(slides):
        nxt=slides[i+1][0] if i+1<len(slides) else None; total=int(dur*fps)
        for f in range(total):
            z=1+0.04*f/total; fr=s.resize((int(SW*z),int(SH*z))); l=(fr.size[0]-SW)//2; t=(fr.size[1]-SH)//2; fr=fr.crop((l,t,l+SW,t+SH))
            if nxt is not None and f>total-8: fr=Image.blend(fr,nxt,(f-(total-8))/8)
            fr.save(os.path.join(frames,f"{n:05d}.jpg"),quality=90); n+=1
    mp4=os.path.join(OUT,name)
    subprocess.run(["C:/ffmpeg/bin/ffmpeg.exe","-y","-loglevel","error","-framerate",str(fps),"-i",os.path.join(frames,"%05d.jpg"),"-f","lavfi","-t",str(n/fps),"-i","anullsrc=r=44100:cl=stereo","-shortest",
        "-c:v","libx264","-crf","27","-preset","slow","-pix_fmt","yuv420p","-c:a","aac","-b:a","64k",mp4],check=True)
    shutil.rmtree(frames); print(name, round(n/fps,1),"s", os.path.getsize(mp4))

# A) money
render("short-2-money.mp4",[
 (title_slide([("BROKE IN",130,PINK),("LEONIDA?",150,ORANGE)],"Fastest money in GTA 6, chapter by chapter",21),2.8),
 (rows_slide("CHAPTER 1-2",[("Raid illegal operations","best early cash"),("Kenton's treasure dives","~$1,000+ per wreck"),("Sell cars to Moses","~$1,000 per car"),("Hunt for Bret Vogel","$500 - a few $K")],22),5.5),
 (rows_slide("CHAPTER 2-3",[("Demolition derby","$3.8K - $6.3K a win"),("Yasmani jewelry jobs","$10K - $25K"),("Randy's car thefts","$30K+ per car"),("Small banks","$5K - $45K")],23,ORANGE),5.5),
 (rows_slide("CHAPTER 4",[("Pilot Pete air drops","$10K - $20K"),("Big bank vaults","up to $205,000 each")],24,CYAN),4.5),
 (text_slide("PRO TIP",["Bank your cash often","(ATM or BuckMe app)","Busted = pocket cash gone"],25,GREEN),3.5),
 (cta(26),3.5)])
# B) PC
render("short-3-pc.mp4",[
 (title_slide([("IS GTA 6",130,CYAN),("ON PC?",160,PINK)],"The real answer (Nov 2026)",31),2.8),
 (text_slide("NOT YET",["Only PS5 + Xbox Series X|S","Rockstar has NOT announced","a PC version"],32,PINK),4),
 (text_slide("THE RUMOR",["GamesBeat report (Oct 2026):","PC in early 2027","Not confirmed by Rockstar"],33,ORANGE),4),
 (rows_slide("PAST GAMES",[("GTA IV","PC 7 months later"),("GTA V","PC 19 months later"),("Red Dead 2","PC 12 months later")],34,CYAN),5),
 (text_slide("BEWARE",["Any 'GTA 6 PC download'","right now is a SCAM","or malware"],35,PINK),3.5),
 (cta(36),3.5)])
# C) 100% tracker
render("short-4-collectibles.mp4",[
 (title_slide([("GTA 6",140,PINK),("100%",190,ORANGE),("CHECKLIST",110,CYAN)],"Collectibles that unlock cheats",41),2.8),
 (rows_slide("COLLECTIBLES",[("Vice City Flamingos cards","24 to find"),("Girlypop vehicles","16 to find"),("Collectible watches","20 to find"),("Cocaine flamingos","50 to destroy")],42),5.5),
 (rows_slide("CHEAT GOALS",[("Workouts","100 = Body Armor"),("Stunt jumps","50 = Unlimited Nitrous"),("Range medals","25 = Max Ammo"),("Skydives 300ft+","50 = Parachute")],43,ORANGE),5.5),
 (text_slide("TRACK IT FREE",["Tick off every item","Progress saves in your browser","No account needed"],44,GREEN),3.5),
 (cta(45),3.5)])
