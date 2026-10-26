import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='C:/Dev/BlenderMCP/.tmp/interceptor-muzzles/inspection.blend')
s=bpy.context.scene
c=s.camera
c.data.ortho_scale=.9
for name,loc,target,up in [('front_close',(0,6,0),(0,.8,0),'Y'),('top_close',(0,.8,6),(0,.8,0),'Y'),('side_close',(6,.9,0),(0,.9,0),'Z')]:
 c.location=loc
 c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z',up).to_euler()
 s.render.filepath='C:/Dev/BlenderMCP/.tmp/interceptor-muzzles/'+name+'.png'
 bpy.ops.render.render(write_still=True)
