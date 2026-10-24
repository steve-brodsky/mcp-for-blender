# Torpedo bomber

The supplied torpedo bomber has been aligned, welded, reduced, flattened, mirrored and given a cleaned paint finish for Godot. The cockpit, both wing nacelles with their intake grilles, the dorsal machinery spine, the ventral keel with its pylons, the aft engine block and the aft ventral pod are all preserved. No design components were removed. Two torpedoes hang under the keel, and the bomber has no other moving parts or animation.

Open `godot/project.godot` in Godot 4 and run the preview. Drag to orbit and scroll to zoom. Press T to load both torpedoes and F to launch one (the sides alternate). Press 1/2/3 to inspect a mesh level and 0 for automatic switching.

![Godot capture](renders/godot_close.png)

![Torpedoes on the hardpoints](renders/godot_loaded.png)

| File | Purpose |
| --- | --- |
| `godot/assets/torpedo_bomber.glb` | Bomber with embedded paint and emission textures |
| `godot/assets/torpedo_bomber_lod1.glb`, `torpedo_bomber_lod2.glb` | Distance meshes (geometry and material slot only) |
| `godot/scenes/torpedo_bomber.tscn` | CharacterBody3D with LODs, seven convex collision hulls, torpedo hardpoints and markers |
| `godot/scripts/torpedo_bomber.gd` | `TorpedoBomber` API: mount and launch torpedoes, signals |
| `godot/scripts/torpedo_standin.gd` | KR45-sized stand-in torpedo, used only by the preview and validation |
| `blender/torpedo_bomber_game_ready.blend` | Current editable game mesh with packed textures |
| `blender/torpedo_bomber_original.blend` | Untouched supplied scene |
| `blender/torpedo_bomber_clean_high.blend` | Aligned, welded, scaled full-resolution bomber |
| `blender/torpedo_bomber_prepared.blend`, `_uv_baked.blend` | Reduced and flattened port half; then unwrapped and baked |
| `textures/torpedo_bomber_basecolor_4k.png`, `_emission_2k.png` | Current albedo and emission atlases |
| `textures/source/` | The three original reconstruction maps (albedo, ORM, normal) |
| `textures/work/` | Baked source albedo, island and hit masks, position and normal maps, texel and face class maps |
| `renders/godot_*.png` | Captures from the actual Godot renderer, including the torpedoes loaded and a launch |
| `reports/` | Alignment, geometry, texture, hardpoint, GLB and Godot validation |

The bomber points along **-Z** (the cockpit nose), with **+Y up** in Godot. Its origin is on the symmetry plane at the bounding-box centre. Port is -X.

A nominal **18 m length** was chosen because the source has no physical dimensions. That makes it a heavy strike craft, just above the 16 m heavy fighter and well below the 48 m beam frigate. The canopy is then about 3 m long, room for a crew of two. The finished bomber measures **18.0 m long x 14.1 m wide x 5.3 m tall**. Scale the scene root to suit your game.

| Detail level | Triangles | Default distance |
| --- | ---: | --- |
| LOD0 | 91,928 | Under 45 m |
| LOD1 | 36,768 | 45-110 m |
| LOD2 | 13,780 | Over 110 m |

The source was a single 699,814-triangle mesh. The game mesh is 87% smaller and uses one PBR material. Roughness is 0.62, metallic 0.15 and emission strength 2, as on the other ships. The main GLB is about 17.5 MB, mostly the embedded 4K albedo.

Godot's automatic mesh LOD generation is disabled in the saved import settings because explicit distance meshes are included. The textures use VRAM compression, as on the supply drone.

## Integration

Copy `godot/assets/torpedo_bomber*.glb`, `godot/scenes/torpedo_bomber.tscn` and `godot/scripts/torpedo_bomber.gd` into the matching `res://` folders and instance `torpedo_bomber.tscn`. The root has no movement or AI; attach your logic there.

