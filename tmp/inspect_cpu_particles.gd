extends SceneTree
func _initialize():
    var particle := CPUParticles3D.new()
    for method in particle.get_method_list():
        if "particle" in method.name or "process" in method.name or "restart" in method.name:
            print(method.name)
    particle.free()
    quit()
