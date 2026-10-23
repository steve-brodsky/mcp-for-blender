# Symmetry revision texture cleanup

Tool: built-in imagegen edit.

Input: `atlas_cleanup_input_4k.png`, a resized copy of the previous baked atlas.
Output: `../hull_clean_atlas.png`, actual resolution 1254 x 1254.
The initial 8K input was rejected by the tool; the resized input succeeded.

Exact final prompt:

Edit this spacecraft UV TEXTURE ATLAS in place. This is a technical game texture, not a render: preserve exact square atlas registration, all UV islands, shapes, orientations and black empty spaces with NO shifting or relayout. Clean the existing warm ivory armor and solid red stripes: remove scratches, speckles, blotchy grime, dirty chipped edges and baked rippled/bumpy shading. Replace with smooth factory-painted ivory surfaces, crisp solid red markings and fine subtle grey panel seams. Clean dark graphite machinery and copper details while retaining vents and visible component structure. Keep exact existing colors and mechanical design. No new details, no text, no border, no added objects, no scene background, no lighting effects. Do not symmetrize the atlas. Highest practical square resolution, ideally 4096 x 4096.

Blender applies this albedo with uniform roughness 0.68 and metallic 0.12.
The previous reconstruction split normals were cleared and no normal/bump map is used.
