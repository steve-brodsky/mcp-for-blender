# Supply frigate assembly: building the supply frigate from hangar-sized kits

The supply frigate is cut into a **61-piece construction kit**, the same way as the beam frigate in [`../ship assembly/`](../ship%20assembly/README.md) and the supply ship in [`../supply ship assembly/`](../supply%20ship%20assembly/README.md):

- a **yellow keel truss** in 4 segments down the centreline, laid first;
- the centre engine block;
- 14 rings of four quarters each, which close over the keel.

The build works outward from the keel, so every piece seats against something already built. Where a piece still has a part that would hang in space, a **yellow construction pylon** braces it. There are 23 pylons, and they are removed when the ship is complete.

Construction drones bring each piece out of the mothership's starboard hangar and assemble the frigate beside it. The open faces of the partly built hull show 3D block interiors.

Everything here was made from copies in `source/`. The supply frigate, supply ship assembly, ship assembly, construction drone and mothership folders were only read. `space-game-prototype` was not touched; it was only read for sizes.

![Build stages, seen from the bow](renders/stages_sheet.png)

## Scale: cut in artwork metres, built in game metres

The supply frigate artwork is 85 m long (66.2 x 85.2 x 48.4 m with the mast and aerials). It is not in the game yet. As agreed, the kit is made for a game scale of **0.25**, the scale of the fighters it docks and of the supply ship. Its pads were sized for the artwork-scale fighters. In the game the frigate is then **16.6 x 21.3 x 12.1 m**, and a `supply_frigate.tscn` should scale its `Model` node by 0.25, as `supply_ship.tscn` does.

- **Cutting and interiors are done in artwork metres**, so the interior detail matches the hull art.
- **`to_game_scale.py` then scales the finished kit by 0.25.** That gives `blender/sf_kit_game.blend` and `reports/kit_pieces_game.json`. The hangar fit, the animation, the collision sweep and the Godot export all run on that, unchanged from the frigate pipeline.

The hangar transit envelope is the frigate's: **10.2 x 7.4 x 3.6 game metres** (40.8 x 29.6 x 14.4 artwork metres). Rings are capped at 6.8 artwork metres (1.7 game metres), as on the supply ship, so the build reads ring by ring.

## How it is cut

![Exploded kit](renders/kit_exploded.png)

1. **One solid.** The game mesh is 16 closed shells that overlap: the hull, three grafted engine sections with their backing sleeves, the six pad decks whose plinths sink into the hull, and a few greebles. `prep_source.py` MANIFOLD-unions them into one solid, `SupplyFrigate_Hull`. That removes 2,114 m³ of overlap; the source keeps its UVs and paint. Without this step every cut would double its faces where shells overlap.
2. **Sections.** The cross-section area along the hull (`reports/section_profile.json`) is flat along the pad blocks. It has waists at:
   - y -35.5, where the side engines meet the stern blocks;
   - y -20.5, at the aft pad blocks;
   - y +16.5, at the bow pods.

   The centre engine stands proud of the stern, so y -45.3 to -40.4 is its own section.
3. **Rings.** Each section is divided into even rings no thicker than 6.8 artwork metres: 1 engine block, 1 stern, 3 aft, 6 midship and 4 bow, so **15 rings**.
4. **Quarters.** The centre engine block (17 x 4.8 x 10.7 m) fits the hangar whole. Every other ring is split twice:
   - port/starboard at X = 0, so the kit is mirrored;
   - into a lower and an upper band at **z = -1.5**, halfway between the ventral (-13.45) and dorsal (+10.55) pad decks.

   The band seam runs level along the whole ship. A quarter is at most 33 x 6.2 x 25.7 artwork metres; the upper quarters under the mast are the tallest.
5. **Keel.** As on the beam frigate, a lattice truss in construction yellow-orange (`build_keel.py`) runs down the centreline. The ship is built around it.
   - **Size:** a 4.8 m square, with 7.8 m flanges between segments (1.2 / 1.9 game m). It is the beam frigate's truss scaled to this hull.
   - **Position:** centred at z -5.5, from y -35 (inside the stern blocks) to y +26.5. Further forward the centreline opens into a crevice and then the gap between the bow pods.
   - **Segments:** 4, split at the section waists and mid-midship: 14.5, 18.5, 18.5 and 10 m long.
   - **Channel:** the keel lies in a 6 m square channel cut through the lower quarters of rings 02-12, wholly inside the lower band (its top is 1 m below the band seam). The channel lies wholly inside the hull (0 m³ outside), and every truss vertex is inside the finished hull by ray parity.
   - **No fittings:** the frigate has no moving parts.
