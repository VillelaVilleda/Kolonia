class_name GameState
extends RefCounted
## Toda la lógica y las reglas de una partida, sin nada visual.
## Mantenerla separada de los gráficos permite que los bots (y en el futuro
## el multijugador en línea) usen exactamente las mismas reglas.

signal message(text: String)

## Eventos para animar (mover, atacar, morir...). Solo se guardan si record_events es true;
## el tablero los lee y los borra.
var record_events := false
var events: Array = []


func _event(e: Dictionary) -> void:
	if record_events:
		events.append(e)

const PASSABLE := {"llanura": true, "bosque": true, "montana": false, "agua": false}
const NO_PLAYER := -1
const NO_CELL := Vector2i(9999, 9999)

## Recursos del mapa.
## "una_vez": se cosechan una sola vez. "edificio": se construye encima y produce cada turno.
const RESOURCES := {
	"frutos": {"nombre": "Frutos", "terreno": "llanura", "tipo": "una_vez",
		"da": {"comida": 3}, "puntos": 1},
	"troncos": {"nombre": "Troncos", "terreno": "bosque", "tipo": "una_vez",
		"da": {"madera": 3}, "puntos": 1},
	"campo": {"nombre": "Campo fértil", "terreno": "llanura", "tipo": "edificio",
		"edificio": "granja"},
	"arboleda": {"nombre": "Arboleda", "terreno": "bosque", "tipo": "edificio",
		"edificio": "aserradero"},
}
## "tech": mejora necesaria para construirlo. "tech2"/"costo2": para subirlo a nivel 2
## (en nivel 2 produce el doble).
const BUILDINGS := {
	"granja": {"nombre": "Granja", "costo": {"madera": 3}, "produce": {"comida": 1}, "puntos": 2,
		"tech": "cultivos", "tech2": "cultivos2", "costo2": {"madera": 4}},
	"aserradero": {"nombre": "Aserradero", "costo": {"oro": 2}, "produce": {"madera": 1}, "puntos": 2,
		"tech": "aserradero", "tech2": "aserradero2", "costo2": {"oro": 4}},
}
const RESOURCE_NAMES := {"comida": "comida", "madera": "madera", "oro": "oro"}
const ROAD_COST := {"madera": 1}
const PORT_COST := {"madera": 3}
const PORT_POINTS := 1
## Recursos extra al empezar para todos menos el primero en jugar.
const LATER_START_BONUS := {"oro": 3}
const CONNECTION_POINTS := 1  ## Cada ciudad gana 1 punto por cada ciudad que se conecte con ella
const VETERAN_KILLS := 3       ## Bajas para que una tropa sea veterana
const VETERAN_HP := 5          ## Vida extra de una veterana
const VETERAN_ATTACK := 1.25   ## Multiplicador de ataque de una veterana
## Recompensas al subir de nivel una ciudad: se elige una de las opciones.
## Nivel 2: visión u oro extra. Nivel 3: más oro por turno o ampliar frontera.
## Nivel 4 en adelante: uno de los dos héroes de la tribu.
const REWARDS := {
	"vision": {"icono": "ojo", "nombre": "Visión", "descripcion": "Despeja la niebla en un radio de 3 casillas alrededor de la ciudad"},
	"oro_extra": {"icono": "bolsa", "nombre": "Oro extra", "descripcion": "+%d oro ahora mismo"},
	"oro_turno": {"icono": "oro", "nombre": "Más oro", "descripcion": "La ciudad produce +%d oro por turno"},
	"frontera": {"icono": "bandera", "nombre": "Ampliar frontera", "descripcion": "El territorio de la ciudad crece a 2 casillas de distancia"},
}
const EXTRA_GOLD := 6
const GOLD_PER_TURN_BONUS := 2
const VISION_RADIUS := 3


class Unit:
	var id: int
	var type: String
	var owner: int
	var pos: Vector2i
	var home: Vector2i      ## Ciudad a la que pertenece (ocupa uno de sus espacios).
	var hp: int
	var moved := false
	var attacked := false
	var exhausted := false  ## Recién creada o recién conquistó: no puede actuar este turno.
	var capturing := false  ## Terminó su turno sobre una ciudad ajena.
	var cooldowns := {}     ## habilidad -> turnos de espera restantes
	var kills := 0          ## Enemigos eliminados
	var veteran := false    ## Con 3 bajas sube a veterana: más vida y más ataque

	func stats() -> Dictionary:
		return UnitTypes.DATA[type]

	func max_hp() -> int:
		return int(stats()["vida"]) + (VETERAN_HP if veteran else 0)

	func is_hero() -> bool:
		return UnitTypes.is_hero(type)

	func abilities() -> Array:
		return stats().get("habilidades", [])

	func can_move() -> bool:
		return not exhausted and not moved and not attacked

	func can_attack() -> bool:
		return not exhausted and not attacked


class City:
	var pos: Vector2i
	var name: String
	var owner: int = NO_PLAYER
	var level: int = 1
	var points: int = 0           ## Puntos de mejora acumulados
	var pending_rewards: Array = []  ## Por cada nivel ganado sin elegir: [opción, opción]
	var expanded := false            ## Territorio ampliado a 2 casillas
	var vision := false              ## Despeja la niebla a su alrededor (radio 3)
	var gold_bonus := 0              ## Oro extra por turno

	func max_units() -> int:
		return level + 2

	func points_needed() -> int:
		return level * 2

	func upgrade_cost() -> int:
		return level * 5


class Player:
	var id: int
	var name: String
	var color: Color
	var is_bot: bool
	var tribe := "reino"
	var res := {"comida": 6, "madera": 0, "oro": 2}
	var techs := {}  ## id de mejora -> true
	var alive := true


var radius: int = 5
var tiles: Dictionary = {}      ## Vector2i -> String (tipo de terreno)
var resources: Dictionary = {}  ## Vector2i -> String (recurso sin usar)
var buildings: Dictionary = {}  ## Vector2i -> String (edificio construido)
var building_levels: Dictionary = {}  ## Vector2i -> int
var flames: Dictionary = {}     ## Vector2i -> {"owner": int, "turns": int}
var roads: Dictionary = {}      ## Vector2i -> int (quién lo construyó)
var ports: Dictionary = {}      ## Vector2i -> int (dueño)
var connections: Dictionary = {}  ## "dueño|ciudadA|ciudadB" -> true (ya premiadas)
var territory: Dictionary = {}  ## Vector2i -> Vector2i (ciudad a la que pertenece la casilla)
var cities: Dictionary = {}     ## Vector2i -> City
var units: Dictionary = {}      ## int -> Unit
var players: Array[Player] = []
var current: int = 0
var turn: int = 1
var winner: int = NO_PLAYER

