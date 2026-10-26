import bpy
from mathutils import Vector
from pathlib import Path
out=Path('C:/Dev/BlenderMCP/.tmp/interceptor-muzzles')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='C:/Users/stevi/OneDrive/Documents/space-game-prototype/assets/ships/interceptor/interceptor.glb')
for o in list(bpy.context.scene.objects):
    if o.type=='MESH':
        for v in o.data.vertices: v.co *= .25
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='TEXTURE'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.background_type='WORLD'
scene.world=bpy.data.worlds.new('World')
scene.world.color=(.12,.12,.12)
scene.render.resolution_x=1100
scene.render.resolution_y=900
scene.render.resolution_percentage=100
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
cam.data.type='ORTHO'
cam.data.ortho_scale=3.7
for name,loc,up in [('front',(0,6,1.6),'Y'),('top',(0,0,6),'Y'),('side',(6,0,0),'Z')]:
    cam.location=loc
    cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z',up).to_euler()
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'inspection.blend'))
