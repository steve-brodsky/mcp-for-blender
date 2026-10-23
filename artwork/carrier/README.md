# Asterion CV-74 modular carrier

Original carrier built in Blender 5.1 through Blender MCP. All six supplied reference images were inspected before construction. The supplied reference artwork and the earlier watchtower files were preserved.

Start with `blender/carrier_source.blend` for editing, `exports/carrier_hull.glb` for the reusable bare hull, or `godot/project.godot` for the working modular demonstration.

![Asterion carrier](renders/front_three_quarter.png)

## Delivered assets

- `blender/carrier_source.blend`: editable layered geometry, bevel/normal stacks, source door animation, all ten module libraries and an assembled preview. A second scene contains the module presentation.
- `blender/carrier_game_ready.blend`: separate optimized scene; main hull has four mesh objects and zero modifiers. Canonical game modules are hidden at the origin for individual export; the bare-hull GLB excludes them.
- `blender/modules/*.blend`: ten independently editable, textured module projects, with origins at the common mounting interface.
- `exports/carrier_hull.glb`: four meshes, 20 socket transforms, three hangar navigation transforms, independent engine emission and two separate sliding doors. Weapons and systems are not baked into this file.
- `exports/weapons/*.glb`: five articulated weapons.
- `exports/subsystems/*.glb`: five standardized subsystems.
- `exports/lods/carrier_lod0.glb`, `carrier_lod1.glb`, `carrier_lod2.glb`: bare-hull variants.
- `textures/hull/`: four shared 2048×2048 atlases: base color, tangent-space normal, packed ORM, emission. All are embedded in GLBs and packed in Blender files. Modules share these atlases; `textures/modules/` intentionally needs no duplicate maps.
- `godot/`: portable project with its own asset copies, wrapper scene, explicit Marker3D sockets, configurable loadout, animation resources, demo controls and runtime tests.
- `renders/`: six requested final views, a closed hangar, six orthographic inspections, actual GLB round-trip render and an actual Godot capture. Earlier phase renders are retained for comparison.
- `reports/`: measured geometry, attachment manifest, launch clearance, binary checks, Blender round-trip and Godot runtime results.

## Scale and coordinates

Hull dimensions are **106.00 m long × 61.34 m wide × 22.67 m tall**, including dorsal mast and lower mechanical details. Root scale is `(1, 1, 1)`.

Blender authoring uses +Y forward, +X starboard, +Z up. glTF converts this to Godot **-Z forward, +X starboard, +Y up**. Do not add an extra -90° root rotation or import scale. All module origins are at the center of the bottom mounting interface. An identity local transform attaches a compatible module.

## Measured geometry

| Hull variant | Triangles | Hull meshes | Draw surfaces |
|---|---:|---:|---:|
| LOD0 | 34,461 | 4 | 7 |
| LOD1 | 19,213 | 4 | 7 |
| LOD2 | 7,831 | 4 | 7 |

| Asset | Socket class | Triangles | Meshes | Draw surfaces |
|---|---|---:|---:|---:|
| heavy_kinetic | HEAVY | 1,444 | 3 | 3 |
| heavy_beam | HEAVY | 2,316 | 3 | 5 |
| medium_assault | MEDIUM | 1,908 | 3 | 3 |
| point_defense | PD | 966 | 3 | 3 |
| missile_launcher | MISSILE | 1,448 | 3 | 4 |
| shield_generator | SYSTEM | 1,336 | 2 | 3 |
| sensor_array | SYSTEM | 1,644 | 2 | 3 |
| fire_control | SYSTEM | 372 | 2 | 3 |
| fighter_operations | SYSTEM | 364 | 2 | 3 |
| aux_reactor | SYSTEM | 776 | 2 | 3 |


Default assembled loadout: **60,457 triangles**, approximately **71 material draw surfaces per render pass**, before engine batching, shadow passes or culling. Four atlas materials represent the shared PBR surface and three distinct emissive strengths. Each GLB embeds its textures; a larger game may externalize these for cross-asset texture deduplication.

