# Mothership / Ion Bay

## Hangar interior repair

Legacy textured hull surfaces were intersecting the manufactured floor, ceiling,
and rear lockers inside both hangars. A local curved recess now clears those
surfaces while retaining the original bay assembly, exterior finish, and native
mirror. All 29,722 protected source-half exterior faces retain their exact
geometry and UVs across every layer. The 8K texture bytes are unchanged.

The Blender forcefield now uses blended transparency with reduced opacity and
emission, avoiding the noisy dithered overlay. Both bays have been reviewed with
the field on and off in Blender and Godot. No viewport offscreen capture is
required: Blender 5.1 hit an EEVEE shadow-renderer crash during that capture path;
the review uses separate CPU background renders instead.

Source: `blender/mothership_refined.blend`. Pre-repair recovered-session backup:
`blender/mothership_before_hangar_display_repair.blend`. The repaired export is
`godot/assets/mothership.glb`, also copied into the game prototype. The assembly
now contains 94,316 triangles and 26 material surfaces. Repair details and 30
visual-mesh clearance probes are in `hangar_interior_validation.json`.
The reproducible repair and export tools are in `tools/`.

Open `blender/mothership_refined.blend` for the editable source, or
`godot/project.godot` for the portable Godot demo.

![Current detailed finish](renders/godot_detailed_overview.png)

## Current finish

The hull remains symmetric about X=0. Its original detailed top artwork has been
reprojected onto the current smoothed geometry, removing stretching from UVs that
were created before the geometric fairing. The red markings and plating lines
retain their original design, mechanical artwork and weathering. The two forward
cannons now use ivory housings and dark steel barrels.

This material is baked natively in Blender into
`textures/hull_detailed_finish_8k.png` at 8192 x 8192 pixels. The game material uses
`UV_SURFACE_FINISH`, a fresh UV layout on the source half, mirrored to the other
side. Both sides now use reprojected canonical starboard artwork. The underside uses a
registered repaint matched to the accepted top, with crisp panels and red markings. Hull/hangar vertex
positions are identical to the prior accepted symmetric geometry.

The source contains `Hull_Detailed_Reprojection` (retained as an editable source
material), the original `UV_REPAINT_ATLAS`, and the final `Hull_Detailed_Final`.
The original atlas and repaint sources remain under `textures/`.
A backup of the previous accepted finish is
`blender/mothership_before_straight_finish.blend`.

## Files and scale

| File | Purpose |
| --- | --- |
| `blender/mothership_refined.blend` | Current packed source with hull Mirror modifier |
| `godot/assets/mothership.glb` | Current export with embedded baked albedo |
| `godot/scenes/mothership.tscn` | Animated forcefields, bay lighting, collision and markers |
| `finish_validation.json` | Bake provenance, texture SHA-256 and current review results |
| `glb_validation.json`, `runtime_validation.json` | Export and runtime checks |
| `renders/godot_detailed_front_close.png` | Forward cannon review in the actual prototype |
| `renders/uv_inspection_underside.png` | Underside under bright neutral inspection lighting |

Godot coordinates are -Z forward, +X starboard and +Y up, at unit scale.
Bounds: approximately 98.14 m long x 49.10 m wide x 29.89 m high.
The assembly contains 94,316 triangles, ten meshes, and 26 material surfaces.
The GLB is approximately 49.2 MB with one embedded 8K basecolor image.
The geometry remains a refined reconstruction; it is not a new hard-surface model.

Both hangars are mirrored copies of the fitted starboard bay, with no doors.
Spawn/exit/approach markers are at (+/-14,1,6), (+/-26,1,6) and (+/-45,1,6).
The membranes have no collider. The hull uses 36 mirrored convex sections fitted
to the geometry, including separate hangar floors and roofs that leave the bays
open. `scripts/build_collision_hulls.py` rebuilds the hull report and both scene
wrappers from the imported game GLB. The wrapper supports
`set_forcefield_enabled(bool)` and `hangar_spawn_transform(port)`.

## Editing and validation

For finish edits in Blender, run `scripts/reproject_side_bottom_finish.py`,
`scripts/bake_detailed_finish.py`, then `scripts/export_symmetry_revision.py`.
The first script extends the frozen accepted top with side and bottom projections, the second bakes to the
fresh UVs, and the last exports and saves the source. Original UVs must be retained
for the side/underside fallback in the editable material. The one-time symmetry
script is intended only for its historical input backup.

```text
python scripts/validate_glb.py
godot --headless --path godot --editor --import --quit
godot --headless --path godot --script res://scripts/validate.gd
```

The exported albedo SHA-256 must match `finish_validation.json`. Binary checks
verify symmetry, finite data, unit normals and zero degenerate triangles. All 117
asset-demo runtime checks passed. Prototype scene/camera checks also passed. Eight
actual Godot Forward+ / D3D12 views, including a front close-up, were reviewed and
repeated with bright inspection lighting. The 1.6 m diameter corridor probes pass
32 sample positions per side.

## Demo controls

Left drag orbits; the wheel zooms. 1 selects overview, 2/H starboard bay, 3 aft,
4 port bay, F toggles fields, Space previews cannon recoil, T toggles turntable, and Escape exits.
The prototype uses right/middle drag and F/Home to reset its own orbit camera.