6. **Open-block interiors (3D).** The bow-facing cut face of each piece gets the frigate's interior treatment:
   - a cavity 1.2 m deep, with a 0.4 m armour rim along the hull skin and a 0.15 m frame along the X = 0 and band joints;
   - decks on a 3 m grid with **both pad decks on the grid**: the ventral deck is deck 0 and the dorsal deck is deck 8;
   - hazard-striped deck edges, girders seen end-on, pillars and partitions;
   - pipe runs, ducts and cable trays, machinery, tanks, scaffolding and work lights.

   Surfaces are quilted from the **supply frigate's own albedo atlas** (`textures/pool_*.png`).

   ![Mid-build open faces](renders/stage_050.png)
7. **Construction pylons.** See *Nothing floats* below.

| | |
| --- | --- |
| Pieces | 61: 4 keel segments (`Keel_0`-`Keel_3`), the centre engine block (`Ring00`), then Ring01-Ring14 as quarters `_PL`, `_SL`, `_PU`, `_SU` |
| Largest piece in transit | Ring07_PU, 8.28 x 3.07 x 1.54 game m (envelope 10.2 x 7.4 x 3.6) |
| Hull volume | 93,146.69 m³ = source 95,360.69 - keel channel 2,214.00 (artwork m³; every hull piece a closed shell, no boundary or non-manifold edges) |
| Cavities | 53 open faces, all 1.2 m deep, all probed wholly inside their piece apart from the keel channel (`reports/interiors.json`) |
| Triangles | 491,000 for the whole kit with interiors; 208,578 without, including 2,944 for the keel (the source hull is 153,504) |

The interiors are thinner than on the other two kits. The frigate's open faces add up to about 14,000 m², twelve times the supply ship's. At the supply ship's density they would have added about 860,000 triangles. For this kit:

- girders are single boxes every 1.8 m;
- each cable tray holds one cable bundle;
- only pipes of at least 0.1 m radius get flanges;
- pipe runs are shorter, and there are fewer scaffolds, lights and service cabinets;
- pipes under 0.12 m radius have four sides.

At 0.25 game scale the dropped detail is a few centimetres across. The whole kit is still about three times the finished hull's triangle count. The kit only exists while the ship is being built.

`reports/kit_pieces.json` (artwork metres) and `reports/kit_pieces_game.json` (game metres) hold every piece's plan:

- name, tier and ring;
- assembled centre, dimensions, transit quaternion and transit dimensions;
- approach direction and staging point;
- build order, triangle count and shell checks.

`reports/hangar_fit.json` re-tests every piece in transit pose in the real starboard bay with the drone docked behind it. **All 61 fit**; the tightest (Ring07_PU) has 1.26 m of side clearance.

![Upper quarter in transit pose in the starboard bay](renders/hangar_fit_cutaway.png)

## How it is assembled

Build order:

1. **The keel**, stern to bow. Each segment comes in from the port side, square to the ship.
2. **Rings 02 to 14, stern to bow**, starting at the keel's stern end. In each ring:
   - the lower port quarter, then the lower starboard quarter. In rings 02-12 these carry the keel notch and slide onto the keel sideways, square to it, as the beam frigate's keel bands do;
   - then the upper port quarter, then the upper starboard quarter.

   The other quarters slide in radially from the keel axis.
3. **The stern, working aft.** Ring01 (the stern blocks with the side engines) and then the centre engine block (Ring00, from astern) go on last. Each seats against the ring forward of it.

### Nothing floats

As first built, the kit went stern to bow from the centre engine. Then 21 of the 57 hull pieces had a part that touched nothing already built when they seated. `scripts/support_check.py` finds these: it splits every piece into its loose hull parts, ignoring the interior fit-out, and walks the build order. A part counts as supported if it is within 3 cm of the keel, of a part already supported, or of a supported part of its own piece. The floating parts were:

