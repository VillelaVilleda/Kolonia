class_name SimpleBot
extends RefCounted
## Bot sencillo: cosecha y construye, mejora sus ciudades, usa las habilidades
## de sus héroes, ataca si puede y avanza hacia la ciudad o tropa enemiga
## más cercana.

## on_step se llama después de cada acción (para refrescar la pantalla).
## delay = segundos de pausa entre acciones (0 = sin pausas, para pruebas).
static func play_turn(gs: GameState, tree: SceneTree, on_step: Callable, delay: float = 0.35) -> void:
	var me := gs.current
	await _economy(gs, tree, on_step, delay)

	for u in gs.units_of(me):
		if gs.winner != GameState.NO_PLAYER:
			return
		if not gs.units.has(u.id) or u.exhausted:
			continue
		if _try_ability(gs, u):
			await _step(tree, on_step, delay)
			continue
		if _try_attack(gs, u):
			await _step(tree, on_step, delay)
			continue
		var target: Variant = _choose_target(gs, u)
		if target != null:
			# Distancia real caminando (rodea ríos y montañas).
			var dist := _walk_distances(gs, target)
			var best_tile := u.pos
			var best_d: int = dist.get(u.pos, 999)
			for p in gs.reachable(u):
				var d: int = dist.get(p, 999)
				if d < best_d:
					best_d = d
					best_tile = p
			if best_tile != u.pos and gs.move_unit(u, best_tile):
				await _step(tree, on_step, delay)
		if gs.units.has(u.id) and _try_attack(gs, u):
			await _step(tree, on_step, delay)

	for c in gs.cities.values():
		if c.owner != me:
			continue
		var options := gs.trainable_types(me)
		options.shuffle()
		for t in options:
			if gs.can_train(c.pos, t) == "":
				gs.train(c.pos, t)
				await _step(tree, on_step, delay)
				break


static func _economy(gs: GameState, tree: SceneTree, on_step: Callable, delay: float) -> void:
	for c in gs.cities.values():
		if c.owner != gs.current:
			continue
		for p in gs.city_territory(c.pos):
			for a in gs.tile_actions(p):
				if a["id"] in ["cosechar", "construir", "mejorar_edificio", "puerto"] and a["bloqueo"] == "" \
						and gs.can_afford(gs.current, a["costo"]):
					gs.do_tile_action(p, a["id"])
					await _step(tree, on_step, delay)
					break
		if gs.can_upgrade_city(c.pos) == "":
			gs.upgrade_city(c.pos)
			await _step(tree, on_step, delay)
		while not c.pending_rewards.is_empty():
			gs.choose_reward(c.pos, c.pending_rewards[0].pick_random())
			await _step(tree, on_step, delay)

	# Mejoras: compra la más barata disponible si le sobra oro.
	var best_tech := ""
	for id in Techs.DATA:
		if gs.can_research(id) == "" and (best_tech == "" or Techs.DATA[id]["costo"] < Techs.DATA[best_tech]["costo"]):
			best_tech = id
	if best_tech != "" and gs.current_player().res["oro"] >= int(Techs.DATA[best_tech]["costo"]) + 3:
		gs.research(best_tech)
		await _step(tree, on_step, delay)


	# Caminos: avanza un tramo hacia conectar dos de sus ciudades.
	for i in 2:
		var tile: Variant = _next_road_tile(gs)
		if tile == null or not gs.can_afford(gs.current, GameState.ROAD_COST):
			break
		gs.do_tile_action(tile, "camino")
		await _step(tree, on_step, delay)


## Primera casilla sin camino en la ruta entre dos ciudades propias aún no conectadas.
static func _next_road_tile(gs: GameState) -> Variant:
	var mine: Array[Vector2i] = []
	for c in gs.cities.values():
		if c.owner == gs.current:
			mine.append(c.pos)
	for a in mine:
		var linked := gs.connected_cities(a)
		for b in mine:
			if a == b or b in linked:
				continue
			for p in _land_path(gs, a, b):
				if gs.can_build_road(p):
					return p
	return null


static func _land_path(gs: GameState, from: Vector2i, to: Vector2i) -> Array[Vector2i]:
	var came := {from: from}
	var frontier: Array[Vector2i] = [from]
	while not frontier.is_empty():
		var cur: Vector2i = frontier.pop_front()
		if cur == to:
			break
		for n in Hex.neighbors(cur):
			if gs.is_passable(n) and not came.has(n):
				came[n] = cur
				frontier.append(n)
	var path: Array[Vector2i] = []
	if not came.has(to):
		return path
	var cur := to
	while cur != from:
		path.push_front(cur)
		cur = came[cur]
	return path


