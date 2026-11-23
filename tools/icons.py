from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
def font(sz):
    for f in ["C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/segoeuib.ttf"]:
        if os.path.exists(f): return ImageFont.truetype(f,sz)
def make(N, pad=0):
    im=Image.new("RGB",(N,N),"#12061f"); d=ImageDraw.Draw(im)
    for y in range(N):
        t=y/N; d.line([(0,y),(N,y)],fill=(int(40+200*t*.9),int(10+20*t),int(90-40*t)))
    r=int(N*(.5-pad)); c=N//2
    d.ellipse([c-r*.8,c-r*.25,c+r*.8,c+r*1.35],fill=(255,120,60))
    for i,yy in enumerate(range(int(c+r*.45),int(c+r*1.4),max(2,N//26))): d.rectangle([0,yy,N,yy+max(1,N//64)+i*max(1,N//256)],fill=(30,8,50))
    g=Image.new("RGBA",(N,N),(0,0,0,0)); gd=ImageDraw.Draw(g); f=font(int(N*.46*(1-pad*1.6)))
    w=gd.textlength("GB",font=f); gd.text(((N-w)/2,N*.18+N*pad*.5),"GB",font=f,fill=(255,63,164,255))
    g=g.filter(ImageFilter.GaussianBlur(N/40)); im.paste(g,(0,0),g)
    d.text(((N-w)/2,N*.18+N*pad*.5),"GB",font=f,fill=(255,255,255))
    return im
os.makedirs("img/icons",exist_ok=True)
for n in (192,512): make(n).save(f"img/icons/icon-{n}.png")
make(512,pad=.1).save("img/icons/maskable-512.png")
make(180).save("img/icons/apple-touch-icon.png")
make(64).save("favicon.ico",sizes=[(16,16),(32,32),(48,48),(64,64)])
print("ok")
