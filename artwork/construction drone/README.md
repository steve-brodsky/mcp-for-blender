# Construction drone

The supplied construction drone has been aligned, welded, reduced, flattened, mirrored and given a cleaned paint finish for Godot. It builds shipyards and frigate and capital ship hulls. Its two arms were cut free and rigged: a gripper claw on port and a welding torch on starboard. They have six clips: three looping construction tasks, a stowed idle, and deploy and stow transitions.

Open `godot/project.godot` in Godot 4 and run the preview. The drone hovers over a stand-in hull plate. Drag to orbit and scroll to zoom. Press 1, 2 or 3 to weld a seam, grab and place a beam section, or stitch-weld; the arms deploy first. Press R to finish the cycle and hold, or S to finish and stow.

![Godot capture](renders/godot_close.png)

![Welding a seam](renders/godot_weld.png)

| File | Purpose |
| --- | --- |
| `godot/assets/construction_drone.glb` | Hull, skinned arms, `ArmRig` skeleton, `TorchTip` / `ClawGrip` nodes, the six clips and embedded paint and emission textures |
| `godot/assets/construction_drone_lod1.glb`, `_lod2.glb` | Distance hulls (geometry and material slot only) |
| `godot/scenes/construction_drone.tscn` | CharacterBody3D with LODs, three convex collision hulls and markers |
| `godot/scripts/construction_drone.gd` | `ConstructionDrone` API: deploy, stow, task loops, torch effect, part handling, signals |
| `blender/construction_drone_game_ready.blend` | Current editable game asset: rig, arms, hull, the clips as NLA tracks, and packed textures |
| `blender/construction_drone_original.blend` | Untouched supplied scene |
| `blender/construction_drone_clean_high.blend` | Aligned, welded, scaled full-resolution drone |
| `blender/construction_drone_arms_split.blend` | Arms cut from the high mesh, split into rigid parts, with knuckle drums |
| `blender/construction_drone_prepared.blend`, `_uv_baked.blend` | Reduced and flattened hull half and arm parts; then unwrapped and baked |
| `textures/construction_drone_basecolor_4k.png`, `_emission_2k.png` | Albedo and emission atlas: hull, both arms and the drums |
| `textures/source/` | The three original reconstruction maps (albedo, ORM, normal) |
| `textures/work/` | Baked source albedo, island, hit and drum masks, position and normal maps, texel and face class maps |
| `renders/godot_*.png` | Captures from the actual Godot renderer, including weld, grab and stitch frames |
| `reports/` | Alignment, arm cut and pivots, geometry, rig, animation, texture, GLB and Godot validation |

The drone points along **-Z**, with **+Y up** in Godot. Its origin is on the symmetry plane at the bounding-box centre. Port is -X; the Blender port side uses the `.L` suffix.

A nominal **16 m length**, arms stowed, was chosen because the source has no physical dimensions. That puts it in the same small-craft class as the 12.5 m supply drone. The hull alone measures **14.5 m long x 11.6 m wide x 5.7 m tall**. Scale the scene root to suit your game.

| Mesh | Triangles | Default distance |
| --- | ---: | --- |
| Hull LOD0 | 93,914 | Under 45 m |
| Hull LOD1 | 37,558 | 45-110 m |
| Hull LOD2 | 14,084 | Over 110 m |
| Both arms (skinned) | 24,838 | Under 160 m |

The source was a single 699,909-triangle mesh. The hull, both arms and the drums share one PBR material. Roughness is 0.62, metallic 0.15 and emission strength 2, as on the other ships. The main GLB is about 23 MB, mostly the embedded 4K albedo. Godot's automatic mesh LOD generation is disabled in the saved import settings because explicit distance meshes are included. The textures use VRAM compression, as on the supply drone.

## Integration

Copy `godot/assets/construction_drone*.glb`, `godot/scenes/construction_drone.tscn` and `godot/scripts/construction_drone.gd` into the matching `res://` folders and instance `construction_drone.tscn`. The root has no movement or AI; attach your logic there.

