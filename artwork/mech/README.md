# Combat mech

This is a fighter-class space-combat mech built from the ComfyUI reconstruction. It is
separated into rigid mechanical parts, mirrored to be symmetric, rigged, given seven animations,
and packaged as a reusable Godot 4.7 scene. The beam rifle is a separate asset that can be swapped.

Open `godot/project.godot` and press **F5** to run the preview
(`scenes/previews/combat_mech_preview.tscn`).

![Godot review](renders/godot_review_sheet.png)

## Folder structure

| Path | Contents |
| --- | --- |
| `blender/combat_mech.blend` | Editable source: rig with IK authoring controls, game mesh, rifle, actions, high-res parts (`HIGH`), original mesh (`SOURCE_original`, hidden) |
| `blender/mech_original.blend` | Untouched copy of the imported ComfyUI scene |
| `blender/mech_segmented_high.blend` | Checkpoint after segmentation and symmetrization |
| `textures/mech_*.png`, `textures/rifle_*.png` | Baked base colour, ORM (occlusion/roughness/metal) and normal maps (2048² mech, 1024² rifle) |
| `textures/source/` | The three original ComfyUI textures |
| `godot/assets/ships/combat_mech/` | `combat_mech.glb` (mesh, skin, markers, 7 clips) and `beam_rifle.glb` |
| `godot/scenes/ships/combat_mech.tscn` | Reusable mech scene |
| `godot/scenes/weapons/beam_rifle.tscn` | Reusable rifle scene |
| `godot/scenes/previews/combat_mech_preview.tscn` | Standalone preview |
| `godot/scripts/` | `ships/combat_mech.gd`, `ships/mech_aim_modifier.gd`, `weapons/beam_rifle.gd`, `effects/` (thruster, beam) |
| `godot/tests/` | `validate_combat_mech.gd` (70 runtime checks), `capture_combat_mech.gd` (renders) |
| `scripts/` | Blender pipeline: segmentation, symmetrization, rig, low-poly, bake, animation, export, `check_glb.py` |
| `reports/` | `asset_report.json`, `glb_validation.json`, `runtime_validation.json`, Godot logs |
| `renders/` | Review images. `seg_pose_test_v1.png` and `close_joints_v2.png` show the segmentation gate. `rig_acceptance_poses.png` shows the rig gate. `godot_*.png` come from Godot. |

The `godot/` folder uses the prototype's layout (`assets/ships`, `scenes/ships`, `scripts/...`).
To integrate it, copy `assets/ships/combat_mech`, `scenes/ships/combat_mech.tscn`, `scenes/weapons`,
`scripts/ships/combat_mech.gd`, `scripts/ships/mech_aim_modifier.gd`, `scripts/weapons` and
`scripts/effects/{mech_thruster.gd,thruster_plume.gdshader,beam_effect.gd,beam.gdshader}` into
`space-game-prototype`, keeping their paths. None of these names clash with existing files there.

## Model

- Scale and axes: about 9.6 m tall. In Godot it faces **-Z**, with +Y up, at unit scale; the Visuals node is rotated 180°.
- Budget: the body is 26,189 triangles and the rifle is 4,000. The source had 699,710.
- Body materials: `M_Mech_Armor` (ivory, charcoal and red, from the atlas), `M_Mech_Thruster` (blue emitters) and `M_Mech_Visor` (amber).
- Rifle materials: `M_Rifle_Metal` and `M_Rifle_Energy`.
- Emission: emissive surfaces are separate surfaces, so their glow is set per instance at runtime.
- Symmetry: each central part (torso, head, thruster pack, pelvis) was mirrored about its own fitted plane. The source torso was yawed 4°. The thruster pack was yawed 8.5° and offset 0.97 m. The right arm and leg were mirrored to the left. The shield was registered onto the new left forearm.
- Segmentation: there are 20 rigid parts plus 15 charcoal joint pieces (ball joints, knee cylinders, waist ring). Every vertex is weighted 100% to one bone, so the armor never bends.

## Rig hierarchy

```
root
└─ pelvis                      (thighs and torso hang from here)
   ├─ torso                    (waist pivot; backpack and thruster pack are rigid on it)
   │  ├─ head
   │  ├─ shoulder.R → upper_arm.R → forearm.R → hand.R   (socket_weapon.R marker on hand.R)
   │  └─ shoulder.L → upper_arm.L → forearm.L → hand.L   (shield is on forearm.L)
   ├─ thigh.R → shin.R → foot.R
   └─ thigh.L → shin.L → foot.L
```

