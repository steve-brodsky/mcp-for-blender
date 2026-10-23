extends SceneTree
## Runtime validation for the combat mech asset. Run:
##   godot --headless --path . -s tests/validate_combat_mech.gd
## Exits with code 1 if any check fails; writes reports/runtime_validation.json next to the project.

var failures: Array[String] = []
var checks := 0
var results := {}


func check(value: bool, message: String) -> void:
	checks += 1
	if not value:
		failures.append(message)
		push_error("FAIL: " + message)
	else:
		print("ok   ", message)


## Distance from the left palm (45% along hand.L) to the rifle's SupportGrip, measured through a
## BoneAttachment3D so it sees the final pose after skeleton modifiers (what is rendered).
func support_gap(mech: CombatMech) -> float:
	var rifle := mech.weapon as BeamRifle
	var att := mech.get_node_or_null("_TestHandL") as BoneAttachment3D
	if att == null:
		att = BoneAttachment3D.new()
		att.name = "_TestHandL"
		att.set_use_external_skeleton(true)
		mech.add_child(att)
		att.set_external_skeleton(att.get_path_to(mech.skeleton))
		att.bone_name = "hand.L"
	var g := att.global_transform
	var palm := g.origin + g.basis.y.normalized() * 0.45
	return palm.distance_to(rifle.support_grip.global_position)


## Largest drift of an upper-arm socket from its rest position in torso space (final pose).
func socket_drift(mech: CombatMech) -> float:
	var worst := 0.0
	var torso := _attach(mech, "torso")
	for s in ["L", "R"]:
		var arm := _attach(mech, "upper_arm." + s)
		var b := mech.skeleton.find_bone("upper_arm." + s)
		var t := mech.skeleton.find_bone("torso")
		var rest_local := mech.skeleton.get_bone_global_rest(t).affine_inverse() * mech.skeleton.get_bone_global_rest(b).origin
		var now_local := torso.global_transform.affine_inverse() * arm.global_position
		worst = maxf(worst, rest_local.distance_to(now_local))
	return worst


func _attach(mech: CombatMech, bone: String) -> BoneAttachment3D:
	var node_name := "_Test_" + bone.replace(".", "_")
	var att := mech.get_node_or_null(node_name) as BoneAttachment3D
	if att == null:
		att = BoneAttachment3D.new()
		att.name = node_name
		att.set_use_external_skeleton(true)
		mech.add_child(att)
		att.set_external_skeleton(att.get_path_to(mech.skeleton))
		att.bone_name = bone
	return att


func _initialize() -> void:
	call_deferred("validate")


func wait(seconds: float) -> void:
	await create_timer(seconds).timeout


