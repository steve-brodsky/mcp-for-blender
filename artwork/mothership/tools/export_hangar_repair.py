"""Export the accepted local repair without changing source camera/render settings."""
import bpy
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
hull = bpy.data.objects['Mothership_Hull']
assert hull.get('hangar_interior_clearance_repaired')
hull.data.uv_layers.active = hull.data.uv_layers['UV_SURFACE_FINISH']
hull.data.uv_layers['UV_SURFACE_FINISH'].active_render = True
bpy.ops.object.select_all(action='DESELECT')
assembly = bpy.data.objects['MOTHERSHIP']
assembly.select_set(True)
for obj in assembly.children_recursive:
    obj.select_set(True)
bpy.context.view_layer.objects.active = hull
formats = [i.identifier for i in bpy.ops.export_scene.gltf.get_rna_type().properties['export_format'].enum_items]
if not formats:
    # glTF's format enumeration is dynamic in this Blender build.
    try:
        bpy.ops.export_scene.gltf(export_format='__ENUM_DISCOVERY__')
    except TypeError as error:
        formats = re.findall(r"'([A-Z_]+)'", str(error))
bpy.ops.export_scene.gltf(filepath=str(root/'godot/assets/mothership.glb'),
    export_format=next(value for value in formats if value == 'GLB'),
    use_selection=True, export_yup=True, export_apply=True,
    export_animations=False, export_cameras=False, export_lights=False)
print('Repaired hangar GLB exported')
