# Point defense corvette

The supplied corvette has been aligned, welded, reduced, flattened, mirrored and given a cleaned paint finish for Godot. The prow, the spine with its sensor mast, both disc lobes, both engine pods, the ventral keel and all eight turret sockets are preserved. No design components were removed. The hull has no moving parts or animation. Its point defense turrets are separate assets: the corvette provides eight sockets for them, four on the dorsal deck and four on the ventral deck, and an API to seat and aim them.

Open `godot/project.godot` in Godot 4 and run the preview. Drag to orbit and scroll to zoom. Press T to make the turrets track a drone that weaves over and under the hull, and hold Space to fire. Press R to remove or refit the turrets. Press 1/2/3 to inspect a mesh level and 0 for automatic switching.

![Godot capture](renders/godot_close.png)

| Underside | Engaging a target above |
| --- | --- |
| ![underside](renders/godot_underside.png) | ![tracking](renders/godot_track_top.png) |

The preview turrets are the mounted turrets collection's gatling at 0.75 scale. They stand in for the point defense turret and are not part of the corvette asset (see **Turrets** below).

| File | Purpose |
| --- | --- |
| `godot/assets/pd_corvette.glb` | Corvette with embedded paint and emission textures |
| `godot/assets/pd_corvette_lod1.glb`, `pd_corvette_lod2.glb` | Distance meshes (geometry and material slot only) |
| `godot/scenes/pd_corvette.tscn` | CharacterBody3D with LODs, nine convex collision hulls, eight turret sockets and markers |
| `godot/scripts/pd_corvette.gd` | `PointDefenseCorvette` API: mount, remove and aim turrets, line-of-fire checks, signals |
| `godot/preview_only/` | Copy of the gatling turret and `mounted_turret.gd`, used only by the preview and validation |
| `blender/pd_corvette_game_ready.blend` | Current editable game mesh with packed textures |
| `blender/pd_corvette_original.blend` | Untouched supplied scene |
| `blender/pd_corvette_clean_high.blend` | Aligned, welded, scaled full-resolution corvette |
| `blender/pd_corvette_prepared.blend`, `_uv_baked.blend` | Reduced and flattened port half; then unwrapped and baked |
| `textures/pd_corvette_basecolor_4k.png`, `_emission_2k.png` | Current albedo and emission atlases |
| `textures/source/` | The three original reconstruction maps (albedo, ORM, normal) |
| `textures/work/` | Baked source albedo, island and hit masks, position and normal maps, texel and face class maps |
| `renders/godot_*.png` | Captures from the actual Godot renderer, with and without turrets, and tracking targets above and below |
| `reports/` | Alignment, geometry, texture, hardpoint, GLB and Godot validation |

The corvette points along **-Z** (the prow), with **+Y up** in Godot. Its origin is on the symmetry plane at the bounding-box centre. Port is -X.

A nominal **32 m length** was chosen because the source has no physical dimensions. That puts it well above the 18 m torpedo bomber and 16 m heavy fighter, and at two thirds of the 48 m beam frigate. The finished corvette measures **32.0 m long x 28.0 m wide x 9.7 m tall**. Scale the scene root to suit your game; the turret sockets scale with it.

| Detail level | Triangles | Default distance |
| --- | ---: | --- |
| LOD0 | 112,174 | Under 80 m |
| LOD1 | 44,844 | 80-200 m |
| LOD2 | 16,802 | Over 200 m |

The source was a single 699,882-triangle mesh. The game mesh is 84% smaller and uses one PBR material. Roughness is 0.62, metallic 0.15 and emission strength 2, as on the other ships. The main GLB is about 20 MB, mostly the embedded 4K albedo. LOD0 is a little heavier than the 92k fighters and bomber because the eight socket turntables are dense in detail.

Godot's automatic mesh LOD generation is disabled in the saved import settings because explicit distance meshes are included. The textures use VRAM compression.

## Integration

Copy `godot/assets/pd_corvette*.glb`, `godot/scenes/pd_corvette.tscn` and `godot/scripts/pd_corvette.gd` into the matching `res://` folders and instance `pd_corvette.tscn`. The root has no movement or AI; attach your logic there.

```gdscript
corvette.mount_turret(turret)                    # first free socket; or pass a socket name
corvette.mount_turret(turret, &"TurretBottomAftPort", 0.75)   # optional uniform turret scale
corvette.remove_turret(socket)                   # returns the turret, detached
corvette.aim_turrets_at(world_point)             # call each frame; returns the sockets engaging
corvette.clear_turret_targets()
corvette.has_line_of_fire(socket, world_point)   # false when the corvette's own hull is in the way
corvette.get_socket(socket); corvette.get_turret(socket); corvette.has_turret(socket)
corvette.get_occupied_sockets(); corvette.is_ventral(socket)
signal turret_mounted(turret, socket)            # the turret is a child of the socket marker
signal turret_removed(turret, socket)
```

