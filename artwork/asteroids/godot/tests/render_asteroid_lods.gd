extends SceneTree
## GPU check: verify the renderer draws exactly one intended mesh at each distance.
var failures: Array[String] = []
var measurements: Array[Dictionary] = []

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	DirAccess.make_dir_recursive_absolute("res://captures/asteroids")
	root.size = Vector2i(1000,800)
	var stage = Node3D.new()
	root.add_child(stage)
	var camera = Camera3D.new()
	camera.current = true
	camera.fov = 42
	camera.far = 5000
	stage.add_child(camera)
	var environment = WorldEnvironment.new()
	var env = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(.014,.021,.031)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(.8,.83,.87)
	env.ambient_light_energy = .35
	environment.environment = env
	stage.add_child(environment)
	var key = DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-32,-35,0)
	key.light_energy = 1.3
	stage.add_child(key)
	var catalog = JSON.parse_string(FileAccess.get_file_as_string("res://assets/environment/asteroids/catalog.json"))
	for asset in catalog:
		var asteroid = load("res://scenes/environment/asteroids/" + asset.id + ".tscn").instantiate()
		stage.add_child(asteroid)
		var distances = [asset.lod_distances[0]*.6,(asset.lod_distances[0]+asset.lod_distances[1])*.5,asset.lod_distances[1]*1.3]
		for level in range(3):
			camera.position = Vector3(0,0,distances[level])
			for frame in range(5):await process_frame
			await RenderingServer.frame_post_draw
			var triangles = root.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_PRIMITIVES_IN_FRAME)
			var objects = root.get_render_info(Viewport.RENDER_INFO_TYPE_VISIBLE,Viewport.RENDER_INFO_OBJECTS_IN_FRAME)
			var expected: int = asset.lod_triangles[level]
			measurements.append({"asset":asset.id,"level":level,"distance":distances[level],"rendered_triangles":triangles,"expected_triangles":expected,"rendered_objects":objects})
			if triangles != expected or objects != 1:
				failures.append("%s LOD%d drew %d triangles / %d objects; expected %d / 1" % [asset.id,level,triangles,objects,expected])
		if asset.id in ["asteroid_01","asteroid_09","asteroid_13","asteroid_16","asteroid_27"]:
			camera.position = Vector3(0,asset.dimensions_godot.max()*.15,asset.dimensions_godot.max()*1.3)
			camera.look_at(Vector3.ZERO)
			for frame in range(5):await process_frame
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png("res://captures/asteroids/godot_" + asset.id + "_close.png")
			camera.rotation = Vector3.ZERO
		asteroid.queue_free()
		await process_frame
	var report = {"passed":failures.is_empty(),"checks":measurements.size(),"failures":failures,"measurements":measurements,"renderer":ProjectSettings.get_setting("rendering/renderer/rendering_method","forward_plus")}
	FileAccess.open("res://captures/asteroids/render_lod_validation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print("Rendered LOD checks: %d; failures: %d" % [measurements.size(),failures.size()])
	for failure in failures:push_error(failure)
	stage.queue_free()
	await process_frame
	await process_frame
	quit(0 if failures.is_empty() else 1)
