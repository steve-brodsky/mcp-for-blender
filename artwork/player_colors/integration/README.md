# Pre-match fleet-color integration

The library and offline catalog are complete authoring assets. No scripts or menu
in the game prototype have been replaced. This directory provides a tested baker
and a concrete integration design for that future work.

## Selection and match loading

Save **hull ID + detail ID**, not a filename or color-list index. The current
palette has 11 choices on each axis. The standardized original is `ivory/oxide`;
the new white scheme is `white/black`. Black hulls and white details can also be
selected independently. Every pairing is allowed, including low-contrast pairs.

1. Populate two scrolling selectors from the manifest color dictionaries. Show
   the selected paint on a representative ship; the offline catalog demonstrates
   this interaction with pre-rendered images for every pairing.
2. While browsing, debounce preview requests and ignore results belonging to an
   older selection. A 256–512 px preview is enough; do not rebake every full-size
   fleet atlas on every scroll event. Prefer the catalog's rendered thumbnails
   or one reusable preview shader for this screen.
3. On confirmation, prepare each unique atlas needed by the selected faction and
   pair. Use a ready-made imported export when available, otherwise bake/cache it
   while the loading screen is visible. Bake sequentially or within a measured
   loading budget, not during combat. Wait for every required atlas before ready.
4. Cache by recipe revision, atlas ID, hull ID, detail ID, and output resolution.
   Share the resulting texture/material set across every identical ship of that
   type/pair. Keep different pairs in separate material resources. Reuse the same
   set for spawned ships, attached turrets/pods, and all LODs.
5. Future multiplayer messages need only palette IDs and the agreed asset/palette
   revision. Validate IDs and ensure clients use the same revision; texture PNGs
   do not need to travel in gameplay messages. Match/ownership logic is separate.

## FPS and memory tradeoff

Recoloring once before combat avoids an extra mask sample/calculation in every
combat fragment shader. It does **not** by itself prove a higher frame rate:
material changes, texture bandwidth, compression, and VRAM pressure matter too.
Godot's guidance emphasizes material/shader reuse. [GPU optimization](https://docs.godotengine.org/en/stable/tutorials/performance/gpu_optimization.html)

For this fixed 121-pair palette, **pre-exporting the release's allowed pairs and
importing them with mipmaps/VRAM compression is the most predictable high-FPS
shipping path**. Load only players' chosen pairs, not the whole product. The
`bake_pair.py --all` command generates those files automatically. Adding a color
does not require hand-authoring ships; rebuild the required combinations.

The smaller layered package plus runtime baking is useful for dynamically added
colors and development. `FleetPaintBaker` produces an **uncompressed RGBA8
ImageTexture**, with mipmaps, cached on disk as PNG. An RGBA8 2048² texture with
full mipmaps occupies about 21.3 MiB; an 8192² texture occupies about 341.3 MiB.
PNG disk size does not indicate GPU memory use. The baker defaults to a 2048 px
maximum dimension; pass 0 for original dimensions, or choose a device-budgeted
limit. Source/mask import size limits should follow the same budget so temporary
bake inputs do not unnecessarily occupy full authoring-resolution VRAM.

