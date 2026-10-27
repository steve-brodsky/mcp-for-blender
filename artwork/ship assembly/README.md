# Ship assembly: building frigates from hangar-sized kits

An exploration of how frigates and capital ships could be built in space by construction drones, each piece carried out of the mothership's hangar. The beam frigate is the worked example. It has been cut into a **74-piece kit**: 70 hull pieces and 4 keel truss segments. Every piece passes through the real hangar opening with a construction drone towing it, and the pieces reassemble into the exact original hull.

To kit another ship, follow [SHIP_KIT_GUIDE.md](SHIP_KIT_GUIDE.md).

Everything here was made from copies in `source/`. The beam frigate, construction drone, mothership and `space-game-prototype` folders were only read.

![Build stages, seen from the bow](renders/stages_sheet.png)

## The constraint

The game runs the mothership, the beam frigate and the small craft at these sizes:

| Unit | Game size |
| --- | --- |
| Mothership | 98 m long |
| Beam frigate (unit scale) | 47.4 x 20.1 x 17.2 m |
| Hangar forcefield opening | 10.8 m wide x 4.2 m tall |
| Bay depth, back wall to forcefield | 12.1 m |
| Construction drone (0.25 scale, like the supply drone) | 4.0 x 2.9 x 1.5 m |

The frigate can never leave a hangar whole, nor can any of its natural modules: the midship section alone is 20 m wide. So the hull has to come out as a kit. A piece leaves the bay **thin side down, long side across the opening, towed in line ahead of its drone**, which gives a **transit envelope of 10.2 x 7.4 x 3.6 m**:

- **Across, 10.2 m:** the 10.8 m opening less a 0.3 m margin each side.
- **Along, 7.4 m:** the 12.1 m bay depth less the 4.0 m drone and 0.6 m of gaps.
- **Height, 3.6 m:** the 4.2 m field less a 0.15 m ride height and top clearance.

A drone riding on top of a piece doesn't work: a 3.2 m piece plus a 1.5 m drone is taller than the opening.

![Widest hull piece in transit pose in the starboard bay, drone docked behind it](renders/hangar_fit_cutaway.png)

## How the frigate is cut

![Exploded kit](renders/kit_exploded.png)

1. **Rings.** The hull is sliced across its length into 16 rings, 2.8-3.2 m thick, so a ring's thickness becomes a piece's height in transit. I measured the cross-section area along the hull (`reports/section_profile.json`) and kept its waists as ring boundaries, at Y = -12.5, +0.25 and +14.5. Those are the joins between the stern block, midship, forward armour and bow neck.
2. **Port and starboard.** Each ring is split at the centreline, so the kit is mirrored.
3. **Bands.** Each half is cut into as few horizontal bands as fit: lower, middle and upper. Bands are better than inboard/outboard columns, because a band's drone grips its top or bottom face, which is open space. With columns, the inboard piece's drone sat in the outboard piece's slot while it welded.
4. **Keel channel.** A 2.2 m square channel runs through the hull for the keel truss (Y -18 to +20). It is completely enclosed (0.0 m³ outside the hull), so it is invisible on the finished ship. During the build it shows in each bulkhead, and the middle bands clamp onto the keel from both sides. Band cuts keep 0.15 m clear of the channel, so every piece carrying the keel has a full notch.
5. **Open-block interiors (3D).** While the hull is open, the bow-facing cut face of every piece shows the inside of a hull block under construction, built as real geometry, not a painted texture: a flat image has no depth and reads as a poster once the camera moves. Each open face gets:
   - **A cavity, 1.2 m deep.** A 0.4 m armour rim stands along the hull skin; block joints at split planes get only a 0.15 m frame.
   - **Deck slabs** on the ship-wide 3 m deck grid (floors at z = -1 + 3k), with hazard-striped edges. About one deck run in six is still unplated, with only its girders in place.
   - **Structure:** longitudinal girders under every deck, seen end-on, plus pillars and partition walls with frame edges.
   - **Fit-out:** pipe runs, ducts and cable trays cut flush with the face; machinery blocks, tanks and service cabinets in about three bays in four; yellow scaffolding in some bays; small work lights.

   Everything is surfaced with tileable textures quilted from the frigate's own albedo atlas (`textures/pool_*.png`), so the interior has the hull's soft, grimy grain. The values follow a cutaway: dark primer cavity walls, light ivory structure, gunmetal decks and machinery. Every other cut face (rims, block joints, keel channel, the stern-facing faces) is the hull's gunmetal grain.

   Each cavity is shaped by the intersection of the piece's cross-sections at 0-1.2 m behind the face, so it follows the hull where it narrows toward a waist. A probe then confirms the cavity lies wholly inside the piece, which is checked for all 62 cavities (`reports/interiors.json`). No cavity can open a hole in the finished hull, and the next ring's flat stern-side face closes each one off. The interiors add about 69k triangles while the ship is under construction (kit 206k in all).

   ![Mid-build: the open block face](renders/stage_050.png)

