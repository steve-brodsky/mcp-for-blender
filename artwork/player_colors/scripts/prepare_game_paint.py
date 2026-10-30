"""Package lossless, size-budgeted runtime paint inputs and attach scene bindings.

Production GLBs and authoring masks are never modified. Run after changing the
paint manifest; the generated runtime registry contains no authoring absolute paths.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import numpy as np
from PIL import Image
from inventory import ROOT,GAME


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--game',type=Path,default=GAME);args=parser.parse_args()
    game=args.game;manifest=json.loads((ROOT/'manifest.json').read_text());assert manifest['version']==2
    out=game/'assets/fleet_paint';out.mkdir(parents=True,exist_ok=True)
    authoring_revision=hashlib.sha256((ROOT/'manifest.json').read_bytes()).hexdigest()
    registry={'version':2,'authoring_revision':authoring_revision,'packing_version':1,
        'max_dimension':2048,'presets':manifest['palettes'],'texture_sets':{},'assets':{}}
    for key,t in manifest['texture_sets'].items():
        folder=out/key;folder.mkdir(exist_ok=True)
        for name,field in [('source.png','original'),('mask.png','packed_mask')]:
            image=Image.open(ROOT/t[field]);image.thumbnail((2048,2048),Image.Resampling.LANCZOS)
            if field=='packed_mask':
                a=np.array(image);a[:,:,1]=np.minimum(a[:,:,1],255-a[:,:,0]);image=Image.fromarray(a)
            image.save(folder/name,compress_level=4)
            # Keep exact SDR input bytes for the one-time compositor, not lossy VRAM blocks.
            settings=folder/(name+'.import')
            if not settings.exists():
                settings.write_text('[remap]\nimporter="texture"\ntype="CompressedTexture2D"\n\n[params]\ncompress/mode=0\nmipmaps/generate=false\nprocess/fix_alpha_border=false\n')
        registry['texture_sets'][key]={'source':'res://'+(folder/'source.png').relative_to(game).as_posix(),
            'mask':'res://'+(folder/'mask.png').relative_to(game).as_posix(),'normalization':t['normalization'],
            'source_sha256':hashlib.sha256((folder/'source.png').read_bytes()).hexdigest(),
            'mask_sha256':hashlib.sha256((folder/'mask.png').read_bytes()).hexdigest()}
    scenes=list((game/'scenes/ships').rglob('*.tscn'))+list((game/'scenes/weapons').rglob('*.tscn'))
    aliases={'torpedo_mounting_rack':'torpedo_bomber_rack'}
    for asset in manifest['assets']:
        assert not asset['id'].startswith('carrier')
        materials=[{k:v for k,v in m.items() if k not in ['variants','texture_info','original_image_sha256']} for m in asset['materials']]
        registry['assets'][asset['id']]={'materials':materials,'scene_paths':[]}
        for scene in scenes:
            if scene.stem!=aliases.get(asset['id'],asset['id']):continue
            registry['assets'][asset['id']]['scene_paths'].append('res://'+scene.relative_to(game).as_posix())
            text=scene.read_text(encoding='utf-8')
            original_text=text
            if 'id="FleetPaint"' not in text:
                start=text.index('\n',text.index('[gd_scene'))+1
                text=text[:start]+'\n[ext_resource type="Script" path="res://scripts/fleet_paint/fleet_paint_binding.gd" id="FleetPaint"]\n'+text[start:]
            if '[node name="FleetPaint"' not in text:
                text+='\n[node name="FleetPaint" type="Node" parent="."]\nscript = ExtResource("FleetPaint")\nasset_id = "'+asset['id']+'"\n'
            if text!=original_text:scene.write_text(text,encoding='utf-8')
    scripts=game/'scripts/fleet_paint';scripts.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/'integration/fleet_paint_baker.gd',scripts/'fleet_paint_baker.gd')
    shutil.copyfile(ROOT/'integration/compose_paint.gdshader',scripts/'compose_paint.gdshader')
    revision={'authoring':authoring_revision,'packing_version':registry['packing_version'],
        'textures':registry['texture_sets'],'max_dimension':registry['max_dimension'],
        'compositor':hashlib.sha256((scripts/'compose_paint.gdshader').read_bytes()).hexdigest()}
    registry['recipe_revision']=hashlib.sha256(json.dumps(revision,sort_keys=True).encode()).hexdigest()
    (out/'registry.json').write_text(json.dumps(registry,indent=2))
    print('PACKAGED',len(registry['assets']),'assets,',len(registry['texture_sets']),'runtime atlases')


if __name__=='__main__':main()
