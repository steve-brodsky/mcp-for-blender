# Mounted turrets

Three ship-mounted turrets, rebuilt from one generated source mesh into game-ready Godot 4 assets: a **quad cannon**, an **8-barrel gatling** and a **laser**. Each turret traverses on its base and its gun elevates on a trunnion, like a real mounted turret. The guns have small clips: the quad cannon's barrels recoil in turn, the gatling's barrels spin up, fire and spin down, and the laser charges and kicks.

Open `godot/project.godot` in Godot 4 and run the preview. A target drone circles over the deck. Press T to make the turrets track it (press again to let them scan), and hold Space to fire. Press 1, 2 or 3 to focus a turret, or 0 for all three. Drag to orbit and scroll to zoom.

![Godot lineup](renders/godot_lineup.png)

| Firing | |
| --- | --- |
| ![quad](renders/godot_fire_quad.png) | ![gatling](renders/godot_fire_gatling.png) |
| ![laser](renders/godot_fire_laser.png) | ![tracking](renders/godot_aim.png) |

| File | Purpose |
| --- | --- |
| `godot/assets/{quad,gatling,laser}_turret.glb` | Pivot hierarchy, meshes, clips and embedded basecolor, emission and ORM textures |
| `godot/scenes/{quad,gatling,laser}_turret.tscn` | Ready-to-use turret scenes (`MountedTurret` script, elevation limits set) |
| `godot/scripts/mounted_turret.gd` | `MountedTurret` API: aiming, firing, signals, muzzle flashes, laser beam, hitboxes |
| `godot/scripts/preview.gd`, `validate.gd` | Preview and capture scene, and the headless validation |
| `blender/mounted_turrets_game_ready.blend` | Current editable asset: all three rigs, the clips as NLA tracks, packed textures |
| `blender/mounted_turrets_original.blend` | Untouched supplied scene |
| `blender/mounted_turrets_welded.blend`, `_aligned.blend` | The source welded into three shells, then levelled, centred and scaled |
| `blender/mounted_turrets_parts_high.blend`, `_rigged_high.blend` | Full-resolution parts after the cuts, then with the rebuilt guns and pivots |
| `blender/mounted_turrets_prepared.blend`, `_uv_baked.blend` | Reduced halves, then unwrapped and baked |
| `textures/<t>_turret_basecolor_2k.png`, `_emission_2k.png`, `_orm_1k.png` | Final maps per turret |
| `textures/source/` | The three original reconstruction maps |
| `textures/work/` | Baked source albedo, masks, part ids, position and normal maps, labels and face classes |
| `renders/godot_*.png` | Captures from the actual Godot renderer |
| `reports/` | Alignment, part split, guns, pitch limits, reduction, bake, textures, symmetry, clips, export and Godot validation |

## Size and orientation

Each turret points along **-Z**, with **+Y up** in Godot. Its origin is at the centre of the base bottom, on the yaw axis. A nominal **4.0 m base diameter** was chosen because the source has no physical dimensions. That suits frigate and capital hulls; the 48 m beam frigate could carry several. Scale the scene root to suit your game.

| Turret | Length (gun forward) | Height | Triangles | Elevation range set | Clear range measured |
| --- | ---: | ---: | ---: | --- | --- |
| Quad cannon | 6.7 m | 2.9 m | 28,712 | -10° to +80° | -35° to +88° |
| Gatling | 7.6 m | 2.9 m | 32,640 | -10° to +75° | -21° to +75° |
| Laser | 7.0 m | 2.8 m | 34,250 | -10° to +80° | -17° to +87° |

The house traverses a full 360° on every turret. Each turret is one material and a 4.1 MB GLB. Godot's automatic mesh LODs are left on at import.

## Integration

Copy `godot/assets/<t>_turret.glb`, `godot/scenes/<t>_turret.tscn` and `godot/scripts/mounted_turret.gd` into the matching `res://` folders and instance the scene on your ship hull (the base bottom is the mounting face).

```gdscript
turret.aim_at(world_point)     # track a point at limited traverse/elevation speeds; call each frame for moving targets
turret.clear_target()          # return to rest, then scan (auto_scan)
turret.start_firing()          # hold the trigger: quad volleys, gatling spins up then fires, laser charge/beam cycles
turret.stop_firing()           # quad finishes its volley, gatling spins down, laser finishes its beam
turret.fire()                  # one laser shot, or start a quad / gatling burst
turret.is_on_target(); turret.can_reach(world_point)
turret.set_angles(yaw_deg, elevation_deg); turret.get_angles()
turret.get_muzzles(); turret.get_aim_direction()
signal shot_fired(muzzle)                       # quad and gatling: one per round, spawn your projectile here
signal charge_started                            # laser
signal beam_fired(origin, direction, length)     # laser: length stops at the first physics hit
signal firing_started / firing_stopped
```