| | |
| --- | --- |
| Hull pieces | 70: four per ring at the stern and bow, six on the tall midship rings, two whole rings at the bow |
| Keel segments | 4 x 9.5 m procedural lattice truss in construction orange, also within the envelope |
| Largest piece in transit | 10.05 x 7.36 x 3.19 m (envelope 10.2 x 7.4 x 3.6) |
| Hull volume | 5494.92 m³ = source 5679.31 less channel 184.4 (closed shells, no boundary edges) |
| Triangles | 206,270 for the whole kit with interiors (137,520 without; source 93,734) |

The plan for every piece is in `reports/kit_pieces.json`:

- name, ring, assembled centre and dimensions;
- transit quaternion and transit dimensions;
- approach direction and staging point;
- build order, triangle count and shell checks.

`reports/hangar_fit.json` re-tests every piece against the opening and the bay depth with the drone docked behind it. All 74 fit; the tightest has 0.38 m of side clearance.

## How it is assembled

Build order:

1. **Keel.** The four keel segments go down first, slid in sideways from the mothership side.
2. **Rings.** Rings follow from stern to bow. Each ring goes bottom up, port before starboard.
3. **Bow.** The bow rings, with the spinal beam emitter, close the hull last.

The ship appears to grow forward along its own spine.

![Mid-build](renders/stage_050.png)

`blender/frigate_build_anim.blend` animates the whole build with 10 drones from the starboard hangar, at five game seconds per video second (`scripts/animate_build.py`). Each trip:

1. **Issue.** A drone docks at the back of the bay facing out. The next piece is issued in front of it, already in its transit pose.
2. **Exit.** The pair leave at 6 m/s. The bay is released only once the drone has also cleared the return queue.
3. **Approach.** In open space the piece turns to its final orientation. It flies to the near side of the build site, then around the keel axis on a 24 m ring, in a lane 10 m ahead of its own ring on the unbuilt side, to its bearing. It then drops back into its ring plane. Departing drones stay in the ring plane, so the two flows never share a plane.
4. **Seat.** The piece waits at a staging point clear of its neighbours: its own extent along the approach plus 2 m, 4.8-13.1 m out. It then slides home at 2.5 m/s. The drone grips the face that ends up outward, so it is never inside the hull. Keel-carrying bands slide in square to the keel; otherwise the drone takes the top face, because the slot above is still empty.
5. **Weld.** Two seconds, the cue for the drone's `stitch_weld` clip and torch effects.
6. **Return.** The drone backs off and returns over the top on a 40 m ring. A piece and its drone reach about 11 m beyond the arrival ring, so the two rings must stay that far apart. It then joins a queue line beside the hull above the opening, and drops below the line to re-enter when the bay is free.

`reports/build_schedule.json` has every trip:

- **Build time:** about 710 s (12 min) of game time from one bay, a mean of 9.6 s per piece.
- **Trips:** 25-38 s per round trip. In practice five drones do nearly all the work.
- **Bottleneck:** the bay, not the drones. Each piece costs about 3 s for the outgoing pair to clear the field, plus about 4 s for a returning drone to re-enter and turn around. Adding drones barely helps; adding bays does.

`scripts/check_collisions.py` sweeps the animation every 3 frames with triangle-BVH overlap:

- every flying piece and drone against every seated piece;
- the mothership hull;
- each other.

Moving objects are tested shrunk by 3 cm, so flush cut faces sliding past each other don't count. `reports/collisions.json` holds the result.

## Game design notes and options

- **Build time is a tuning dial.** One bay gives about 12 minutes for a frigate. Both bays roughly halve it, but port-bay drones have to fly round the mothership. Faster bay transit also helps, and so does recovering drones through a separate dock so the launch bay never takes returns. A "construction bay" or "shipyard tug" research upgrade could change those numbers.
- **Progress is visible and interruptible.** The ship visibly grows stern to bow. A half-built hull is a natural target: destroyed pieces could fall off and be re-issued. Open faces show block interiors, so a damaged or partial ship still looks deliberate.
- **Capital ships.** Use the same rule at a larger scale: a ring pitch of at most 3.4 m and pieces within 10.2 x 7.4 x 3.6 m. A 100 m capital ship would be roughly 300-500 pieces, a long build that justifies dedicated construction tugs or a shipyard.
  - **Shipyard.** The keel-truss idea could be built out of the same kit parts into a reusable gantry beside the mothership, then grow a hull inside it.
  - **Spine.** For capital ships, a truss spine with ribs, built first from many small truss pieces, makes a strong visual. The hull rings can then be heavier pieces carried by two drones in tandem: one tows and one steadies.
