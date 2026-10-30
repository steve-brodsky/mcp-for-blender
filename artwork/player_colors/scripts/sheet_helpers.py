"""Build contact sheets and an offline browseable gallery from actual Blender renders."""
import html
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from inventory import ROOT

BG='#101923'
PANEL='#1b2836'
WHITE='#ecf1f4'
MUTED='#a8b9c9'


def font(size):
    for name in [r'C:\Windows\Fonts\segoeui.ttf',r'C:\Windows\Fonts\arial.ttf']:
        if Path(name).exists():return ImageFont.truetype(name,size)
    return ImageFont.load_default()


def label(asset):return asset.replace('_',' ').title()


def tile(path,title,width=480,height=400):
    im=Image.new('RGB',(width,height),PANEL)
    render=Image.open(path).convert('RGB');render.thumbnail((width,height-36))
    im.paste(render,((width-render.width)//2,0))
    ImageDraw.Draw(im).text((14,height-30),title,font=font(19),fill=WHITE)
    return im


def sheet(path,title,items,cols,width=480,height=400,subtitle=''):
    head=92 if subtitle else 65
    rows=(len(items)+cols-1)//cols
    im=Image.new('RGB',(cols*width,head+rows*height),BG)
    d=ImageDraw.Draw(im)
    d.text((20,14),title,font=font(28),fill=WHITE)
    if subtitle:d.text((20,53),subtitle,font=font(17),fill=MUTED)
    for i,(source,caption) in enumerate(items):
        im.paste(tile(source,caption,width,height),((i%cols)*width,head+(i//cols)*height))
    im.save(path)



