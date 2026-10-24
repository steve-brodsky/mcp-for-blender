# Beam frigate

The supplied beam frigate has been aligned, welded, reduced, flattened, mirrored and given a cleaned paint finish for Godot. The spinal beam aperture, armored hull sections, bridge, antennas, side pods and stern engine banks are preserved. No design components were removed.

Open `godot/project.godot` in Godot 4 and run the preview. Drag to orbit, scroll to zoom, press 1/2/3 to inspect a mesh level and 0 for automatic switching.

![Godot capture](renders/godot_close.png)

| File | Purpose |
| --- | --- |
| `godot/assets/beam_frigate.glb` | Standalone model with embedded paint and emission textures |
| `godot/assets/beam_frigate_lod1.glb`, `beam_frigate_lod2.glb` | Distance meshes (geometry and material slot only) |
| `godot/scenes/beam_frigate.tscn` | CharacterBody3D with automatic LODs, five convex collision hulls and attachment markers |
| `blender/beam_frigate_game_ready.blend` | Current editable game mesh with packed textures |
| `blender/beam_frigate_original.blend` | Untouched supplied scene |
| `blender/beam_frigate_clean_high.blend` | Aligned, welded, scaled full-resolution hull with the source material |
| `blender/beam_frigate_prepared.blend` | Reduced, smoothed port half, before panel flattening |
| `blender/beam_frigate_uv_baked.blend` | Flattened port half with the `GameUV` atlas, plus the high hull for baking |
| `blender/previous/beam_frigate_panels.blend` | Checkpoint right after panel flattening |
| `textures/beam_frigate_basecolor_4k.png` | Current 4096 x 4096 albedo atlas |
| `textures/beam_frigate_emission_2k.png` | Current 2048 x 2048 orange/blue light emission map |
| `textures/source/` | The three original reconstruction maps (albedo, ORM, normal) |
| `textures/work/` | Source albedo baked to `GameUV`, island mask, texel and face class maps |
| `renders/godot_*.png` | Captures from the actual Godot renderer |
| `reports/` | Alignment, geometry, texture, buffer and runtime validation |

The ship points along **-Z**, with **+Y up** in Godot. Its origin lies on the symmetry plane at the bounding-box center. A nominal **48 m length** was chosen because the source has no physical dimensions; this sits between the 12-16 m fighters and the ~100 m carrier and mothership. The mirrored hull measures **47.4 m long x 20.1 m wide x 17.2 m tall**. Scale the scene root to suit your game.

| Detail level | Triangles | Default distance |
| --- | ---: | --- |
| LOD0 | 93,734 | Under 120 m |
| LOD1 | 37,482 | 120-300 m |
| LOD2 | 14,034 | Over 300 m |

The main mesh is 87% smaller than the 699,884-triangle source and uses one PBR material. The main GLB is about 20 MB, mostly the embedded 4K albedo. `godot/scripts/beam_frigate.gd` assigns the main material to the LOD meshes and sets the visibility ranges, which are scaled up from the fighters' 40/100 m for the larger hull. Godot's automatic mesh LOD generation is disabled in the saved import settings because explicit distance meshes are included.

For integration into an existing project, copy `godot/assets/`, `godot/scenes/beam_frigate.tscn` and `godot/scripts/beam_frigate.gd` into the matching `res://assets/`, `res://scenes/` and `res://scripts/` locations. Instance the supplied scene. The asset root contains no movement or AI; attach your logic there. `Nose`, `BeamMuzzle` (the spinal beam aperture), `Bridge`, `EnginePort` and `EngineStarboard` are approximate attachment markers. Engine markers face aft and identify each engine bank rather than every outlet.

The five collision hulls cover the bow, forward armor, midship, stern and the raised bridge. Adjacent sections overlap by 0.5 m. They bridge small machinery gaps for practical ship collision and are coarse gameplay proxies, not exact projectile meshes.

## Mesh cleanup

