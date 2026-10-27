# Guide: cutting a ship into a construction kit

This is for an AI session asked to turn another ship (a frigate, corvette or capital ship) into a construction kit like the beam frigate's. Drones carry the kit out of the mothership's hangar and assemble it in space. Read the `README.md` beside this file first; it covers the finished frigate example and the reasoning. This guide is the procedure, the rules that are not obvious, and the mistakes already made once.

## Quick run order

Each step is detailed below. MCP means `execute_blender_code`, with the file opened in its own call first. Headless means `blender.exe -b`.

| # | Where | Step | Check |
| --- | --- | --- | --- |
| 1 | system Python | `make_hull_pools.py` (needs the atlas, label and mask copies in `source/`) | `textures/pool_*.png` look like the hull's grain, with no blocks |
| 2 | MCP, source copy open | exec `section_profile.py`, then set `SECTIONS` | the waists are the ship's block joins |
| 3 | MCP, source copy open | exec `make_kit.py`, then `interior_export.py` | `all_fit`, `all_closed`, volume = source - channel, channel/keel outside = 0 |
| 4 | system Python | `interior_layout.py` | every open face has a cavity and primitives |
| 5 | MCP, same session | exec `interior_build.py` | `open 0 skipped [] shallow []`; render a mid-build still and look at it |
| 6 | headless | `hangar_fit.py` | `fail 0`; look at the cutaway |
| 7 | headless | `animate_build.py` | build time and bay cycle are plausible |
| 8 | headless, background | `check_collisions.py` with STEP=3 | 0 contacts, or a reason for each |
| 9 | headless | `render_video.py`, `render_kit.py` / `anim_stills.py` | watch it |
| 10 | headless | `export_kit.py -- --name <ship>_kit` | `godot_export/<ship>_kit.glb` and `_plan.json` (Godot frame) |
| 11 | space-game-prototype | `python tools/construction/import_ship_kit.py <ship>_kit assets/ships/<class>/<ship>/construction`, then a `ConstructionKit` `.tres` on the carrier's `Shipyard` | the prototype's `docs/ship_construction.md` |

## Ground rules from the user

- **Never edit `space-game-prototype`.** Read it for sizes only.
- **Never edit another asset's folder.** Copy what you need into the new kit's own `artwork/<ship> assembly/source/` folder as `*_COPY.*`, and work only on the copies.
- **Make a new folder per ship** under `artwork/`. Don't put a second ship into `ship assembly/`.
- **Check sizes in the game before cutting.** The frigate and mothership are unit scale. Small craft (drones, fighters) are 0.25 scale. Read the ship's `.tscn` in the prototype for any `scale` on its `Model` node, and its doc in `docs/`.

## Tools in this environment

- **Blender 5.1** through the MCP (`execute_blender_code`). It shares no Python state between calls: `exec()` a script file each call. `bpy.ops.wm.open_mainfile` must be its own call. If you exec a script that reuses a name you set in the calling code (it reused `t`), the script overwrites your variable.
- **Headless Blender:** `"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b file.blend -P script.py`. Use it for anything over about a minute (animation baking, sweeps, video), so the MCP does not drop. The foreground Bash limit is 10 minutes; use `run_in_background` beyond that. Don't filter the output with `grep` so tightly that a traceback is hidden: one sweep "finished" with exit 0 and wrote nothing.
- **Python with numpy/cv2/PIL:** `C:\Users\stevi\AppData\Local\Microsoft\WindowsApps\python.exe`. Plain `python` lacks cv2.
- **Previews:** Workbench with `color_type='TEXTURE'` (`scripts/wb_render.py`). EEVEE and material previews render blank here. The mothership texture smears in Workbench; that is a render artefact, not the asset.
- **Video:** Blender's own FFMPEG output (`scripts/render_video.py`). There is no ffmpeg binary. The 3,536-frame 720p Workbench video took about 2 minutes.

