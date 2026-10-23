extends SceneTree
## Renders the preview scene in a real window and saves review captures to ../renders/godot_*.png.
##   godot --path . -s tests/capture_combat_mech.gd

var preview: Node3D
var out_dir := ""


func _initialize() -> void:
	call_deferred("run")


func wait(seconds: float) -> void:
	await create_timer(seconds).timeout


func shot(name: String) -> void:
	await process_frame
	await process_frame
	var img := root.get_texture().get_image()
	img.save_png(out_dir.path_join("godot_" + name + ".png"))
	print("captured ", name)


func run() -> void:
	out_dir = ProjectSettings.globalize_path("res://").path_join("../renders")
	root.size = Vector2i(1280, 800)
	preview = load("res://scenes/previews/combat_mech_preview.tscn").instantiate()
	root.add_child(preview)
	var mech: CombatMech = preview.get_node("CombatMech")
	preview.get_node("UI").visible = false
	await wait(1.0)
	preview.set_view(0, 8, 24)
	await wait(0.5)
	await shot("hover_front")
	preview.set_view(35, 14, 24)
	await shot("hover_three_quarter")
	preview.set_view(180, 10, 24)
	await shot("hover_back")
	preview.set_view(90, 4, 24)
	await shot("hover_side")
	mech.set_state("cruise_flight")
	await wait(1.2)
	preview.set_view(70, 10, 24)
	await shot("cruise_side")
	mech.set_state("boost")
	preview.get_node("%BoostSlider").value = 1.0
	await wait(1.4)
	preview.set_view(140, 15, 26)
	await shot("boost_rear")
	preview.set_view(165, 25, 14)
	await shot("boost_thrusters_close")
	preview.get_node("%BoostSlider").value = 0.0
	mech.set_state("aim")
	await wait(1.2)
	preview.set_view(25, 10, 26)
	await shot("aim")
	preview.set_view(-70, 12, 18)
	await shot("aim_support_left")
	preview.set_view(-25, -15, 16)
	await shot("aim_support_below")
	preview.set_view(160, 20, 20)
	await shot("aim_support_rear")
	preview.set_view(-150, 40, 16)
	await shot("aim_support_rear_high")
	mech.play_fire(preview.get_node("Target").global_position)
	preview.set_view(80, 8, 70)
	preview.focus = Vector3(0, 6, -25)
	preview.set_view(80, 8, 70)
	await wait(0.06)
	await shot("fire_beam")
	preview.focus = Vector3(0, 5.2, 0)
	await wait(0.6)
	preview.set_view(40, 12, 24)
	mech.play_hit()
	await wait(0.12)
	await shot("hit_reaction")
	await wait(1.0)
	mech.set_state("disabled")
	await wait(2.2)
	preview.set_view(30, 10, 24)
	await shot("disabled")
	mech.set_state("hover_idle")
	preview.get_node("%SquadToggle").button_pressed = true
	await wait(1.2)
	preview.set_view(20, 12, 44)
	preview.get_node("UI").visible = true
	await shot("multi_instance_ui")
	quit()
