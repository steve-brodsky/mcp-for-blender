import bpy,re
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='C:/Dev/BlenderMCP/.tmp/interceptor-muzzles/inspection.blend')
s=bpy.context.scene
scene_text=open('C:/Users/stevi/OneDrive/Documents/space-game-prototype/scenes/ships/interceptor.tscn').read()
for name in ['MuzzlePort','MuzzleStarboard']:
 values=re.search(r'\[node name="'+name+r'"[^\n]*\]\nposition = Vector3\(([^)]+)\)',scene_text).group(1)
 x,y,z=map(float,values.split(','))
 p=Vector((x,-z,y))
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.009,location=p)
 bpy.context.object.color=(1,.6,0,1)
 # A short forward line makes the launch direction visible.
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.002,depth=.12,location=p+Vector((0,.06,0)),rotation=(1.57079632679,0,0))
 bpy.context.object.color=(1,.6,0,1)
for o in s.objects:
 if o.type=='MESH' and len(o.data.vertices)>1000: o.color=(.6,.6,.6,1)
s.display.shading.color_type='OBJECT'
s.camera.data.ortho_scale=1.3
for name,loc,target,up in [('marked_front',(0,6,0),(0,.7,0),'Y'),('marked_top',(0,.7,6),(0,.7,0),'Y')]:
 s.camera.location=loc;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z',up).to_euler()
 s.render.filepath='C:/Dev/BlenderMCP/.tmp/interceptor-muzzles/'+name+'.png';bpy.ops.render.render(write_still=True)
# Cut away the wing only in the inspection copy for an unobstructed side view.
import bmesh
o=next(o for o in s.objects if o.type=='MESH' and len(o.data.vertices)>1000)
bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if abs(v.co.x)>.36],context='VERTS')
bm.to_mesh(o.data);bm.free()
s.camera.location=(6,.7,0);s.camera.rotation_euler=(Vector((0,.7,0))-s.camera.location).to_track_quat('-Z','Z').to_euler()
s.render.filepath='C:/Dev/BlenderMCP/.tmp/interceptor-muzzles/marked_side.png';bpy.ops.render.render(write_still=True)