Do not rely on runtime `Image.compress()` to recover shipping VRAM compression;
Godot only supports it in editor builds. Use editor-imported exports for that.
[Image compression API](https://docs.godotengine.org/en/stable/classes/class_image.html#class-image-method-compress)

If the target match size cannot fit baked per-player textures in VRAM, benchmark
a shared-base/mask combat shader instead. It adds a sample/calculation but shares
source textures across players. Keep the same recipe and palette IDs so the
choice of rendering backend does not change the authoring pipeline. No in-game
FPS comparison between these approaches has been performed for this project.

## Offline exported material sets

```powershell
python artwork/player_colors/scripts/bake_pair.py --hull blue --detail orange
```

Copy that export directory into the game and import its PNGs using appropriate
3D sRGB/mipmap/VRAM-compression settings. Load selected imported resources with
`load()`/`ResourceLoader`, not raw `Image.load()` from `res://` in an exported
game. The raw-image API is appropriate for external `user://` cache files.
[ImageTexture loading](https://docs.godotengine.org/en/stable/classes/class_imagetexture.html)

Read the export's `materials.json`. For each material index:

- `replace_base_color_texture`: duplicate the original material once per
  asset/pair; set its albedo texture to the exported PNG. Retain the original
  albedo-color multiplier, UV channel/transform, PBR maps, and transparency mode.
- `replace_base_color_factor`: set its albedo color from the exported **linear
  RGBA** value. Do not convert those values from sRGB again.
- `preserve`: reuse the original material.

Apply the same set to the mapped LOD surfaces. The interceptor's four surfaces
include protected engine metals; do not replace all of them with hull paint.
Never multiply a precolored albedo by the selected hull color a second time.

## Runtime baker API

Copy `fleet_paint_baker.gd` and `compose_paint.gdshader` together into the game.
Add one `FleetPaintBaker` node to the menu/loading tree. It must stay in the tree
until outstanding bakes finish. Source inputs are imported **untouched albedo +
packed paint mask**, both lossless for the bake pass. The mask is linear RG data.
The 2D compositor deliberately performs numeric SDR/sRGB math and does not apply
`source_color` conversion to its uniforms. Do not substitute an HDR 2D viewport
without redoing parity tests.

```gdscript
# manifest_text is the exact shipped version-2 manifest text.
# t is the selected texture_sets entry; hull/detail are validated palette IDs.
var source: Texture2D = load(source_resource_path)
var mask: Texture2D = load(mask_resource_path)
var hull_color := Color.html(manifest.hull_colors[hull].srgb)
var detail_color := Color.html(manifest.detail_colors[detail].srgb)
var references := Vector2(t.normalization.hull, t.normalization.detail)
var key := manifest_text.sha256_text() + ":" + atlas_id + ":" + hull + ":" + detail
var texture: Texture2D = await $FleetPaintBaker.bake(
    source, mask, hull_color, detail_color, references, key, true, 2048)
if texture == null:
    # Keep the loading screen active and show a recoverable load error.
    return
# Assign texture to the cached original-material duplicate's albedo_texture.
```

The full signature is:

```text
bake(source, mask, hull_srgb, detail_srgb, normalization,
     recipe_key, disk_cache=true, max_dimension=2048) -> Texture2D
```

The baker incorporates the actual output dimensions into its key, deduplicates
concurrent requests for the same key, and returns the same in-memory texture
resource on a cache hit. Disk files live under `user://fleet_paint_cache/`.
`clear_memory_cache()` releases the baker's references; material users still keep
their textures alive. It does not delete disk files. Implement a disk cache quota
and stale-revision cleanup when wiring the production loading screen.

The compositor only changes albedo. Copy all other original material settings.
Solid paint roles are handled from palette targets/manifest material metadata;
they need no render pass. This keeps the baker independent from ship scene trees.

## Tested behavior and reproduction

The fixture uses an 8×8 synthetic albedo with separate hull/detail/protected
regions and partial alpha. It renders all 121 pairs in actual Godot Compatibility,
checks memory/disk cache behavior and separate output-resolution keys, and saves
results. Python tests compare every result to the reference formula within one
RGBA8 byte; protected pixels and alpha must be exact. Tests also cover all-pair
offline exports, solid targets, partial masks, normalization, and invalidation.

On Windows, start the fixture with a hidden offscreen window. Ordinary headless
Godot has no active graphics viewport for this render test. For example:

```powershell
$env:APPDATA = 'C:\Dev\BlenderMCP\artwork\player_colors\integration\.userdata'
Start-Process -FilePath $godot -WindowStyle Hidden -Wait -ArgumentList '--path C:/Dev/BlenderMCP/artwork/player_colors/integration --script res://test_project/test_baker.gd --rendering-method gl_compatibility --audio-driver Dummy --resolution 8x8 --position -32000,-32000 --quit-after 600 --log-file C:/Dev/BlenderMCP/artwork/player_colors/godot_gpu_test.log'
python -m unittest discover -s artwork/player_colors/tests -v
```

`rebuild.py --godot <exe>` performs the same test. Require the
`GODOT_BAKER_COMPLETE` marker as well as a successful process exit. The supplied
test project and outputs are validation artifacts, not game content. Other
renderers/platforms and an exported-game build still require target testing.
