class_name StartMenu
extends Control
## Menú de inicio y pantalla para preparar la partida (enemigos, mapa, color, tribu).

signal play(config: MatchConfig)
signal host_play(config: MatchConfig)   ## El anfitrión empieza la partida en red

var config: MatchConfig
var _home: Control
var _setup: Control
var _enemy_label: Label
var _enemy_dots: HBoxContainer
var _size_buttons := {}
var _size_note: Label
var _color_buttons: Array[Button] = []
var _fog_button: Button
var _setup_title: Label
var _enemy_title: Label
var _tribe_rows: Array[Control] = []
var _lobby_section: Control
var _lobby_box: VBoxContainer
var _ip_note: Label
var _net_mode := false          ## La pantalla de preparar partida es para una partida en red

## Juego en red (lo pone main)
var net: Net:
	set(value):
		net = value
		net.games_found_changed.connect(_refresh_found)
		net.lobby_changed.connect(_on_lobby_changed)
		net.connection_failed.connect(func(): show_net("No se pudo conectar con esa partida."))
var _net_screen: Control
var _net_msg: Label
var _found_box: VBoxContainer
var _ip_edit: LineEdit
var _wait_screen: Control
var _wait_status: Label
var _wait_list: VBoxContainer
var _wait_colors: Array[Button] = []


func _init() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	config = MatchConfig.load_saved()


func _ready() -> void:
	theme = KoloniaTheme.build()
	_build_home()
	_build_setup()
	_build_net()
	_build_wait()
	show_home()


func _show_only(screen: Control) -> void:
	for c in [_home, _setup, _net_screen, _wait_screen]:
		c.visible = c == screen


func show_home() -> void:
	visible = true
	if net != null:
		net.stop_search()
	_show_only(_home)


func show_setup() -> void:
	_net_mode = false
	_show_only(_setup)
	_refresh()


## Pantalla de juego en red: crear partida o buscar una en el mismo Wi-Fi.
func show_net(message := "") -> void:
	visible = true
	if net.is_online():
		net.close()
	_net_mode = false
	_show_only(_net_screen)
	_net_msg.text = message
	_net_msg.visible = message != ""
	net.start_search()
	_refresh_found()


func show_net_message(text: String) -> void:
	show_net(text)


# --- Pantalla de inicio ------------------------------------------------------------------

func _build_home() -> void:
	_home = Control.new()
	_home.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_home.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_home)
	# Oscurece arriba y abajo para que se lea el título sobre el mapa
	var shade := TextureRect.new()
	var grad := Gradient.new()
	grad.set_color(0, Color(0.05, 0.07, 0.12, 0.85))
	grad.add_point(0.35, Color(0.05, 0.07, 0.12, 0.15))
	grad.add_point(0.65, Color(0.05, 0.07, 0.12, 0.15))
	grad.set_color(grad.get_point_count() - 1, Color(0.05, 0.07, 0.12, 0.85))
	var gt := GradientTexture2D.new()
	gt.gradient = grad
	gt.fill_from = Vector2(0, 0)
	gt.fill_to = Vector2(0, 1)
	shade.texture = gt
	shade.stretch_mode = TextureRect.STRETCH_SCALE
	shade.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_home.add_child(shade)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 18)
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	_home.add_child(v)
	var top_space := Control.new()
	top_space.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(top_space)
	var crown := TextureRect.new()
	crown.texture = KoloniaTheme.icon("corona")
	crown.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	crown.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	crown.custom_minimum_size = Vector2(0, 90)
	v.add_child(crown)
	var title := Label.new()
	title.text = "KOLONIA"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 104)
	title.add_theme_color_override("font_color", Color("ffd23f"))
	title.add_theme_constant_override("outline_size", 22)
	title.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.5))
	title.add_theme_constant_override("shadow_offset_y", 8)
	v.add_child(title)
	var sub := Label.new()
	sub.text = "Conquista todas las ciudades"
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.add_theme_font_size_override("font_size", 30)
	v.add_child(sub)
	var mid := Control.new()
	mid.size_flags_vertical = Control.SIZE_EXPAND_FILL
	mid.size_flags_stretch_ratio = 1.6
	v.add_child(mid)
	var buttons := VBoxContainer.new()
	buttons.add_theme_constant_override("separation", 18)
	buttons.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	v.add_child(buttons)
	_big_button(buttons, "Jugar", "jugar", "BotonVerde", show_setup)
	_big_button(buttons, "Jugar en red", "wifi", "BotonAzul", func(): show_net())
	_big_button(buttons, "Salir", "salir", "BotonRojo", func(): get_tree().quit())
	var bottom := Control.new()
	bottom.custom_minimum_size = Vector2(0, 70)
	v.add_child(bottom)


