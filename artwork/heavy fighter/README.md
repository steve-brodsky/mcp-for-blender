# Heavy fighter

The supplied heavy fighter has been welded, reduced, smoothed, reoriented and repainted for Godot. Its weapons, engine housings and lower machinery are preserved. No design components were removed. The source's separate UV seam vertices become one closed connected hull after welding.

Open `godot/project.godot` in Godot 4 and run the preview. Drag to orbit, scroll to zoom, press 1/2/3 to inspect a mesh level and 0 for automatic switching.

| File | Purpose |
| --- | --- |
| `godot/assets/heavy_fighter.glb` | Standalone model with embedded paint and emission textures |
| `godot/scenes/heavy_fighter.tscn` | CharacterBody3D with automatic LODs and three convex collision hulls |
| `blender/heavy_fighter_game_ready.blend` | Current editable game mesh with packed textures |
| `blender/heavy_fighter_original.blend` | Untouched supplied scene |
| `blender/heavy_fighter_clean_high.blend` | Welded high resolution geometry, before repainting |
| `blender/heavy_fighter_prepared.blend` | Reduced geometry and original UV/material checkpoint for repainting |
| `textures/heavy_fighter_repaint_basecolor_4k.png` | Current 4096 x 4096 albedo atlas |
| `textures/heavy_fighter_emission_2k.png` | Current 2048 x 2048 cyan light emission map |
| `textures/repaint/` | Six orthographic source paint views |
| `renders/godot_*.png` | Captures from the actual Godot renderer |
| `reports/` | Geometry, buffer, material and runtime validation |

The ship points along **-Z**, with **+Y up** in Godot. Its origin is at the bounding-box center. A nominal **16 m length** was chosen because the supplied reconstruction has no physical dimensions; the finished width is about 10.04 m. Scale the scene root to suit your game.

| Detail level | Triangles | Default distance |
| --- | ---: | --- |
| LOD0 | 90,974 | Under 40 m |
| LOD1 | 36,386 | 40-100 m |
| LOD2 | 13,644 | Over 100 m |

The main mesh is 87% smaller than the 699,856-triangle source and uses one PBR material. The main GLB is about 13.5 MB. The companion LOD GLBs contain geometry and material slots; `godot/scripts/heavy_fighter.gd` assigns the main material to them so all three levels share the textures. The supplied scene sets the visibility ranges. Godot's additional automatic mesh LOD generation is disabled in the saved import settings because explicit distance meshes are included.

For integration into an existing project, copy `godot/assets/`, `godot/scenes/heavy_fighter.tscn` and `godot/scripts/heavy_fighter.gd` into the matching `res://assets/`, `res://scenes/` and `res://scripts/` locations. Instance the supplied scene. The standalone GLB can also be dragged directly into a scene. The asset root contains no flight controller; attach your movement logic there. `Nose`, `MuzzlePort`, `MuzzleStarboard`, `EnginePort` and `EngineStarboard` are approximate gameplay attachment markers. Engine markers identify each bank rather than every individual outlet.

The three collision hulls cover the central fuselage and each outer hull. They deliberately bridge small machinery gaps for practical flight collision. They are coarse gameplay proxies rather than exact projectile collision meshes.

Paint was cleaned in six orthographic views using the built-in imagegen tool, then projected into a new `GameUV` atlas with visibility weighting. [Exact repaint prompts](reports/repaint_prompts.md) are included. After baking, the ship was bisected at X=0 and the port (negative X) half mirrored to make both sides identical. Geometry, engines, paint and emission are now bilaterally symmetric. Mirrored halves intentionally share the retained half's UV coordinates. The six paint guides and earlier checkpoints document the previous asymmetric source; the current Blender asset, GLBs and Godot captures show the symmetric revision. The previous game mesh is preserved in `blender/previous/heavy_fighter_before_symmetry.blend`, with measurements in `reports/symmetry.json`.

The old normal and ORM maps are archived as `textures/source_*.png` and are not used by the current game material because they amplify the original surface noise. Roughness is 0.68, metallic is 0.12, and cyan inset lights use a dedicated emission map. Some soft panel edges and reconstruction irregularities remain in the retained geometry.

The rear engine banks use their original detailed texture mapping recovered from the aligned prepared mesh and baked into the current atlas. This restores the weathered metal and cream armor covers while removing the misplaced roof projection across upper nozzle interiors. The flat graphite refinish was reverted, including its emission changes. Geometry and shared mirrored UVs are unchanged. See `renders/godot_engine_close.png` and `reports/engine_texture_correction.json`. To rebuild this repair, open `blender/previous/heavy_fighter_before_engine_texture_fix.blend` and run `scripts/restore_engine_uvs.py`; normal later edits only require `export_asset.py`. `fix_engine_projection.py` and `refinish_engine_surfaces.py` record superseded attempts and should not be run on the current asset. The original source texture retains some reconstruction softness and weathering.

The final mesh has zero boundary edges and zero edges shared by more than two faces. Exported buffers have finite coordinates, normals and UVs, valid triangle indices, and embedded 4K/2K textures. Validation in Godot 4.7.2 Compatibility checks all three meshes, shared materials, imported emission and collision shapes, including a physics ray query. Front, rear, side, underside and orthographic top captures are supplied. The restricted execution environment logs editor-settings, user-log, shader-cache and Windows certificate-store access errors; asset import, rendering and the runtime checks complete successfully.

For later edits, open `heavy_fighter_game_ready.blend`, run `scripts/export_asset.py` in Blender, then run `scripts/package_asset.py` in Python. To redo the repaint bake, open `heavy_fighter_prepared.blend` and run `scripts/bake_repaint.py`, followed by export and packaging. To rebuild the geometry from the original, open `heavy_fighter_original.blend` and run `scripts/prepare_asset.py`; it applies the saved source alignment. Blender scripts declare the workspace path at their start. `scripts/check_glb.py` validates exported buffers; `godot/scripts/validate.gd` validates the imported asset.
