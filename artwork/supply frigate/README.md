# Supply frigate

The supplied supply frigate has been aligned, welded, reduced, flattened, mirrored and given a cleaned paint finish for Godot. It resupplies and reloads fighters and corvettes that land on its pads.

- **Landing pads.** All six share one look: a flat deck with nothing rising out of it, a lamp-lit mustard lip, a dashed white border, amber rings and a centreline.
  - **Dorsal.** Four pads in the source's positions and at the source's size, for fighters and bombers.
  - **Ventral.** One large 29 m x 43 m deck on each side, where a corvette docks upside down without touching the hull.
- **Engines.** The stern carries three engine banks copied from the beam frigate, the fleet's other frigate.

The bow pods, the spine with its bridge tower and mast, the pad blocks, the stern blocks and the ventral aerials are all preserved. The hull has no moving parts or animation.

Open `godot/project.godot` in Godot 4 and run the preview. Drag to orbit and scroll to zoom. Press D to launch every docked ship or fly them back in. Press 1/2/3 to inspect a mesh level and 0 for automatic switching. The label shows each pad's resupply progress.

![Godot capture](renders/godot_close.png)

| Underside, corvettes docked inverted | Engines |
| --- | --- |
| ![underside](renders/godot_underside.png) | ![engines](renders/godot_engines.png) |

| Dorsal pads | Ventral decks |
| --- | --- |
| ![dorsal pads](renders/godot_pads_top.png) | ![ventral decks](renders/godot_pads_bottom.png) |

The docked ships in the preview are copies of the torpedo bomber (on the dorsal pads) and the point defense corvette (on the ventral decks), in `godot/preview_only/`. They are not part of the frigate asset.

| File | Purpose |
| --- | --- |
| `godot/assets/supply_frigate.glb` | Frigate with embedded paint and emission textures |
| `godot/assets/supply_frigate_lod1.glb`, `supply_frigate_lod2.glb` | Distance meshes (geometry and material slot only) |
| `godot/scenes/supply_frigate.tscn` | CharacterBody3D with LODs, ten convex collision hulls, six landing pads and markers |
| `godot/scripts/supply_frigate.gd` | `SupplyFrigate` API: pick, dock, resupply and undock on the pads, with signals |
| `godot/preview_only/` | Torpedo bomber and corvette GLBs, used only by the preview and validation |
| `blender/supply_frigate_game_ready.blend` | Current editable game mesh with packed textures |
| `blender/supply_frigate_original.blend` | Untouched supplied scene |
| `blender/supply_frigate_clean_high.blend` | Aligned, welded, scaled full-resolution frigate |
| `blender/supply_frigate_high_pads.blend`, `_high_engines.blend` | The same with the six pad decks, then the engines added |
| `blender/supply_frigate_prepared.blend`, `_uv_baked.blend` | Reduced and flattened port half; then unwrapped and baked |
| `textures/supply_frigate_basecolor_4k.png`, `_emission_2k.png` | Current albedo and emission atlases |
| `textures/source/` | The three original reconstruction maps (albedo, ORM, normal) |
| `textures/work/` | Baked source albedo, island and hit masks, position and normal maps, texel and face class maps, deck and stern depth maps |
| `renders/godot_*.png` | Captures from the actual Godot renderer, with ships docked and bare |
| `reports/` | Alignment, pads, engines, geometry, texture, hardpoint, GLB and Godot validation |

The frigate points along **-Z** (the bow pods), with **+Y up** in Godot. Its origin is on the symmetry plane at the hull's bounding-box centre (before the engines were added). Port is -X.

The hull was scaled to a nominal **80 m** because the source has no physical dimensions. At that size each dorsal pad is 20-22 m across, which takes the 16-18 m fighters and the 18 m torpedo bomber. The engines add 5 m at the stern. The finished frigate measures **85.1 m long x 66.2 m wide x 48.4 m tall**, including the 6 m bridge mast and the ventral aerials. Scale the scene root to suit your game; the pads scale with it.

| Detail level | Triangles | Default distance |
| --- | ---: | --- |
| LOD0 | 152,858 | Under 160 m |
| LOD1 | 61,128 | 160-420 m |
| LOD2 | 22,924 | Over 420 m |

The source was a single 699,894-triangle mesh. The three engine sections added 440,000 more source triangles. The game mesh uses one PBR material. Roughness is 0.62, metallic 0.15 and emission strength 2, as on the other ships. The main GLB is about 26 MB, mostly the embedded 4K albedo.

Godot's automatic mesh LOD generation is disabled in the saved import settings because explicit distance meshes are included. The textures use VRAM compression. The LOD switch distances have no hysteresis margin. With fading off, a margin left a camera that started within it of a switch distance seeing neither level.

## Integration

