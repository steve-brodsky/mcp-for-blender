# Flak corvette and flak turret

Two game-ready Godot 4 assets.

- **The flak corvette.** The supplied mesh was aligned, cleaned of its detached chunk, mirrored, reduced and repainted. It is a rigid hull with eight turret seats on its flanks, four each side.
- **The flak turret.** This is a new twin heavy flak gun built for those seats. Its guns elevate a full 90 degrees, so they can fire straight out of the flank as well as along it.

The turret is a separate asset that mounts on the corvette's sockets.

Open `godot/project.godot` in Godot 4 and run the preview. Drag to orbit and scroll to zoom. Press T to make the turrets track a drone circling the ship, and hold Space to fire. Press R to remove or refit the turrets. Press 1/2/3 to inspect a mesh level and 0 for automatic switching.

![Godot capture](renders/godot_close.png)

| Port seats (two turrets removed) | Flak turret at 90 degrees |
| --- | --- |
| ![sockets](renders/godot_sockets.png) | ![turret](renders/godot_turret_90.png) |

| File | Purpose |
| --- | --- |
| `godot/assets/flak_corvette.glb` | Corvette with embedded paint and emission textures |
| `godot/assets/flak_corvette_lod1.glb`, `_lod2.glb` | Distance meshes (geometry and material slot only) |
| `godot/scenes/flak_corvette.tscn` | CharacterBody3D with LODs, seven convex collision hulls, eight turret sockets and effect markers |
| `godot/scripts/flak_corvette.gd` | `FlakCorvette` API: mount, remove and aim turrets, line-of-fire checks, signals |
| `godot/assets/flak_turret.glb` | Turret pivot hierarchy, meshes, `scan` and `fire` clips, embedded basecolor, emission and ORM |
| `godot/scenes/flak_turret.tscn` | Ready-to-use turret (`FlakTurret` script, elevation -10 to 90 degrees) |
| `godot/scripts/flak_turret.gd` | `FlakTurret` API: aiming, firing, signals, muzzle flashes, hitboxes |
| `godot/scripts/preview.gd`, `validate.gd` | Preview and capture scene, and the headless validation |
| `blender/flak_corvette_game_ready.blend`, `flak_turret_game_ready.blend` | Current editable assets with packed textures |
| `blender/flak_corvette_original.blend` | Untouched supplied scene |
| `blender/flak_corvette_clean_high.blend`, `_seated_high.blend` | Aligned, chunk-free full-resolution hull; then with the flat turret seats |
| `blender/flak_corvette_prepared.blend`, `_uv_baked.blend` | Reduced port half; then unwrapped and baked |
| `blender/flak_turret_high.blend`, `_uv_baked.blend` | Built turret; then unwrapped and baked |
| `textures/flak_corvette_basecolor_4k.png`, `_emission_2k.png` | Corvette albedo and emission atlases |
| `textures/flak_turret_basecolor_2k.png`, `_emission_2k.png`, `_orm_1k.png` | Turret maps |
| `textures/work/` | Bakes, masks, position and normal maps, texel and face class maps |
| `renders/godot_*.png` | Captures from the actual Godot renderer |
| `reports/` | Alignment, reduction, seats, hardpoints, textures, turret build, clearance and export, GLB and Godot validation |

## The corvette

The corvette points along **-Z** (the prow), with **+Y up** in Godot. Its origin is on the symmetry plane at the bounding-box centre. Port is -X.

It is set to the point defense corvette's nominal **32 m length**, because the source has no physical dimensions. It is a tall, narrow slab, unlike the point defense corvette's disc, and measures **32.0 m long x 7.0 m wide x 13.8 m tall**. Scale the scene root to suit your game; the turret sockets scale with it.

| Detail level | Triangles | Default distance |
| --- | ---: | --- |
| LOD0 | 81,856 | Under 80 m |
| LOD1 | 32,726 | 80-200 m |
| LOD2 | 12,262 | Over 200 m |

The source was a single 699,826-triangle mesh. The game mesh is 88% smaller and uses one PBR material. Roughness is 0.62, metallic 0.15 and emission strength 2, as on the other ships. Godot's automatic mesh LODs are disabled in the saved import settings, because explicit distance meshes are included. The textures use VRAM compression.

### Mesh cleanup