## Niebla de guerra. explored[jugador] guarda las casillas que ese jugador ya vio
## alguna vez (se ve el terreno); las tropas enemigas solo se ven en las casillas
## que están a la vista en este momento.
var fog := true
var explored: Array[Dictionary] = []
const UNIT_VISION := 1  ## Las tropas solo ven las casillas vecinas (2 desde una montaña)
const CITY_VISION := 2
var _next_id: int = 1


# --- Preparación de la partida -------------------------------------------------

const RUIN_NAMES := ["Ruinas del Norte", "Ruinas del Sur", "Fuerte Viejo", "Aldea Perdida",
	"Torre Olvidada", "Ruinas del Valle", "Monasterio", "Ruinas del Lago", "Puesto Abandonado",
	"Ciudad Vieja", "Ruinas del Bosque", "Bastión Caído", "Granja Vieja", "Ruinas del Río"]


## config = null: partida de prueba (Rojo contra Azul en un mapa pequeño).
func setup(seed_value: int, map_radius: int = 5, config: MatchConfig = null) -> void:
	radius = map_radius if config == null else config.radius()
	players.clear()
	units.clear()
	cities.clear()
	resources.clear()
	buildings.clear()
	building_levels.clear()
	flames.clear()
	roads.clear()
	ports.clear()
	connections.clear()
	territory.clear()
	current = 0
	turn = 1
	winner = NO_PLAYER
	var defs: Array = [["Rojo", "Roja", Color(0.85, 0.2, 0.2), false, "reino"],
		["Azul", "Azul", Color(0.2, 0.45, 0.95), true, "reino"]]
	if config != null:
		defs = config.players()
		fog = config.fog
	for d in defs:
		_add_player(d[0], d[2], d[3], d[4])
	# Quien juega después empieza con un poco más (compensa mover primero)
	for i in range(1, players.size()):
		for k in LATER_START_BONUS:
			players[i].res[k] += LATER_START_BONUS[k]
	var city_defs := _place_cities(seed_value, defs)
	var s := seed_value
	for attempt in 300:
		_generate_terrain(s, city_defs)
		if _cities_connected(city_defs):
			break
		s += 1

	for def in city_defs:
		var c := City.new()
		c.pos = def[0]
		c.name = def[1]
		c.owner = def[2]
		cities[c.pos] = c
		for n in Hex.neighbors(c.pos):
			if tiles.has(n):
				territory[n] = c.pos
		if c.owner != NO_PLAYER:
			var u := _spawn_unit("caballero", c.owner, c.pos, c.pos)
			u.exhausted = false
	_place_resources(s, city_defs)
	explored.clear()
	for pl in players:
		explored.append({})
		update_vision(pl.id)
	_start_turn()


func _add_player(player_name: String, color: Color, is_bot: bool, tribe := "reino") -> void:
	var p := Player.new()
	p.id = players.size()
	p.name = player_name
	p.color = color
	p.is_bot = is_bot
	p.tribe = tribe
	for t in Techs.STARTING:
		p.techs[t] = true
	players.append(p)


## Capitales repartidas en círculo cerca del borde y ruinas (ciudades abandonadas)
## lo más separadas posible entre sí.
func _place_cities(seed_value: int, defs: Array) -> Array:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value * 13 + 5
	var n := defs.size()
	var out: Array = []
	var ring := float(radius - 1)
	var offset := rng.randf() * TAU if radius > 5 else PI * 0.83
	for i in n:
		var a := offset + TAU * i / n
		var w := Vector3(cos(a), 0, sin(a)) * ring * 1.6
		var h := Hex.from_world(w)
		while Hex.distance(h, Vector2i.ZERO) > radius - 1:
			w *= 0.92
			h = Hex.from_world(w)
		out.append([h, "Capital " + str(defs[i][1]), i])
	var ruins := 2
	if radius >= 7:
		ruins = n + 1
	if radius >= 9:
		ruins = n + 3
	if radius >= 11:
		ruins = n + 5
	var min_gap := 3 if radius <= 7 else 4
	var cells := Hex.area(Vector2i.ZERO, radius - 1)
	for k in ruins:
		var best := NO_CELL
		var best_d := -1
		for t in 60:
			var c: Vector2i = cells[rng.randi() % cells.size()]
			var d := 99
			for o in out:
				d = mini(d, Hex.distance(c, o[0]))
			if d > best_d:
				best_d = d
				best = c
		if best_d < min_gap:
			break
		out.append([best, RUIN_NAMES[k % RUIN_NAMES.size()], NO_PLAYER])
	return out


func _generate_terrain(s: int, city_defs: Array) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = s
	tiles.clear()
	for p in Hex.area(Vector2i.ZERO, radius):
		var roll := rng.randf()
		var t := "llanura"
		if roll < 0.18:
			t = "bosque"
		elif roll < 0.26:
			t = "montana"
		elif roll < 0.30:
			t = "agua"
		tiles[p] = t
	# Ríos que cruzan el mapa de un borde al otro pasando cerca del centro,
	# con algunos vados (casillas de tierra) para poder cruzarlos a pie.
	var rivers := 1 if radius < 9 else 2
	for r in rivers:
		var a := rng.randf() * TAU
		var edge_a := Hex.from_world(Vector3(cos(a), 0, sin(a)) * radius * 1.5)
		var edge_b := Hex.from_world(Vector3(cos(a + PI + rng.randf_range(-0.5, 0.5)), 0, sin(a + PI)) * radius * 1.5)
		var mid := Vector2i(rng.randi_range(-1, 1), rng.randi_range(-1, 1))
		var pts: Array[Vector2i] = [_clamp_cell(edge_a), mid, _clamp_cell(edge_b)]
		var river := _river_path(rng, pts)
		for p in river:
			tiles[p] = "agua"
		var fords := 0
		var tries := 0
		var want := 3 + radius / 3
		while fords < want and tries < 80 and river.size() > 2:
			tries += 1
			var f: Vector2i = river[rng.randi_range(1, river.size() - 2)]
			if tiles[f] != "agua":
				continue
			tiles[f] = "llanura"
			fords += 1
	# Alrededor de las ciudades no hay montañas, y la ciudad misma es llanura.
	for def in city_defs:
		var c: Vector2i = def[0]
		tiles[c] = "llanura"
		for n in Hex.neighbors(c):
			if tiles.get(n, "") == "montana":
				tiles[n] = "llanura"
		# Al menos 4 casillas de tierra alrededor (para frutos, troncos, campo y arboleda)
		var land := 0
		for n in Hex.neighbors(c):
			if tiles.has(n) and tiles[n] != "agua":
				land += 1
		for n in Hex.neighbors(c):
			if land >= 4:
				break
			if tiles.get(n, "") == "agua":
				tiles[n] = "llanura"
				land += 1


