# Fleet paint library — v2

Open **[index.html](index.html)** to choose hull and detail colors independently,
scroll through choices, switch presets, and compare the entire fleet.

The library covers **19 ships/support assets, 11 hull choices × 11 detail choices
= 121 pairings**. White hull / black details and its inverse are included. The
carrier and all carrier modules are excluded. Standardized original paint uses
one ivory/oxide-red palette across the fleet; untouched historical paint remains
available for comparison.

## Ready to use

- `textures/`: **17 unique atlas sets**, each with untouched `original.png`,
  reviewed hull/detail masks, packed RG mask, and **11 full-resolution preset PNGs**.
  `standardized_original.png` is the unified original finish.
- `palette.json`: independent color choices and preset pairs. IDs, not list
  positions or translated labels, identify saved player selections.
- `assets.json`: exclusions, extra source registrations, solid paint roles, and
  optional normalization overrides.
- `manifest.json`: material bindings, normalized recipes, every supported pair,
  source hashes, texture paths, and LOD surface assignments.
- `exports/white__black/`: complete ready-to-use white/black PNGs and material map.
- `exports/blue__orange/`: mixed-color example for the interceptor and torpedo rack.
- `previews/combinations/`: an actual Blender rendering for every asset/pair.
- `previews/matrices/`: every pairing in one labeled matrix per asset.
- `previews/fleets/`, `ships/`, `inspection/`, and `lod_comparison.png`: preset,
  original-paint, surface, and distance-mesh comparisons.
- `previews/blender/`: editable previews. Run their embedded **Choose hull and
  details.py**, choosing `HULL`, `DETAIL`, or a `PRESET`. `SHOW_SOURCE` displays
  the untouched historical material. Preview inputs are limited to 2048 px.

## Export any combination

Run from the repository root with Python, Pillow, and NumPy:

```powershell
python artwork/player_colors/scripts/bake_pair.py --hull white --detail black
python artwork/player_colors/scripts/bake_pair.py --hull blue --detail orange
python artwork/player_colors/scripts/bake_pair.py --hull black --detail white --asset interceptor
python artwork/player_colors/scripts/bake_pair.py --all
```

Each export creates `exports/<hull>__<detail>/materials.json` and its referenced
full-resolution PNGs. Shared source atlases are exported once. Repeating the same
command verifies hashes and reuses the cache. `--all` materializes every pairing;
it is deliberately optional because full-resolution copies take much more space.
The layered recipes already cover every pair, without storing thousands of PNGs.

## Runtime direction

The game prototype now includes a main menu and pre-match picker. Preview colors,
then prepare
only the selected pairs before starting combat. Reuse textures/materials by ship
type and color pair; never create another material or bake a texture per ship
instance or per frame. All LODs inherit the same selected material set.

For a fixed shipping palette, pre-export/imported PNGs support Godot's VRAM
compression and offer the most predictable texture memory. A tested standalone
Godot baker supports dynamically added colors and caches the selected result;
its output is an uncompressed `ImageTexture`, capped at 2048 px by default.
See **[integration/README.md](integration/README.md)** for the loading flow,
compression/memory tradeoffs, cache keys, and tested API. Actual combat FPS has
not been benchmarked. The installed runtime implementation is documented in the
game's `docs/fleet_colors.md`; `prepare_game_paint.py` refreshes its inputs and bindings.

## Extend and rebuild

**[PIPELINE.md](PIPELINE.md)** documents the source selection, masks, normalization,
color math, manifests, exports, previews, validation, and exact steps for adding
ships or colors. **[AGENTS.md](AGENTS.md)** is the entry point for future coding
agents. `scripts/rebuild.py` runs the complete pipeline; use `--force-previews`
after changing rendering code. Tests and validation results are recorded locally.

Paint recoloring preserves alpha, protected pixels, panel shading, and wear.
Normal/ORM/emission maps and safety markings retain their source appearance.
No new stripes are invented on ships without them. Same-color or low-contrast
pairs remain available as player choices. Source files outside this folder are
never overwritten.
