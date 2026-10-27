# Supply ship assembly: building the supply ship from hangar-sized kits

The supply ship cut into a **26-piece construction kit**, the same way the beam frigate was in [`../ship assembly/`](../ship%20assembly/README.md):

- **22 hull pieces**;
- **2 stowed cranes**;
- **2 cargo pods**.

Construction drones bring each piece out of the mothership's starboard hangar and assemble the ship beside it. The open faces of the partly built hull show 3D block interiors.

Everything here was made from copies in `source/`. The supply ship, beam frigate, ship assembly, construction drone and mothership folders were only read, and so was `space-game-prototype`.

![Build stages, seen from the bow](renders/stages_sheet.png)

## Scale: cut in artwork metres, built in game metres

The supply ship artwork is a 60 m ship (59.8 x 24.8 x 21.1 m), but the game shows it at **0.25 scale**: `supply_ship.tscn` scales its `Model` node, so in the game it is **15.0 x 6.2 x 5.3 m**. The mothership, its hangar and the construction drones are all in game metres.

- **Cutting and interiors are done in artwork metres.** The 3D interiors use the same primitive sizes as the frigate's (3 m deck grid, 0.4 m armour rim, girders, pipes, machinery), so their detail matches the hull art.
- **`to_game_scale.py` then scales the finished kit by 0.25.** That gives `blender/supply_kit_game.blend` and `reports/kit_pieces_game.json`. The hangar fit, the animation, the collision sweep and the Godot export all run on that, unchanged from the frigate pipeline.

The hangar transit envelope is the frigate's, **10.2 x 7.4 x 3.6 game metres** (40.8 x 29.6 x 14.4 artwork metres). At game scale the hangar alone would allow about five pieces, because whole blocks fit. As asked, the ship is instead cut frigate-style into rings of at most 1.7 game metres, so the build reads ring by ring with a dozen drones' worth of traffic.

## How it is cut

![Exploded kit](renders/kit_exploded.png)

1. **Sections.** I measured the cross-section area along the hull (`reports/section_profile.json`). It splits into three natural blocks:
   - the **stern engine block**, Y -30 to -17;
   - the slim **midship** around the cargo bay, -17 to +10.75;
   - the **bow block**, +10.75 to +30, with a waist at +21.
2. **Rings.** Each section is divided into even rings no thicker than 6.8 artwork metres (1.7 game metres): 2 stern, 5 midship, 2 + 2 bow, so **11 rings**.
3. **Midship: keel and deck slabs.** The cargo bay is a clean through-tunnel (z -4.5 to +1.3) from Y -16.5 to +10.5. Every midship ring is therefore two separate slabs, cut apart at z = -1.5 through the empty bay:
   - the **keel slab `K`** below, which is the ship's spine (no keel truss is needed);
   - the **deck slab `D`** above.
4. **Stern and bow: port and starboard.** Each stern and bow ring is split at X = 0, so the kit is mirrored.
5. **Fittings.** The two cranes are frozen in their stowed pose and split port/starboard. The two pods are seated at the ship's own pod seats, matching the game's `PodSeat*` markers to within 3 mm.
6. **Open-block interiors (3D).** The bow-facing cut face of each hull piece gets the frigate's interior treatment:
   - a cavity up to 1.2 m deep (artwork metres), with a 0.4 m armour rim;
   - decks on a 3 m grid with the **bay floor (z -4.5) on the grid**, hazard-striped deck edges, girders seen end-on, pillars and partitions;
   - pipe runs, ducts and cable trays, machinery, tanks, scaffolding and work lights.

   Surfaces are quilted from the **supply ship's own albedo atlas** (`textures/pool_*.png`, 44 px/m source density), so they carry the hull's grain. The keel and deck slabs are split through empty space, so their bay sides are hull skin and keep the full armour rim.

   ![Stern block open face](renders/stage_005.png)

| | |
| --- | --- |
| Hull pieces | 22: 4 stern half-rings, 5 keel slabs + 5 deck slabs, 8 bow half-rings |
| Fittings | Crane_L / Crane_R (stowed, 2.8 x 0.9 x 0.5 m in transit) and Pod_L / Pod_R |
| Largest piece in transit | a cargo pod, 6.47 x 2.15 x 1.46 m (envelope 10.2 x 7.4 x 3.6) |
| Hull volume | 9662.14 m³ = source 9662.13 (artwork m³; closed shells, no boundary edges) |
| Cavities | 20 open faces, all probed wholly inside their piece; Ring00_P/S at 0.8 m and Ring05_D at 0.5 m depth where the hull narrows (`reports/interiors.json`) |
| Triangles | 220,714 for the whole kit with interiors (170,302 without; source hull 93,314, cranes 5,548, pods 2 x 22,632) |

