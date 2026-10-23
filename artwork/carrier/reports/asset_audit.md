# Carrier asset audit

Measured final exports: 34,461 / 19,213 / 7,831 hull triangles. Bare hull: four mesh objects, seven draw surfaces, four shared game materials, zero remaining modifiers. Default assembled preview: 60,457 triangles and 71 material surfaces before additional render passes.

Source hull: 19 mesh objects and 126,303 evaluated triangles. The reusable game hull excludes all ten module types and the default loadout. All root scales are identity.

## Hierarchy

Source: CARRIER_ROOT owns permanent hull pieces, independent doors, engine emission, 20 socket empties and three hangar navigation transforms. Preview modules are children of sockets and reference canonical library mesh data. The game hull root owns one consolidated static hull, one engine-emission mesh and two doors. Canonical weapons retain mounting root → TURRET_YAW → TURRET_PITCH → geometry/muzzles. Subsystems have a common mounting root and separate equipment/scanning node.

Godot: Carrier owns Hull, WeaponSockets (12 explicit Marker3Ds), SystemSockets (8 explicit Marker3Ds), Hangar (Spawn/Exit/Approach and Doors), Collision (13 proxies), Animations and Modules. Attached models live under their actual socket; the installed dictionary is the loadout registry.

## Module geometry and compatibility

| Asset | Socket class | Triangles | Meshes | Draw surfaces |
|---|---|---:|---:|---:|
| heavy_kinetic | HEAVY | 1,444 | 3 | 3 |
| heavy_beam | HEAVY | 2,316 | 3 | 5 |
| medium_assault | MEDIUM | 1,908 | 3 | 3 |
| point_defense | PD | 966 | 3 | 3 |
| missile_launcher | MISSILE | 1,448 | 3 | 4 |
| shield_generator | SYSTEM | 1,336 | 2 | 3 |
| sensor_array | SYSTEM | 1,644 | 2 | 3 |
| fire_control | SYSTEM | 372 | 2 | 3 |
| fighter_operations | SYSTEM | 364 | 2 | 3 |
| aux_reactor | SYSTEM | 776 | 2 | 3 |


| Socket class | Compatible modules |
|---|---|
| HEAVY | heavy_kinetic, heavy_beam |
| MEDIUM | medium_assault |
| PD | point_defense |
| MISSILE | missile_launcher |
| SYSTEM | shield_generator, sensor_array, fire_control, fighter_operations, aux_reactor |


## Socket transforms

Coordinates below are Godot meters, Y-up and -Z forward. No negative-scale mirroring is used.

| Socket ID | Class | Godot position (m) | Yaw (degrees) |
|---|---|---|---:|
| SOCKET_WEAPON_HEAVY_01 | HEAVY | [-4, 10, 0] | -0.0 |
| SOCKET_WEAPON_HEAVY_02 | HEAVY | [4, 9, 24] | -180 |
| SOCKET_WEAPON_MEDIUM_01 | MEDIUM | [-21, 8.5, 19] | -0.0 |
| SOCKET_WEAPON_MEDIUM_02 | MEDIUM | [21, 8.5, 19] | -0.0 |
| SOCKET_WEAPON_MEDIUM_03 | MEDIUM | [-21, 7, -5] | -0.0 |
| SOCKET_WEAPON_MEDIUM_04 | MEDIUM | [21, 7, -5] | -0.0 |
| SOCKET_WEAPON_PD_01 | PD | [-25, 8.6, 29] | -180.0 |
| SOCKET_WEAPON_PD_02 | PD | [25, 8.6, 29] | -180.0 |
| SOCKET_WEAPON_PD_03 | PD | [-17, 7.2, -43] | -0.0 |
| SOCKET_WEAPON_PD_04 | PD | [17, 7.2, -43] | -0.0 |
| SOCKET_WEAPON_MISSILE_01 | MISSILE | [-20, 7.1, -20] | -0.0 |
| SOCKET_WEAPON_MISSILE_02 | MISSILE | [20, 7.1, -20] | -0.0 |
| SOCKET_SYSTEM_01 | SYSTEM | [-18, 8.6, 35] | -0.0 |
| SOCKET_SYSTEM_02 | SYSTEM | [-23, 8.6, 35] | -0.0 |
| SOCKET_SYSTEM_03 | SYSTEM | [18, 8.6, 35] | -0.0 |
| SOCKET_SYSTEM_04 | SYSTEM | [23, 8.6, 35] | -0.0 |
| SOCKET_SYSTEM_05 | SYSTEM | [-3, 5, 33] | -0.0 |
| SOCKET_SYSTEM_06 | SYSTEM | [3, 5, 33] | -0.0 |
| SOCKET_SYSTEM_07 | SYSTEM | [-3, 5.5, -12] | -0.0 |
| SOCKET_SYSTEM_08 | SYSTEM | [3, 5.5, -12] | -0.0 |


## Texture and draw considerations

Four shared 2048² PNGs are stored under textures/hull and embedded in exports. Nonemissive ceramic, graphite, steel and paint share an atlas shader. Three emissive materials preserve their independent strengths. The four-mesh hull needs seven material draw surfaces; individual modules need 2–5. This is geometry/material accounting, not a measured GPU draw-call profile. Each independent GLB embeds copies of the atlas; a consuming game can deduplicate imported textures.

UVs are intentionally overlapping atlas/trim coordinates. Small seam, fastener and roughness details are textures; silhouette armor, doors, interior ribs, mounts, guns and engines are geometry. The underside is simpler than the dorsal hero surfaces. Box collision is independent of render topology and leaves the starboard launch corridor open.

No unrelated project files were edited. Reference SHA256 values are recorded in reference_inventory.json. The user's supplied reference logos were not reproduced on the ship.
