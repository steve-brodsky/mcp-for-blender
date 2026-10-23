# Medieval watchtower optimization report

Completed in the connected Blender 5.1.0 application using Blender MCP. The original medieval_watchtower.blend was not overwritten. The new project is medieval_watchtower_optimized.blend; export is medieval_watchtower_game.glb.

The asset comparison excludes presentation scenery, camera and lighting on both sides. A separate unoptimized, asset-only GLB was exported to establish the file-size baseline.

| Measurement | Source asset | Game asset |
|---|---:|---:|
| Tower mesh objects | 519 | 6 |
| Evaluated/exported triangles | 16,980 | 14,842 |
| Materials used by asset | 14 | 14 |
| Modifier instances | 848 | 0 |
| glTF primitives / material surfaces | 519 | 25 |
| Exported vertices | 24,648 | 31,854 |
| GLB size (bytes) | 1,145,212 | 1,125,104 |

Objects decreased by 98.84%, triangles by 12.59%, and GLB size by 1.76%. Material surfaces decreased from 519 to 25. Surfaces are a submission-cost indicator, not a measured Godot draw-call count; actual passes and rendering settings affect that count. The principal gain is scene/submission overhead. Exported vertex count increased because the reconstructed meshes retain split/custom normals and explicit UV0 data. This limits binary-size savings; no compression or LOD simplification was used.

The full original scene contained 535 objects (531 meshes, one camera, three lights), 17,380 evaluated triangles, 858 modifiers, and 18 material datablocks. Fourteen materials are assigned to the tower, three to presentation scenery, and one is unused. The new project deliberately contains 547 objects: 519 source meshes, six game meshes, six validation re-import meshes, and 16 presentation objects. The exported GLB contains only the six game meshes.

| Architectural component | Source objects | Source evaluated triangles | Source modifiers | Game objects | Game triangles | Material surfaces |
|---|---:|---:|---:|---:|---:|---:|
| Foundation | 6 | 264 | 12 | 1 | 244 | 3 |
| Masonry | 225 | 9,900 | 450 | 1 | 8,874 | 5 |
| Doorway | 22 | 1,044 | 42 | 1 | 1,004 | 3 |
| Windows | 16 | 704 | 32 | 1 | 704 | 2 |
| Lookout | 57 | 2,508 | 114 | 1 | 1,640 | 6 |
| Roof | 193 | 2,560 | 198 | 1 | 2,376 | 6 |

Foundation includes the stone cornice and entrance steps. Windows include sills, lintels and iron bars; doorway includes jambs, door boards and hardware. The excluded set contains 12 meshes: studio floor, earth island, grass surface, four rocks and five path stones. Camera and three lights are also excluded.

Material assignments were retained, including all limestone and cedar color variants. All asset materials use constant Principled BSDF color and roughness (0.8); forged iron has metallic 0.65, and the other asset materials have metallic 0. There are no external image textures to bake or package.

| Material | Source objects using it |
|---|---:|
| Cedar 0 | 42 |
| Cedar 1 | 39 |
| Cedar 2 | 32 |
| Cedar 3 | 39 |
| Cedar 4 | 40 |
| Dark oak | 58 |
| Door oak | 6 |
| Dressed sandstone | 19 |
| Forged iron | 15 |
| Limestone 0 | 50 |
| Limestone 1 | 39 |
| Limestone 2 | 44 |
| Limestone 3 | 51 |
| Limestone 4 | 45 |

The tower had 334 Bevel, 334 Weighted Normal and 180 Solidify modifiers (848 total). Base geometry had 4,492 triangles; evaluated geometry had 16,980. Modifier evaluation therefore expanded triangle count by about 3.78 times. Bevels and shingle thickness were baked only on the game derivative; their visible forms and weighted normals were retained. Source modifiers remain editable.

No original mesh datablocks were shared between objects. The 225 masonry blocks fall into six repeated local-geometry profiles (151, 40, 16, 8, 6 and 4 blocks). Jambs, boards, straps, rivets, sills, bars, floor planks, posts, braces, rails and roof trim also repeat. Linked meshes or material-specific instancing are opportunities for a modular construction kit. The source was kept independent and editable; for this single assembled static asset, batching by architectural component and material reduces node overhead more directly.

There were 184 meshes without UVs: 180 shingles and four roof backing faces. Existing evaluated UV0 was retained elsewhere; box-projected UV0 was added where absent. All six exported and re-imported meshes now have UV0. Some UV islands overlap, so this is not a lightmap atlas or a final unique texture-paint unwrap. Generate UV2 on Godot import if using baked lightmaps.

