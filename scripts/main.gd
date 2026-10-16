extends Node3D
## Escena principal: crea la cámara, la luz, el tablero y la interfaz,
## y traduce los toques del jugador en acciones sobre la partida.
##
## Interfaz:
## - Barra superior: turno y recursos.
## - Barra inferior: Tropas, Investigar, Pasar turno.
## - Panel deslizable (sale de abajo hacia arriba, sobre la barra inferior) con
##   las opciones de lo que esté seleccionado: tropa, ciudad, casilla o el árbol
##   de investigación. Se puede esconder con ▼ y volver a sacar con ▲.

const CAMERA_ANGLE := 55.0
const MIN_ZOOM := 5.0
const MAX_ZOOM := 30.0
const TAP_TOLERANCE := 14.0
const BAR_HEIGHT := 118.0
const NO_CELL := Vector2i(9999, 9999)

var gs: GameState
var board: BoardView
var camera: Camera3D
var cam_target := Vector3.ZERO
var cam_distance := 15.0

# Selección
var selected: GameState.Unit = null   ## Tropa propia seleccionada
var viewed_unit: GameState.Unit = null ## Tropa enemiga que se está mirando
var sel_city := NO_CELL
var sel_tile := NO_CELL
var sheet_mode := ""     ## "", "unit", "enemy", "city", "tile", "tech"
var sheet_hidden := false
var targeting := ""      ## Habilidad esperando que se toque una casilla
var bot_running := false
var _unit_cycle := 0

# Control táctil
var _touches := {}
var _press_pos := Vector2.ZERO
var _dragged := false
var _pinch_dist := 0.0

# Interfaz
var _top_label: Label
var _res_labels := {}
var _bottom_bar: PanelContainer
var _end_button: Button
var _units_button: Button
var _tech_button: Button
var _sheet: PanelContainer
var _sheet_title: Label
var _sheet_scroll: ScrollContainer
var _sheet_box: VBoxContainer
var _show_tab: Button
var _over_panel: PanelContainer
var _over_label: Label
var _ui_blockers: Array[Control] = []
var _log_lines: Array[String] = []
var _sheet_tween: Tween
var _sheet_v: VBoxContainer
var _sheet_ribbon: PanelContainer
var _reward_layer: Control      ## Ventana obligatoria para elegir recompensa de nivel
var _reward_box: VBoxContainer
var _reward_city := Vector2i(9999, 9999)
var _detail := {}  ## Vista de detalle abierta en el panel: {"kind", "id"}
var _config: MatchConfig
var _menu: StartMenu
var _in_menu := false
var _menu_angle := 0.0
var _game_id := 0                 ## Cambia al salir o reiniciar (corta los turnos de bots en curso)
var _top_bar: PanelContainer
var _top_pad: Control
var _bottom_pad: Control
var _ui_root: Control
var _bar_h := BAR_HEIGHT
var _pause_layer: Control
var _over_again: Button
var _over_watch: Button
var _eliminated_shown := false
var _sheet_locked := false        ## Con el candado puesto, tocar el mapa no abre el panel
var _lock_button: Button
var _restart_button: Button

# Juego en red
var net: Net
var me := 0                       ## Jugador que maneja este teléfono
var _waiting := false             ## Invitado: mandó una acción y espera la respuesta


func _ready() -> void:
	net = Net.new()
	net.name = "Net"
	add_child(net)
	net.state_received.connect(_on_net_state)
	net.game_started.connect(_on_net_game_started)
	net.action_requested.connect(_on_net_action)
	net.peer_left.connect(_on_net_peer_left)
	net.host_lost.connect(_on_net_host_lost)
	_setup_world()
	_setup_ui()
	_apply_safe_area()
	_show_menu()


# --- Menú --------------------------------------------------------------------

## Muestra el menú de inicio con un mapa de fondo que gira despacio.
func _show_menu() -> void:
	_game_id += 1
	bot_running = false
	_waiting = false
	me = 0
	if net.in_game:
		net.close()
	_in_menu = true
	_pause_layer.visible = false
	_over_panel.visible = false
	_reward_layer.visible = false
	_clear_selection()
	_set_hud_visible(false)
	var demo := MatchConfig.new()
	demo.enemies = 3
	demo.map_size = "mediano"
	demo.fog = false
	gs = GameState.new()
	gs.setup(randi(), 5, demo)
	board.viewer = 0
	board.build(gs)
	board.sync()
	cam_distance = 13.0
	_menu.show_home()


func _process(delta: float) -> void:
	if _in_menu and camera != null:
		_menu_angle += delta * 0.06
		var pitch := deg_to_rad(42.0)
		var target := Vector3.ZERO
		camera.position = target + Vector3(sin(_menu_angle) * cos(pitch), sin(pitch), cos(_menu_angle) * cos(pitch)) * cam_distance
		camera.look_at(target, Vector3.UP)


func _on_menu_play(config: MatchConfig) -> void:
	_config = config
	_in_menu = false
	_set_hud_visible(true)
	_new_game()


func _set_hud_visible(on: bool) -> void:
	_top_bar.visible = on
	_bottom_bar.visible = on
	if not on:
		_sheet.visible = false
		_show_tab.visible = false


func _on_pause_pressed() -> void:
	if _in_menu:
		return
	_restart_button.visible = not net.is_online()
	_pause_layer.visible = true


func _on_restart_pressed() -> void:
	_pause_layer.visible = false
	_new_game()


func _on_exit_pressed() -> void:
	_show_menu()


# --- Partida -----------------------------------------------------------------

func _new_game() -> void:
	_game_id += 1
	bot_running = false
	gs = GameState.new()
	gs.record_events = true
	SimpleBot.is_busy = board.busy
	gs.message.connect(_on_message)
	gs.setup(randi(), 5, _config)
	gs.events.clear()
	me = 0
	board.viewer = me
	board.build(gs)
	_log_lines.clear()
	_over_panel.visible = false
	_pause_layer.visible = false
	_eliminated_shown = false
	_clear_selection()
	cam_distance = 11.0
	cam_target = Hex.to_world(gs.units_of(me)[0].pos)
	_update_camera()
	if net.is_host():
		net.start_game(gs)
	_begin_turn()


func _begin_turn() -> void:
	var id := _game_id
	_refresh()
	if gs.winner != GameState.NO_PLAYER:
		_show_game_over()
		return
	if net.is_client():
		return  # Los invitados solo siguen lo que manda el anfitrión
	if gs.current_player().is_bot:
		bot_running = true
		_set_bar_enabled(false)
		var this_gs := gs
		await SimpleBot.play_turn(gs, get_tree(), _refresh, 0.25)
		if id != _game_id or this_gs != gs:
			return  # Se salió de la partida mientras jugaba el bot
		bot_running = false
		if gs.winner == GameState.NO_PLAYER:
			gs.end_turn()
		_begin_turn()
	elif gs.current == me:
		_set_bar_enabled(true)
		_check_pending_rewards()
	else:
		_set_bar_enabled(false)  # Turno de otro jugador humano (en red)


func _set_bar_enabled(on: bool) -> void:
	_end_button.disabled = not on
	_units_button.disabled = not on
	_tech_button.disabled = not on


func _on_end_turn_pressed() -> void:
	if _locked() or gs.winner != GameState.NO_PLAYER:
		return
	_clear_selection()
	_act("terminar", [])


## ¿Le toca a este teléfono y puede tocar el tablero?
func _my_turn() -> bool:
	return gs != null and gs.current == me and gs.winner == GameState.NO_PLAYER


func _locked() -> bool:
	return bot_running or _waiting or not _my_turn()