func _clamp_cell(h: Vector2i) -> Vector2i:
	var w := Hex.to_world(h)
	while Hex.distance(h, Vector2i.ZERO) > radius:
		w *= 0.95
		h = Hex.from_world(w)
	return h


func _river_path(rng: RandomNumberGenerator, waypoints: Array[Vector2i]) -> Array[Vector2i]:
	var path: Array[Vector2i] = [waypoints[0]]
	var cur := waypoints[0]
	for w in waypoints.slice(1):
		var guard := 0
		while cur != w and guard < 40:
			guard += 1
			var closer: Array[Vector2i] = []
			for n in Hex.neighbors(cur):
				if tiles.has(n) and Hex.distance(n, w) < Hex.distance(cur, w):
					closer.append(n)
			if closer.is_empty():
				break
			cur = closer[rng.randi() % closer.size()]
			path.append(cur)
	return path


func _place_resources(s: int, city_defs: Array) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = s * 7 + 1
	for p in tiles:
		if cities.has(p) or rng.randf() > 0.3:
			continue
		var options: Array[String] = []
		for id in RESOURCES:
			if RESOURCES[id]["terreno"] == tiles[p]:
				options.append(id)
		if not options.is_empty():
			resources[p] = options[rng.randi() % options.size()]
	# Cada ciudad tiene en su territorio lo necesario para subir a nivel 2 y
	# para producir: frutos, troncos, un campo fértil y una arboleda.
	for def in city_defs:
		var free: Array[Vector2i] = []
		for n in Hex.neighbors(def[0]):
			if tiles.has(n) and tiles[n] != "agua":
				free.append(n)
		free.shuffle()
		var needed: Array[String] = ["frutos", "troncos", "campo", "arboleda"]
		for res_id in needed:
			var already := false
			for n in free:
				if resources.get(n, "") == res_id:
					already = true
			if already:
				continue
			var spot := NO_CELL
			for n in free:
				if not resources.has(n):
					spot = n
					break
			if spot == NO_CELL:
				# Sin lugar libre: se reemplaza un recurso repetido
				var counts := {}
				for n in free:
					counts[resources[n]] = counts.get(resources[n], 0) + 1
				for n in free:
					if counts[resources[n]] > 1:
						spot = n
						break
			if spot != NO_CELL:
				resources[spot] = res_id
				tiles[spot] = RESOURCES[res_id]["terreno"]


func _cities_connected(city_defs: Array) -> bool:
	var start: Vector2i = city_defs[0][0]
	var seen := {start: true}
	var frontier: Array[Vector2i] = [start]
	while not frontier.is_empty():
		var cur: Vector2i = frontier.pop_back()
		for n in Hex.neighbors(cur):
			if is_passable(n) and not seen.has(n):
				seen[n] = true
				frontier.append(n)
	for def in city_defs:
		if not seen.has(def[0]):
			return false
	return true


# --- Consultas -------------------------------------------------------------------

func is_passable(p: Vector2i) -> bool:
	return tiles.has(p) and PASSABLE[tiles[p]]


func has_tech(player_id: int, tech: String) -> bool:
	return players[player_id].techs.has(tech)


## ¿Puede una tropa del jugador pasar de "from" a "to"? (sin contar otras tropas)
## - Montañas: requieren Exploración.
## - Agua: requiere Navegación, y desde tierra solo se sube al barco en un puerto propio.
func can_enter(player_id: int, from: Vector2i, to: Vector2i) -> bool:
	if not tiles.has(to) or _blocked_by_flames(to, player_id):
		return false
	match tiles[to]:
		"montana":
			return has_tech(player_id, "exploracion")
		"agua":
			if not has_tech(player_id, "navegacion"):
				return false
			return tiles.get(from, "") == "agua" or ports.get(to, NO_PLAYER) == player_id
	return true


## Terreno por el que el jugador puede caminar (para calcular rutas; ignora el agua).
func walkable(p: Vector2i, player_id: int) -> bool:
	if not tiles.has(p):
		return false
	return PASSABLE[tiles[p]] or (tiles[p] == "montana" and has_tech(player_id, "exploracion"))


func attack_range(u: Unit) -> int:
	var r := stat(u, "alcance")
	if r > 1 and tiles.get(u.pos, "") == "montana":
		r += 1
	return r


func unit_at(p: Vector2i) -> Unit:
	for u in units.values():
		if u.pos == p:
			return u
	return null


func units_of(player_id: int) -> Array[Unit]:
	var result: Array[Unit] = []
	for u in units.values():
		if u.owner == player_id:
			result.append(u)
	return result


## Tropas que ocupan espacio en la ciudad (los héroes también cuentan).
func units_from_city(city_pos: Vector2i) -> int:
	var n := 0
	for u in units.values():
		if u.home == city_pos:
			n += 1
	return n


func current_player() -> Player:
	return players[current]


func city_territory(city_pos: Vector2i) -> Array[Vector2i]:
	var result: Array[Vector2i] = []
	for p in territory:
		if territory[p] == city_pos:
			result.append(p)
	return result


## Dueño de una casilla: el dueño de la ciudad en cuyo territorio está.
func tile_owner(p: Vector2i) -> int:
	if cities.has(p):
		return cities[p].owner
	if territory.has(p):
		return cities[territory[p]].owner
	return NO_PLAYER


func income(player_id: int) -> Dictionary:
	var result := {"comida": 0, "madera": 0, "oro": 0}
	for c in cities.values():
		if c.owner == player_id:
			# Las ciudades no producen comida: sale de cosechas y granjas (partidas más pausadas)
			result["oro"] += c.level + 1 + c.gold_bonus
	for p in buildings:
		if tile_owner(p) == player_id:
			var prod: Dictionary = BUILDINGS[buildings[p]]["produce"]
			for k in prod:
				result[k] += prod[k] * int(building_levels.get(p, 1))
	return result


func can_afford(player_id: int, cost: Dictionary) -> bool:
	for k in cost:
		if players[player_id].res[k] < cost[k]:
			return false
	return true


static func cost_text(cost: Dictionary) -> String:
	var parts: Array[String] = []
	for k in cost:
		parts.append("%d %s" % [cost[k], RESOURCE_NAMES[k]])
	return ", ".join(parts) if not parts.is_empty() else "gratis"


func _blocked_by_flames(p: Vector2i, player_id: int) -> bool:
	return flames.has(p) and flames[p]["owner"] != player_id