func _big_button(parent: Control, text: String, icon_name: String, style: String, action: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.icon = KoloniaTheme.icon(icon_name)
	b.theme_type_variation = style
	b.custom_minimum_size = Vector2(380, 96)
	b.add_theme_font_size_override("font_size", 38)
	b.pressed.connect(action)
	parent.add_child(b)
	return b


# --- Preparar partida --------------------------------------------------------------------

func _build_setup() -> void:
	_setup = Control.new()
	_setup.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_setup)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.45)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_setup.add_child(dim)
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right"]:
		margin.add_theme_constant_override("margin_" + side, 14)
	margin.add_theme_constant_override("margin_top", 24)
	margin.add_theme_constant_override("margin_bottom", 24)
	_setup.add_child(margin)
	var center := CenterContainer.new()
	margin.add_child(center)
	var panel := PanelContainer.new()
	panel.theme_type_variation = "PanelPergamino"
	panel.custom_minimum_size = Vector2(640, 0)
	center.add_child(panel)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 12)
	panel.add_child(v)

	var ribbon := PanelContainer.new()
	ribbon.theme_type_variation = "Cinta"
	v.add_child(ribbon)
	var rt := Label.new()
	_setup_title = rt
	rt.text = "Nueva partida"
	rt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	rt.add_theme_font_size_override("font_size", 34)
	ribbon.add_child(rt)

	# Enemigos
	_enemy_title = _section(v, "robot", "Enemigos (bots)")
	var er := HBoxContainer.new()
	er.alignment = BoxContainer.ALIGNMENT_CENTER
	er.add_theme_constant_override("separation", 16)
	v.add_child(er)
	_small_button(er, "−", "BotonRojo", func(): _change_enemies(-1))
	_enemy_label = Label.new()
	_enemy_label.custom_minimum_size = Vector2(80, 0)
	_enemy_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_enemy_label.add_theme_font_size_override("font_size", 48)
	er.add_child(_enemy_label)
	_small_button(er, "+", "BotonVerde", func(): _change_enemies(1))
	_enemy_dots = HBoxContainer.new()
	_enemy_dots.alignment = BoxContainer.ALIGNMENT_CENTER
	_enemy_dots.add_theme_constant_override("separation", 8)
	v.add_child(_enemy_dots)

	# Tamaño del mapa
	_section(v, "mapa", "Tamaño del mapa")
	var grid := GridContainer.new()
	grid.columns = 4
	grid.add_theme_constant_override("h_separation", 8)
	v.add_child(grid)
	for key in MatchConfig.SIZE_ORDER:
		var b := Button.new()
		b.text = MatchConfig.MAP_SIZES[key]["nombre"]
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.custom_minimum_size = Vector2(0, 66)
		b.add_theme_font_size_override("font_size", 22)
		b.pressed.connect(func(): config.map_size = key; _refresh())
		grid.add_child(b)
		_size_buttons[key] = b
	_size_note = Label.new()
	_size_note.theme_type_variation = "TextoPergamino"
	_size_note.add_theme_font_size_override("font_size", 19)
	_size_note.add_theme_color_override("font_color", KoloniaTheme.TEXT_NOTE)
	_size_note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_size_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(_size_note)

	# Color
	_section(v, "paleta", "Tu color")
	var colors := HBoxContainer.new()
	colors.alignment = BoxContainer.ALIGNMENT_CENTER
	colors.add_theme_constant_override("separation", 8)
	v.add_child(colors)
	for i in MatchConfig.COLORS.size():
		var b := Button.new()
		b.custom_minimum_size = Vector2(62, 62)
		b.tooltip_text = MatchConfig.COLORS[i][0]
		b.pressed.connect(func(): _pick_color(i))
		colors.add_child(b)
		_color_buttons.append(b)

	# Tribu
	_tribe_rows.append(_section(v, "corona", "Tribu").get_parent())
	var tribe := PanelContainer.new()
	tribe.theme_type_variation = "Chip"
	v.add_child(tribe)
	_tribe_rows.append(tribe)
	var th := HBoxContainer.new()
	th.add_theme_constant_override("separation", 12)
	tribe.add_child(th)
	var ti := TextureRect.new()
	ti.texture = KoloniaTheme.icon("escudo")
	ti.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	ti.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	ti.custom_minimum_size = Vector2(56, 56)
	th.add_child(ti)
	var tv := VBoxContainer.new()
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	th.add_child(tv)
	var tn := Label.new()
	tn.text = MatchConfig.TRIBES["reino"]["nombre"]
	tn.add_theme_font_size_override("font_size", 28)
	tv.add_child(tn)
	var td := Label.new()
	td.text = MatchConfig.TRIBES["reino"]["descripcion"] + " Más tribus pronto."
	td.add_theme_font_size_override("font_size", 17)
	td.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	tv.add_child(td)

	# Niebla
	var fog_row := HBoxContainer.new()
	fog_row.add_theme_constant_override("separation", 12)
	v.add_child(fog_row)
	var fi := TextureRect.new()
	fi.texture = KoloniaTheme.icon("nube")
	fi.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	fi.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	fi.custom_minimum_size = Vector2(44, 44)
	fog_row.add_child(fi)
	var fl := Label.new()
	fl.text = "Niebla de guerra"
	fl.theme_type_variation = "TextoPergamino"
	fl.add_theme_font_size_override("font_size", 26)
	fl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	fog_row.add_child(fl)
	_fog_button = Button.new()
	_fog_button.custom_minimum_size = Vector2(130, 60)
	_fog_button.pressed.connect(func(): config.fog = not config.fog; _refresh())
	fog_row.add_child(_fog_button)

	# Jugadores conectados (solo en red)
	_lobby_section = VBoxContainer.new()
	_lobby_section.add_theme_constant_override("separation", 8)
	v.add_child(_lobby_section)
	_section(_lobby_section, "wifi", "Jugadores en la partida")
	_lobby_box = VBoxContainer.new()
	_lobby_box.add_theme_constant_override("separation", 6)
	_lobby_section.add_child(_lobby_box)
	_ip_note = _note_label(_lobby_section, "")

	# Botones finales
	var sep := HSeparator.new()
	v.add_child(sep)
	var br := HBoxContainer.new()
	br.add_theme_constant_override("separation", 14)
	v.add_child(br)
	var back := Button.new()
	back.text = "Atrás"
	back.icon = KoloniaTheme.icon("volver")
	back.theme_type_variation = "BotonGris"
	back.custom_minimum_size = Vector2(0, 84)
	back.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	back.pressed.connect(func(): show_net() if _net_mode else show_home())
	br.add_child(back)
	var go := Button.new()
	go.text = "¡A jugar!"
	go.icon = KoloniaTheme.icon("espadas")
	go.theme_type_variation = "BotonVerde"
	go.custom_minimum_size = Vector2(0, 84)
	go.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	go.size_flags_stretch_ratio = 1.6
	go.add_theme_font_size_override("font_size", 32)
	go.pressed.connect(_on_play)
	br.add_child(go)