## The hard constraint: the hangar transit envelope

Every piece must leave a mothership side bay **thin side down, long side across the opening, towed in line ahead of a construction drone**:

| Limit | Value | From |
| --- | --- | --- |
| Across the opening | ≤ 10.2 m | forcefield 10.8 m wide, less 0.3 m each side |
| Along the bay | ≤ 7.4 m | 12.1 m from back wall to field, less the 4.0 m drone and 0.6 m of gaps |
| Height | ≤ 3.6 m | field 4.2 m tall (z -0.31 to 3.91), less 0.15 m ride height and top clearance |

Rejected alternatives:

- **Drone on top of the piece.** It doesn't fit: the drone alone is 1.5 m tall.
- **The 9.0 m "along" limit from my first estimate.** That came from a 13.8 m bay depth, but the forcefield sits at x = 19.2, so only 12.1 m is usable.

Measure the bay yourself if the mothership changes. Import `mothership_COPY.glb` and read the bounds of `Hangar_Forcefield` and `Hangar_Architecture`; `scripts/hangar_fit.py` does this.

## Procedure

Copy `scripts/` from `artwork/ship assembly/` into the new folder, then change the constants named below. Everything else is generic.

### 1. Prepare the source

Copy the ship's game-ready `.blend` into `source/`. The kit scripts expect the following, so fix them on the copy first:

- one **closed, manifold** hull mesh (zero boundary edges);
- length along **Blender Y** with the bow at +Y, Z up;
- metres at **game scale**, with the origin on the centreline.

Note the hull object's name; it is `SRC` in `build_kit.py` and `SRC_NAME` in `section_profile.py`.

If the source has several meshes (turrets, a separate bridge), join them into the hull. Or treat each as its own kit piece if it already fits the envelope, as a "fitting" installed last.

Also copy the ship's **albedo atlas, paint-class map and UV mask** into `source/` for the interior pools. The beam frigate has `textures/work/texel_labels.png` from its texture-cleanup pipeline: 0 graphite, 40 gunmetal, 80 armour, 120 red, 160 orange, 200 blue. If another ship has no such map, make one on the copy from luminance, as the frigate's `clean_texture.py` does. On CIELAB L (0-100, after a light blur): graphite ≤ 23 < gunmetal ≤ 46 < armour; it also pulls out red, orange and blue by hue. For the mask, use the atlas's non-black texels. Or quilt from the beam frigate's copies, since the ships share a paint scheme.

### 2. Find the waists

Exec `scripts/section_profile.py`. It prints the cross-section area along Y and the **waists**: dips at least 12% below the peaks within 3 m either side. They are the joins between the ship's natural blocks. Ring cuts there follow existing panel seams, and the build reads as real modules.

Set `build_kit.SECTIONS` from the waists. Each section is divided evenly into rings no thicker than `MAX_RING` (3.4 m, within the 3.6 m height limit). Avoid sections much shorter than a ring. On the frigate I used 14.5 instead of the 17.0 waist, where the area starts falling into the bow neck.

### 3. Size the keel

Look at where the hull's interior is solid enough to hide a truss. The keel and its channel must be completely enclosed by the hull:

- `build_kit.py` prints `keel channel outside hull (m3)`, which must be 0.0;
- `make_kit.py` prints `keel verts outside hull`, which must be 0.

Then set:

- `KEEL_AXIS_Z` / `KEEL_Z` and `CHANNEL` (y0, y1, half-size) in `build_kit.py`;
- `KEEL_SPLITS` in `build_keel.py`. Each segment must be ≤ 10.2 m long, which is the "across" limit.

Stop the keel short of grooves or engine bays where the hull is open. On the frigate the stern engine groove at |x| < 0.8 m, y < -18.2 ruled out the last few metres.

### 4. Build and check the kit