func validate() -> void:
	var packed: PackedScene = load("res://scenes/ships/combat_mech.tscn")
	check(packed != null, "combat_mech.tscn loads")
	var stage := Node3D.new()
	root.add_child(stage)
	var mechs: Array[CombatMech] = []
	for i in 3:
		var m := packed.instantiate() as CombatMech
		m.position = Vector3(i * 16.0, 0, 0)
		stage.add_child(m)
		mechs.append(m)
	await process_frame
	await process_frame
	var mech := mechs[0]

	# --- asset structure
	check(mech.skeleton != null and mech.skeleton.get_bone_count() == 18, "skeleton with 18 bones")
	var expected := ["hover_idle", "cruise_flight", "boost", "aim", "fire", "hit_reaction", "disabled"]
	var lengths := {}
	for a in expected:
		var anim := mech.anim_player.get_animation(a)
		check(anim != null, "animation present: " + a)
		if anim:
			var keys := 0
			for t in anim.get_track_count():
				keys = maxi(keys, anim.track_get_key_count(t))
			lengths[a] = anim.length
			check(anim.length > 0.1 and keys > 3, "animation has real keys: %s (%.2fs, %d keys)" % [a, anim.length, keys])
	results["animation_lengths"] = lengths
	check(mech.anim_player.get_animation("hover_idle").loop_mode == Animation.LOOP_LINEAR, "hover_idle loops")
	check(mech.anim_player.get_animation("cruise_flight").loop_mode == Animation.LOOP_LINEAR, "cruise_flight loops")
	var body := mech.visuals.find_child("CombatMech_Body", true, false) as MeshInstance3D
	check(body != null and body.mesh.get_surface_count() == 3, "body mesh with 3 surfaces")
	var tris := 0
	for s in body.mesh.get_surface_count():
		tris += body.mesh.surface_get_arrays(s)[Mesh.ARRAY_INDEX].size() / 3
		check(body.get_active_material(s) != null, "material on surface %d" % s)
	results["body_triangles"] = tris
	check(tris > 15000 and tris < 30000, "triangle budget (%d)" % tris)
	var aabb := body.get_aabb()
	results["height_m"] = aabb.size.y
	check(absf(aabb.size.y - 10.0) < 0.6, "approximately 10 m tall (%.2f)" % aabb.size.y)
	check(mech.anim_tree.active, "AnimationTree active")

	# --- rifle attachment
	check(mech.weapon != null and mech.weapon is BeamRifle, "rifle mounted")
	var rifle := mech.weapon as BeamRifle
	check(rifle.muzzle != null and rifle.is_ancestor_of(rifle.muzzle), "muzzle belongs to rifle")
	check(mech.weapon_socket.bone_name == "hand.R", "weapon socket on hand.R")

	# --- states
	var muzzle_pos := {}
	for s in ["hover_idle", "cruise_flight", "boost", "aim", "disabled"]:
		mech.set_state(s)
		await wait(1.1)
		check(String(mech.current_state_node()) == s, "state machine reaches " + s)
		# rifle follows the hand bone
		var hand := mech.skeleton.find_bone("hand.R")
		var hand_global := mech.skeleton.global_transform * mech.skeleton.get_bone_global_pose(hand)
		var socket_err := (mech.weapon_socket.global_transform.origin - hand_global.origin).length()
		check(socket_err < 0.01, "weapon socket follows hand in %s (%.4f m)" % [s, socket_err])
		var rifle_err := (rifle.global_position - mech.grip.global_position).length()
		check(rifle_err < 0.001, "rifle on grip in %s" % s)
		muzzle_pos[s] = rifle.muzzle.global_position
		socket_drift(mech)
		await process_frame
		await process_frame
		var drift := socket_drift(mech)
		check(drift < 0.15, "arm sockets stay on the torso in %s (%.3f m)" % [s, drift])
	check((muzzle_pos["aim"] - muzzle_pos["hover_idle"]).length() > 1.0, "muzzle moves with animation (%.2f m)" % (muzzle_pos["aim"] - muzzle_pos["hover_idle"]).length())
	results["muzzle_positions"] = {}
	for k in muzzle_pos:
		results["muzzle_positions"][k] = [snappedf(muzzle_pos[k].x, 0.01), snappedf(muzzle_pos[k].y, 0.01), snappedf(muzzle_pos[k].z, 0.01)]

	# --- aim direction: mech faces -Z, rifle should point forward while aiming
	mech.set_aim_target(null)
	mech.set_state("aim")
	await wait(1.0)
	var fwd := -mech.global_basis.z
	var dir0 := rifle.muzzle_direction()
	results["aim_forward_dot"] = fwd.dot(dir0)
	check(fwd.dot(dir0) > 0.9, "aim clip points rifle forward (dot %.3f)" % fwd.dot(dir0))
	support_gap(mech)
	await process_frame
	await process_frame
	results["support_gap_aim"] = support_gap(mech)
	check(support_gap(mech) < 0.2, "left hand supports the underbarrel in aim (%.3f m)" % support_gap(mech))
	# procedural aim toward a target 40 deg to the left and slightly up
	var target := mech.global_position + Vector3(0, 7, 0) + (fwd.rotated(Vector3.UP, deg_to_rad(40)) * 120.0)
	mech.set_aim_target(target)
	await wait(1.2)
	var to_target := (target - rifle.muzzle.global_position).normalized()
	var dir1 := rifle.muzzle_direction()
	results["aim_target_dot_before_after"] = [dir0.dot(to_target), dir1.dot(to_target)]
	check(support_gap(mech) < 0.2, "left hand stays on the underbarrel with procedural aim (%.3f m)" % support_gap(mech))
	check(socket_drift(mech) < 0.15, "arm sockets stay on the torso with procedural aim (%.3f m)" % socket_drift(mech))
	check(dir1.dot(to_target) > dir0.dot(to_target) + 0.05, "procedural aim turns rifle toward target (%.3f -> %.3f)" % [dir0.dot(to_target), dir1.dot(to_target)])

	# --- firing
	var fired := [false]
	mech.weapon_fired.connect(func(a, b): fired[0] = true)
	var end := mech.play_fire()
	await process_frame
	await process_frame
	check(fired[0], "weapon_fired signal")
	check(rifle.beam.is_firing(), "beam visible while firing")
	check(bool(mech.anim_tree.get("parameters/fire/active")), "fire one-shot playing")
	await wait(0.06)
	results["support_gap_fire"] = support_gap(mech)
	check(support_gap(mech) < 0.25, "left hand stays on the underbarrel while firing (%.3f m)" % support_gap(mech))
	check(end.distance_to(target) < 0.01, "beam endpoint uses aim target")
	await wait(0.6)
	check(not rifle.beam.is_firing(), "beam ends after its duration")
	var custom_end := rifle.muzzle.global_position + Vector3(10, 0, -50)
	rifle.fire(custom_end)
	await process_frame
	check((rifle.beam.get_node("ImpactFlare") as Node3D).global_position.distance_to(custom_end) < 0.01, "configurable beam endpoint")

	# --- hit
	mech.play_hit()
	await process_frame
	check(bool(mech.anim_tree.get("parameters/hit/active")), "hit_reaction one-shot playing")
	await wait(0.8)

	# --- thrusters
	check(mech.thrusters.size() == 8, "8 thruster mounts (%d)" % mech.thrusters.size())
	mech.set_aim_target(null)
	mech.set_state("hover_idle")
	mech.set_boost(0.0)
	await wait(0.8)
	var pack: MechThruster = mech.thrusters["thruster_pack_L"]
	var calf: MechThruster = mech.thrusters["thruster_calf_L"]
	check(pack.intensity > 0.2 and pack.intensity < 0.5, "idle main thrusters low (%.2f)" % pack.intensity)
	check(calf.intensity < 0.01, "leg jets off at idle")
	mech.set_boost(1.0)
	await wait(1.0)
	check(pack.intensity > 0.95, "boost drives main thrusters (%.2f)" % pack.intensity)
	check(calf.intensity > 0.5, "boost drives leg jets (%.2f)" % calf.intensity)
	mech.set_boost(0.0)
	mech.pulse_jet("shoulder_L", 0.4)
	await wait(0.15)
	check(mech.thrusters["thruster_shoulder_L"].intensity > 0.3, "manoeuvre jet pulse")
	check(mech.thrusters["thruster_shoulder_R"].intensity < 0.01, "other manoeuvre jet stays off")
	await wait(0.8)
	check(mech.thrusters["thruster_shoulder_L"].intensity < 0.05, "manoeuvre jet ends")
	mech.set_thrusters_enabled(false)
	await wait(0.8)
	check(pack.intensity < 0.01, "thrusters can be switched off")
	mech.set_thrusters_enabled(true)
	mech.set_state("disabled")
	await wait(0.8)
	check(pack.intensity < 0.01, "disabled state cuts thrusters")
	# thruster marker follows its bone
	var shin := mech.skeleton.find_bone("shin.L")
	var shin_g := mech.skeleton.global_transform * mech.skeleton.get_bone_global_pose(shin)
	var att := calf.get_parent().get_parent() as BoneAttachment3D
	check(att != null and att.bone_name == "shin.L", "calf thruster mounted on shin.L attachment")
	check(att.global_position.distance_to(shin_g.origin) < 0.01, "thruster attachment follows bone")

	# --- hitboxes
	var areas := mech.find_children("Area", "Area3D", true, false)
	check(areas.size() == 11, "11 bone hitboxes (%d)" % areas.size())

	# --- multiple instances are independent
	mechs[1].set_state("boost")
	mechs[2].set_state("aim")
	await wait(1.0)
	check(String(mechs[1].current_state_node()) == "boost" and String(mechs[2].current_state_node()) == "aim" and String(mech.current_state_node()) == "disabled", "instances animate independently")
	check(mechs[1].weapon != mechs[2].weapon and mechs[1].weapon != null, "each instance has its own rifle")
	check(mechs[1]._thruster_material != mechs[2]._thruster_material, "per-instance emissive materials")

	# --- weapon replacement
	var spare: Node3D = load("res://scenes/weapons/beam_rifle.tscn").instantiate()
	mechs[2].equip_weapon(spare)
	await process_frame
	check(mechs[2].weapon == spare and spare.get_parent() == mechs[2].grip, "weapon can be replaced at runtime")

	results["checks"] = checks
	results["failures"] = failures
	var dir := ProjectSettings.globalize_path("res://").path_join("../reports")
	DirAccess.make_dir_recursive_absolute(dir)
	var f := FileAccess.open(dir.path_join("runtime_validation.json"), FileAccess.WRITE)
	f.store_string(JSON.stringify(results, "  "))
	f.close()
	print("\n%d checks, %d failures" % [checks, failures.size()])
	for x in failures:
		print("FAILED: ", x)
	quit(1 if failures.size() > 0 else 0)