`reports/kit_pieces.json` (artwork metres) and `reports/kit_pieces_game.json` (game metres) hold every piece's plan:

- name, tier (`hull` / `fitting` / `pod`) and ring;
- assembled centre, dimensions, transit quaternion and transit dimensions;
- approach direction and staging point;
- build order, triangle count and shell checks.

`reports/hangar_fit.json` re-tests every piece in transit pose in the real starboard bay with the drone docked behind it. **All 26 fit**; the tightest (a pod) has 2.16 m of side clearance.

![Keel slab in transit pose in the starboard bay](renders/hangar_fit_cutaway.png)

## How it is assembled

Build order:

1. **Stern.** The stern rings go down first, port before starboard; each half slides in from its own side.
2. **Midship.** Midship rings follow, each **keel slab from below, then its deck slab from above**.
3. **Bow.** The bow rings follow, port before starboard; the intake ring comes last.
4. **Cranes.** Both cranes drop onto the deck from above.
5. **Pods.** The pods slide into the bay from their own side, the way the cranes unload and load them in the game.

`blender/supply_build_anim.blend` animates the build with 8 drones from the starboard hangar, at five game seconds per video second (`scripts/animate_build.py`). The trip logic is the frigate's: issue in the bay, exit, turn in open space, a lane ahead of the ring, staging, seat, weld, return over the top and queue for the bay. The constants are scaled to this ship:

| Constant | Supply ship | Frigate |
| --- | --- | --- |
| Build site (mothership Blender frame) | (58, -6, 2) | (82, -6, 2) |
| Arrival ring `R_ARC` / return ring `R_RET` | 13 / 24 m | 24 / 40 m |
| Lane ahead of the ring `Y_LANE` | 8 m | 10 m |
| Drones | 8 | 10 |
| Staging clearance | 2 game m | 2 m |

Results (`reports/build_schedule.json`):

- **Build time:** about **208 s** (3.5 min) of game time, **8.0 s per piece**. As on the frigate, the single bay is the bottleneck.
- **Video:** `renders/supply_build.mp4`, 45 s at 1280x720. The wide camera looks from bow-starboard at the hangar mouth, lanes and site; the site camera looks into the open bow faces. Local only; `*.mp4` is gitignored.

![Site camera: deck slab going down, a bow half-ring arriving, the crane dropping in, the finished ship with both pods](renders/anim_site_sheet.png)

`scripts/check_collisions.py` swept every third frame. It tests each flying piece and drone against every seated piece, the mothership hull and each other, with movers shrunk 3 cm. **4 contacts remain** (`reports/collisions.json`):

| Contact | Frame | What it is |
| --- | --- | --- |
| Drone_00 / Ring01_P and Drone_02 | 79 | the drone that welded Ring00_P backs off as the next half-ring arrives |
| Drone_01 / Drone_03 | 112 | the same at Ring01_S |
| Drone_04 / Drone_05 | 886 | the first crane's drone leaves as the second crane comes down |

Each lasts a single sampled frame (about 0.6 s of game time) and is a drone brushing drone traffic. That is the light clipping accepted on the frigate build, so the routes were left alone.

The first sweep found 117 contacts from two real problems, both fixed in `build_kit.py`:

- **The seated pods sat 1.5 m too high, inside the deck slabs.** `finish_piece()` assumed a piece's mesh was already in world coordinates, as boolean-carved pieces are. The pods carry their seat as an object location, so it was lost. The object transform is now baked into the mesh first. The pods now clear every hull piece at their seat, as on the original ship.
- **Drones carrying midship slabs stuck into the seated rings behind them for about 2.5 s.** The keel and deck slabs are thinner vertically than their ring thickness. The frigate's "thinnest side down" transit rule therefore put the tow axis, and the drone, along the ship's length. `transit_fit_towed()` now tows along the axis nearest the piece's approach whenever the piece still fits, so the drone sits on the outward face. That means below a keel slab, above a deck slab, and outboard of a half-ring or pod.

## Into the game