## Si se da, el bot espera a que esto devuelva false (animaciones en curso) antes de seguir.
static var is_busy: Callable


static func _step(tree: SceneTree, on_step: Callable, delay: float) -> void:
	on_step.call()
	if delay > 0.0:
		await tree.create_timer(delay).timeout
		var waited := 0
		while is_busy.is_valid() and is_busy.call() and waited < 600:
			await tree.process_frame
			waited += 1


static func _try_ability(gs: GameState, u: GameState.Unit) -> bool:
	for a in u.abilities():
		if gs.can_use_ability(u, a) != "":
			continue
		match a:
			"curacion":
				var missing := 0
				for other in gs.units_of(u.owner):
					if Hex.distance(other.pos, u.pos) <= 3:
						missing += other.max_hp() - other.hp
				if missing >= 4:
					return gs.use_ability(u, a)
			"embestida":
				for n in gs.ability_targets(u, a):
					var dir := n - u.pos
					for step in range(1, 4):
						var p := u.pos + dir * step
						var occ := gs.unit_at(p)
						if not gs.can_enter(u.owner, p - dir, p) or (occ != null and occ.owner == u.owner):
							break
						if occ != null:
							return gs.use_ability(u, a, n)
			"muralla":
				# Solo para defender: quema a enemigos que amenazan una ciudad propia.
				var visible := gs.visible_tiles(u.owner)
				for other in gs.units.values():
					if other.owner == u.owner or Hex.distance(other.pos, u.pos) > 3 or not visible.has(other.pos):
						continue
					for c in gs.cities.values():
						if c.owner == u.owner and Hex.distance(c.pos, other.pos) <= 1:
							return gs.use_ability(u, a, other.pos)
	return false


## Casilla sin explorar más cercana a pie (para salir a explorar).
static func _nearest_unexplored(gs: GameState, u: GameState.Unit) -> Variant:
	var seen := {u.pos: true}
	var frontier: Array[Vector2i] = [u.pos]
	while not frontier.is_empty():
		var cur: Vector2i = frontier.pop_front()
		for n in Hex.neighbors(cur):
			if seen.has(n) or not gs.walkable(n, u.owner):
				continue
			seen[n] = true
			if not gs.is_explored(u.owner, n):
				return n
			frontier.append(n)
	return null


## Pasos a pie desde cada casilla hasta el objetivo (ignorando tropas).
static func _walk_distances(gs: GameState, target: Vector2i) -> Dictionary:
	var dist := {target: 0}
	var frontier: Array[Vector2i] = [target]
	while not frontier.is_empty():
		var cur: Vector2i = frontier.pop_front()
		for n in Hex.neighbors(cur):
			if gs.walkable(n, gs.current) and not dist.has(n):
				dist[n] = dist[cur] + 1
				frontier.append(n)
	return dist


static func _try_attack(gs: GameState, u: GameState.Unit) -> bool:
	var targets := gs.attack_targets(u)
	if targets.is_empty():
		return false
	var weakest: GameState.Unit = targets[0]
	for t in targets:
		if t.hp < weakest.hp:
			weakest = t
	return gs.attack(u, weakest)


## Devuelve la casilla objetivo (Vector2i) o null.
static func _choose_target(gs: GameState, u: GameState.Unit) -> Variant:
	# Si está defendiendo una ciudad propia y hay enemigos cerca, se queda.
	if gs.cities.has(u.pos) and gs.cities[u.pos].owner == u.owner:
		for other in gs.units.values():
			if other.owner != u.owner and Hex.distance(other.pos, u.pos) <= 2:
				return null
	# Si ya está sobre una ciudad ajena, se queda para conquistarla.
	if gs.cities.has(u.pos) and gs.cities[u.pos].owner != u.owner:
		return null
	# El bot respeta la niebla: solo va hacia ciudades que ya descubrió y
	# tropas enemigas que ve ahora mismo.
	var seen := gs.visible_tiles(u.owner)
	var best: Variant = null
	var best_d := 999
	for c in gs.cities.values():
		if c.owner == u.owner or not gs.is_explored(u.owner, c.pos):
			continue
		var occ := gs.unit_at(c.pos)
		if occ != null and occ.owner == u.owner:
			continue  # Otra tropa propia ya la está conquistando.
		var d := Hex.distance(u.pos, c.pos)
		if d < best_d:
			best_d = d
			best = c.pos
	for other in gs.units.values():
		if other.owner != u.owner and seen.has(other.pos):
			var d := Hex.distance(u.pos, other.pos) + 1
			if d < best_d:
				best_d = d
				best = other.pos
	if best == null:
		best = _nearest_unexplored(gs, u)
	return best