Copy `godot/assets/supply_frigate*.glb`, `godot/scenes/supply_frigate.tscn` and `godot/scripts/supply_frigate.gd` into the matching `res://` folders and instance `supply_frigate.tscn`. The root has no movement or AI; attach your logic there.

```gdscript
var pad := frigate.find_free_pad(ship.global_position, not frigate.fits_dorsal_pad(ship))
ship.fly_to(frigate.get_approach_point(pad))             # your approach AI; 25 m out of the deck by default
frigate.dock_ship(ship, pad)                             # seats it on the deck and starts resupply
await frigate.ship_resupplied                            # after resupply_time (6 s by default)
frigate.undock_ship(pad)                                 # back to its old parent, world transform kept

frigate.dock_ship(corvette)                              # no pad: a ship too big for a dorsal deck gets a ventral deck
frigate.get_pad(pad); frigate.is_ventral(pad); frigate.is_pad_free(pad)
frigate.get_docked_ship(pad); frigate.get_occupied_pads(); frigate.fits_dorsal_pad(ship)
frigate.get_resupply_progress(pad); frigate.is_resupplied(pad)
signal ship_docked(ship, pad)       # the ship is a child of the pad marker
signal ship_undocked(ship, pad)
signal ship_resupplied(ship, pad)   # a ship with a resupply() method has it called first
```

**Pads.** `SupplyFrigate.PADS` lists the six Marker3D names, dorsal first:

| Pad | Godot position (port; starboard mirrors x) | Flat deck |
| --- | --- | --- |
| `PadTopForePort` / `...Starboard` | (∓16.30, 10.55, -8.70) | 22.6 m x 21.2 m |
| `PadTopAftPort` / `...Starboard` | (∓16.95, 10.55, 13.50) | 21.9 m x 20.0 m |
| `PadBottomPort` / `...Starboard` | (∓17.00, -13.45, 2.00) | 29 m x 43 m |

- Each marker sits on the deck at the centre of its octagon, where the markings are centred. It has +Y pointing out of the deck and -Z forward. The ventral markers are rolled 180 degrees about the forward axis, so a ship docked on them hangs upside down and still faces the bow.
- Every deck is a flat chamfered octagon with nothing rising out of it: the relief measured over each whole octagon is 0.0 m, and nothing of the hull lies straight out from any deck.
- **Dorsal pads** sit in the source's positions and at its size (`DORSAL_DECK_SIZE`, the smaller aft pair). A ship fits if its footprint is within `PAD_FRAME_SIZE = 20` m, as the fighters and the bomber are.
- **Ventral decks** (`VENTRAL_DECK_SIZE = (29, 43)`) take the 28 m x 32 m corvette with 0.5 m to spare on each side and 5.5 m fore and aft. Checked against the actual corvette mesh, docked inverted it touches only the deck (zero intersections with a 2 cm gap). In Godot its bounding box clears all ten collision hulls.
- `dock_ship()` makes the ship a child of the pad marker, so it moves with the frigate. The ship keeps its own forward along the bow, and its lowest visible point rests on the deck (`get_seat_height()`).
  - A physics body stops colliding with the frigate while docked. A RigidBody3D is also frozen, then restored on undock.
  - Without a pad, a ship that doesn't fit a dorsal deck (`fits_dorsal_pad()`) is offered only the ventral decks.
  - Otherwise, a ship above the frigate gets the nearest free dorsal pad and one below gets a ventral deck.
- Resupply runs per pad over `resupply_time` seconds. When it completes, a docked ship's own `resupply()` method is called if it has one, then `ship_resupplied` is emitted. The ship stays docked until you call `undock_ship()`.

Other markers, all facing aft except the first two:

- `Nose`: the bow tip on the centreline.
- `MastTop`: the top of the bridge mast.
- `EngineCentre`, `EnginePort`, `EngineStarboard`: the aft faces of the three engine banks.
- `NozzleCentrePort` / `...Starboard`, `NozzlePortUpper` / `Lower`, `NozzleStarboardUpper` / `Lower`: the six main nozzles' aft faces, for exhaust effects.

The ten collision hulls are coarse gameplay proxies, not exact projectile meshes:

- **Centreline:** the spine and the stern keel. The keel covers the centre block and centre engine; the mast and aerials are left out.
- **Each side:** a bow pod, the fore pad block, the aft pad block and a stern block with its engine.

The pad blocks and spine are clipped at the dorsal and ventral deck planes, and the pad blocks carry the decks' own outlines, so a landing ship meets each deck. Every pad marker lies within 2 cm of the collision surface.

## Landing pads

`scripts/add_pads.py` builds all six on the full-resolution mesh, before reduction, so they go through the same reduction, bake and paint as the rest of the hull. The source's dorsal pads had raised frames with yellow corner clamps. They are rebuilt on the same frame octagons (`mesh_tools.PAD_OCTAGONS`), so they look like the ventral decks without growing.

