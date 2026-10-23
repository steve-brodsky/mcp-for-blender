# Missiles + Torpedo

Four independently reusable Godot 4 projectile scenes. The current precision revision replaces the reconstruction's crooked noses, irregular shells and blurry paint with concentric machined geometry and authored PBR maps. The ST25 is now an interceptor with a recessed engine. All deliverables are inside this directory. The supplied reference is preserved at `refrences/missles.jpg`.

Open `godot/project.godot` and run the project. Drag to orbit, wheel to zoom, 1-4 to inspect each asset, 0 for the collection, Space for the turntable, F to launch at the range target, R to return to inspection, Escape to quit. Buttons provide the same selection and launch actions.

| Projectile scene in `godot/scenes/` | Length | LOD0 | LOD1 | LOD2 | Albedo |
| --- | ---: | ---: | ---: | ---: | --- |
| `mts8_nuclear_missile.tscn` | 8.00 m | 10,752 | 5,376 | 2,688 | 2048 square |
| `kr45_fusion_torpedo.tscn` | 6.44 m | 7,296 | 3,648 | 1,824 | 2048 square |
| `vn113_tactical_missile.tscn` | 3.72 m | 4,992 | 2,496 | 1,248 | 1024 square |
| `st25_interceptor_missile.tscn` | 1.68 m | 2,624 | 1,312 | 656 | 1024 square |

`st25_interceptor_missile.tscn` is the named entry point for the interceptor. It instances `st25_scatter_missile.tscn`, whose original resource paths remain compatible with earlier integration. The ST25 Blender object and GLB retain the historical filename; the demo and catalog identify it as an interceptor.

The collection preserves relative source scale. A nominal 8 m length for the largest missile establishes metres; the reconstruction does not supply real dimensions. Forward is **-Z**, up is **+Y** in Godot. Each root has identity scale and a bounding-box-centered origin. Blender uses +Y forward and +Z up; GLB performs the conversion.

## Projectile integration

Copy `godot/assets/`, `godot/scenes/` and `godot/scripts/projectile.gd` into equivalent directories in your game. Each missile scene works independently of the demo and catalog. Each contains an `Area3D` root, `Visual/LOD0`, `Visual/LOD1`, `Visual/LOD2`, an approximate capsule collision shape, and `Nose` / `Exhaust` attachment markers. The scene remains stationary with its collider disabled until `launch()` is called. You can replace the root script with your own projectile logic.

```gdscript
var missile = preload("res://scenes/kr45_fusion_torpedo.tscn").instantiate()
get_tree().current_scene.add_child(missile)
missile.global_transform = muzzle.global_transform
missile.speed = 60.0
missile.lifetime = 8.0
missile.impacted.connect(on_missile_impact)
missile.launch(-muzzle.global_basis.z, shooter_body)

func on_missile_impact(collider: Object, point: Vector3, normal: Vector3) -> void:
    # Apply your game's damage and effects here.
    pass
```

The optional script supplies straight flight, configurable speed/lifetime, shooter exclusion, a swept nose/center ray collision query, body overlap detection, an `impacted(collider, point, normal)` signal, and an `expired` signal. Impacts stop motion and free the projectile by default. Set `destroy_on_impact=false` to handle the stopped instance yourself; lifetime expiry always frees it. Collision layer 2 is reserved for projectiles, with mask 1 for world/target bodies. Change masks to match your project. Interceptor target tracking, homing, damage, splash damage, nuclear effects and torpedo behavior belong in your game's scripts; the ST25 revision supplies the interceptor asset and attachment points.

LOD switching is automatic at 30 m / 80 m by default. The three mesh levels share one material and its albedo/ORM maps per missile. LODs use the same axial profiles with fewer circular segments, keeping noses concentric at every distance. Godot's additional mesh LOD generation is disabled in the saved import settings. The capsule is an approximate gameplay proxy, and the swept rays protect the centerline at high speed. Full-volume continuous collision for off-axis grazing hits is not implemented. Damage targets should be physics bodies; Area3D hit detection is not enabled.