## Side and underside extension

The top and cannon colors are protected by sampling the frozen
`textures/hull_top_accepted_8k.png`. All 4,288 sampled protected top points have
zero pixel difference after baking. Geometry, normals, UVs and triangle indices
are identical to the accepted top revision. The prior source is backed up at
`blender/mothership_before_side_bottom_finish.blend`.

The side projection source is `textures/repaint/starboard_repaint.png`, applied to
both mirrored sides. The underside projection source is
`textures/repaint/bottom_repaint.png` (1774 x 887), produced with built-in imagegen
from a registered orthographic underside guide and the approved top style.
Exact prompt and source notes: `textures/repaint/side_bottom_finish.md`.
The combined finish is still baked natively to the existing 8192 x 8192 game atlas.

For repeatable asset captures independent of the current scene orientation, append
`-- --canonical` to the visual review command. This affects only the running
review process and does not save or change the main scene.

## Recoiling forward barrels

The two forward cannon housings now contain short hollow tapered steel inserts,
exported separately as `Cannon_Barrel_Starboard` and `Cannon_Barrel_Port`. Their
gunmetal artwork comes from the existing detailed hull atlas. No hull vertices or
texture pixels changed. `blender/mothership_before_recoil_barrels.blend` preserves
the accepted hull; `scripts/add_recoil_barrels.py` rebuilds only these inserts.
After rebuilding, run `scripts/export_symmetry_revision.py` to export and save.

The reusable Godot ship supports `fire_cannon(port=false)` and
`fire_forward_cannons()`. Each barrel cycles independently: a 0.55 m aft kick over
0.07 seconds, then a 0.38 second return. Exported settings control these values.
Accepted shots emit `cannon_fired(port, muzzle: Transform3D)` with the world muzzle
transform. Disable `cannon_preview_input` when connecting gameplay input. This
includes recoil only; projectile simulation and damage remain future gameplay.
Run `godot --headless --path godot --script res://scripts/validate_cannons.gd`
for the import/recoil integration check.

## Inner cannon panel repair

The inward walls and small shelves next to the forward cannons use a local,
smoothly blended ivory plating repair from the approved texture. Hull vertices
and UVs remain identical to the pre-repair source. Of 4,288 historical top samples,
4,287 remain identical; one falls on the repaired upward-facing cannon shelf.
The editable reference and source are preserved as
`textures/hull_before_inner_panel_8k.png` and
`blender/mothership_before_inner_panel_repair.blend`.

Run `scripts/repair_inner_cannon_panels.py`, `scripts/bake_detailed_finish.py`,
then `scripts/export_symmetry_revision.py` to reproduce this local finish.
The first script uses the frozen complete finish as its base, so earlier top,
side and underside projections do not need to be rerun for this repair.
See `inner_panel_validation.json` and `renders/godot_inner_panel_port.png`.

## Engine color cleanup

The original engine geometry is retained. Orange artwork in the aft engine well
and cowls is converted to charcoal with a native color mask, preserving the
original dark steel texture and markings. No engine replacement meshes are used.
Geometry and UVs match `blender/mothership_before_engine_desaturation.blend`.
The frozen reference is `textures/hull_before_engine_desaturation_8k.png`.

To reproduce, run `scripts/desaturate_engine_orange.py`, then
`scripts/bake_detailed_finish.py` and `scripts/export_symmetry_revision.py`.
See `engine_color_validation.json` and `renders/godot_engines_charcoal.png`.

## Local nozzle bridge removal

Only the small contacts between each upper/lower nozzle pair are cut away. The
native mirrored hull remains; no replacement engines are added. All 29,998
untouched source-half faces retain identical UVs, and the hull texture bytes are
unchanged. Newly exposed interior cut faces use matching dark steel.
`scripts/remove_nozzle_bridges.py` applies the local cut before the usual export.
The pre-cut source is `blender/mothership_before_nozzle_bridge_cut.blend`.
See `nozzle_bridge_validation.json` and `renders/godot_nozzle_bridges_removed.png`.

## Aft dorsal fitting removal

The small raised blue/white fitting is removed and its socket is filled. A thin
sloped steel deck plate reuses existing mechanical artwork, with no texture-image
changes. `scripts/remove_dorsal_fitting.py` reproduces the edit from
`blender/mothership_before_dorsal_fitting_removal.blend`. See
`dorsal_fitting_validation.json` and `renders/godot_dorsal_fitting_removed.png`.

## Side window spill correction

Blue projected onto the cladding above the side windows is neutralized to dark
steel using native position/color masks. All 27 sampled blue window points remain
pixel-identical; none of the 10 sampled upper spill points remain blue. Geometry,
UVs and material assignments are unchanged. The bake keeps separate engine cut
materials on the original mesh and bakes only the textured hull slot.

The reference is `textures/hull_before_window_spill_fix_8k.png`; the editable
backup is `blender/mothership_before_window_spill_fix.blend`. Reproduce with
`scripts/clip_window_spill.py`, then bake and export. See
`window_spill_validation.json`, `renders/godot_windows_starboard.png` and
`renders/godot_windows_port.png`.
