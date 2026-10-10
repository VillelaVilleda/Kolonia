class_name UnitTypes
extends RefCounted
## Estadísticas de cada tipo de tropa. Todas las tribus comparten estos números;
## solo cambia el aspecto visual.
##
## "requiere": mejora del árbol de investigación necesaria para entrenarla
## ("heroe" = no se entrena, se invoca).

const DATA := {
	"caballero": {
		"icono": "espada", "nombre": "Caballero", "sigla": "C",
		"vida": 10, "ataque": 3, "defensa": 2, "movimiento": 1, "alcance": 1,
		"costo": 2, "requiere": "espada",
	},
	"escudero": {
		"icono": "escudo", "nombre": "Caballero con escudo", "sigla": "E",
		"vida": 12, "ataque": 2, "defensa": 4, "movimiento": 1, "alcance": 1,
		"costo": 4, "requiere": "escudo",
	},
	"jinete": {
		"icono": "caballo", "nombre": "Jinete", "sigla": "J",
		"vida": 10, "ataque": 2, "defensa": 1, "movimiento": 2, "alcance": 1,
		"costo": 3, "requiere": "caballos",
	},
	"jinete_lancero": {
		"icono": "lanza", "nombre": "Jinete lancero", "sigla": "L",
		"vida": 12, "ataque": 4, "defensa": 2, "movimiento": 2, "alcance": 1,
		"costo": 5, "requiere": "lanza",
	},
	"arquero": {
		"icono": "arco", "nombre": "Arquero", "sigla": "A",
		"vida": 8, "ataque": 2, "defensa": 1, "movimiento": 1, "alcance": 2,
		"costo": 3, "requiere": "arco",
	},
	"catapulta": {
		"icono": "catapulta", "nombre": "Catapulta", "sigla": "K",
		"vida": 8, "ataque": 4, "defensa": 1, "movimiento": 1, "alcance": 3,
		"costo": 6, "requiere": "ingenieria",
	},
	## Débil en tierra; en el agua ataca a distancia, defiende más y navega más rápido.
	## "en_agua" reemplaza esas estadísticas mientras está sobre el agua.
	"capitan": {
		"icono": "timon", "nombre": "Capitán de barco", "sigla": "B",
		"vida": 10, "ataque": 1, "defensa": 1, "movimiento": 1, "alcance": 1,
		"costo": 4, "requiere": "capitan",
		"en_agua": {"ataque": 3, "defensa": 3, "movimiento": 2, "alcance": 2},
	},
	# --- Héroes de la tribu roja (se invocan al subir una ciudad a nivel 3, 5, 7...) ---
	"super_caballero": {
		"icono": "corona", "nombre": "Súper caballero", "sigla": "SC", "heroe": true,
		"vida": 20, "ataque": 5, "defensa": 3, "movimiento": 2, "alcance": 1,
		"costo": 0, "requiere": "heroe", "habilidades": ["embestida"],
	},
	"sacerdote": {
		"icono": "baston", "nombre": "Sacerdote", "sigla": "S", "heroe": true,
		"vida": 14, "ataque": 2, "defensa": 2, "movimiento": 1, "alcance": 2,
		"costo": 0, "requiere": "heroe", "habilidades": ["curacion", "muralla"],
	},
}

## Habilidades de héroe. "espera" = turnos hasta poder usarla otra vez.
const ABILITIES := {
	"embestida": {
		"icono": "rayo", "nombre": "Embestida", "espera": 3, "objetivo": "direccion", "distancia": 3,
		"descripcion": "Avanza en línea recta hasta 3 casillas golpeando a todo enemigo en su camino",
	},
	"curacion": {
		"icono": "corazon", "nombre": "Curación", "espera": 2, "objetivo": "ninguno", "radio": 3, "cantidad": 4,
		"descripcion": "Cura 4 de vida a tus tropas en un radio de 3 casillas",
	},
	"muralla": {
		"icono": "fuego", "nombre": "Muralla de llamas", "espera": 2, "objetivo": "casilla", "distancia": 3,
		"duracion": 2, "dano": 3,
		"descripcion": "Llamas en 3 casillas durante 2 turnos: los enemigos no pueden entrar y se queman",
	},
}

const HEROES: Array[String] = ["super_caballero", "sacerdote"]


static func is_hero(type: String) -> bool:
	return DATA[type].get("heroe", false)
