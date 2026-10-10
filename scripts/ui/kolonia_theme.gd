class_name KoloniaTheme
extends RefCounted
## Estilo visual de la interfaz: botones gruesos de colores con borde oscuro,
## paneles de pergamino, barras de madera y letra redonda con contorno.
## Todo se arma con código (StyleBoxFlat); cuando tengamos imágenes hechas con IA
## se pueden cambiar aquí por StyleBoxTexture sin tocar el resto del juego.

const FONT_PATH := "res://assets/fonts/LilitaOne-Regular.ttf"

const INK := Color("2b1a0e")            ## Contorno oscuro de todo
const PARCHMENT := Color("f6e7bf")
const PARCHMENT_EDGE := Color("8a5a2b")
const WOOD := Color("6b4423")
const WOOD_DARK := Color("3d2512")
const TEXT_DARK := Color("4a2c12")      ## Texto sobre pergamino
const TEXT_TITLE := Color("9c3d12")     ## Subtítulos sobre pergamino
const TEXT_NOTE := Color("7d6040")      ## Notas sobre pergamino
const TEXT_WARN := Color("c0531a")      ## Avisos sobre pergamino
const TEXT_MAGIC := Color("6a3fa0")     ## Habilidades

## Colores de botón: [cara, sombra inferior]
const BUTTONS := {
	"BotonVerde": [Color("7ed957"), Color("3f8f22")],
	"BotonAzul": [Color("5ab4f0"), Color("2a6fb0")],
	"BotonAmarillo": [Color("ffd23f"), Color("c98a12")],
	"BotonRojo": [Color("f0624d"), Color("a5291b")],
	"BotonGris": [Color("a8a196"), Color("6e685f")],
}
const DISABLED := [Color("b9b2a6"), Color("7d766b")]

static var _font: Font


static func font() -> Font:
	if _font == null:
		var f: FontFile = load(FONT_PATH)
		# Los símbolos que no tiene esta letra (★, ✔, →) salen de la letra por defecto.
		f.fallbacks = [ThemeDB.fallback_font]
		_font = f
	return _font


static func icon(name: String) -> Texture2D:
	return load("res://assets/ui/%s.svg" % name)


static func build() -> Theme:
	var t := Theme.new()
	t.default_font = font()
	t.default_font_size = 24

	# Texto normal: blanco con contorno (sobre el mapa y las barras de madera)
	t.set_color("font_color", "Label", Color.WHITE)
	t.set_color("font_outline_color", "Label", INK)
	t.set_constant("outline_size", "Label", 8)

	# Texto sobre pergamino: café, sin contorno
	t.set_type_variation("TextoPergamino", "Label")
	t.set_color("font_color", "TextoPergamino", TEXT_DARK)
	t.set_constant("outline_size", "TextoPergamino", 0)

	# Botones
	_button(t, "Button", BUTTONS["BotonVerde"][0], BUTTONS["BotonVerde"][1])
	for variation in BUTTONS:
		t.set_type_variation(variation, "Button")
		_button(t, variation, BUTTONS[variation][0], BUTTONS[variation][1])

	# Paneles
	t.set_type_variation("PanelPergamino", "PanelContainer")
	t.set_stylebox("panel", "PanelPergamino", _box(PARCHMENT, PARCHMENT_EDGE, 5, 22, 18, 6))
	t.set_type_variation("PanelMadera", "PanelContainer")
	var wood := _box(WOOD, WOOD_DARK, 4, 0, 12, 0)
	wood.border_color = INK
	t.set_stylebox("panel", "PanelMadera", wood)
	t.set_type_variation("Cinta", "PanelContainer")
	t.set_stylebox("panel", "Cinta", _box(Color("c9482b"), INK, 4, 14, 10, 4))
	t.set_type_variation("Chip", "PanelContainer")
	var chip := _box(Color(0, 0, 0, 0.35), INK, 3, 16, 8, 0)
	chip.content_margin_top = 4
	chip.content_margin_bottom = 4
	t.set_stylebox("panel", "Chip", chip)

	# Barra de vida
	t.set_stylebox("background", "ProgressBar", _box(Color("4a3a2a"), INK, 3, 9, 0, 0))
	t.set_stylebox("fill", "ProgressBar", _box(Color("5fd24a"), INK, 3, 9, 0, 0))

	# Separadores y barra de desplazamiento
	var line := StyleBoxLine.new()
	line.color = PARCHMENT_EDGE
	line.thickness = 3
	t.set_stylebox("separator", "HSeparator", line)
	t.set_constant("separation", "HSeparator", 14)
	t.set_stylebox("scroll", "VScrollBar", _box(Color(0, 0, 0, 0.12), Color(0, 0, 0, 0), 0, 8, 0, 0))
	for state in ["grabber", "grabber_highlight", "grabber_pressed"]:
		t.set_stylebox(state, "VScrollBar", _box(WOOD, INK, 2, 8, 0, 0))
	return t


static func _button(t: Theme, type: String, face: Color, shade: Color) -> void:
	t.set_stylebox("normal", type, _button_box(face, shade, false))
	t.set_stylebox("hover", type, _button_box(face.lightened(0.12), shade, false))
	t.set_stylebox("pressed", type, _button_box(face.darkened(0.08), shade, true))
	t.set_stylebox("focus", type, StyleBoxEmpty.new())
	t.set_stylebox("disabled", type, _button_box(DISABLED[0], DISABLED[1], false))
	for c in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color"]:
		t.set_color(c, type, Color.WHITE)
	t.set_color("font_disabled_color", type, Color("f2efe9"))
	t.set_color("font_outline_color", type, INK)
	t.set_constant("outline_size", type, 8)
	t.set_constant("icon_max_width", type, 44)
	t.set_constant("h_separation", type, 10)
	t.set_font_size("font_size", type, 22)


## Botón "gordito": cara de color, sombra inferior gruesa más oscura y contorno.
## Al presionarlo la sombra se achica y el texto baja, como si se hundiera.
static func _button_box(face: Color, shade: Color, pressed: bool) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = face
	s.border_color = shade
	s.set_border_width_all(3)
	s.border_width_bottom = 3 if pressed else 9
	s.set_corner_radius_all(16)
	s.shadow_color = INK
	s.shadow_size = 3
	s.shadow_offset = Vector2(0, 1)
	s.content_margin_left = 16
	s.content_margin_right = 16
	s.content_margin_top = 16 if pressed else 10
	s.content_margin_bottom = 8
	s.expand_margin_top = 0
	s.anti_aliasing = true
	return s


static func _box(bg: Color, border: Color, border_w: int, radius: int, margin: int, shadow: int) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = border
	s.set_border_width_all(border_w)
	s.set_corner_radius_all(radius)
	s.set_content_margin_all(margin)
	if shadow > 0:
		s.shadow_color = Color(0, 0, 0, 0.45)
		s.shadow_size = shadow
		s.shadow_offset = Vector2(0, 3)
	s.anti_aliasing = true
	return s
