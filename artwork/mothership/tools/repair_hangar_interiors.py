"""Clear legacy textured hull intrusions without changing the fitted bay assembly.

Run on the backed-up source before saving/exporting. Native X Mirror is retained.
No texture rebake or UV re-layout is performed.
"""
import bpy
import json
import hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
hull = bpy.data.objects['Mothership_Hull']
assert not hull.get('hangar_interior_clearance_repaired'), 'Hangar repair already applied'
fit = json.loads((ROOT / 'hangar_fit_validation.json').read_text())['Starboard']
coeff = fit['skin_coefficients']

def skin(y, z):
    u, v = (y + 6.0) / 6.45, (z - 1.8) / 3.05
    terms = (1, u, v, u*u, u*v, v*v, u*u*u, u*u*v, u*v*v, v*v*v)
    return sum(c*t for c, t in zip(coeff, terms))

def face_key(face, mesh):
    return tuple(sorted(tuple(round(v, 6) for v in mesh.vertices[i].co) for i in face.vertices))

uv_cache = {}

def cache_uvs(mesh):
    uv_cache.clear()
    for uv in mesh.uv_layers:
        values = np.empty(len(mesh.loops) * 2, dtype=np.float32)
        uv.data.foreach_get('uv', values)
        uv_cache[uv.name] = values.reshape((-1, 2))

def face_uvs(face, mesh):
    return {name: sorted((tuple(round(v, 6) for v in mesh.vertices[mesh.loops[i].vertex_index].co), tuple(round(float(v), 6) for v in values[i])) for i in face.loop_indices) for name, values in uv_cache.items()}

print('Snapshotting exterior UVs', flush=True)
cache_uvs(hull.data)

# Protect every existing face outside the recess envelope, including UV values.
protected = {}
for face in hull.data.polygons:
    points = [hull.data.vertices[i].co for i in face.vertices]
    intersects = (max(v.x for v in points) >= 6.8 and min(v.x for v in points) <= 21.0
                  and max(v.y for v in points) >= -11.95 and min(v.y for v in points) <= -0.05
                  and max(v.z for v in points) >= -0.92 and min(v.z for v in points) <= 4.52)
    if not intersects:
        protected[face_key(face, hull.data)] = face_uvs(face, hull.data)

# Subdivided front follows the known curved hull mouth, recessed behind its rim.
# Back and side/bottom/top caps sit behind the manufactured interior surfaces.
ny, nz = 8, 4
vertices = []
for back in [True, False]:
    for j in range(nz + 1):
        z = -0.92 + (4.52 + 0.92) * j / nz
        for i in range(ny + 1):
            y = -11.95 + 11.9 * i / ny
            vertices.append((6.8 if back else skin(y, z) - 0.15, y, z))
layer = (ny + 1) * (nz + 1)
faces = []
for j in range(nz):
    for i in range(ny):
        a = j*(ny+1) + i
        b = a + ny + 1
        faces.append((a, a+1, b+1, b))
        faces.append((layer+a, layer+b, layer+b+1, layer+a+1))
perimeter = list(range(ny+1))
perimeter += [j*(ny+1)+ny for j in range(1, nz+1)]
perimeter += [nz*(ny+1)+i for i in range(ny-1, -1, -1)]
perimeter += [j*(ny+1) for j in range(nz-1, 0, -1)]
for a, b in zip(perimeter, perimeter[1:] + perimeter[:1]):
    faces.append((a, b, layer+b, layer+a))

import bmesh
mesh = bpy.data.meshes.new('Hangar clearance cutter')
mesh.from_pydata(vertices, [], faces)
mesh.update()
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
mesh.materials.append(bpy.data.materials['Hangar titanium'])
cutter = bpy.data.objects.new('Temporary hangar interior clearance', mesh)
bpy.context.scene.collection.objects.link(cutter)

selection = list(bpy.context.selected_objects)
active = bpy.context.view_layer.objects.active
bpy.ops.object.select_all(action='DESELECT')
hull.select_set(True)
bpy.context.view_layer.objects.active = hull
modifier = hull.modifiers.new('Clear buried hangar artwork', 'BOOLEAN')
modifier.object = cutter
modifier.operation = next(i.identifier for i in modifier.bl_rna.properties['operation'].enum_items if i.identifier == 'DIFFERENCE')
modifier.solver = next(i.identifier for i in modifier.bl_rna.properties['solver'].enum_items if i.identifier == 'EXACT')
modifier.material_mode = next(i.identifier for i in modifier.bl_rna.properties['material_mode'].enum_items if i.identifier == 'TRANSFER')
while list(hull.modifiers).index(modifier) > 0:
    bpy.ops.object.modifier_move_up(modifier=modifier.name)
print('Applying local interior clearance', flush=True)
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(cutter, do_unlink=True)
bpy.data.meshes.remove(mesh)

print('Checking protected exterior geometry and UVs', flush=True)
cache_uvs(hull.data)
after = {face_key(p, hull.data): p for p in hull.data.polygons}
for key, uvs in protected.items():
    assert key in after, 'Repair altered exterior hull geometry'
    assert face_uvs(after[key], hull.data) == uvs, 'Repair altered exterior UVs'

field = bpy.data.materials['Forcefield blue membrane']
field.surface_render_method = next(i.identifier for i in field.bl_rna.properties['surface_render_method'].enum_items if i.identifier == 'BLENDED')
field.use_transparency_overlap = False
field.use_transparent_shadow = False
shader = next(n for n in field.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
shader.inputs['Alpha'].default_value = 0.10
shader.inputs['Emission Strength'].default_value = 0.65

tree = BVHTree.FromObject(hull, bpy.context.evaluated_depsgraph_get())
clear_rays = 0
for side in [-1, 1]:
    for y in [-10, -8, -6, -4, -2]:
        for z in [0.0, 1.8, 3.3]:
            hit, *_ = tree.ray_cast(Vector((side*25, y, z)), Vector((-side, 0, 0)), 17.9)
            assert hit is None, ('Hull still obstructs bay interior', side, y, z, hit)
            clear_rays += 1
hull['hangar_interior_clearance_repaired'] = True
report = {
    'method': 'Local curved recess removes buried hull artwork; original manufactured bay geometry/materials unchanged',
    'protected_exterior_faces_and_all_uv_layers_unchanged': len(protected),
    'interior_clearance_rays': clear_rays,
    'native_mirror_retained': any(m.type == 'MIRROR' for m in hull.modifiers),
    'hull_texture_sha256': hashlib.sha256((ROOT/'textures/hull_detailed_finish_8k.png').read_bytes()).hexdigest(),
    'blender_forcefield': {'method': field.surface_render_method, 'alpha': 0.10, 'emission_strength': 0.65},
}
(ROOT/'hangar_interior_validation.json').write_text(json.dumps(report, indent=2))
bpy.ops.object.select_all(action='DESELECT')
for obj in selection:
    obj.select_set(True)
bpy.context.view_layer.objects.active = active
print('HANGAR REPAIR:', json.dumps(report))
