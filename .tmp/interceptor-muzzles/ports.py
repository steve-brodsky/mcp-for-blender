import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='C:/Dev/BlenderMCP/.tmp/interceptor-muzzles/inspection.blend')
o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
for x in [-.16,-.15,-.14,.14,.15,.16]:
 for z in [-.07,-.08,-.09,-.10]:
  hit,p,n,i=o.ray_cast(Vector((x,3,z)),Vector((0,-1,0)))
  if hit: print('RAY',x,z,tuple(round(v,5) for v in p))
s=bpy.context.scene;c=s.camera;c.data.ortho_scale=.65
for name,loc,target,up in [('ports_front',(0,6,-.07),(0,1.15,-.07),'Y'),('ports_top',(0,1.15,6),(0,1.15,0),'Y'),('ports_angle',(2,5,1),(0,1.1,-.06),'Y')]:
 c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z',up).to_euler()
 s.render.filepath='C:/Dev/BlenderMCP/.tmp/interceptor-muzzles/'+name+'.png';bpy.ops.render.render(write_still=True)
