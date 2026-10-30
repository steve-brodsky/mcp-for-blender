"""Meaningful invariants for normalization, independent masks and cached exports."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import paint
import bake_pair
from inventory import ROOT


class PaintTests(unittest.TestCase):
    def setUp(self):
        self.palette=paint.config()
        self.source=np.array([[[180,170,150,255],[130,40,40,127],[40,55,70,0]]],np.uint8)
        self.hull=np.array([[255,0,0]],np.uint8)
        self.detail=np.array([[0,255,0]],np.uint8)
        self.refs={'hull':float(self.source[0,0,:3]@paint.LUMA/255),'detail':float(self.source[0,1,:3]@paint.LUMA/255)}

    def test_all_color_pairs_and_independent_channels(self):
        for h,hc in self.palette['hull_colors'].items():
            for d,dc in self.palette['detail_colors'].items():
                out=paint.compose(self.source,self.hull,self.detail,hc['srgb'],dc['srgb'],self.refs)
                np.testing.assert_array_equal(out[0,0,:3],np.rint(paint.rgb(hc['srgb'])*255).astype(np.uint8))
                np.testing.assert_array_equal(out[0,1,:3],np.rint(paint.rgb(dc['srgb'])*255).astype(np.uint8))
                np.testing.assert_array_equal(out[0,2],self.source[0,2])
                np.testing.assert_array_equal(out[:,:,3],self.source[:,:,3])

    def test_normalization_matches_different_original_hulls(self):
        mask=np.full((20,20),255,np.uint8);no_detail=np.zeros_like(mask)
        results=[]
        for pixel in [[210,200,175],[155,148,130]]:
            source=np.empty((20,20,4),np.uint8);source[:,:,:3]=pixel;source[:,:,3]=255
            refs=paint.references(source,mask,no_detail,self.palette['normalization'])
            results.append(paint.compose(source,mask,no_detail,'#c9c4b2','#a13931',refs))
        np.testing.assert_array_equal(results[0],results[1])
        np.testing.assert_array_equal(results[0][0,0,:3],[201,196,178])

    def test_partial_masks_protect_alpha_and_unpainted_pixels(self):
        h=self.hull.copy();d=self.detail.copy();h[0,0]=128;d[0,1]=128
        out=paint.compose(self.source,h,d,'#eceeed','#181b21',self.refs)
        np.testing.assert_array_equal(out[:,:,3],self.source[:,:,3])
        np.testing.assert_array_equal(out[0,2],self.source[0,2])
        self.assertGreater(out[0,1,0],24)

    def test_every_pair_exports_solid_and_textured_materials_and_invalidates_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);folder=root/'textures';folder.mkdir()
            for name,data in [('original',self.source),('hull_mask',self.hull),('stripe_mask',self.detail)]:
                Image.fromarray(data).save(folder/(name+'.png'))
            m={'version':2,'composition_version':'test-v2','hull_colors':self.palette['hull_colors'],
                'detail_colors':self.palette['detail_colors'],'palettes':{},'texture_sets':{'test':{
                    'original':'textures/original.png','hull_mask':'textures/hull_mask.png','stripe_mask':'textures/stripe_mask.png',
                    'normalization':self.refs,'source_image_sha256':'source','hull_mask_sha256':'hull','stripe_mask_sha256':'detail'}},
                'assets':[{'id':'ship','source':'untouched.glb','lods':[],'materials':[
                    {'index':0,'action':'replace_base_color_texture','texture_set':'test'},
                    {'index':1,'action':'replace_base_color_factor','role':'stripe','original_base_color_factor':[.3,.1,.1,1]}]}]}
            with patch.object(bake_pair,'ROOT',root),patch.object(paint,'ROOT',root),contextlib.redirect_stdout(io.StringIO()):
                for h in m['hull_colors']:
                    for d in m['detail_colors']:
                        result=bake_pair.bake(m,h,d)
                        target=root/'exports'/(h+'__'+d)/result['texture_sets']['test']
                        self.assertTrue(target.exists())
                        self.assertEqual(result['assets'][0]['materials'][1]['base_color_factor'],paint.linear(paint.rgb(m['detail_colors'][d]['srgb']))+[1])
                result=bake_pair.bake(m,'white','black')
                target=root/'exports/white__black/textures/test.png';before=target.stat().st_mtime_ns
                bake_pair.bake(m,'white','black');self.assertEqual(before,target.stat().st_mtime_ns)
                m['hull_colors']['white']['srgb']='#dddddd'
                changed=bake_pair.bake(m,'white','black');self.assertNotEqual(result['recipe_sha256'],changed['recipe_sha256'])

    def test_gpu_baker_matches_python_all_pairs(self):
        folder=ROOT/'integration/test_project'
        if not (folder/'results').exists():self.skipTest('Run the Godot integration fixture first.')
        source=np.array(Image.open(folder/'source.png').convert('RGBA'))
        mask=np.array(Image.open(folder/'mask.png').convert('RGB'))
        for h,hc in self.palette['hull_colors'].items():
            for d,dc in self.palette['detail_colors'].items():
                path=folder/'results'/(h+'__'+d+'.png');self.assertTrue(path.exists())
                expected=paint.compose(source,mask[:,:,0],mask[:,:,1],hc['srgb'],dc['srgb'],{'hull':.72,'detail':.245})
                actual=np.array(Image.open(path).convert('RGBA'))
                self.assertLessEqual(int(np.max(np.abs(actual.astype(int)-expected.astype(int)))),1,(h,d))
                np.testing.assert_array_equal(actual[:,:,3],source[:,:,3])
                protected=(mask[:,:,0]==0)&(mask[:,:,1]==0)
                np.testing.assert_array_equal(actual[protected],source[protected])


if __name__=='__main__':unittest.main()