`scripts/export_kit.py` wrote `godot_export/supply_ship_kit.glb` (26 top-level nodes, origin at each piece's bounds centre, 32.5 MB including the packed hull, pod and pool textures) and `supply_ship_kit_plan.json`. The plan is in the Godot frame (bow -Z, up +Y), **already at game scale**. It therefore lines up with `supply_ship.tscn`'s root, whose `Model` is scaled 0.25: bounds 6.2 x 5.3 x 15.0 m, and `Pod_R` at (1.1145, -0.377, 0.628) against the scene's `PodSeatStarboard` (1.1145, -0.375, 0.625). The keel axis height is -0.375 (the bay axis), with a hull radius of 3.44 m.

Nothing was installed into `space-game-prototype`. To use the kit there, follow the frigate route in that project's `docs/ship_construction.md` (`tools/construction/import_ship_kit.py`, then a `ConstructionKit` resource). Two things differ from the frigate:

- **New tiers.** The plan has the tiers `fitting` and `pod` besides `hull`, and no `keel` tier. The game's construction code may need to accept them; ordering is already in `order`.
- **Pod swap.** The finished `supply_ship.tscn` spawns its own pods on ready (`start_loaded`). When the kit is swapped for the finished ship, either drop the kit's two pods or start the ship empty and hand it these pods.

## Files

| File | Purpose |
| --- | --- |
| `source/*_COPY.*` | Copies of the supply ship game-ready blend, its albedo atlas, paint-class map and UV mask, the cargo pod GLB, and the construction drone and mothership GLBs (from `ship assembly/source/`) |
| `blender/supply_source_prepared.blend` | Static hull, stowed cranes split L/R, pods at their seats (`prep_source.py`) |
| `blender/supply_kit.blend` | The kit in artwork metres, with interiors: every piece at its assembled position, `kit_order` property |
| `blender/supply_kit_game.blend` | The same kit at game scale (x 0.25) |
| `blender/supply_build_anim.blend` | The build animation, with the mothership copy, 8 drones and cameras `Cam_Wide` and `Cam_Site` |
| `blender/hangar_fit.blend` | A keel slab and docked drone in the starboard bay (roof removed on the copy) |
| `textures/pool_*.png` | Tileable 8 m surface textures quilted from the supply ship's albedo atlas |
| `godot_export/` | `supply_ship_kit.glb` and `supply_ship_kit_plan.json` |
| `renders/` | Exploded kit, build stages, hangar fit, animation stills (`anim_*`), and `supply_build.mp4` |
| `reports/` | Section profile, kit plan (both scales), interiors, hangar fit, build schedule, collision sweep |

## Rebuilding

Scripts declare the workspace path at their start. Blender 5.1. Every boolean uses the MANIFOLD solver. `B` = `"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"`.

1. `python scripts/make_hull_pools.py` (system Python with OpenCV and SciPy).
2. Open `source/supply_ship_game_ready_COPY.blend` (in its own MCP call), then exec `scripts/prep_source.py`. To re-derive the sections, exec `scripts/section_profile.py` with `SRC_NAME='SupplyShip_Hull'; STEP=0.5; WINDOW=6.0`.
3. Open `blender/supply_source_prepared.blend`, then exec `scripts/make_kit.py`. Reopen `blender/supply_kit.blend`, then exec `scripts/interior_export.py`.
4. `python scripts/interior_layout.py`, then in the same Blender session exec `scripts/interior_build.py`.
5. `B -b blender/supply_kit.blend -P scripts/to_game_scale.py`.
6. `B -b --factory-startup -P scripts/hangar_fit.py`.
7. `B -b blender/supply_kit_game.blend -P scripts/animate_build.py`.
8. `B -b blender/supply_build_anim.blend --python-expr "STEP=3; exec(open(r'...\scripts\check_collisions.py').read())"`.
9. `B -b blender/supply_build_anim.blend -P scripts/render_video.py`. Stills: `B -b blender/supply_kit.blend -P scripts/render_kit.py`, or `anim_stills.py` with `FRAMES` / `CAMS` set.
10. `B -b blender/supply_kit_game.blend -P scripts/export_kit.py -- --name supply_ship_kit`.

Renders use Workbench (textured), because EEVEE previews render blank on this machine. The mothership's texture smears in Workbench; it looks correct in Godot.

## Differences from the beam frigate pipeline

- `prep_source.py` (new): freezes the skinned cranes and seats the pods, so they become kit pieces.
- `build_kit.py`:
  - the envelope is scaled to artwork metres;
  - there is no keel channel and no `build_keel.py`;
  - midship rings split through the bay into K/D slabs;
  - the fittings are added with fixed approaches (cranes from above, pods from their side);
  - `finish_piece()` bakes the object transform into the mesh, and the transit tow axis follows the approach (`transit_fit_towed()`).
- `make_kit.py`: fittings are ordered after the hull and pods last; `STAGE_CLEAR` is 8 artwork metres (2 game metres).
- `interior_layout.py`: `DECK_Z0 = -4.5` (bay floor). `interior_build.py`: no keel-channel exclusion in the breach probe.
- `to_game_scale.py` (new): the 0.25 conversion. Downstream scripts read `kit_pieces_game.json` and `supply_kit_game.blend`.
- `animate_build.py`: the site, rings, lane, drone count and cameras are sized for a 15 m ship.
