"""Embedded in every v2 Blender preview. Choose IDs from palette.json, then Run Script."""
import bpy
import json
from pathlib import Path
import sys

HULL = 'white'
DETAIL = 'black'
PRESET = ''  # Optional: original, blue, white_black, etc.; overrides HULL/DETAIL.
SHOW_SOURCE = False  # True displays the untouched historical source paint.

manifest_path=Path(bpy.path.abspath(bpy.context.scene['pc_manifest']))
manifest=json.loads(manifest_path.read_text())
if PRESET:
    HULL=manifest['palettes'][PRESET]['hull'];DETAIL=manifest['palettes'][PRESET]['detail']
assert HULL in manifest['hull_colors'] and DETAIL in manifest['detail_colors']
sys.path.insert(0,str(manifest_path.parent/'scripts'))
from blender_paint import set_pair

changed=set()
for obj in bpy.context.scene.objects:
    if obj.type!='MESH' or 'pc_source_material_names' not in obj:continue
    for index,name in enumerate(obj['pc_source_material_names']):
        material=bpy.data.materials.get(name) if SHOW_SOURCE else bpy.data.materials.get('FleetPaint / '+name,bpy.data.materials.get(name))
        assert material is not None,name
        obj.data.materials[index]=material
        if not SHOW_SOURCE and material not in changed:set_pair(material,HULL,DETAIL,manifest);changed.add(material)
bpy.context.scene['selected_hull']=HULL
bpy.context.scene['selected_detail']=DETAIL
print('Preview:', 'source paint' if SHOW_SOURCE else HULL+' hull / '+DETAIL+' details')