## Las ciudades cuentan como camino.
func has_road(p: Vector2i) -> bool:
	return roads.has(p) or cities.has(p)


## Casillas a las que la tropa puede moverse este turno.
## El movimiento se cuenta en medios puntos: un paso normal cuesta 2 y un paso
## de camino a camino (o de agua a agua en barco) cuesta 1.
## Entrar a un bosque fuera del camino gasta todo el movimiento restante.
func reachable(u: Unit) -> Array[Vector2i]:
	var result: Array[Vector2i] = []
	if not u.can_move():
		return result
	var best := {u.pos: stat(u, "movimiento") * 2}
	var frontier: Array[Vector2i] = [u.pos]
	while not frontier.is_empty():
		var cur: Vector2i = frontier.pop_front()
		var rem: int = best[cur]
		if rem <= 0:
			continue
		for n in Hex.neighbors(cur):
			if not can_enter(u.owner, cur, n):
				continue
			var occ := unit_at(n)
			if occ != null and occ.owner != u.owner:
				continue  # Las tropas enemigas bloquean el paso.
			# Por camino o navegando en barco se avanza el doble.
			var on_road: bool = (has_road(cur) and has_road(n)) or (tiles[cur] == "agua" and tiles[n] == "agua")
			var cost := 1 if on_road else 2
			if rem < cost:
				continue
			var nrem := rem - cost
			if tiles[n] in ["bosque", "montana"] and not on_road:
				nrem = 0  # Bosques y montañas gastan todo el movimiento.
			if best.has(n) and best[n] >= nrem:
				continue
			best[n] = nrem
			frontier.append(n)
	for p in best:
		if p != u.pos and unit_at(p) == null:
			result.append(p)
	return result


# --- Niebla de guerra -------------------------------------------------------------------

## Casillas que el jugador ve en este momento: alrededor de sus tropas (más desde
## una montaña), de sus ciudades (más con la recompensa Visión) y todo su territorio.
## Las tropas descubren solo las casillas vecinas, pero en zonas ya descubiertas
## ven una casilla más lejos (for_explore = true: solo lo que se descubre).
func visible_tiles(player_id: int, for_explore := false) -> Dictionary:
	var seen := {}
	if not fog:
		for p in tiles:
			seen[p] = true
		return seen
	var known: Dictionary = explored[player_id] if player_id >= 0 and player_id < explored.size() else {}
	for u in units.values():
		if u.owner == player_id:
			var r := UNIT_VISION + (1 if tiles.get(u.pos, "") == "montana" else 0)
			for p in Hex.area(u.pos, r):
				if tiles.has(p):
					seen[p] = true
			if not for_explore:
				for p in Hex.area(u.pos, r + 1):
					if known.has(p):
						seen[p] = true
	for c in cities.values():
		if c.owner == player_id:
			var r := VISION_RADIUS if c.vision else CITY_VISION
			for p in Hex.area(c.pos, r):
				if tiles.has(p):
					seen[p] = true
	for p in territory:
		if cities[territory[p]].owner == player_id:
			seen[p] = true
	return seen


func update_vision(player_id: int) -> void:
	if player_id < 0 or player_id >= explored.size():
		return
	for p in visible_tiles(player_id, true):
		explored[player_id][p] = true


func is_explored(player_id: int, p: Vector2i) -> bool:
	return not fog or explored[player_id].has(p)


## Tropas enemigas que esta tropa puede atacar ahora mismo.
func attack_targets(u: Unit) -> Array[Unit]:
	var result: Array[Unit] = []
	if not u.can_attack():
		return result
	var reach := attack_range(u)
	var seen := visible_tiles(u.owner)
	for other in units.values():
		if other.owner != u.owner and Hex.distance(u.pos, other.pos) <= reach and seen.has(other.pos):
			result.append(other)
	return result


## Defensa efectiva: +50 % en bosque o dentro de una ciudad propia.
func defense_value(u: Unit) -> float:
	var d := float(stat(u, "defensa"))
	var in_own_city: bool = cities.has(u.pos) and cities[u.pos].owner == u.owner
	if tiles.get(u.pos, "") == "bosque" or in_own_city:
		d *= 1.5
	return d


func attack_value(u: Unit) -> float:
	return float(stat(u, "ataque")) * (VETERAN_ATTACK if u.veteran else 1.0)


## Combate: la fuerza de cada lado depende de su ataque/defensa y de cuánta vida le queda.
## Devuelve [daño al defensor, daño del contraataque si sobrevive y alcanza].
func combat(attacker: Unit, defender: Unit) -> Array:
	var atk := attack_value(attacker)
	var def := defense_value(defender)
	var a := atk * float(attacker.hp) / float(attacker.max_hp())
	var d := def * float(defender.hp) / float(defender.max_hp())
	var total := maxf(a + d, 0.01)
	var dmg := maxi(1, roundi(a / total * atk * 4.5))
	var back := maxi(1, roundi(d / total * def * 4.5))
	return [dmg, back]


func calc_damage(attacker: Unit, defender: Unit) -> int:
	return int(combat(attacker, defender)[0])


## Estadística efectiva de una tropa donde está parada (p. ej. el Capitán en el agua).
func stat(u: Unit, key: String) -> int:
	var s := u.stats()
	if tiles.get(u.pos, "") == "agua" and s.has("en_agua") and s["en_agua"].has(key):
		return int(s["en_agua"][key])
	return int(s[key])


## Devuelve "" si se puede entrenar, o el motivo por el que no.
func can_train(city_pos: Vector2i, type: String) -> String:
	if winner != NO_PLAYER:
		return "La partida terminó"
	var c: City = cities.get(city_pos)
	if c == null or c.owner != current:
		return "No es tu ciudad"
	var req: String = UnitTypes.DATA[type]["requiere"]
	if req == "heroe":
		return "Solo se invoca"
	if req != "" and not has_tech(current, req):
		return "Requiere la mejora %s" % Techs.DATA[req]["nombre"]
	if unit_at(city_pos) != null:
		return "La ciudad está ocupada"
	if units_from_city(city_pos) >= c.max_units():
		return "Límite de tropas de la ciudad"
	if players[current].res["comida"] < int(UnitTypes.DATA[type]["costo"]):
		return "Falta comida"
	return ""


## Tropas que el jugador puede entrenar con sus mejoras actuales.
func trainable_types(player_id: int) -> Array[String]:
	var result: Array[String] = []
	for id in UnitTypes.DATA:
		var req: String = UnitTypes.DATA[id]["requiere"]
		if req != "heroe" and has_tech(player_id, req):
			result.append(id)
	return result