Open the source copy, then exec `scripts/make_kit.py`. That runs `build_kit.py` and `build_keel.py`, sets up the cut-face material, orders the build, writes `reports/kit_pieces.json` and saves `blender/frigate_kit.blend`. Rename the output for your ship.

Check the printout and the report:

- **`all_fit` true.** Every piece is within the envelope.
- **`all_closed` true.** No boundary or non-manifold edges.
- **`hull_volume` equals `source_volume - keel_channel_volume`** to within about 0.05 m³. This is the check that no cut lost geometry.
- **Plausible piece count.** The frigate (47 m) gave 70 hull pieces. Roughly, expect volume ÷ 80 m³.

Then run `blender -b -P scripts/hangar_fit.py`. It re-tests every piece in transit pose inside the real bay with the drone docked behind it, and renders the widest piece in a cutaway (`renders/hangar_fit_cutaway.png`). Look at that image.

### 5. Interiors

See *Open-block interiors* below: `interior_export.py`, `interior_layout.py` and `interior_build.py`, in that order, on the freshly built kit.

### 6. Animate and sweep

1. **Animate.** `blender -b blender/<kit>.blend -P scripts/animate_build.py`. Set `SITE` to a clear spot beside the mothership's hangar; the frigate is at (82, -6, 2) in mothership Blender coordinates, starboard side. For a bigger ship, also scale `R_ARC` to the hull radius plus the largest piece-plus-drone reach (about 11 m) plus a margin. Keep `R_RET` at least 11 m beyond `R_ARC`.
2. **Sweep.** `blender -b <anim>.blend --python-expr "STEP=3; exec(open(r'...\check_collisions.py').read())"`. It writes `reports/collisions.json`. Every contact pair needs a reason or a fix.
3. **Spot-check frames.** Use `scripts/anim_stills.py`, then render the video.

Also confirm the drone ends up on the outward face of every piece. At each piece's seated frame, the vector from piece to drone should point along the piece's approach. For square-on approaches (keel bands) it should point up.

## Rules learned the hard way

1. **Use the MANIFOLD boolean solver.** EXACT without self-intersection silently returned **empty** results, and once **nearly the whole ship** for a 2.8 m slab. EXACT with `use_self` worked but is slower. Always compare volumes after a split; `split_part()` nudges a failed plane a few centimetres and retries.
2. **Don't split a ring into inboard/outboard columns.** The drone grips the piece face that becomes outward. On an inboard column that face is the outboard column's slot, so the welding drone sits where the next piece must go. Split port/starboard at X = 0, then into **horizontal bands**, so drones grip top and bottom faces, which face open space.
3. **Give the keel a channel.** A keel buried in a solid hull means every piece around it interpenetrates it at seat. Keep band cuts `CHANNEL_MARGIN` clear of the channel, so a piece has either the whole notch or none. Bands carrying the keel must slide in exactly square to it, with an approach of (±1, 0, 0); a radial approach scrapes the notch walls.
4. **The drone towing face has a sign choice.** In transit the drone is at hangar −X. Rotating 180° about vertical flips which end of the piece it holds. `piece_mats()` picks the end that ends up outward. When the approach is square to that axis, it picks the top face, because rings build bottom up.
5. **Turn pieces in open space.** The transit-to-final rotation happens on the first leg (bay to arc entry). Turning near the hull swept a 6 m piece into its neighbour.
6. **Keep incoming and return traffic radially apart.** Carried pieces travel on a ring of radius `R_ARC`, but piece plus drone reaches about 11 m past it. Returning drones need `R_RET ≥ R_ARC + 11` and go back over the top (`avoid=math.pi`), never through the near-side outbound lane.
7. **Run the bay as one-at-a-time.** Release it (`bay_free`) only once the outbound pair, drone included, is past the return queue line. Returning drones wait in a line beside the hull above the opening, join it from above (`LANE_Z`), and drop below it to enter. A diagonal path to the mouth crossed the other queued drones.
8. **Count a drone's re-entry when assigning trips.** A returning drone needs about 4 s to cross the bay and turn around. Ignoring that left half the fleet idle and the bay stalled.
9. **Don't share end flanges between keel segments.** Inset them by half their thickness, or neighbouring segments overlap.
10. **Collision-test movers shrunk by 3 cm.** Rings share coplanar cut faces, so a piece sliding home legitimately touches its neighbour; shrinking distinguishes that from real penetration.
11. **`carve()` copies the source object, including `hide_render`.** Unhide pieces you carve from a hidden source, or they vanish from renders.
12. **Clear the neighbours at staging.** A fixed 8 m staging distance left a 9.4 m piece overlapping its seated neighbour sideways while it waited, and it climbed into staging from below. `make_kit.py` sets `stage_dist` = the piece's extent along its approach + `STAGE_CLEAR` (2 m).
13. **Keep incoming and outgoing traffic out of one plane.** An incoming arc in the ring plane swept through the slot the previous piece's drone was leaving. Incoming pieces now circle in a lane `Y_LANE` (10 m) ahead of their ring, on the unbuilt side, and drop into the ring plane only at their own bearing.
14. **Keep keel ribs inside the segment.** End ribs on the segment boundary poke their strut radius into the next segment. `build_keel.py` insets them behind the end flanges.
15. **Don't write paths in Python heredocs.** Through a shell heredoc `"\renders"` became a carriage return and `r"\blender"` a backspace. Edit path strings with the Edit tool.

