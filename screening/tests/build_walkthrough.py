"""Make a silent, explicitly labelled key-frame walkthrough from actual UI captures."""
import json, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/desktop/screenshots'
DEST=Path('D:/Fossee-runtime/submission')
DEST.mkdir(parents=True,exist_ok=True)
render=DEST/'video-frames'; render.mkdir(exist_ok=True)
frames=json.loads((SOURCE/'frames.json').read_text())
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for i,f in enumerate(frames):
    im=Image.open(SOURCE/f['file']).convert('RGB')
    assert im.width>400 and im.height>150,(f['file'],im.size)
    canvas=Image.new('RGB',(1600,1000),'#142333'); d=ImageDraw.Draw(canvas)
    d.text((28,18),'OSDAGBRIDGE | Software testing | Akshit Singh',font=font,fill='white')
    d.text((28,52),'Desktop walkthrough - captured key frames; pauses omitted. No audio.',font=small,fill='#b9d3e5')
    im.thumbnail((1540,800))
    canvas.paste(im,((1600-im.width)//2,92+(800-im.height)//2))
    caption=f['caption'].replace('cross-bracing CAD isolated','girders and cross-bracing CAD displayed')
    d.multiline_text((28,910),'\n'.join(textwrap.wrap(caption,110)),font=font,fill='white',spacing=7)
    d.text((1510,970),f'{i+1}/{len(frames)}',font=small,fill='#b9d3e5')
    canvas.save(render/f'{i:02d}.png')
listing=render/'concat.txt'
listing.write_text(''.join(f"file '{i:02d}.png'\nduration 6\n" for i in range(len(frames)))+f"file '{len(frames)-1:02d}.png'\n")
video=DEST/'OsdagBridge_Demonstration.mp4'
ffmpeg=Path('D:/Fossee-runtime/env/Library/bin/ffmpeg.exe')
subprocess.run([str(ffmpeg),'-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-vf','fps=15',
                '-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(video)],check=True)
print(video,video.stat().st_size)
