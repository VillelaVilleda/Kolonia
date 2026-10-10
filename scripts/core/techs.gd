class_name Techs
extends RefCounted
## Árbol de investigación. Cada mejora se compra con oro una sola vez por jugador
## y puede requerir otra antes. Para agregar una nueva basta con añadirla aquí
## (y programar su efecto donde corresponda).

const BRANCHES: Array[String] = ["Ejército", "Exploración", "Construcciones"]

## Mejoras con las que empieza cada jugador.
const STARTING: Array[String] = ["espada"]

const DATA := {
	# --- Ejército ---
	"espada": {
		"icono": "espada", "nivel": 1, "nombre": "Espada", "rama": "Ejército", "costo": 0, "requiere": [],
		"descripcion": "Caballero",
	},
	"escudo": {
		"icono": "escudo", "nivel": 1, "nombre": "Escudo", "rama": "Ejército", "costo": 6, "requiere": ["espada"],
		"descripcion": "Caballero con escudo",
	},
	"arco": {
		"icono": "arco", "nivel": 1, "nombre": "Arco y flecha", "rama": "Ejército", "costo": 4, "requiere": [],
		"descripcion": "Arquero",
	},
	"ingenieria": {
		"icono": "catapulta", "nivel": 1, "nombre": "Ingeniería", "rama": "Ejército", "costo": 10, "requiere": ["arco"],
		"descripcion": "Catapulta",
	},
	"caballos": {
		"icono": "caballo", "nivel": 1, "nombre": "Caballos", "rama": "Ejército", "costo": 4, "requiere": [],
		"descripcion": "Jinete",
	},
	"lanza": {
		"icono": "lanza", "nivel": 1, "nombre": "Lanza", "rama": "Ejército", "costo": 7, "requiere": ["caballos"],
		"descripcion": "Jinete lancero",
	},
	# --- Exploración ---
	"exploracion": {
		"icono": "montana", "nivel": 1, "nombre": "Exploración", "rama": "Exploración", "costo": 5, "requiere": [],
		"descripcion": "Subir montañas (+1 alcance a tropas de distancia)",
	},
	"caminos": {
		"icono": "camino", "nivel": 1, "nombre": "Caminos", "rama": "Exploración", "costo": 3, "requiere": [],
		"descripcion": "Construir caminos",
	},
	"muelle": {
		"icono": "ancla", "nivel": 1, "nombre": "Muelle", "rama": "Exploración", "costo": 5, "requiere": [],
		"descripcion": "Construir puertos",
	},
	"navegacion": {
		"icono": "barco", "nivel": 1, "nombre": "Navegación", "rama": "Exploración", "costo": 6, "requiere": ["muelle"],
		"descripcion": "Las tropas suben a un barco en un puerto propio y navegan",
	},
	"capitan": {
		"icono": "timon", "nivel": 1, "nombre": "Capitán", "rama": "Exploración", "costo": 6, "requiere": ["navegacion"],
		"descripcion": "Capitán de barco: en el agua navega en su galeón y es más fuerte",
	},
	# --- Construcciones ---
	"cultivos": {
		"icono": "trigo", "nivel": 1, "nombre": "Cultivos", "rama": "Construcciones", "costo": 3, "requiere": [],
		"descripcion": "Granjas (+1 comida por turno)",
	},
	"cultivos2": {
		"icono": "trigo", "nivel": 2, "nombre": "Cultivos nv.2", "rama": "Construcciones", "costo": 7, "requiere": ["cultivos"],
		"descripcion": "Mejorar granjas (+1 comida más)",
	},
	"aserradero": {
		"icono": "hacha", "nivel": 1, "nombre": "Aserradero", "rama": "Construcciones", "costo": 3, "requiere": [],
		"descripcion": "Aserraderos (+1 madera por turno)",
	},
	"aserradero2": {
		"icono": "hacha", "nivel": 2, "nombre": "Aserradero nv.2", "rama": "Construcciones", "costo": 7, "requiere": ["aserradero"],
		"descripcion": "Mejorar aserraderos (+1 madera más)",
	},
}


## Mejoras de una rama que no requieren otra de la misma rama (inicio de cada cadena).
static func roots(branch: String) -> Array[String]:
	var result: Array[String] = []
	for id in DATA:
		if DATA[id]["rama"] == branch and DATA[id]["requiere"].is_empty():
			result.append(id)
	return result


## Mejoras que requieren directamente a esta.
static func children(tech: String) -> Array[String]:
	var result: Array[String] = []
	for id in DATA:
		if tech in DATA[id]["requiere"]:
			result.append(id)
	return result
