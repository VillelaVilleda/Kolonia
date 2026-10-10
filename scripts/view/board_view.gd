class_name BoardView
extends Node3D
## Dibuja el tablero en 3D a partir de un GameState.
## Por ahora usa figuras simples (prismas, cápsulas, cajas) como marcadores;
## más adelante se reemplazan por los modelos 3D de cada tribu.

const TERRAIN_COLORS := {
	"llanura": Color(0.47, 0.73, 0.35),
	"bosque": Color(0.27, 0.52, 0.26),
	"montana": Color(0.56, 0.52, 0.47),
	"agua": Color(0.24, 0.52, 0.86),
}
const HIGHLIGHT_COLORS := {
	"move": Color(1, 1, 1, 0.38),
	"attack": Color(1, 0.15, 0.1, 0.55),
	"select": Color(1, 0.85, 0.15, 0.55),
	"ability": Color(0.7, 0.3, 1.0, 0.55),
	"territory": Color(1, 0.95, 0.6, 0.3),
	"action": Color(0.3, 1.0, 0.5, 0.5),
}
const NEUTRAL_COLOR := Color(0.6, 0.6, 0.6)

var _gs: GameState
var _overlays := {}     # Vector2i -> MeshInstance3D
var _unit_nodes := {}   # id -> Node3D
var _city_nodes := {}   # Vector2i -> Node3D
var _deco_nodes := {}   # Vector2i -> [clave, Node3D] recursos, edificios y llamas
var _tile_nodes := {}   # Vector2i -> Node3D (casilla y su decoración)
var _fog_nodes := {}    # Vector2i -> Node3D (nube: casilla sin explorar)
var _dim_nodes := {}    # Vector2i -> MeshInstance3D (sombra: explorada pero fuera de la vista)

## Jugador desde cuyo punto de vista se dibuja la niebla (el jugador humano).
var viewer := 0
var _materials := {}    # clave -> StandardMaterial3D
var _tile_mesh: ArrayMesh
var _models := {}       # nombre -> PackedScene (modelos de KayKit)
var _city_keys := {}    # Vector2i -> "dueño|nivel" con el que se armó la ciudad

## Los modelos de KayKit miden 1.155 del centro a una esquina; nuestras casillas, 1.
const KK_SCALE := 0.866
## Están "de punta" en otra dirección: girarlos 30° los alinea con nuestras casillas.
const KK_TILE_ROT := PI / 6.0
const GRASS_TINT := Color(0.62, 0.9, 0.5)
var _overlay_mesh: ArrayMesh
var anim: UnitAnimator


func build(gs: GameState) -> void:
	_gs = gs
	for child in get_children():
		child.queue_free()
	_overlays.clear()
	_unit_nodes.clear()
	_city_nodes.clear()
	_city_keys.clear()
	_deco_nodes.clear()
	_tile_nodes.clear()
	_fog_nodes.clear()
	_dim_nodes.clear()
	anim = UnitAnimator.new()
	anim.name = "Animador"
	anim.board = self
	add_child(anim)
	_tile_mesh = make_hex_mesh(0.96, 0.5)
	_overlay_mesh = make_hex_mesh(0.9, 0.02)

	for p in gs.tiles:
		var terrain: String = gs.tiles[p]
		var holder := Node3D.new()
		add_child(holder)
		_tile_nodes[p] = holder
		# El pasto de KayKit es casi amarillo; se le da un tono más verde.
		var tile := _model("hex_water" if terrain == "agua" else "hex_grass", 1.0, KK_TILE_ROT,
			Color.WHITE if terrain == "agua" else GRASS_TINT)
		# La parte de arriba del pasto queda a la altura 0.25 (el agua queda un poco más abajo).
		tile.position = Hex.to_world(p) + Vector3(0, 0.25, 0)
		holder.add_child(tile)
		_add_decoration(p, terrain, holder)

		# Nube para las casillas sin explorar (modelo assets/nubes/nube.glb, ya tiene
		# forma de hexágono). Se gira de 60 en 60 grados para que no se vean todas iguales.
		var cloud := Node3D.new()
		cloud.position = Hex.to_world(p)
		var seed_i := absi(p.x * 7 + p.y * 13)
		if _cloud_scene == null:
			_cloud_scene = load("res://assets/nubes/nube.glb")
		var puff: Node3D = _cloud_scene.instantiate()
		puff.rotation.y = PI / 3.0 * (seed_i % 6)
		puff.position.y = 0.05
		_set_material(puff, _cloud_mat())
		cloud.add_child(puff)
		cloud.visible = false
		add_child(cloud)
		_fog_nodes[p] = cloud

		# Sombra para lo explorado que ahora no se ve
		var dim := MeshInstance3D.new()
		dim.mesh = _overlay_mesh
		dim.scale = Vector3(1.07, 1, 1.07)
		dim.material_override = _mat("sombra", Color(0.05, 0.08, 0.15, 0.42), true)
		dim.position = Hex.to_world(p) + Vector3(0, tile_height(p) + 0.003, 0)
		dim.visible = false
		add_child(dim)
		_dim_nodes[p] = dim

		var ov := MeshInstance3D.new()
		ov.mesh = _overlay_mesh
		ov.position = Hex.to_world(p) + Vector3(0, tile_height(p) + 0.005, 0)
		ov.visible = false
		add_child(ov)
		_overlays[p] = ov

	for pos in gs.cities:
		var node := _make_city(pos)
		_city_nodes[pos] = node
		add_child(node)
	sync()