- **The stern.** The centre engine block and both side engines were seated before anything they touch. The keel starts 5 m forward of them.
- **Ring02's outboard stern blocks.** They meet the rest of the hull only through Ring01 and Ring03.
- **Ventral machinery under the belly (z about -11)**, the aerials and a few greebles. Each meets the hull only in a neighbouring ring.
- **Boolean crumbs.** These are bits under 0.4 m across, and zero-thickness slivers lying on cut planes.

The fixes, in this order:

1. **Build outward from the keel.** The rings astern of the keel's stern end are built last, working aft (`make_kit.py`). That removes the stern floaters.
2. **Construction pylons** (`scripts/pylons.py`). Every part still floating gets a yellow square strut with a foot plate at each end, in the keel's construction yellow, to the nearest supported surface.
   - **Target:** a supported part of the same piece is preferred, so the piece arrives as one braced unit. All 23 pylons ended up that way. The longest, 6.5 m, spans the slot between an outboard stern block and the main hull in Ring02.
   - **Placement:** strut ends are kept inside the piece's own bounds, so no pylon pokes into a neighbouring piece. A strut is kept only if it really meets both parts and crosses no other piece of the finished ship, the keel included.
   - **Scene setup:** each pylon is an object `Pylon_<piece>_<n>`, parented to its piece. It flies in with the piece and appears and disappears with it.
   - **Removal:** the animation removes every pylon after the last weld. The finished ship has none.
3. **Crumbs deleted.** 8 boolean crumbs (6-8 triangles each) are removed from their pieces rather than braced.

The support check now reports **0 of 57 hull pieces floating** (`reports/support.json`). `reports/pylons.json` lists every pylon (its ends, length and radius) and every deleted crumb.

| Ring02 from below and astern: a pylon across the stern block slot | The belly mid-build: braces on the ventral machinery |
| --- | --- |
| ![stern pylons](renders/pylons_stern.png) | ![belly pylons](renders/pylons_belly.png) |

`blender/sf_build_anim.blend` animates the build with 8 drones from the starboard hangar, at eight game seconds per video second (`scripts/animate_build.py`). The trip logic is the frigate's:

1. The piece is issued in the bay and leaves.
2. It turns in open space and flies a lane 10 m ahead of its ring.
3. It stops at staging, then seats and is welded.
4. The drone returns over the top and queues for the bay.

Results (`reports/build_schedule.json`):

- **Build time:** about **557 s** (9.3 min) of game time, **9.1 s per piece**. As on the other two kits, the single bay is the bottleneck. Before the keel was added, a 12-drone build took 506 s against 530 s with 8, but seven of them flew only once, because their queue slots at the ends of the holding line always lost the bay to the drones nearer the mouth. Eight drones keep the bay just as busy with fewer drones parked.
- **Drones on the outward face.** At every piece's seated frame its drone is on the outward side.
  - **39 pieces:** the piece-to-drone direction lies along the approach.
  - **The 22 keel quarters:** these slide in square to the keel, so, as on the beam frigate's keel bands, the drone grips the top face. It sits straight above the piece, on the band seam, which stays empty until the upper quarters follow.
- **Video:** `renders/sf_build.mp4`, 72 s at 1280x720. The wide camera looks from bow-starboard at the hangar mouth, the return queue and the site; the site camera looks into the open bow faces. It is local only, because `*.mp4` is gitignored.

![Wide camera: quarters leaving the hangar, the return queue above it, the rings going down at the site](renders/anim_wide_sheet.png)

![Site camera: the keel laid with the first quarters arriving, the stern rings closing over the keel, the midship rings, the bow](renders/anim_site_sheet.png)

`scripts/check_collisions.py` swept every third frame. It tests each flying piece and drone against every seated piece, the mothership hull and each other, with movers shrunk 3 cm. Over 1,716 frames it found **19 contact samples in 5 pairs**, all involving a drone (`reports/collisions.json`):

| Contact | Frames | What it is |
| --- | --- | --- |
| Drone_02 / Ring02_PU, Ring03_PU | 166-175, 283-295 | the drone welding a keel quarter of ring 03 or 04 from above overhangs the previous ring's seated upper quarter by about 9 cm |
| Drone_03 / Ring02_SU, Ring03_SU | 208-217, 322-334 | the same on the starboard side |
| Drone_02 / Ring02_SL | 82 | the drone that welded a first-ring quarter backs off past its neighbour |