```gdscript
var torpedo := preload("res://scenes/kr45_fusion_torpedo.tscn").instantiate()
bomber.mount_torpedo(torpedo)          # first free hardpoint, or pass &"port" / &"starboard"
bomber.launch_torpedo()                # alternates sides; returns the torpedo, or null when empty
bomber.has_torpedo(side); bomber.get_torpedo(side); bomber.get_loaded_sides(); bomber.get_hardpoint(side)
signal torpedo_mounted(torpedo, side)  # the torpedo is a child of its hardpoint
signal torpedo_launched(torpedo, side) # re-parented to the bomber's parent and fired forward
```

**Torpedoes.** The hardpoints are sized for the KR45 fusion torpedo from `artwork/missles/` (0.83 m x 6.44 m, origin at its centre, forward -Z). A mounted torpedo sits with its centre on `TorpedoPort` or `TorpedoStarboard`.

`launch_torpedo()` releases the torpedo in place, re-parents it to the bomber's parent and calls its `launch(direction, shooter)`. That is the entry point of the missiles' `projectile.gd`, with the bomber's forward axis as the direction and the bomber as the shooter, so the torpedo ignores it. Any other node can be mounted too; it is simply released if it has no `launch()`.

The KR45 GLBs are not in this checkout, so the preview and validation use `TorpedoStandin`, a capsule of the same size with the same `launch()` call.

**Hardpoints.** The ventral keel carries two rails side by side, with pylons under them. The rail fronts sit behind the nose chin, so a torpedo cannot leave straight off the rails. Instead the torpedoes hang under the pylons, 1.2 m apart, 0.6 m either side of the centreline:

- The top of each torpedo sits 5 cm below the lowest keel surface over its footprint.
- Ray casts confirm a clear path forward (`reports/hardpoints.json`).
- In Godot, both mounted torpedoes clear the bomber's collision hulls.

Markers:

- `TorpedoPort`, `TorpedoStarboard`: the torpedo hardpoints, facing forward.
- `Nose`: the tip of the nose.
- `Cockpit`: under the canopy.
- `EnginePort`, `EngineStarboard`: the two main nozzles on the aft face of the engine block, facing aft.
- `NacelleExhaustPort`, `NacelleExhaustStarboard`: the rear ends of the wing nacelles, facing aft.

The engine and exhaust markers are approximate VFX points rather than modelled thrust axes.

The seven collision hulls are the nose, the midbody, the tail, the two wing spars and the two nacelles. The midbody covers the wing roots and keel, and the tail covers the engine block and aft ventral pod. The midbody hull stops above the front lip of the aft pod (the tail hull covers it), so its underside stays above the slung torpedoes. These are coarse gameplay proxies, not exact projectile meshes.

## Mesh cleanup

- **Alignment.** The source was yawed about 45 degrees and pitched about 20 degrees. Principal axes were skewed because the fuselage length and the nacelle span are close. So, as on the construction drone, up was taken from the dominant top and bottom armor plates and side from the fuselage flanks. Forward is the narrow cockpit nose. Yaw, roll and the centreline offset were then refined by minimising mirrored surface distance (a further 0.19 degrees of yaw and 0.5 degrees of roll). See `reports/source_alignment.json`.
- **Weld.** The source's split UV-seam vertices were welded into one closed shell, and its custom normals were cleared. The weld left one edge shared by four faces, where two surface sheets touched; that edge was split so each sheet closes on its own.
- **Reduction, smoothing and panel flattening.** These are the supply drone methods, applied to the port half: half-only reduction, crease-locked non-shrinking smoothing, and plate regions pulled onto fitted planes. The plate thresholds and the 6 cm movement cap sit between the drones' and the frigate's. 251 plates cover 53% of the surface (`reports/mesh_reduction.json`). Every game vertex lies within 6.1 cm of the source surface (median 3.1 mm, 99th percentile 2.9 cm).
- **Symmetry.** Mirrored across X=0, with zero reflected position and UV error in every GLB.
- **Shading.** Edges sharper than 40 degrees are marked sharp.

The mesh and both LODs have zero boundary edges and zero edges shared by more than two faces. Some soft reconstruction forms remain, mostly in the dorsal spine machinery and around the aft engine block. They were kept as part of the supplied silhouette.

## Texture cleanup

The port half has a new 4096 `GameUV` atlas, using 49% of the sheet. The source albedo was baked onto it selected-to-active, and both halves share the atlas.

`scripts/clean_texture.py` uses the supply drone method with a bomber palette sampled from the reference render:

1. **Classification.** Seven classes: graphite, gunmetal, ivory armor, red stripe, yellow hazard paint, amber light and blue light.
2. **Plate majority.** `scripts/classify_faces.py` gives every face and every flat plate one base paint: graphite, gunmetal or armor. This keeps grime patches on the ivory from turning into grey camouflage. Red stripes stay texel-accurate, but only around faces voted red, so rust and brown grime stay armor. Hazard paint and lights stay texel-accurate everywhere.
3. **Detail-preserving cleanup.**
   - Painted surfaces (armor, stripe and hazard paint): blotches (2.5-24 texels) are damped to 45%, grime on armor is lifted 40%, and fine detail is kept at 100%.
   - Machinery: blotches are damped to 25% and fine detail kept at 60%.
   - Each paint is pulled towards its palette colour. The source's dark maroon stripe is lifted most, towards the reference's brick red.
4. **Lights.** Unlike the drones' sources, this source keeps its lamps:
   - **Amber lamps** are bright saturated texels and are kept per texel: the nose lamps, the nacelle front and tail lamps, the keel strip and the small lamps along the hull.
   - **Blue glows** survive only as faint cyan tints. Those spots are kept and lit: the slots under the wings at the nacelle roots, the flanks of the aft engine block, and small sensors on the centreline.
   - **The nacelle intake grilles** are dark in the source but glow blue in the reference, so they are placed from the baked position and normal maps (the floor of each intake recess). The source paints their light tubes as dark navy bars, so the darkest texels glow brightest and the grille reads as three bright bars, as in the reference.

The reference also shows a few small blue slots on the fuselage flanks. The source has no trace of them, so they were not invented. See `reports/texture_cleanup.json` for the class coverage and the intake region.

The old normal and ORM maps are archived in `textures/source/` and are not used, because they amplify reconstruction noise.

## Validation

- **Blender:** the half and the mirrored mesh are closed, and mirror error is zero (`reports/mesh_reduction.json`, `symmetry.json`). The torpedo footprint and forward path were ray-tested against the game mesh (`reports/hardpoints.json`).
- **GLB buffers:** `scripts/check_glb.py` confirms the following for all three GLBs (`reports/glb_validation.json`):
  - finite positions, normals and UVs, and valid indices;
  - exact mirror symmetry including UVs;
  - embedded 4K/2K textures.
- **Godot 4.7.2 Compatibility:** `godot/scripts/validate.gd` runs 36 checks with 0 failures (`reports/godot_validation.json`). It covers:
  - the LODs and the shared material;
  - size and orientation, and all markers;
  - seven convex hulls, with ray hits across the nose, body, tail, wings and nacelles;
  - mounting two torpedoes, refusing a third, and both staying seated on their hardpoints;
  - both mounted torpedoes clearing the bomber's hulls, with a clear path forward;
  - launching both: sides alternate, each torpedo is released to the world and flies along the bomber's forward axis.
- **Captures:** close, front, side, rear, top and underside views, the loaded torpedoes and a launch are in `renders/`.

## Rebuilding

Blender scripts declare the workspace path at their start. Run them with the stated file open; Python-side scripts need numpy, opencv-python, scipy and Pillow.

1. `torpedo_bomber_original.blend` → `scripts/align_source.py` → `scripts/prepare_asset.py`.
2. `scripts/reduce_meshes.py` → `scripts/bake_source.py`.
3. `python scripts/clean_texture.py labels`, then `scripts/classify_faces.py` in Blender, then `python scripts/clean_texture.py paint`.
4. Reopen `torpedo_bomber_uv_baked.blend` → `scripts/finalize_asset.py` → `scripts/export_asset.py`.
5. `python scripts/package_asset.py` → `python scripts/check_glb.py`.
6. `godot --headless --path godot --editor --import --quit`, then `godot --headless --path godot --script res://scripts/validate.gd`. Captures: `godot --path godot -- --capture=close` (or `front`, `side`, `rear`, `top`, `underside`, `loaded`, `launch`).

For texture-only changes, repeat steps 3-6. When running Godot under a restricted account, set `APPDATA` to `godot/.local_appdata/`.