```gdscript
drone.get_work_transform(target)     # drone pose that puts WorkPoint on target (target +Y = surface normal)
drone.start_work(&"weld_seam")       # or &"grab_place", &"stitch_weld"; deploys first if stowed
drone.stop_work()                    # finish the cycle, then stow; stop_work(false) holds READY
drone.deploy(); drone.stow()         # explicit transitions
drone.set_part(part)                 # the part grab_place lifts from PartPick and sets on PartPlace
drone.get_state(); drone.get_task(); drone.is_torch_lit(); drone.get_torch_tip(); drone.get_claw_grip()
signal deployed / stowed
signal work_started(task) / cycle_started(task) / work_stopped(task)
signal torch_ignited / torch_extinguished
signal part_gripped(part) / part_released(part)
```

**Working.** Fly the drone to `get_work_transform(target)`, where `target` is a point on the hull or girder being built, with +Y pointing back at the drone. The work surface is then 6 m below the drone's centre, under its nose. Each task loops until stopped, and a new `start_work()` switches task at the end of the current cycle. All three loops start and end on the same READY pose, so they chain without a pop.

**Torch.** While the torch is lit, the drone runs a blue-white OmniLight and a spark emitter at `TorchTip` (turn them off with `torch_effects = false`). The windows come from the Blender animation, and `torch_ignited` / `torch_extinguished` fire with them, so your own VFX or audio can hook in.

**Parts.** In `grab_place` the claw closes on `PartPick`; a part given with `set_part()` is seated there and rides in the claw. The claw lowers it onto `PartPlace` and releases it there, re-parented to the drone's parent. Supply the next part on `cycle_started`. Without a part, the claw works empty-handed.

| Clip | Length | What happens |
| --- | --- | --- |
| `idle` | 4.0 s loop | Arms stowed as supplied, breathing slightly |
| `deploy` / `stow` | 2.0 s | Stowed to READY (arms lowered under the nose) and back |
| `weld_seam` | 6.0 s loop | The claw clamps the work. The torch runs a weaving bead 0.8 m along a seam (lit 1.1-4.4 s), then both lift back to READY |
| `grab_place` | 7.0 s loop | The claw picks a part up beside the drone (grips at 1.85 s), carries it 1.8 m and sets it down (4.3 s); the torch then tack-welds it (4.6-5.4 s) |
| `stitch_weld` | 4.5 s loop | The claw braces the work while the torch makes three 0.37 s tack welds |

Markers:

- `WorkPoint`: the centre of the work surface the arms reach, facing up.
- `PartPick`, `PartPlace`: where grab_place lifts a part and sets it down, on the work surface.
- `NoseCamera`: the nose camera lens.
- `RodTipPort`, `RodTipStarboard`: the glowing tips of the two cutting rods under the nose.
- `ThrusterRearPort`, `ThrusterRearStarboard`: the rear ends of the tail pods, facing aft.
- `TorchTip`, `ClawGrip`: imported nodes under the wrist bones (`get_torch_tip()`, `get_claw_grip()`).

The thruster markers are approximate VFX points rather than modelled nozzles.

The three collision hulls are the hull body, the underside machinery and the tail pods. The arms move and have no collision; add per-bone shapes on `BoneAttachment3D` nodes if your game needs them. These are coarse gameplay proxies, not exact projectile meshes.

## Arms and animation

The arms were reconstructed fused to the underside machinery and to their shoulder housings. They are different tools, so each was cut from its own side of the full-resolution drone along clean planes: the housing front face and the hull floor plane ahead of it (`scripts/split_arms.py`). Every cut was capped, so the hull and every arm part stay closed.

Each arm was then split into rigid parts at its joints. At the shoulder, elbow and wrist a 0.24-0.28 m slab was removed and replaced by a **knuckle drum**: a new cylinder on the joint axis, sized to the arm tube there. A drum turning about its own axis never opens a gap, so the parts can pitch without exposing cut faces or swallowing each other. The drums are painted like the reference's joints: orange housings with graphite hubs. The claw head was split again into two jaw groups either side of its palm spine.