func _section(parent: Control, icon_name: String, text: String) -> Label:
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 10)
	parent.add_child(h)
	var i := TextureRect.new()
	i.texture = KoloniaTheme.icon(icon_name)
	i.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	i.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	i.custom_minimum_size = Vector2(40, 40)
	h.add_child(i)
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", 26)
	l.add_theme_color_override("font_color", KoloniaTheme.TEXT_TITLE)
	l.add_theme_constant_override("outline_size", 0)
	h.add_child(l)
	return l


func _small_button(parent: Control, text: String, style: String, action: Callable) -> void:
	var b := Button.new()
	b.text = text
	b.theme_type_variation = style
	b.custom_minimum_size = Vector2(76, 70)
	b.add_theme_font_size_override("font_size", 40)
	b.pressed.connect(action)
	parent.add_child(b)


func _change_enemies(d: int) -> void:
	var humans := net.lobby.size() if _net_mode else 1
	var min_bots := 0 if _net_mode and humans >= 2 else 1
	config.enemies = clampi(config.enemies + d, min_bots, 8 - humans)
	_refresh()


func _pick_color(i: int) -> void:
	if _net_mode:
		net.request_color(i)
		config.color_index = i
	else:
		config.color_index = i
	_refresh()


static func _swatch(color: Color, selected: bool, pressed: bool) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = color.darkened(0.1) if pressed else color
	s.set_corner_radius_all(31)
	s.border_color = Color.WHITE if selected else KoloniaTheme.INK
	s.set_border_width_all(6 if selected else 3)
	s.shadow_color = Color(0, 0, 0, 0.4)
	s.shadow_size = 3 if selected else 1
	s.anti_aliasing = true
	return s


