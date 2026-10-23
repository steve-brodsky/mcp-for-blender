# Mothership / Ion Bay

Refinement of the textured reconstruction that was open in Blender. The original silhouette, beige/red livery and machinery are retained. The unwanted added armor plates, side band and service housings have been removed. The original hull around the completed forcefield hangar has been restored.

The top, port and starboard albedo artwork has now been repainted with defined paint edges, fine panel seams, vents and machinery detail, projected back onto the hull and baked to an **8192 × 8192 base-color atlas**. A view-packed UV layout and continuous blends prevent hard projection seams; source UVs are retained in the fallback atlas page. The artwork is a repaint rather than a sharpening filter. A clean **2048 × 2048 ORM map** replaces the earlier material response. The old reconstruction normal map has been removed to avoid its noisy rippled appearance. Repaint source artwork and exact built-in image-generation prompts are documented in `textures/repaint/README.md`.

Both hull slots now contain **transparent animated blue forcefield hangars**. Thin hull-textured collars, structural rims and subdivided membranes follow each side's measured hull contour. The flat projecting surround has been removed. The opposite slot is higher on this asymmetric reconstruction, so the port bay is fitted independently rather than mirrored into the wrong place. There are no sliding doors.

![Godot demo](renders/godot_demo.png)

Open `godot/project.godot` in Godot 4.7 and press **F6** on `scenes/demo.tscn`, or **F5** to run the project. Tested with the existing local **Godot 4.7.2 stable**, Compatibility renderer, on an RTX 3080.

| File | Purpose |
| --- | --- |
| `blender/rough_original.blend` | Untouched original model saved before editing |
| `blender/mothership_refined.blend` | Finished Blender model with packed textures |
| `godot/assets/mothership.glb` | Portable mesh with embedded PBR textures and static blue field material |
| `godot/scenes/mothership.tscn` | Reusable game asset with animated field, bay lighting, markers and collision proxies |
| `godot/scenes/demo.tscn` | Space presentation with orbit/zoom and inspection views |
| `godot/assets/forcefield.gdshader` | Animated grid, traveling scan lines, glowing perimeter and adjustable energy |
| `renders/godot_hangar.png`, `renders/godot_hangar_port.png` | Actual Godot captures of both bays |
| `renders/godot_hangar_starboard_oblique.png`, `renders/godot_hangar_port_oblique.png` | Grazing-angle fit checks in Godot |
| `glb_validation.json`, `runtime_validation.json`, `hangar_fit_validation.json` | Binary, engine and measured hull-contact validation |

The complete portable project is also provided as `mothership_godot.zip`. It excludes editor caches and the engine executable.

| Control | Action |
| --- | --- |
| Left drag / wheel | Orbit / zoom |
| 1 | Ship overview |
| 2 or H | Starboard hangar inspection |
| 3 | Aft view |
| 4 | Port hangar inspection |
| F | Enable/disable both blue forcefields |
| Space | Automatic turntable |
| Escape | Close demo |

To use the asset in another project, copy the contents of `godot/assets/`, `godot/scripts/mothership.gd`, and `godot/scenes/mothership.tscn` into matching `res://` directories. Instance the wrapper scene. The raw GLB does not contain the Godot shader animation; use the wrapper for that effect. In code, call `ship.set_forcefield_enabled(false)` or adjust `ship.field_energy` between 0 and 3.

The revised asset contains **90,304 triangles**, **7 meshes**, and **19 material surfaces**, compared with 699,864 source triangles. Godot import settings enable generated mesh LODs and shadow meshes. The GLB is about 44.6 MB and embeds the repainted base color/ORM maps plus the two existing side-art textures used on the fitted collars. Interiors share their PBR materials. Texture filtering uses mipmaps and anisotropic sampling.

Coordinates are **-Z forward, +X starboard, +Y up**, at unit root scale. Bounds are approximately **101.33 m long × 46.15 m wide × 30.06 m high**. Each forcefield aperture is 10.8 m wide × 4.22 m high, with about 11.8 m of modeled bay depth. `HangarSpawn`, `HangarExit`, and `HangarApproach` are Godot Marker3D nodes facing starboard. `PortHangarSpawn`, `PortHangarExit`, and `PortHangarApproach` face port. `ship.hangar_spawn_transform(true)` returns the port spawn transform; the default remains starboard.

Both interiors include deck expansion joints, centerline approach markings, threshold hazard stripes, structural ribs, blue guide strips, ceiling rails, equipment lockers and service lamps. Each blue membrane is a separate curved mesh; the shared additive transparent shader preserves the view into each bay. The fields have no collider so friendly ships can pass through.

Binary validation checks finite positions and UVs, unit normals, index ranges, embedded maps, forcefield nodes, and zero degenerate triangles. Runtime validation checks both curved membranes and their animated material, scene dimensions, geometry budget, field controls and six navigation markers. A 1.6 m diameter physics probe sweeps 32 positions along each launch corridor. Independent Blender measurements check 192 collar contact positions per side and 15 hull-clearance rays through each aperture. Outer contact edges remain within 3.3 cm of the original surface, with buried skirts closing grazing-angle gaps. Actual GPU captures verify both sides visually.

```powershell
python scripts/validate_glb.py
godot --headless --path godot --editor --import --quit
godot --headless --path godot --script res://scripts/validate.gd
godot --path godot -- --capture
godot --path godot -- --capture --hangar
godot --path godot -- --capture --port-hangar
godot --path godot -- --capture --hangar --oblique
godot --path godot -- --capture --port-hangar --oblique
```

Collision uses simple static boxes and deliberately leaves the launch corridor open. It is approximate, not a per-triangle hull or a full fighter-clearance certification. Reconstruction geometry irregularities remain; this revision repaints the surfaces and removes the unwanted geometry overlays. Areas hidden from all three repaint cameras retain the original color as a fallback. UVs are intended for texture projection rather than unique baked lightmaps. The asset has no combat, fighter AI, damage states or articulated weapons. The model refinement scripts are stateful construction records; edit the finished Blender file for subsequent changes. `finalize_export.py` can export that finished scene again.

The supplied references were found in `../carrier/mothership/references/`; they were inspected and preserved. The existing carrier project was not modified. Godot printed a Windows certificate-store warning under the restricted execution account; local import, rendering and runtime validation completed successfully.
