class_name MountedTurret
extends Node3D
## Shared controller for the three ship-mounted turrets (quad cannon, gatling, laser).
##
## The imported model has the same node layout on all three:
##   <T>Turret > BaseMesh, Yaw (traverse, about +Y) > YawMesh, YawRing,
##   Pitch (elevation, about +X on the trunnion) > PitchMesh and the gun:
##     quad:    Barrel1..4 (recoil), each with Muzzle1..4
##     gatling: Spin (barrel cluster), Muzzle (12 o'clock barrel)
##     laser:   Projector (recoil), Muzzle (emitter window)
## Aiming is code-driven: aim_at() turns Yaw and Pitch toward a point at limited
## speeds, inside the elevation limits measured in Blender (reports/pitch_limits.json).
## The clips play on top: fire (quad recoil), spin_up / fire / spin_down (gatling),
## charge / fire (laser), and scan, an idle sweep that stops as soon as it aims.

signal shot_fired(muzzle: Node3D)                                  ## quad and gatling, one per round
signal charge_started                                              ## laser
signal beam_fired(origin: Vector3, direction: Vector3, length: float)  ## laser, when the beam lights
signal firing_started
signal firing_stopped

enum Kind { QUAD, GATLING, LASER }
enum State { IDLE, SPIN_UP, FIRING, SPIN_DOWN, CHARGING, BEAM, COOLDOWN }

@export var kind: Kind = Kind.QUAD
@export_group("Aiming")
@export var traverse_speed_deg := 70.0
@export var elevation_speed_deg := 45.0
@export var min_elevation_deg := -10.0
@export var max_elevation_deg := 80.0
## Half-arc the house may traverse either side of forward; 180 means unlimited.
@export var traverse_limit_deg := 180.0
@export var aim_tolerance_deg := 1.0
## Play the idle scan sweep while there is no target.
@export var auto_scan := true
@export_group("Weapon")
## Gatling rate of fire once spun up.
@export var rounds_per_second := 40.0
@export var beam_range := 800.0
@export var beam_duration := 0.6
@export var beam_cooldown := 0.4
@export var beam_color := Color(0.55, 0.8, 1.0)
## Muzzle flashes, laser glow and beam. Turn off to drive your own VFX from the signals.
@export var effects := true
@export var hitbox_layer := 1

var state := State.IDLE
var _yaw: Node3D
var _pitch: Node3D
var _player: AnimationPlayer
var _muzzles: Array[Node3D] = []
var _target = null
var _yaw_angle := 0.0
var _pitch_angle := 0.0
var _trigger := false
var _clip_pos := 0.0
var _round_clock := 0.0
var _state_time := 0.0
var _flashes := {}
var _beam: MeshInstance3D
var _glow: MeshInstance3D
var _glow_light: OmniLight3D

# quad: recoil starts in the fire clip (seconds) and the barrel that fires
const QUAD_SHOTS := [[0.0, 1], [1.0 / 6.0, 4], [2.0 / 6.0, 2], [3.0 / 6.0, 3]]
const LASER_CHARGE := 1.0


func _ready() -> void:
	_yaw = find_child("Yaw", true, false)
	_pitch = find_child("Pitch", true, false)
	_player = find_child("AnimationPlayer", true, false)
	assert(_yaw and _pitch and _player, "MountedTurret: model is missing Yaw, Pitch or AnimationPlayer")
	for name in ["Muzzle1", "Muzzle2", "Muzzle3", "Muzzle4", "Muzzle"]:
		var m: Node3D = find_child(name, true, false)
		if m:
			_muzzles.append(m)
	for clip in ["scan", "fire"]:
		if _player.has_animation(clip) and not (kind == Kind.LASER and clip == "fire"):
			_player.get_animation(clip).loop_mode = Animation.LOOP_LINEAR
	_build_hitbox()
	if effects:
		_build_effects()
	if auto_scan:
		_player.play("scan")


# ---- public API -------------------------------------------------------------------

## Turn toward a world-space point (and keep tracking it until clear_target()).
func aim_at(world_point: Vector3) -> void:
	_target = world_point
	_stop_scan()


## Drop the target: the gun returns to the rest pose, then scans if auto_scan.
func clear_target() -> void:
	_target = null


