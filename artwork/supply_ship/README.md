# Supply ship

The supplied supply ship and cargo pod have been separated, aligned, welded, reduced, flattened, mirrored and given a cleaned paint finish for Godot. The two deck cranes were cut free, rigged and animated: each crane can unload its cargo pod into space beside the ship and load a floating pod back into the bay. Two pods, one per side, fill the central cargo bay.

Open `godot/project.godot` in Godot 4 and run the preview. Drag to orbit and scroll to zoom. Press 1 or 2 to unload the port or starboard pod, 3 or 4 to load it back, and D for a demo in which a stand-in drone collects the released pod and returns it.

![Godot capture](renders/godot_close.png)

![Crane animation captures](renders/godot_animation_sheet.png)

| File | Purpose |
| --- | --- |
| `godot/assets/supply_ship.glb` | Hull, skinned cranes, `CraneRig` skeleton, `PodMount_L`/`_R` nodes, the four crane clips and embedded paint and emission textures |
| `godot/assets/supply_ship_lod1.glb`, `supply_ship_lod2.glb` | Distance hulls (geometry and material slot only) |
| `godot/assets/cargo_pod.glb`, `cargo_pod_lod1.glb` | Cargo pod with its own material, plus a distance mesh |
| `godot/scenes/supply_ship.tscn` | CharacterBody3D with LODs, four convex collision hulls that keep the bay open, and markers |
| `godot/scenes/cargo_pod.tscn` | CharacterBody3D with a LOD, one convex hull and the two latch markers |
| `godot/scripts/supply_ship.gd` | `SupplyShip` API: unload, load, signals, and one animation player per side |
| `blender/supply_ship_game_ready.blend` | Current editable game asset: rig, cranes, hull, pod, the clips as NLA tracks, and packed textures |
| `blender/supply_ship_original.blend` | Untouched supplied scene |
| `blender/supply_ship_clean_high.blend` | Aligned, welded, scaled full-resolution ship and pod |
| `blender/supply_ship_cranes_cut.blend`, `_cranes_split.blend` | Port crane cut from the high hull, then split into rigid parts |
| `blender/supply_ship_prepared.blend`, `_uv_baked.blend` | Reduced and flattened halves with the fitted pod; then unwrapped and baked |
| `textures/supply_ship_basecolor_4k.png`, `_emission_2k.png` | Ship atlas: hull and both cranes |
| `textures/cargo_pod_basecolor_2k.png`, `_emission_1k.png` | Pod atlas |
| `textures/source/` | The three original reconstruction maps (albedo, ORM, normal) |
| `textures/work/` | Baked source albedo, island, hit and procedural masks, texel and face class maps |
| `renders/godot_*.png` | Captures from the actual Godot renderer, including six animation stills |
| `reports/` | Alignment, crane cut and pivots, pod fit, geometry, texture, animation, GLB and Godot validation |

The ship points along **-Z**, with **+Y up** in Godot. Its origin is on the symmetry plane at the bounding-box centre. Port is -X and starboard is +X; the Blender port side uses the `.L` / `_L` suffix. A nominal **60 m length** was chosen because the source has no physical dimensions. This sits between the 48 m beam frigate and the ~100 m carrier. The mirrored hull measures **59.8 m long x 24.8 m wide x 21.1 m tall**. Each pod is **25.9 m long x 8.6 m wide x 5.8 m tall**. Scale the scene root to suit your game.

| Mesh | Triangles | Default distance |
| --- | ---: | --- |
| Hull LOD0 | 93,314 | Under 150 m |
| Hull LOD1 | 37,310 | 150-380 m |
| Hull LOD2 | 13,980 | Over 380 m |
| Both cranes (skinned) | 5,548 | Under 420 m |
| Cargo pod LOD0 / LOD1 | 22,632 / 7,914 | Under / over 90 m |

The source was a single 699,974-triangle mesh. The ship and both cranes share one PBR material, and the pod has its own. Roughness is 0.62, metallic 0.15 and emission strength 2, as on the beam frigate. The main GLB is about 24 MB, mostly the embedded 4K albedo. Godot's automatic mesh LOD generation is disabled in the saved import settings because explicit distance meshes are included.

## Integration

Copy `godot/assets/`, `godot/scenes/supply_ship.tscn`, `godot/scenes/cargo_pod.tscn`, `godot/scripts/supply_ship.gd` and `godot/scripts/cargo_pod.gd` into the matching `res://` folders and instance `supply_ship.tscn`. The root has no movement or AI; attach your logic there. The pods are spawned into their seats on ready (`start_loaded`).

```gdscript
ship.unload_pod(&"port")          # or &"starboard"; returns false if busy or empty
ship.load_pod(&"port", pod)       # pod = a free CargoPod, or null to spawn one
ship.is_busy(side); ship.has_pod(side); ship.get_pod(side)
ship.get_handoff_transform(side)  # where a drone should deliver a pod for load_pod()
ship.get_drop_transform(side)     # where an unloaded pod comes to rest
signal pod_released(side, pod)    # end of unload: pod re-parented to the ship's parent, at the drop point
signal pod_loaded(side, pod)      # end of load: pod seated and parented to its mount
signal crane_started(side, clip)
```

