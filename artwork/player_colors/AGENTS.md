# Fleet paint package

Read `README.md`, `PIPELINE.md`, and `integration/README.md` before editing.
This directory is the complete authoring/export package; production game assets
and the live Blender scene are separate sources, not output destinations.

- Color definitions belong in `palette.json`, asset settings in `assets.json`.
  Keep existing color IDs stable. Hull and detail choices are independent.
- `paint.py` is the reference color math. Keep Blender and Godot implementations
  equivalent; run the GPU/Python parity fixture after changing either.
- Preserve reviewed mask PNGs. `--rebuild-masks` explicitly replaces them.
  Verify source image identity before reusing UV masks on a revised model.
- Preserve raw `original.png`; standardized originals use a different filename.
  Never normalize by overwriting the source GLB, UVs, or external artwork.
- Carrier assets stay excluded. Do not add carrier recovery to the rebuild.
- Do not bake during combat or duplicate textures/materials per ship instance.
  Read the documented VRAM-compression tradeoff before promising an FPS benefit.
- Use `rebuild.py` and complete validation. Use `--force-previews` for shader,
  camera, or renderer changes. Check masks and top/underside/close views visually.
- The catalog remains an offline developer preview. A main menu and arbitrary-RGB
  picker are installed in the Godot prototype; see its `docs/fleet_colors.md`.
  `prepare_game_paint.py` refreshes runtime inputs/bindings without changing GLBs.
  Multiplayer remains a separate feature.
