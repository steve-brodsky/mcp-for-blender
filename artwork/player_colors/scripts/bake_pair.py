"""Bake selected hull/detail pairs for ordinary materials; cache by recipe and content.

python .../bake_pair.py --hull white --detail black
python .../bake_pair.py --hull blue --detail orange --asset interceptor
python .../bake_pair.py --all
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image
from inventory import ROOT
from paint import compose,load_set,solid_color,recipe_fingerprint


def bake(manifest,hull,detail,asset_ids=None,output_root=None):
    assert hull in manifest['hull_colors'] and detail in manifest['detail_colors']
    assets=[a for a in manifest['assets'] if not asset_ids or a['id'] in asset_ids]
    if asset_ids and {a['id'] for a in assets}!=set(asset_ids):raise ValueError('Unknown asset in '+str(asset_ids))
    key=hull+'__'+detail;folder=(output_root or ROOT/'exports')/key
    target_manifest=folder/'materials.json'
    fingerprint=recipe_fingerprint(manifest)
    if target_manifest.exists():
        old=json.loads(target_manifest.read_text())
        if old.get('recipe_sha256')==fingerprint and old.get('asset_ids')==[a['id'] for a in assets]:
            if all((folder/path).exists() and hashlib.sha256((folder/path).read_bytes()).hexdigest()==digest for path,digest in old['files'].items()):
                print('CACHE_HIT',key,flush=True);return old
    folder.mkdir(parents=True,exist_ok=True)
    out={'version':2,'hull':hull,'detail':detail,'recipe_sha256':fingerprint,
         'asset_ids':[a['id'] for a in assets],'files':{},'texture_sets':{},'assets':[]}
    needed={m['texture_set'] for a in assets for m in a['materials'] if m['action']=='replace_base_color_texture'}
    matching=next((name for name,p in manifest['palettes'].items() if p['hull']==hull and p['detail']==detail),None)
    for set_id in sorted(needed):
        t=manifest['texture_sets'][set_id]
        target=folder/'textures'/(set_id+'.png');target.parent.mkdir(exist_ok=True)
        temp=target.with_suffix('.pending.png')
        if matching:
            shutil.copyfile(ROOT/t['variants'][matching],temp)
        else:
            source,hm,dm=load_set(t)
            result=compose(source,hm,dm,manifest['hull_colors'][hull]['srgb'],manifest['detail_colors'][detail]['srgb'],t['normalization'])
            Image.fromarray(result).save(temp,compress_level=4)
        temp.replace(target)
        rel=target.relative_to(folder).as_posix()
        out['texture_sets'][set_id]=rel;out['files'][rel]=hashlib.sha256(target.read_bytes()).hexdigest()
    for asset in assets:
        entry={'id':asset['id'],'source':asset['source'],'lods':asset['lods'],'materials':[]}
        for material in asset['materials']:
            m={k:v for k,v in material.items() if k not in ['variants','texture_info']}
            if material['action']=='replace_base_color_texture':m['albedo_texture']=out['texture_sets'][material['texture_set']]
            elif material['action']=='replace_base_color_factor':m['base_color_factor']=solid_color(material,hull,detail,manifest)
            entry['materials'].append(m)
        out['assets'].append(entry)
    temp=target_manifest.with_suffix('.pending.json');temp.write_text(json.dumps(out,indent=2));temp.replace(target_manifest)
    print('BAKED',key,len(assets),'assets',len(needed),'atlases',flush=True)
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--hull');parser.add_argument('--detail')
    parser.add_argument('--all',action='store_true');parser.add_argument('--asset',action='append')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();manifest=json.loads((ROOT/'manifest.json').read_text())
    if args.all:
        if args.hull or args.detail:parser.error('Choose --all or --hull/--detail, not both.')
        pairs=[(h,d) for h in manifest['hull_colors'] for d in manifest['detail_colors']]
    else:
        if not args.hull or not args.detail:parser.error('Provide both --hull and --detail.')
        if args.hull not in manifest['hull_colors'] or args.detail not in manifest['detail_colors']:parser.error('Unknown color; see palette.json.')
        pairs=[(args.hull,args.detail)]
    for hull,detail in pairs:bake(manifest,hull,detail,args.asset,args.output)


if __name__=='__main__':main()