Rings 03 and 04 are 1.25 game m thick, thinner than the drone (1.49 m), which sits straight above a keel quarter. Rings 05 onward are 1.54 m and clear it. Each overhang lasts about 4 game seconds, during the weld. This is the light drone clipping already accepted on the frigate and supply ship builds, so the routes were left alone.

No piece touches another piece, the keel or the mothership, including the stern rings that now go on last. The pylons lie inside their piece's bounds and cross no other piece of the finished ship (`pylons.py` checks this).

## Into the game

`scripts/export_kit.py` wrote `godot_export/supply_frigate_kit.glb` and `supply_frigate_kit_plan.json`:

- The GLB has 61 top-level nodes, each with its origin at the piece's bounds centre. The 23 `Pylon_*` braces are child nodes of their pieces. It is 47.7 MB, including the packed 4K hull atlas and the pool textures.
- The plan is in the Godot frame (bow -Z, up +Y), **already at game scale**. Its bounds are 16.555 x 12.094 x 21.289 m, the finished frigate's 66.22 x 48.38 x 85.16 m at 0.25 to the millimetre. The kit therefore lines up with the finished frigate under a 0.25-scaled `Model` node, origin for origin.
- The keel axis height is -1.375 and the hull radius about it is 8.77 m. The keel segments are tier `keel`, as on the beam frigate.
- Each piece carries `transit_axes`, which the game's `ConstructionSite.transit_basis()` uses.
- Each piece also lists its `pylons`, and the plan's `temporary_nodes` note says how to treat them. The game should show them with their piece and remove them all once the last piece is welded. If it swaps the whole kit for the finished ship at completion, that removes them too.

The supply frigate is not in the game yet, so this kit has not been imported. Once the frigate is in, the import follows the supply ship's:

```text
python tools/construction/import_ship_kit.py supply_frigate_kit assets/ships/<class>/supply_frigate/construction "C:\Dev\BlenderMCP\artwork\supply frigate assembly"
```

That project's `docs/ship_construction.md` describes the rest:

- a `ConstructionKit` `.tres` on the carrier's `Shipyard`, with its own `build_key`;
- the finished scene, which must be the same hull in the same frame;
- `critical_pieces`. `Keel_*` is the natural choice, as on the beam frigate.

## Files

| File | Purpose |
| --- | --- |
| `source/*_COPY.*` | Copies of the supply frigate game-ready blend, its albedo atlas, texel-label map and UV mask, and the construction drone and mothership GLBs (from `supply ship assembly/source/`) |
| `blender/sf_source_prepared.blend` | The frigate unioned into one solid (`prep_source.py`) |
| `blender/sf_kit.blend` | The kit in artwork metres, with interiors: every piece at its assembled position, `kit_order` property |
| `blender/sf_kit_game.blend` | The same kit at game scale (x 0.25) |
| `blender/sf_build_anim.blend` | The build animation, with the mothership copy, 8 drones and cameras `Cam_Wide` and `Cam_Site` |
| `blender/hangar_fit.blend` | An upper quarter and docked drone in the starboard bay (roof removed on the copy) |
| `textures/pool_*.png` | Tileable 8 m surface textures quilted from the supply frigate's albedo atlas |
| `godot_export/` | `supply_frigate_kit.glb` and `supply_frigate_kit_plan.json` |
| `renders/` | Exploded kit, build stages, pylon close-ups, hangar fit, animation stills (`anim_*`), and `sf_build.mp4` |
| `reports/` | Section profile, kit plan (both scales), interiors, support check, pylons, hangar fit, build schedule, collision sweep, run logs |

## Rebuilding

Scripts declare the workspace path at their start. They need Blender 5.1, and every boolean uses the MANIFOLD solver. `B` = `"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"`. Each Blender step also runs headless (`B -b <file> -P <script>`); the whole chain takes about three minutes.

