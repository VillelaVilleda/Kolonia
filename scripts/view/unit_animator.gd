class_name UnitAnimator
extends Node
## Anima en el tablero lo que pasó en la partida (moverse, atacar, recibir daño, morir...).
## Lee los eventos que deja GameState y los reproduce uno tras otro.

const HOP_TIME := 0.26          ## segundos por casilla al caminar
const HOP_TIME_FAST := 0.15

var board: BoardView
var _queue: Array = []
var _running := false
var busy_ids := {}               ## tropas que se están animando (sync no las mueve)
var dying := {}                  ## tropas muertas cuyo nodo sigue vivo hasta terminar
## Más rápido durante los turnos de los bots (lo pone el tablero).
var speed := 1.0


func _wait(t: float) -> Signal:
	return get_tree().create_timer(t / speed).timeout


func busy() -> bool:
	return _running or not _queue.is_empty()


func enqueue(events: Array) -> void:
	for e in events:
		if e["t"] == "nace":
			pass
		elif e.has("id"):
			busy_ids[e["id"]] = true
		if e.has("objetivo"):
			busy_ids[e["objetivo"]] = true
		if e["t"] == "muerte":
			dying[e["id"]] = true
	_queue.append_array(events)
	if not _running:
		_run()


func _run() -> void:
	_running = true
	await get_tree().process_frame  # sync crea los nodos nuevos
	while not _queue.is_empty():
		var e: Dictionary = _queue.pop_front()
		await _play(e)
	_running = false
	busy_ids.clear()
	board.sync()


func _node(id: int) -> Node3D:
	return board.unit_node(id)


func _visible(n: Node3D) -> bool:
	return n != null and is_instance_valid(n) and n.visible


func _play(e: Dictionary) -> void:
	match e["t"]:
		"mover":
			await _move(e)
		"ataque":
			await _attack(e)
		"golpe":
			await _attack({"id": e["id"], "hacia": e["hacia"], "corto": true})
		"dano":
			_hurt(e)
			var n := _node(e["id"])
			if _visible(n):
				await _wait(0.2)
		"muerte":
			await _die(e)
		"habilidad":
			await _ability(e)
		"nace":
			_spawn(e)


# --- Moverse ---------------------------------------------------------------------------

func _move(e: Dictionary) -> void:
	var n := _node(e["id"])
	if n == null:
		return
	var from: Vector2i = e["desde"]
	var to: Vector2i = e["hasta"]
	var type: String = n.get_meta("type")
	var owner_id: int = n.get_meta("owner")
	var seen := board.viewer_sees(from) or board.viewer_sees(to)
	if not seen:
		board.place(n, to)
		return
	n.visible = true
	var fast: bool = e.get("rapido", false)
	var path := _path(owner_id, from, to)
	var model: Node3D = n.get_node("Model")
	TroopModel.loop(model, TroopModel.walk_anim(type, fast), (1.4 if not fast else 1.0) * speed)
	var t_hop := (HOP_TIME_FAST if fast else HOP_TIME) / speed
	for i in range(1, path.size()):
		var a: Vector2i = path[i - 1]
		var b: Vector2i = path[i]
		await _turn_to(n, board.cell_pos(b) - board.cell_pos(a), 0.08)
		board.set_water(n, b)
		var tw := create_tween()
		tw.tween_property(n, "position", board.cell_pos(b), t_hop)
		await tw.finished
	TroopModel.play_idle(model, type)


## Camino casilla por casilla (el más corto por donde la tropa puede pasar).
func _path(owner_id: int, from: Vector2i, to: Vector2i) -> Array:
	var gs := board.state()
	if Hex.distance(from, to) <= 1:
		return [from, to]
	var prev := {from: from}
	var frontier := [from]
	while not frontier.is_empty() and not prev.has(to):
		var nxt := []
		for c in frontier:
			for nb in Hex.neighbors(c):
				if prev.has(nb) or not gs.tiles.has(nb):
					continue
				if Hex.distance(nb, to) > Hex.distance(from, to) + 2:
					continue
				if not gs.can_enter(owner_id, c, nb):
					continue
				prev[nb] = c
				nxt.append(nb)
		frontier = nxt
	if not prev.has(to):
		return [from, to]
	var path := [to]
	while path[0] != from:
		path.push_front(prev[path[0]])
	return path