- **Detached chunk.** Welding the source's split UV seams leaves two closed shells: the 513k-triangle hull and a 187k-triangle chunk hanging off the port quarter. The chunk is a reconstruction artifact and was deleted.
- **Alignment.** The source was turned well off its axes in yaw and pitched 10.5 degrees nose-down. The side axis comes from the two big flank plates, up from the dorsal deck plates and forward towards the twin-beaked prow. Roll and the centreline offset were then refined by minimising mirrored surface distance (`reports/source_alignment.json`).
- **Symmetry.** The port flank, where the chunk hung, is also damaged: its lower aft turret socket came out as a flat hatch. The starboard flank has all four sockets, so the starboard half was kept and mirrored. Reflected position and UV error is zero in every GLB.
- **Reduction, smoothing and panel flattening.** These are the point defense corvette's methods and thresholds, applied to the kept half. 238 plates cover 60% of the surface. Every game vertex lies within 8.7 cm of the source surface (median 5 mm, 99th percentile 4.5 cm; `reports/mesh_reduction.json`).
- **Validity.** Decimation left two zero-volume pillows: identical tiny triangles back to back, touching the hull only at vertices. The glTF exporter's `Mesh.validate()` silently dropped one face of each, which opened the mesh. Both faces of each pair are now removed, and the finalize step asserts that `validate()` would change nothing.
- **Shading.** Edges sharper than 40 degrees are marked sharp.

The mesh and both LODs have zero boundary edges and zero edges shared by more than two faces.

### Turret seats

Each source socket was a boss with two lugs and a raised collar around a well. A stub gun stood 0.8 m proud of the flank in it, and a mounted turret would have sat on that stub. `scripts/seat_sockets.py` turns each socket into a flat mounting seat with two manifold booleans on the closed high-resolution hull:

1. a cylinder on the socket axis cuts the collar and stub off above the seat plane;
2. a chamfered turntable fills the well and gives a flat seat 3.0 m across, the point defense corvette's seat size.

The socket centres were found by maximising the rotational symmetry of a ray-cast depth map of each socket. They were then put on one grid: fore and aft, upper and lower. No centre moved more than 6 cm (`reports/seats.json`).

### Texture cleanup

The port half has a 4096 `GameUV` atlas, using 52% of the sheet; both halves share it. The source albedo was baked onto it from the untouched high-resolution hull. `scripts/clean_texture.py` follows the point defense corvette's method:

- **Palette.** The source armor is a near-grey off-white, but every other ship and turret in `artwork/` wears the same sand tan (armor b* 16-22). The armor is therefore pulled onto the fleet palette: tan (0.72, 0.61, 0.47), graphite, gunmetal and brick red, as on the point defense corvette and the mounted turrets. The finished armor median is (0.73, 0.62, 0.47), b* 22.6; the point defense corvette's is b* 22.7.
- **Classes.** Texels are sorted into six classes, with re-measured thresholds (armor L > 48), then given one paint per face (`scripts/classify_faces.py`). A flat plate is unified to one paint only when that paint covers at least 75% of it. The flank lobes are coplanar with the dark machinery band, and an unconditional plate vote had painted whole armor lobes gunmetal.
- **Wear.** The cleanup is detail-preserving, as on the point defense corvette, but keeps more of the source's wear: lighter denoising, mid-scale blotches kept in full, fine scuffs boosted 1.7x, and grime only 55% lifted. The armor's fine-grain and blotch variation (std 1.12 and 4.98 L) sits inside the fleet's range (1.06-1.35 and 4.4-5.6).
- **Lights.** The source's pale blue lamps are kept per texel; it has no amber. The engines are dark in the source but glow blue in the reference. They are placed from the baked position and normal maps: the upper hull's octagonal engine recess and the lower hull's two nozzle rings.
- **Seats.** The boolean faces carry no source UVs, so they are painted by position. Each seat has a brick-red outer ring like the reference's socket rings, a graphite groove, and a gunmetal plate with a bolt circle and a dark hub. Their fine grain is copied from a nearby patch of the hull's own armor texels.

The source normal and ORM maps are not used, because they amplify reconstruction noise.

## The flak turret

The turret points along **-Z** with **+Y up** (out of the hull). Its origin is the centre of the base bottom, on the yaw axis. It is built at the corvette seat's size: the base is **3.0 m** across, so it mounts at scale 1. The 4 m mounted turrets collection mounts at 0.75.

| | |
| --- | --- |
| Triangles | 17,436, one material |
| Height at rest / at 90 degrees | 1.9 m / 3.8 m |
| Barrels | Twin, 0.42 m apart, muzzles 2.35 m ahead of the trunnion |
| Elevation set | -10 to +90 degrees; clear from -15 to +95 with the barrels in full recoil (`reports/turret_clearance.json`) |
| Traverse | 360 degrees |
| GLB | 3.2 MB |

