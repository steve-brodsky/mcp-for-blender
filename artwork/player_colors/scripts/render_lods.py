"""Background Blender: visually check the furthest existing LOD with inherited paint.

Temporary GLB copies add placeholder surface indices only. Production LODs stay intact.
"""
import bpy
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from inventory import read_glb

manifest=json.loads((ROOT/'manifest.json').read_text())
out=ROOT/'previews/lods';out.mkdir(exist_ok=True)
temp=out/'sources';temp.mkdir(exist_ok=True)
results=[]
for asset in manifest['assets']:
    if not asset['lods']:continue
    lod=asset['lods'][-1]
    doc,binary=read_glb(lod['path'])
    doc['materials']=[{'name':'PC_LOD_BIND_'+str(m['index'])} for m in asset['materials']]
    for binding in lod['primitive_bindings']:
        doc['meshes'][binding['lod_mesh_index']]['primitives'][binding['lod_primitive_index']]['material']=binding['source_material_index']
    payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4)
    binary+=b'\0'*((-len(binary))%4)
    raw=struct.pack('<III',0x46546C67,2,28+len(payload)+len(binary))
    raw+=struct.pack('<II',len(payload),0x4E4F534A)+payload
    raw+=struct.pack('<II',len(binary),0x004E4942)+binary
    copy=temp/(asset['id']+'.glb');copy.write_bytes(raw)
    preview=ROOT/'previews/blender'/(asset['id']+'.blend')
    bpy.ops.wm.open_mainfile(filepath=str(preview))
    scene=bpy.context.scene
    root=bpy.data.objects['Preview normalization']
    originals=set(scene.objects)
    for obj in originals:
        if obj.type=='MESH':obj.hide_render=True
    bpy.ops.import_scene.gltf(filepath=str(copy))
    imported=set(scene.objects)-originals
    names=json.loads((ROOT/'previews/raw'/asset['id']/'render_report.json').read_text())['material_bindings']
    by_index={index:name for name,index in names.items()}
    used=[]
    for obj in imported:
        if obj.parent is None:obj.parent=root
        if obj.type!='MESH':continue
        for slot in obj.material_slots:
            index=int(slot.material.name.removeprefix('PC_LOD_BIND_').split('.')[0])
            material=bpy.data.materials.get('FleetPaint / '+by_index[index],bpy.data.materials.get(by_index[index]))
            slot.material=material;used.append(index)
            for node in material.node_tree.nodes:
                if node.type=='TEX_IMAGE' and node.image and max(node.image.size)>2048:
                    image=node.image;r=2048/max(image.size);image.scale(round(image.size[0]*r),round(image.size[1]*r))
    from blender_paint import set_pair
    for material in bpy.data.materials:set_pair(material,'blue','blue',manifest)
    image_path=out/(asset['id']+'_blue.png')
    scene.render.filepath=str(image_path)
    bpy.ops.render.render(write_still=True)
    results.append({'asset':asset['id'],'lod':lod['path'],'source_material_indices':sorted(set(used)),
        'image':str(image_path.relative_to(ROOT)),'production_lod_unchanged':True})
    print('LOD_PREVIEW_COMPLETE',asset['id'],flush=True)
(out/'report.json').write_text(json.dumps(results,indent=2))