Editable hull source: 19 mesh objects, 126,303 evaluated triangles. The source scene includes 99 meshes including library parts and linked default-loadout instances, using 46 unique mesh datablocks. Static game geometry is consolidated independently of that source structure.

## Use in Godot

Open `godot/project.godot` in Godot 4 and run the project. Tested with **4.7.2-stable (official)** on Windows; the preview uses the Compatibility renderer. The project is isolated from existing Godot projects. The engine executable extracted from the user's existing archive is under ignored `tools/`; an installed Godot executable works equally well.

| Control | Action |
|---|---|
| Left drag / wheel | Orbit / zoom |
| H | Open or close the side hangar |
| F | Spawn and launch a fighter-sized clearance placeholder |
| W | Swap the first heavy gun between kinetic and twin beam |
| A | Apply yaw and elevation to the first heavy gun |
| M | Toggle a missile launcher's covers |
| S | Swap a shield generator and auxiliary reactor |

The wrapper scene creates **real Marker3D nodes**; it does not assume imported Blender empties are Marker3D. The ready handler reparents the imported door meshes under `Hangar/Doors`; the wrapper's AnimationPlayer has `hangar_open` and `hangar_close`, each two seconds long. In Blender the source actions run across frames 1–49 at 24 fps.

```gdscript
var sockets = $Carrier.available_sockets("HEAVY")
$Carrier.attach_module("SOCKET_WEAPON_HEAVY_01", "heavy_kinetic")
$Carrier.swap_weapon("SOCKET_WEAPON_HEAVY_01", "heavy_beam")
$Carrier.aim_weapon("SOCKET_WEAPON_HEAVY_01", 0.3, 0.2)
$Carrier.attach_module("SOCKET_SYSTEM_01", "shield_generator")
$Carrier.remove_module("SOCKET_SYSTEM_01")
print($Carrier.installed_loadout())
$Carrier.set_hangar_open(true)
# Wait for opening to finish before spawning.
var fighter = $Carrier.spawn_placeholder_fighter()
$Carrier.launch_fighter(fighter)
$Carrier.set_engine_intensity(4.0)
```

Weapons contain `TURRET_YAW`, `TURRET_PITCH` and `MUZZLE_01` (additional muzzle nodes for paired barrels). Missile cells point upward and have their own cell markers and two cover hinges. The covers rotate smoothly about those hinges through 110° over 1.5 seconds, with eased starts and stops. Adjust `missile_cover_duration` on the Carrier wrapper to change the speed. Pressing M during movement reverses from the current pose; removing the launcher cancels its animation. For an immediate setup pose, call `missile_covers(socket_id, opened, true)`. The demo limits yaw to ±60° and elevation to -0.03…π/3 radians. The aft heavy socket faces rearward to keep barrels clear of the bridge. Do not assume a free 360° traverse at every hardpoint.

The default loadout lives in `reports/attachment_manifest.json`, copied into `godot/assets/attachment_manifest.json`. Edit that data and run `python scripts/prepare_godot.py` to regenerate the wrapper and portable asset copies. Runtime scripts can replace modules without re-exporting the hull.

| Socket class | Compatible modules |
|---|---|
| HEAVY | heavy_kinetic, heavy_beam |
| MEDIUM | medium_assault |
| PD | point_defense |
| MISSILE | missile_launcher |
| SYSTEM | shield_generator, sensor_array, fire_control, fighter_operations, aux_reactor |


## Functional hangar

Starboard launch direction is +X. The physical bay has an approximately 22 m wide × 7.2 m high clear aperture and 12 m depth. Two coplanar external leaves slide along the ship's length from ±5.9 m closed to ±17.8 m open. Each leaf is 11.8 m wide and 8.4 m tall. Their exterior edges meet flush at the center; a narrow recessed gasket blocks light behind that seam without overlapping the visible panels. Internal floor, ceiling, back wall, portal ribs, service lockers and guide lights are modeled. Decorative dorsal square hatches and grille plates were removed to distinguish the 20 real attachment sockets from ordinary armor.

| Navigation marker | Godot position | Godot yaw |
|---|---|---:|
| HANGAR_SPAWN | (23, -1.3, 0) | -90° |
| HANGAR_EXIT | (42, -1.3, 0) | -90° |
| HANGAR_APPROACH | (65, -1.3, 0) | -90° |

