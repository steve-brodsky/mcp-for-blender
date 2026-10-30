# Fleet paint authoring and maintenance

This is the implementation record for humans and future AI sessions. Read it
together with `palette.json`, `assets.json`, and the generated `manifest.json`.

## 1. Inputs, outputs, and ownership

Production GLBs are read from the game prototype, with artwork-folder fallbacks.
`scripts/inventory.py::discover()` defines the discovery roots and precedence:

1. `space-game-prototype/assets/ships`: current accepted main ships.
2. `space-game-prototype/assets/weapons`: attached turret models.
3. Artwork fallbacks for the supply ship, mounted turrets, and flak turret.
4. Explicit `assets.json.extra_sources` entries override a discovered asset ID.

LOD files, assembly/construction demos, and detached debris are not independent
ships. `excluded_prefixes` excludes the carrier and every `carrier_*` module.
Mechs, loose projectiles, and environment assets are outside these discovery
roots. The current inventory is 19 assets, 17 unique albedo atlases, and 25 LODs.
The supply ship and resource collector intentionally share one atlas set.

GLB JSON/binary chunks are decoded without importing or resaving production
models. Embedded albedo images are extracted from `bufferView` ranges; external
image URIs and data URIs are also supported. Source SHA-256 hashes are recorded
and rechecked. All output goes below `artwork/player_colors/`.

`textures/<set>/original.png` is a pixel-identical RGBA archive of source albedo.
It is never a standardized replacement. Source material multipliers and all
non-albedo material properties stay with the original material.

## 2. Paint masks and protected areas

Each unique source atlas has `hull_mask.png` and `stripe_mask.png`. They are
8-bit grayscale linear weights: 0 protects, 255 fully recolors, and gray blends.
Their sum must not exceed 255 at any pixel. Alpha-zero texels are protected.
The packed `paint_mask.png` puts hull in **R**, stripe/detail in **G**, and zero
in B. It is a data texture, not a color texture.

`scripts/masks.py` supplies initial masks from warm ceramic paint and oxide-red
markings. It rejects saturated safety amber, neutral metal, dark machinery, and
blue/cyan lights. Emission texels are excluded when registering a new mask.
This is an initial classification, not a semantic understanding of every surface.
Review and edit the PNG masks for every new ship. Existing reviewed masks take
precedence on rebuild; `generate.py --rebuild-masks` intentionally replaces them.

Do not recolor engines, emission maps, normal/ORM maps, exposed steel, windows,
forcefields, or safety markings merely because they are colorful. Add a new
detail region only when the model actually has paint there. A ship with no stripe
region can legitimately look identical for multiple detail selections.

For solid-color painted materials, put the exact glTF material name in
`assets.json.solid_roles` as `hull` or `stripe`. The current examples are the
mothership's oxide accents/matched hangar and the rack's ceramic plates. Default
all other solids to `preserve`. A safety latch is not a player-color detail.

## 3. Standardizing original paint and composing any pair

The old library multiplied every source by one global brightness reference. That
retained the source ships' slightly different cream finishes. Version 2 estimates
each atlas's reference brightness from confidently masked paint: sample every
fourth texel and take the 65th percentile where mask weight is at least 200.
Sparse detail masks fall back to the configured reference. The exact measured
references are stored per atlas. `normalization_overrides` can set either `hull`
or `detail` reference for a particular texture-set ID when visual review warrants
it. Use a neutral studio view to judge changes; geometry and PBR response can
still make two surfaces appear different under lighting.

All color math in `scripts/paint.py` uses **numeric sRGB values**, before the
normal PBR material converts albedo into linear space. Let `S` be source sRGB,
`H` and `D` the two normalized mask weights, and `Ch`/`Cd` the chosen colors:

```text
L = dot(S.rgb, [0.2126, 0.7152, 0.0722])
painted_hull   = min(1, Ch * L / reference_hull)
painted_detail = min(1, Cd * L / reference_detail)
result.rgb = clamp(S.rgb * (1-H-D) + painted_hull*H + painted_detail*D, 0, 1)
result.a = source.a
```