func tile_height(p: Vector2i) -> float:
	return 0.08 if _gs.tiles.get(p, "") == "agua" else 0.25


## Dónde se para una tropa en esa casilla (en la cima si es montaña).
func cell_pos(p: Vector2i) -> Vector3:
	var pos := Hex.to_world(p) + Vector3(0, tile_height(p), 0)
	if _gs.tiles.get(p, "") == "montana":
		pos.y += 0.95
	return pos


func state() -> GameState:
	return _gs


func unit_node(id: int) -> Node3D:
	return _unit_nodes.get(id, null)


func viewer_sees(p: Vector2i) -> bool:
	return _gs.visible_tiles(viewer).has(p)


## Pone el bote si la casilla es agua.
func set_water(node: Node3D, p: Vector2i) -> void:
	var water: bool = _gs.tiles.get(p, "") == "agua"
	node.get_node("Boat").visible = water
	var model: Node3D = node.get_node("Model")
	var s: float = UNIT_SCALE.get(node.get_meta("type"), 0.39)
	if node.get_meta("type") == "capitan" and water:
		# En la proa del galeón (así se ve desde arriba), un poco más chico
		model.position = Vector3(0, 0.36, 0.32)
		model.scale = Vector3.ONE * s * 0.8
	else:
		model.position = Vector3(0, 0.12 if water else 0.0, 0)
		model.scale = Vector3.ONE * s


func place(node: Node3D, p: Vector2i) -> void:
	node.position = cell_pos(p)
	set_water(node, p)


func forget_unit(id: int) -> void:
	if _unit_nodes.has(id):
		_unit_nodes[id].queue_free()
		_unit_nodes.erase(id)


var _time := 0.0


func _process(delta: float) -> void:
	# Los barcos se mecen en el agua
	_time += delta
	for id in _unit_nodes:
		var n: Node3D = _unit_nodes[id]
		var boat: Node3D = n.get_node_or_null("Boat")
		if boat and boat.visible:
			boat.rotation.z = sin(_time * 1.7 + id) * 0.05
			boat.rotation.x = sin(_time * 1.3 + id * 2) * 0.03
			boat.position.y = -0.05 + sin(_time * 2.1 + id) * 0.02


func busy() -> bool:
	return anim != null and anim.busy()


