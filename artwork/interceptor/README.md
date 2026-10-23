# Interceptor fighter

The two orange-circled landing supports have been removed and their attachment cuts capped. Both engines now have load-bearing titanium collars, retaining bands and axial ribs overlapping the rear mounts and engine housings. The three-prong silhouette and cream/red/blue paint scheme are retained.

The current revision smooths reconstruction noise, refines broad armor planes, clears the old custom normals, and replaces the noisy source shading with a cleaner repaint. A new non-overlapping UV atlas prevents the source mapping from producing patchy paint. Use `interceptor_game_ready.blend` for the current editable asset.

Both engine housings have also been rotated about their front mounts to remove approximately 3 degrees of outward yaw and 1 degree of vertical tilt. Their fitted exhaust-rim axes now follow the ship's longitudinal axis and the machined collars. The orthographic `renders/godot_top.png` shows the current alignment without perspective convergence. Measurements are in `reports/engine_alignment.json`; the source repaint guide images predate this rigid geometry adjustment.

Open `godot/project.godot` in Godot 4 and run the preview. Drag to orbit, scroll to zoom, press 1/2/3 to inspect a mesh level, or 0 for automatic switching.

| File | Purpose |
| --- | --- |
| `godot/assets/interceptor.glb` | Standalone textured game model; drag directly into Godot |
| `godot/scenes/interceptor.tscn` | CharacterBody3D with three convex collision hulls, automatic LODs, and attachment markers |
| `blender/interceptor_game_ready.blend` | Clean editable game mesh with packed textures |
| `blender/interceptor_clean_high.blend` | Archived first-pass high resolution hull, before the engine and paint revision |
| `blender/interceptor_original.blend` | Untouched source scene |
| `textures/interceptor_repaint_basecolor_4k.png` | Current baked albedo atlas |
| `textures/repaint/` | Four source repaint views used for the current atlas |
| `blender/previous/` | Previous asset and intermediate geometry/bake checkpoints |
| `renders/godot_*.png` | Captures from the actual Godot renderer |
| `reports/` | Blender topology, glTF buffer, and Godot runtime validation |

The game model points along **-Z**, with **+Y up** in Godot. Its origin is at the bounding-box center. Length is **12 m**, chosen because the source has no physical dimensions; width is about 9.31 m. Scale the scene root to change this.

| Detail level | Triangles | Default distance |
| --- | ---: | --- |
| LOD0 | 82,468 | Under 40 m |
| LOD1 | 32,986 | 40–100 m |
| LOD2 | 12,370 | Over 100 m |

LOD0 is 88.2% smaller than the 699,826-triangle source, including the new engine hardware. The textured GLB is about 12.4 MB. The two companion LOD GLBs contain geometry and material slots; `scripts/interceptor.gd` assigns the LOD0 materials so all levels share the same textures. Use the supplied scene for this behavior. Distance thresholds are editable in that script. For integration, copy the `assets`, `scenes`, and `scripts` directories from `godot/` into your project's `res://` root, retaining their paths, then instance `res://scenes/interceptor.tscn`. The asset root has no flight controller; attach your game's movement logic there.

Three coarse convex collision hulls cover the fuselage and each wing. They intentionally bridge local machinery gaps for practical flight collision. `Nose`, `EnginePort`, and `EngineStarboard` are approximate attachment markers for effects and weapons; adjust to your gameplay.

The current base color is baked into a 4096 x 4096 `GameUV` atlas from four cleaned orthographic views. The views were repainted with the built-in imagegen tool and baked using visibility tests so hidden machinery retains appropriate source paint. Exact prompts are saved in `reports/repaint_prompts.md`. Hull roughness is 0.68 and metallic is 0.12; the new engine hardware uses separate titanium materials. The old ORM, normal and base-color maps remain in `textures/` for the archived sources and are not used by the current game material. Removing the reconstructed normal/AO maps avoids reintroducing their marbling. Some larger reconstruction irregularities remain in the machinery and silhouette; this is a surface refinement of the existing model.

The revised main mesh has **zero boundary edges and zero edges with more than two faces**. Engine collars are closed overlapping mechanical shells, as is common for assembled game models. The exported glTF buffers have finite positions, normals and UVs with valid indices. Runtime validation in **Godot 4.7.2 Compatibility** checks all three meshes, their four materials, and collision shapes, including a physics ray query. Preview captures cover the front, rear, side and underside. The restricted execution environment logged user-log/editor-settings, shader-cache and Windows certificate-store access errors; asset import and rendering completed successfully.

For future edits, open the current game `.blend`, run `scripts/export_revision.py` inside Blender, then run `scripts/package_asset.py` in Python to regenerate the collision scene. `scripts/bake_repaint.py` rebuilds the UV atlas and paint from the saved `interceptor_geometry_revised.blend` checkpoint and the four repaint views. These Blender scripts declare the workspace path at their start. `scripts/build_final.py` is the legacy first-pass cleanup recipe and requires the pre-revision material setup. `scripts/check_glb.py` validates the exported buffers; `godot/scripts/validate.gd` validates the imported asset.