This replaces paint hue while preserving local brightness variation, panel lines,
and dirt. Python rounds the result to RGBA8. Masks-zero pixels and alpha remain
exactly unchanged. White is off-white so it retains shading headroom; black is
near-black so panel details remain visible. Raw historical originals remain raw;
the `original` preset is normalized ivory + oxide red and writes
`standardized_original.png`.

Solid painted materials use the chosen target color converted once to linear
RGBA with their original alpha. They do not inherit the old material's mismatched
paint hue/brightness. Textured material multipliers, UV transforms, roughness,
metallic, normals, and emission are preserved.

## 4. Definitions and generated interfaces

`palette.json` is the editable source of truth:

- `hull_colors` and `detail_colors`: stable IDs, labels, and sRGB hex values.
- `presets`: named pairs of independent IDs. A preset does not add a new color.
- `normalization`: reference-estimation settings and sparse-mask fallbacks.

`assets.json` contains exclusions, manually registered source paths, solid roles,
and reference overrides. Relative extra-source paths are relative to the repo
root; absolute paths are accepted. The default game-project path currently lives
in `inventory.py`; update it when moving the workspace.

The version-2 manifest includes `hull_colors`, `detail_colors`, `palettes`, the
Cartesian product in `mix_and_match.combinations`, unique `texture_sets`, and
per-asset `materials` and `lods`. Material actions are:

| Action | Replacement | Retained properties |
| --- | --- | --- |
| `preserve` | None | Entire original material |
| `replace_base_color_texture` | Selected albedo PNG/recipe | Original color multiplier, UVs, PBR, alpha settings |
| `replace_base_color_factor` | Selected linear RGBA target | Other original material settings |

`texture_info` records original glTF provenance. Its texture index belongs to
that GLB; it is not a file ID for the exported PNG.

Existing LOD files are geometry-only. `lods.primitive_bindings` maps each LOD mesh
index and primitive/surface index to a source material index. Do not assign the
hull material to every interceptor surface: it has separate protected engine
metals. Single-material ships can inherit the one source material even when
their LOD merges several source meshes. For new multi-material LODs, require an
explicit reliable surface mapping; never guess from unrelated names.

## 5. Export and caching

`generate.py` writes the layered recipes and the 11 preset PNGs. The independent
color product is represented once in the manifest, not as thousands of full-size
images. `bake_pair.py` materializes a selected pair and emits `materials.json`
with source material indices, relative PNG paths, solid targets, and LOD bindings.
`--all` materializes the entire product if a release needs offline compressed
imports for every allowed pair.

The exporter caches by composition version, palette values, source-image hashes,
mask hashes, normalization references, and asset/material definitions. It checks
PNG content hashes before returning `CACHE_HIT`. Files and manifests are replaced
atomically from pending files. Failed partial exports can be rerun. Do not use
cached images from a previous recipe after changing masks or paint definitions.

For the runtime/cache architecture and texture compression tradeoffs, read
`integration/README.md`. Python is an authoring tool; a shipped game must not
depend on the player having Python installed.

## 6. Adding a color

1. Add a stable lowercase ID to one or both independent color dictionaries.
   For example, `teal` can have a muted hull hex and a stronger detail hex.
2. Add an optional `presets.teal` pairing. Existing saved color IDs stay valid.
3. Run the rebuild below. Adding one color to both axes grows an 11×11 set to
   12×12, not 12 old-style paired schemes. No new ship UV masks are required.
4. Inspect the small-silhouette and pairing-matrix sheets, especially white/black,
   same-color, low-contrast, and original-paint cases. Low contrast is allowed.
5. Commit the definitions, regenerated manifest, and intended delivery artifacts;
   keep hardware-specific caches and temporary logs out of a release package.

## 7. Adding or revising a ship

1. Register its current main GLB through discovery or `extra_sources`. Use a
   stable asset ID; keep LODs as siblings named `<stem>_lod1.glb`, etc.
2. Check every material, source albedo, UV set, base-color factor, emission map,
   and solid paint part. Assign solid roles only to painted materials.