```
root
├─ arm_shoulder.L   yaw + pitch at the housing front (upper arm, shoulder drum)
│  └─ arm_elbow.L   pitch (forearm, elbow drum)
│     └─ arm_wrist.L      pitch + yaw (claw palm, wrist drum, ClawGrip)
│        ├─ claw_jaw_out.L   yaw (opens outboard)
│        └─ claw_jaw_in.L    yaw (opens inboard)
└─ arm_shoulder.R > arm_elbow.R > arm_wrist.R (torch, TorchTip)
```

Every vertex is weighted 100% to one bone, so the parts never bend.

The reconstructed starboard shoulder housing sat 0.29 m further outboard and 0.09 m higher than the port one. The mirrored hull uses the port housing on both sides, so the starboard arm was moved by the same offset to keep its knuckle on the housing face.

Key poses are set in task space: the torch tip or claw grip point plus a tool direction. They are solved by a damped least-squares IK (`scripts/arm_kinematics.py`), which matches Blender's evaluated rig exactly, with a coarse global grid search wherever it would stall on a joint limit. Shoulder pitch may only swing down from the stowed line, because the upper arm sits 0.3 m under the hull floor.

The arm has two sideways joints, shoulder yaw and wrist yaw. The IK holds the wrist yaw firmly near centre, so sideways reach always comes from the shoulder.

**How the motion is built**

- Each key pose is solved once, from the same seed, so READY is identical in every clip.
- Between keys the joints ease in joint space, so each joint moves steadily from one pose to the next. The first build re-solved IK every frame; the solver traded the two yaws back and forth, and the joints wobbled when the arms moved sideways.
- Straight drags along the work (the seam bead and the tack weld) are solved in 0.1 s sub-steps, at constant speed between short acceleration ramps.
- The weld weave is a ±3° wrist wiggle at 2 Hz.

The largest frame-to-frame change in joint velocity is now 0.8 degrees/frame² (`max_joint_accel_deg_per_frame2` in `reports/animation.json`), and that is the quick hops of the stitch weld. Before, the wrist flipped by up to 90 degrees/frame².

The work zone was chosen from a sweep of reachable tool poses. The work surface is 6 m below the drone's centre, under the nose, and the tools tilt naturally from straight down to forward.

Every frame is baked as FK keys at 30 fps. Every third frame of every clip was tested for arm/hull and arm/arm intersection, with zero contacts. The largest IK residual is 7 cm, on the READY transit pose. While the torch is lit it stays 0.15-0.16 m above the work surface (`reports/animation.json`, `godot_validation.json`).

## Mesh cleanup

- **Alignment.** Up was taken from the dominant top and bottom armor plates and side from the flank plates. Principal axes would have been skewed by the asymmetric arms. Forward is the end the arms reach towards. Yaw, roll and the centreline offset were refined by minimising the mirrored surface distance of the hull above the arms. See `reports/source_alignment.json`.
- **Weld.** The source's split UV seams were welded into one closed shell, and one loose flap triangle was removed. Its custom normals were cleared.
- **Reduction, smoothing and panel flattening.** These are the supply drone methods, applied to the port half of the hull: half-only reduction, crease-locked non-shrinking smoothing, and plate regions pulled onto fitted planes (5 cm movement cap). 253 plates cover 34% of the surface (`reports/mesh_reduction.json`). The arm parts were reduced to 42% and lightly smoothed.
- **Symmetry.** The hull is mirrored across X=0, with zero reflected position and UV error in every hull GLB. The arms are deliberately not mirrored.
- **Shading.** Edges sharper than 40 degrees are marked sharp.

Mirroring the port half also gives the cutting rod under the port nose a starboard twin. The hull, every arm part and every LOD have zero boundary edges and zero edges shared by more than two faces. Soft reconstruction forms remain in places, mostly in the underside machinery and the claw fingers; they were kept as part of the supplied silhouette. The cut faces are flat graphite caps that read as internal structure.

## Texture cleanup

The hull half, every arm part and the drums share one 4096 `GameUV` atlas, using 45% of the sheet. The source albedo was baked onto it selected-to-active from the high drone, with both arms still in their supplied places.

