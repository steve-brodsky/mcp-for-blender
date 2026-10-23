extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func dump(n: Node, d: int) -> void:
	var extra := ""
	if n is BoneAttachment3D: extra = " bone=" + n.bone_name
	if n is Skeleton3D: extra = " bones=%d" % n.get_bone_count()
	if n is MeshInstance3D: extra = " surfaces=%d" % n.mesh.get_surface_count()
	if n is AnimationPlayer: extra = " anims=" + str(n.get_animation_list())
	print("  ".repeat(d), n.name, " <", n.get_class(), ">", extra)
	for c in n.get_children(): dump(c, d + 1)
func run() -> void:
	for p in ["res://assets/ships/combat_mech/combat_mech.glb", "res://assets/ships/combat_mech/beam_rifle.glb"]:
		var s: PackedScene = load(p)
		var i := s.instantiate()
		dump(i, 0)
		i.free()
	quit()