func can_research(tech: String) -> String:
	var p := players[current]
	if p.techs.has(tech):
		return "Ya investigada"
	for req in Techs.DATA[tech]["requiere"]:
		if not p.techs.has(req):
			return "Requiere %s" % Techs.DATA[req]["nombre"]
	if p.res["oro"] < int(Techs.DATA[tech]["costo"]):
		return "Falta oro"
	return ""


func research(tech: String) -> bool:
	if can_research(tech) != "":
		return false
	var p := players[current]
	p.res["oro"] -= int(Techs.DATA[tech]["costo"])
	p.techs[tech] = true
	message.emit("Nueva mejora: %s" % Techs.DATA[tech]["nombre"])
	return true


func _expand(c: City) -> int:
	c.expanded = true
	var added := 0
	for p in Hex.area(c.pos, 2):
		if tiles.has(p) and not territory.has(p) and not cities.has(p):
			territory[p] = c.pos
			added += 1
	return added


func can_upgrade_city(city_pos: Vector2i) -> String:
	var c: City = cities.get(city_pos)
	if c == null or c.owner != current:
		return "No es tu ciudad"
	if c.points < c.points_needed():
		return "Faltan puntos de mejora (%d/%d)" % [c.points, c.points_needed()]
	if players[current].res["oro"] < c.upgrade_cost():
		return "Falta oro"
	return ""


## ¿Se puede poner un camino aquí? Debe ser tierra fuera del territorio enemigo
## y junto al territorio, una ciudad o un camino del jugador actual.
func road_spot_ok(p: Vector2i) -> bool:
	if not is_passable(p) or roads.has(p) or cities.has(p):
		return false
	var owner_id := tile_owner(p)
	if owner_id != NO_PLAYER and owner_id != current:
		return false
	if owner_id == current:
		return true
	for n in Hex.neighbors(p):
		if tile_owner(n) == current or roads.get(n, NO_PLAYER) == current:
			return true
	return false


func can_build_road(p: Vector2i) -> bool:
	return road_spot_ok(p) and has_tech(current, "caminos")


func _tech_block(tech: String) -> String:
	return "" if has_tech(current, tech) else "Requiere investigar %s" % Techs.DATA[tech]["nombre"]


## Acciones posibles sobre una casilla: [{id, nombre, costo, detalle, bloqueo}]
## "bloqueo" no vacío = se muestra pero aún no se puede (falta investigar algo).
## Si hay una tropa encima de la casilla no se puede hacer nada en ella.
func tile_actions(p: Vector2i) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if unit_at(p) != null or cities.has(p) or not is_explored(current, p):
		return result
	var mine := territory.has(p) and tile_owner(p) == current
	if mine and resources.has(p):
		var r: Dictionary = RESOURCES[resources[p]]
		if r["tipo"] == "una_vez":
			result.append({"id": "cosechar", "nombre": "Cosechar %s" % r["nombre"], "costo": {},
				"icono": "manzana" if resources[p] == "frutos" else "madera", "corto": "Cosechar",
				"detalle": "+" + cost_text(r["da"]) + ", +%d puntos" % r["puntos"], "bloqueo": ""})
		else:
			var b: Dictionary = BUILDINGS[r["edificio"]]
			result.append({"id": "construir", "nombre": "Construir %s" % b["nombre"], "costo": b["costo"],
				"icono": "trigo" if r["edificio"] == "granja" else "hacha", "corto": b["nombre"],
				"detalle": "+" + cost_text(b["produce"]) + " por turno, +%d puntos" % b["puntos"],
				"bloqueo": _tech_block(b["tech"])})
	elif mine and tiles[p] == "bosque" and not buildings.has(p):
		# Cualquier bosque de tu territorio sirve para un aserradero
		var b: Dictionary = BUILDINGS["aserradero"]
		result.append({"id": "construir", "nombre": "Construir %s" % b["nombre"], "costo": b["costo"],
			"icono": "hacha", "corto": b["nombre"],
			"detalle": "+" + cost_text(b["produce"]) + " por turno, +%d puntos" % b["puntos"],
			"bloqueo": _tech_block(b["tech"])})
	if mine and buildings.has(p) and building_levels.get(p, 1) == 1:
		var b: Dictionary = BUILDINGS[buildings[p]]
		result.append({"id": "mejorar_edificio", "nombre": "Mejorar %s a nivel 2" % b["nombre"],
			"icono": "trigo" if buildings[p] == "granja" else "hacha", "corto": "Nivel 2", "nivel": 2,
			"costo": b["costo2"], "detalle": "Produce el doble, +%d puntos" % b["puntos"],
			"bloqueo": _tech_block(b["tech2"])})
	if road_spot_ok(p):
		result.append({"id": "camino", "nombre": "Construir camino", "costo": ROAD_COST,
			"icono": "camino", "corto": "Camino",
			"detalle": "Las tropas avanzan el doble. Cada ciudad gana +%d punto por cada ciudad conectada a ella" % CONNECTION_POINTS,
			"bloqueo": _tech_block("caminos")})
	if mine and tiles[p] == "agua" and not ports.has(p):
		result.append({"id": "puerto", "nombre": "Construir puerto", "costo": PORT_COST,
			"icono": "ancla", "corto": "Puerto",
			"detalle": "Conecta ciudades por agua; con Navegación, las tropas suben aquí a los barcos. +%d punto" % PORT_POINTS,
			"bloqueo": _tech_block("muelle")})
	return result


# --- Acciones --------------------------------------------------------------------

func move_unit(u: Unit, to: Vector2i) -> bool:
	if u.owner != current or not to in reachable(u):
		return false
	_event({"t": "mover", "id": u.id, "desde": u.pos, "hasta": to})
	u.pos = to
	u.moved = true
	update_vision(u.owner)
	return true


func attack(attacker: Unit, defender: Unit) -> bool:
	if attacker.owner != current or not defender in attack_targets(attacker):
		return false
	var result := combat(attacker, defender)
	var dmg: int = result[0]
	var target_pos := defender.pos
	attacker.attacked = true
	attacker.moved = true
	var text := "%s atacó a %s (-%d)" % [attacker.stats()["nombre"], defender.stats()["nombre"], dmg]
	_event({"t": "ataque", "id": attacker.id, "objetivo": defender.id,
		"desde": attacker.pos, "hacia": defender.pos, "dano": dmg})
	if _damage(defender, dmg):
		text += ". ¡Lo eliminó!"
		_add_kill(attacker)
		# Cuerpo a cuerpo: el que ganó ocupa la casilla del vencido
		if Hex.distance(attacker.pos, target_pos) == 1 and can_enter(attacker.owner, attacker.pos, target_pos) \
				and unit_at(target_pos) == null:
			_event({"t": "mover", "id": attacker.id, "desde": attacker.pos, "hasta": target_pos})
			attacker.pos = target_pos
			update_vision(attacker.owner)
	elif Hex.distance(attacker.pos, defender.pos) <= attack_range(defender):
		var back: int = result[1]
		text += ", contraataque (-%d)" % back
		_event({"t": "ataque", "id": defender.id, "objetivo": attacker.id,
			"desde": defender.pos, "hacia": attacker.pos, "dano": back})
		if _damage(attacker, back):
			text += ". El atacante murió"
			_add_kill(defender)
	message.emit(text)
	return true


