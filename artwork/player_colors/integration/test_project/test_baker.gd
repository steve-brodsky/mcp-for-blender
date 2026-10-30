extends SceneTree

func _initialize() -> void:call_deferred("run")

func run() -> void:
    var script = load("res://fleet_paint_baker.gd")
    if script == null:
        push_error("Baker script failed to parse.")
        quit(1)
        return
    var baker = script.new()
    root.add_child(baker)
    var palette_path := ProjectSettings.globalize_path("res://").path_join("../palette.json")
    var palette: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(palette_path))
    var source := Image.create(8,8,false,Image.FORMAT_RGBA8)
    var mask := Image.create(8,8,false,Image.FORMAT_RGBA8)
    for x in range(8):
        for y in range(8):
            source.set_pixel(x,y,Color((x+2.0)/10.0,(y+2.0)/10.0,0.3,0.5 if y==7 else 1.0))
            mask.set_pixel(x,y,Color(1,0,0,1) if x<3 else (Color(0,1,0,1) if x<6 else Color(0,0,0,1)))
    source.save_png("res://test_project/source.png")
    mask.save_png("res://test_project/mask.png")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://test_project/results"))
    var source_texture := ImageTexture.create_from_image(source)
    var mask_texture := ImageTexture.create_from_image(mask)
    var checked := 0
    for hull: String in palette.hull_colors:
        for detail: String in palette.detail_colors:
            var hc := Color.html(palette.hull_colors[hull].srgb)
            var dc := Color.html(palette.detail_colors[detail].srgb)
            var recipe := "synthetic-v2:" + hull + ":" + detail + ":" + JSON.stringify(palette).sha256_text()
            var result: Texture2D = await baker.bake(source_texture,mask_texture,hc,dc,Vector2(0.72,0.245),recipe,false)
            assert(result != null)
            var image := result.get_image()
            image.clear_mipmaps()
            image.save_png("res://test_project/results/"+hull+"__"+detail+".png")
            var cached: Texture2D = await baker.bake(source_texture,mask_texture,hc,dc,Vector2(0.72,0.245),recipe,false)
            assert(cached == result)
            checked += 1
    var disk_key := "disk-test-v2:" + JSON.stringify(palette).sha256_text()
    var disk_first: Texture2D = await baker.bake(source_texture,mask_texture,Color.WHITE,Color.BLACK,Vector2(0.72,0.245),disk_key,true)
    baker.clear_memory_cache()
    var disk_second: Texture2D = await baker.bake(source_texture,mask_texture,Color.WHITE,Color.BLACK,Vector2(0.72,0.245),disk_key,true)
    assert(disk_first.get_image().get_data() == disk_second.get_image().get_data())
    var reduced: Texture2D = await baker.bake(source_texture,mask_texture,Color.WHITE,Color.BLACK,Vector2(0.72,0.245),disk_key,false,4)
    assert(reduced.get_size() == Vector2(4,4))
    assert(reduced != disk_first)
    print("GODOT_BAKER_COMPLETE ",checked," pairs; memory and disk cache checked")
    quit(0)