**Sockets.** `PointDefenseCorvette.SOCKETS` lists the eight Marker3D names, dorsal first:

| Socket | Godot position (port; starboard mirrors x) | Seat diameter | Clear arc, level / 15° elevation |
| --- | --- | ---: | --- |
| `TurretTopForePort` / `...Starboard` | (∓5.99, 2.12, -5.80) | 3.0 m | 75% / 100% |
| `TurretTopAftPort` / `...Starboard` | (∓7.16, 2.87, 2.21) | 3.2 m | 90% / 100% |
| `TurretBottomForePort` / `...Starboard` | (∓5.91, -2.30, -5.76) | 3.2 m | 75% / 100% |
| `TurretBottomAftPort` / `...Starboard` | (∓7.19, -4.04, 2.24) | 3.2 m | 100% / 100% |

- Each socket is a raised turntable, 0.7-0.8 m proud of the surrounding deck, with a 3.0-3.2 m flat seat and a chamfer down to the deck.
- The marker sits on the seat's centre, with +Y pointing out of the hull and -Z forward. The ventral markers are rolled 180 degrees about the forward axis, so a turret seated on them hangs upside down and still faces the prow.
- The seat is the socket's outer ring. A low hub dome rises up to 0.18 m above it in the middle, which a turret base covers.
- A turret is seated by making it a child of the marker: its origin should be the centre of its base bottom, with its gun pointing along -Z at rest. That is the layout of the mounted turrets collection.
- The clear arcs are measured 1.2 m above each seat, every 5 degrees of azimuth (`reports/hardpoints.json`). Level fire from the fore sockets is blocked across the spine, and from the dorsal aft sockets partly by the spine machinery. Every socket is clear all round at 15 degrees of elevation.

**Turrets.** Any Node3D can be mounted. `aim_turrets_at()` drives turrets that have the mounted turrets collection's API (`aim_at`, `clear_target`, and optionally `can_reach`). A turret engages when it can reach the point and `has_line_of_fire()` finds no part of the corvette's collision hulls in the way; the others drop their target. Mounted turrets never block each other's line of fire.