func _turn_to(n: Node3D, dir: Vector3, time := 0.12) -> void:
	if Vector2(dir.x, dir.z).length() < 0.01:
		return
	var target := atan2(dir.x, dir.z)
	var cur := n.rotation.y
	var diff := wrapf(target - cur, -PI, PI)
	if absf(diff) < 0.05:
		return
	var tw := create_tween()
	tw.tween_property(n, "rotation:y", cur + diff, time)
	await tw.finished


# --- Atacar ----------------------------------------------------------------------------

func _attack(e: Dictionary) -> void:
	var n := _node(e["id"])
	if n == null:
		return
	var type: String = n.get_meta("type")
	var target_pos: Vector3 = board.cell_pos(e["hacia"])
	var from_pos: Vector3 = n.position
	if not (_visible(n) or board.viewer_sees(e["hacia"])):
		return
	await _turn_to(n, target_pos - from_pos, 0.12)
	var model: Node3D = n.get_node("Model")
	var anim: String = TroopModel.ATTACK.get(type, "kol/Espadazo")
	var spd := (1.5 if e.get("corto", false) else 1.0) * speed
	TroopModel.play(model, anim, type, true, spd)
	var hit_time: float = TroopModel.HIT_TIME.get(anim, 0.4) / spd
	var dist := Vector2(target_pos.x - from_pos.x, target_pos.z - from_pos.z).length()
	if TroopModel.PROJECTILE.has(type) and dist > 0.5:
		await get_tree().create_timer(hit_time).timeout
		await _projectile(TroopModel.PROJECTILE[type], from_pos, target_pos, n.get_meta("owner"))
	else:
		# Se acerca un poco al enemigo para golpear y luego regresa
		var lunge := from_pos + (target_pos - from_pos) * 0.28
		var tw := create_tween()
		tw.tween_property(n, "position", lunge, hit_time * 0.8).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
		tw.tween_interval(0.25)
		tw.tween_property(n, "position", from_pos, 0.3).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		await get_tree().create_timer(hit_time).timeout


func _projectile(kind: String, from: Vector3, to: Vector3, owner_id: int) -> void:
	var p := MeshInstance3D.new()
	var mat := StandardMaterial3D.new()
	var height := 0.9
	var time := 0.45
	match kind:
		"flecha":
			var m := CylinderMesh.new()
			m.top_radius = 0.015
			m.bottom_radius = 0.015
			m.height = 0.45
			p.mesh = m
			mat.albedo_color = Color(0.45, 0.28, 0.12)
			height = 0.7
			time = 0.38
		"piedra":
			var m := SphereMesh.new()
			m.radius = 0.12
			m.height = 0.24
			p.mesh = m
			mat.albedo_color = Color(0.55, 0.55, 0.55)
			height = 1.8
			time = 0.7
		_:
			var m := SphereMesh.new()
			m.radius = 0.1
			m.height = 0.2
			p.mesh = m
			mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			mat.albedo_color = Color(1.4, 1.5, 0.7)
			height = 0.5
			time = 0.4
	p.material_override = mat
	board.add_child(p)
	var a := from + Vector3(0, 0.55, 0)
	var b := to + Vector3(0, 0.45, 0)
	var step := func(t: float) -> void:
		var pos := a.lerp(b, t) + Vector3(0, sin(t * PI) * height, 0)
		var vel := (b - a) + Vector3(0, cos(t * PI) * PI * height, 0)
		p.position = pos
		if kind == "flecha" and vel.length() > 0.01:
			p.basis = Basis(Quaternion(Vector3.UP, vel.normalized()))
	var tw := create_tween()
	tw.tween_method(step, 0.0, 1.0, time / speed)
	await tw.finished
	p.queue_free()


