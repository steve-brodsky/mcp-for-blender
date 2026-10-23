# Asteroid library

28 independently reusable asteroids from the supplied Blender collection. The original 699,860-triangle mesh is archived, welded and separated into its 28 connected rock bodies. Shapes, crater placement and relative sizes are retained. IDs follow the source layout, left to right within each row; the preview rearranges them into seven columns for easier inspection.

## Deliverables

| Folder | Contents |
| --- | --- |
| `blender/asteroids_original.blend` | Untouched original geometry and packed source textures |
| `blender/asteroids_separated.blend` | Welded, separated source collection |
| `blender/asteroids_material_authoring.blend` | Cleaned high meshes and editable rock shaders |
| `blender/asteroids_game_ready.blend` | Final collection with packed baked textures |
| `blender/asteroid_01.blend` through `asteroid_28.blend` | Independent centered asset scenes with packed images |
| `textures/` | Per-asteroid albedo and tangent normal atlases; original maps in `source/` |
| `exports/` | 84 GLBs: main textured mesh plus two geometry-only LOD exports per asteroid |
| `godot/` | Complete standalone preview project and copy of the deployed game assets |
| `renders/` | Actual Godot renderer captures, including backs and all three LODs |
| `reports/` | Source mapping, topology counts, deployment hashes and validation evidence |
| `scripts/` | Reproducible Blender build, packaging and independent validation tools |

The finished library is also installed in `space-game-prototype`:

- `assets/environment/asteroids/`: GLBs, native binary mesh resources, shared materials, mipmapped textures and catalog.
- `scenes/environment/asteroids/asteroid_01.tscn` through `asteroid_28.tscn`: one reusable scene per asteroid.
- `scenes/environment/asteroids/asteroid_gallery.tscn`: optional inspection scene.
- `scripts/environment/asteroid_gallery.gd`: optional gallery controls.

Open the gallery in Godot and press **F6**, or open this folder's `godot/project.godot` and press **F5**. Drag to orbit, scroll to zoom, Home to reset, and 1/2/3 to inspect each LOD. Gallery sizes are normalized; captions show each asset's native diameter. Drag an individual asteroid scene into any level for normal use.

The game main scene now also includes `asteroid_field.tscn`: a saved random assortment of 112 asteroids using every shape, varied 4–42 m diameters, random orientation/location and slow independent spin. `scripts/build_field.gd` builds this field with private seed 20261023 and archives its placements in `reports/field_manifest.json`. Copies of the field scene and runtime spin script are in `godot/`. The main game keeps a clear starting region and camera sightline. Synchronized animatable bodies rotate meshes and collision together on physics ticks. Field validation passes 7,675 checks, and the existing main-scene/camera validation still passes. Native game captures are in `renders/main_field.png` and `renders/field_overview.png`. The individual library scenes remain static reusable assets.

## Meshes, appearance and scale

Mesh cleanup welds split vertices, removes degenerate geometry, corrects normals and applies a mild smoothing pass to reduce reconstruction chatter. The final three sets contain approximately **111,000 / 44,000 / 13,000 triangles**, an **84% reduction** at the main level. All 84 mesh levels are closed, with zero boundary/non-manifold edges and zero degenerate faces. Exact per-asset counts are in `reports/asset_report.json` and the game catalog.

Each asteroid has a fresh non-overlapping UV atlas. Source rock color is gently desaturated and blended with subtle procedural variation; the supplied angular surface markings are retained. Tangent normals bake the cleaned high geometry and restrained fine grain onto the low mesh. Materials are nonmetallic, roughness 0.91, with backface culling and anisotropic mipmapped sampling. Atlases are 1024 square above 10 m diameter and 512 square for smaller rocks. Source color can retain some reconstructed shading; this is a cleaned reconstruction, rather than a new photogrammetry scan or exact recreation of every stone in the reference image. The actual source contains 28 bodies.

The source has no real dimensions. A nominal **40 m** largest diameter establishes scale, preserving relative proportions; the smallest is approximately **5.2 m**. Minor smoothing/decimation differences make the measured largest diameter approximately 40.02 m. Godot uses +Y up. Each reusable scene has identity transforms and a bounding-box-centered pivot, within the small tolerance introduced by reduction. Change scene-root scale to suit your level.

## Runtime behavior

Each scene is a `StaticBody3D` on collision layer/mask 1 with `LOD0`, `LOD1`, `LOD2` and one low-complexity `ConvexPolygonShape3D`. Convex collision intentionally bridges craters and the open regions of crescent/dumbbell shapes. It is an approximate solid gameplay proxy. These are stationary obstacles; attach your own rigid-body or orbital behavior if needed.

LOD switching uses Godot's native visibility ranges with hysteresis and no runtime script. LOD1 starts at `max(35, diameter * 5)` metres; LOD2 starts at `max(100, diameter * 14)`. The last LOD has no far cutoff. All levels share one material and texture pair; repeated instances share mesh resources. The geometry-only LOD GLBs need the main material; use the supplied scene for the complete behavior. Additional automatic mesh LOD generation is disabled in the GLB import settings.

## Validation and rebuilding

Godot 4.7.2 checks **983 assertions with zero failures** in both the standalone project and the actual game. Checks cover all scene resources, dimensions, pivots, triangles, textures, culling, shared materials, visibility ranges, convex collision and 28 physics ray hits. A separate **84-case GPU check** on the game's **Forward+ / D3D12** renderer confirms exactly one intended LOD is drawn at each tested distance for every asteroid. Godot Compatibility rendering is also visually reviewed. The engine emits a Windows root certificate store warning in this restricted environment; imports, rendering and asset checks complete.

Independent binary validation checks all 84 GLBs for finite positions/normals/UVs, unit normals, valid indices, atlas bounds, zero degenerate triangles and embedded PBR textures. Blender validation reopens all 28 independent projects and round-trips every main GLB. This does not establish large-field frame rates, mobile performance or suitability of convex collision for close surface navigation.

Rebuild from the archived separated collection using Blender 5.1:

```text
blender --background blender/asteroids_separated.blend --python scripts/build_assets.py
godot --headless --path godot --editor --import --quit
godot --headless --path godot --script C:/Dev/BlenderMCP/artwork/asteroids/scripts/package_assets.gd
python scripts/package.py
python scripts/validate_glb.py
blender --background --python scripts/validate_blender.py
```

The Blender and packaging scripts declare this workspace's absolute paths. Preserve `meshes/generate_lods=false` in GLB sidecars when rebuilding. Runtime tests and capture helpers use project-relative paths and can run independently in the game:

```text
godot --headless --path . --script res://tests/validate_asteroids.gd
godot --path . --script res://tests/capture_asteroids.gd
godot --path . --script res://tests/render_asteroid_lods.gd
```

Game captures and runtime reports are written to `captures/asteroids/`. Rebuilds never publish or commit files.