## Actualiza tropas y ciudades para que coincidan con el estado de la partida.
func sync() -> void:
	var seen := _gs.visible_tiles(viewer)
	for p in _tile_nodes:
		var known := _gs.is_explored(viewer, p)
		_tile_nodes[p].visible = known
		_fog_nodes[p].visible = not known
		_dim_nodes[p].visible = known and not seen.has(p)

	if _gs.record_events and not _gs.events.is_empty():
		var evs := _gs.events.duplicate()
		_gs.events.clear()
		# Los turnos de los bots se animan más rápido
		anim.speed = 1.7 if _gs.current_player().is_bot else 1.0
		anim.enqueue(evs)
	for id in _unit_nodes.keys():
		if not _gs.units.has(id) and not anim.dying.has(id) and not anim.busy_ids.has(id):
			_unit_nodes[id].queue_free()
			_unit_nodes.erase(id)
	for id in _gs.units:
		var u: GameState.Unit = _gs.units[id]
		if not _unit_nodes.has(id):
			var n := _make_unit(u)
			_unit_nodes[id] = n
			add_child(n)
			place(n, u.pos)
			n.visible = u.owner == viewer or seen.has(u.pos)
		var node: Node3D = _unit_nodes[id]
		if not anim.busy_ids.has(id):
			place(node, u.pos)
			node.visible = u.owner == viewer or seen.has(u.pos)
		if anim.busy_ids.has(id):
			continue  # La vida se actualiza cuando la animación muestra el golpe
		var label: Label3D = node.get_node("Label")
		var text := "%s %d" % [u.stats()["sigla"], u.hp]
		if u.capturing:
			text += " (!)"
		label.text = text
		var done := u.exhausted or u.attacked or (u.moved and _gs.attack_targets(u).is_empty())
		label.modulate = Color(0.6, 0.6, 0.6) if (done and u.owner == _gs.current) else Color.WHITE

	for pos in _city_nodes:
		var c: GameState.City = _gs.cities[pos]
		var node: Node3D = _city_nodes[pos]
		node.visible = _gs.is_explored(viewer, pos)
		var city_key := "%d|%d" % [c.owner, c.level]
		if _city_keys.get(pos, "") != city_key:
			_city_keys[pos] = city_key
			_build_city_houses(node.get_node("Houses"), c)
		var label: Label3D = node.get_node("Label")
		label.text = "%s  Nv.%d" % [c.name, c.level]
		if not c.pending_rewards.is_empty() and c.owner == _gs.current:
			label.text += "  ★"

	# Recursos, edificios y llamas: se reconstruyen solo si cambiaron.
	var wanted := {}
	for p in _gs.resources:
		wanted[p] = "r_" + _gs.resources[p]
	for p in _gs.buildings:
		wanted[p] = "b_" + _gs.buildings[p] + "@" + str(_gs.tile_owner(p))
	for p in _gs.flames:
		wanted[p] = wanted.get(p, "") + "|fuego"
	for p in _gs.roads:
		var mask := ""
		for n in Hex.neighbors(p):
			mask += "1" if _gs.has_road(n) else "0"
		wanted[p] = wanted.get(p, "") + "|camino" + mask
	for p in _gs.ports:
		wanted[p] = wanted.get(p, "") + "|puerto"
	for p in _deco_nodes.keys():
		if wanted.get(p, "") != _deco_nodes[p][0]:
			_deco_nodes[p][1].queue_free()
			_deco_nodes.erase(p)
	for p in wanted:
		if not _deco_nodes.has(p):
			var n := _make_deco(p, wanted[p])
			add_child(n)
			_deco_nodes[p] = [wanted[p], n]
		_deco_nodes[p][1].visible = _gs.is_explored(viewer, p)


func clear_highlights() -> void:
	for ov in _overlays.values():
		ov.visible = false


func highlight(cells: Array, kind: String) -> void:
	var mat := _mat("hl_" + kind, HIGHLIGHT_COLORS[kind], true)
	for p in cells:
		if _overlays.has(p):
			var ov: MeshInstance3D = _overlays[p]
			ov.material_override = mat
			ov.visible = true


# --- Construcción de figuras -----------------------------------------------------

func _add_decoration(p: Vector2i, terrain: String, parent: Node3D) -> void:
	var base := Hex.to_world(p) + Vector3(0, tile_height(p), 0)
	var variant := absi(p.x * 31 + p.y * 17)
	var turn := KK_TILE_ROT + PI / 3.0 * (variant % 6)
	if terrain == "bosque":
		var tree := _model(["trees_A_medium", "trees_B_medium", "trees_A_large"][variant % 3], 1.0, turn)
		tree.position = base
		parent.add_child(tree)
	elif terrain == "montana":
		var m := _model(["mountain_A", "mountain_B", "mountain_C"][variant % 3], 1.0, turn)
		m.position = base
		parent.add_child(m)


var _cloud_scene: PackedScene


