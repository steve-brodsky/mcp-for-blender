import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='C:/Dev/BlenderMCP/.tmp/interceptor-muzzles/inspection.blend')
o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
print('MATRIX',o.matrix_world)
for x in [-.22,-.21,-.20,-.19,.19,.20,.21,.22]:
 for z in [-.01,-.02,-.03,-.04]:
  inv=o.matrix_world.inverted()
  hit,p,n,i=o.ray_cast(inv@Vector((x,3,z)),inv.to_3x3()@Vector((0,-1,0)))
  if hit: print('RAY',x,z,tuple(round(v,5) for v in o.matrix_world@p))
# Hide wings in this inspection copy to reveal the gun from the side.
import bmesh
bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if abs((o.matrix_world@v.co).x)>.36],context='VERTS')
bm.to_mesh(o.data);bm.free()
s=bpy.context.scene;c=s.camera;c.data.ortho_scale=1.7
for name,loc,target,up in [('hull_side',(6,.7,0),(0,.7,0),'Z'),('hull_angle',(2,4,1),(0,.7,0),'Y')]:
 c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z',up).to_euler()
 s.render.filepath='C:/Dev/BlenderMCP/.tmp/interceptor-muzzles/'+name+'.png';bpy.ops.render.render(write_still=True)
