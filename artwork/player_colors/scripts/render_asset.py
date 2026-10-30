"""Background Blender preview renderer. Usage: blender -b --python this.py -- ASSET.

Only writes below player_colors/. The preview .blend uses linked variant PNGs.
"""
import bpy
import json
import math
from mathutils import Vector
from pathlib import Path
import sys
import time
import hashlib

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT/'manifest.json').read_text())
asset_id = sys.argv[sys.argv.index('--')+1]
asset = next(a for a in manifest['assets'] if a['id'] == asset_id)
out = ROOT/'previews/raw'/asset_id
out.mkdir(parents=True,exist_ok=True)
started = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=asset['source'])
scene = bpy.context.scene
scene.render.engine = 'CYCLES' if '--cycles' in sys.argv else 'CYCLES'
if '--eevee' in sys.argv:
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        scene.render.engine = 'BLENDER_EEVEE'
if scene.render.engine == 'CYCLES':
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 2
    scene.cycles.transparent_max_bounces = 4
scene.render.resolution_x = 480
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.render.threads_mode = 'FIXED'
scene.render.threads = 8
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast' if 'Medium High Contrast' in [i.name for i in scene.view_settings.bl_rna.properties['look'].enum_items] else scene.view_settings.look
scene.view_settings.exposure = 0
scene.world = bpy.data.worlds.new('Player color neutral studio')
scene.world.use_nodes = True
background = next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
background.inputs[0].default_value = (.12,.145,.18,1)
background.inputs[1].default_value = .65

meshes = [o for o in scene.objects if o.type=='MESH']
assert meshes, asset_id
# Freeze source animation at its imported pose; no production file is saved.
for obj in scene.objects:
    obj.hide_render = False
    obj.hide_set(False)
    if obj.animation_data:
        obj.animation_data_clear()
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.evaluated_get(dg).bound_box]
lo = Vector([min(v[i] for v in corners) for i in range(3)])
hi = Vector([max(v[i] for v in corners) for i in range(3)])
center = (lo+hi)/2
scale = max(hi-lo)
# A common root retains all skinned and articulated transforms.
root = bpy.data.objects.new('Preview normalization',None)
scene.collection.objects.link(root)
for obj in list(scene.objects):
    if obj != root and obj.parent is None:
        world = obj.matrix_world.copy(); obj.parent=root; obj.matrix_world=world
root.scale = (2/scale,)*3
root.location = -center*(2/scale)
bpy.context.view_layer.update()

def area(name, location, power, size):
    light = bpy.data.lights.new(name,'AREA'); light.energy=power;light.shape='DISK';light.size=size
    obj = bpy.data.objects.new(name,light);scene.collection.objects.link(obj);obj.location=location
    obj.rotation_euler = (-obj.location).to_track_quat('-Z','Y').to_euler()

area('Key softbox',(1,-3,5),480,4)
area('Fill softbox',(-3,-1,2),300,4)
area('Rim softbox',(1,4,3),420,3)
area('Underside fill',(-1,-2,-4),240,4)
cam_data=bpy.data.cameras.new('Preview camera');cam_data.type='ORTHO';cam_data.lens=45
cam=bpy.data.objects.new('Preview camera',cam_data);scene.collection.objects.link(cam);scene.camera=cam

def camera(direction, zoom=1):
    cam.location=Vector(direction).normalized()*6
    cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    inv=cam.matrix_world.inverted()
    points=[inv@(o.matrix_world@Vector(c)) for o in meshes for c in o.bound_box]
    width=max(v.x for v in points)-min(v.x for v in points)
    height=max(v.y for v in points)-min(v.y for v in points)
    aspect=scene.render.resolution_x/scene.render.resolution_y
    cam_data.ortho_scale=max(width,height*aspect)*1.13/zoom

materials = list({m for o in meshes for m in o.data.materials if m})
bindings = {}
for mat in materials:
    mat.use_fake_user = True
    candidates = [m for m in asset['materials'] if m['name'] == mat.name]
    if not candidates:
        # Import appends suffixes to duplicate names, e.g. the mothership hull slots.
        import re
        name = re.sub(r'\.\d+$','',mat.name)
        candidates=[m for m in asset['materials'] if re.sub(r'\.\d+$','',m['name']) == name]
    if not candidates:
        raise ValueError('Unmapped imported material '+mat.name)
    bindings[mat] = candidates[0]


assert manifest['version']==2
sys.path.insert(0,str(ROOT/'scripts'))
from blender_paint import make_paint_material,set_pair
import shutil

original_slots={o:list(o.data.materials) for o in meshes}
controlled={m:make_paint_material(m,b,manifest,ROOT) for m,b in bindings.items()}
for obj,slots in original_slots.items():
    obj['pc_source_material_names']=[m.name if m else '' for m in slots]

def apply_pair(hull,detail,source=False):
    for obj,slots in original_slots.items():
        for i,mat in enumerate(slots):
            obj.data.materials[i]=mat if source else controlled[mat]
    if not source:
        for material in set(controlled.values()):set_pair(material,hull,detail,manifest)

records=[]
def render(path,direction=(3,-5,4),zoom=1):
    camera(direction,zoom);scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    records.append(str(path.relative_to(ROOT)).replace('\\','/'))

apply_pair('ivory','oxide',source=True)
render(out/'source_overview.png')
for view,direction in [('top',(0,-.001,6)),('underside',(0,-.001,-6))]:
    render(out/('source_'+view+'.png'),direction)

combo_dir=ROOT/'previews/combinations'/asset_id;combo_dir.mkdir(parents=True,exist_ok=True)
for pair in manifest['mix_and_match']['combinations']:
    apply_pair(pair['hull'],pair['detail'])
    render(combo_dir/(pair['id']+'.png'))
for name,preset in manifest['palettes'].items():
    shutil.copyfile(combo_dir/(preset['hull']+'__'+preset['detail']+'.png'),out/(name+'_overview.png'))
for name in ['original','white_black']:
    preset=manifest['palettes'][name];apply_pair(preset['hull'],preset['detail'])
    render(out/(name+'_top.png'),(0,-.001,6))
    render(out/(name+'_underside.png'),(0,-.001,-6))
apply_pair('white','black')
render(out/'white_black_close.png',(3,-5,4),1.65)
camera((3,-5,4))

blend_dir=ROOT/'previews/blender';blend_dir.mkdir(exist_ok=True)
blend_path=blend_dir/(asset_id+'.blend')
for image in bpy.data.images:
    if image.source=='FILE' and image.filepath and not image.packed_file:
        image.filepath=bpy.path.relpath(image.filepath,start=str(blend_dir))
scene['player_color_asset']=asset_id
scene['pc_manifest']='//../../manifest.json'
text=bpy.data.texts.new('Choose hull and details.py')
text.write((ROOT/'scripts/apply_preview_palette.py').read_text())
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
(out/'render_report.json').write_text(json.dumps({'version':2,'asset':asset_id,'seconds':time.time()-started,
    'manifest_sha256':hashlib.sha256((ROOT/'manifest.json').read_bytes()).hexdigest(),
    'engine':scene.render.engine,'resolution':[480,360],'preview_texture_max_size':2048,
    'renders':records,'combination_count':len(manifest['mix_and_match']['combinations']),
    'preset_aliases':{key:str((out/(key+'_overview.png')).relative_to(ROOT)).replace('\\','/') for key in manifest['palettes']},
    'material_bindings':{m.name:b['index'] for m,b in bindings.items()},
    'preview_blend':str(blend_path.relative_to(ROOT))},indent=2))
print('PREVIEW_COMPLETE',asset_id,round(time.time()-started,2),flush=True)