The placeholder envelope is 7 m wide × 2.5 m high × 9 m long in fighter-local axes. Blender tested 81 surface-intersection samples against evaluated hull triangles. Godot tested 41 volume-overlap samples against 13 solid collision proxies. Both passed. The source side-hangar render shows a simple full-envelope placeholder; it is not a finished fighter asset. The former aft shoulder gaps on both sides are sealed with full-depth solid bulkheads and matching collision volumes, leaving the starboard hangar as the only side entrance.

## Editing and export

Work from the detailed source. Source collections separate hull, armor, hangar, engines, structural details, emissives, socket markers, weapon libraries, subsystem libraries and presentation. Preview instances share library mesh data. Hide `DEFAULT_LOADOUT_PREVIEW` to inspect the bare hull.

For a local edit, open `carrier_game_ready.blend`, select `GAME__CARRIER_ROOT` and all descendants, and export selected objects as GLB with +Y-up conversion enabled. Exclude canonical modules, cameras and lights. Export module roots individually at the origin. Keep hierarchy, normals, UVs and textures enabled. Use `scripts/validate_glb.py` afterward. The original construction and staged optimization scripts are retained as implementation records; they are stateful Blender scripts and should not be executed repeatedly in an existing finished scene.

Normalize UV layer names to `UV_ATLAS` before joining meshes. The final atlas is a 4×4 shared sheet with 512 px tiles; armor materials use distinct tile regions. UVs overlap intentionally for a trim workflow and are not a unique lightmap unwrap. Game materials collapse equivalent nonemissive shaders while preserving the UV-encoded appearance. ORM red carries an authored AO mask, green roughness and blue metallic; the glTF material uses metallic/roughness, with geometric lighting providing occlusion. No Blender-only procedural shader is required by the export.

Revalidate the portable demo after updating exports:

```text
python scripts/validate_glb.py
python scripts/prepare_godot.py
godot --headless --path godot --editor --import --quit
godot --headless --path godot --script res://scripts/validate.gd
```

Use a writable APPDATA location when running Godot under a restricted automation account. This session used `godot/.local_appdata/`; generated cache folders and the local engine are ignored.

## Validation and remaining limits

- Final binary checks passed for all 14 GLBs: finite vertices/UVs, unit normals, valid indices, zero degenerate triangles, embedded textures, weapon hierarchy, muzzle nodes, hull separation and socket positions.
- All 14 final exports were actually re-imported through Blender MCP; texture appearance was visually compared to the source. Every editable module and both principal Blender projects were opened from disk.
- Godot runtime: 228 checks passed, zero failures. An actual GPU-rendered Compatibility screenshot is in `renders/godot_preview.png`.
- A Blender 5.1 viewport access violation occurred after the initial rapid import/delete validation batch. Saved assets survived and were reopened. Later validation retained imported data until reopening the source, and removed unrelated empty export scenes; no second crash was observed. The precise Blender crash cause is not proven.
- LOD0 is above the requested 15k–25k hull guideline to retain modeled bay, bevelled primary forms and mechanical detail. LOD1 is within that range. The sensor array is slightly above its suggested triangle range.
- LOD GLBs are supplied separately; the demo does not implement automatic distance switching. Reduced LODs are decimated and can simplify small trim details.
- Collision is deliberately approximate. Door leaves are visually animated and launch is script-gated; the leaves do not have moving physics colliders. Fighters are validation placeholders, with no combat or docking AI.
- Shared trim UVs trade unique paint/weathering for lower material count. There is no unique sculpt-to-lowpoly bake, damage state, custom lightmap UV set or hand-painted per-panel wear pass.
- Only the installed Godot 4.7.2 Compatibility renderer was runtime tested. Other Godot 4 releases and mobile/Forward+ rendering require project-specific validation. Large-fleet performance and production gameplay integration were not benchmarked.

Full socket positions, orientations, compatibility lists and loadout are machine-readable in `reports/attachment_manifest.json`. See `reports/asset_audit.md` and `reports/export_validation.md` for measured details.
