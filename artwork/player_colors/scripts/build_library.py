"""Build normalized layered recipes and ready-to-use preset PNGs.

All independent hull/detail combinations are supported by bake_pair.py.
"""
import argparse
import hashlib
import io
import json
import re
import numpy as np
from PIL import Image
from inventory import ROOT,discover,read_glb,image_bytes
from lod_bindings import primitive_bindings
from masks import classify
from paint import config,references,compose,solid_color


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):return path.relative_to(ROOT).as_posix()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--rebuild-masks',action='store_true')
    parser.add_argument('--reuse-masks',action='store_true',help='Compatibility alias; masks are retained by default.')
    args=parser.parse_args()
    colors=config();settings=json.loads((ROOT/'assets.json').read_text())
    manifest={'version':2,'composition_version':'normalized-srgb-v2',
        'color_space':'Albedo PNGs and palette hex values are sRGB; material RGBA factors are linear.',
        'hull_colors':colors['hull_colors'],'detail_colors':colors['detail_colors'],
        'palettes':{key:{**p,'hull_srgb':colors['hull_colors'][p['hull']]['srgb'],
                       'stripe_srgb':colors['detail_colors'][p['detail']]['srgb']} for key,p in colors['presets'].items()},
        'mix_and_match':{'storage':'Base albedo + reviewed masks + normalization references; bake selected pair before match.',
            'combinations':[{'id':h+'__'+d,'hull':h,'detail':d} for h in colors['hull_colors'] for d in colors['detail_colors']],
            'export_command':'python artwork/player_colors/scripts/bake_pair.py --hull HULL --detail DETAIL',
            'bulk_export_command':'python artwork/player_colors/scripts/bake_pair.py --all'},
        'assets':[],'texture_sets':{},'source_files':{}}
    seen={}
    for asset,path in discover().items():
        print('GENERATE',asset,flush=True)
        doc,binary=read_glb(path);manifest['source_files'][str(path)]=sha(path)
        item={'id':asset,'source':str(path),'materials':[],'lods':[]}
        for index,mat in enumerate(doc.get('materials',[])):
            pbr=mat.get('pbrMetallicRoughness',{});name=mat.get('name',str(index))
            entry={'index':index,'name':name,'original_base_color_factor':pbr.get('baseColorFactor',[1,1,1,1]),
                'action':'preserve','preserve_other_material_properties':True}
            if 'baseColorTexture' in pbr:
                ti=pbr['baseColorTexture'];image_index=doc['textures'][ti['index']]['source']
                raw=image_bytes(doc,binary,doc['images'][image_index],path);digest=hashlib.sha256(raw).hexdigest()
                entry.update(original_image_sha256=digest,texture_coordinate=ti.get('texCoord',0),texture_info=ti)
                if digest not in seen:
                    key=asset if asset not in manifest['texture_sets'] else asset+'_'+str(index);seen[digest]=key
                    folder=ROOT/'textures'/key;folder.mkdir(parents=True,exist_ok=True)
                    image=Image.open(io.BytesIO(raw)).convert('RGBA');source=np.array(image);original=folder/'original.png'
                    if not original.exists():image.save(original,compress_level=4)
                    else:assert np.array_equal(np.array(Image.open(original).convert('RGBA')),source),key+' changed source atlas'
                    hp,dp=folder/'hull_mask.png',folder/'stripe_mask.png'
                    if hp.exists() and dp.exists() and not args.rebuild_masks:
                        hull,detail=np.array(Image.open(hp)),np.array(Image.open(dp))
                    else:
                        emission=None
                        if 'emissiveTexture' in mat:
                            et=mat['emissiveTexture'];assert et.get('texCoord',0)==ti.get('texCoord',0)
                            ei=doc['textures'][et['index']]['source']
                            emission=np.array(Image.open(io.BytesIO(image_bytes(doc,binary,doc['images'][ei],path))).convert('RGB').resize(image.size,Image.Resampling.NEAREST))
                        hull,detail=classify(source,emission=emission)
                        Image.fromarray(hull).save(hp);Image.fromarray(detail).save(dp)
                    assert hull.shape==detail.shape==source.shape[:2]
                    assert np.all(hull.astype(np.uint16)+detail<=255)
                    refs=references(source,hull,detail,colors['normalization'])
                    refs.update(settings['normalization_overrides'].get(key,{}));assert all(v>0 for v in refs.values())
                    packed=np.zeros_like(source[:,:,:3]);packed[:,:,0]=hull;packed[:,:,1]=detail
                    packed_path=folder/'paint_mask.png';Image.fromarray(packed).save(packed_path)
                    outputs={}
                    for preset,p in manifest['palettes'].items():
                        target=folder/('standardized_original.png' if preset=='original' else preset+'.png')
                        Image.fromarray(compose(source,hull,detail,p['hull_srgb'],p['stripe_srgb'],refs)).save(target,compress_level=4)
                        outputs[preset]=rel(target)
                    manifest['texture_sets'][key]={'size':list(image.size),'source_image_sha256':digest,
                        'original':rel(original),'hull_mask':rel(hp),'stripe_mask':rel(dp),'packed_mask':rel(packed_path),
                        'hull_mask_sha256':sha(hp),'stripe_mask_sha256':sha(dp),'normalization':refs,
                        'hull_coverage_fraction':float(np.mean(hull>0)),'stripe_coverage_fraction':float(np.mean(detail>0)),
                        'variants':outputs}
                    del source,hull,detail,packed
                entry.update(action='replace_base_color_texture',texture_set=seen[digest])
            elif name in settings['solid_roles']:
                entry.update(action='replace_base_color_factor',role=settings['solid_roles'][name])
                entry['variants']={preset:solid_color(entry,p['hull'],p['detail'],colors) for preset,p in colors['presets'].items()}
            item['materials'].append(entry)
        for path_lod in sorted(path.parent.glob(path.stem+'_lod*.glb')):
            ld,_=read_glb(path_lod);manifest['source_files'][str(path_lod)]=sha(path_lod);bindings=[]
            for j,lm in enumerate(ld.get('materials',[])):
                normalized=re.sub(r'\.\d+$','',lm.get('name',''))
                candidates=[m for m in item['materials'] if re.sub(r'\.\d+$','',m['name'])==normalized]
                if not candidates and len(item['materials'])==1:candidates=item['materials']
                assert candidates,('Unmapped LOD material',asset,lm.get('name'))
                bindings.append({'lod_material_index':j,'source_material_index':candidates[0]['index']})
            item['lods'].append({'path':str(path_lod),'material_bindings':bindings,
                'primitive_bindings':primitive_bindings(doc,ld,bindings),
                'usage':'Assign the LOD0 variant material to each listed mesh surface, including geometry-only LODs.'})
        manifest['assets'].append(item)
    temp=ROOT/'manifest.pending.json';temp.write_text(json.dumps(manifest,indent=2));temp.replace(ROOT/'manifest.json')
    print('GENERATED',len(manifest['assets']),'assets;',len(manifest['texture_sets']),'atlases;',len(manifest['mix_and_match']['combinations']),'pairs',flush=True)


if __name__=='__main__':main()
