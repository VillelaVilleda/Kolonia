# Animaciones propias de Kolonia para el esqueleto "Rig_Medium" de KayKit.
# Cada animación se arma con "poses clave": en cada cuadro se parte de una pose base
# (por ejemplo el reposo Idle_A de KayKit) y se giran algunos huesos.
# Los giros se dan en el espacio del esqueleto: personaje mirando a -Y, Z arriba.
#   X negativo = levantar hacia adelante (brazo) / X positivo = inclinar el tronco adelante
#   Z positivo = girar el tronco hacia su izquierda (+X)
import bpy, math, os
from mathutils import Matrix, Vector

ROOT = os.environ.get("KOLONIA_ROOT", r"C:\Personal\Kolonia")
ANIM_DIR = os.environ.get("KOLONIA_ANIMS", os.path.join(ROOT, "assets", "animaciones"))


def bone_order(arm):
    order = []

    def walk(b):
        order.append(b.name)
        for c in b.children:
            walk(c)
    for b in arm.data.bones:
        if b.parent is None:
            walk(b)
    return order


def capture_pose(arm, action=None, frame=1):
    """Guarda la pose (matrix_basis de cada hueso) de una acción en un cuadro."""
    bpy.context.view_layer.objects.active = arm
    if action is not None:
        arm.animation_data_create()
        arm.animation_data.action = action
        # Blender 4.4+: la acción necesita su "slot" para afectar a otro objeto
        slots = getattr(action, "slots", None)
        if slots and hasattr(arm.animation_data, "action_slot"):
            arm.animation_data.action_slot = slots[0]
    bpy.context.scene.frame_set(frame)
    pose = {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}
    if action is not None:
        arm.animation_data.action = None
    return pose


def _apply(arm, base, rots, locs, order):
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.matrix_basis = base[pb.name].copy() if base and pb.name in base else Matrix()
    bpy.context.view_layer.update()
    for bn in order:
        pb = arm.pose.bones[bn]
        changed = False
        m = pb.matrix.copy()
        if bn in locs:
            m = Matrix.Translation(Vector(locs[bn])) @ m
            changed = True
        if bn in rots:
            r = Matrix()
            for axis, deg in rots[bn]:
                r = Matrix.Rotation(math.radians(deg), 4, axis) @ r
            p = m.to_translation()
            m = Matrix.Translation(p) @ r @ Matrix.Translation(-p) @ m
            changed = True
        if changed:
            pb.matrix = m
            bpy.context.view_layer.update()


def keyed_action(arm, name, keys, base=None, bones=None):
    """keys: lista de (cuadro, {hueso: [(eje, grados), ...]}, {hueso: (dx, dy, dz)}).
    bones: si se da, solo se guardan esos huesos (los demás quedan libres)."""
    bpy.context.view_layer.objects.active = arm
    if bpy.context.object.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data_create()
    arm.animation_data.action = act
    order = bone_order(arm)
    prev = {}
    for k in keys:
        frame, rots = k[0], k[1]
        locs = k[2] if len(k) > 2 else {}
        _apply(arm, base, rots, locs, order)
        for pb in arm.pose.bones:
            if bones is not None and pb.name not in bones:
                continue
            # Que el cuaternión no cambie de signo entre cuadros (si no, gira "por el lado largo")
            q = pb.rotation_quaternion.copy()
            if pb.name in prev and prev[pb.name].dot(q) < 0:
                q.negate()
                pb.rotation_quaternion = q
            prev[pb.name] = q.copy()
            pb.keyframe_insert("rotation_quaternion", frame=frame)
            pb.keyframe_insert("location", frame=frame)
    arm.animation_data.action = None
    bpy.ops.object.mode_set(mode="OBJECT")
    return act


def mirror(rots):
    return {b: [(a, -d if a in ("Y", "Z") else d) for a, d in v] for b, v in rots.items()}


# ---------------------------------------------------------------------------------------
# Ataques de infantería (librería "kol" en Godot)

def espadazo(arm, base):
    """Tajo horizontal con la espada en la mano derecha (se lee mejor con cabezas grandes)."""
    wind = {"upperarm.r": [("Y", 80), ("Z", -55)], "lowerarm.r": [("Z", -35)],
            "chest": [("Z", -30)], "spine": [("Z", -10)], "head": [("Z", 20)],
            "upperarm.l": [("Y", -30), ("Z", -20)]}
    hit = {"upperarm.r": [("Y", 75), ("Z", 85)], "lowerarm.r": [("Z", 10)],
           "chest": [("Z", 22), ("X", 10)], "spine": [("Z", 10), ("X", 6)], "head": [("Z", -15)],
           "upperarm.l": [("Y", -25), ("Z", 25)],
           "upperleg.r": [("X", 15)], "upperleg.l": [("X", -28)], "lowerleg.l": [("X", 18)]}
    follow = {"upperarm.r": [("Y", 70), ("Z", 125)], "lowerarm.r": [("Z", 20)],
              "chest": [("Z", 35), ("X", 12)], "spine": [("Z", 12), ("X", 6)], "head": [("Z", -25)],
              "upperarm.l": [("Y", -25), ("Z", 35)],
              "upperleg.r": [("X", 15)], "upperleg.l": [("X", -28)], "lowerleg.l": [("X", 18)]}
    return keyed_action(arm, "Espadazo", [
        (1, {}),
        (9, wind, {"hips": (0, 0.05, 0)}),
        (13, hit, {"hips": (0, -0.12, -0.05)}),
        (17, follow, {"hips": (0, -0.12, -0.05)}),
        (30, {}),
    ], base)