## Open-block interiors

The open bow-facing cut of every piece shows a hull block under construction, as **real 3D geometry**. Two painted-texture versions were rejected before this. The user found a cruise-ship-style cutaway "flat and way too clean", and a version weathered with hull texels still "doesn't convincingly look like the interior of a spaceship being assembled". A picture on a cut face has no depth, and a ship under assembly is exposed structure, not finished cabins.

Pipeline, after `make_kit.py`:

1. **`interior_export.py`** (Blender). For each piece it exports the cut-face polygons on its forward ring plane, plus its cross-sections at 0.01-1.2 m behind it.
2. **`interior_layout.py`** (system Python, OpenCV). It rasterises the face (4 cm/px) and intersects it with every section behind it, so a hull narrowing toward a waist can't let the cavity out through the skin. It then erodes the outline by `RIM` along the hull skin and by `JOINT` along split planes; `split_sides()` reads them from the piece tag. Finally it places the primitives: decks on the deck grid (`DECK` 3 m, `DECK_Z0`), girders, pillars, partitions, pipes, ducts, trays, machinery, tanks, scaffolding and lights, each clipped to the cavity by corner tests.
3. **`interior_build.py`** (Blender, same session). It probes each cavity prism, starting 3 mm inside the face, against the piece minus the keel channel. If any of it is outside, the depth steps down to 0.8 / 0.5 m, and then the face is skipped. Then it MANIFOLD-subtracts the cavity, joins the primitives into the piece, and box-projects the pool UVs (8 m tile).

Rules:

- **Bands don't follow the deck grid.** A band piece often holds only part of a deck's height. Fill what's there: floor-standing kit only where the floor is in the piece, and pipes under the joint frame when the deckhead is in the next piece. Requiring full deck height left most midship faces empty.
- **Keep everything flush with the face.** Pipe flanges standing 5 cm proud would poke into the next ring at seat.
- **Value structure is what makes depth read.** Use dark primer for cavity walls and light ivory for structure, against them. Machinery in graphite on graphite walls vanished.
- **Quilt pools with normalisation.** Pull each atlas window to the class median colour with half its contrast (`synth(normalize=0.5)`). Raw windows keep their own baked light level and tile as a visible checkerboard.
- **Don't trust the volume-ratio check for breaches.** Raster-vs-contour error makes every cavity remove 93-99% of the "expected" volume; only the direct prism-outside-piece probe is reliable. Exclude the keel channel from that probe: it's an enclosed void, and a cavity reaching it is fine.
- **Expect about 1k triangles per open face.** The frigate's 62 cavities added about 69k triangles in all.