Exports on the scene root: `traverse_speed_deg` (70), `elevation_speed_deg` (45), `min_elevation_deg` / `max_elevation_deg`, `traverse_limit_deg` (180 = unlimited), `aim_tolerance_deg`, `auto_scan`, `rounds_per_second` (gatling, 40), `beam_range`, `beam_duration`, `beam_cooldown`, `beam_color`, `effects` and `hitbox_layer`. With `effects = false` the turret draws no flashes, glow or beam, so your own VFX can hook onto the signals.

**Aiming.** The game drives aiming: the script turns the `Yaw` node about Y and the `Pitch` node about X. Elevation is measured from the trunnion. The muzzles sit up to 0.3 m off the trunnion axis, which is negligible at combat range. The elevation limits in the scenes are inside the clear ranges measured in Blender (`reports/pitch_limits.json`). The gun was swept in 1° steps against the house and base, with the barrels in full recoil.

**Hitboxes.** The script adds a cylinder on the base and a box on the house, which turns with `Yaw`, on `hitbox_layer`. The barrels have no collision.

**Node layout** (identical on all three, so one script drives them):

```
<T>Turret
├─ BaseMesh
└─ Yaw                         traverse (Y)
   ├─ YawMesh, YawRing         gun house + bearing ring
   └─ Pitch                    elevation (X) on the trunnion
      ├─ PitchMesh             mantlet drum (+ breech block / rotor housing)
      ├─ Barrel1..4 > Barrel#Mesh, Muzzle1..4    quad: recoil along the bore
      ├─ Spin > SpinMesh, Muzzle                 gatling: barrel cluster; Muzzle at 12 o'clock
      └─ Projector > ProjectorMesh, Muzzle       laser: recoil; Muzzle at the emitter window
```

| Turret | Clip | Length | What happens |
| --- | --- | --- | --- |
| all | `scan` | 8 s loop | Idle sweep, yaw ±35° with a gentle nod; stops as soon as the turret aims |
| Quad | `fire` | 0.67 s loop | Barrels 1, 4, 2, 3 recoil 0.18 m in turn, 1/6 s apart; `shot_fired` at each kick |
| Gatling | `spin_up` | 1.0 s | The cluster accelerates from rest to 4 rev/s; no rounds yet |
| | `fire` | 0.5 s loop | 4 rev/s; the script fires `rounds_per_second` from `Muzzle` |
| | `spin_down` | 1.5 s | Decelerates to rest |
| Laser | `charge` | 1.0 s | The projector draws back 6 cm while the emitter glow grows |
| | `fire` | 0.6 s | 12 cm recoil kick as the beam lights, then runs out |

The gatling's barrels are eightfold symmetric. `spin_up` ends after exactly two turns and `spin_down` covers exactly three, so the clips chain without a pop.

## What was done to the source

**Splitting and alignment.** The source was one 700k-triangle mesh with all three turrets. Welding its split UV seams left three closed shells. Every turret had been reconstructed tilted about 10° and yawed differently. For each turret:

- up comes from its dominant bottom-plate normal;
- the yaw axis is the centre of a circle fitted to the base rim;
- forward and the symmetry plane come from minimising the mirrored surface distance of the upper body (`reports/source_alignment.json`).