## Toda acción del jugador pasa por aquí: sin red (o en el anfitrión) se hace en el
## momento; un invitado se la pide al anfitrión y espera el nuevo estado.
func _act(action: String, args: Array) -> void:
	if net.is_client():
		_waiting = true
		net.send_action(action, args)
		var id := _game_id
		await get_tree().create_timer(2.0).timeout
		if id == _game_id:
			_waiting = false  # Por si el anfitrión no respondió (acción rechazada)
		return
	_apply_action(gs.current, action, args)


func _apply_action(player: int, action: String, args: Array) -> bool:
	if gs.current != player or gs.winner != GameState.NO_PLAYER or bot_running:
		return false
	var u: GameState.Unit = gs.units.get(args[0]) if action in ["mover", "atacar", "habilidad"] else null
	if action in ["mover", "atacar", "habilidad"] and (u == null or u.owner != player):
		return false
	match action:
		"mover":
			if args[1] in gs.reachable(u):
				gs.move_unit(u, args[1])
		"atacar":
			var target: GameState.Unit = gs.units.get(args[1])
			if target != null and target in gs.attack_targets(u):
				gs.attack(u, target)
		"habilidad":
			if args[2] == null:
				gs.use_ability(u, args[1])
			else:
				gs.use_ability(u, args[1], args[2])
		"investigar":
			gs.research(args[0])
		"entrenar":
			if gs.cities.has(args[0]) and gs.cities[args[0]].owner == player:
				gs.train(args[0], args[1])
		"mejorar":
			if gs.cities.has(args[0]) and gs.cities[args[0]].owner == player:
				gs.upgrade_city(args[0])
		"recompensa":
			if gs.cities.has(args[0]) and gs.cities[args[0]].owner == player:
				gs.choose_reward(args[0], args[1])
		"accion":
			gs.do_tile_action(args[0], args[1])
		"terminar":
			_clear_selection()
			gs.end_turn()
			_begin_turn()
			return true
		_:
			return false
	return true


# --- Red ----------------------------------------------------------------------------------

## Anfitrión: un invitado pidió una acción.
func _on_net_action(player: int, action: String, args: Array) -> void:
	if gs == null or _in_menu:
		return
	if _apply_action(player, action, args) and action != "terminar":
		_refresh()


## Anfitrión: un invitado se desconectó; un bot sigue jugando por él.
func _on_net_peer_left(player: int) -> void:
	if gs == null or player >= gs.players.size():
		return
	gs.players[player].is_bot = true
	_refresh()
	if gs.current == player and not bot_running:
		_begin_turn()


## Invitado: llegó el estado nuevo de la partida.
func _on_net_state(state: PackedByteArray, events: Array) -> void:
	if gs == null or _in_menu:
		return
	gs.load_bytes(state)
	gs.events.append_array(events)
	_waiting = false
	_refresh()
	if gs.winner != GameState.NO_PLAYER:
		_show_game_over()
		return
	_set_bar_enabled(_my_turn() and not _reward_layer.visible)


## Invitado: el anfitrión empezó la partida.
func _on_net_game_started(state: PackedByteArray, my_player: int) -> void:
	_game_id += 1
	_in_menu = false
	_menu.visible = false
	_set_hud_visible(true)
	me = my_player
	gs = GameState.new()
	gs.record_events = true
	SimpleBot.is_busy = board.busy
	gs.message.connect(_on_message)
	gs.load_bytes(state)
	board.viewer = me
	board.build(gs)
	_log_lines.clear()
	_over_panel.visible = false
	_pause_layer.visible = false
	_eliminated_shown = false
	_waiting = false
	_clear_selection()
	cam_distance = 11.0
	var mine := gs.units_of(me)
	cam_target = Hex.to_world(mine[0].pos if not mine.is_empty() else gs.cities.keys()[0])
	_update_camera()
	_refresh()
	_set_bar_enabled(_my_turn())


## Invitado: se cortó la conexión con el anfitrión.
func _on_net_host_lost() -> void:
	if _in_menu:
		_menu.show_net_message("Se perdió la conexión con el anfitrión.")
		return
	_show_menu()
	_menu.show_net_message("Se perdió la conexión con el anfitrión.")


func _on_menu_host_play(config: MatchConfig) -> void:
	config.humans = net.human_colors()
	_on_menu_play(config)


func _on_message(text: String) -> void:
	_log_lines.append(text)
	if _log_lines.size() > 4:
		_log_lines.pop_front()
	# Los mensajes ya no se muestran en pantalla (se guardan por si se necesitan).


## Actualiza tablero, barra superior, resaltados y el panel inferior.
func _refresh() -> void:
	if net.is_host() and net.in_game and not _in_menu:
		net.broadcast_state(gs, gs.events.duplicate())
	board.sync()
	var p := gs.current_player()
	var mine := gs.players[me]
	var inc := gs.income(me)
	if _in_menu:
		return
	var who := "Tu turno" if gs.current == me else "Juega " + p.name
	if net.is_online() and gs.current != me and not p.is_bot:
		who += " (en otro teléfono)"
	_top_label.text = "Turno %d · %s" % [gs.turn, who]
	if not mine.alive and not _eliminated_shown and gs.winner == GameState.NO_PLAYER:
		_eliminated_shown = true
		_show_game_over()
	for res in _res_labels:
		_res_labels[res].text = "%d  +%d" % [mine.res[res], inc[res]]

	if selected != null and not gs.units.has(selected.id):
		_clear_selection()
	if viewed_unit != null and not gs.units.has(viewed_unit.id):
		_clear_selection()

	board.clear_highlights()
	if selected != null and targeting != "":
		board.highlight(gs.ability_targets(selected, targeting), "ability")
		board.highlight([selected.pos], "select")
	elif selected != null:
		board.highlight(gs.reachable(selected), "move")
		var targets: Array[Vector2i] = []
		for t in gs.attack_targets(selected):
			targets.append(t.pos)
		board.highlight(targets, "attack")
		board.highlight([selected.pos], "select")
	elif sel_city != NO_CELL:
		board.highlight(gs.city_territory(sel_city), "territory")
		board.highlight([sel_city], "select")
	elif sel_tile != NO_CELL:
		board.highlight([sel_tile], "select")
	elif viewed_unit != null:
		board.highlight([viewed_unit.pos], "attack")
	_rebuild_sheet()
	_check_pending_rewards()


# --- Selección --------------------------------------------------------------------

func _clear_selection() -> void:
	selected = null
	viewed_unit = null
	sel_city = NO_CELL
	sel_tile = NO_CELL
	targeting = ""
	_set_sheet_mode("")


func _select(mode: String) -> void:
	_set_sheet_mode(mode)
	_refresh()


func _select_unit(u: GameState.Unit) -> void:
	_clear_selection()
	if u.owner == gs.current:
		selected = u
		_select("unit")
	else:
		viewed_unit = u
		_select("enemy")


func _select_city(pos: Vector2i) -> void:
	_clear_selection()
	sel_city = pos
	_select("city")


func _select_tile(pos: Vector2i) -> void:
	_clear_selection()
	sel_tile = pos
	_select("tile")


func _on_units_pressed() -> void:
	if _locked():
		return
	# Recorre las tropas propias que todavía pueden hacer algo este turno.
	var ready_units: Array[GameState.Unit] = []
	for u in gs.units_of(gs.current):
		if not u.exhausted and (u.can_move() or not gs.attack_targets(u).is_empty()):
			ready_units.append(u)
	if ready_units.is_empty():
		_on_message("No quedan tropas por mover")
		return
	_unit_cycle = (_unit_cycle + 1) % ready_units.size()
	var u := ready_units[_unit_cycle]
	_select_unit(u)
	cam_target = Hex.to_world(u.pos)
	_update_camera()