## Hold the trigger. The quad and laser cycle while held; the gatling spins up first.
func start_firing() -> void:
	if _trigger:
		return
	_trigger = true
	_stop_scan()
	firing_started.emit()
	match kind:
		Kind.QUAD:
			_set_state(State.FIRING)
			_player.play("fire")
			_clip_pos = -1.0
		Kind.GATLING:
			if state != State.FIRING:
				_set_state(State.SPIN_UP)
				_player.play("spin_up")
				_player.queue("fire")
		Kind.LASER:
			if state == State.IDLE:
				_charge()


func stop_firing() -> void:
	if not _trigger:
		return
	_trigger = false
	firing_stopped.emit()
	if kind == Kind.GATLING and state in [State.SPIN_UP, State.FIRING]:
		_player.clear_queue()
		_set_state(State.SPIN_DOWN)
		_player.play("spin_down")
	# the quad finishes its volley; the laser finishes its beam


## One shot: a quad volley, a gatling burst while called each frame, or one laser beam.
func fire() -> void:
	start_firing()
	if kind == Kind.LASER:
		_trigger = false


## True when the gun points at the target within aim_tolerance_deg.
func is_on_target() -> bool:
	if _target == null:
		return false
	var desired := _desired_angles(_target)
	return absf(wrapf(desired.x - _yaw_angle, -PI, PI)) <= deg_to_rad(aim_tolerance_deg) \
		and absf(desired.y - _pitch_angle) <= deg_to_rad(aim_tolerance_deg)


## True when the point lies inside the elevation and traverse limits.
func can_reach(world_point: Vector3) -> bool:
	var raw := _raw_angles(world_point)
	return raw.y >= deg_to_rad(min_elevation_deg) and raw.y <= deg_to_rad(max_elevation_deg) \
		and absf(raw.x) <= deg_to_rad(traverse_limit_deg)


## Snap the gun to angles in degrees (yaw left-positive, elevation up-positive).
func set_angles(yaw_deg: float, elevation_deg: float) -> void:
	_stop_scan()
	_yaw_angle = deg_to_rad(clampf(yaw_deg, -traverse_limit_deg, traverse_limit_deg))
	_pitch_angle = deg_to_rad(clampf(elevation_deg, min_elevation_deg, max_elevation_deg))
	_apply()


func get_angles() -> Vector2:
	return Vector2(rad_to_deg(_yaw_angle), rad_to_deg(_pitch_angle))


func get_muzzles() -> Array[Node3D]:
	return _muzzles


## World-space firing direction (the bore axis).
func get_aim_direction() -> Vector3:
	return -_pitch.global_transform.basis.z.normalized()


# ---- aiming -------------------------------------------------------------------------

func _raw_angles(world_point: Vector3) -> Vector2:
	var local := global_transform.affine_inverse() * world_point
	var yaw := atan2(-local.x, -local.z)
	var in_yaw := Basis(Vector3.UP, yaw).inverse() * local - _pitch.position
	var elevation := atan2(in_yaw.y, Vector2(in_yaw.x, in_yaw.z).length())
	return Vector2(yaw, elevation)


func _desired_angles(world_point: Vector3) -> Vector2:
	var raw := _raw_angles(world_point)
	return Vector2(clampf(raw.x, -deg_to_rad(traverse_limit_deg), deg_to_rad(traverse_limit_deg)),
		clampf(raw.y, deg_to_rad(min_elevation_deg), deg_to_rad(max_elevation_deg)))


func _stop_scan() -> void:
	if _player.current_animation == "scan":
		_player.stop(true)
		_yaw_angle = wrapf(_yaw.rotation.y, -PI, PI)
		_pitch_angle = _pitch.rotation.x


func _apply() -> void:
	_yaw.rotation = Vector3(0, _yaw_angle, 0)
	_pitch.rotation = Vector3(_pitch_angle, 0, 0)


func _process(delta: float) -> void:
	_state_time += delta
	var scanning := _player.current_animation == "scan"
	if not scanning:
		var desired := Vector2.ZERO if _target == null else _desired_angles(_target)
		var dyaw := desired.x - _yaw_angle
		if traverse_limit_deg >= 180.0:
			dyaw = wrapf(dyaw, -PI, PI)
		_yaw_angle = wrapf(_yaw_angle + clampf(dyaw, -deg_to_rad(traverse_speed_deg) * delta,
			deg_to_rad(traverse_speed_deg) * delta), -PI, PI)
		_pitch_angle += clampf(desired.y - _pitch_angle, -deg_to_rad(elevation_speed_deg) * delta,
			deg_to_rad(elevation_speed_deg) * delta)
		_apply()
		if _target == null and auto_scan and state == State.IDLE and not _trigger \
				and absf(_yaw_angle) < 0.002 and absf(_pitch_angle) < 0.002:
			_player.play("scan")
	match kind:
		Kind.QUAD: _process_quad()
		Kind.GATLING: _process_gatling(delta)
		Kind.LASER: _process_laser()
	_fade_flashes(delta)