`scripts/clean_texture.py` uses the supply drone method with this drone's palette:

1. **Classification.** Five paints: graphite, gunmetal, ivory armor, red stripe and orange. This source's ivory is more saturated than the supply drone's, so armor and orange are separated by lightness and chroma.
2. **Plate majority.** `scripts/classify_faces.py` gives every face and every flat plate one majority paint, across all objects in the atlas. This removes the orange that the reconstruction smeared into the dark machinery.
3. **Detail-preserving cleanup.**
   - Painted surfaces: blotches are damped to 45%, grime on armor is lifted 40%, and fine detail is kept.
   - Machinery: blotches are damped to 25% and fine detail kept at 60%.
   - Each paint is pulled towards its palette colour, and the dark source red is lifted towards the reference red.
4. **Lights.** The source has no light texels, so the lights are placed from baked position and normal maps where the reference shows them:
   - the two wide slots and two small windows either side of the nose camera;
   - the two cutting-rod tips;
   - a faint blue plasma pilot glow in the torch nozzle, which is repainted pale ceramic.
5. **New surfaces.** Texels the bake could not reach (the cut caps, 1.1% of the atlas) are graphite. The drums are procedural orange with graphite end hubs.

See `reports/texture_cleanup.json`. The old normal and ORM maps are archived in `textures/source/` and are not used, because they amplify reconstruction noise.

## Validation

- **Blender:** every cut part and mesh is closed, arm weights are rigid, and all six clips have zero intersections (`reports/arm_pivots.json`, `mesh_reduction.json`, `symmetry_and_rig.json`, `animation.json`).
- **GLB buffers:** `scripts/check_glb.py` confirms the following for all three GLBs (`reports/glb_validation.json`):
  - finite positions, normals and UVs, and valid indices;
  - exact mirror symmetry including UVs on every hull;
  - rigid single-bone skin weights;
  - 9 joints, the six clips and both marker nodes.
- **Godot 4.7.2 Compatibility:** `godot/scripts/validate.gd` runs 43 checks with 0 failures (`reports/godot_validation.json`). It covers:
  - the LODs and the shared material, size and orientation, markers, the skeleton and all six clip lengths;
  - three convex hulls, with ray hits across the hull;
  - `get_work_transform`;
  - a real deploy, weld_seam loop, switch to stitch_weld and stow at 4x speed: the torch lights in its windows at the work surface, and stitch_weld makes three tack welds per cycle;
  - a real grab_place carrying a part 1.8 m and setting it down 2.5 cm from `PartPlace` before it is seated exactly.
- **Captures:** close, front, side, rear, top and underside views, plus weld, grab and stitch frames, are in `renders/`.

## Rebuilding

Blender scripts declare the workspace path at their start. Run them with the stated file open; Python-side scripts need numpy, opencv-python, scipy and Pillow.

1. `construction_drone_original.blend` → `scripts/align_source.py` → `scripts/prepare_asset.py`.
2. `scripts/split_arms.py` → `scripts/reduce_meshes.py` → `scripts/bake_source.py`.
3. `python scripts/clean_texture.py labels`, then `scripts/classify_faces.py` in Blender, then `python scripts/clean_texture.py paint`.
4. Reopen `construction_drone_uv_baked.blend` → `scripts/finalize_asset.py` → `scripts/arm_anim.py` → `scripts/export_asset.py`.
5. `python scripts/package_asset.py` → `python scripts/check_glb.py`. Packaging writes the scene and regenerates the clip timing block in `construction_drone.gd`.
6. `godot --headless --path godot --editor --import --quit`, then `godot --headless --path godot --script res://scripts/validate.gd`.
   - Captures: `godot --path godot -- --capture=close` (or `front`, `side`, `rear`, `top`, `underside`).
   - Work frames: `-- --capture=weld --task=weld_seam --time=2.6`.

For animation-only changes, open `construction_drone_game_ready.blend` and repeat steps 4 (from `arm_anim.py`) to 6. `arm_anim.py` takes a few minutes. When running Godot under a restricted account, set `APPDATA` to `godot/.local_appdata/`.