For another ship: set `DECK_Z0` so a deck floor falls where the ship's geometry suggests (a hangar floor, a window row, the keel line). Change the fit-out mix in `interior_layout.py` (`kind` choice, scaffold and pipe probabilities) to suit the ship, for example more machinery for a tug or hangar decks for a carrier. Re-quilt the pools from that ship's own atlas: copy its albedo, paint-class map and UV mask into `source/`.

## Into the game

`scripts/export_kit.py` writes the kit as one GLB plus a build plan in the Godot frame: Blender (x, y, z) becomes Godot (x, z, -y), so the bow is -Z. Each piece is a top-level node at its assembled place, origin at its bounds centre. The plan gives each piece's centre, size, approach, staging distance, ring and order, plus the kit's keel axis height, hull radius and bounds.

The game recomputes everything else from the plan, so no Blender-only numbers need converting:

- the transit attitude;
- which face the drone holds;
- the lanes;
- the airspace for site selection.

The game's construction drone is 3.125 m long, not the 4 m assumed when the envelope was set, so every piece fits with margin.

In space-game-prototype, `tools/construction/import_ship_kit.py` copies the kit in. The kit is a `ConstructionKit` resource (pieces scene, plan, finished scene) on the carrier's `Shipyard`; `scripts/construction/` holds the generic code. The finished scene must be the same hull in the same frame. Keep the kit's interiors flush and inside the hull: the game swaps the kit for the finished ship in place.

## Capital ships

The same rules scale. Expect roughly 300-500 pieces for a 100 m hull at a 3.4 m ring pitch; 6-8 bands per half-ring on a tall hull is normal (`BAND_TAGS` falls back to numbered bands). Things that change:

- **Build time.** One bay takes about 9.6 s per piece, so 500 pieces is about 80 minutes. Plan for both bays (port pieces fly round the mothership) or a separate drone-recovery dock. Model that in `animate_build.py` as a second bay with its own markers and `bay_free`.
- **Structure first.** The keel and the procedural truss can grow into ribs or a reusable shipyard gantry (`build_keel.py`'s `strut()` builds any lattice). For a capital ship, build the gantry and spine first, then hang the rings in it.
- **Pieces over the limit.** Two drones in tandem could carry pieces over the "along" limit, but only if the bay is redefined to fit both. Re-derive the envelope and change `TRANSIT_ENVELOPE` in one place; `hangar_fit.py` re-checks it.

## Files to touch per ship

| Script | Change |
| --- | --- |
| `build_kit.py` | `SRC`, `SECTIONS`, `KEEL_AXIS_Z`, `CHANNEL`. `TRANSIT_ENVELOPE` only if the hangar changes |
| `build_keel.py` | `KEEL_SPLITS`, `KEEL_Z`; truss size `HALF` if the hull is small |
| `make_kit.py` | output file name (also `frigate_kit.blend` in `interior_*`, `hangar_fit.py`, `render_kit.py` and the headless command lines) |
| `interior_layout.py` | `DECK_Z0`, `RIM`, `JOINT`, fit-out mix; `split_sides()` relies on the P/S and L/M/U piece tags |
| `interior_build.py` | `CH`: a copy of `build_kit.CHANNEL` and `KEEL_AXIS_Z`, which must match them |
| `make_hull_pools.py` | the source atlas, label map and UV mask copies |
| `animate_build.py` | `SITE`, `R_ARC`, `R_RET`, `Y_LANE`, `N_DRONES`, `TIMELAPSE`; the hidden source object name |
| `hangar_fit.py`, `check_collisions.py`, `render_*.py` | `ROOT` and file names only |
| every script | `ROOT` at the top |