**Design.** The turret shares the mounted turrets family's base and bearing ring: the quad cannon's, appended and scaled 0.75. The gun is an open-cheek mount, as on a real anti-aircraft gun:

- two armoured cheeks carry the trunnion, and the slot between them is open above, so nothing overhangs the barrels;
- the trunnion lies on the yaw axis, so at 90 degrees the bore runs straight out of the seat;
- the breech is short enough to clear the deck at 90 degrees, and the low rear bustle stays behind it at -10 degrees;
- each barrel has a heavy jacket, a recoil collar, a slotted muzzle brake and a recuperator cylinder above it;
- there are ammunition magazines on the cheeks, trunnion caps and a fire-control rangefinder with a blue lens.

**Texture.** The new parts have no source texture. They are surfaced from the flak corvette's own cleaned paint, as the interiors were (`scripts/turret_paint.py`):

- armor, graphite and gunmetal swatches are cut from the corvette atlas where its face classes say a window is wholly one paint, picking the windows with the most panel and wear detail and keeping the seats out;
- each swatch is resampled to the same texels per metre as the hull and centred on its paint's palette colour;
- each UV island is mirror-tiled from a random offset.

The family base keeps its own cleaned paint and light strips, with its tan armor regained to the fleet tan the corvette wears. The barrels are dark steel with sooty brakes and machined lips. A brick-red band crosses the front of each cheek. Roughness and metalness follow the family per paint, in a 1K ORM map.