1. `python scripts/make_hull_pools.py` (system Python with OpenCV and SciPy).
2. Open `source/supply_frigate_game_ready_COPY.blend` (in its own MCP call), then exec `scripts/prep_source.py`. To re-derive the sections, exec `scripts/section_profile.py` with `SRC_NAME='SupplyFrigate'; STEP=0.5; WINDOW=6.0`.
3. `B -b blender/sf_source_prepared.blend -P scripts/make_kit.py`, then `B -b blender/sf_kit.blend -P scripts/interior_export.py`.
4. `python scripts/interior_layout.py`, then `B -b blender/sf_kit.blend -P scripts/interior_build.py`, then `B -b blender/sf_kit.blend -P scripts/pylons.py`. Check the result with `B -b blender/sf_kit.blend -P scripts/support_check.py`; it must report 0 floating.
5. `B -b blender/sf_kit.blend -P scripts/to_game_scale.py`.
6. `B -b --factory-startup -P scripts/hangar_fit.py`.
7. `B -b blender/sf_kit_game.blend -P scripts/animate_build.py`.
8. `B -b blender/sf_build_anim.blend --python-expr "STEP=3; exec(open(r'...\scripts\check_collisions.py').read())"`.
9. `B -b blender/sf_build_anim.blend -P scripts/render_video.py`. For stills, run `B -b blender/sf_kit.blend -P scripts/render_kit.py`, or `anim_stills.py` with `FRAMES` / `CAMS` set.
10. `B -b blender/sf_kit_game.blend -P scripts/export_kit.py -- --name supply_frigate_kit`.

Steps 3 and 4 rewrite `sf_kit.blend`, so rerun from step 3 after changing a layout.

Renders use Workbench (textured), because EEVEE previews render blank on this machine. The mothership's texture smears in Workbench; it looks correct in Godot.

## Differences from the supply ship pipeline

- `prep_source.py`: unions the 16 overlapping shells into one solid. There are no cranes or pods to freeze.
- `build_keel.py` (from the beam frigate): its truss scaled for artwork metres, with `KEEL_SPLITS` -35 / -20.5 / -2 / 16.5 / 26.5.
- `build_kit.py`:
  - the keel channel is carved from every ring it crosses, and is probed to lie inside the hull;
  - the sections are listed above, and Ring00 (the centre engine) stays whole;
  - every other ring is split at X = 0, then at `BAND_Z` = -1.5, into PL / PU / SL / SU;
  - there are no fittings;
  - the lower quarters on the keel slide in sideways; the other quarters come in radially from the keel axis (z -5.5).
- `make_kit.py`:
  - the keel goes first, then rings 02-14 stern to bow, then Ring01 and Ring00 working aft; within a ring, lower quarters before upper, port before starboard;
  - the keel-inside-hull test uses ray parity. The beam frigate's closest-point normal test flagged 7 truss vertices 8 m deep in the hull, next to thin slivers by the ventral deck plinths.
- `support_check.py` and `pylons.py` (new): the floating-part check and the construction braces described above.
- `to_game_scale.py`: skips `ring_y` for keel segments and scales the pylons with their pieces.
- `animate_build.py`: pylons share their piece's visibility keys and are hidden after the last weld.
- `export_kit.py`: pylons are exported as child nodes and listed per piece in the plan.
- `render_kit.py`: the stages show the pylons and the finished stage hides them; `pylons_stern.png` and `pylons_belly.png` are close-ups.
- `interior_build.py`: the breach probe excludes the keel channel (its own copy of `CHANNEL`).
- `section_profile.py`: ignores NaN slivers from degenerate cut triangles.
- `make_hull_pools.py`: label values are class index x 36, the atlas is 23 px/m, and a window texel must also be near its class's median colour. The label map predates the frigate's final repaint, and without that test the quilts showed blue and yellow blocks.
- `interior_layout.py`:
  - `DECK_Z0` = -13.45, the ventral pad deck;
  - the deck range reaches the mast;
  - the thinner fit-out described above;
  - sections are rasterised **even-odd**. `holes_fill` gives every loop of a section its own face, so a void behind the face counted as solid, and the probe then rejected 5 cavities and cut 4 shallow. Now all 53 are full depth.
- `interior_build.py`: pipes up to 0.12 m radius have four sides.
- `animate_build.py`, sized for a 21 m, 16.6 m wide ship:

  | Constant | Supply frigate | Supply ship |
  | --- | --- | --- |
  | Build site | (70, -6, 2) | (58, -6, 2) |
  | `R_ARC` / `R_RET` | 21 / 32 m | 13 / 24 m |
  | `Y_LANE` | 10 m | 8 m |
  | Time-lapse | 8 game s per video s | 5 game s per video s |
  | Cameras | further out | |