func _add_kill(u: Unit) -> void:
	if not units.has(u.id):
		return
	u.kills += 1
	if u.kills >= VETERAN_KILLS and not u.veteran:
		u.veteran = true
		u.hp = u.max_hp()
		_event({"t": "veterano", "id": u.id, "vida": u.hp})
		message.emit("¡%s es ahora veterano!" % u.stats()["nombre"])


func train(city_pos: Vector2i, type: String) -> Unit:
	if can_train(city_pos, type) != "":
		return null
	players[current].res["comida"] -= int(UnitTypes.DATA[type]["costo"])
	return _spawn_unit(type, current, city_pos, city_pos)


func do_tile_action(p: Vector2i, action_id: String) -> bool:
	var action: Dictionary = {}
	for a in tile_actions(p):
		if a["id"] == action_id:
			action = a
	if action.is_empty() or action["bloqueo"] != "" or not can_afford(current, action["costo"]):
		return false
	var res: Dictionary = players[current].res
	for k in action["costo"]:
		res[k] -= action["costo"][k]
	match action_id:
		"cosechar":
			var r: Dictionary = RESOURCES[resources[p]]
			var c: City = cities[territory[p]]
			for k in r["da"]:
				res[k] += r["da"][k]
			c.points += int(r["puntos"])
			resources.erase(p)
			message.emit("Cosechaste %s (+%d puntos para %s)" % [r["nombre"], r["puntos"], c.name])
		"construir":
			var kind: String = RESOURCES[resources[p]]["edificio"] if resources.has(p) else "aserradero"
			var b: Dictionary = BUILDINGS[kind]
			var c: City = cities[territory[p]]
			buildings[p] = kind
			building_levels[p] = 1
			c.points += int(b["puntos"])
			resources.erase(p)
			message.emit("Construiste %s (+%d puntos para %s)" % [b["nombre"], b["puntos"], c.name])
		"mejorar_edificio":
			var b: Dictionary = BUILDINGS[buildings[p]]
			var c: City = cities[territory[p]]
			building_levels[p] = 2
			c.points += int(b["puntos"])
			message.emit("%s mejorada a nivel 2 (+%d puntos para %s)" % [b["nombre"], b["puntos"], c.name])
		"camino":
			roads[p] = current
			_check_connections()
		"puerto":
			var c: City = cities[territory[p]]
			ports[p] = current
			c.points += PORT_POINTS
			message.emit("Construiste un puerto en %s" % c.name)
			_check_connections()
	return true


## Ciudades del jugador conectadas con la ciudad dada por caminos y puertos.
func connected_cities(city_pos: Vector2i) -> Array[Vector2i]:
	var owner_id: int = cities[city_pos].owner
	var seen := {city_pos: true}
	var frontier: Array[Vector2i] = [city_pos]
	var result: Array[Vector2i] = []
	while not frontier.is_empty():
		var cur: Vector2i = frontier.pop_back()
		var next: Array[Vector2i] = []
		for n in Hex.neighbors(cur):
			var is_own_city: bool = cities.has(n) and cities[n].owner == owner_id
			if roads.has(n) or is_own_city or ports.get(n, NO_PLAYER) == owner_id:
				next.append(n)
		if ports.get(cur, NO_PLAYER) == owner_id:
			next.append_array(_ports_on_same_water(cur, owner_id))
		for n in next:
			if seen.has(n):
				continue
			seen[n] = true
			if cities.has(n):
				if cities[n].owner != owner_id:
					continue  # Las ciudades ajenas cortan la conexión.
				result.append(n)
			frontier.append(n)
	return result


func _ports_on_same_water(port: Vector2i, owner_id: int) -> Array[Vector2i]:
	var result: Array[Vector2i] = []
	var seen := {port: true}
	var frontier: Array[Vector2i] = [port]
	while not frontier.is_empty():
		var cur: Vector2i = frontier.pop_back()
		for n in Hex.neighbors(cur):
			if seen.has(n) or tiles.get(n, "") != "agua":
				continue
			seen[n] = true
			frontier.append(n)
			if ports.get(n, NO_PLAYER) == owner_id:
				result.append(n)
	return result


## Premia las conexiones nuevas entre ciudades del jugador actual.
func _check_connections() -> void:
	for c in cities.values():
		if c.owner != current:
			continue
		for other_pos in connected_cities(c.pos):
			var a: Vector2i = c.pos
			var b: Vector2i = other_pos
			if b < a:
				var tmp := a
				a = b
				b = tmp
			var key := "%d|%s|%s" % [current, a, b]
			if connections.has(key):
				continue
			connections[key] = true
			cities[a].points += CONNECTION_POINTS
			cities[b].points += CONNECTION_POINTS
			message.emit("¡%s y %s quedaron conectadas! +%d punto para cada una" % [
				cities[a].name, cities[b].name, CONNECTION_POINTS])


func upgrade_city(city_pos: Vector2i) -> bool:
	if can_upgrade_city(city_pos) != "":
		return false
	var c: City = cities[city_pos]
	players[current].res["oro"] -= c.upgrade_cost()
	c.points -= c.points_needed()
	c.level += 1
	var options: Array = []
	match c.level:
		2:
			options = ["vision", "oro_extra"]
		3:
			options = ["oro_turno", "frontera"]
		_:
			for h in UnitTypes.HEROES:
				options.append("heroe:" + h)
	c.pending_rewards.append(options)
	message.emit("%s subió a nivel %d. ¡Elige una recompensa!" % [c.name, c.level])
	return true


## Nombre y descripción de una opción de recompensa.
func reward_info(option: String) -> Dictionary:
	if option.begins_with("heroe:"):
		var hero := option.substr(6)
		var abilities: Array[String] = []
		for a in UnitTypes.DATA[hero]["habilidades"]:
			abilities.append(UnitTypes.ABILITIES[a]["nombre"])
		return {"icono": UnitTypes.DATA[hero]["icono"], "nombre": UnitTypes.DATA[hero]["nombre"],
			"descripcion": "Habilidades: %s" % ", ".join(abilities)}
	var info: Dictionary = REWARDS[option].duplicate()
	if option == "oro_extra":
		info["descripcion"] = info["descripcion"] % EXTRA_GOLD
	elif option == "oro_turno":
		info["descripcion"] = info["descripcion"] % GOLD_PER_TURN_BONUS
	return info


