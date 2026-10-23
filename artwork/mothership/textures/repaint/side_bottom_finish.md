# Side and underside finish

The existing starboard repaint is projected onto both mirrored sides. The underside
uses a registered projection painted from `bottom_guide.png`, with `top_repaint.png`
as the style reference. Tool: built-in imagegen edit. The result is
`bottom_repaint.png`; it is a projection source, never a replacement for a UV atlas.

The accepted top and cannon finish are sampled from the frozen
`../hull_top_accepted_8k.png`. The combined material is authored in Blender and baked
to the existing `UV_SURFACE_FINISH`, preserving hull and hangar positions.

Exact imagegen prompt:

Use case: precise-object-edit. Asset: detailed orthographic underside paint projection for an existing spacecraft game model. Image 1 is the EDIT TARGET and exact geometry/layout guide: spacecraft underside, nose pointing RIGHT, engines LEFT, centered horizontally in a 2:1 canvas. Image 2 is ONLY the approved TOP paint style reference. Repaint only the underside shown in image 1, retaining EXACT silhouette, overall placement, scale, framing, component positions, panel forms, engine positions, central mechanical spine, underside grilles and all visible hardware. Do NOT copy the top layout onto the underside. Match the approved top's detailed warm ivory armor, red identification stripes, charcoal/steel machinery and restrained copper mechanical accents. Replace the melted smeary surface drawing with crisp manufactured plating seams, finely delineated vents, fasteners and believable machinery, and straighten the existing red identification bands into clean angular lines at their original locations. Keep detailed moderate edge weathering matching image 2; avoid a simplified flat grid or a plain repainted hull. Left/right sides of underside should be bilaterally symmetric. Keep forward outer cannon casings ivory with dark steel barrels. This is a BASE COLOR projection texture: flat even illumination, no directional shadows, no specular reflections or extra painted relief bumps. Keep the same dark navy background and exact 2:1 registration; no cropping, perspective tilt, new geometry, added wings/weapons, letters, labels, borders or watermark. Produce a sharp 2048x1024 landscape image if practical.
