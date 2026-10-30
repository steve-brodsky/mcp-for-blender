"""Validate source integrity, normalized preset pixels, masks, solids and LOD UV mappings."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import numpy as np
from PIL import Image
from inventory import ROOT,read_glb,image_bytes
from paint import compose,solid_color,recipe_fingerprint


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--require-previews',action='store_true');args=parser.parse_args()
    m=json.loads((ROOT/'manifest.json').read_text());assert m['version']==2
    pairs={(p['hull'],p['detail']) for p in m['mix_and_match']['combinations']}
    assert len(pairs)==len(m['mix_and_match']['combinations'])
    assert pairs=={(h,d) for h in m['hull_colors'] for d in m['detail_colors']}
    assert not any(a['id'].startswith('carrier') for a in m['assets'])
    report={'passed':False,'version':2,'recipe_sha256':recipe_fingerprint(m),'checks':{},'texture_sets':{},'assets':{}}
    for path,digest in m['source_files'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
    for key,t in m['texture_sets'].items():
        print('VALIDATE_TEXTURE',key,flush=True)
        source=Image.open(ROOT/t['original']).convert('RGBA');h=Image.open(ROOT/t['hull_mask']);d=Image.open(ROOT/t['stripe_mask'])
        mask=Image.open(ROOT/t['packed_mask']).convert('RGB')
        assert source.size==h.size==d.size==mask.size==tuple(t['size'])
        assert set(t['variants'])==set(m['palettes'])
        for field in ['hull_mask','stripe_mask']:assert hashlib.sha256((ROOT/t[field]).read_bytes()).hexdigest()==t[field+'_sha256']
        assert all(np.isfinite(v) and v>0 for v in t['normalization'].values())
        stats={}
        for name,path in t['variants'].items():
            result=Image.open(ROOT/path).convert('RGBA');assert result.size==source.size
            p=m['palettes'][name];changed=0
            for row in range(0,source.height,256):
                box=(0,row,source.width,min(row+256,source.height))
                a=np.array(source.crop(box));b=np.array(result.crop(box));hm=np.array(h.crop(box));dm=np.array(d.crop(box));packed=np.array(mask.crop(box))
                assert np.all(hm.astype(np.uint16)+dm<=255)
                assert np.array_equal(packed[:,:,0],hm) and np.array_equal(packed[:,:,1],dm)
                assert np.array_equal(a[:,:,3],b[:,:,3])
                protected=(hm==0)&(dm==0);assert np.array_equal(a[protected],b[protected])
                expected=compose(a,hm,dm,p['hull_srgb'],p['stripe_srgb'],t['normalization'])
                assert np.array_equal(expected,b),(key,name,'Composition mismatch')
                changed+=int(np.any(a!=b,axis=-1).sum())
            assert changed>0
            stats[name]={'alpha_exact':True,'protected_pixels_exact':True,'formula_exact':True,
                         'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()}
        report['texture_sets'][key]={'variants':stats,'normalization':t['normalization']}
    checked=set()
    for asset in m['assets']:
        doc,binary=read_glb(asset['source']);materials={x['index']:x for x in asset['materials']}
        assert len(materials)==len(doc.get('materials',[]))
        for mat in materials.values():
            assert mat['preserve_other_material_properties']
            if mat['action']=='replace_base_color_factor':
                for name,p in m['palettes'].items():assert mat['variants'][name]==solid_color(mat,p['hull'],p['detail'],m)
            elif mat['action']=='replace_base_color_texture' and mat['texture_set'] not in checked:
                ti=doc['materials'][mat['index']]['pbrMetallicRoughness']['baseColorTexture'];ii=doc['textures'][ti['index']]['source']
                source=Image.open(io.BytesIO(image_bytes(doc,binary,doc['images'][ii],asset['source']))).convert('RGBA')
                original=Image.open(ROOT/m['texture_sets'][mat['texture_set']]['original']).convert('RGBA')
                assert source.size==original.size
                for row in range(0,source.height,256):
                    box=(0,row,source.width,min(row+256,source.height));assert np.array_equal(np.array(source.crop(box)),np.array(original.crop(box)))
                checked.add(mat['texture_set'])
        for lod in asset['lods']:
            ld,_=read_glb(lod['path'])
            assert len(lod['primitive_bindings'])==sum(len(mesh['primitives']) for mesh in ld['meshes'])
            for binding in lod['primitive_bindings']:
                p=ld['meshes'][binding['lod_mesh_index']]['primitives'][binding['lod_primitive_index']]
                material=materials[binding['source_material_index']]
                if material['action']=='replace_base_color_texture':assert 'TEXCOORD_'+str(material['texture_coordinate']) in p['attributes']
        report['assets'][asset['id']]={'source_materials':len(materials),'lod_bindings_valid':True}
    report['checks'].update(source_files_unchanged=len(m['source_files']),assets=len(m['assets']),hull_choices=len(m['hull_colors']),detail_choices=len(m['detail_colors']),
        supported_pairs=len(pairs),unique_atlases=len(m['texture_sets']),preset_textures=sum(len(t['variants']) for t in m['texture_sets'].values()),
        lod_files=sum(len(a['lods']) for a in m['assets']),carriers_excluded=True,normalized_preset_pixels_exact=True,preview_required=False)
    report['passed']=True;(ROOT/'validation.json').write_text(json.dumps(report,indent=2))
    if args.require_previews:
        from validate_delivery import main as validate_delivery
        validate_delivery()
    print('VALIDATION_PASSED',flush=True)


if __name__=='__main__':main()
