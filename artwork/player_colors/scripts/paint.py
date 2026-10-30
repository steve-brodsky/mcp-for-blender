"""Shared v2 color math. Inputs/outputs are sRGB bytes; masks are linear weights."""
import hashlib
import json
import numpy as np
from PIL import Image
from inventory import ROOT

LUMA=np.array([.2126,.7152,.0722],np.float32)


def rgb(code):
    return np.array([int(code[i:i+2],16)/255 for i in (1,3,5)],np.float32)


def linear(values):
    a=np.asarray(values,np.float32)
    return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4).tolist()


def config():
    c=json.loads((ROOT/'palette.json').read_text())
    for family in ['hull_colors','detail_colors']:
        for key,entry in c[family].items():
            assert key and all(ch.islower() or ch.isdigit() or ch=='_' for ch in key),key
            assert len(entry['srgb'])==7 and entry['srgb'].startswith('#')
            rgb(entry['srgb'])
    for p in c['presets'].values():
        assert p['hull'] in c['hull_colors'] and p['detail'] in c['detail_colors']
    return c


def references(source,hull,detail,settings):
    step=settings['sample_stride']
    lum=source[::step,::step,:3].astype(np.float32)@LUMA/255
    result={}
    for role,mask,fallback in [('hull',hull,settings['fallback_hull']),('detail',detail,settings['fallback_detail'])]:
        sample=lum[mask[::step,::step]>=settings['mask_confidence']]
        result[role]=float(np.percentile(sample,settings['percentile'])) if sample.size>=16 else fallback
        result[role]=max(result[role],.02)
    return result


def compose(source,hull,detail,hull_hex,detail_hex,refs):
    result=source.copy()
    hc,dc=rgb(hull_hex),rgb(detail_hex)
    for row in range(0,source.shape[0],256):
        end=min(row+256,source.shape[0])
        a=source[row:end,:,:3].astype(np.float32)/255
        lum=a@LUMA
        hw=hull[row:end,:,None].astype(np.float32)/255
        dw=detail[row:end,:,None].astype(np.float32)/255
        ht=np.minimum(1,hc*(lum/refs['hull'])[:,:,None])
        dt=np.minimum(1,dc*(lum/refs['detail'])[:,:,None])
        result[row:end,:,:3]=np.rint(np.clip(a*(1-hw-dw)+ht*hw+dt*dw,0,1)*255).astype(np.uint8)
    return result


def load_set(t):
    return (np.array(Image.open(ROOT/t['original']).convert('RGBA')),
            np.array(Image.open(ROOT/t['hull_mask'])),np.array(Image.open(ROOT/t['stripe_mask'])))


def solid_color(material,hull,detail,palette):
    role='hull_colors' if material['role']=='hull' else 'detail_colors'
    key=hull if material['role']=='hull' else detail
    return linear(rgb(palette[role][key]['srgb']))+[material['original_base_color_factor'][3]]


def recipe_fingerprint(manifest):
    recipe={'version':manifest['version'],'hull_colors':manifest['hull_colors'],'detail_colors':manifest['detail_colors'],
            'composition_version':manifest['composition_version'],'assets':manifest['assets'],
            'sets':{k:{field:t[field] for field in ['source_image_sha256','hull_mask_sha256','stripe_mask_sha256','normalization']} for k,t in manifest['texture_sets'].items()}}
    return hashlib.sha256(json.dumps(recipe,sort_keys=True).encode()).hexdigest()
