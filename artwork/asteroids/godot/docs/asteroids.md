# Asteroid assets

28 reusable scenes are installed at `scenes/environment/asteroids/asteroid_01.tscn` through `asteroid_28.tscn`. Drag any scene into a level. Each has a centered pivot, rough gray rock material, three automatic distance LODs, and an approximate convex collider on layer/mask 1. No runtime script is required.

Models, native mesh resources, materials, textures and a size/triangle catalog live in `assets/environment/asteroids/`. The largest is nominally 40 m across and the smallest approximately 5.2 m; their original relative sizes are preserved. Change scene-root scale to fit your level. Colliders bridge concavities and crater openings. Individual library scenes are static obstacles; mining, damage and navigation behavior belong to the game.

Open `scenes/environment/asteroids/asteroid_gallery.tscn` and press **F6** to inspect the collection. Drag to orbit, scroll to zoom, Home to reset, and 1/2/3 to preview mesh detail. Gallery display sizes are normalized; labels show actual diameters.

## Main-scene field

Spin speeds mix 67 slow-moving rocks with 45 more visibly tumbling rocks at approximately 4–9 degrees per second (one turn every 40–90 seconds).

`scenes/main.tscn` instances `asteroid_field.tscn`: 112 rocks covering all 28 shapes, with randomized positions, full 3D orientations, diameters between 4 and 42 m, and slow independent spins around varied axes. The layout spans a 480 m horizontal radius and heights from -90 to +90 m. A 95 m clear radius around the mothership and clearance along the initial camera sightline protect the starting view. Conservative envelopes prevent rocks from intersecting as they spin.

The generated layout is saved in the scene and visible/editable in the Godot editor; restarting the game preserves it. `scripts/environment/asteroid_field.gd` updates synchronized `AnimatableBody3D` rotations on physics ticks, keeping each collision shape aligned with its mesh. Positions stay fixed. The field root exposes **Spin Enabled** and **Spin Speed Multiplier**. Each rock stores its spin axis, speed and diameter in metadata. LOD distances follow its placed size; mesh/material resources remain shared.

The reproducible generator is `BlenderMCP/artwork/asteroids/scripts/build_field.gd`. Change `FIELD_SEED` (currently 20261023) or `ROCK_COUNT` there and run it using the game as `--path` and the generator's absolute path as `--script`. This regenerates the saved field, replacing manual field edits. Field validation checks runtime rotation, fixed positions/scales, all shape variants, collision queries and clearances. Run `godot --headless --path . --script res://tests/validate_asteroid_field.gd`; omit `--headless` and append `-- --capture` for the starting view and field overview under `captures/asteroids/`.

There are about 111,000 triangles across all 28 main meshes, with 44,000 and 13,000 at the lower levels. The main level reduces the supplied 700,000-triangle collection by 84%. Each rock has independent 512- or 1024-square albedo/normal maps. The three LODs share a material and texture pair. Native visibility ranges switch at `max(35, diameter*5)` and `max(100, diameter*14)` metres with hysteresis. Import settings disable additional automatic GLB mesh LOD generation.

All editable sources, packed individual Blender files, working textures, scripts, reference image, standalone preview project and another copy of these game assets are in `C:/Dev/BlenderMCP/artwork/asteroids/`. That folder's README contains the build workflow and full validation evidence.

Validated in Godot 4.7.2: 983 runtime assertions, 28 physics ray hits, and 84 rendered LOD checks with no failures. Native rendering checks use Forward+ / D3D12. Run these from the project root:

```text
godot --headless --path . --script res://tests/validate_asteroids.gd
godot --path . --script res://tests/capture_asteroids.gd
godot --path . --script res://tests/render_asteroid_lods.gd
```

The last two require a graphical renderer. Captures and reports go into `captures/asteroids/`. The optional gallery script is independent of reusable asteroid scenes.