func _on_tech_pressed() -> void:
	if _locked():
		return
	if sheet_mode == "tech" and not sheet_hidden:
		_clear_selection()
		_refresh()
		return
	_clear_selection()
	_select("tech")


# --- Toques en el tablero -----------------------------------------------------------

func _on_tap(screen_pos: Vector2) -> void:
	if _in_menu or _pause_layer.visible or _locked() or gs.winner != GameState.NO_PLAYER \
			or _reward_layer.visible or board.busy() or not gs.players[me].alive:
		return
	var hex_pos: Variant = _screen_to_hex(screen_pos)
	if hex_pos == null or not gs.tiles.has(hex_pos):
		_clear_selection()
		_refresh()
		return
	var h: Vector2i = hex_pos
	var unit_there := gs.unit_at(h)
	# Lo que está bajo la niebla no se puede tocar ni ver.
	if unit_there != null and unit_there.owner != gs.current and not gs.visible_tiles(gs.current).has(h):
		unit_there = null

	if selected != null and targeting != "":
		var ability := targeting
		targeting = ""
		if h in gs.ability_targets(selected, ability):
			_act("habilidad", [selected.id, ability, h])
		_refresh()
		return

	if selected != null:
		if h in gs.reachable(selected):
			_act("mover", [selected.id, h])
			_refresh()
			return
		if unit_there != null and unit_there in gs.attack_targets(selected):
			_act("atacar", [selected.id, unit_there.id])
			_refresh()
			return

	if unit_there != null:
		_select_unit(unit_there)
	elif gs.cities.has(h) and gs.is_explored(gs.current, h):
		_select_city(h)
	else:
		_select_tile(h)


# --- Panel inferior -------------------------------------------------------------------

func _set_sheet_mode(mode: String) -> void:
	var was_open := sheet_mode != "" and not sheet_hidden
	sheet_mode = mode
	sheet_hidden = false
	_detail = {}
	if mode == "":
		_hide_sheet()
	elif _sheet_locked and mode in ["unit", "enemy", "city", "tile"]:
		# Panel bloqueado: solo queda la pestaña para abrirlo a mano
		sheet_hidden = true
		_hide_sheet()
	elif not was_open:
		_open_sheet()


func _on_lock_pressed() -> void:
	_sheet_locked = not _sheet_locked
	_update_lock_button()
	if _sheet_locked and sheet_mode in ["unit", "enemy", "city", "tile"] and not sheet_hidden:
		sheet_hidden = true
		_hide_sheet()


func _update_lock_button() -> void:
	_lock_button.theme_type_variation = "BotonRojo" if _sheet_locked else "BotonAzul"
	# Flecha + candado: abierto = el panel se abre solo; cerrado = bloqueado
	_lock_button.icon = KoloniaTheme.icon("panel_cerrado" if _sheet_locked else "panel_abierto")


func _open_sheet() -> void:
	_sheet.visible = true
	_sheet.modulate.a = 0.0
	_show_tab.visible = false
	_rebuild_sheet()
	# Se espera a que el contenido tenga su ancho real para medir su alto.
	await get_tree().process_frame
	await get_tree().process_frame
	_layout_sheet()
	_sheet.modulate.a = 1.0
	var final_y := _sheet.position.y
	_sheet.position.y = final_y + _sheet.size.y + _bar_h
	if _sheet_tween:
		_sheet_tween.kill()
	_sheet_tween = create_tween()
	_sheet_tween.tween_property(_sheet, "position:y", final_y, 0.18) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


func _hide_sheet() -> void:
	if _sheet_tween:
		_sheet_tween.kill()
	_sheet.visible = false
	_show_tab.visible = sheet_mode != "" and sheet_hidden


func _on_collapse_pressed() -> void:
	sheet_hidden = true
	_hide_sheet()


func _on_show_tab_pressed() -> void:
	sheet_hidden = false
	_open_sheet()


## Ajusta el alto del panel a su contenido (máximo la mitad de la pantalla).
func _layout_sheet() -> void:
	var max_h := get_viewport().get_visible_rect().size.y * 0.5
	var content_h := _sheet_box.get_combined_minimum_size().y
	var scroll_h := minf(content_h, max_h)
	_sheet_scroll.custom_minimum_size.y = scroll_h
	# El alto se calcula pieza por pieza (encabezado + contenido + márgenes del panel)
	# para no depender de tamaños guardados de antes, que dejaban el final del
	# contenido escondido detrás de la barra inferior.
	var header_h := _sheet_ribbon.get_combined_minimum_size().y
	var sep := float(_sheet_v.get_theme_constant("separation"))
	var frame := _sheet.get_theme_stylebox("panel").get_minimum_size().y
	var total := header_h + sep + scroll_h + frame
	_sheet.offset_top = _sheet.offset_bottom - total
	_sheet.size.y = total


func _schedule_layout() -> void:
	await get_tree().process_frame
	_layout_sheet()
	await get_tree().process_frame
	_layout_sheet()


func _rebuild_sheet() -> void:
	if sheet_mode == "" or sheet_hidden:
		return
	for child in _sheet_box.get_children():
		_sheet_box.remove_child(child)
		child.queue_free()
	if not _detail.is_empty():
		_build_detail_view()
	else:
		match sheet_mode:
			"unit":
				_build_unit_sheet(selected)
			"enemy":
				_build_unit_sheet(viewed_unit)
			"city":
				_build_city_sheet(gs.cities[sel_city])
			"tile":
				_build_tile_sheet(sel_tile)
			"tech":
				_build_tech_sheet()
	_schedule_layout()


func _open_detail(kind: String, id: Variant) -> void:
	_detail = {"kind": kind, "id": id}
	_rebuild_sheet()
	_sheet_scroll.scroll_vertical = 0


func _close_detail() -> void:
	_detail = {}
	_refresh()


# --- Vistas principales (cuadrícula de íconos) -------------------------------------------

func _build_unit_sheet(u: GameState.Unit) -> void:
	var s := u.stats()
	_sheet_title.text = s["nombre"] if u.owner == gs.current else "%s de %s" % [s["nombre"], gs.players[u.owner].name]
	_unit_summary(u)
	if u.owner != gs.current:
		return
	var state := ""
	if u.capturing:
		state = "Conquistando esta ciudad"
	elif u.exhausted:
		state = "No puede actuar este turno"
	elif u.attacked:
		state = "Ya actuó este turno"
	elif u.moved:
		state = "Ya se movió (aún puede atacar)"
	if state != "":
		_sheet_label(state, 18, KoloniaTheme.TEXT_WARN)

	if targeting != "":
		_sheet_label("Toca una casilla morada", 22, KoloniaTheme.TEXT_MAGIC)
		_sheet_button("Cancelar", "", func():
			targeting = ""
			_refresh(), "BotonRojo")
		return

	# Habilidades de héroe
	if not u.abilities().is_empty():
		var grid := _grid()
		for a in u.abilities():
			var info: Dictionary = UnitTypes.ABILITIES[a]
			var wait: int = u.cooldowns.get(a, 0)
			var reason := gs.can_use_ability(u, a)
			_tile(grid, info["icono"], info["nombre"], {}, "ok" if reason == "" else "gris",
				func(): _open_detail("habilidad", a), "BotonAzul",
				"Espera %d" % wait if wait > 0 else "")

	# Si está en su ciudad, se puede mejorar la ciudad desde aquí.
	if gs.cities.has(u.pos) and gs.cities[u.pos].owner == gs.current:
		var c: GameState.City = gs.cities[u.pos]
		_sheet_separator()
		_city_info_row(c)
		var grid2 := _grid()
		_city_tiles(grid2, c)


