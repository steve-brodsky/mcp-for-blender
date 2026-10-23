extends SceneTree

var failures: Array[String] = []
var checks := 0
var stage: Node3D
var instances: Array[StaticBody3D] = []

func check(value: bool, message: String) -> void:
	checks += 1
	if not value:
		failures.append(message)
		push_error(message)

func _initialize() -> void:
	call_deferred("validate")

func validate() -> void:
	var catalog = JSON.parse_string(FileAccess.get_file_as_string("res://assets/environment/asteroids/catalog.json"))
	check(catalog.size() == 28, "28 independent assets")
	stage = Node3D.new()
	root.add_child(stage)
	for index in range(catalog.size()):
		var asset = catalog[index]
		var packed = load("res://scenes/environment/asteroids/" + asset.id + ".tscn")
		check(packed is PackedScene, asset.id + " scene loads")
		var body = packed.instantiate() as StaticBody3D
		check(body != null and body.transform == Transform3D.IDENTITY, asset.id + " identity static body")
		check(body.is_in_group("asteroids"), asset.id + " asteroid group")
		check(body.get_script() == null, asset.id + " no runtime script dependency")
		stage.add_child(body)
		body.position = Vector3(index * 120, 0, 0)
		instances.append(body)
		var material: Material
		for level in range(3):
			var mesh_instance: MeshInstance3D = body.get_node("LOD%d" % level)
			check(mesh_instance.mesh != null and mesh_instance.mesh.get_surface_count() == 1, asset.id + " LOD%d single mesh surface" % level)
			var mesh = mesh_instance.mesh
			check(mesh.get_faces().size() / 3 == asset.lod_triangles[level], asset.id + " LOD%d triangle count" % level)
			var arrays = mesh.surface_get_arrays(0)
			check(arrays[Mesh.ARRAY_NORMAL].size() == arrays[Mesh.ARRAY_VERTEX].size(), asset.id + " normal buffer")
			check(arrays[Mesh.ARRAY_TEX_UV].size() == arrays[Mesh.ARRAY_VERTEX].size(), asset.id + " UV buffer")
			if level == 0:
				var bounds = mesh.get_aabb()
				var expected = Vector3(asset.dimensions_godot[0],asset.dimensions_godot[1],asset.dimensions_godot[2])
				check(bounds.size.distance_to(expected) < .01, asset.id + " native dimensions")
				check(bounds.get_center().length() < .02, asset.id + " centered pivot")
				material = mesh_instance.material_override
				check(material is StandardMaterial3D, asset.id + " standard PBR material")
				check(material.albedo_texture != null and material.normal_texture != null, asset.id + " textures resolve")
				check(material.albedo_texture.get_width() == asset.texture_size and material.normal_texture.get_width() == asset.texture_size, asset.id + " atlas resolution")
				check(material.metallic == 0 and material.roughness > .8, asset.id + " nonmetal rock")
				check(material.cull_mode == BaseMaterial3D.CULL_BACK, asset.id + " backface culling")
			check(mesh_instance.material_override == material, asset.id + " shared LOD material")
			check(absf(mesh_instance.visibility_range_begin - (0 if level == 0 else asset.lod_distances[level-1])) < .001, asset.id + " LOD start threshold")
			check(absf(mesh_instance.visibility_range_end - (0 if level == 2 else asset.lod_distances[level])) < .001, asset.id + " LOD end threshold")
		var collision: CollisionShape3D = body.get_node("Collision")
		check(collision.shape is ConvexPolygonShape3D and not collision.disabled,asset.id + " active convex collider")
		check(collision.shape.points.size() == asset.collision_point_count and collision.shape.points.size() >= 4,asset.id + " valid collision points")
	await physics_frame
	await physics_frame
	for index in range(instances.size()):
		var body = instances[index]
		var diameter: float = body.get_meta("diameter_m")
		var query = PhysicsRayQueryParameters3D.create(body.position + Vector3(0,0,diameter*2),body.position - Vector3(0,0,diameter*2),1)
		var hit = stage.get_world_3d().direct_space_state.intersect_ray(query)
		check(not hit.is_empty() and hit.collider == body, "Physics ray hits " + body.name)
	var second = load("res://scenes/environment/asteroids/asteroid_01.tscn").instantiate()
	stage.add_child(second)
	second.position = Vector3(0,0,100)
	check(second.get_node("LOD0").mesh == instances[0].get_node("LOD0").mesh,"Repeated instances share GPU mesh resources")
	check(second.get_node("Collision").shape == instances[0].get_node("Collision").shape,"Repeated instances share collision resources")
	var output = {"checks":checks,"failures":failures,"passed":failures.is_empty(),"engine":Engine.get_version_info().string}
	DirAccess.make_dir_recursive_absolute("res://captures/asteroids")
	var path = "res://captures/asteroids/runtime_validation.json"
	FileAccess.open(path,FileAccess.WRITE).store_string(JSON.stringify(output,"\t"))
	print(JSON.stringify(output))
	stage.queue_free()
	await process_frame
	await process_frame
	quit(0 if failures.is_empty() else 1)
