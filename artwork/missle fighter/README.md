# Missile fighter

Open `godot/project.godot` in Godot 4 and run the preview. Drag to orbit, scroll to zoom, press 1/2/3 to inspect each mesh level, or 0 for automatic distance switching.

The source scene is preserved in `blender/missile_fighter_original.blend`. The editable final model is `blender/missile_fighter_game_ready.blend`; its textures are packed. The supplied twin missile banks, cockpit, forward prongs, machinery and engines are retained. No design components were removed.

The game asset faces **-Z**, with **+Y up** in Godot. Its origin lies on the symmetry plane at the original asset origin. The retained half yields a final length of about **15.52 m**, using the original nominal 16 m scale assumption because the source has no physical dimensions. Scale the scene root to suit your game.

Use `godot/assets/missile_fighter.glb` for the standalone textured mesh, or instance `godot/scenes/missile_fighter.tscn` for a CharacterBody3D with three convex collision hulls, three distance meshes and attachment markers. The scene has no flight controller. Copy `godot/assets/`, `godot/scripts/missile_fighter.gd` and `godot/scenes/missile_fighter.tscn` to the matching paths in your Godot project.

The distance meshes share the main mesh material at runtime. Switching distances are 40 m and 100 m. The three collision hulls cover the center and each outer hull; they bridge machinery gaps for practical ship collision. Nose, muzzle, engine and missile-bank markers are approximate effects/gameplay attachment points. Missile-bank markers point upward along their local -Z axis.

Paint is cleaned in six orthographic views and projected with visibility tests into a 4096 x 4096 GameUV atlas; mirrored halves now intentionally share the retained half?s UVs. A dedicated 2048 x 2048 map provides cyan light emission. The old reconstructed normal and ORM maps are archived in `textures/source_*.png`; the final shader uses metallic 0.12 and roughness 0.68 to avoid amplifying their surface noise. This refines the existing reconstruction; some soft panel geometry remains. Geometry, paint, emission and engine placement are now exactly mirrored across X=0.

`renders/` contains source guides and actual Godot captures. `reports/` contains geometry metrics, exported-buffer checks, runtime checks and repaint documentation. `scripts/` contains the reproducible preparation, projection bake, export, scene packaging and validation steps. Blender scripts declare the workspace path at their start. For future edits to the final Blender asset, run `scripts/export_asset.py` inside Blender and then run `scripts/package_asset.py` with Python.

| Detail level | Triangles | Default distance |
| --- | ---: | --- |
| LOD0 | 97,088 | Under 40 m |
| LOD1 | 38,806 | 40-100 m |
| LOD2 | 14,534 | Over 100 m |

The main mesh is 86% smaller than the 699,874-triangle source, with one material and a 14.5 MB standalone GLB. Its final Blender mesh has zero boundary edges and zero edges shared by more than two faces. One tiny isolated doubled triangle was removed as reconstruction debris. Exported buffers have finite positions, unit normals, finite UVs and valid indices. Godot 4.7.2 Compatibility validation checks the imported meshes, emission/albedo maps, LOD ranges, attachment markers and collision response. Six captured views cover the front, rear, top, side and underside. The sandbox logs user-directory, editor-settings, shader-cache and Windows certificate-store errors; asset import, runtime checks and rendering completed.

The symmetric revision retains the port (negative X) half and mirrors it across the centerline. The pre-symmetry asset is preserved in `blender/previous/missile_fighter_before_symmetry.blend`. All three exported meshes have zero reflected position and UV error, measured by `scripts/check_glb.py`. Collisions and paired attachment markers are regenerated for the symmetric hull. The six repaint guides document the previous asymmetric source; the current Blender file, GLBs and Godot captures show the symmetric revision. See `reports/symmetry.json`.

A Blender 5.1 crash occurred while converting a decimated mesh into BMesh. The final export recipe reduces a single half, removes center-plane faces, then mirrors it; the background rebuild completed with all three meshes closed. Later exports use this revised recipe.