- Shoulder armor rides on the `shoulder.*` bones. Raise them a little when lifting the arms.
- In Blender, `IK_rifle` drives both hands with 3-bone IK chains (hand, forearm, upper arm). The clavicle bones are deliberately left out, so the arm sockets never leave the torso. The right hand follows the grip offset. The left hand is position- and rotation-constrained: palm up under the rifle's receiver just ahead of the grip (`SupportGrip`), fingers forward along the barrel, elbow pole below and to the left (`SUPPORT_*` in `scripts/mech_aim_rig.py`). Constraint influence is 0 by default.
- `scripts/mech_anim.py` captures the IK result back to FK. The GLB contains only baked FK keys.

## Animations (30 fps)

| Clip | Length | Loop | Notes |
| --- | --- | --- | --- |
| `hover_idle` | 3.0 s | yes | Low-ready rifle, gentle torso, leg and pelvis stabilization |
| `cruise_flight` | 2.0 s | yes | Legs half tucked, rifle along the body, torso pitched forward |
| `boost` | 2.5 s | no | Braces into a tight tuck in 0.5 s, then holds with a vibration; ends on the boost pose |
| `aim` | 0.67 s | no | Raises into a two-handed aim, in a bladed stance (torso turned 45°), rifle shouldered on the right, left palm up under the receiver; ends holding the aim pose |
| `fire` | 0.4 s | no | Small kick and return. In the AnimationTree it is filtered to the upper body |
| `hit_reaction` | 0.6 s | no | Torso jolt, arm flail, recovery |
| `disabled` | 2.0 s | no | Power loss into a limp drift pose; the rifle lowers |

The AnimationTree is built by `combat_mech.gd`. It has a state machine with 0.35 s crossfades and two one-shots: `hit` (full body), then `fire` (upper body).

## Godot API (`CombatMech`)

```gdscript
mech.set_state("hover_idle" | "cruise_flight" | "boost" | "aim" | "disabled")
mech.set_aim_target(global_point)   # or null; procedural torso/head tracking while aiming
mech.play_fire(optional_end_point)  # plays fire + beam; defaults to the aim target or 220 m ahead
mech.play_hit()
mech.set_thrusters_enabled(bool)    # main engines idle glow
mech.set_boost(0.0 .. 1.0)          # main + leg jets
mech.pulse_jet("shoulder_L" | "shoulder_R" | "legs" | "pack", duration, strength)
mech.equip_weapon(scene_instance)   # swap the hand-held weapon
signal weapon_fired(muzzle_global, end_global)
```

The mech has no movement, AI or damage logic. `Hitboxes` holds 11 bone-following capsule
`Area3D`s (monitoring off, `bone` meta) for gameplay queries.

### Weapon replacement

`WeaponSocket` is a `BoneAttachment3D` on `hand.R`. Its `Grip` child copies the grip frame
authored in Blender (`socket_weapon.R`). Any weapon scene works if it meets three requirements:

1. Its origin is at the pistol grip.
2. It fires along its local **+Z**, with +Y up. This is the Blender −Y forward / +Z up convention exported to glTF.
3. It has a `Muzzle` node and a `fire(end_point)` method. A `fired` signal is optional.

Set `rifle_scene` on the mech, or call `equip_weapon()` at runtime. `BeamRifle` exposes `muzzle`,
`support_grip`, `beam_range`, `beam_duration` and `set_idle_energy()`.

### Thrusters

There are eight imported marker attachments, so they follow the bones:
- `thruster_pack_L/R` on the torso
- `thruster_shoulder_L/R` on the shoulder armor
- `thruster_calf_L/R` and `thruster_heel_L/R` on the shins

Each gets a `MechThruster` node: an additive plume cone, a nozzle glow, sparse soft particles on the main pack, and an omni light. Exhaust is along the marker's local +Z. By default:
- The main pack runs at 0.3 at idle, 0.55 in cruise, and 0.85–1.0 in boost or at boost 1.
- The leg jets follow `boost`.
- The shoulder jets fire only on `pulse_jet` or `play_hit`.
- Everything is off when disabled, and the visor dims.

The thruster surface's emission tracks the main intensity.

### Firing effect

`BeamEffect` sits on the rifle's `Muzzle`. Each shot draws a muzzle flash, a blue core and halo
beam, an impact flare at the endpoint, and a light. It lasts 0.28 s (fast attack, then fade).
The beam start follows the animated muzzle every frame. The endpoint is configurable, and the
effect is purely visual.

## Preview controls