func _hurt(e: Dictionary) -> void:
	var n := _node(e["id"])
	if not _visible(n):
		return
	var type: String = n.get_meta("type")
	TroopModel.play(n.get_node("Model"), TroopModel.hurt_anim(type), type)
	popup_text(n.position + Vector3(0, 1.0, 0), "-%d" % e["dano"], Color(1, 0.35, 0.3))
	if e.has("vida"):
		(n.get_node("Label") as Label3D).text = "%s %d" % [n.get_meta("sigla"), e["vida"]]
	_flash(n)


func _flash(n: Node3D) -> void:
	# Pequeño "salto" de la tropa al recibir el golpe
	var model: Node3D = n.get_node("Model")
	var s := model.scale
	var tw := create_tween()
	tw.tween_property(model, "scale", s * Vector3(1.15, 0.85, 1.15), 0.06)
	tw.tween_property(model, "scale", s, 0.15)


func _die(e: Dictionary) -> void:
	var n := _node(e["id"])
	dying.erase(e["id"])
	if n == null:
		return
	if not _visible(n):
		board.forget_unit(e["id"])
		return
	var type: String = n.get_meta("type")
	var model: Node3D = n.get_node("Model")
	n.get_node("Label").visible = false
	var anim := TroopModel.death_anim(type)
	if anim != "":
		TroopModel.play(model, anim, type, false)
		await _wait(0.7)
	else:
		var tw0 := create_tween()
		tw0.tween_property(model, "rotation:z", PI / 2.2, 0.45).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
		await tw0.finished
	var tw := create_tween()
	tw.tween_property(n, "position:y", n.position.y - 0.5, 0.5).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(n, "scale", Vector3.ONE * 0.6, 0.5)
	await tw.finished
	board.forget_unit(e["id"])


func _ability(e: Dictionary) -> void:
	var n := _node(e["id"])
	if not _visible(n):
		return
	var type: String = n.get_meta("type")
	var model: Node3D = n.get_node("Model")
	match e["nombre"]:
		"curacion":
			TroopModel.play(model, "kol/Hechizo", type)
			await _wait(0.5)
			for id in e.get("curados", []):
				var h := _node(id)
				if _visible(h):
					popup_text(h.position + Vector3(0, 1.0, 0), "+%d" % e["cantidad"], Color(0.4, 1, 0.45))
					_flash(h)
			await _wait(0.3)
		"muralla":
			await _turn_to(n, board.cell_pos(e["hacia"]) - n.position)
			TroopModel.play(model, "kol/Hechizo", type)
			await _wait(0.55)
		"embestida":
			TroopModel.play(model, "kol/Festejo", type, true, 1.6)
			await _wait(0.25)


func _spawn(e: Dictionary) -> void:
	var n := _node(e["id"])
	if not _visible(n):
		return
	var model: Node3D = n.get_node("Model")
	var s := model.scale
	model.scale = s * 0.05
	var tw := create_tween()
	tw.tween_property(model, "scale", s, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	TroopModel.play(model, "general/Spawn_Ground", n.get_meta("type"))


## Texto que sube y se desvanece (daño, curación).
func popup_text(pos: Vector3, text: String, color: Color) -> void:
	var l := Label3D.new()
	l.text = text
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.font_size = 120
	l.outline_size = 28
	l.pixel_size = 0.003
	l.no_depth_test = true
	l.font = KoloniaTheme.font()
	l.modulate = color
	l.outline_modulate = KoloniaTheme.INK
	l.position = pos
	board.add_child(l)
	var tw := l.create_tween()
	tw.tween_property(l, "position:y", pos.y + 0.7, 0.9).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.parallel().tween_property(l, "modulate:a", 0.0, 0.9).set_delay(0.35)
	tw.tween_callback(l.queue_free)