func _unit_summary(u: GameState.Unit) -> void:
	var s := u.stats()
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 14)
	_sheet_box.add_child(row)
	row.add_child(_icon_rect(s["icono"], 76))
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(col)
	var hp := ProgressBar.new()
	hp.max_value = u.max_hp()
	hp.value = u.hp
	hp.show_percentage = false
	hp.custom_minimum_size = Vector2(0, 22)
	if u.hp * 2 <= u.max_hp():
		var fill := (hp.get_theme_stylebox("fill") as StyleBoxFlat).duplicate()
		fill.bg_color = Color("f08a2c")
		hp.add_theme_stylebox_override("fill", fill)
	col.add_child(hp)
	var stats := HFlowContainer.new()
	stats.add_theme_constant_override("h_separation", 16)
	col.add_child(stats)
	_stat(stats, "corazon", "%d/%d" % [u.hp, u.max_hp()])
	_stat(stats, "espada", str(gs.stat(u, "ataque")))
	_stat(stats, "escudo", str(gs.stat(u, "defensa")))
	_stat(stats, "bota", str(gs.stat(u, "movimiento")))
	_stat(stats, "diana", str(gs.attack_range(u)))


func _build_city_sheet(c: GameState.City) -> void:
	if c.owner == gs.current:
		_sheet_title.text = "Tu ciudad · Nivel %d" % c.level
	elif c.owner == GameState.NO_PLAYER:
		_sheet_title.text = "Ciudad abandonada"
	else:
		_sheet_title.text = "Ciudad de %s · Nivel %d" % [gs.players[c.owner].name, c.level]
	if c.owner != gs.current:
		_sheet_label("Deja una tropa dentro un turno completo para conquistarla.", 18, KoloniaTheme.TEXT_NOTE)
		return
	_city_info_row(c)
	var grid := _grid()
	_city_tiles(grid, c)
	_sheet_label("Entrenar", 20, KoloniaTheme.TEXT_TITLE)
	var grid2 := _grid()
	for type in gs.trainable_types(gs.current):
		var data: Dictionary = UnitTypes.DATA[type]
		var reason := gs.can_train(c.pos, type)
		_tile(grid2, data["icono"], data["nombre"], {"comida": data["costo"]}, "ok" if reason == "" else "gris",
			func(): _open_detail("entrenar", type), "BotonVerde")


func _city_info_row(c: GameState.City) -> void:
	var row := HFlowContainer.new()
	row.add_theme_constant_override("h_separation", 18)
	_sheet_box.add_child(row)
	_stat(row, "estrella", "%d/%d" % [c.points, c.points_needed()])
	_stat(row, "casa", "%d/%d" % [gs.units_from_city(c.pos), c.max_units()])
	_stat(row, "camino", str(gs.connected_cities(c.pos).size()))


## Mejorar ciudad + recompensas pendientes.
func _city_tiles(grid: GridContainer, c: GameState.City) -> void:
	var reason := gs.can_upgrade_city(c.pos)
	_tile(grid, "castillo", "Mejorar", {"oro": c.upgrade_cost()}, "ok" if reason == "" else "gris",
		func(): _open_detail("mejorar", c.pos), "BotonAmarillo")


func _build_tile_sheet(h: Vector2i) -> void:
	if not gs.is_explored(gs.current, h):
		_sheet_title.text = "Zona inexplorada"
		_sheet_label("Acerca una tropa para descubrir lo que hay aquí.", 20, KoloniaTheme.TEXT_NOTE)
		return
	var names := {"llanura": "Llanura", "bosque": "Bosque", "montana": "Montaña", "agua": "Agua"}
	var title: String = names.get(gs.tiles[h], gs.tiles[h])
	if gs.resources.has(h):
		title += " · " + GameState.RESOURCES[gs.resources[h]]["nombre"]
	if gs.buildings.has(h):
		title += " · %s nv.%d" % [GameState.BUILDINGS[gs.buildings[h]]["nombre"], gs.building_levels.get(h, 1)]
	_sheet_title.text = title
	if gs.territory.has(h):
		var tc: GameState.City = gs.cities[gs.territory[h]]
		if tc.owner >= 0:
			_sheet_label("Territorio tuyo" if tc.owner == gs.current else "Territorio de %s" % gs.players[tc.owner].name,
				18, KoloniaTheme.TEXT_NOTE)
	var actions := gs.tile_actions(h)
	if actions.is_empty():
		_sheet_label("No hay nada que hacer aquí", 20, KoloniaTheme.TEXT_NOTE)
		return
	var grid := _grid()
	for a in actions:
		var ok: bool = a["bloqueo"] == "" and gs.can_afford(gs.current, a["costo"])
		var id: String = a["id"]
		_tile(grid, a["icono"], a["corto"], a["costo"], "ok" if ok else ("bloqueado" if a["bloqueo"] != "" else "gris"),
			func(): _open_detail("accion", [h, id]), "BotonVerde", "", a.get("nivel", 1) == 2)


## Árbol de investigación: una cuadrícula de íconos por rama.
func _build_tech_sheet() -> void:
	_sheet_title.text = "Investigar"
	var gold := HBoxContainer.new()
	_sheet_box.add_child(gold)
	_stat(gold, "oro", "%d disponible" % gs.current_player().res["oro"])
	for branch in Techs.BRANCHES:
		_sheet_label(branch, 20, KoloniaTheme.TEXT_TITLE)
		var grid := _grid()
		for root in Techs.roots(branch):
			var chain: Array[String] = [root]
			var kids := Techs.children(root)
			while not kids.is_empty():
				chain.append(kids[0])
				kids = Techs.children(kids[0])
			for id in chain:
				var data: Dictionary = Techs.DATA[id]
				var state := "ok"
				if gs.has_tech(gs.current, id):
					state = "listo"
				elif gs.can_research(id) != "":
					var missing_req := false
					for req in data["requiere"]:
						if not gs.has_tech(gs.current, req):
							missing_req = true
					state = "bloqueado" if missing_req else "gris"
				_tile(grid, data["icono"], data["nombre"], {} if state == "listo" else {"oro": data["costo"]}, state,
					func(): _open_detail("tech", id), "BotonAzul", "", data["nivel"] == 2)


# --- Vista de detalle (información completa + botón de acción) ---------------------------

