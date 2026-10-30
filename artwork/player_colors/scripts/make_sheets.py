"""Contact sheets for presets, source paint, all pairs and LODs; build offline selector."""
import textwrap
from sheet_helpers import *
from gallery import build_gallery


def main():
    manifest=json.loads((ROOT/'manifest.json').read_text());assert manifest['version']==2
    assets=manifest['assets'];presets=list(manifest['palettes'])
    for name in ['ships','fleets','inspection','matrices']:(ROOT/'previews'/name).mkdir(exist_ok=True)
    for asset in assets:
        key=asset['id'];raw=ROOT/'previews/raw'/key
        report=json.loads((raw/'render_report.json').read_text());assert report['version']==2
        sheet(ROOT/'previews/ships'/(key+'.png'),label(key)+' | Fleet presets',
            [(raw/'source_overview.png','Historical source')]+[(raw/(c+'_overview.png'),manifest['palettes'][c]['label']) for c in presets],
            4,subtitle='Standardized paint / independent hull and detail colors')
        views=[(raw/(c+'_'+v+'.png'),('Historical source' if c=='source' else manifest['palettes'][c]['label'])+' / '+v)
               for c in ['source','original','white_black'] for v in ['overview','top','underside']]
        views.append((raw/'white_black_close.png','White / black - close'))
        sheet(ROOT/'previews/inspection'/(key+'.png'),label(key)+' | Surface inspection',views,3,
            subtitle='Historical source, standardized original, and white hull / black details')
        hs=list(manifest['hull_colors']);ds=list(manifest['detail_colors']);cw,ch,left,head=128,96,185,125
        matrix=Image.new('RGB',(left+cw*len(ds),head+ch*len(hs)),BG);md=ImageDraw.Draw(matrix)
        md.text((18,12),label(key)+' | All '+str(len(hs)*len(ds))+' pairings',font=font(25),fill=WHITE)
        md.text((18,51),'Rows: hull color / columns: detail color',font=font(16),fill=MUTED)
        for column,d in enumerate(ds):
            md.multiline_text((left+column*cw+4,83),textwrap.fill(manifest['detail_colors'][d]['label'],15),font=font(12),fill=WHITE)
        for row,h in enumerate(hs):
            md.multiline_text((12,head+row*ch+28),textwrap.fill(manifest['hull_colors'][h]['label'],20),font=font(15),fill=WHITE)
            for column,d in enumerate(ds):
                im=Image.open(ROOT/'previews/combinations'/key/(h+'__'+d+'.png')).convert('RGB').resize((cw,ch),Image.Resampling.LANCZOS)
                matrix.paste(im,(left+column*cw,head+row*ch))
        matrix.save(ROOT/'previews/matrices'/(key+'.png'))
    for color in ['source']+presets:
        title='Historical source' if color=='source' else manifest['palettes'][color]['label']
        sheet(ROOT/'previews/fleets'/(color+'.png'),title+' | Complete fleet',
            [(ROOT/'previews/raw'/a['id']/(color+'_overview.png'),label(a['id'])) for a in assets],5,width=320,height=264,
            subtitle=str(len(assets))+' ships and support assets / individually framed; sizes are not to scale')
    lr=ROOT/'previews/lods/report.json'
    if lr.exists():
        items=[]
        for entry in json.loads(lr.read_text()):
            key=entry['asset']
            if key not in {a['id'] for a in assets}:continue
            items.extend([(ROOT/'previews/raw'/key/'blue_overview.png',label(key)+' / LOD0'),(ROOT/entry['image'],label(key)+' / far LOD')])
        sheet(ROOT/'previews/lod_comparison.png','Blue fleet | LOD material inheritance',items,4,width=320,height=264,
            subtitle='LOD0 and furthest supplied LOD / identical camera and normalized palette')
    primary=[a for a in assets if 'turret' not in a['id'] and a['id']!='torpedo_mounting_rack']
    readability=Image.new('RGB',(180+160*len(presets),120+120*len(primary)),BG);rd=ImageDraw.Draw(readability)
    rd.text((20,12),'Fleet presets | Small silhouettes',font=font(28),fill=WHITE)
    rd.text((20,52),'Fixed 160 px tiles / matched normalized paint',font=font(17),fill=MUTED)
    for column,color in enumerate(presets):rd.text((190+column*160,89),label(color),font=font(16),fill=WHITE)
    for row,asset in enumerate(primary):
        key=asset['id'];y=120+row*120
        rd.multiline_text((12,y+35),textwrap.fill(label(key),18),font=font(15),fill=WHITE)
        for column,color in enumerate(presets):
            image=Image.open(ROOT/'previews/raw'/key/(color+'_overview.png')).convert('RGB').resize((160,120),Image.Resampling.LANCZOS)
            readability.paste(image,(180+column*160,y))
    readability.save(ROOT/'previews/skirmish_readability.png')
    build_gallery(manifest)
    print('SHEETS_COMPLETE',len(assets),'assets,',len(presets),'presets,',len(manifest['mix_and_match']['combinations']),'pairings')


if __name__=='__main__':main()