1. Before anything changes, the source's dorsal fore deck is sampled top-down on a 5 cm grid and saved as `textures/work/deck_grime.npz`. Every deck is later painted with this grime.
2. The hull is not cut. Inside each octagon its vertices on the deck side of the lip are pressed back to 0.8 m inside the deck, into the plinth. On top, these are the old deck, rails and clamps, and the press reaches 0.6 m past the edge, where the clamps stood. Underneath, they are the bay plates and rims.
3. Each deck is modelled flat, its outline sampled every 0.5 m:
   - **Dorsal:** at the source deck's 10.55 m.
   - **Ventral:** at -13.45 m, spanning the source's two machinery bays on each side, |x| 2.5-31.5 m and y -23.5 to 19.5 m (`mesh_tools.VENTRAL_OCTAGON`).
4. A 0.5 m lip runs from each deck edge, then the plinth tapers 2 m inwards to 0.4 m inside the hull beyond each point. A cap closes it inside the hull, so the hull and all six pads stay closed shells.
5. The caps and the pressed hull under the decks can never be seen. Their UV islands are shrunk to 3% before the atlas is packed, which leaves the space for visible surfaces.

`scripts/clean_texture.py` paints all six decks alike, by position:

- **Plate.** The dark deck plate carries the sampled grime (old markings filled in), mirror-tiled metre for metre at 70% contrast.
- **Markings.** A dashed white border 1.2 m in, a double amber ring, a white centre cross, amber ticks and a dashed white centreline. The rings are 4.45 m on the dorsal decks and 7 m on the ventral ones.
- **Lip.** Each lip is the mustard frame, with an amber lamp every 2.5 m.

## Engines

The source had no engines. Its stern ends in three flat block faces. `scripts/add_engines.py` gives each a copy of the beam frigate's stern engine section, so the two frigates share one engine design. The section is two round main nozzles between four square blue vents, ringed by pipe greebles.

- The section is everything aft of y = -18 m on the beam frigate's full-resolution reconstruction: 19 m x 12 m and 6 m deep, with its cut face capped.
- **Centre block:** the section as on the beam frigate, at 0.9 scale.
- **Outboard stern blocks:** turned 90 degrees, so the two main nozzles stack vertically on the tall blocks, at 0.8 scale.
- **Backing sleeves.** On the beam frigate the engine block continues forward, so the section on its own is an open frame. Each copy is therefore seated just aft of its stern face and backed by a dark sleeve that runs 8 m into the hull. The centre block's stepped face sits up to 5 m forward of the engine at its edges. The frame openings show dark machinery rather than the frigate's tan stern, and no gap opens behind the engine.
- **Paint.** The section keeps its source UVs and albedo as a second material on the high mesh, so the bake carries its paint into the frigate's single atlas. `clean_texture.py` repaints it in the frigate's palette and keeps its small yellow handles. The blue vents stay lit per texel (as on the beam frigate), and the six main nozzles glow blue from the throat out, placed by position.

## Mesh cleanup

- **Alignment.** The source was pitched 27.4 degrees nose-down. Up was taken from the dominant dorsal and ventral plates (the pad decks and the keel), and forward from the longest principal axis, towards the bow pods. Yaw (2.0 degrees), roll and the centreline offset were then refined by minimising mirrored surface distance. See `reports/source_alignment.json`.
- **Weld.** The source's split UV-seam vertices were welded and its custom normals cleared. Seven edges shared by more than two faces were split.
- **Reduction, smoothing and panel flattening.** These are the corvette methods, applied to the port half at a 0.13 ratio. The plate thresholds and the 20 cm movement cap are scaled up from the 48 m beam frigate's for this hull. 328 plates are flattened (`reports/mesh_reduction.json`). The median game vertex lies 1.3 cm from the source surface; 99% lie within 10 cm and the worst within 34 cm.
- **Symmetry.** Mirrored across X=0, with zero reflected position and UV error in every GLB.
- **Stranded triangles.** The reduction left three detached pairs of back-to-back triangles on each side. The glTF exporter validates meshes in place and deletes one of each pair, which strands its twin. `finalize_asset.py` therefore validates first and removes the stranded triangles.
- **Shading.** Edges sharper than 40 degrees are marked sharp.

The mesh and both LODs have zero boundary edges and zero edges shared by more than two faces. Some soft reconstruction forms remain, mostly in the machinery between the pad blocks and along the stern. They were kept as part of the supplied silhouette.

## Texture cleanup