func _build_detail_view() -> void:
	var kind: String = _detail["kind"]
	var id: Variant = _detail["id"]
	match kind:
		"tech":
			var data: Dictionary = Techs.DATA[id]
			var owned := gs.has_tech(gs.current, id)
			var unit_type := ""
			for t in UnitTypes.DATA:
				if UnitTypes.DATA[t]["requiere"] == id:
					unit_type = t
			_detail_header(data["icono"], data["nombre"], data["descripcion"], data["nivel"] == 2)
			if unit_type != "":
				_unit_type_stats(unit_type)
			if owned:
				_sheet_label("✔ Ya investigada", 22, Color("3f8f22"))
			else:
				_detail_action("Investigar", {"oro": data["costo"]}, gs.can_research(id), func():
					_act("investigar", [id])
					_close_detail(), "BotonAzul")
		"entrenar":
			var data: Dictionary = UnitTypes.DATA[id]
			_detail_header(data["icono"], data["nombre"], "Tropa de %s" % gs.cities[sel_city].name, false)
			_unit_type_stats(id)
			_detail_action("Entrenar", {"comida": data["costo"]}, gs.can_train(sel_city, id), func():
				_act("entrenar", [sel_city, id])
				_close_detail(), "BotonVerde")
		"mejorar":
			var c: GameState.City = gs.cities[id]
			_detail_header("castillo", "Mejorar %s" % c.name,
				"Sube a nivel %d: +1 espacio de tropa, más comida y oro por turno, y una recompensa a elegir." % (c.level + 1), false)
			var row := HFlowContainer.new()
			_sheet_box.add_child(row)
			_stat(row, "estrella", "Puntos %d/%d" % [c.points, c.points_needed()])
			_detail_action("Mejorar", {"oro": c.upgrade_cost()}, gs.can_upgrade_city(id), func():
				_act("mejorar", [id])
				_close_detail(), "BotonAmarillo")
		"recompensa":
			var city_pos: Vector2i = id[0]
			var option: String = id[1]
			var info := gs.reward_info(option)
			_detail_header(info["icono"], info["nombre"], info["descripcion"], false)
			if option.begins_with("heroe:"):
				_unit_type_stats(option.substr(6))
			_detail_action("Elegir", {}, "", func():
				_act("recompensa", [city_pos, option])
				_detail = {}
				if option.begins_with("heroe:") and gs.unit_at(city_pos) != null:
					_select_unit(gs.unit_at(city_pos))
				else:
					_refresh(), "BotonAmarillo")
		"accion":
			var h: Vector2i = id[0]
			var action_id: String = id[1]
			var action: Dictionary = {}
			for a in gs.tile_actions(h):
				if a["id"] == action_id:
					action = a
			if action.is_empty():
				_close_detail.call_deferred()
				return
			_detail_header(action["icono"], action["nombre"], action["detalle"], action.get("nivel", 1) == 2)
			var reason: String = action["bloqueo"]
			if reason == "" and not gs.can_afford(gs.current, action["costo"]):
				reason = "Faltan recursos"
			_detail_action("Hacer", action["costo"], reason, func():
				_act("accion", [h, action_id])
				_close_detail(), "BotonVerde")
		"habilidad":
			var info: Dictionary = UnitTypes.ABILITIES[id]
			_detail_header(info["icono"], info["nombre"], info["descripcion"], false)
			_sheet_label("Espera entre usos: %d turnos. Usarla gasta la acción del turno." % info["espera"],
				18, KoloniaTheme.TEXT_NOTE)
			_detail_action("Usar", {}, gs.can_use_ability(selected, id), func():
				_detail = {}
				if info["objetivo"] == "ninguno":
					_act("habilidad", [selected.id, id, null])
				else:
					targeting = id
				_refresh(), "BotonAzul")


func _detail_header(icon_name: String, title: String, description: String, level2: bool) -> void:
	_sheet_title.text = title
	var back := Button.new()
	back.theme_type_variation = "BotonAmarillo"
	back.icon = KoloniaTheme.icon("volver")
	back.text = "Volver"
	back.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	back.custom_minimum_size = Vector2(0, 52)
	back.pressed.connect(_close_detail)
	_sheet_box.add_child(back)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 16)
	_sheet_box.add_child(row)
	var icon_holder := Control.new()
	icon_holder.custom_minimum_size = Vector2(110, 110)
	row.add_child(icon_holder)
	var ico := _icon_rect(icon_name, 110)
	icon_holder.add_child(ico)
	if level2:
		icon_holder.add_child(_level_badge())
	var desc := Label.new()
	desc.theme_type_variation = "TextoPergamino"
	desc.text = description
	desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	desc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	desc.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	desc.add_theme_font_size_override("font_size", 22)
	row.add_child(desc)


func _unit_type_stats(type: String) -> void:
	var s: Dictionary = UnitTypes.DATA[type]
	var row := HFlowContainer.new()
	row.add_theme_constant_override("h_separation", 16)
	_sheet_box.add_child(row)
	_stat(row, "corazon", str(s["vida"]))
	_stat(row, "espada", str(s["ataque"]))
	_stat(row, "escudo", str(s["defensa"]))
	_stat(row, "bota", str(s["movimiento"]))
	_stat(row, "diana", str(s["alcance"]))
	if s.has("en_agua"):
		var water: Dictionary = s["en_agua"]
		_sheet_label("En el agua:", 18, KoloniaTheme.TEXT_TITLE)
		var row2 := HFlowContainer.new()
		row2.add_theme_constant_override("h_separation", 16)
		_sheet_box.add_child(row2)
		_stat(row2, "espada", str(water.get("ataque", s["ataque"])))
		_stat(row2, "escudo", str(water.get("defensa", s["defensa"])))
		_stat(row2, "bota", str(water.get("movimiento", s["movimiento"])))
		_stat(row2, "diana", str(water.get("alcance", s["alcance"])))


## Botón grande de acción con su costo; si hay motivo, aparece bloqueado con el motivo.
func _detail_action(text: String, cost: Dictionary, reason: String, action: Callable, style: String) -> void:
	if reason != "":
		var warn := HBoxContainer.new()
		_sheet_box.add_child(warn)
		warn.add_child(_icon_rect("candado", 30))
		var l := Label.new()
		l.theme_type_variation = "TextoPergamino"
		l.text = reason
		l.add_theme_color_override("font_color", KoloniaTheme.TEXT_WARN)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		warn.add_child(l)
	var b := Button.new()
	b.theme_type_variation = style
	b.custom_minimum_size = Vector2(0, 76)
	b.add_theme_font_size_override("font_size", 28)
	b.text = text
	b.disabled = reason != ""
	b.pressed.connect(action)
	_sheet_box.add_child(b)
	if not cost.is_empty():
		var price := HBoxContainer.new()
		price.alignment = BoxContainer.ALIGNMENT_CENTER
		price.mouse_filter = Control.MOUSE_FILTER_IGNORE
		price.set_anchors_and_offsets_preset(Control.PRESET_CENTER_RIGHT, Control.PRESET_MODE_MINSIZE, 20)
		b.add_child(price)
		for k in cost:
			price.add_child(_icon_rect(k, 34))
			var l := Label.new()
			l.text = str(cost[k])
			l.add_theme_font_size_override("font_size", 26)
			price.add_child(l)
		price.grow_horizontal = Control.GROW_DIRECTION_BEGIN


# --- Piezas de la interfaz -----------------------------------------------------------------

func _grid() -> GridContainer:
	var g := GridContainer.new()
	var width := get_viewport().get_visible_rect().size.x
	g.columns = maxi(3, int((width - 40.0) / 170.0))
	g.add_theme_constant_override("h_separation", 10)
	g.add_theme_constant_override("v_separation", 10)
	_sheet_box.add_child(g)
	return g