**Lopsidedness.** The reconstruction placed each house 0.07-0.15 m off its base centre. The parts were separated and the base recentred on its rim. The laser's and gatling's bases had also come out oval (the laser's was 3.5 × 4.0 m). The reference uses one base design for all three, so every turret now uses the quad's base, the roundest one.

**Moving parts.** Every cut is a manifold boolean on the closed high-resolution shells, so every part stays closed (`scripts/split_parts.py`).

1. A stepped solid of revolution separates the base from the house at the neck.
2. A cylinder on the trunnion axis is cut out of the house between the armour cheeks. A **mantlet drum** of the same axis fills it. A drum turning on its own axis never opens a gap, so the gun pitches cleanly.
3. On the quad and gatling, everything in front of the house face inside the gun slot was removed (the bent source barrels). The hood over the slot is cut back to just ahead of the trunnion; the first quad build could only elevate 31°.
4. A gunmetal **bearing ring** covers the neck joint.

**Barrels rebuilt straight.** The source barrels were bent, melted together and not parallel. They were rebuilt as clean solids of revolution, sized from the source: spacing, radii and the 4.3-4.7 m muzzle distance (`scripts/build_guns.py`).

- **Quad:** four barrels on a 0.34 × 0.31 m grid. Each has a heavy jacket, a collar, a slotted muzzle brake and a recessed bore. They share a breech block and a guide band.
- **Gatling:** a rotor housing with eight barrels on a 0.29 m circle, a spindle, a hub and two clamp rings. The barrels have open bores.
- **Laser:** the source projector box was kept. It was cut out above its sloped underside, turned level about the trunnion (it sat 10.75° nose-up) and mirrored.

**Symmetry.** The base, the house and the laser projector are mirrored from their port (-X) halves. There is zero reflected-vertex error and the UVs are shared (`reports/symmetry.json`). The rebuilt guns are symmetric by construction. Every mesh is closed, with no boundary or non-manifold edges.

**Reduction.** The supply and construction drone methods were applied to the half meshes, with thresholds scaled to these 4 m turrets (`reports/mesh_reduction.json`):

- collapse decimation to 12-16%;
- crease-locked Taubin smoothing against reconstruction ripple;
- panel flattening, which covers 29-70% of the surface depending on the part.

Edges sharper than 40° are marked sharp.

## Texture cleanup

Each turret has its own 4096 working atlas (exported at 2K). The source albedo was baked onto it from the high-resolution parts, in the rest pose. The base underside and the neck cap under the house are never seen, so their UV islands are shrunk to 15%.

`scripts/clean_texture.py` and `classify_faces.py` follow the drone pipeline with the reference palette:

1. **Classification.** Texels are sorted into four paints by Lab lightness, chroma and hue: sand armour, graphite, gunmetal and the base light strips. Blender then gives every face, and every flat plate, one majority paint.
2. **Detail-preserving cleanup.** Mid-scale blotches are damped (armour 45%, machinery 25%) and grime on armour is lifted 40%. Each paint is pulled towards its palette colour, and panel seams, bolts and chips are kept. The armour palette was checked against the reference render.
3. **Cut faces.** Faces the booleans created carry no source UVs. They baked magenta and are painted graphite machinery.
4. **Rebuilt parts.** These are painted procedurally:
   - a gunmetal bearing ring;
   - graphite drums and breech blocks with gunmetal hub faces;
   - dark blued-steel barrels with sooty muzzles and machined forward-facing lips.
5. **Lights.** The base strips are the source's near-white texels on the base. They glow white-blue in the emission map. The laser's emitter window glows blue.
6. **ORM.** Occlusion is 1. Roughness and metalness are set per paint: armour 0.68 / 0.1, graphite 0.55 / 0.45, gunmetal 0.5 / 0.55, barrels 0.38 / 0.8. Emission strength is 2, as on the ships.

See `reports/texture_cleanup.json`. The source ORM and normal maps are archived in `textures/source/` and are not used, because they amplify reconstruction noise.

## Validation

- **Blender:**
  - all cut parts are closed;
  - the halves mirror exactly;
  - the elevation sweeps include the barrels in full recoil;
  - the house clears the base through 360° of traverse at rest, minimum and maximum elevation (`reports/pitch_limits.json`).
- **Godot 4.7.2 Compatibility:** `godot/scripts/validate.gd` runs 73 checks with 0 failures (`reports/godot_validation.json`). For each turret it covers:
  - nodes, muzzles, the 4 m size, orientation, the single shared PBR material, generated LODs and clip lengths;
  - aiming at a far target, with an error under 0.001°;
  - the elevation clamp and `can_reach`;
  - house and base hitboxes;
  - a real firing run:
    - quad: 8 rounds in two loops, 0.15 m recoil observed, stops after the volley;
    - gatling: no rounds while spinning up, 40 rounds/s once spun up, spins down to rest;
    - laser: charges for 1 s, then the beam stops on a wall 56.5 m away and leaves along the bore.

## Rebuilding

Blender scripts declare the workspace path at their start. Run each with the stated file open (`exec(open(path).read())`). The Python-side script needs numpy and opencv-python.

1. `mounted_turrets_welded.blend` → `scripts/align_source.py` (saves `_aligned`).
2. `scripts/split_parts.py` → `scripts/build_guns.py` → `scripts/pitch_limits.py`.
3. `scripts/reduce_meshes.py` → `scripts/bake_source.py`. The bake can take one turret per call: set `TURRETS = ('Quad',)` first.
4. `python scripts/clean_texture.py labels`, then `scripts/classify_faces.py` in Blender, then `python scripts/clean_texture.py paint`.
5. Reopen `mounted_turrets_uv_baked.blend` → `scripts/finalize_asset.py` → `scripts/animate.py` → `scripts/export_asset.py`.
6. `godot --headless --path godot --editor --import --quit`, then `godot --headless --path godot --script res://scripts/validate.gd`.
   - Captures: `godot --path godot -- --capture=lineup` (or `quad`, `gatling`, `laser`, `aim`, `fire_quad`, `fire_gatling`, `fire_laser`).

When running Godot under a restricted account, set `APPDATA` to `godot/.local_appdata/`.
