class_name TroopModel
extends RefCounted
## Prepara el modelo 3D de una tropa: le pone las armas en las manos y las animaciones
## (todas las tropas usan el esqueleto "Rig_Medium" de KayKit, así que comparten animaciones).

const ANIM_FILES := {
	"general": "res://assets/animaciones/Rig_Medium_General.glb",
	"mov": "res://assets/animaciones/Rig_Medium_MovementBasic.glb",
	"kol": "res://assets/animaciones/Kolonia_Ataques.glb",
}
const LOOPING := ["Idle_A", "Idle_B", "Walking_A", "Walking_B", "Walking_C", "Running_A", "Running_B", "Montado", "Galope"]

## Armas que lleva cada tropa: [archivo en assets/tropas/armas, hueso, (giro en grados)]
const WEAPONS := {
	"caballero": [["espada", "handslot.r"]],
	"escudero": [["espada", "handslot.r"], ["escudo_puas", "handslot.l"]],
	"arquero": [["arco", "handslot.l", Vector3(0, 0, 180)]],
	"jinete": [["espada", "handslot.r"]],
	"jinete_lancero": [["lanza", "handslot.r"]],
	"capitan": [["sable", "handslot.r"], ["garfio", "handslot.l"]],
	"catapulta": [],
	"super_caballero": [["espadon", "handslot.r"]],
	"sacerdote": [["baculo", "handslot.r"]],
}
## Animación de reposo (si no está, "general/Idle_A").
const IDLE := {
	"jinete": "Montado",
	"jinete_lancero": "Montado",
}

static var _libs := {}
static var _weapons := {}


static func _libraries() -> Dictionary:
	if _libs.is_empty():
		for key in ANIM_FILES:
			var scene: Node = (load(ANIM_FILES[key]) as PackedScene).instantiate()
			var ap := scene.find_child("AnimationPlayer", true, false) as AnimationPlayer
			if ap:
				var lib := ap.get_animation_library("")
				for anim_name in lib.get_animation_list():
					if anim_name in LOOPING:
						lib.get_animation(anim_name).loop_mode = Animation.LOOP_LINEAR
				_libs[key] = lib
			scene.free()
	return _libs


static func setup(model: Node3D, type: String) -> void:
	var skel := model.find_child("Skeleton3D", true, false) as Skeleton3D
	if skel == null:
		return
	for w in WEAPONS.get(type, []):
		var att := BoneAttachment3D.new()
		att.bone_name = w[1]
		skel.add_child(att)
		if not _weapons.has(w[0]):
			_weapons[w[0]] = load("res://assets/tropas/armas/%s.glb" % w[0])
		var weapon: Node3D = (_weapons[w[0]] as PackedScene).instantiate()
		if w.size() > 2:
			weapon.rotation_degrees = w[2]
		att.add_child(weapon)
	var ap := model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if ap == null:
		ap = AnimationPlayer.new()
		ap.name = "AnimationPlayer"
		model.add_child(ap)
	else:
		var own := ap.get_animation_library("")
		for anim_name in own.get_animation_list():
			if anim_name in LOOPING:
				own.get_animation(anim_name).loop_mode = Animation.LOOP_LINEAR
	var libs := _libraries()
	for key in libs:
		if not ap.has_animation_library(key):
			ap.add_animation_library(key, libs[key])
	play_idle(model, type)


static func play_idle(model: Node3D, type: String) -> void:
	var ap := model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if ap == null:
		return
	var idle: String = IDLE.get(type, "general/Idle_A")
	if ap.has_animation(idle):
		ap.play(idle)
		# Que no se muevan todas al mismo tiempo
		ap.seek(randf() * ap.current_animation_length, true)


# --- Animaciones de acción --------------------------------------------------------------

const MOUNTED := ["jinete", "jinete_lancero"]
## Ataque de cada tropa y el momento (segundos) en que el golpe "pega".
const ATTACK := {
	"caballero": "kol/Espadazo", "escudero": "kol/Escudazo", "arquero": "kol/Disparo_Arco",
	"capitan": "kol/Espadazo", "super_caballero": "kol/Espadon", "sacerdote": "kol/Hechizo",
	"jinete": "Ataque_Montado", "jinete_lancero": "Ataque_Montado", "catapulta": "Disparo",
}
const HIT_TIME := {
	"kol/Espadazo": 0.43, "kol/Escudazo": 0.37, "kol/Disparo_Arco": 0.62, "kol/Espadon": 0.47,
	"kol/Hechizo": 0.53, "Ataque_Montado": 0.47, "Disparo": 0.45,
}
## Tropas que disparan algo (flecha, piedra, magia).
const PROJECTILE := {"arquero": "flecha", "catapulta": "piedra", "sacerdote": "magia"}


static func player(model: Node) -> AnimationPlayer:
	return model.find_child("AnimationPlayer", true, false) as AnimationPlayer


static func walk_anim(type: String, fast := false) -> String:
	if type in MOUNTED:
		return "Galope"
	return "mov/Running_A" if fast else "mov/Walking_A"


static func hurt_anim(type: String) -> String:
	return "Golpe_Montado" if type in MOUNTED else "general/Hit_A"


static func death_anim(type: String) -> String:
	if type in MOUNTED or type == "catapulta":
		return ""
	return "general/Death_A"


## Reproduce una animación; si back_to_idle, al terminar vuelve al reposo.
static func play(model: Node, anim_name: String, type: String, back_to_idle := true, speed := 1.0) -> float:
	var ap := player(model)
	if ap == null or not ap.has_animation(anim_name):
		return 0.0
	ap.play(anim_name, 0.12, speed)
	if back_to_idle:
		var idle: String = IDLE.get(type, "general/Idle_A")
		if ap.has_animation(idle) and ap.get_animation(anim_name).loop_mode == Animation.LOOP_NONE:
			ap.queue(idle)
	return ap.get_animation(anim_name).length / speed


static func loop(model: Node, anim_name: String, speed := 1.0) -> void:
	var ap := player(model)
	if ap and ap.has_animation(anim_name):
		ap.clear_queue()
		ap.play(anim_name, 0.15, speed)