## Casilla con ícono grande, nombre corto y costo.
## state: "ok" (se puede), "gris" (aún no alcanza), "bloqueado" (falta un requisito), "listo" (ya hecho).
func _tile(grid: GridContainer, icon_name: String, title: String, cost: Dictionary, state: String,
		action: Callable, style := "BotonAzul", badge := "", level2 := false) -> void:
	var b := Button.new()
	b.custom_minimum_size = Vector2(150, 156)
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	match state:
		"ok":
			b.theme_type_variation = style
		"listo":
			b.theme_type_variation = "BotonVerde"
		_:
			b.theme_type_variation = "BotonGris"
	b.pressed.connect(action)
	grid.add_child(b)

	var v := VBoxContainer.new()
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT, Control.PRESET_MODE_KEEP_SIZE, 8)
	v.offset_bottom = -14
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_theme_constant_override("separation", 2)
	b.add_child(v)
	var ico := _icon_rect(icon_name, 64)
	ico.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	if state == "bloqueado":
		ico.modulate = Color(1, 1, 1, 0.55)
	v.add_child(ico)
	var name_label := Label.new()
	name_label.text = title
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_label.add_theme_font_size_override("font_size", 18)
	name_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(name_label)
	if not cost.is_empty():
		var price := HBoxContainer.new()
		price.alignment = BoxContainer.ALIGNMENT_CENTER
		price.mouse_filter = Control.MOUSE_FILTER_IGNORE
		v.add_child(price)
		for k in cost:
			price.add_child(_icon_rect(k, 24))
			var l := Label.new()
			l.text = str(cost[k])
			l.add_theme_font_size_override("font_size", 18)
			price.add_child(l)

	# Marcas en la esquina: ✔ hecho, candado, nivel 2, aviso.
	var corner := ""
	if state == "listo":
		corner = "check"
	elif state == "bloqueado":
		corner = "candado"
	if corner != "":
		var mark := _icon_rect(corner, 34)
		mark.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT, Control.PRESET_MODE_KEEP_SIZE, 6)
		b.add_child(mark)
	if level2:
		b.add_child(_level_badge())
	if badge != "":
		var tag := Label.new()
		tag.text = badge
		tag.add_theme_font_size_override("font_size", 15)
		tag.add_theme_color_override("font_color", Color("ffe680"))
		tag.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT, Control.PRESET_MODE_MINSIZE, 8)
		b.add_child(tag)


func _level_badge() -> Control:
	var tag := Label.new()
	tag.text = "Nv.2"
	tag.add_theme_font_size_override("font_size", 17)
	tag.add_theme_color_override("font_color", Color("ffd23f"))
	tag.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT, Control.PRESET_MODE_MINSIZE, 6)
	tag.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return tag


func _icon_rect(icon_name: String, size_px: float) -> TextureRect:
	var t := TextureRect.new()
	t.texture = KoloniaTheme.icon(icon_name)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.custom_minimum_size = Vector2(size_px, size_px)
	t.size = Vector2(size_px, size_px)
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t


## Ícono pequeño + número (vida, ataque, puntos...)
func _stat(parent: Control, icon_name: String, text: String) -> void:
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 4)
	parent.add_child(h)
	h.add_child(_icon_rect(icon_name, 30))
	var l := Label.new()
	l.theme_type_variation = "TextoPergamino"
	l.text = text
	l.add_theme_font_size_override("font_size", 22)
	h.add_child(l)


func _sheet_label(text: String, font_size := 20, color := KoloniaTheme.TEXT_DARK) -> void:
	var l := Label.new()
	l.theme_type_variation = "TextoPergamino"
	l.text = text
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	_sheet_box.add_child(l)


func _sheet_separator() -> void:
	_sheet_box.add_child(HSeparator.new())


func _sheet_button(text: String, reason: String, action: Callable, style := "BotonVerde") -> void:
	var b := Button.new()
	b.theme_type_variation = style
	b.text = text
	b.custom_minimum_size = Vector2(0, 60)
	if reason != "":
		b.disabled = true
	b.pressed.connect(action)
	_sheet_box.add_child(b)


# --- Recompensa de nivel (obligatoria) ---------------------------------------------------

## Si una ciudad del jugador subió de nivel, se muestra una ventana con las 2 opciones
## y no se puede hacer nada más hasta elegir una.
func _check_pending_rewards() -> void:
	var pending: GameState.City = null
	if not bot_running and not _waiting and _my_turn():
		for c in gs.cities.values():
			if c.owner == gs.current and not c.pending_rewards.is_empty():
				pending = c
				break
	if pending == null:
		if _reward_layer.visible:
			_reward_layer.visible = false
			_reward_city = NO_CELL
			_set_bar_enabled(not _locked())
		return
	_set_bar_enabled(false)
	if _reward_layer.visible and _reward_city == pending.pos:
		return
	_reward_city = pending.pos
	_reward_layer.visible = true
	for child in _reward_box.get_children():
		_reward_box.remove_child(child)
		child.queue_free()
	var ribbon := PanelContainer.new()
	ribbon.theme_type_variation = "Cinta"
	_reward_box.add_child(ribbon)
	var title := Label.new()
	title.text = "¡%s subió a nivel %d!" % [pending.name, pending.level]
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 30)
	ribbon.add_child(title)
	var sub := Label.new()
	sub.theme_type_variation = "TextoPergamino"
	sub.text = "Elige una recompensa"
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.add_theme_font_size_override("font_size", 24)
	_reward_box.add_child(sub)
	var cards := HBoxContainer.new()
	cards.add_theme_constant_override("separation", 14)
	_reward_box.add_child(cards)
	for option in pending.pending_rewards[0]:
		var info := gs.reward_info(option)
		var card := Button.new()
		card.theme_type_variation = "BotonAmarillo"
		card.custom_minimum_size = Vector2(270, 330)
		card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		cards.add_child(card)
		var v := VBoxContainer.new()
		v.mouse_filter = Control.MOUSE_FILTER_IGNORE
		v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT, Control.PRESET_MODE_KEEP_SIZE, 12)
		v.offset_bottom = -18
		v.alignment = BoxContainer.ALIGNMENT_CENTER
		v.add_theme_constant_override("separation", 8)
		card.add_child(v)
		var ico := _icon_rect(info["icono"], 110)
		ico.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		v.add_child(ico)
		var name_l := Label.new()
		name_l.text = info["nombre"]
		name_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		name_l.add_theme_font_size_override("font_size", 26)
		v.add_child(name_l)
		var desc := Label.new()
		desc.text = info["descripcion"]
		desc.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		desc.add_theme_font_size_override("font_size", 18)
		v.add_child(desc)
		var city_pos := pending.pos
		card.pressed.connect(func():
			_act("recompensa", [city_pos, option])
			_reward_layer.visible = false
			_reward_city = NO_CELL
			_set_bar_enabled(true)
			if option.begins_with("heroe:") and gs.unit_at(city_pos) != null:
				_select_unit(gs.unit_at(city_pos))
			else:
				_refresh())


func _show_game_over() -> void:
	_clear_selection()
	if gs.winner == GameState.NO_PLAYER:
		_over_label.text = "¡Te eliminaron!"
	else:
		_over_label.text = "¡Ganaste!" if gs.winner == me else "Ganó %s" % gs.players[gs.winner].name
	_over_watch.visible = gs.winner == GameState.NO_PLAYER
	_over_again.visible = not net.is_online()
	_over_panel.visible = true
	_set_bar_enabled(false)


# --- Entrada: tocar, arrastrar y pellizcar ---------------------------------------------

func _unhandled_input(event: InputEvent) -> void:
	if _in_menu:
		return
	if event is InputEventScreenTouch:
		if event.pressed:
			_touches[event.index] = event.position
			if _touches.size() == 1:
				_press_pos = event.position
				_dragged = false
			elif _touches.size() == 2:
				_dragged = true
				_pinch_dist = _pinch_distance()
		else:
			var was_single := _touches.size() == 1
			_touches.erase(event.index)
			if was_single and not _dragged and not _over_ui(event.position):
				_on_tap(event.position)
	elif event is InputEventScreenDrag:
		_touches[event.index] = event.position
		if _touches.size() == 1:
			if event.position.distance_to(_press_pos) > TAP_TOLERANCE:
				_dragged = true
			if _dragged and not _over_ui(_press_pos):
				_pan(event.relative)
		elif _touches.size() >= 2:
			var d := _pinch_distance()
			if _pinch_dist > 0.0 and d > 0.0:
				_zoom(_pinch_dist / d)
			_pinch_dist = d
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_zoom(0.9)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_zoom(1.1)