func _set_state(new_state: State) -> void:
	state = new_state
	_state_time = 0.0


# ---- weapons ------------------------------------------------------------------------

func _process_quad() -> void:
	if state != State.FIRING or _player.current_animation != "fire":
		return
	var previous := _clip_pos
	var pos := _player.current_animation_position
	var wrapped := previous >= 0.0 and pos < previous
	if wrapped and not _trigger:
		# trigger released: the volley ends at the loop point
		_player.stop()
		_player.seek(0.0, true)
		_set_state(State.IDLE)
		return
	for shot in QUAD_SHOTS:
		var t: float = shot[0]
		var due := pos >= t
		if previous >= 0.0:
			due = (t > previous or t <= pos) if wrapped else (t > previous and t <= pos)
		if due:
			_shoot(_muzzles[shot[1] - 1])
	_clip_pos = pos


func _process_gatling(delta: float) -> void:
	if state == State.SPIN_UP and _player.current_animation == "fire":
		_set_state(State.FIRING)
		_round_clock = 0.0
	if state == State.FIRING:
		_round_clock += delta * rounds_per_second
		while _round_clock >= 1.0:
			_round_clock -= 1.0
			_shoot(_muzzles[0])
	if state == State.SPIN_DOWN and not _player.is_playing():
		_set_state(State.IDLE)


func _charge() -> void:
	_set_state(State.CHARGING)
	_player.play("charge")
	charge_started.emit()


func _process_laser() -> void:
	var muzzle := _muzzles[0]
	match state:
		State.CHARGING:
			_set_glow(_state_time / LASER_CHARGE)
			if _state_time >= LASER_CHARGE:
				_set_state(State.BEAM)
				_player.play("fire")
				var origin := muzzle.global_position
				var direction := -muzzle.global_transform.basis.z.normalized()
				var length := _beam_length(origin, direction)
				if _beam:
					_beam.visible = true
					_beam.scale = Vector3(1, 1, length)
				beam_fired.emit(origin, direction, length)
		State.BEAM:
			var fade := 1.0 - _state_time / beam_duration
			_set_glow(fade)
			if _beam:
				_beam.scale = Vector3(fade, fade, _beam.scale.z)
			if _state_time >= beam_duration:
				if _beam:
					_beam.visible = false
				_set_state(State.COOLDOWN)
		State.COOLDOWN:
			_set_glow(0.0)
			if _state_time >= beam_cooldown:
				_set_state(State.IDLE)
				if _trigger:
					_charge()


func _beam_length(origin: Vector3, direction: Vector3) -> float:
	var space := get_world_3d().direct_space_state
	if space == null:
		return beam_range
	var query := PhysicsRayQueryParameters3D.create(origin, origin + direction * beam_range)
	query.exclude = _hitbox_rids()
	var hit := space.intersect_ray(query)
	return beam_range if hit.is_empty() else origin.distance_to(hit.position)


func _shoot(muzzle: Node3D) -> void:
	shot_fired.emit(muzzle)
	if _flashes.has(muzzle):
		_flashes[muzzle] = 1.0


# ---- effects and hitboxes -------------------------------------------------------------

func _additive(color: Color, soft := false) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = color
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	if soft:
		# radial falloff: hot core, soft edge
		var gradient := Gradient.new()
		# additive: fading to black (rather than to transparent) is what removes the edge
		gradient.offsets = PackedFloat32Array([0.0, 0.22, 0.6, 1.0])
		gradient.colors = PackedColorArray([Color(1, 1, 1), Color(0.85, 0.85, 0.85), Color(0.18, 0.18, 0.18), Color(0, 0, 0)])
		var texture := GradientTexture2D.new()
		texture.gradient = gradient
		texture.fill = GradientTexture2D.FILL_RADIAL
		texture.fill_from = Vector2(0.5, 0.5)
		texture.fill_to = Vector2(1.0, 0.5)
		texture.width = 64
		texture.height = 64
		m.albedo_texture = texture
	return m