- **Alignment.** The source was yawed about 45 degrees and slightly rolled. Principal axes set forward (the beam aperture) and up (the bridge and antennas). Yaw, roll and the centerline offset were then refined by minimizing mirrored surface distance. See `reports/source_alignment.json`.
- **Weld.** The source's split UV-seam vertices were welded into one closed hull, and its custom normals were cleared.
- **Reduction and smoothing.** Only the port half is reduced, with mild non-shrinking smoothing that locks creases above 38 degrees.
- **Panel flattening.** The reconstruction left the armor plates lumpy. Near-coplanar faces were grown into 268 plate regions covering about 38% of the surface. Each region got a fitted plane and its vertices were pulled onto it. Shared vertices converge onto the crease or corner between plates. Movement is capped at 14 cm, and a fold check restores any vertex that would flip a triangle. See `reports/panel_flattening.json`.
- **Symmetry.** The port half is mirrored across X=0, giving zero reflected position and UV error in every GLB. The source was lopsided: its starboard mid-ship pod was about 2.2 m wider than the port pod, and the port proportions are kept. See `reports/symmetry.json`.
- **Shading.** Edges sharper than 40 degrees are marked sharp, so plate edges render crisply instead of as soft gradients.

The final mesh has zero boundary edges and zero edges shared by more than two faces, and so do both LODs. Some soft reconstruction forms remain, particularly the drip-like greebles around the stern engine banks; they were kept because they are part of the supplied silhouette.

## Texture cleanup

The half hull was given a new `GameUV` atlas: smart projection, then a concave repack that uses 43% of the sheet. The source albedo was baked onto it selected-to-active from the full-resolution hull. Both halves share the atlas, which doubles texel density.

`scripts/clean_texture.py` then cleans the paint without replacing it:

1. **Classification.** Texels are sorted into ivory armor, red stripe, gunmetal, graphite, orange light and blue light.
2. **Plate majority.** `scripts/classify_faces.py` gives every face, and every flat plate, one majority base paint. This keeps grime patches on armor from being treated as machinery.
3. **Detail-preserving cleanup:**
   - non-local-means denoise;
   - mid-scale blotches and marbling (2.5-24 texels) damped to 45% on armor and 70% on machinery;
   - grey grime on armor lifted 40% toward the typical armor tone;
   - stripe hue evened 40%;
   - fine detail (panel lines, greebles, wear) kept at 100%.
4. **Emission.** The emission map is built from the orange and blue light classes.

A flat per-class repaint was tried first and rejected because it lost the surface detail.

The old normal and ORM maps are archived in `textures/source/` and are not used by the game material because they amplify reconstruction noise. Roughness is 0.62, metallic is 0.15 and emission strength is 2. Some source weathering and reconstruction softness intentionally remain.

## Validation

- **GLB buffers:** `scripts/check_glb.py` confirms finite positions, normals, tangents and UVs, valid indices, embedded 4K/2K textures and exact mirror symmetry for all three GLBs (`reports/glb_validation.json`).
- **Godot 4.7.2 Compatibility:** `godot/scripts/validate.gd` checks all three meshes, triangle counts, LOD ranges, shared materials with albedo and emission, five convex collision shapes, physics ray hits at five stations along the hull, and all markers (`reports/godot_validation.json`).
- **Captures:** beauty, close, rear, side, front, orthographic top and underside views are in `renders/`.

## Rebuilding

Blender scripts declare the workspace path at their start. Run each one with the stated file open:

1. `beam_frigate_original.blend` → `scripts/prepare_asset.py` (alignment, weld, scale, half reduction).
2. `scripts/flatten_panels.py` → `scripts/bake_source.py` (UV atlas, source albedo and island mask).
3. `python scripts/clean_texture.py labels`, then `scripts/classify_faces.py` in Blender, then `python scripts/clean_texture.py paint`.
4. Reopen `beam_frigate_uv_baked.blend` → `scripts/finalize_asset.py` (material, mirror, sharp edges).
5. `scripts/export_asset.py` → `python scripts/package_asset.py` → `python scripts/check_glb.py`.
6. `godot --headless --path godot --editor --import --quit`, then `godot --headless --path godot --script res://scripts/validate.gd`. Captures: `godot --path godot -- --capture=close`.

For texture-only changes, repeat steps 3-5. For later edits to the game mesh, open `beam_frigate_game_ready.blend` and run step 5. When running Godot under a restricted account, set `APPDATA` to `godot/.local_appdata/`.
