# Export validation

All final 14 GLBs passed the independent binary validator. All final 14 were re-imported in Blender through MCP after atlas material consolidation. Saved source and optimized projects reopened successfully; all ten source modules were opened and saved as standalone Blender projects.

| Test | Observed result |
|---|---|
| Serialized geometry | Finite positions and UVs, unit normals, valid indices, no zero-area triangles |
| Export UVs | Present on every primitive; all nine palette regions preserved |
| Materials and images | Embedded PNGs, standard metallic/roughness and tangent normal data |
| Bare-hull separation | Four meshes, 20 sockets, no baked weapon/subsystem instances |
| Socket transforms | All 20 translations match manifest within 0.0001 m |
| Module pivots | Mount-origin local identity verified for all compatible combinations in Godot |
| Weapon controls | Preserved yaw/pitch hierarchy and muzzle transforms; swap and controls ran |
| Hangar geometry | 81 actual evaluated-hull BVH samples, no envelope intersections |
| Godot physics clearance | 41 full-volume shape queries, no collisions along launch path |
| Doors | Flush, non-overlapping exterior faces; sealed center/frame; open and closed endpoints ran in AnimationPlayer |
| Godot runtime | 228 checks, zero failures, 4.7.2-stable (official) |
| Visual checks | Six requested views, six orthographic directions, closed bay, GLB round-trip, GPU Godot capture |

| Final GLB | Triangles | Meshes | Surfaces | Embedded images |
|---|---:|---:|---:|---:|
| exports/carrier_hull.glb | 34,461 | 4 | 7 | 4 |
| exports/lods/carrier_lod0.glb | 34,461 | 4 | 7 | 4 |
| exports/lods/carrier_lod1.glb | 19,213 | 4 | 7 | 4 |
| exports/lods/carrier_lod2.glb | 7,831 | 4 | 7 | 4 |
| exports/subsystems/aux_reactor.glb | 776 | 2 | 3 | 4 |
| exports/subsystems/fighter_operations.glb | 364 | 2 | 3 | 4 |
| exports/subsystems/fire_control.glb | 372 | 2 | 3 | 4 |
| exports/subsystems/sensor_array.glb | 1,644 | 2 | 3 | 4 |
| exports/subsystems/shield_generator.glb | 1,336 | 2 | 3 | 4 |
| exports/weapons/heavy_beam.glb | 2,316 | 3 | 5 | 4 |
| exports/weapons/heavy_kinetic.glb | 1,444 | 3 | 3 | 3 |
| exports/weapons/medium_assault.glb | 1,908 | 3 | 3 | 3 |
| exports/weapons/missile_launcher.glb | 1,448 | 3 | 4 | 4 |
| exports/weapons/point_defense.glb | 966 | 3 | 3 | 3 |

Blender's exporter emitted a shared-image sampler warning because the same atlas is referenced by several material nodes. These nodes use identical sampler settings. Visual re-import and Godot rendering were checked rather than treating that warning as a pass/fail result.

Godot logged a Windows root-certificate-store access warning in this restricted environment. No networking was used by the demonstration; imports, rendering and the runtime tests completed. An initial attempt using a console launcher failed because the corresponding engine executable was absent; the complete engine was extracted from the user's existing archive into the carrier's ignored tools directory.

The initial Blender viewport crash and its recovery are documented in README.md. No claim is made that the underlying Blender defect is fixed. The final source was reopened after all batch validation work.

Unverified: automatic LOD transitions, arbitrary extreme weapon articulation, moving-door physics, mobile/Forward+ renderer behavior, older Godot versions and large-fleet frame-time performance. The supplied demo is a functional asset integration example rather than a full game.

Evidence: glb_binary_validation.json, glb_roundtrip.json, hangar_clearance.json, godot_runtime_validation.json, geometry_statistics.json, dimensions.json and renders/roundtrip_hull.png.
