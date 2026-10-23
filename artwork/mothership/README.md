# Mothership / Ion Bay

The current model has bilateral symmetry around **X = 0**, matching forcefield hangars,
and a cleaner ivory/red paint finish. Open `blender/mothership_refined.blend` for the
editable source, or `godot/project.godot` for the portable demo.

![Symmetric mothership](renders/symmetric_top.png)

## Current revision

- The starboard hull half is the source of both sides. The saved Blender file retains
  its Mirror modifier, so future hull edits can remain symmetric.
- The outer armor was faired, stale custom split normals were removed, and a detached
  bow fragment was removed. The mesh retains the original reconstruction's general
  shape and mechanical detail; this is not a complete hard-surface retopology.
- The entire starboard hangar assembly is reflected to port, including collar,
  architecture and curved forcefield. Both bays now share the same elevation.
- The albedo was cleaned using built-in imagegen. `textures/hull_clean_atlas.png`
  is the actual 1254 x 1254 output; it is not presented as an 8K texture. It replaces
  the heavy weathering and painted surface chatter with cleaner ivory/red paint.
  Fine machinery detail is simplified compared with the previous 8K atlas.
- Hull roughness is 0.68 and metallic is 0.12. No normal/bump texture is applied.
- The previous source is preserved in `blender/mothership_before_symmetry.blend`.
  Earlier texture artwork remains under `textures/`.

## Files

| File | Purpose |
| --- | --- |
| `blender/mothership_refined.blend` | Current editable, packed Blender source |
| `blender/mothership_before_symmetry.blend` | Previous source backup |
| `godot/assets/mothership.glb` | Current portable export with embedded clean albedo |
| `godot/scenes/mothership.tscn` | Reusable animated fields, lights, collision and markers |
| `godot/scenes/demo.tscn` | Orbit/zoom presentation |
| `symmetry_validation.json` | Geometry comparison and revision notes |
| `glb_validation.json`, `runtime_validation.json` | Latest export/runtime checks |
| `textures/repaint/symmetry_cleanup.md` | Texture tool and exact prompt |

The prototype at `C:/Users/stevi/OneDrive/Documents/space-game-prototype` also contains
this updated GLB and matching wrapper scene.

## Scale and coordinates

Godot uses **-Z forward, +X starboard, +Y up**, at unit scale. The current assembly
measures approximately **98.14 m long x 49.10 m wide x 29.89 m high** and contains
**92,052 triangles**, seven meshes, and 19 material surfaces. The GLB is about 6 MB.
Blender uses +Y forward and +Z up; do not add another import rotation.

| Marker | Starboard position in Godot | Port position in Godot |
| --- | --- | --- |
| HangarSpawn | (14, 1, 6) | (-14, 1, 6) |
| HangarExit | (26, 1, 6) | (-26, 1, 6) |
| HangarApproach | (45, 1, 6) | (-45, 1, 6) |

The blue membranes have no colliders. Collision proxies are approximate. The wrapper
supports `set_forcefield_enabled(bool)` and `hangar_spawn_transform(port)`.

## Demo controls

Left drag orbits; the wheel zooms. 1 selects overview, 2/H starboard bay, 3 aft,
4 port bay, F toggles the fields, Space toggles turntable motion, Escape exits.
The prototype uses its own right/middle-drag orbit controller.

## Validation and editing

The exported GLB has mirrored position counterparts to 0.1 mm precision and zero
degenerate triangles. Both launch corridors passed a 1.6 m diameter probe sweep
(32 positions per side). All 111 demo runtime checks passed in Godot 4.7.2. The
prototype's camera, field, marker and imported geometry checks also passed, including
an actual Forward+ / D3D12 rendering on an RTX 3080. Godot's mesh compression can
introduce submillimeter differences between separately imported surfaces.

```text
python scripts/validate_glb.py
godot --headless --path godot --editor --import --quit
godot --headless --path godot --script res://scripts/validate.gd
```

For future Blender edits, work from the current source and run
`scripts/export_symmetry_revision.py` through Blender. The one-time
`scripts/symmetry_revision.py` is for the **before-symmetry backup only**.
Historical reconstruction/projection scripts are implementation records, not a
repeatable pipeline for the current source. The earlier hangar fit report describes
the previous asymmetric source; current runtime clearance is in `runtime_validation.json`.
