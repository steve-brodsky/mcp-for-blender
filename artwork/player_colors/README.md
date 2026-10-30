# Fleet player colors

Eight coordinated schemes for **30 ships and support assets**: red, blue, green,
yellow, orange, purple, cyan, and pink. Each scheme recolors existing hull paint
and oxide-red markings using a muted hull shade and a stronger matching accent.
Existing panel lines, paint wear, UVs, and texture dimensions are retained.

Open **[index.html](index.html)** in a browser to browse all comparisons.
The package is standalone: no production models, textures, or Godot scripts are replaced.

## Contents

- `textures/`: 18 unique atlas sets, each containing the original albedo, editable
  hull/stripe masks, and eight full-resolution RGBA PNG variants (144 variant PNGs).
- `manifest.json`: source model paths and hashes, per-material texture assignments,
  linear solid-color replacements, shared-atlas references, and 25 LOD mappings.
- `previews/fleets/`: one complete-fleet sheet per palette, plus the original finish.
- `previews/ships/`: original and eight variants for each asset.
- `previews/inspection/`: original/blue overview, top, underside, and blue close views.
- `previews/skirmish_readability.png`: small silhouette comparisons of primary ships.
- `previews/lod_comparison.png`: LOD0 versus the furthest supplied LOD, using the
  same blue materials and camera. Temporary preview LOD copies live below `previews/lods/`.
- `previews/blender/`: editable preview scenes with all eight material sets.
- `validation.json`: machine-checked source integrity, pixels, alpha, material/UV
  bindings, and preview coverage.
- `scripts/`: reproducible extraction, generation, rendering, and validation tools.

## Coverage and paint behavior

Includes the mothership, carrier, both corvettes, four fighter/bomber types, beam
and supply frigates, supply ship/resource collector, construction and supply
drones, cargo pod, torpedo mounting rack, four turret types, and all ten carrier
weapon/system modules. Shared atlases are intentionally generated once and reused.
The resource collector and supply ship share one delivered texture set.

Excludes the mech, loose missiles, assembly demos, and detached destruction debris.
No additional stripes are invented on assets whose source finish has none.
Safety yellow/amber paint, exposed neutral metals, dark mechanisms, windows,
lighting, and separate emission/normal/ORM maps retain their source appearance.
The torpedo rack's safety release latch also stays amber.

Hull/stripe masks are grayscale PNGs: black protects a pixel; white fully
recolors it; gray blends. Warm ceramic paint and oxide-red markings are classified
from each source atlas. The carrier uses explicit regions of its shared atlas,
including its painted armor panels. Masks preserve darker wear and shading through
local brightness variation; they are editable for future art direction.

## Use the Blender previews

Open `previews/blender/<asset>.blend`; the initial scheme is blue. In the Scripting
workspace, choose the embedded text **Switch player color.py**, set `PALETTE` to
one of the eight names or `original`, then Run Script. This changes the existing
material assignments throughout that preview. The same helper is in `scripts/`.

Keep this folder structure intact: variant images are linked by relative paths.
Previews contain neutral studio lights and a camera, not gameplay scenes. Renders
use Blender EEVEE with preview images capped at 2048 pixels; delivered textures
retain their full source resolution. Opening a saved preview reloads its linked
full-resolution PNGs. Fleet sheets frame each model individually, not to scale.

The carrier is recovered from the available packed `carrier_source.blend1` backup.
Its hull and ten module copies are under `sources/carrier/`; these are preview
sources and do not replace a game-ready production export. Recovery details and
the original backup hash are recorded in `carrier_recovery.json`.

## Later Godot integration

1. Find the asset in `manifest.json`. Match its source material **index and name**.
2. For `replace_base_color_texture`, resolve `texture_set` and select the requested
   entry in that set's `variants`. Assign it as the material's albedo texture,
   keeping the original albedo color multiplier, UV channel, texture transform,
   alpha settings, metallic/roughness, normals, emission, and other properties.
3. For `replace_base_color_factor`, use the palette's `variants` RGBA value. These
   values are **linear**, as in glTF; do not treat them as sRGB color-picker bytes.
4. For `preserve`, keep the material unchanged. Apply the same material set to all
   LOD surfaces using `lods.primitive_bindings` (mesh index, surface index, and
   source material index). The existing LOD files omit embedded materials;
   their surfaces inherit the matching LOD0 material. The interceptor retains
   four distinct surfaces, including its protected metal engine parts.
5. Cache a material set per player palette. Players using different colors must
   receive distinct material resources, while ships sharing a palette may reuse
   those resources. Do not tint the already recolored albedo a second time.

`texture_info` records the original glTF texture index/UV metadata for provenance;
its texture index belongs to the source GLB, not to an external replacement file.
PNG albedo textures use sRGB. Palette hex values are sRGB as well.
No team selection, multiplayer logic, or Godot integration is included here.

## Rebuild

Requires ordinary Python with Pillow and NumPy, plus Blender 5.1 for previews.
Commands below run from this repository's root. `inventory.py` contains the
source game-project path; update it if the project has moved.

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe'
& $blender --factory-startup -b --python artwork/player_colors/scripts/recover_carrier.py
python artwork/player_colors/scripts/inventory.py
python artwork/player_colors/scripts/generate.py
python artwork/player_colors/scripts/render_all.py --blender $blender
& $blender --factory-startup -b --python artwork/player_colors/scripts/finalize_previews.py
& $blender --factory-startup -b --python artwork/player_colors/scripts/render_lods.py
python artwork/player_colors/scripts/make_sheets.py
python artwork/player_colors/scripts/validate.py --require-previews
```

After editing masks, use `generate.py --reuse-masks` and `render_all.py --force`,
then repeat finalization, sheet generation, and validation. Regenerating without
`--reuse-masks` intentionally rebuilds the masks from the source artwork.
