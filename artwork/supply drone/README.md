# Supply drone

The supplied supply drone has been aligned, welded, reduced, flattened, mirrored and given a cleaned paint finish for Godot. It is the tug that collects and carries the supply ship's cargo pods. Its nose coupler is magnetic: the drone flies up to either end of a pod and the coupler pulls the pod on and holds it. The drone has no moving parts and no animation.

Open `godot/project.godot` in Godot 4 and run the preview. Drag to orbit and scroll to zoom. Press D to fly to the floating pod and dock it, R to release it, C for a carry demo, 1/2/3 to inspect a mesh level and 0 for automatic switching.

![Godot capture](renders/godot_close.png)

![Docked cargo pod](renders/godot_docked.png)

| File | Purpose |
| --- | --- |
| `godot/assets/supply_drone.glb` | Drone with embedded paint and emission textures |
| `godot/assets/supply_drone_lod1.glb`, `supply_drone_lod2.glb` | Distance meshes (geometry and material slot only) |
| `godot/scenes/supply_drone.tscn` | CharacterBody3D with LODs, five convex collision hulls, `PodMount` and markers |
| `godot/scripts/supply_drone.gd` | `SupplyDrone` API: dock, release, approach and carry poses, signals |
| `godot/assets/cargo_pod*.glb`, `scenes/cargo_pod.tscn`, `scripts/cargo_pod.gd` | Unchanged copies from `supply_ship/`, used only by the preview and validation |
| `blender/supply_drone_game_ready.blend` | Current editable game mesh with packed textures |
| `blender/supply_drone_original.blend` | Untouched supplied scene |
| `blender/supply_drone_clean_high.blend` | Aligned, welded, scaled full-resolution drone |
| `blender/supply_drone_prepared.blend`, `_uv_baked.blend` | Reduced and flattened port half; then unwrapped and baked |
| `textures/supply_drone_basecolor_4k.png`, `_emission_2k.png` | Current albedo and emission atlases |
| `textures/source/` | The three original reconstruction maps (albedo, ORM, normal) |
| `textures/work/` | Baked source albedo, island and hit masks, position and normal maps, texel and face class maps |
| `renders/godot_*.png` | Captures from the actual Godot renderer, including a docked pod and an approach |
| `reports/` | Alignment, geometry, texture, docking, GLB and Godot validation |

The drone points along **-Z** (the coupler), with **+Y up** in Godot. Its origin is on the symmetry plane at the bounding-box centre. Port is -X. A nominal **12.5 m length** was chosen because the source has no physical dimensions. That puts it in the 12-16 m fighter range, and it makes the coupler match the cargo pod's end caps: the coupler frame is about 6 m across and its centre plate about 2 m, against a 6 x 5.4 m end cap with a 2.2 m docking boss. The finished drone measures **12.4 m long x 11.2 m wide x 6.1 m tall**. Scale the scene root to suit your game, and scale the pods by the same amount.

| Detail level | Triangles | Default distance |
| --- | ---: | --- |
| LOD0 | 92,628 | Under 40 m |
| LOD1 | 37,050 | 40-100 m |
| LOD2 | 13,892 | Over 100 m |

The source was a single 699,802-triangle mesh. The game mesh is 87% smaller and uses one PBR material. Roughness is 0.62, metallic 0.15 and emission strength 2, as on the beam frigate and supply ship. The main GLB is about 17.7 MB, mostly the embedded 4K albedo. Godot's automatic mesh LOD generation is disabled in the saved import settings because explicit distance meshes are included.

## Integration

Copy `godot/assets/supply_drone*.glb`, `godot/scenes/supply_drone.tscn` and `godot/scripts/supply_drone.gd` into the matching `res://` folders and instance `supply_drone.tscn`. Use the supply ship's own pod files, not the copies here. The root has no movement or AI; attach your logic there.

```gdscript
drone.get_docking_transform(pod)        # where the drone must be to hold the pod where it floats
drone.can_dock(pod); drone.dock_pod(pod) # nearest pod end, or pass &"aft" / &"fore"
drone.release_pod()                     # lets go in place; returns the pod
drone.get_carry_transform(target)       # where the drone must be so its pod sits on `target`
drone.has_pod(); drone.get_pod(); drone.is_docking(); drone.get_docked_end()
signal pod_docked(pod)                  # the magnet has seated the pod
signal pod_released(pod)                # pod re-parented to the drone's parent
```

**Docking.** `dock_pod` accepts a pod whose end is within 8 m of `PodDock`. The magnet then eases the pod onto the coupler over 1 s, so the approach can be approximate. The pod becomes a child of `PodMount` and moves with the drone. The docked pod has a collision exception with its drone, and either pod end can be docked.

**With the supply ship.**

1. When `ship.pod_released(side, pod)` fires, fly the drone to `drone.get_docking_transform(pod)` and call `drone.dock_pod(pod)`.
2. To return the pod, fly the drone to `drone.get_carry_transform(ship.get_handoff_transform(side))`.
3. Call `drone.release_pod()`, then `ship.load_pod(side, pod)`.

**Docking standoff.** The pod's end cap is wider than the gap between the drone's corner thruster pods, which stand 1.1-1.6 m proud of the coupler. The boss therefore cannot touch the plate, and the magnet holds the pod with its boss tip 0.85 m ahead of the plate, on `PodDock`.

- The real meshes would already clear at 0.51 m (aft end) and 0.42 m (fore end), measured against `cargo_pod.glb` (`reports/docking.json`).
- The extra distance lets the pod's single convex collision hull clear the drone's hulls too.

Markers:

- `PodDock`: the docked boss tip, facing forward.
- `Coupler`: the centre of the coupler plate.
- `ThrusterFrontPort`, `ThrusterFrontStarboard`: the outer ends of the front corner pods, facing forward.
- `ThrusterRearPort`, `ThrusterRearStarboard`: the outer ends of the rear corner pods, facing aft.

The thruster markers are approximate VFX points rather than modelled nozzles.

The five collision hulls are the core body between the corner pods and the four corner pods. The core hull stops at the coupler frame, so a docked boss is not swallowed. These are coarse gameplay proxies, not exact projectile meshes.

## Mesh cleanup

- **Alignment.** Principal axes set up and forward; forward is the coupler, which matches the pod end caps. Yaw, roll and the centreline offset were refined by minimising mirrored surface distance. The coupler face was then levelled to exactly vertical (0.75 degrees). See `reports/source_alignment.json`.
- **Weld.** The source's split UV-seam vertices were welded into one closed shell (there were no stray pieces), and its custom normals were cleared.
- **Reduction, smoothing and panel flattening.** These are the beam frigate methods, applied to the port half: half-only reduction, crease-locked non-shrinking smoothing, and plate regions pulled onto fitted planes. The plate thresholds and the 5 cm movement cap are scaled down for the smaller drone. 376 plates cover 48% of the surface (`reports/mesh_reduction.json`). Every game vertex lies within 6 cm of the source surface (median 3.5 mm).
- **Symmetry.** Mirrored across X=0, with zero reflected position and UV error in every GLB.
- **Shading.** Edges sharper than 40 degrees are marked sharp.

The mesh and both LODs have zero boundary edges and zero edges shared by more than two faces. Some soft reconstruction forms remain, mostly in the machinery between the corner pods; they were kept as part of the supplied silhouette. The underside is mostly orange, as the source painted it.

## Texture cleanup

The port half has a new 4096 `GameUV` atlas, using 45% of the sheet. The source albedo was baked onto it selected-to-active, and both halves share the atlas.

`scripts/clean_texture.py` uses the beam frigate and supply ship method with a drone palette:

1. **Classification.** Five paints: graphite, gunmetal, ivory armor, red stripe and orange. Unlike on the supply ship, orange is a full base paint here: frames, brackets and most of the underside.
2. **Plate majority.** `scripts/classify_faces.py` gives every face and every flat plate one majority paint. This removes the orange that the reconstruction smeared into the dark machinery. Red stripes stay texel-accurate, but only around faces voted red, because the pale clamp tabs on the coupler are faintly pink in the source.
3. **Detail-preserving cleanup.**
   - Painted surfaces (armor, stripe and orange): blotches (2.5-24 texels) are damped to 45%, grime on armor is lifted 40%, and fine detail is kept at 100%.
   - Machinery: blotches are damped to 25% and fine detail kept at 60%.
   - Each paint is pulled towards its palette colour. The source's dark maroon stripe is lifted most, towards the reference red.
4. **Lights.** The source albedo has no light texels, because the reconstruction turned every glow into plain orange. The lights are placed from baked position and normal maps where the reference shows them:
   - a thin line along the ring channel around the coupler;
   - the four corner-pod windows;
   - the two slots beside the coupler frame.

   See `reports/texture_cleanup.json` for the regions.

The old normal and ORM maps are archived in `textures/source/` and are not used, because they amplify reconstruction noise.

## Validation

- **Blender:** the half and the mirrored mesh are closed, and mirror error is zero (`reports/mesh_reduction.json`, `symmetry.json`). Both pod ends were overlap-tested against the real cargo pod mesh (`reports/docking.json`).
- **GLB buffers:** `scripts/check_glb.py` confirms the following for all three drone GLBs (`reports/glb_validation.json`):
  - finite positions, normals and UVs, and valid indices;
  - exact mirror symmetry including UVs;
  - embedded 4K/2K textures.
- **Godot 4.7.2 Compatibility:** `godot/scripts/validate.gd` runs 31 checks with 0 failures (`reports/godot_validation.json`). It covers:
  - the LODs and the shared material;
  - size and orientation, and all markers;
  - five convex hulls, with ray hits across the drone;
  - refusal of an out-of-range pod;
  - real magnetic docks of both pod ends, seated to 0.0 mm with the boss tip on `PodDock`;
  - the docked pod's hull clearing the drone's hulls;
  - the pod following the drone, and its release;
  - `get_carry_transform` placing a pod exactly on a target.
- **Captures:** close, front, side, rear, top and underside views, a docked pod and an approach are in `renders/`.

## Rebuilding

Blender scripts declare the workspace path at their start. Run them with the stated file open; Python-side scripts need numpy, opencv-python, scipy and Pillow.

1. `supply_drone_original.blend` → `scripts/align_source.py` → `scripts/prepare_asset.py`.
2. `scripts/reduce_meshes.py` → `scripts/bake_source.py`.
3. `python scripts/clean_texture.py labels`, then `scripts/classify_faces.py` in Blender, then `python scripts/clean_texture.py paint`.
4. Reopen `supply_drone_uv_baked.blend` → `scripts/finalize_asset.py` → `scripts/export_asset.py`. The export reads `supply_ship/godot/assets/cargo_pod.glb` to measure the docking pose.
5. `python scripts/package_asset.py` → `python scripts/check_glb.py`.
6. `godot --headless --path godot --editor --import --quit`, then `godot --headless --path godot --script res://scripts/validate.gd`. Captures: `godot --path godot -- --capture=close` (or `front`, `side`, `rear`, `top`, `underside`, `docked`, `approach`).

For texture-only changes, repeat steps 3-6. When running Godot under a restricted account, set `APPDATA` to `godot/.local_appdata/`.
