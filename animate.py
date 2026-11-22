from PIL import Image, ImageDraw, ImageFont
import math, os, subprocess
import imageio_ffmpeg
W,H=540,960; FPS=30; DUR=7.2
os.makedirs('frames',exist_ok=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def ease(t): return t*t*(3-2*t)
def frame(t):
    im=Image.new('RGB',(W,H),(15,21,49)); d=ImageDraw.Draw(im)
    # theatrical backlit forest; layered silhouettes
    for y in range(H):
        q=y/H; col=(int(13+22*q),int(20+17*q),int(48+12*q)); d.line((0,y,W,y),fill=col)
    # aureole and moon
    d.ellipse((340,115,495,270),fill=(55,55,89)); d.ellipse((365,138,470,243),fill=(250,203,119))
    for x,y,r in [(60,280,3),(285,145,2),(465,370,3),(110,490,2),(410,510,2)]:
        d.ellipse((x-r,y-r,x+r,y+r),fill=(244,201,124))
    # distant trees
    for x in [-20,50,460,510]:
        d.polygon([(x-85,620),(x,210+(x%3)*20),(x+100,620)],fill=(20,42,53))
        d.rectangle((x-9,550,x+10,920),fill=(25,35,48))
    # stage ground
    d.rectangle((0,800,W,H),fill=(30,25,42)); d.line((0,800,W,800),fill=(211,145,74),width=3)
    # Lakshmana puppet body, scale+lean expressive
    bob=math.sin(t*2.3)*5
    cx=275+int(5*math.sin(t*1.1)); cy=510+int(bob)
    # shadow behind and ornate body
    d.ellipse((cx-115,770,cx+120,805),fill=(10,15,31))
    # legs
    d.polygon([(cx-58,650),(cx+45,650),(cx+80,770),(cx+20,770),(cx-5,700),(cx-28,770),(cx-89,770)],fill=(111,48,47),outline=(18,18,32),width=5)
    # dhoti folds
    d.polygon([(cx-54,659),(cx+46,659),(cx+8,719),(cx-15,695),(cx-38,725)],fill=(220,161,69),outline=(34,24,31),width=3)
    # torso
    d.polygon([(cx-57,430),(cx+56,430),(cx+73,654),(cx-73,654)],fill=(184,80,54),outline=(18,18,32),width=6)
    d.polygon([(cx-50,443),(cx+3,457),(cx+62,435),(cx+45,486),(cx-28,486)],fill=(237,181,76),outline=(34,24,31),width=3)
    # punched leather dots
    for yy in range(466,633,22):
      for xx in [cx-48,cx+48]: d.ellipse((xx-2,yy-2,xx+2,yy+2),fill=(248,199,105))
    # head, hair and crown
    d.ellipse((cx-50,321,cx+48,425),fill=(181,105,68),outline=(20,18,30),width=6)
    d.pieslice((cx-57,312,cx+53,386),180,355,fill=(34,26,35),outline=(16,17,29),width=4)
    d.polygon([(cx-35,330),(cx-18,278),(cx+1,321),(cx+19,276),(cx+38,332)],fill=(224,168,71),outline=(18,18,30),width=5)
    d.line((cx-2,342,cx-2,374),fill=(238,196,118),width=3); d.ellipse((cx+17,361,cx+24,368),fill=(23,22,32))
    # bow fixed at rear
    d.arc((cx+57,410,cx+190,675),270,90,fill=(231,174,82),width=8); d.line((cx+123,410,cx+123,674),fill=(239,208,152),width=2)
    # articulated near arm: shoulder->hinged forearm rotates at elbow
    d.line((cx-53,454,cx-95,536),fill=(179,102,67),width=24); d.line((cx-53,454,cx-95,536),fill=(24,20,31),width=4)
    jx,jy=cx-95,536
    phase=max(0,min(1,(t-1.05)/1.25)); ang=math.radians(-72*ease(phase) + (12*math.sin(t*2.1) if t>2.3 else 0))
    ex=jx+int(111*math.sin(ang)); ey=jy-int(111*math.cos(ang))
    d.line((jx,jy,ex,ey),fill=(190,111,72),width=23); d.line((jx,jy,ex,ey),fill=(24,20,31),width=4)
    d.ellipse((jx-12,jy-12,jx+12,jy+12),fill=(232,177,82),outline=(24,20,31),width=3)
    d.ellipse((ex-12,ey-12,ex+12,ey+12),fill=(179,102,67),outline=(24,20,31),width=3)
    # drifting golden sleep motif, released from hand, swirls upward
    p=max(0,(t-2.0)/4.5); sx=ex+30+int(28*math.sin(t*1.6)); sy=int(ey-60-p*150)
    for k in range(3):
      rr=13-k*3; ox=int(math.sin(t*2+k)*16)
      d.ellipse((sx+ox-rr,sy-k*28-rr,sx+ox+rr,sy-k*28+rr),outline=(248,207,124),width=3)
    # caption plate
    cap='FOR FOURTEEN YEARS' if t<2.05 else ('LAKSHMANA NEVER SLEPT.' if t<3.65 else 'SO WHO CARRIED HIS SLEEP?')
    f=ImageFont.truetype(font,24 if len(cap)>23 else 27)
    box=d.textbbox((0,0),cap,font=f); tw=box[2]-box[0]
    d.rounded_rectangle((20,82,W-20,150),radius=16,fill=(10,14,31),outline=(213,164,90),width=2)
    d.text(((W-tw)//2,102),cap,font=f,fill=(255,232,184),stroke_width=0)
    # end punctuation card treatment, no extra narration
    return im
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
proc=subprocess.Popen([ffmpeg,'-y','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-i','audio/voiceover.mp3','-t',str(DUR),'-vf','scale=1080:1920:flags=lanczos,format=yuv420p','-c:v','libx264','-preset','medium','-crf','20','-c:a','aac','-b:a','160k','-ar','48000','-af','apad','-movflags','+faststart','final.mp4'],stdin=subprocess.PIPE)
for i in range(round(DUR*FPS)):
    t=i/FPS; im=frame(t)
    if i in [0,45,100,170]: im.save(f'frames/proof_{i:03d}.jpg',quality=88)
    proc.stdin.write(im.tobytes())
proc.stdin.close(); raise SystemExit(proc.wait())