## Elige una de las opciones de la recompensa pendiente más antigua de la ciudad.
func choose_reward(city_pos: Vector2i, option: String) -> bool:
	var c: City = cities.get(city_pos)
	if c == null or c.owner != current or c.pending_rewards.is_empty():
		return false
	if not option in c.pending_rewards[0]:
		return false
	c.pending_rewards.pop_front()
	match option:
		"vision":
			c.vision = true
			message.emit("%s ahora ve a %d casillas" % [c.name, VISION_RADIUS])
		"oro_extra":
			players[current].res["oro"] += EXTRA_GOLD
			message.emit("+%d oro" % EXTRA_GOLD)
		"oro_turno":
			c.gold_bonus += GOLD_PER_TURN_BONUS
			message.emit("%s produce +%d oro por turno" % [c.name, GOLD_PER_TURN_BONUS])
		"frontera":
			message.emit("%s amplió su frontera (+%d casillas)" % [c.name, _expand(c)])
		_:
			_summon_hero(c, option.substr(6))
	update_vision(current)
	return true


## Los héroes se invocan aunque haya una tropa en la ciudad: esa tropa se
## desplaza a la casilla libre más cercana. Son las únicas tropas que pueden
## pasar el límite de la ciudad (si caben, simplemente ocupan un espacio).
func _summon_hero(c: City, type: String) -> void:
	var occupant := unit_at(c.pos)
	if occupant != null:
		var spot: Variant = _nearest_free_tile(c.pos, occupant.owner)
		if spot != null:
			occupant.pos = spot
			occupant.capturing = false
		else:
			units.erase(occupant.id)  # No hay ningún lugar libre (casi imposible).
	_spawn_unit(type, current, c.pos, c.pos)
	update_vision(current)
	message.emit("¡%s fue invocado en %s!" % [UnitTypes.DATA[type]["nombre"], c.name])


func _nearest_free_tile(from: Vector2i, player_id: int) -> Variant:
	var seen := {from: true}
	var frontier: Array[Vector2i] = [from]
	while not frontier.is_empty():
		var cur: Vector2i = frontier.pop_front()
		for n in Hex.neighbors(cur):
			if seen.has(n) or not walkable(n, player_id):
				continue
			seen[n] = true
			if unit_at(n) == null and not cities.has(n):
				return n
			frontier.append(n)
	return null


# --- Habilidades de héroe ------------------------------------------------------------

## Devuelve "" si la habilidad se puede usar ahora.
func can_use_ability(u: Unit, ability: String) -> String:
	if u.owner != current or not ability in u.abilities():
		return "No disponible"
	if u.exhausted or u.attacked:
		return "Ya actuó este turno"
	if ability == "embestida" and u.moved:
		return "Ya se movió este turno"
	var wait: int = u.cooldowns.get(ability, 0)
	if wait > 0:
		return "Espera %d turno%s" % [wait, "" if wait == 1 else "s"]
	return ""


## Casillas válidas para apuntar la habilidad.
func ability_targets(u: Unit, ability: String) -> Array[Vector2i]:
	var result: Array[Vector2i] = []
	if can_use_ability(u, ability) != "":
		return result
	match ability:
		"embestida":
			for n in Hex.neighbors(u.pos):
				if can_enter(u.owner, u.pos, n):
					result.append(n)
		"muralla":
			for p in Hex.area(u.pos, int(UnitTypes.ABILITIES["muralla"]["distancia"])):
				if tiles.has(p) and p != u.pos:
					result.append(p)
	return result


## Las 3 casillas de la muralla: el objetivo y sus dos vecinos en línea, cruzada
## respecto a la dirección desde el sacerdote.
func wall_cells(caster: Vector2i, target: Vector2i) -> Array[Vector2i]:
	var dir := Hex.to_world(target) - Hex.to_world(caster)
	var best_i := 0
	var best_dot := -INF
	for i in 6:
		var d := Hex.to_world(Hex.DIRS[i])
		var dot := d.normalized().dot(dir.normalized())
		if dot > best_dot:
			best_dot = dot
			best_i = i
	var side := Hex.DIRS[(best_i + 2) % 6]
	var result: Array[Vector2i] = []
	for p in [target, target + side, target - side]:
		if tiles.has(p):
			result.append(p)
	return result


func use_ability(u: Unit, ability: String, target: Vector2i = Vector2i.ZERO) -> bool:
	if can_use_ability(u, ability) != "":
		return false
	var info: Dictionary = UnitTypes.ABILITIES[ability]
	match ability:
		"embestida":
			if not target in ability_targets(u, ability):
				return false
			_charge(u, target - u.pos, int(info["distancia"]))
		"curacion":
			var healed := 0
			var healed_ids := []
			for other in units_of(u.owner):
				if Hex.distance(other.pos, u.pos) <= int(info["radio"]) and other.hp < other.max_hp():
					other.hp = mini(other.max_hp(), other.hp + int(info["cantidad"]))
					healed += 1
					healed_ids.append(other.id)
			_event({"t": "habilidad", "id": u.id, "nombre": "curacion", "curados": healed_ids,
				"cantidad": int(info["cantidad"])})
			message.emit("El sacerdote curó a %d tropa%s" % [healed, "" if healed == 1 else "s"])
		"muralla":
			if not target in ability_targets(u, ability):
				return false
			_event({"t": "habilidad", "id": u.id, "nombre": "muralla", "hacia": target})
			for p in wall_cells(u.pos, target):
				flames[p] = {"owner": u.owner, "turns": int(info["duracion"])}
			message.emit("¡Muralla de llamas!")
	if units.has(u.id):
		u.attacked = true
		u.moved = true
		u.cooldowns[ability] = int(info["espera"])
	update_vision(current)
	return true


func _charge(u: Unit, dir: Vector2i, max_steps: int) -> void:
	var hits := 0
	_event({"t": "habilidad", "id": u.id, "nombre": "embestida"})
	for step in max_steps:
		var next := u.pos + dir
		if not can_enter(u.owner, u.pos, next):
			break
		var occ := unit_at(next)
		if occ != null and occ.owner == u.owner:
			break
		if occ != null:
			hits += 1
			_event({"t": "golpe", "id": u.id, "hacia": next})
			if not _damage(occ, calc_damage(u, occ)):
				break  # Sobrevivió: la embestida se detiene frente a él.
			_add_kill(u)
		_event({"t": "mover", "id": u.id, "desde": u.pos, "hasta": next, "rapido": true})
		u.pos = next
	message.emit("¡Embestida! Golpeó a %d enemigo%s" % [hits, "" if hits == 1 else "s"])