**Drone loop.** Collect the pod after `pod_released`; its `Latch` / `LatchMirrored` markers are good grab points. To return a pod, fly it near `get_handoff_transform(side)` and call `load_pod(side, pod)`. The ship eases the pod onto the exact hand-off point in 1.2 s before the crane hooks it, so the delivery can be approximate. Both sides can run at the same time. The glTF clips sample every bone, so on ready the script strips each clip down to its own crane and mount, and runs the starboard clips on a second `AnimationPlayer` that shares the same library.

Markers: `Bow`, `Bridge`, `EnginePort` and `EngineStarboard` (facing aft), and per side `PodSeat*`, `PodBayMouth*`, `PodHandoff*` and `PodDrop*`. Engine markers identify the aft engine block rather than individual nozzles.

The four collision hulls are the bow block, the stern block, and the slabs above and below the bay. The bay tunnel is deliberately left open, and a mounted pod has a collision exception with its ship. These are coarse gameplay proxies, not exact projectile meshes.

## Cranes and animation

The two cranes lie folded side by side on the centreline, aft of the bridge. They were reconstructed fused to the deck and to each other. The port crane was sliced off the full-resolution hull along clean planes: the deck plane under it, a box around it, and X=0. Every cut was capped so both the crane and the hull stay closed (`scripts/cut_cranes.py`). It was then split into rigid parts at its real joints (`scripts/split_crane.py`). The starboard crane is its mirror. Every vertex is weighted 100% to one bone, so the parts never bend.

```
root
└─ crane_base.L      yaw at the deck foot
   └─ crane_leg.L    pitch (foot to knuckle)
      └─ crane_boom.L      pitch at the knuckle (hydraulic rod + piston)
         └─ crane_slide.L  telescoping housing, up to 4.6 m along the rod
            └─ crane_wrist.L   counter-rotates so the hook hangs level
               ├─ crane_hook.L   cable payout (translation)
               └─ crane_cable.L  stretches with the payout
```

The reconstructed boom is only about 10 m long and could not reach a pod that has slid out of the bay. Two parts were added for that:

- **Telescope piston:** a piston inside the housing, hidden while stowed and revealed as the housing slides out. Its radius is the largest that stays inside the housing (point-in-mesh test).
- **Hoist cable:** lets the hook drop below the hull edge while the boom stays clear of it.

Both use procedural steel and graphite paint in the shared atlas.

| Clip | Length | What happens |
| --- | --- | --- |
| `unload_L` / `unload_R` | 13.5 s | The pod slides out of the bay. The crane swings out and pays out its cable, then latches the pod's aft frame bar. It hoists the pod 3 m clear of the hull, carries it outboard and releases it. The pod drifts, braking to rest at `PodDrop`, and the crane stows. |
| `load_L` / `load_R` | 10.0 s | The crane hooks a pod floating at `PodHandoff`, carries it down to the bay mouth and releases it. The pod slides into its seat and the crane reels in and stows. |

Key poses come from an analytic crane IK (`scripts/crane_kinematics.py`) corrected against the evaluated rig, with residuals under 0.04 mm. Every frame is baked as FK keys at 30 fps. While attached, the pod follows the rig's real hook point. Every third frame of every clip was tested for crane/hull, pod/hull and pod/crane intersection, with zero contacts (`reports/animation.json`).

## Mesh cleanup

- **Separation.** After welding the split UV seams the source fell into three closed shells: the ship and two near-identical pods. The second pod is a reconstruction duplicate hidden behind the ship, so only the pod visible in the reference was kept.
- **Alignment.** Principal axes set forward and up. Forward is the ring-aperture end, with the four engine nozzles aft; up is the bridge and cranes. Yaw, roll and the centreline offset were refined by minimising mirrored surface distance. Pitch was set by levelling the cargo bay floor (2.9 degrees). The pod's roll was chosen for its tightest axis-aligned section. See `reports/source_alignment.json`.
- **Reduction, smoothing and panel flattening.** These are the beam frigate methods, applied to the port half of the hull and the pod: half-only reduction, crease-locked non-shrinking smoothing, and plate regions pulled onto fitted planes. Movement is capped at 14 cm on the hull and 8 cm on the pod (`reports/mesh_reduction.json`). Every final hull vertex lies within 0.19 m of the source surface (median 1 cm).
- **Pod fit.** The pod is extended to fill the open bay. Its middle tank section is stretched 6.5 m while the octagonal end caps keep their proportions, and it is widened 27.5%. The fit is the largest that keeps a 0.12 m gap to the hull in the seat and all along the sideways slide out of the bay (0.03 m vertically, where the bay is barely taller than the pod). See `reports/pod_fit.json`.
- **Bay sill.** A beam along the bottom edge of each bay mouth stood about 1 m above the floor. A full-height pod could not be lifted over it under the low inner ceiling, so it was lowered to a step 8% of its former height. This is the only change to the design.
- **Symmetry.** Hull, pod and cranes are mirrored across X=0, with zero reflected position and UV error in every GLB.
- **Shading.** Edges sharper than 40 degrees are marked sharp.

