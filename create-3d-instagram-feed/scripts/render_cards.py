#!/usr/bin/env python3
"""Author LABMAP cards from fixed coordinates. Requires Pillow; no network calls."""
import argparse, json, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
W,H=1080,1350
NAVY='#073858'; BLUE='#1262F5'; INK='#24445F'; PALE='#EDF6FF'
def font(size,bold=False):
    return ImageFont.truetype(str(ROOT/'assets/fonts'/('NotoSansKR-700.ttf' if bold else 'NotoSansKR-400.ttf')),size)
def canvas():
    return Image.open(ROOT/'assets/background.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
def text(draw,xy,value,size,bold=False,fill=NAVY,maxwidth=None):
    if maxwidth is not None and draw.textlength(value,font=font(size,bold))>maxwidth:
        raise ValueError(f'Text exceeds fixed width: {value!r}; shorten the copy, never shrink type.')
    draw.text(xy,value,font=font(size,bold),fill=fill,anchor='lt')
def lines(draw,x,y,values,size,leading,bold=False,maxwidth=None):
    for i,v in enumerate(values): text(draw,(x,y+i*leading),v,size,bold,maxwidth=maxwidth)
def base_header(d,category):
    text(d,(64,52),'LABMAP',27,True)
    text(d,(64,102),'BUSINESS INSIGHT',16,False,INK)
    # Category lives in a fixed slot; never shift any other object.
    d.rounded_rectangle((650,48,1016,94),radius=23,fill=PALE)
    width=d.textlength(category,font=font(20,True))
    if width>330: raise ValueError('Category is too long')
    text(d,(833-width/2,60),category,20,True)
def render_body(card,index,total,out):
    im=canvas(); d=ImageDraw.Draw(im)
    base_header(d,card['category'])
    if len(card['title'])!=2 or len(card['panels'])!=3: raise ValueError('Body requires exactly two title lines and three panels')
    lines(d,64,190,card['title'],58,78,True,952)
    text(d,(64,365),card['subtitle'],27,maxwidth=952)
    for i,p in enumerate(card['panels']):
        y=435+i*218
        d.rounded_rectangle((64,y,1016,y+194),radius=26,fill=PALE,outline='#DCEBFA',width=1)
        d.rounded_rectangle((88,y+42,192,y+146),radius=24,fill='#D8EAFF')
        text(d,(109,y+69),f'{i+1:02}',40,True,BLUE)
        text(d,(226,y+35),p['heading'],34,True,maxwidth=748)
        body=p['body']
        if len(body)>2: raise ValueError('Each panel allows at most two body lines')
        lines(d,226,y+98,body,27,39,maxwidth=748)
    d.rounded_rectangle((64,1112,1016,1210),radius=22,fill=NAVY)
    text(d,(90,1147),card['takeaway'],28,True,'#FFFFFF',900)
    d.line((64,1260,1016,1260),fill='#B8D3EA',width=1)
    text(d,(64,1280),'LABMAP · 비즈니스 인사이트',18,True)
    text(d,(930,1280),f'{index:02} / {total:02}',18)
    im.save(out)
def render_ending(out):
    im=canvas(); d=ImageDraw.Draw(im)
    text(d,(64,60),'LABMAP',27,True)
    text(d,(64,112),'TECHNOLOGY TO BUSINESS',16,False,INK)
    text(d,(64,350),'LABMAP',130,True)
    lines(d,64,555,['기술과 비즈니스를','연결합니다.'],58,82,True)
    lines(d,64,765,['복잡한 과제를 정리하고,','실행의 방향을 함께 찾습니다.'],30,48)
    d.line((64,925,1016,925),fill='#BED5EB',width=2)
    for x,n,t in [(64,'01','기술'),(392,'02','전략'),(720,'03','실행')]:
        text(d,(x,966),n,20,True,BLUE)
        text(d,(x,1008),t,36,True)
    d.rounded_rectangle((64,1140,1016,1236),radius=22,fill=NAVY)
    text(d,(118,1172),'저장하고, 다음 인사이트도 함께하세요',31,True,'#FFFFFF',850)
    text(d,(64,1290),'LABMAP',18,True)
    # Deliberately no subject, dates, source URL or page count: identical reuse.
    im.save(out)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    data=json.loads(a.input.read_text()); a.output.mkdir(parents=True,exist_ok=True)
    bodies=data['body_cards']; total=len(bodies)+2
    manifest={'size':[W,H],'layout_version':'labmap-fixed-v1','title':{'x':64,'y':190,'size':58,'leading':78},'subtitle':{'x':64,'y':365,'size':27},'panels':{'x':64,'y':[435,653,871],'w':952,'h':194,'heading_size':34,'body_size':27},'footer_y':1280,'cards':[]}
    for i,c in enumerate(bodies,2):
        path=a.output/f'{i:02}-body.png'; render_body(c,i,total,path); manifest['cards'].append(path.name)
    path=a.output/'labmap-ending.png'
    master=ROOT/'assets/labmap-ending.png'
    if master.exists(): shutil.copyfile(master,path)
    else: render_ending(path)
    manifest['cards'].append(path.name)
    (a.output/'layout-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(f'Rendered {len(bodies)} body cards and one reusable LABMAP ending at {a.output}')
if __name__=='__main__': main()