func end_turn() -> void:
	if winner != NO_PLAYER:
		return
	# Las tropas que terminan su turno sobre una ciudad ajena empiezan a conquistarla.
	for u in units_of(current):
		u.capturing = cities.has(u.pos) and cities[u.pos].owner != current
	var nxt := current
	for i in players.size():
		nxt = (nxt + 1) % players.size()
		if nxt == 0:
			turn += 1
		if players[nxt].alive:
			break
	current = nxt
	_start_turn()


# --- Internas --------------------------------------------------------------------

func _spawn_unit(type: String, owner_id: int, pos: Vector2i, home: Vector2i) -> Unit:
	var u := Unit.new()
	u.id = _next_id
	_next_id += 1
	u.type = type
	u.owner = owner_id
	u.pos = pos
	u.home = home
	u.hp = int(UnitTypes.DATA[type]["vida"])
	u.exhausted = true  # Una tropa no actúa el turno en que se crea.
	units[u.id] = u
	_event({"t": "nace", "id": u.id})
	return u


## Resta vida y elimina la tropa si llega a 0. Devuelve true si murió.
func _damage(u: Unit, amount: int) -> bool:
	u.hp -= amount
	_event({"t": "dano", "id": u.id, "dano": amount, "vida": maxi(0, u.hp)})
	if u.hp <= 0:
		units.erase(u.id)
		_event({"t": "muerte", "id": u.id})
		return true
	return false


func _start_turn() -> void:
	var p := players[current]
	# Las llamas propias se consumen; las enemigas queman a quien esté dentro.
	for f in flames.keys():
		if flames[f]["owner"] == current:
			flames[f]["turns"] -= 1
			if flames[f]["turns"] <= 0:
				flames.erase(f)
	var burn := int(UnitTypes.ABILITIES["muralla"]["dano"])
	for u in units_of(current):
		if _blocked_by_flames(u.pos, current) and _damage(u, burn):
			message.emit("%s murió quemado" % u.stats()["nombre"])
	for u in units_of(current):
		u.moved = false
		u.attacked = false
		u.exhausted = false
		for a in u.cooldowns:
			u.cooldowns[a] = maxi(0, u.cooldowns[a] - 1)
		if u.capturing:
			u.capturing = false
			var c: City = cities.get(u.pos)
			if c != null and c.owner != current:
				_capture(c, u)
				u.exhausted = true  # Conquistar le ocupa este turno completo.
	var inc := income(current)
	for k in inc:
		p.res[k] += inc[k]
	update_vision(current)
	_update_players()


func _capture(c: City, conqueror: Unit) -> void:
	var previous := c.owner
	# Todas las tropas que pertenecían a esa ciudad desaparecen (héroes incluidos).
	for other in units.values():
		if other.home == c.pos and other != conqueror:
			units.erase(other.id)
	# La tropa conquistadora pasa a ocupar un espacio de su nueva ciudad
	# y libera el de su ciudad de origen.
	conqueror.home = c.pos
	c.owner = current
	c.pending_rewards.clear()
	for p in ports:
		if territory.get(p, NO_CELL) == c.pos:
			ports[p] = current
	_check_connections()
	if previous == NO_PLAYER:
		message.emit("%s ocupó %s" % [players[current].name, c.name])
	else:
		message.emit("%s conquistó %s de %s" % [players[current].name, c.name, players[previous].name])


func _update_players() -> void:
	for p in players:
		if not p.alive:
			continue
		var has_city := false
		for c in cities.values():
			if c.owner == p.id:
				has_city = true
				break
		if not has_city:
			p.alive = false
			for u in units_of(p.id):
				units.erase(u.id)
			message.emit("%s fue eliminado" % p.name)
	var alive: Array[int] = []
	for p in players:
		if p.alive:
			alive.append(p.id)
	if alive.size() == 1:
		winner = alive[0]


# --- Copia del estado (para el juego en red) ---------------------------------------
# El anfitrión manda una copia completa del estado después de cada acción; los demás
# teléfonos la cargan encima del suyo (sin crear otro GameState, así el tablero y la
# tropa seleccionada siguen apuntando a los mismos objetos).

const _SAVED_VARS := ["radius", "tiles", "resources", "buildings", "building_levels", "flames",
	"roads", "ports", "connections", "territory", "current", "turn", "winner", "fog", "_next_id"]


static func _obj_to_dict(o: Object) -> Dictionary:
	var d := {}
	for prop in o.get_property_list():
		if prop["usage"] & PROPERTY_USAGE_SCRIPT_VARIABLE:
			d[prop["name"]] = o.get(prop["name"])
	return d


static func _fill_obj(o: Object, d: Dictionary) -> void:
	for key in d:
		o.set(key, d[key])


func to_data() -> Dictionary:
	var d := {}
	for key in _SAVED_VARS:
		d[key] = get(key)
	var cs := {}
	for pos in cities:
		cs[pos] = _obj_to_dict(cities[pos])
	d["cities"] = cs
	var us := {}
	for id in units:
		us[id] = _obj_to_dict(units[id])
	d["units"] = us
	d["players"] = players.map(func(p): return _obj_to_dict(p))
	d["explored"] = explored.duplicate()
	return d


func load_data(d: Dictionary) -> void:
	for key in _SAVED_VARS:
		if d.has(key):
			set(key, d[key])
	# Ciudades y tropas: se actualizan los objetos que ya existen
	var cs: Dictionary = d["cities"]
	for pos in cities.keys():
		if not cs.has(pos):
			cities.erase(pos)
	for pos in cs:
		if not cities.has(pos):
			cities[pos] = City.new()
		_fill_obj(cities[pos], cs[pos])
	var us: Dictionary = d["units"]
	for id in units.keys():
		if not us.has(id):
			units.erase(id)
	for id in us:
		if not units.has(id):
			units[id] = Unit.new()
		_fill_obj(units[id], us[id])
	var ps: Array = d["players"]
	while players.size() > ps.size():
		players.pop_back()
	for i in ps.size():
		if i >= players.size():
			players.append(Player.new())
		_fill_obj(players[i], ps[i])
	explored.clear()
	for e in d["explored"]:
		explored.append(e)


func to_bytes() -> PackedByteArray:
	return var_to_bytes(to_data()).compress(FileAccess.COMPRESSION_DEFLATE)


func load_bytes(b: PackedByteArray) -> void:
	load_data(bytes_to_var(b.decompress_dynamic(-1, FileAccess.COMPRESSION_DEFLATE)))