There were 239 scene meshes with nonzero object rotation, including 234 tower meshes and five excluded path stones. The only non-unit scales were on the four excluded rocks. Nonzero rotation is not inherently an export error, but all game geometry is baked into mesh coordinates and every game object has identity transforms. All six mesh origins are at (0,0,0), centered on the tower axis. The copies were shifted downward by 0.0600000024 Blender units so the foundation rests at Z=0. Scale and proportions are unchanged. The asset is approximately 6.07 m wide, 6.275 m deep including the steps, and 10.10 m tall. Blender Z-up is converted to glTF/Godot Y-up.

Safe cleanup removed 1,894 triangles whose three vertices lie strictly inside another closed convex solid, plus 244 zero/near-zero-area evaluated triangles. Convex half-space tests ensure each removed triangle is entirely enclosed. No visible bevels, masonry seams, railing pieces or roof shingles were decimated. Remaining intersecting/internal faces were retained when enclosure was not proven. The game geometry is a static visual mesh, not a watertight collision solid.

SOURCE_WATCHTOWER contains six named architectural subcollections and the 519 original editable objects. Object names have component prefixes and retain source_original_name metadata. GAME_WATCHTOWER contains six baked meshes, each with material-separated surfaces. PRESENTATION_NOT_EXPORTED preserves the stage, camera and lighting. VALIDATION_GLB_REIMPORT contains the six roundtrip meshes and is hidden.

Source integrity was checked against linked objects from the original file: 519 objects matched with 0 differences in original vertices, polygons, smooth flags, UVs, material slots/indices, local transforms and editable modifier settings. Object names/organization and added metadata were intentionally changed. Original file SHA-256: 5c7b96690429ae50da7729cc4ae28f23ae389f1312e27b8a266c49cd9e6b8dc3.

The GLB was exported with mesh selection only, normals, UV0, PBR materials, Y-up conversion, and no animation, camera or lights. It uses no glTF extensions, external buffers or external textures. Binary checks verified valid accessor indices, finite geometry/normals, normalized normals, and no zero-area exported triangles. Blender re-import verified six meshes, 14 materials, 14,842 triangles, UVs on every mesh, matching bounds, and matching PBR color/roughness/metallic factors. Imported Blender bounds are (-3.035, -3.240, 0.000) to (3.035, 3.035, 10.100).

Source and game versions were rendered from the same front and rear cameras with the same Cycles CPU lighting, sample seed, 48 samples, and stage. Game meshes were temporarily aligned upward by 0.06 m for comparison, then restored to their ground-centered export placement. The re-imported GLB was also rendered from the front. Blender MCP visual inspection found no visible missing parts, shading defects or color changes. Comparisons are near-identical, not bit-identical, due to triangulation/custom-normal encoding and render sampling.

| Render comparison | Mean absolute normalized RGB difference | RMS difference |
|---|---:|---:|
| front_source_game | 0.00003540 | 0.00058964 |
| front_game_roundtrip | 0.00001785 | 0.00027677 |
| rear_source_game | 0.00003913 | 0.00058969 |

Evidence images: [source front](watchtower_compare_source.png), [game front](watchtower_compare_game.png), [GLB roundtrip front](watchtower_compare_reimport.png), [source rear](watchtower_back_source.png), [game rear](watchtower_back_game.png), and [final asset without presentation island](watchtower_game_final.png).

Blender encountered native crashes during the early custom-normal/material-copy attempts. Work resumed from separate saved checkpoints; final meshes use validated topology, the supported vertex-normal assignment path, and original material datablocks resolved by name. The final build, export, re-import and render checks completed successfully.

Godot itself was not run as part of validation. Import the GLB using the [Godot 4 glTF scene workflow](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html). No gameplay collision, LOD chain, navigation mesh or lightmap UV2 is supplied. The closed doorway remains static with the original visual design; it is not an animated door asset. Whole-tower instancing can reuse the imported scene. Separate architectural meshes permit part-level culling but still have 25 material surfaces. Further draw-call reduction would require a material/vertex-color atlas or more aggressive batching; no such appearance-sensitive conversion was made.

The [Blender glTF documentation](https://docs.blender.org/manual/en/3.6/addons/import_export/scene_gltf2.html) explains export of PBR materials/normals and vertex splitting at UV discontinuities and flat-shaded boundaries. UV and normal splits are retained where needed for appearance.