func _pinch_distance() -> float:
	var pts := _touches.values()
	if pts.size() < 2:
		return 0.0
	return (pts[0] as Vector2).distance_to(pts[1])


func _over_ui(pos: Vector2) -> bool:
	for c in _ui_blockers:
		if c.is_visible_in_tree() and c.get_global_rect().has_point(pos):
			return true
	return false


func _pan(relative: Vector2) -> void:
	var factor := cam_distance * 0.0022
	cam_target -= Vector3(relative.x, 0, relative.y) * factor
	var limit := float(gs.radius) * 1.8
	cam_target.x = clampf(cam_target.x, -limit, limit)
	cam_target.z = clampf(cam_target.z, -limit, limit)
	_update_camera()


func _zoom(factor: float) -> void:
	cam_distance = clampf(cam_distance * factor, MIN_ZOOM, MAX_ZOOM)
	_update_camera()


## Se adapta a la orientación: en vertical se fija el ancho visible,
## en horizontal el alto, para que el tablero se vea bien en ambos casos.
func _on_screen_resized() -> void:
	_apply_safe_area()
	var size := get_viewport().get_visible_rect().size
	if size.y > size.x:
		camera.keep_aspect = Camera3D.KEEP_WIDTH
		camera.fov = 55.0
	else:
		camera.keep_aspect = Camera3D.KEEP_HEIGHT
		camera.fov = 45.0
	if _sheet != null and _sheet.visible:
		_layout_sheet.call_deferred()


## En teléfonos con cámara frontal "en la pantalla" (o barra de gestos), deja libre esa
## zona: la barra de arriba y la de abajo crecen lo necesario.
func _apply_safe_area() -> void:
	if _top_pad == null:
		return
	var insets := Vector4.ZERO  # arriba, abajo, izquierda, derecha (en unidades de la UI)
	var fake := OS.get_environment("KOLONIA_SAFE")
	if fake != "":
		var v := fake.split_floats(",")
		insets = Vector4(v[0], v[1], v[2], v[3])
	elif OS.has_feature("mobile"):
		var win := Vector2(DisplayServer.window_get_size())
		var safe := Rect2(DisplayServer.get_display_safe_area())
		if win.x > 0 and win.y > 0 and safe.size.x > 0:
			var vis := get_viewport().get_visible_rect().size
			var k := vis.y / win.y
			insets = Vector4(maxf(safe.position.y, 0.0) * k, maxf(win.y - safe.end.y, 0.0) * k,
				maxf(safe.position.x, 0.0) * k, maxf(win.x - safe.end.x, 0.0) * k)
	_top_pad.custom_minimum_size.y = insets.x
	_bottom_pad.custom_minimum_size.y = insets.y
	_bar_h = BAR_HEIGHT + insets.y
	_bottom_bar.custom_minimum_size.y = _bar_h
	_bottom_bar.offset_top = -_bar_h
	_sheet.offset_bottom = -_bar_h + 10
	_show_tab.offset_bottom = -_bar_h - 6
	_ui_root.offset_left = insets.z
	_ui_root.offset_right = -insets.w


func _update_camera() -> void:
	var a := deg_to_rad(CAMERA_ANGLE)
	camera.position = cam_target + Vector3(0, sin(a), cos(a)) * cam_distance
	camera.look_at(cam_target, Vector3.UP)


func _screen_to_hex(screen_pos: Vector2) -> Variant:
	var origin := camera.project_ray_origin(screen_pos)
	var dir := camera.project_ray_normal(screen_pos)
	var hit: Variant = Plane(Vector3.UP, 0.25).intersects_ray(origin, dir)
	if hit == null:
		return null
	return Hex.from_world(hit)


# --- Construcción de la escena -------------------------------------------------------

func _setup_world() -> void:
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.13, 0.2, 0.3)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.75, 0.78, 0.85)
	e.ambient_light_energy = 0.55
	# Tono de color más suave y natural (como las fotos de muestra de KayKit).
	e.tonemap_mode = Environment.TONE_MAPPER_AGX
	e.tonemap_exposure = 1.15
	env.environment = e
	add_child(env)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, -30, 0)
	sun.light_energy = 1.0
	sun.shadow_enabled = true
	add_child(sun)

	camera = Camera3D.new()
	add_child(camera)
	get_viewport().size_changed.connect(_on_screen_resized)
	_on_screen_resized()

	board = BoardView.new()
	add_child(board)