func _build_effects() -> void:
	if kind == Kind.LASER:
		var muzzle := _muzzles[0]
		_glow = MeshInstance3D.new()
		_glow.name = "EmitterGlow"
		_glow.mesh = QuadMesh.new()
		_glow.mesh.size = Vector2(1.4, 1.4)
		_glow.material_override = _additive(beam_color, true)
		_glow.material_override.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
		_glow.visible = false
		muzzle.add_child(_glow)
		_glow_light = OmniLight3D.new()
		_glow_light.light_color = beam_color
		_glow_light.omni_range = 6.0
		_glow_light.light_energy = 0.0
		muzzle.add_child(_glow_light)
		# a unit-length beam along -Z from the muzzle; scale.z sets its length
		var cyl := CylinderMesh.new()
		cyl.top_radius = 0.14
		cyl.bottom_radius = 0.14
		cyl.height = 1.0
		cyl.radial_segments = 12
		cyl.rings = 1
		var arrays := cyl.get_mesh_arrays()
		var along := Transform3D(Basis(Vector3.RIGHT, -PI / 2), Vector3(0, 0, -0.5))
		var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
		for i in verts.size():
			verts[i] = along * verts[i]
			normals[i] = along.basis * normals[i]
		arrays[Mesh.ARRAY_VERTEX] = verts
		arrays[Mesh.ARRAY_NORMAL] = normals
		arrays[Mesh.ARRAY_TANGENT] = null
		var beam_mesh := ArrayMesh.new()
		beam_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		_beam = MeshInstance3D.new()
		_beam.name = "Beam"
		_beam.mesh = beam_mesh
		_beam.material_override = _additive(Color(beam_color.r, beam_color.g, beam_color.b, 0.55))
		_beam.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_beam.visible = false
		muzzle.add_child(_beam)
	else:
		for muzzle in _muzzles:
			var flash := MeshInstance3D.new()
			flash.name = "MuzzleFlash"
			var quad := QuadMesh.new()
			quad.size = Vector2(0.9, 0.9) if kind == Kind.QUAD else Vector2(1.1, 1.1)
			flash.mesh = quad
			var m := _additive(Color(1.0, 0.75, 0.4), true)
			m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
			flash.material_override = m
			flash.position = Vector3(0, 0, -0.3)
			flash.visible = false
			muzzle.add_child(flash)
			var light := OmniLight3D.new()
			light.name = "MuzzleLight"
			light.light_color = Color(1.0, 0.7, 0.4)
			light.omni_range = 5.0
			light.light_energy = 0.0
			light.position = Vector3(0, 0, -0.3)
			muzzle.add_child(light)
			_flashes[muzzle] = 0.0


func _set_glow(amount: float) -> void:
	if _glow == null:
		return
	amount = clampf(amount, 0.0, 1.0)
	_glow.visible = amount > 0.01
	_glow.scale = Vector3.ONE * (0.3 + 0.7 * amount)
	_glow_light.light_energy = 3.0 * amount


func _fade_flashes(delta: float) -> void:
	for muzzle in _flashes:
		var v: float = _flashes[muzzle]
		var flash: MeshInstance3D = muzzle.get_node("MuzzleFlash")
		var light: OmniLight3D = muzzle.get_node("MuzzleLight")
		flash.visible = v > 0.0
		flash.scale = Vector3.ONE * (0.6 + 0.6 * v)
		light.light_energy = 4.0 * v
		_flashes[muzzle] = maxf(0.0, v - delta * 16.0)


func _build_hitbox() -> void:
	# Base: a cylinder on the root. House: a box from the house mesh, on Yaw, so it turns.
	var base := StaticBody3D.new()
	base.name = "BaseHitbox"
	base.collision_layer = hitbox_layer
	var cyl := CylinderShape3D.new()
	cyl.radius = 2.0
	cyl.height = 0.98
	var shape := CollisionShape3D.new()
	shape.shape = cyl
	shape.position = Vector3(0, 0.49, 0)
	base.add_child(shape)
	add_child(base)
	var house_mesh: MeshInstance3D = _yaw.find_child("YawMesh", false, false)
	if house_mesh:
		var box := StaticBody3D.new()
		box.name = "HouseHitbox"
		box.collision_layer = hitbox_layer
		var aabb := house_mesh.get_aabb()
		var b := BoxShape3D.new()
		b.size = aabb.size
		var s := CollisionShape3D.new()
		s.shape = b
		s.position = aabb.get_center()
		box.add_child(s)
		_yaw.add_child(box)


func _hitbox_rids() -> Array[RID]:
	var rids: Array[RID] = []
	for body in find_children("*Hitbox", "StaticBody3D", true, false):
		rids.append(body.get_rid())
	return rids