3. Generate initial masks. For a new atlas ID, this happens automatically. For
   revised UVs, archive the old atlas directory and regenerate its masks rather
   than reusing them. The generator refuses to reuse an `original.png` whose
   pixels no longer match the source. For a same-UV texture revision, explicitly
   review and migrate the archived image/masks before replacing that directory.
4. Inspect masks over the atlas and render overview, top, underside, and close
   views. Verify mechanical gaps, panel borders, decals, glass, and safety paint.
5. Review the normalized original against other ships. If needed, set an atlas
   reference override and rebuild; do not manually recolor only one preset PNG.
6. Verify LOD material inheritance. Extend `lod_bindings.py` with an explicit
   mapping if the new asset's multi-material LOD layout cannot be inferred safely.
7. Run all validation and browse its full color matrix and original/white-black
   inspection sheet. Recheck source hashes before delivery.

## 8. Rebuild and verify

Requires Python with Pillow/NumPy and Blender 5.1. An optional Godot 4 executable
runs the GPU parity fixture. The provided tools were exercised with Godot 4.7.2
Compatibility on Windows/NVIDIA; full game performance and other renderers are
separate measurements.

```powershell
python artwork/player_colors/scripts/rebuild.py --blender 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' --godot 'C:\path\to\Godot.exe'
```

Use `--force-previews` after changing Blender shader code, lights, or camera setup.
For individual steps, the order is:

```powershell
python artwork/player_colors/scripts/generate.py
python artwork/player_colors/scripts/inventory.py
python artwork/player_colors/scripts/prepare_preview_inputs.py
python artwork/player_colors/scripts/render_all.py --blender $blender
& $blender --factory-startup -b --python artwork/player_colors/scripts/finalize_previews.py
& $blender --factory-startup -b --python artwork/player_colors/scripts/render_lods.py
python artwork/player_colors/scripts/make_sheets.py
python artwork/player_colors/scripts/bake_pair.py --hull white --detail black
python artwork/player_colors/scripts/validate.py --require-previews
python -m unittest discover -s artwork/player_colors/tests -v
```

`render_all.py` resumes only reports matching the manifest hash; a failed Blender
script must not count as a successful preview just because Blender exits 0.
Blender previews use the same formula in `blender_paint.py`; sRGB is explicitly
converted to linear before Principled BSDF. They use 2048 px input proxies and
do not overwrite full-resolution albedos. Every independent pair gets an actual
render; preset thumbnails alias the matching pair, not a screen-space tint.

Validation checks source identity, exact normalized preset pixels, dimensions,
alpha, protected pixels, packed masks, solid values, combination completeness,
LOD UV bindings, preview links, and saved Blender palette switching. The unit
suite tests every pair, normalization, partial masks, solid exports, cache hits,
and invalidation. The Godot fixture compares all 121 GPU results with Python to
within one RGBA8 byte, plus exact protected pixels/alpha and cache behavior.

If only previews were added after successful pixel validation,
`validate_delivery.py` rechecks image hashes and completes the preview checks
without decoding all full-resolution pixels again. Any recipe change requires
full `validate.py` again. Review images manually before declaring delivery done.

An optional real-browser check is in `tests/check_gallery.cjs`. With Playwright
installed, run `node artwork/player_colors/tests/check_gallery.cjs <path-to-playwright-core>`.
It exercises every independent pair, presets, source toggle, scrolling, image
paths, and mobile overflow in Chrome. Screenshots go to `output/playwright/`;
the compact result goes to `browser_validation.json`. The tests derive counts
from the manifest, so adding a ship/color does not require hardcoded count edits.

## 9. Moving or packaging the library

Keep relative texture/proxy paths intact for the offline catalog and Blender
previews. Source model paths in the authoring manifest are absolute and need
updating for a different workspace. Exported `materials.json` has relative PNG
paths and is the integration handoff; it does not copy the source meshes.

The shipping game generally needs only chosen imported exports or the runtime
base/mask inputs, palette IDs, material/LOD bindings, and the baker. It does not
need the entire preview gallery, Python caches, `.godot`, `.userdata`, browser
caches, test outputs, or authoring source archives. Do not delete original
production artwork when cleaning generated artifacts. The carrier is deliberately
absent from the v2 generated library and catalog.
