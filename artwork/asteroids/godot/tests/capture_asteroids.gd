extends SceneTree

func _initialize() -> void:
	call_deferred("capture")

func capture() -> void:
	DirAccess.make_dir_recursive_absolute("res://captures/asteroids")
	root.size = Vector2i(1600,1000)
	var gallery = load("res://scenes/environment/asteroids/asteroid_gallery.tscn").instantiate()
	root.add_child(gallery)
	await process_frame
	for level in range(3):
		gallery.set_level(level)
		for frame in range(12): await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://captures/asteroids/godot_gallery_lod%d.png" % level)
	gallery.set_level(0)
	# Review the reverse side with labels hidden.
	for child in gallery.get_node("Collection").get_children():
		if child is Label3D:child.visible=false
	gallery.yaw=PI
	gallery.update_camera()
	for frame in range(12): await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://captures/asteroids/godot_gallery_back.png")
	print("Captured all three mesh levels and reverse sides")
	gallery.queue_free()
	await process_frame
	await process_frame
	quit()