**Node layout** (the mounted turrets' layout, two barrels):

```
FlakTurret
├─ BaseMesh
└─ Yaw                         traverse (Y)
   ├─ YawMesh, YawRing         cheeks, magazines, rangefinder + bearing ring
   └─ Pitch                    elevation (X) on the trunnion, 1.42 m above the base bottom
      ├─ PitchMesh             mantlet drum, breech, cradle, recuperators
      └─ Barrel1, Barrel2 > Barrel#Mesh, Muzzle#     recoil along the bore
```

| Clip | Length | What happens |
| --- | --- | --- |
| `scan` | 8 s loop | Idle sweep, yaw ±35 degrees with a nod up to 30 degrees; stops as soon as the turret aims |
| `fire` | 0.8 s loop | Barrel 1 then barrel 2 recoil 0.22 m, 0.4 s apart; `shot_fired` at each kick |

## Integration

Copy `godot/assets/flak_*.glb`, `godot/scenes/flak_corvette.tscn`, `flak_turret.tscn` and `godot/scripts/flak_corvette.gd`, `flak_turret.gd` into the matching `res://` folders. Then instance `flak_corvette.tscn`. The root has no movement or AI; attach your logic there.

```gdscript
var turret_scene := preload("res://scenes/flak_turret.tscn")
for socket in FlakCorvette.SOCKETS:
    corvette.mount_turret(turret_scene.instantiate(), socket)   # flak turret at scale 1
corvette.aim_turrets_at(world_point)        # each frame; returns the sockets engaging
corvette.clear_turret_targets()
corvette.has_line_of_fire(socket, world_point)
corvette.remove_turret(socket); corvette.get_turret(socket); corvette.is_port(socket); corvette.is_upper(socket)
signal turret_mounted(turret, socket) / turret_removed(turret, socket)

turret.aim_at(world_point); turret.clear_target(); turret.can_reach(world_point); turret.is_on_target()
turret.start_firing(); turret.stop_firing(); turret.fire()      # barrels alternate while held
turret.set_angles(yaw_deg, elevation_deg); turret.get_angles(); turret.get_muzzles(); turret.get_aim_direction()
signal shot_fired(muzzle)      # spawn your flak shell here; turret.fuse_range is exported for it
```

`FlakTurret` has the mounted turrets' API, so `aim_turrets_at()` drives either kind. The exports are `traverse_speed_deg` (60), `elevation_speed_deg` (45), `min_elevation_deg` / `max_elevation_deg` (-10 / 90), `traverse_limit_deg`, `aim_tolerance_deg`, `auto_scan`, `fuse_range`, `effects` and `hitbox_layer`. The turret adds a base cylinder hitbox and a house box that turns with `Yaw`.

**Sockets.** `FlakCorvette.SOCKETS` lists the eight Marker3D names:

| Socket | Godot position (port; starboard mirrors x) | Seat |
| --- | --- | --- |
| `TurretUpperForePort` / `...Starboard` | (∓2.41, 0.71, -3.99) | 3.0 m |
| `TurretUpperAftPort` / `...Starboard` | (∓2.42, 0.71, 4.88) | 3.0 m |
| `TurretLowerForePort` / `...Starboard` | (∓2.41, -3.87, -3.99) | 3.0 m |
| `TurretLowerAftPort` / `...Starboard` | (∓2.41, -3.87, 4.88) | 3.0 m |

- Each marker sits on the centre of its seat, with +Y pointing straight out of the flank (port -X, starboard +X) and -Z towards the prow.
- A seated turret therefore stands sideways, with its gun at rest along the hull. From there it covers the whole outward hemisphere: 360 degrees of traverse, and elevation from 10 degrees into the flank up to straight out.
- Rays from 1.2 m out of each seat are clear in every direction of that hemisphere sampled (`reports/hardpoints.json`). The far beam is screened by the hull, which `has_line_of_fire()` reports.

Other markers:

- `Nose`: the tip of the upper prow.
- `EngineMain`: the upper hull's engine recess, facing aft.
- `EngineLowerPort`, `EngineLowerStarboard`: the lower hull's two nozzle rings, facing aft.

The seven collision hulls are the upper and lower hulls (each split fore, mid and stern) and the bridge with its mast. They are coarse gameplay proxies. The mid sections stop short of the wider stern modules, so every seat lies within 4 cm of the collision surface.

## Validation

- **Blender:**
  - the hull half, the mirrored hull and both LODs are closed, and the mirror error is zero;
  - every turret part is closed;
  - the turret's gun was swept from -15 to 95 degrees in 1 degree steps, barrels in full recoil, against the house, ring and base, with no contact. At -25 and -40 degrees the same test does hit, so the check is live.
- **GLB buffers:** `scripts/check_glb.py` confirms finite data, valid indices, exact mirror symmetry including UVs, and the embedded textures for the corvette GLBs (`reports/glb_validation.json`).
- **Godot 4.7.2 Compatibility:** `godot/scripts/validate.gd` runs 51 checks with 0 failures (`reports/godot_validation.json`). It covers:
  - the corvette's LODs, material, size, symmetry and markers;
  - the eight sockets: mirrored, pointing out of their flanks, each seat on the collision surface;
  - the seven hulls;
  - the turret's nodes, clips, 3.0 m base and material;
  - the turret pointing straight out at 90 degrees and clamping beyond it;
  - aiming at a far point;
  - a real firing run: the barrels alternate over two loops, recoil 0.2 m and stop with the trigger;
  - mounting eight turrets, refusing a ninth, removal and remounting;
  - a target off each beam engaged by that side's four turrets only, and the hull blocking fire to the far beam;
  - a flank turret slewing straight out of the hull with its bore on target;
  - a lower turret aiming forward and below.
- **Captures:** close, bare, front, side, rear, top, underside, sockets, broadside (port guns at 90 degrees), tracking off the port beam and overhead, and the turret alone at rest and at 90 degrees are in `renders/`.

## Rebuilding

Blender scripts declare the workspace path at their start. Run them with the stated file open (`exec(open(path).read())`). Python-side scripts need numpy, opencv-python and scipy.

1. `flak_corvette_original.blend` → `scripts/align_source.py`; reopen → `scripts/prepare_asset.py` → `scripts/seat_sockets.py` → `scripts/reduce_meshes.py` → `scripts/bake_source.py`.
2. `python scripts/clean_texture.py labels`, then `scripts/classify_faces.py` in Blender, then `python scripts/clean_texture.py paint`.
3. Reopen `flak_corvette_uv_baked.blend` → `scripts/finalize_asset.py` → `scripts/export_asset.py`. Then `python scripts/package_asset.py` → `python scripts/check_glb.py`.
4. Turret, in an empty scene: `scripts/turret_build.py` → `scripts/turret_bake.py`. Then `python scripts/turret_paint.py` (it needs the corvette paint from step 2). Then reopen `flak_turret_uv_baked.blend` → `scripts/turret_finalize.py`.
5. `godot --headless --path godot --editor --import --quit`, then `godot --headless --path godot --script res://scripts/validate.gd`.
   - Captures: `godot --path godot -- --capture=close`, or `bare`, `front`, `side`, `rear`, `top`, `underside`, `sockets`, `broadside`, `track_port`, `track_above`, `turret` or `turret_90`.

`classify_faces.py` and the bakes switch Blender to Cycles. When running Godot under a restricted account, set `APPDATA` to `godot/.local_appdata/`.