The projectile script sets anisotropic mipmapped filtering on the shared materials, and the demo project uses 16x anisotropy. This keeps thin identification bands and panel seams sharp when cylindrical UVs are compressed at oblique viewing angles. Texture imports remain lossless and mipmaps remain enabled for stable distant rendering. When copying the scenes into another project, set its anisotropic filtering level to 16x for the same result. When using a bare GLB without the scene/script, also set its material texture filter to Linear with Mipmaps Anisotropic. Matching grazing-angle captures are in `renders/band_filter_before.png` and `renders/band_filter_after.png`; reproduce them with `godot --path godot --script res://scripts/capture_band_comparison.gd`.

## Assets and cleanup

- `blender/missles_original.blend`: untouched supplied scene.
- `blender/missles_welded.blend`: four separated, welded source meshes.
- `blender/missles_prepared.blend`: aligned, reduced meshes before baking.
- `blender/missles_game_ready.blend`: current edited collection with packed paint.
- `blender/missles_material_authoring.blend`: editable procedural panel, vent, identification-band and PBR masks before baking.
- `blender/previous/missles_before_precision_revision.blend`: previous delivered collection, before this correction.
- `blender/<asset_id>.blend`: independent editable project for each missile.
- `exports/<asset_id>.glb`: standalone main model with embedded texture.
- `godot/assets/`: main exports and two additional LOD exports per missile.
- `textures/`: baked albedos and packed ORM maps per missile, plus the original combined source albedo.
- `renders/godot_*.png`: captures from the actual Godot Compatibility renderer.
- `reports/`: measurements, binary validation, Blender reopen/roundtrip and Godot runtime results.

The current four meshes total 25,664 main-level triangles versus the 699,984-triangle combined source, a reduction of about 96.3%. The circular hulls were rebuilt from editable axial profiles matched to the measured source envelopes, with consistent collars, grooves, smooth centered nose curves and analytic ring normals. All four nose tips sit exactly on the longitudinal axis. The ST25's former tapered tail is now a cylindrical engine housing with a modeled lip, recessed chamber and dark nozzle throat. All four main meshes are closed, with zero boundary and non-manifold edges.

The blurry source paint is replaced with newly authored Blender shader masks baked to cylindrical UV atlases. Clean panels, vent slots, fasteners, coupling bands and nose markings follow straight circumferential and longitudinal coordinates. The palette retains steel, bronze, yellow and red from the reference; the ST25 uses cyan interceptor identification bands. Albedo contains no reconstruction lighting or painted metallic highlights. ORM maps pack white ambient occlusion in red, authored roughness in green and metalness in blue. Shading comes from the renderer and real geometry. Source normal maps are unused. Main GLBs embed both maps, and individual Blender projects pack them. These are modeled interpretations of the reference, with some mechanical detail represented in textures rather than geometry.

## Validation and rebuilding

Tested in Godot **4.7.2-stable**, Compatibility renderer on Windows. `runtime_validation.json` records **188 checks, zero failures**, including all three LODs, albedo and PBR maps, anisotropic material filtering, transforms, markers, the interceptor scene, inert instancing, launch direction, lifetime cleanup, demo selection, four demo-range target impacts and four thin-wall impacts at **3,000 m/s**. `precision_validation.json` measures every saved nose section for concentricity and checks real exhaust opening radii and chamber depths on all four meshes. `glb_validation.json` validates all **12 exports** for finite buffers, normals, UVs, triangle indices, embedded image decoding and zero degenerate triangles. `blender_validation.json` verifies four independent projects reopen and all four main GLBs roundtrip into Blender. The engine prints a Windows certificate-store warning in this environment; rendering and runtime checks pass.

For the current revision, run `precision_revision.py` in Blender on the current collection, then `standalone_blends.py`, then `python scripts/package.py`. The axial profiles, nose shape, shader colors and pattern coordinates are defined in `precision_revision.py`; adjust them there and rebake. `prepare.py`, `bake_export.py` and `refine_export.py` document the earlier reconstruction cleanup and will restore the superseded appearance if reapplied. Scripts use this workspace's absolute path for Blender operations. Texture baking requires Cycles; export uses Blender's bundled glTF exporter. The Python binary validator requires numpy and Pillow.

```text
python scripts/validate_glb.py
godot --headless --path godot --editor --import --quit
godot --headless --path godot --script res://scripts/validate.gd
```

For ordinary modeling edits, export each object alone at location zero as GLB with +Y-up conversion, preserving UVs, normals and material. Refresh the corresponding LOD meshes and atlas if geometry changes substantially. Regenerate the catalog/scenes with `package.py` after updating measured bounds in `reports/asset_report.json`.