| Input | Action |
| --- | --- |
| Left/right drag, wheel, middle drag | Orbit, zoom, pan |
| `1`–`5` | hover / cruise / boost / aim / disabled |
| `F` / `Space` | Fire. It switches to aim first, then shoots the orange target drone |
| `H` | Hit reaction |
| `T` | Thrusters on or off |
| `B` | Boost toggle (or use the slider) |
| `Q` / `E` | Left / right shoulder jet |
| `C` | Auto-cycle through every clip, firing during aim |
| `M` | Spawn two extra instances |
| `F1`–`F5` | Front, side, back, three-quarter and top views |
| `R` | Reset the camera |

## Validation

- **Blender, segmentation gate:** every part posed independently with no stretching (`renders/seg_pose_test_v1.png`). Joint close-ups were re-checked after boundary relaxation and joint hardware were added (`renders/close_joints_v2.png`).
- **Blender, rig gate:** all eight required poses rendered, including the IK two-handed aim with zero IK residual (`renders/rig_acceptance_poses.png`). The animation key poses were reviewed in `renders/anim_keyposes_v2.png`.
- **GLB:** `scripts/check_glb.py` parses the binary. It confirmed 26,189 + 4,000 triangles, no invalid indices or non-finite data, weight sums of exactly 1.0 with 100% rigid vertices, 18 joints, 7 clips starting at t = 0, and all markers present.
- **Godot 4.7.2:** `godot --headless --path godot -s tests/validate_combat_mech.gd` ran **79 checks with 0 failures** and logged no errors or warnings. It checks:
  - import and clips, loop modes, the triangle budget and AnimationTree states
  - the socket error against `hand.R` (0.0000 m in every state)
  - the rifle pointing forward in the aim clip (dot 1.000), and procedural aim turning to a target 40° off-axis (0.766 → 1.000)
  - the left palm stays on the underbarrel support point in the aim clip (0.077 m), under procedural aim (0.077 m) and while firing (0.008 m), measured on the final rendered pose
  - both upper-arm sockets stay on the torso in every state and under procedural aim. Drift is under 0.1 m; the only shoulder motion is the small authored shrug in boost and disabled.
  - the beam, its endpoint and duration, plus the fire and hit one-shots
  - every thruster mode, and thruster attachments following their bones
  - 11 hitboxes, 3 independent instances with their own rifles and materials, and runtime weapon replacement
- **Godot captures:** `godot --path godot -s tests/capture_combat_mech.gd` renders `renders/godot_*.png` with Forward+.

## Known limitations

- **Hip region:** the source was one fused shell, and its thighs and skirt plates merged into a single surface. Thighs are separated by a cut plane, so extreme hip flexion shows the charcoal ball joint and cap rather than a modeled socket. Shoulders, elbows, knees and ankles are cleaner.
- **Cut faces:** the faces at the cuts are flat charcoal caps. They read as internal structure, not modeled mechanisms.
- **Shared texture on the left:** the left limbs share the right side's UVs, so painted markings are mirrored. The original asymmetric red stripes on the shoulders are therefore identical.
- **Height:** it is 9.55 m rather than 10 m, because the symmetrized thruster pack uses the shorter source pod.
- **Hands:** fingers are rigid parts of the hand. The rifle grip sits in the open claw rather than being wrapped by articulated fingers.
- **Two-handed aim:** the arms are short for the body, so the two-handed aim needs a strongly bladed stance (torso turned 45°), and the left hand supports the rifle just ahead of the grip rather than far out on the foregrip. The placement came from a search over reach and armor penetration; a few rifle vertices still graze the right shoulder armor.
- **`boost` does not loop:** it holds its final pose. Crossfade out to change state.
- **Emissive surfaces were picked by baked color,** so a few nozzle-rim faces stay non-emissive.
- **Hitboxes** are approximate capsules, and there is no physics body.
- **Source texture artifacts:** the textures keep the source's weathering and some AI-generation noise. No new PBR detail was invented. ORM and normal are baked from the source maps.
- **Prototype integration:** the asset is not wired into the prototype's `main.tscn`. Per the brief, everything lives in this folder; see the copy list above.
- **EEVEE preview:** Blender 5.1's EEVEE viewport capture did not render in this environment (also noted in the mothership asset), so Blender reviews use Workbench renders.

## Rebuilding

In Blender, run the scripts in this order:

1. `mech_label.py` and `mech_build_symmetric.build()`, which make the HIGH parts.
2. `mech_rig.py`, `build_armature()`, `build_joint_hardware()` and `bone_parent_all()`.
3. `mech_lowpoly.build_body()`, then `mech_bake.bake_atlas(...)`.
4. `mech_anim.build_all()`.
5. `mech_export.export_all()`.

Then run `python scripts/check_glb.py` on the GLBs and the Godot test.