The port half has a new 4096 `GameUV` atlas, using 39% of the sheet. The source albedo (and the engines' beam frigate albedo) was baked onto it selected-to-active, and both halves share the atlas.

`scripts/clean_texture.py` follows the corvette method:

1. **Classification.** Seven classes: graphite, gunmetal, tan armor, mustard yellow, amber light, white marking and blue light. The thresholds were measured on this bake, which is lighter than the corvette's and has mustard instead of a red stripe.
2. **Plate majority.** `scripts/classify_faces.py` gives every face and every flat plate one base paint: graphite, gunmetal or armor. It then repaints armor over 281 small dark grime blotches on curved tan panels.
3. **Yellow paint.** Yellow is kept, texel-accurate, only on the engines. Everywhere else the source's yellow is smeared splashes, which are repainted armor. Each bow pod instead gets one clean mustard band by position, wrapping the pod about mid-length as in the reference.
4. **Detail-preserving cleanup.** Blotches (2.5-24 texels) are damped and grime on armor is lifted 75%, while fine detail is kept. Each paint is pulled towards its palette colour. The armor tan is the corvette's and the mounted turrets', (0.72, 0.61, 0.47), so the fleet shares one paint scheme.
5. **Pad decks and lips.** Painted by position, as described under Landing pads.
6. **Lights.** About 820 small, bright saturated blobs survive as amber lamps along the hull. Any blob over 0.2 m² is a sunlit stretch of mustard paint rather than a lamp, and is not lit. The pad lip lamps, engine vents and nozzle glow are described above.

See `reports/texture_cleanup.json` for the class coverage and every marking dimension. The old normal and ORM maps are archived in `textures/source/` and are not used, because they amplify reconstruction noise.

## Validation

- **Blender:**
  - The half and the mirrored mesh are closed, and mirror error is zero (`reports/mesh_reduction.json`, `symmetry.json`).
  - The six pads and the engine sections are closed shells (`reports/pads.json`, `engines.json`).
  - Each deck's relief and open sky were ray-tested over its whole octagon on the game mesh (`reports/hardpoints.json`).
  - The corvette GLB, docked inverted on a ventral deck, intersects the frigate's game mesh nowhere.
- **GLB buffers:** `scripts/check_glb.py` confirms the following for all three GLBs (`reports/glb_validation.json`):
  - finite positions, normals and UVs, and valid indices;
  - exact mirror symmetry including UVs;
  - embedded 4K/2K textures.
- **Godot 4.7.2 Compatibility:** `godot/scripts/validate.gd` runs 44 checks with 0 failures (`reports/godot_validation.json`). It covers:
  - the LODs and the shared material;
  - size and orientation, and all markers, including mirrored, aft-facing engine and nozzle markers;
  - the six pads: mirrored pairs, each ventral deck under its side's dorsal pads, dorsal up, ventral down, all facing forward, every deck on the collision surface with open space out of it;
  - ten convex hulls, with ray hits across the frigate;
  - docking six ships in order and refusing a seventh;
  - every ship resting on its deck, the ventral ones inverted, all facing the bow, and carried when the frigate moves;
  - resupply completing on all six pads;
  - undocking back to the old parent, and dorsal/ventral pad choice by approach side;
  - the torpedo bomber fitting a dorsal deck;
  - the corvette being given a ventral deck from above, lying within the deck and clearing every collision hull.
- **Captures:** close, bare, front, side, rear, top, underside, engines, and dorsal pad and ventral deck close-ups are in `renders/`.

## Rebuilding

Blender scripts declare the workspace path at their start. Run them with the stated file open; Python-side scripts need numpy, opencv-python, scipy and Pillow.

1. `supply_frigate_original.blend` → `scripts/align_source.py` → `scripts/prepare_asset.py`.
2. `scripts/add_pads.py` (on `supply_frigate_clean_high.blend`) → `scripts/add_engines.py`. This step reads `artwork/beam frigate/blender/beam_frigate_clean_high.blend`.
3. `scripts/reduce_meshes.py` → `scripts/bake_source.py`.
4. `python scripts/clean_texture.py labels`, then `scripts/classify_faces.py` in Blender, then `python scripts/clean_texture.py paint`.
5. Reopen `supply_frigate_uv_baked.blend` → `scripts/finalize_asset.py` → `scripts/export_asset.py`.
6. `python scripts/package_asset.py` → `python scripts/check_glb.py`.
7. `godot --headless --path godot --editor --import --quit`, then `godot --headless --path godot --script res://scripts/validate.gd`. Captures: `godot --path godot -- --capture=close` (or `bare`, `front`, `side`, `rear`, `top`, `underside`, `engines`, `pads_top`, `pads_bottom`, `lod1`, `lod2`).

For texture-only changes, repeat steps 4-7. `classify_faces.py` switches Blender to Cycles for its bake. When running Godot under a restricted account, set `APPDATA` to `godot/.local_appdata/`.