The point defense turret itself is not part of this asset. A turret built for these sockets should have a base no wider than **3.0 m**. The existing mounted turrets have a 4.0 m base and fit at `turret_scale = 0.75`, which is how the preview uses the gatling. Their hitboxes scale with them (checked in Godot: the base cylinder's top drops from 0.98 m to 0.735 m).

Other markers:

- `Nose`: the tip of the prow.
- `EnginePort`, `EngineStarboard`: the centres of the engine pods' stern recesses, facing aft.
- `NozzlePort`, `NozzleStarboard`: the two small nozzles either side of the centreline stern block, facing aft.

The engine markers are approximate VFX points rather than modelled thrust axes.

The nine collision hulls are the prow, spine and stern down the centreline, and on each side a fore disc lobe, an aft disc lobe and an engine pod. They are coarse gameplay proxies, not exact projectile meshes. Each socket seat lies within 0.25 m of the hull surface.

## Mesh cleanup

- **Alignment.** The source was pitched 20.2 degrees nose-down and nearly unyawed. The hull is a flat disc, so up was taken from the dominant dorsal and ventral armor plates, which agree with the thinnest principal axis. Forward is the longest principal axis, towards the prow. Yaw, roll and the centreline offset were then refined by minimising mirrored surface distance (a further 0.44 degrees of yaw). See `reports/source_alignment.json`.
- **Weld.** The source's split UV-seam vertices were welded into one closed shell, and its custom normals were cleared. Unlike the bomber's, the weld left no edges shared by more than two faces.
- **Reduction, smoothing and panel flattening.** These are the torpedo bomber methods, applied to the port half. The plate thresholds and the 9 cm movement cap sit between the bomber's and the frigate's. 433 plates cover 52% of the surface (`reports/mesh_reduction.json`). Every game vertex lies within 9.5 cm of the source surface (median 6 mm, 99th percentile 4.6 cm).
- **Symmetry.** Mirrored across X=0, with zero reflected position and UV error in every GLB. Under the keel, two thin sheets meet the symmetry plane along one edge. Collapsing in-plane edges there creates a new in-plane edge, so the collapse repeats until none remain; otherwise that edge would be shared by four faces once mirrored.
- **Shading.** Edges sharper than 40 degrees are marked sharp.

The mesh and both LODs have zero boundary edges and zero edges shared by more than two faces. Some soft reconstruction forms remain, mostly in the spine machinery and the prow. They were kept as part of the supplied silhouette.

## Texture cleanup

The port half has a new 4096 `GameUV` atlas, using 45% of the sheet. The source albedo was baked onto it selected-to-active, and both halves share the atlas.

`scripts/clean_texture.py` uses the torpedo bomber method with a palette sampled from the two reference renders:

1. **Classification.** Six classes: graphite, gunmetal, tan armor, red stripe, amber light and blue light. This source is darker than the bomber's and has no hazard paint, so the thresholds were re-measured on the bake.
2. **Plate majority.** `scripts/classify_faces.py` gives every face and every flat plate one base paint: graphite, gunmetal or armor. Red stripes stay texel-accurate, but only around faces voted red. Lights stay texel-accurate everywhere.
3. **Grime blotches.** The source smears dark grime across curved tan panels, such as the engine pods and the disc rims, where the flat plates cannot reach. Smooth surfaces are therefore grown across edges creased less than 25 degrees. Inside a surface that is at least half armor, each connected dark patch under 6 m² is repainted armor (143 patches). The large dark deck rings around the turret sockets stay dark, as in the reference.
4. **Detail-preserving cleanup.**
   - Painted surfaces (armor and stripe): blotches (2.5-24 texels) are damped to 45%, grime on armor is lifted 80% (the bomber used 40%), and fine detail is kept at 100%.
   - Machinery: blotches are damped to 25% and fine detail kept at 60%.
   - Each paint is pulled towards its palette colour, and the dark maroon stripe is lifted towards the reference's brick red.
   - The source tan was too dark and brown even after that, so a per-channel gain puts the armor median on the palette while keeping its panel-to-panel wear. The palette tan is the mounted turrets' armor colour, (0.72, 0.61, 0.47), so the hull and its turrets share one paint scheme.
5. **Lights.**
   - **Amber lamps** survive in the source as about 65 small saturated blobs and are kept per texel: the slit lamps on the socket turntables, along the hull flanks and on the prow.
   - **Blue lamps** survive only as a few faint cyan tints (822 texels, on the pod corners). They are kept and lit.
   - **The engines** are dark in the source but glow blue in the reference. They are placed from the baked position and normal maps: each engine pod's stern recess, and the two small nozzles beside the centreline stern block. The round nozzles burn brightest, fading towards the recess walls.

The reference also shows blue lamps beside the front grilles of the disc lobes. The source has no trace of them, so they were not invented. See `reports/texture_cleanup.json` for the class coverage and the engine regions.

The old normal and ORM maps are archived in `textures/source/` and are not used, because they amplify reconstruction noise.

## Validation

- **Blender:** the half and the mirrored mesh are closed, and mirror error is zero (`reports/mesh_reduction.json`, `symmetry.json`). The socket centres were found by maximising the rotational symmetry of the height map around each one; the dorsal and ventral pairs line up to within 8 cm. The firing arcs were ray-tested against the game mesh (`reports/hardpoints.json`).
- **GLB buffers:** `scripts/check_glb.py` confirms the following for all three GLBs (`reports/glb_validation.json`):
  - finite positions, normals and UVs, and valid indices;
  - exact mirror symmetry including UVs;
  - embedded 4K/2K textures.
- **Godot 4.7.2 Compatibility:** `godot/scripts/validate.gd` runs 29 checks with 0 failures (`reports/godot_validation.json`). It covers:
  - the LODs and the shared material;
  - size and orientation, and all markers;
  - the eight sockets: mirrored pairs, dorsal up, ventral down, all facing forward, each seat on the collision surface;
  - nine convex hulls, with ray hits across the prow, spine, stern, disc lobes and pods;
  - mounting eight turrets in order, refusing a ninth, each seated and oriented on its socket, then removal and remounting;
  - the 0.75-scale gatling base fitting the seat;
  - a target above engaged only by dorsal turrets, one below only by ventral turrets, and the hull blocking fire across the deck;
  - an inverted ventral turret's bore pointing at a target below.
- **Captures:** close, bare, front, side, rear, top, underside, socket close-up, and tracking above and below are in `renders/`.

## Rebuilding

Blender scripts declare the workspace path at their start. Run them with the stated file open; Python-side scripts need numpy, opencv-python, scipy and Pillow.

1. `pd_corvette_original.blend` → `scripts/align_source.py` → `scripts/prepare_asset.py`.
2. `scripts/reduce_meshes.py` → `scripts/bake_source.py`.
3. `python scripts/clean_texture.py labels`, then `scripts/classify_faces.py` in Blender, then `python scripts/clean_texture.py paint`.
4. Reopen `pd_corvette_uv_baked.blend` → `scripts/finalize_asset.py` → `scripts/export_asset.py`.
5. `python scripts/package_asset.py` → `python scripts/check_glb.py`.
6. `godot --headless --path godot --editor --import --quit`, then `godot --headless --path godot --script res://scripts/validate.gd`. Captures: `godot --path godot -- --capture=close` (or `bare`, `front`, `side`, `rear`, `top`, `underside`, `sockets`, `track_top`, `track_bottom`).

For texture-only changes, repeat steps 3-6. `classify_faces.py` switches Blender to Cycles for its bake. When running Godot under a restricted account, set `APPDATA` to `godot/.local_appdata/`.