func _setup_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.theme = KoloniaTheme.build()
	_ui_root = root
	layer.add_child(root)

	# Barra superior: turno y recursos
	var top := _panel(root, "PanelMadera")
	_top_bar = top
	top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE, Control.PRESET_MODE_MINSIZE, 0)
	var top_col := VBoxContainer.new()
	top_col.add_theme_constant_override("separation", 0)
	top.add_child(top_col)
	_top_pad = Control.new()
	_top_pad.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top_col.add_child(_top_pad)
	var top_h := HBoxContainer.new()
	top_h.add_theme_constant_override("separation", 6)
	top_col.add_child(top_h)
	var pause := Button.new()
	pause.theme_type_variation = "BotonAmarillo"
	pause.icon = KoloniaTheme.icon("menu")
	pause.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	pause.custom_minimum_size = Vector2(72, 72)
	pause.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	pause.pressed.connect(_on_pause_pressed)
	top_h.add_child(pause)
	var top_v := VBoxContainer.new()
	top_v.add_theme_constant_override("separation", 6)
	top_v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top_h.add_child(top_v)
	# Candado: evita que el panel se abra solo al tocar el mapa
	_lock_button = Button.new()
	_lock_button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_lock_button.custom_minimum_size = Vector2(84, 72)
	_lock_button.add_theme_constant_override("icon_max_width", 56)
	_lock_button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_lock_button.pressed.connect(_on_lock_pressed)
	top_h.add_child(_lock_button)
	_update_lock_button()
	_top_label = Label.new()
	_top_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_top_label.add_theme_font_size_override("font_size", 24)
	top_v.add_child(_top_label)
	var chips := HBoxContainer.new()
	chips.alignment = BoxContainer.ALIGNMENT_CENTER
	chips.add_theme_constant_override("separation", 12)
	top_v.add_child(chips)
	for res in ["comida", "madera", "oro"]:
		var chip := PanelContainer.new()
		chip.theme_type_variation = "Chip"
		chips.add_child(chip)
		var row := HBoxContainer.new()
		chip.add_child(row)
		var ico := TextureRect.new()
		ico.texture = KoloniaTheme.icon(res)
		ico.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		ico.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		ico.custom_minimum_size = Vector2(38, 38)
		row.add_child(ico)
		var l := Label.new()
		l.add_theme_font_size_override("font_size", 22)
		row.add_child(l)
		_res_labels[res] = l

	# Panel deslizable (se agrega antes que la barra para quedar detrás de ella)
	_sheet = _panel(root, "PanelPergamino")
	_sheet.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE, Control.PRESET_MODE_MINSIZE, 0)
	_sheet.offset_left = 6
	_sheet.offset_right = -6
	_sheet.offset_bottom = -BAR_HEIGHT + 10
	_sheet.grow_vertical = Control.GROW_DIRECTION_BEGIN
	var sheet_v := VBoxContainer.new()
	sheet_v.add_theme_constant_override("separation", 10)
	_sheet.add_child(sheet_v)
	_sheet_v = sheet_v
	var ribbon := PanelContainer.new()
	ribbon.theme_type_variation = "Cinta"
	sheet_v.add_child(ribbon)
	_sheet_ribbon = ribbon
	var header := HBoxContainer.new()
	ribbon.add_child(header)
	_sheet_title = Label.new()
	_sheet_title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_sheet_title.add_theme_font_size_override("font_size", 26)
	_sheet_title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	header.add_child(_sheet_title)
	var collapse := Button.new()
	collapse.theme_type_variation = "BotonAmarillo"
	collapse.icon = KoloniaTheme.icon("flecha_abajo")
	collapse.custom_minimum_size = Vector2(64, 50)
	collapse.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	collapse.pressed.connect(_on_collapse_pressed)
	header.add_child(collapse)
	_sheet_scroll = ScrollContainer.new()
	_sheet_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	sheet_v.add_child(_sheet_scroll)
	_sheet_box = VBoxContainer.new()
	_sheet_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_sheet_box.add_theme_constant_override("separation", 10)
	_sheet_scroll.add_child(_sheet_box)
	_sheet.visible = false

	# Pestaña para volver a sacar el panel
	_show_tab = Button.new()
	_show_tab.theme_type_variation = "BotonAmarillo"
	_show_tab.icon = KoloniaTheme.icon("flecha_arriba")
	_show_tab.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_show_tab.custom_minimum_size = Vector2(110, 56)
	_show_tab.pressed.connect(_on_show_tab_pressed)
	root.add_child(_show_tab)
	_show_tab.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM, Control.PRESET_MODE_MINSIZE, 0)
	_show_tab.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_show_tab.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_show_tab.offset_bottom = -BAR_HEIGHT - 6
	_show_tab.offset_top = _show_tab.offset_bottom - 56
	_show_tab.visible = false
	_ui_blockers.append(_show_tab)

	# Barra inferior: acciones
	_bottom_bar = _panel(root, "PanelMadera")
	_bottom_bar.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE, Control.PRESET_MODE_MINSIZE, 0)
	_bottom_bar.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_bottom_bar.custom_minimum_size = Vector2(0, BAR_HEIGHT)
	_bottom_bar.offset_top = -BAR_HEIGHT
	var bottom_col := VBoxContainer.new()
	bottom_col.add_theme_constant_override("separation", 0)
	_bottom_bar.add_child(bottom_col)
	var bar := HBoxContainer.new()
	bar.add_theme_constant_override("separation", 10)
	bar.size_flags_vertical = Control.SIZE_EXPAND_FILL
	bottom_col.add_child(bar)
	_bottom_pad = Control.new()
	_bottom_pad.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bottom_col.add_child(_bottom_pad)
	_units_button = _bar_button(bar, "Tropas", "espadas", "BotonAzul", _on_units_pressed)
	_tech_button = _bar_button(bar, "Investigar", "libro", "BotonAzul", _on_tech_pressed)
	_end_button = _bar_button(bar, "Pasar turno", "reloj", "BotonVerde", _on_end_turn_pressed)

	# Ventana de recompensa de nivel: oscurece y bloquea todo lo demás.
	_reward_layer = Control.new()
	_reward_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_reward_layer.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(_reward_layer)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.55)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_reward_layer.add_child(dim)
	var reward_panel := PanelContainer.new()
	reward_panel.theme_type_variation = "PanelPergamino"
	_reward_layer.add_child(reward_panel)
	reward_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER, Control.PRESET_MODE_MINSIZE, 0)
	reward_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	reward_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	_reward_box = VBoxContainer.new()
	_reward_box.add_theme_constant_override("separation", 14)
	reward_panel.add_child(_reward_box)
	_reward_layer.visible = false
	_ui_blockers.append(_reward_layer)

	# Fin de partida
	_over_panel = _panel(root, "PanelPergamino")
	_over_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER, Control.PRESET_MODE_MINSIZE, 0)
	_over_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_over_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	var obox := VBoxContainer.new()
	obox.add_theme_constant_override("separation", 16)
	_over_panel.add_child(obox)
	var star := TextureRect.new()
	star.texture = KoloniaTheme.icon("estrella")
	star.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	star.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	star.custom_minimum_size = Vector2(0, 96)
	obox.add_child(star)
	_over_label = Label.new()
	_over_label.add_theme_font_size_override("font_size", 52)
	_over_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	obox.add_child(_over_label)
	_over_watch = Button.new()
	_over_watch.text = "Seguir mirando"
	_over_watch.icon = KoloniaTheme.icon("ojo")
	_over_watch.theme_type_variation = "BotonAzul"
	_over_watch.custom_minimum_size = Vector2(340, 80)
	_over_watch.pressed.connect(func(): _over_panel.visible = false)
	obox.add_child(_over_watch)
	var again := Button.new()
	again.text = "Nueva partida"
	again.icon = KoloniaTheme.icon("reiniciar")
	again.custom_minimum_size = Vector2(340, 80)
	again.pressed.connect(_new_game)
	obox.add_child(again)
	_over_again = again
	var to_menu := Button.new()
	to_menu.text = "Menú principal"
	to_menu.icon = KoloniaTheme.icon("salir")
	to_menu.theme_type_variation = "BotonRojo"
	to_menu.custom_minimum_size = Vector2(340, 80)
	to_menu.pressed.connect(_on_exit_pressed)
	obox.add_child(to_menu)
	_over_panel.visible = false

	# Pausa: continuar, reiniciar o salir al menú
	_pause_layer = Control.new()
	_pause_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_pause_layer.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(_pause_layer)
	var pdim := ColorRect.new()
	pdim.color = Color(0, 0, 0, 0.55)
	pdim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_pause_layer.add_child(pdim)
	var pc := CenterContainer.new()
	pc.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_pause_layer.add_child(pc)
	var pp := PanelContainer.new()
	pp.theme_type_variation = "PanelPergamino"
	pp.custom_minimum_size = Vector2(420, 0)
	pc.add_child(pp)
	var pv := VBoxContainer.new()
	pv.add_theme_constant_override("separation", 16)
	pp.add_child(pv)
	var pr := PanelContainer.new()
	pr.theme_type_variation = "Cinta"
	pv.add_child(pr)
	var pt := Label.new()
	pt.text = "Pausa"
	pt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	pt.add_theme_font_size_override("font_size", 34)
	pr.add_child(pt)
	for item in [["Continuar", "jugar", "BotonVerde", func(): _pause_layer.visible = false],
			["Reiniciar partida", "reiniciar", "BotonAmarillo", _on_restart_pressed],
			["Salir al menú", "salir", "BotonRojo", _on_exit_pressed]]:
		var b := Button.new()
		b.text = item[0]
		b.icon = KoloniaTheme.icon(item[1])
		b.theme_type_variation = item[2]
		b.custom_minimum_size = Vector2(0, 84)
		b.add_theme_font_size_override("font_size", 28)
		b.pressed.connect(item[3])
		pv.add_child(b)
		if item[1] == "reiniciar":
			_restart_button = b
	_pause_layer.visible = false
	_ui_blockers.append(_pause_layer)

	# Menú de inicio (encima de todo)
	_menu = StartMenu.new()
	root.add_child(_menu)
	_menu.play.connect(_on_menu_play)
	_menu.host_play.connect(_on_menu_host_play)
	_menu.net = net


func _bar_button(parent: Control, text: String, icon_name: String, style: String, action: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.icon = KoloniaTheme.icon(icon_name)
	b.theme_type_variation = style
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.add_theme_font_size_override("font_size", 27)
	b.add_theme_constant_override("icon_max_width", 54)
	b.pressed.connect(action)
	parent.add_child(b)
	return b


func _panel(parent: Control, style: String) -> PanelContainer:
	var p := PanelContainer.new()
	p.theme_type_variation = style
	parent.add_child(p)
	_ui_blockers.append(p)
	return p