- **Two kinds of geometry.** Hull pieces are cut from the real ship, so the finished ship looks exactly like the original. Structure (keel, ribs, gantries) is procedural, cheap and reusable for any hull. Any ship can be kitted the same way: run `build_kit.py` against a different source with its own station list.
- **Interior lights.** The work lights have an emission material (`Int_WorkLight`, strength 4), so in Godot the open block glows faintly. Workbench previews don't show emission. Short-range OmniLights at a few work-light positions would add pools of light in the cavities, for a handful of lights per open face.
- **In-engine.** Assemble the pieces under one node at the frigate's transform. When the last piece is seated, swap the whole kit for the normal `beam_frigate.tscn`: one mesh, LODs and collision, same pose, no visual pop. The mirrored pairs could share one mesh with a negative X scale on the MeshInstance to halve kit memory.

## Files

| File | Purpose |
| --- | --- |
| `source/*_COPY.*` | Copies of the beam frigate game-ready blend, the construction drone GLB and the mothership GLB (from the prototype's assets) |
| `blender/frigate_kit.blend` | The kit: every piece at its assembled position, origin at its bounds centre, `kit_order` property, the keel truss |
| `blender/frigate_build_anim.blend` | The build animation, with the mothership copy, 10 drones and cameras `Cam_Wide` and `Cam_Site` |
| `blender/hangar_fit.blend` | The widest hull piece and a docked drone in the starboard bay (roof removed on the copy) |
| `textures/pool_*.png` | Tileable 8 m surface textures quilted from the frigate's albedo atlas: graphite, gunmetal, armour ivory, primer, four pipe paints, hazard stripe (`scripts/make_hull_pools.py`) |
| `source/beam_frigate_{basecolor_4k,texel_labels,uv_mask}_COPY.png` | Copies of the frigate's albedo atlas, paint-class map and UV mask, the quilting source |
| `renders/` | Kit, stage and hangar-fit stills. `frigate_build.mp4` is the build video (local only, gitignored) |
| `reports/` | Section profile, kit plan, hangar fit, build schedule and collision sweep |

`renders/src_*.png` and `seg_explode_*.png` are from the first attempt: four whole-section modules, before the hangar limit was applied.

## Rebuilding

Scripts declare the workspace path at their start. Blender 5.1. Every boolean uses the MANIFOLD solver: on this hull, EXACT without self-intersection returned empty or near-whole results.

1. `python scripts/make_hull_pools.py`. To re-derive the ring boundaries, exec `scripts/section_profile.py` with the source copy open.
2. Open `source/beam_frigate_game_ready_COPY.blend` (in its own MCP call), then exec `scripts/make_kit.py` and `scripts/interior_export.py`. `make_kit.py` runs `build_kit.py` and `build_keel.py`, writes `reports/kit_pieces.json` and saves `blender/frigate_kit.blend`.
3. `python scripts/interior_layout.py`, then, in the same Blender session, exec `scripts/interior_build.py`. This cuts the cavities, builds the interiors and saves the kit.
4. `blender -b -P scripts/hangar_fit.py`.
5. `blender -b blender/frigate_kit.blend -P scripts/animate_build.py`.
6. `blender -b blender/frigate_build_anim.blend --python-expr "STEP=3; exec(open(r'...\scripts\check_collisions.py').read())"`.
7. `blender -b blender/frigate_build_anim.blend -P scripts/render_video.py`.
8. For the game, run `blender -b blender/frigate_kit.blend -P scripts/export_kit.py`. This writes `godot_export/beam_frigate_kit.glb` and `beam_frigate_kit_plan.json`. In space-game-prototype, `tools/construction/import_ship_kit.py` copies them in; see that project's `docs/ship_construction.md`. Stills: exec `scripts/render_kit.py` with the kit open, or `scripts/anim_stills.py` with the animation open.

Renders use Workbench (textured), because EEVEE previews render blank on this machine. The mothership's texture smears in Workbench; it looks correct in Godot.
