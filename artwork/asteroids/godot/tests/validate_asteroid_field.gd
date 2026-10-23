extends SceneTree

var checks := 0
var failures: Array[String] = []

func check(condition: bool, description: String) -> void:
	checks += 1
	if not condition:
		failures.append(description)
		push_error(description)

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var world = load("res://scenes/main.tscn").instantiate()
	root.add_child(world)
	current_scene = world
	await physics_frame
	await physics_frame
	var field = world.get_node("AsteroidField")
	var rocks = field.get_children()
	check(rocks.size() == 112,"Main scene includes 112 asteroids")
	var shapes := {}
	var transforms: Array[Transform3D] = []
	for i in range(rocks.size()):
		var rock = rocks[i]
		check(rock is AnimatableBody3D and rock.sync_to_physics,"Spin uses synchronized physics body")
		shapes[rock.get_meta("source_scene")] = true
		var diameter: float = rock.get_meta("diameter_m")
		check(diameter >= 4 and diameter <= 42,"Random diameter in range")
		check(rock.scale.x > 0 and rock.scale.is_equal_approx(Vector3.ONE*rock.scale.x),"Uniform positive scale")
		check(rock.position.length() - rock.get_meta("clearance_radius_m") >= 95,"Mothership spawn clearance")
		check(is_equal_approx(rock.get_meta("spin_axis").length(),1.0) and rock.get_meta("spin_radians_per_second")>0,"Valid arbitrary spin axis and speed")
		check(rock.get_node("Collision").shape is ConvexPolygonShape3D,"Physics collider retained")
		for lod in range(3):
			check(rock.get_node("LOD%d" % lod).mesh != null,"LOD resource retained")
		for j in range(i):
			check(rock.position.distance_to(rocks[j].position) >= rock.get_meta("clearance_radius_m") + rocks[j].get_meta("clearance_radius_m") + 7.99,"Spin envelopes stay separated")
		transforms.append(rock.transform)
	check(shapes.size()==28,"All 28 asteroid shapes represented")
	for frame in range(35):await physics_frame
	for i in range(rocks.size()):
		var rock = rocks[i]
		check(rock.position.is_equal_approx(transforms[i].origin),"Spin preserves position")
		check(not rock.basis.is_equal_approx(transforms[i].basis),"Asteroid spins at runtime")
		check(rock.scale.is_equal_approx(transforms[i].basis.get_scale()),"Spin preserves size")
		var radius: float = rock.get_meta("clearance_radius_m")
		var query = PhysicsRayQueryParameters3D.create(rock.global_position+Vector3.FORWARD*radius*3,rock.global_position-Vector3.FORWARD*radius*3,1)
		var hit = world.get_world_3d().direct_space_state.intersect_ray(query)
		check(not hit.is_empty() and hit.collider == rock,"Spinning collider remains queryable")
	field.spin_enabled=false
	var paused: Transform3D = rocks[0].transform
	for frame in range(5):await physics_frame
	check(rocks[0].transform.is_equal_approx(paused),"Spin can be paused")
	if "--capture" in OS.get_cmdline_user_args():
		await create_timer(1.5).timeout
		await RenderingServer.frame_post_draw
		DirAccess.make_dir_recursive_absolute("res://captures/asteroids")
		root.get_texture().get_image().save_png("res://captures/asteroids/main_field.png")
		var rig = world.get_node("OrbitCamera")
		rig.set_process(false)
		rig.camera.global_position=Vector3(540,370,-540)
		rig.camera.look_at(Vector3.ZERO,Vector3.UP)
		for frame in range(8):await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://captures/asteroids/field_overview.png")
	var report = {"passed":failures.is_empty(),"checks":checks,"failures":failures,"count":rocks.size(),"variants":shapes.size()}
	DirAccess.make_dir_recursive_absolute("res://captures/asteroids")
	FileAccess.open("res://captures/asteroids/field_validation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
	print(JSON.stringify(report))
	world.queue_free()
	await process_frame
	await process_frame
	quit(0 if failures.is_empty() else 1)