def disparo_arco(arm, base):
    aim = {"chest": [("Z", -50)], "spine": [("Z", -15)], "head": [("Z", 55)],
           "upperarm.l": [("X", -85), ("Z", 50)], "lowerarm.l": [("X", 0)],
           "upperarm.r": [("X", -80), ("Z", 30)], "lowerarm.r": [("Z", 110)]}
    draw = {"chest": [("Z", -55)], "spine": [("Z", -15)], "head": [("Z", 60)],
            "upperarm.l": [("X", -88), ("Z", 55)],
            "upperarm.r": [("X", -82), ("Z", 15)], "lowerarm.r": [("Z", 140)]}
    shot = {"chest": [("Z", -55)], "spine": [("Z", -15)], "head": [("Z", 60)],
            "upperarm.l": [("X", -88), ("Z", 55)],
            "upperarm.r": [("X", -70), ("Z", -20)], "lowerarm.r": [("Z", 40)]}
    return keyed_action(arm, "Disparo_Arco", [
        (1, {}),
        (8, aim),
        (16, draw),
        (19, shot),
        (26, shot),
        (36, {}),
    ], base)


def hechizo(arm, base):
    up = {"upperarm.r": [("X", -165)], "lowerarm.r": [("X", -10)], "chest": [("X", -10)],
          "spine": [("X", -6)], "head": [("X", -15)], "upperarm.l": [("X", -40), ("Y", 30)]}
    cast = {"upperarm.r": [("X", -85)], "lowerarm.r": [("X", -5)], "chest": [("X", 15)],
            "spine": [("X", 8)], "upperarm.l": [("X", -60), ("Y", 20)], "upperleg.l": [("X", -20)]}
    return keyed_action(arm, "Hechizo", [
        (1, {}),
        (10, up, {"hips": (0, 0.03, 0.04)}),
        (16, cast, {"hips": (0, -0.08, -0.03)}),
        (24, cast, {"hips": (0, -0.08, -0.03)}),
        (34, {}),
    ], base)


def escudazo(arm, base):
    """Golpe con el escudo (mano izquierda) y luego la espada."""
    push = {"upperarm.l": [("X", -80), ("Z", -20)], "lowerarm.l": [("X", -20)],
            "chest": [("Z", -25), ("X", 12)], "spine": [("X", 8)],
            "upperleg.l": [("X", -30)], "lowerleg.l": [("X", 20)]}
    return keyed_action(arm, "Escudazo", [
        (1, {}),
        (6, {"chest": [("Z", 15)], "upperarm.l": [("X", -30)]}, {"hips": (0, 0.05, 0)}),
        (11, push, {"hips": (0, -0.14, -0.04)}),
        (16, push, {"hips": (0, -0.14, -0.04)}),
        (28, {}),
    ], base)


def espadon(arm, base):
    """Golpe de arriba hacia abajo con la espada grande (héroe)."""
    up = {"upperarm.r": [("X", -170)], "lowerarm.r": [("X", -40)],
          "upperarm.l": [("X", -160), ("Y", -25)], "lowerarm.l": [("X", -40)],
          "chest": [("X", -14)], "spine": [("X", -8)], "head": [("X", -10)]}
    down = {"upperarm.r": [("X", -50)], "lowerarm.r": [("X", -10)],
            "upperarm.l": [("X", -50), ("Y", -25)], "lowerarm.l": [("X", -10)],
            "chest": [("X", 22)], "spine": [("X", 12)],
            "upperleg.r": [("X", 20)], "upperleg.l": [("X", -30)], "lowerleg.l": [("X", 20)]}
    return keyed_action(arm, "Espadon", [
        (1, {}),
        (10, up, {"hips": (0, 0.06, 0.03)}),
        (14, down, {"hips": (0, -0.12, -0.12)}),
        (20, down, {"hips": (0, -0.12, -0.12)}),
        (32, {}),
    ], base)


def festejo(arm, base):
    """Brazos arriba (al conquistar o subir de nivel)."""
    up = {"upperarm.r": [("X", -160), ("Y", 20)], "upperarm.l": [("X", -160), ("Y", -20)],
          "head": [("X", -15)]}
    return keyed_action(arm, "Festejo", [
        (1, {}),
        (8, up, {"hips": (0, 0, 0.25)}),
        (14, up, {"hips": (0, 0, 0.0)}),
        (20, up, {"hips": (0, 0, 0.2)}),
        (30, {}),
    ], base)


def export_library(path_in, path_out):
    """Toma el esqueleto de Rig_Medium_General.glb, arma las animaciones propias y las
    exporta en un .glb aparte (Godot las carga como librería "kol")."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path_in)
    bpy.context.scene.render.fps = 30
    arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
    base = capture_pose(arm, bpy.data.actions["Idle_A"], 1)
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)
    for f in (espadazo, disparo_arco, hechizo, escudazo, espadon, festejo):
        f(arm, base)
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=path_out, export_format="GLB", use_selection=True,
                              export_animations=True, export_animation_mode="ACTIONS",
                              export_force_sampling=True, export_frame_range=False)
    return path_out


def todas():
    src = os.path.join(ANIM_DIR, "Rig_Medium_General.glb")
    return export_library(src, os.path.join(ANIM_DIR, "Kolonia_Ataques.glb"))
