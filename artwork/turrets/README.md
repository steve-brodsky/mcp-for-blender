# Turret armory

Nine independent Godot 4.7 weapon assets, based on the supplied generated model and reference sheet.

Open `blender/turrets_refined.blend` for the full edited collection. Each named weapon also has its own packed `.blend` in that directory. The untouched generated source is `blender/turrets_original.blend`.

Import `godot/project.godot` and run the project. Keys 1–9 select weapons, 0 shows the collection, drag orbits, wheel zooms, Space toggles the turntable, and A/D traverses the selected turret. The collection normalizes display sizes; individual asset scenes keep their relative authored scale.

Reusable scenes are in `godot/scenes/`, with standalone embedded-texture GLBs in `godot/assets/`. Forward is -Z, up is +Y, and origins sit at the mounting base. Each scene includes a yaw pivot, muzzle markers and an approximate body hitbox on collision layer 2. Long barrels are excluded from the hitbox. `muzzle_transforms()` returns firing transforms; `aim_yaw_at(world_target)` controls horizontal aiming. Elevation and firing mechanics are not rigged.

Meshes were welded, smoothed, reduced and triangulated. Each weapon has its own repainted 2K albedo with sharp panel seams, vents and metal wear. Main armor uses restrained constant PBR roughness and metalness; editable experimental ORM maps are retained under `textures/`. Repaints used the built-in image-generation tool; complete prompts are in `textures/repaint/PROMPTS.md`.

Alignment revision: individual longitudinal axes were corrected, curved source barrel roots were removed back to their receivers, 13 full exposed barrels were rebuilt with parallel axes, level paired centerlines and recessed bores. The siege cannon has straight machined rails. Original silhouette irregularities remain in some generated body armor.

Validation: `glb_validation.json` checks every exported mesh and texture; `runtime_validation.json` records 200 successful Godot 4.7.2 checks; `barrel_centerline_validation.json` measures all 13 tube centerlines. `asset_report.json` lists current dimensions, triangles and muzzle coordinates. GPU captures are in `renders/`.

The Windows engine prints a certificate-store warning in this environment; imports, runtime checks and rendering completed successfully.