func _refresh() -> void:
	if _net_mode:
		config.humans = net.human_colors()
		config.color_index = net.lobby.get(1, config.color_index)
		var humans := config.humans.size()
		config.enemies = clampi(config.enemies, 0 if humans >= 2 else 1, 8 - humans)
	else:
		config.humans = []
	_setup_title.text = "Partida en red" if _net_mode else "Nueva partida"
	_enemy_title.text = "Bots" if _net_mode else "Enemigos (bots)"
	for r in _tribe_rows:
		r.visible = not _net_mode
	_lobby_section.visible = _net_mode
	if _net_mode:
		_fill_player_list(_lobby_box)
		var ips := Net.local_ips()
		_ip_note.text = ("Si no te encuentran, que escriban tu dirección: %s" % ", ".join(ips)) if not ips.is_empty() \
			else "No se encontró una red Wi-Fi."
	_enemy_label.text = str(config.enemies)
	for c in _enemy_dots.get_children():
		c.queue_free()
	var players := config.players()
	for i in range(config.humans.size() if _net_mode else 1, players.size()):
		var dot := Panel.new()
		dot.custom_minimum_size = Vector2(30, 30)
		dot.add_theme_stylebox_override("panel", _swatch(players[i][2], false, false))
		_enemy_dots.add_child(dot)
	var eff := config.effective_size()
	for key in _size_buttons:
		var b: Button = _size_buttons[key]
		var fits: bool = int(MatchConfig.MAP_SIZES[key]["max"]) >= config.player_count()
		b.disabled = not fits
		b.theme_type_variation = "BotonAmarillo" if key == eff else "BotonAzul"
	if eff != config.map_size:
		_size_note.text = "Con %d jugadores el mapa más chico es %s." % [config.player_count(), MatchConfig.MAP_SIZES[eff]["nombre"]]
	elif _net_mode:
		_size_note.text = "%d jugadores en total (%d personas + %d bots)." % [config.player_count(), config.humans.size(), config.enemies]
	else:
		_size_note.text = "%d jugadores en total (tú + %d)." % [config.player_count(), config.enemies]
	var host_free := net.free_colors(1) if _net_mode else []
	for i in _color_buttons.size():
		var b := _color_buttons[i]
		var col: Color = MatchConfig.COLORS[i][2]
		var sel := i == config.color_index
		b.disabled = _net_mode and not i in host_free
		b.add_theme_stylebox_override("disabled", _swatch(col.darkened(0.6), false, false))
		b.add_theme_stylebox_override("normal", _swatch(col, sel, false))
		b.add_theme_stylebox_override("hover", _swatch(col.lightened(0.1), sel, false))
		b.add_theme_stylebox_override("pressed", _swatch(col, sel, true))
		b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		b.text = "✔" if sel else ""
	_fog_button.text = "Sí" if config.fog else "No"
	_fog_button.theme_type_variation = "BotonVerde" if config.fog else "BotonGris"


func _on_play() -> void:
	config.map_size = config.effective_size()
	if _net_mode:
		config.humans = net.human_colors()
		visible = false
		host_play.emit(config)
		return
	config.save()
	visible = false
	play.emit(config)


# --- Juego en red: buscar / crear / sala de espera ----------------------------------------

