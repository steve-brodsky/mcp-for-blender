extends SceneTree
func _initialize() -> void:
    call_deferred("verify")
func verify() -> void:
    var packed = load("res://scenes/ships/interceptor.tscn") as PackedScene
    assert(packed != null)
    var ship = packed.instantiate() as Node3D
    ship.process_mode = Node.PROCESS_MODE_DISABLED
    root.add_child(ship)
    for name in ["MuzzlePort", "MuzzleStarboard"]:
        var marker = ship.get_node(name) as Marker3D
        assert(marker != null and marker.get_parent() == ship)
        assert(marker.basis == Basis.IDENTITY)
        assert(is_equal_approx(marker.position.y, -0.085) and is_equal_approx(marker.position.z, -1.0))
        assert(is_equal_approx(absf(marker.position.x), 0.145))
        for lod in ["LOD0", "LOD1", "LOD2"]:
            ship.get_node(lod).visible = false
            assert(marker.is_visible_in_tree())
        ship.position = Vector3(12, 8, -4)
        ship.rotation = Vector3(0.2, 0.7, -0.1)
        assert(marker.global_position.is_equal_approx(ship.global_transform * marker.position))
        assert((-marker.global_basis.z).is_equal_approx(-ship.global_basis.z))
        print("PASS ", name, " position=", marker.position, " forward/attachment/LOD independence")
    ship.free()
    print("MUZZLE_VALIDATION_OK")
    quit()


