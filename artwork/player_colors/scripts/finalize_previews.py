"""Background Blender: test all independent choices and source switching in saved previews."""
import bpy
import json
from pathlib import Path
import sys
import hashlib

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from blender_paint import rgb
manifest=json.loads((ROOT/'manifest.json').read_text())
helper=(ROOT/'scripts/apply_preview_palette.py').read_text();results=[]
for asset in manifest['assets']:
    path=ROOT/'previews/blender'/(asset['id']+'.blend')
    bpy.ops.wm.open_mainfile(filepath=str(path))
    for pair in manifest['mix_and_match']['combinations']:
        code=helper.replace("HULL = 'white'",'HULL = '+repr(pair['hull'])).replace("DETAIL = 'black'",'DETAIL = '+repr(pair['detail']))
        exec(compile(code,'Choose hull and details.py','exec'),{})
        for material in bpy.data.materials:
            if material.get('pc_action')=='replace_base_color_texture':
                for node,expected in [('PC Hull sRGB',rgb(manifest['hull_colors'][pair['hull']]['srgb'])),
                                      ('PC Detail sRGB',rgb(manifest['detail_colors'][pair['detail']]['srgb']))]:
                    actual=material.node_tree.nodes[node].outputs[0].default_value
                    assert all(abs(a-b)<1e-6 for a,b in zip(actual,expected))
    exec(compile(helper.replace('SHOW_SOURCE = False','SHOW_SOURCE = True'),'Choose hull and details.py','exec'),{})
    for obj in bpy.context.scene.objects:
        if obj.type=='MESH' and 'pc_source_material_names' in obj:
            assert [m.name for m in obj.data.materials]==list(obj['pc_source_material_names'])
    exec(compile(helper,'Choose hull and details.py','exec'),{})
    text=bpy.data.texts.get('Choose hull and details.py');text.clear();text.write(helper)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path))
    bpy.ops.wm.open_mainfile(filepath=str(path))
    assert bpy.data.texts.get('Choose hull and details.py')
    assert bpy.context.scene['selected_hull']=='white' and bpy.context.scene['selected_detail']=='black'
    for image in bpy.data.images:
        if image.source=='FILE' and image.filepath and not image.packed_file:
            assert Path(bpy.path.abspath(image.filepath)).exists(),image.filepath
    results.append({'asset':asset['id'],'pair_switches_checked':len(manifest['mix_and_match']['combinations']),
                    'source_switch_checked':True,'saved_file_reopened':True,'relative_texture_links_valid':True})
    print('FINALIZED',asset['id'],flush=True)
    report_path=ROOT/'previews/raw'/asset['id']/'render_report.json'
    report=json.loads(report_path.read_text());report['manifest_sha256']=hashlib.sha256((ROOT/'manifest.json').read_bytes()).hexdigest()
    report_path.write_text(json.dumps(report,indent=2))
(ROOT/'previews/blender_validation.json').write_text(json.dumps(results,indent=2))