func _panel_screen(title_text: String) -> Array:
	var screen := Control.new()
	screen.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(screen)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.45)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	screen.add_child(dim)
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right"]:
		margin.add_theme_constant_override("margin_" + side, 14)
	margin.add_theme_constant_override("margin_top", 24)
	margin.add_theme_constant_override("margin_bottom", 24)
	screen.add_child(margin)
	var center := CenterContainer.new()
	margin.add_child(center)
	var panel := PanelContainer.new()
	panel.theme_type_variation = "PanelPergamino"
	panel.custom_minimum_size = Vector2(640, 0)
	center.add_child(panel)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 14)
	panel.add_child(v)
	var ribbon := PanelContainer.new()
	ribbon.theme_type_variation = "Cinta"
	v.add_child(ribbon)
	var rt := Label.new()
	rt.text = title_text
	rt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	rt.add_theme_font_size_override("font_size", 34)
	ribbon.add_child(rt)
	return [screen, v]


func _note_label(parent: Control, text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.theme_type_variation = "TextoPergamino"
	l.add_theme_font_size_override("font_size", 19)
	l.add_theme_color_override("font_color", KoloniaTheme.TEXT_NOTE)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(560, 0)
	parent.add_child(l)
	return l


func _wide_button(parent: Control, text: String, icon_name: String, style: String, action: Callable) -> Button:
	var b := Button.new()
	b.text = text
	if icon_name != "":
		b.icon = KoloniaTheme.icon(icon_name)
	b.theme_type_variation = style
	b.custom_minimum_size = Vector2(0, 80)
	b.add_theme_font_size_override("font_size", 28)
	b.pressed.connect(action)
	parent.add_child(b)
	return b


func _build_net() -> void:
	var made := _panel_screen("Jugar en red")
	_net_screen = made[0]
	var v: VBoxContainer = made[1]
	_note_label(v, "Todos deben estar conectados al mismo Wi-Fi, o al punto de acceso del teléfono de uno de ustedes.")
	_net_msg = _note_label(v, "")
	_net_msg.add_theme_color_override("font_color", Color("b0301c"))
	_wide_button(v, "Crear partida", "corona", "BotonVerde", _on_create_game)
	v.add_child(HSeparator.new())
	_section(v, "wifi", "Partidas encontradas")
	_found_box = VBoxContainer.new()
	_found_box.add_theme_constant_override("separation", 8)
	v.add_child(_found_box)
	_section(v, "mapa", "Unirse con la dirección")
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	v.add_child(row)
	_ip_edit = LineEdit.new()
	_ip_edit.placeholder_text = "192.168.1.10"
	_ip_edit.custom_minimum_size = Vector2(0, 72)
	_ip_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_ip_edit.add_theme_font_size_override("font_size", 28)
	_ip_edit.virtual_keyboard_type = LineEdit.KEYBOARD_TYPE_NUMBER_DECIMAL
	var box := StyleBoxFlat.new()
	box.bg_color = Color("fff6dd")
	box.border_color = KoloniaTheme.INK
	box.set_border_width_all(3)
	box.set_corner_radius_all(12)
	box.content_margin_left = 14
	box.content_margin_right = 14
	_ip_edit.add_theme_stylebox_override("normal", box)
	_ip_edit.add_theme_stylebox_override("focus", box)
	_ip_edit.add_theme_color_override("font_color", KoloniaTheme.TEXT_DARK)
	_ip_edit.add_theme_color_override("font_placeholder_color", KoloniaTheme.TEXT_NOTE)
	row.add_child(_ip_edit)
	var join := Button.new()
	join.text = "Unirse"
	join.theme_type_variation = "BotonAzul"
	join.custom_minimum_size = Vector2(170, 72)
	join.add_theme_font_size_override("font_size", 26)
	join.pressed.connect(func(): _join(_ip_edit.text.strip_edges()))
	row.add_child(join)
	v.add_child(HSeparator.new())
	_wide_button(v, "Atrás", "volver", "BotonGris", show_home)


func _refresh_found() -> void:
	if _found_box == null:
		return
	for c in _found_box.get_children():
		c.queue_free()
	if net.found.is_empty():
		_note_label(_found_box, "Buscando partidas en tu Wi-Fi…")
		return
	for ip in net.found:
		var g: Dictionary = net.found[ip]
		var b := _wide_button(_found_box, "%s  ·  %d jugador%s" % [g["nombre"], g["jugadores"],
			"" if g["jugadores"] == 1 else "es"], "jugar", "BotonAmarillo", func(): _join(ip))
		b.add_theme_font_size_override("font_size", 24)


func _on_create_game() -> void:
	var c: Array = MatchConfig.COLORS[config.color_index]
	if net.host(config.color_index, "Partida de " + c[0]) != OK:
		show_net("No se pudo crear la partida (¿estás conectado al Wi-Fi?).")
		return
	_net_mode = true
	if config.enemies > 7:
		config.enemies = 7
	_show_only(_setup)
	_refresh()


func _join(ip: String) -> void:
	if ip.is_valid_ip_address() == false:
		show_net("Escribe una dirección válida, por ejemplo 192.168.1.10")
		return
	if net.join(ip) != OK:
		show_net("No se pudo conectar con esa partida.")
		return
	_show_only(_wait_screen)
	_wait_status.text = "Conectando con %s…" % ip
	_refresh_wait()


func _build_wait() -> void:
	var made := _panel_screen("Sala de espera")
	_wait_screen = made[0]
	var v: VBoxContainer = made[1]
	_wait_status = _note_label(v, "")
	_section(v, "wifi", "Jugadores")
	_wait_list = VBoxContainer.new()
	_wait_list.add_theme_constant_override("separation", 6)
	v.add_child(_wait_list)
	_section(v, "paleta", "Tu color")
	var colors := HBoxContainer.new()
	colors.alignment = BoxContainer.ALIGNMENT_CENTER
	colors.add_theme_constant_override("separation", 8)
	v.add_child(colors)
	for i in MatchConfig.COLORS.size():
		var b := Button.new()
		b.custom_minimum_size = Vector2(62, 62)
		b.pressed.connect(func(): net.request_color(i))
		colors.add_child(b)
		_wait_colors.append(b)
	v.add_child(HSeparator.new())
	_wide_button(v, "Salir de la partida", "salir", "BotonRojo", func(): show_net())


func _on_lobby_changed() -> void:
	if _setup.visible and _net_mode:
		_refresh()
	elif _wait_screen.visible:
		_refresh_wait()


func _refresh_wait() -> void:
	var me := multiplayer.get_unique_id()
	if net.lobby.has(me):
		_wait_status.text = "Esperando a que el anfitrión empiece la partida…"
	_fill_player_list(_wait_list)
	var mine: int = net.lobby.get(me, -1)
	var free := net.free_colors(me)
	for i in _wait_colors.size():
		var b := _wait_colors[i]
		var col: Color = MatchConfig.COLORS[i][2]
		var sel := i == mine
		b.disabled = not i in free
		b.add_theme_stylebox_override("normal", _swatch(col, sel, false))
		b.add_theme_stylebox_override("hover", _swatch(col.lightened(0.1), sel, false))
		b.add_theme_stylebox_override("pressed", _swatch(col, sel, true))
		b.add_theme_stylebox_override("disabled", _swatch(col.darkened(0.6), false, false))
		b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		b.text = "✔" if sel else ""


## Lista de personas en la sala, cada una con su color.
func _fill_player_list(box: VBoxContainer) -> void:
	for c in box.get_children():
		c.queue_free()
	var me := multiplayer.get_unique_id()
	for peer in net.lobby_order:
		if not net.lobby.has(peer):
			continue
		var color: Array = MatchConfig.COLORS[net.lobby[peer]]
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 12)
		box.add_child(row)
		var dot := Panel.new()
		dot.custom_minimum_size = Vector2(38, 38)
		dot.add_theme_stylebox_override("panel", _swatch(color[2], false, false))
		row.add_child(dot)
		var l := Label.new()
		var tags := []
		if peer == 1:
			tags.append("anfitrión")
		if peer == me:
			tags.append("tú")
		l.text = color[0] + ("  (%s)" % ", ".join(tags) if not tags.is_empty() else "")
		l.theme_type_variation = "TextoPergamino"
		l.add_theme_font_size_override("font_size", 26)
		row.add_child(l)
