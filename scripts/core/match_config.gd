class_name MatchConfig
extends RefCounted
## Opciones de una partida: jugadores (color, tribu, bot o humano) y tamaño del mapa.
## El color es de cada jugador y no depende de la tribu: la tribu solo cambia el estilo
## de las tropas.

## Colores que se pueden elegir: [nombre, adjetivo femenino (para "Capital ..."), color]
const COLORS := [
	["Rojo", "Roja", Color(0.85, 0.2, 0.2)],
	["Azul", "Azul", Color(0.2, 0.45, 0.95)],
	["Verde", "Verde", Color(0.25, 0.72, 0.28)],
	["Amarillo", "Amarilla", Color(0.95, 0.78, 0.15)],
	["Morado", "Morada", Color(0.58, 0.3, 0.85)],
	["Naranja", "Naranja", Color(0.97, 0.52, 0.12)],
	["Celeste", "Celeste", Color(0.2, 0.8, 0.85)],
	["Rosa", "Rosa", Color(0.95, 0.4, 0.7)],
]
## Tribus (por ahora una sola; las demás tendrán otro estilo de tropas).
const TRIBES := {
	"reino": {"nombre": "Reino", "descripcion": "Caballeros, jinetes y arqueros de armadura."},
}
## Tamaños de mapa: radio en casillas y cuántos jugadores caben como máximo.
const MAP_SIZES := {
	"pequeno": {"nombre": "Pequeño", "radio": 5, "max": 3},
	"mediano": {"nombre": "Mediano", "radio": 7, "max": 5},
	"grande": {"nombre": "Grande", "radio": 9, "max": 8},
	"enorme": {"nombre": "Enorme", "radio": 11, "max": 8},
}
const SIZE_ORDER := ["pequeno", "mediano", "grande", "enorme"]

var enemies := 1
var map_size := "pequeno"
var color_index := 0
var tribe := "reino"
var fog := true


func player_count() -> int:
	return enemies + 1


## El tamaño elegido o, si no caben todos, el más chico en el que sí caben.
func effective_size() -> String:
	var start := SIZE_ORDER.find(map_size)
	for i in range(maxi(start, 0), SIZE_ORDER.size()):
		if int(MAP_SIZES[SIZE_ORDER[i]]["max"]) >= player_count():
			return SIZE_ORDER[i]
	return SIZE_ORDER[-1]


func radius() -> int:
	return int(MAP_SIZES[effective_size()]["radio"])


## Lista de jugadores: [nombre, adjetivo, color, es_bot, tribu]. El humano va primero.
func players() -> Array:
	var out := []
	var c: Array = COLORS[color_index]
	out.append([c[0], c[1], c[2], false, tribe])
	var i := 0
	while out.size() < player_count():
		if i != color_index:
			var b: Array = COLORS[i]
			out.append([b[0], b[1], b[2], true, "reino"])
		i += 1
	return out


func save() -> void:
	var f := ConfigFile.new()
	f.set_value("partida", "enemigos", enemies)
	f.set_value("partida", "mapa", map_size)
	f.set_value("partida", "color", color_index)
	f.set_value("partida", "tribu", tribe)
	f.set_value("partida", "niebla", fog)
	f.save("user://partida.cfg")


static func load_saved() -> MatchConfig:
	var m := MatchConfig.new()
	var f := ConfigFile.new()
	if f.load("user://partida.cfg") == OK:
		m.enemies = clampi(int(f.get_value("partida", "enemigos", 1)), 1, 7)
		m.map_size = str(f.get_value("partida", "mapa", "pequeno"))
		if not MAP_SIZES.has(m.map_size):
			m.map_size = "pequeno"
		m.color_index = clampi(int(f.get_value("partida", "color", 0)), 0, COLORS.size() - 1)
		m.tribe = str(f.get_value("partida", "tribu", "reino"))
		m.fog = bool(f.get_value("partida", "niebla", true))
	return m
