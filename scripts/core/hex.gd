class_name Hex
extends RefCounted
## Utilidades para coordenadas hexagonales "axiales" (q, r) con hexágonos de
## punta plana. Guía de referencia: https://www.redblobgames.com/grids/hexagons/

## Distancia del centro de un hexágono a una de sus esquinas, en unidades 3D.
const SIZE := 1.0

## Las 6 direcciones vecinas en coordenadas axiales.
const DIRS: Array[Vector2i] = [
	Vector2i(1, 0), Vector2i(1, -1), Vector2i(0, -1),
	Vector2i(-1, 0), Vector2i(-1, 1), Vector2i(0, 1),
]


static func neighbors(h: Vector2i) -> Array[Vector2i]:
	var result: Array[Vector2i] = []
	for d in DIRS:
		result.append(h + d)
	return result


@warning_ignore("integer_division")
static func distance(a: Vector2i, b: Vector2i) -> int:
	var d := a - b
	return (absi(d.x) + absi(d.y) + absi(d.x + d.y)) / 2


## Centro del hexágono en el mundo 3D (sobre el plano XZ, y = 0).
static func to_world(h: Vector2i) -> Vector3:
	var x := SIZE * 1.5 * h.x
	var z := SIZE * sqrt(3.0) * (h.y + h.x / 2.0)
	return Vector3(x, 0.0, z)


## Hexágono que contiene un punto del mundo 3D.
static func from_world(p: Vector3) -> Vector2i:
	var q := (2.0 / 3.0 * p.x) / SIZE
	var r := (-1.0 / 3.0 * p.x + sqrt(3.0) / 3.0 * p.z) / SIZE
	return round_axial(q, r)


static func round_axial(q: float, r: float) -> Vector2i:
	var s := -q - r
	var rq := roundf(q)
	var rr := roundf(r)
	var rs := roundf(s)
	var dq := absf(rq - q)
	var dr := absf(rr - r)
	var ds := absf(rs - s)
	if dq > dr and dq > ds:
		rq = -rr - rs
	elif dr > ds:
		rr = -rq - rs
	return Vector2i(int(rq), int(rr))


## Todos los hexágonos a una distancia <= radius del centro.
static func area(center: Vector2i, radius: int) -> Array[Vector2i]:
	var result: Array[Vector2i] = []
	for q in range(-radius, radius + 1):
		for r in range(maxi(-radius, -q - radius), mini(radius, -q + radius) + 1):
			result.append(center + Vector2i(q, r))
	return result
