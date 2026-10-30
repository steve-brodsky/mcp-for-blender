class_name FleetPaintBaker
extends Node
## Attach one instance to a loading/menu scene. Bake selected pairs before combat.
## Inputs are imported lossless source/mask textures, not the recolored preset PNGs.

signal bake_finished(key: String, result: Texture2D)
const COMPOSITOR = preload("compose_paint.gdshader")
var _cache: Dictionary = {}
var _pending: Dictionary = {}
var _disk_cache_dir := "user://fleet_paint_cache"

func bake(source: Texture2D, mask: Texture2D, hull_srgb: Color, detail_srgb: Color,
        normalization: Vector2, recipe_key: String, disk_cache := true, max_dimension := 2048) -> Texture2D:
    assert(is_inside_tree(), "FleetPaintBaker must be attached to the scene tree.")
    assert(source != null and mask != null and source.get_size() == mask.get_size())
    assert(normalization.x > 0.0 and normalization.y > 0.0)
    var target_size := Vector2i(source.get_size())
    if max_dimension > 0 and maxi(target_size.x,target_size.y) > max_dimension:
        target_size = Vector2i(Vector2(target_size) * float(max_dimension) / float(maxi(target_size.x,target_size.y)))
        target_size.x = maxi(target_size.x,1)
        target_size.y = maxi(target_size.y,1)
    var key := (recipe_key + ":" + str(target_size)).sha256_text()
    if _cache.has(key): return _cache[key]
    if _pending.has(key):
        while _pending.has(key): await bake_finished
        return _cache.get(key)
    _pending[key] = true
    var cache_path := _disk_cache_dir.path_join(key + ".png")
    if disk_cache and FileAccess.file_exists(cache_path):
        var cached := Image.load_from_file(cache_path)
        if cached != null and not cached.is_empty() and cached.get_size() == target_size:
            return _finish(key, cached)

    var viewport := SubViewport.new()
    viewport.size = target_size
    viewport.disable_3d = true
    viewport.transparent_bg = true
    viewport.use_hdr_2d = false
    viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
    var rect := ColorRect.new()
    rect.size = Vector2(target_size)
    var material := ShaderMaterial.new()
    material.shader = COMPOSITOR
    material.set_shader_parameter("source_albedo", source)
    material.set_shader_parameter("paint_mask", mask)
    material.set_shader_parameter("hull_srgb", Vector4(hull_srgb.r, hull_srgb.g, hull_srgb.b, hull_srgb.a))
    material.set_shader_parameter("detail_srgb", Vector4(detail_srgb.r, detail_srgb.g, detail_srgb.b, detail_srgb.a))
    material.set_shader_parameter("normalization", normalization)
    rect.material = material
    viewport.add_child(rect)
    add_child(viewport)
    await RenderingServer.frame_post_draw
    var image := viewport.get_texture().get_image()
    viewport.queue_free()
    if image == null or image.is_empty():
        _pending.erase(key)
        bake_finished.emit(key, null)
        push_error("Fleet paint bake failed: " + recipe_key)
        return null
    image.convert(Image.FORMAT_RGBA8)
    if disk_cache:
        var directory_error := DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(_disk_cache_dir))
        if directory_error == OK:
            var save_error := image.save_png(cache_path)
            if save_error != OK: push_warning("Fleet paint disk cache could not be saved.")
    return _finish(key, image)

func _finish(key: String, image: Image) -> Texture2D:
    image.generate_mipmaps()
    var texture := ImageTexture.create_from_image(image)
    _cache[key] = texture
    _pending.erase(key)
    bake_finished.emit(key, texture)
    return texture

func clear_memory_cache() -> void:
    _cache.clear()