func _set_material(node: Node, m: Material) -> void:
	if node is MeshInstance3D:
		(node as MeshInstance3D).material_override = m
		(node as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for child in node.get_children():
		_set_material(child, m)


var _cloud_mesh_cache: SphereMesh
func _cloud_mesh() -> SphereMesh:
	if _cloud_mesh_cache == null:
		_cloud_mesh_cache = SphereMesh.new()
		_cloud_mesh_cache.radial_segments = 20
		_cloud_mesh_cache.rings = 10
	return _cloud_mesh_cache


## Nubes con sombreado propio (no dependen de la luz): arriba blancas y hacia
## (los colores pasan de 1 porque el tono de la cámara oscurece los blancos)
## los bordes azuladas, para que se vean esponjosas y no como manchas planas.
var _fog_tile_mesh: ArrayMesh


func _tile_mesh_fog() -> ArrayMesh:
	if _fog_tile_mesh == null:
		_fog_tile_mesh = make_hex_mesh(0.96, 0.25)
	return _fog_tile_mesh


func _cloud_base_mat() -> ShaderMaterial:
	if not _materials.has("nube_base"):
		var m: ShaderMaterial = _cloud_mat().duplicate()
		m.set_shader_parameter("top_color", Vector3(1.05, 1.3, 1.75))
		m.set_shader_parameter("side_color", Vector3(0.55, 0.7, 1.05))
		_materials["nube_base"] = m
	return _materials["nube_base"]


func _cloud_mat() -> ShaderMaterial:
	if not _materials.has("nube2"):
		var sh := Shader.new()
		sh.code = """
shader_type spatial;
render_mode unshaded, cull_back;
uniform vec3 top_color = vec3(2.2, 2.25, 2.35);
uniform vec3 side_color = vec3(1.05, 1.2, 1.55);
varying vec3 n_world;
void vertex() { n_world = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz); }
void fragment() {
	float up = clamp(n_world.y * 0.5 + 0.5, 0.0, 1.0);
	float rim = 1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	vec3 c = mix(side_color, top_color, smoothstep(0.35, 0.95, up));
	ALBEDO = mix(c, side_color * 0.9, rim * 0.35);
}
"""
		var m := ShaderMaterial.new()
		m.shader = sh
		_materials["nube2"] = m
	return _materials["nube2"]


func _puff(mesh: Mesh, mat: Material, pos: Vector3, size: float) -> MeshInstance3D:
	# (el material es compartido por todas las nubes)
	var m := MeshInstance3D.new()
	m.mesh = mesh
	m.material_override = mat
	m.position = pos
	m.scale = Vector3(size, size * 0.55, size)
	m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return m


## Instancia un modelo de assets/kaykit (escala y giro para encajar en la casilla).
func _model(model_name: String, scale_mul := 1.0, rot := 0.0, tint := Color.WHITE) -> Node3D:
	if not _models.has(model_name):
		_models[model_name] = load("res://assets/kaykit/%s.gltf" % model_name)
	var n: Node3D = (_models[model_name] as PackedScene).instantiate()
	_fix_materials(n, tint)
	n.scale = Vector3.ONE * KK_SCALE * scale_mul
	n.rotation.y = rot
	return n


## KayKit pinta con una pequeña paleta de colores en una sola imagen: hay que leerla
## "pixel por pixel" (sin suavizar), o los colores se mezclan entre sí.
func _fix_materials(node: Node, tint := Color.WHITE) -> void:
	if node is MeshInstance3D:
		var mi := node as MeshInstance3D
		for i in mi.mesh.get_surface_count():
			var key := "kk_%d_%s" % [mi.mesh.surface_get_material(i).get_instance_id(), tint.to_html()]
			if not _materials.has(key):
				var m := (mi.mesh.surface_get_material(i) as BaseMaterial3D).duplicate() as BaseMaterial3D
				m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
				m.albedo_color = tint
				_materials[key] = m
			mi.set_surface_override_material(i, _materials[key])
	for child in node.get_children():
		_fix_materials(child, tint)


## Los edificios de KayKit vienen en rojo: se cambia la zona roja de su textura
## por el color del jugador.
var _team_textures := {}


func _team_texture(color: Color) -> Texture2D:
	var key := color.to_html()
	if _team_textures.has(key):
		return _team_textures[key]
	var src: Texture2D = load("res://assets/kaykit/hexagons_medieval.png")
	var img := src.get_image()
	if img.is_compressed():
		img.decompress()
	img = img.duplicate()
	var w := img.get_width()
	var h := img.get_height()
	var x0 := w / 8
	var x1 := w / 4
	var y0 := int(h * 0.78)
	for y in range(y0, h):
		for x in range(x0, x1):
			var c := img.get_pixel(x, y)
			var v := maxf(c.r, maxf(c.g, c.b))
			var f := clampf(v * 1.12, 0.0, 1.15)
			img.set_pixel(x, y, Color(color.r * f, color.g * f, color.b * f, c.a))
	var tex := ImageTexture.create_from_image(img)
	_team_textures[key] = tex
	return tex


func _tint_team(node: Node, color: Color) -> void:
	if node is MeshInstance3D:
		var mi := node as MeshInstance3D
		for i in mi.mesh.get_surface_count():
			var base := mi.get_surface_override_material(i)
			if base == null:
				base = mi.mesh.surface_get_material(i)
			var key := "team_%d_%s" % [base.get_instance_id(), color.to_html()]
			if not _materials.has(key):
				var m := (base as BaseMaterial3D).duplicate() as BaseMaterial3D
				m.albedo_texture = _team_texture(color)
				_materials[key] = m
			mi.set_surface_override_material(i, _materials[key])
	for child in node.get_children():
		_tint_team(child, color)


func _make_deco(p: Vector2i, key: String) -> Node3D:
	var root := Node3D.new()
	root.position = Hex.to_world(p) + Vector3(0, tile_height(p), 0)
	if key.begins_with("r_frutos"):
		root.add_child(_shape(SphereMesh.new(), Vector3(0.28, 0.22, 0.28), _mat("arbusto", Color(0.2, 0.55, 0.2)), Vector3(0.45, 0.1, 0.25)))
		for o in [Vector3(0.38, 0.2, 0.2), Vector3(0.52, 0.18, 0.3), Vector3(0.45, 0.24, 0.35)]:
			root.add_child(_shape(SphereMesh.new(), Vector3(0.07, 0.07, 0.07), _mat("fruta", Color(0.9, 0.15, 0.2)), o))
	elif key.begins_with("r_troncos"):
		var lumber := _model("resource_lumber", 1.2, 0.4)
		lumber.position = Vector3(0.35, 0, 0.3)
		root.add_child(lumber)
	elif key.begins_with("r_campo"):
		var dirt := _model("building_dirt", 0.55, KK_TILE_ROT)
		dirt.position = Vector3(0.25, 0.01, 0.3)
		root.add_child(dirt)
	elif key.begins_with("r_arboleda"):
		root.add_child(_shape(CylinderMesh.new(), Vector3(0.2, 0.15, 0.2), _mat("tronco", Color(0.5, 0.33, 0.18)), Vector3(0.45, 0.08, 0.3)))
	elif key.begins_with("b_granja"):
		var grain := _model("building_grain", 1.0, KK_TILE_ROT)
		root.add_child(grain)
	elif key.begins_with("b_aserradero"):
		var mill := _model("building_lumbermill_red", 0.55, 0.0)
		var mill_owner := _gs.tile_owner(p)
		if mill_owner >= 0:
			_tint_team(mill, _gs.players[mill_owner].color)
		mill.position = Vector3(0.3, 0, 0.25)
		root.add_child(mill)
	var road_at := key.find("|camino")
	if road_at != -1:
		var road_mat := _mat("camino", Color(0.62, 0.5, 0.33))
		var disc := CylinderMesh.new()
		disc.radial_segments = 8
		root.add_child(_shape(disc, Vector3(0.38, 0.02, 0.38), road_mat, Vector3(0, 0.012, 0)))
		var mask := key.substr(road_at + 7, 6)
		for i in 6:
			if mask[i] != "1":
				continue
			var dir := Hex.to_world(Hex.DIRS[i])
			var strip := _shape(BoxMesh.new(), Vector3(0.22, 0.02, dir.length() / 2.0), road_mat, dir / 4.0 + Vector3(0, 0.012, 0))
			strip.rotation.y = atan2(dir.x, dir.z)
			root.add_child(strip)
	if key.contains("|puerto"):
		var wood := _mat("madera_casa", Color(0.55, 0.38, 0.2))
		root.add_child(_shape(BoxMesh.new(), Vector3(0.7, 0.08, 0.4), wood, Vector3(0, 0.12, 0)))
		for o in [Vector3(-0.3, 0, -0.15), Vector3(0.3, 0, -0.15), Vector3(-0.3, 0, 0.15), Vector3(0.3, 0, 0.15)]:
			root.add_child(_shape(CylinderMesh.new(), Vector3(0.06, 0.15, 0.06), wood, o + Vector3(0, 0.05, 0)))
		root.add_child(_shape(CylinderMesh.new(), Vector3(0.04, 0.5, 0.04), wood, Vector3(0.2, 0.5, 0)))
		root.add_child(_shape(BoxMesh.new(), Vector3(0.02, 0.22, 0.3), _mat("vela", Color(0.95, 0.93, 0.85)), Vector3(0.2, 0.6, 0.15)))
	if key.contains("|fuego"):
		var fire_mat := _mat("fuego", Color(1.0, 0.45, 0.05, 0.75), true)
		for o in [Vector3(-0.25, 0, 0), Vector3(0.2, 0, -0.2), Vector3(0.05, 0, 0.25)]:
			var cone := CylinderMesh.new()
			cone.top_radius = 0.0
			cone.bottom_radius = 0.5
			cone.height = 1.0
			root.add_child(_shape(cone, Vector3(0.4, 0.6, 0.4), fire_mat, o + Vector3(0, 0.3, 0)))
	return root


func _shape(mesh: PrimitiveMesh, scale_v: Vector3, mat: Material, pos: Vector3) -> MeshInstance3D:
	var m := MeshInstance3D.new()
	m.mesh = mesh
	m.material_override = mat
	m.scale = scale_v
	m.position = pos
	return m


func _make_city(pos: Vector2i) -> Node3D:
	var root := Node3D.new()
	root.position = Hex.to_world(pos) + Vector3(0, tile_height(pos), 0)
	var houses := Node3D.new()
	houses.name = "Houses"
	root.add_child(houses)
	var label := Label3D.new()
	label.name = "Label"
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size = 80
	label.outline_size = 20
	label.pixel_size = 0.003
	label.no_depth_test = true
	label.font = KoloniaTheme.font()
	label.outline_modulate = KoloniaTheme.INK
	label.position = Vector3(0, 0.15, 0.95)
	root.add_child(label)
	return root


## Arma los edificios de la ciudad según su dueño y su nivel. La tropa se para al
## frente, así que los edificios van atrás y a los lados.
func _build_city_houses(houses: Node3D, c: GameState.City) -> void:
	for child in houses.get_children():
		child.queue_free()
	var slots := [Vector3(0, 0, -0.42), Vector3(-0.52, 0, -0.02), Vector3(0.52, 0, -0.02), Vector3(-0.45, 0, 0.5), Vector3(0.48, 0, 0.48)]
	if c.owner == GameState.NO_PLAYER:
		var ruin := _model("building_destroyed", 0.95, 0.3)
		ruin.position = Vector3(0, 0, -0.3)
		houses.add_child(ruin)
		var scaf := _model("building_scaffolding", 0.5, 0.0)
		scaf.position = Vector3(-0.5, 0, 0.1)
		houses.add_child(scaf)
		return
	var color := "red"
	var team: Color = _gs.players[c.owner].color
	var pieces: Array = ["home_A"]
	if c.level >= 2:
		pieces = ["home_B", "home_A", "well"]
	if c.level >= 3:
		pieces = ["market", "home_A", "home_B", "well"]
	if c.level >= 4:
		pieces = ["castle", "home_A", "home_B", "tower_A", "well"]
	for i in pieces.size():
		var s := 0.95 if i == 0 else 0.72
		match pieces[i]:
			"castle":
				s = 0.62
			"market":
				s = 0.8
			"well":
				s = 0.6
		var b := _model("building_%s_%s" % [pieces[i], color], s, PI)
		_tint_team(b, team)
		b.position = slots[i]
		houses.add_child(b)
	var flag := _model("flag_%s" % color, 2.6, 0.0)
	_tint_team(flag, team)
	flag.position = Vector3(0.7, 0, 0.25)
	houses.add_child(flag)


## Tamaño de cada modelo de tropa en el tablero y altura de su etiqueta.
const UNIT_SCALE := {"jinete": 0.33, "jinete_lancero": 0.33, "catapulta": 0.3, "escudero": 0.42,
	"super_caballero": 0.45, "sacerdote": 0.45}
const UNIT_LABEL_Y := {"jinete": 1.45, "jinete_lancero": 1.45, "catapulta": 1.15, "escudero": 1.3,
	"super_caballero": 1.5, "sacerdote": 1.4}


func _make_unit(u: GameState.Unit) -> Node3D:
	var root := Node3D.new()
	root.set_meta("type", u.type)
	root.set_meta("owner", u.owner)
	root.set_meta("sigla", u.stats()["sigla"])
	var model := _unit_model(u.type, u.owner, UNIT_SCALE.get(u.type, 0.39))
	model.name = "Model"
	root.add_child(model)
	# El capitán navega en su galeón; las demás tropas, en un bote.
	var boat := _unit_model("barco" if u.type == "capitan" else "bote", u.owner, 0.5 if u.type == "capitan" else 0.42)
	boat.name = "Boat"
	boat.position.y = -0.05
	boat.visible = false
	root.add_child(boat)
	var label := Label3D.new()
	label.name = "Label"
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.font_size = 96
	label.outline_size = 24
	label.pixel_size = 0.003
	label.no_depth_test = true
	label.font = KoloniaTheme.font()
	label.outline_modulate = KoloniaTheme.INK
	label.position = Vector3(0, UNIT_LABEL_Y.get(u.type, 1.25), 0)
	root.add_child(label)
	return root


## Carga el modelo de assets/tropas y lo pinta con el color del jugador: las piezas
## con material "K_Tribu" (y "K_TribuOscuro") son las que cambian de color.
func _unit_model(type: String, owner_id: int, scale_v: float) -> Node3D:
	var key := "tropa_" + type
	if not _models.has(key):
		_models[key] = load("res://assets/tropas/%s.glb" % type)
	var n: Node3D = (_models[key] as PackedScene).instantiate()
	n.scale = Vector3.ONE * scale_v
	TroopModel.setup(n, type)
	if owner_id >= 0:
		_recolor(n, _gs.players[owner_id].color)
	return n


func _recolor(node: Node, color: Color) -> void:
	if node is MeshInstance3D:
		var mi := node as MeshInstance3D
		for i in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(i)
			if m == null or not m.resource_name.begins_with("K_Tribu"):
				continue
			var dark := m.resource_name == "K_TribuOscuro"
			var key := "tribu_%s_%s_%d" % [color.to_html(), dark, m.get_instance_id()]
			if not _materials.has(key):
				var nm := (m as BaseMaterial3D).duplicate() as BaseMaterial3D
				nm.albedo_color = color.darkened(0.3) if dark else color
				_materials[key] = nm
			mi.set_surface_override_material(i, _materials[key])
	for child in node.get_children():
		_recolor(child, color)


func _capsule(mat: Material, r: float, h: float, pos: Vector3) -> MeshInstance3D:
	var m := MeshInstance3D.new()
	var cap := CapsuleMesh.new()
	cap.radius = r
	cap.height = h
	m.mesh = cap
	m.material_override = mat
	m.position = pos
	return m


func _mat(key: String, color: Color, transparent := false) -> StandardMaterial3D:
	if _materials.has(key):
		return _materials[key]
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	if transparent:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_materials[key] = m
	return m


## Prisma hexagonal (punta plana) con la cara superior en y = height.
static func make_hex_mesh(radius: float, height: float) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var corners: Array[Vector3] = []
	for i in 6:
		var a := deg_to_rad(60.0 * i)
		corners.append(Vector3(cos(a) * radius, 0.0, sin(a) * radius))
	var up := Vector3(0, height, 0)
	for i in 6:
		var a := corners[i]
		var b := corners[(i + 1) % 6]
		# Cara superior
		st.set_normal(Vector3.UP)
		st.add_vertex(up)
		st.set_normal(Vector3.UP)
		st.add_vertex(a + up)
		st.set_normal(Vector3.UP)
		st.add_vertex(b + up)
		# Lado
		var n := ((a + b) / 2.0).normalized()
		for v in [a, a + up, b + up, a, b + up, b]:
			st.set_normal(n)
			st.add_vertex(v)
	return st.commit()