The hull, pod, every crane part and every LOD have zero boundary edges and zero edges shared by more than two faces. Soft reconstruction forms remain in places, especially around the bow ring and the greebles; they were kept as part of the supplied silhouette. The crane parts keep the reconstruction's rounded shapes. The cut faces are flat graphite caps that read as internal structure.

## Texture cleanup

The hull half and the port crane parts share one `GameUV` 4096 atlas, so the whole ship renders with a single material. The pod has its own 2048 atlas. The source albedo was baked selected-to-active. The cut crane pieces had lost their source UVs, so they were baked from the untouched high hull, where the crane still sits in its stowed place.

`scripts/clean_texture.py` uses the beam frigate method with a supply-ship palette:

1. **Classification.** Six paints: graphite, gunmetal, ivory armor, red stripe, orange trim and amber light. Most of the orange on this ship is painted trim and piping, so only bright amber texels become full-strength lights; trim glows at 12%.
2. **Plate majority.** `scripts/classify_faces.py` gives every face and every flat plate one majority base paint, across all objects in an atlas.
3. **Rails and piping.** The reconstruction smeared the orange trim into the dark machinery as a marbled speckle. On machinery, trim is decided geometrically instead of per texel:
   - A face that is at least 40% orange becomes a trim face, with neighbour voting.
   - Each connected machinery strip (normals within 25 degrees, at least 0.3 m²) then becomes all trim if at least 35% of it is orange, otherwise all dark.
   - Texel-level trim is kept only on armor, for painted bands.
4. **Detail-preserving cleanup.**
   - Armor: blotches (2.5-24 texels) are damped to 45%, grime is lifted 40% and stripe hue is evened 40%. Fine detail is kept at 100%.
   - Machinery: blotches are damped to 25% and fine detail kept at 60%.
   - Trim is pulled 85% to an even painted orange; graphite and gunmetal lose the orange smear and are evened 70%.
5. **Special texels.** Texels the bake could not reach (0.7% of the ship atlas, the new cut caps) are painted graphite. The piston is brushed steel and the cable graphite.

The old normal and ORM maps are archived in `textures/source/` and are not used, because they amplify reconstruction noise.

## Validation

- **Blender:** every cut part and mesh is closed, crane weights are rigid, and all four clips have zero intersections (`reports/crane_cut.json`, `crane_pivots.json`, `symmetry_and_rig.json`, `animation.json`).
- **GLB buffers:** `scripts/check_glb.py` confirms the following for all five GLBs (`reports/glb_validation.json`):
  - finite positions, normals and UVs, and valid indices;
  - exact mirror symmetry including UVs;
  - rigid single-bone skin weights;
  - 15 joints and the four clips.
- **Godot 4.7.2 Compatibility:** `godot/scripts/validate.gd` runs 33 checks with 0 failures (`reports/godot_validation.json`). It covers:
  - LODs, shared materials, the skinned cranes and per-side clip isolation;
  - collision along the hull, and an open bay tunnel;
  - pod seating to 0.0 mm;
  - a real unload of both pods at the same time, which come to rest within 2 mm of their drop markers;
  - a real load back into the seat to 0.0 mm, and a spawned-pod load;
  - the standalone pod scene.
- **Captures:** beauty, close, side, front, rear, top and underside views, plus six animation stills, are in `renders/`.

## Rebuilding

Blender scripts declare the workspace path at their start. Run them with the stated file open; Python-side scripts need numpy, opencv-python, scipy and Pillow.

1. `supply_ship_original.blend` → `scripts/align_source.py` → `scripts/prepare_asset.py`.
2. `scripts/cut_cranes.py` → `scripts/split_crane.py` → `scripts/reduce_meshes.py` → `scripts/fit_pod.py` → `scripts/bake_source.py`.
3. `python scripts/clean_texture.py labels ship` and `... labels pod`, then `scripts/classify_faces.py` in Blender with `ATLAS = 'ship'` and `'pod'`, then `python scripts/clean_texture.py paint ship` and `... paint pod`.
4. Reopen `supply_ship_uv_baked.blend` → `scripts/finalize_asset.py` → `scripts/crane_anim.py` → `scripts/export_asset.py`.
5. `python scripts/package_asset.py` → `python scripts/check_glb.py`.
6. `godot --headless --path godot --editor --import --quit`, then `godot --headless --path godot --script res://scripts/validate.gd`. Captures: `godot --path godot -- --capture=close`, or `-- --capture=hoist --clip=unload_L --time=8.6` for an animation frame.

For animation-only changes, open `supply_ship_game_ready.blend` and repeat steps 4 (from `crane_anim.py`) to 6. When running Godot under a restricted account, set `APPDATA` to `godot/.local_appdata/`.
