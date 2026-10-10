# Tropas de Kolonia (tribu base) sobre personajes KayKit. Ver kk_lib.py.
# Uso en Blender (pestaña Scripting) o con Python + bpy:
#   import sys; sys.path.append(r"C:\Personal\Kolonia\tools\blender")
#   import kk_tropas; kk_tropas.todas()
# Las armas en la mano se ponen en Godot (scripts/view/troop_model.gd).
#
# Para una tribu nueva: copiar estas funciones y cambiar las piezas propias
# (cascos, plumas, capas, caballos) y/o el personaje KayKit de base.
import math, os
import kolonia_lib as K
import kk_lib as L
from kolonia_lib import R, sphere, cyl, box, torus, tube, mat

KNIGHT = ["ArmLeft", "ArmRight", "Body", "Cape", "Head", "Helmet", "LegLeft", "LegRight"]
BODY = ["ArmLeft", "ArmRight", "Body", "Head", "LegLeft", "LegRight"]


# ---------------------------------------------------------------------------------------
# Piezas propias

def plume(top, size=1.0):
    """Penacho de plumas del color de la tribu (hacia atrás)."""
    x, y, z = top
    for i, (dy, dz, s) in enumerate([(0, 0, 1.0), (0.1, 0.1, 0.92), (0.22, 0.14, 0.8), (0.34, 0.1, 0.66)]):
        sphere(0.14 * size * s, (x, y + dy * size, z + dz * size), K.TRIBU(),
               (0.5, 1.6, 1.0), rot=(R(-25 - 14 * i), 0, 0), sub=1)
    cyl(0.06 * size, 0.08 * size, 0.1 * size, (x, y, z - 0.05 * size), K.GOLD())


def tabard(top=0.62, bottom=0.2, width=0.46, y=-0.36):
    """Faldón con el color de la tribu y borde dorado (va en la cadera)."""
    h = top - bottom
    box((width, 0.05, h), (0, y, bottom + h / 2), K.TRIBU(), bevel=0.02)
    box((width + 0.02, 0.06, 0.05), (0, y - 0.005, bottom + 0.02), K.GOLD(), bevel=0.01)


def on(bone, fn, *a, **kw):
    """Arma piezas con fn y las pega al hueso."""
    before = K.mark()
    fn(*a, **kw)
    objs = L.since(before)
    L.on_bone(objs, bone)
    return objs


class Part:
    """with Part("hueso"): ... -> las piezas creadas adentro se pegan a ese hueso."""
    def __init__(self, bone, world=True):
        self.bone, self.world = bone, world

    def __enter__(self):
        self.before = K.mark()

    def __exit__(self, *a):
        L.on_bone(L.since(self.before), self.bone, world=self.world)


# Huesos del caballo (posición en el mundo, con el caballo en el suelo mirando a -Y)
HORSE_BONES = [
    ("caballo_raiz", (0, 0.55, 0.0), (0, 0.55, 0.3), None),
    ("caballo", (0, 0.1, 1.2), (0, -0.3, 1.2), "caballo_raiz"),
    ("pata_dd", (-0.25, -0.42, 1.0), (-0.25, -0.42, 0.1), "caballo"),
    ("pata_di", (0.25, -0.42, 1.0), (0.25, -0.42, 0.1), "caballo"),
    ("pata_td", (-0.25, 0.55, 1.0), (-0.25, 0.55, 0.1), "caballo"),
    ("pata_ti", (0.25, 0.55, 1.0), (0.25, 0.55, 0.1), "caballo"),
    ("cuello", (0, -0.5, 1.4), (0, -0.85, 1.95), "caballo"),
    ("cabeza_c", (0, -0.85, 1.95), (0, -1.3, 1.9), "cuello"),
    ("cola", (0, 0.88, 1.38), (0, 1.05, 0.8), "caballo"),
]
LEGS = {"pata_dd": (-1, -0.42, False), "pata_di": (1, -0.42, False),
        "pata_td": (-1, 0.55, True), "pata_ti": (1, 0.55, True)}


def horse(coat, mane, muzzle, armor=False, blaze=True):
    """Caballo estilo chibi (cabeza grande), mirando hacia -Y, armado por partes que se
    pegan a los huesos del caballo. Devuelve la altura de la silla."""
    BLACK, LEATHER, WHITE = K.BLACK, K.LEATHER_D, K.WHITE
    with Part("caballo"):
        sphere(0.5, (0, -0.32, 1.22), coat, (0.82, 0.95, 0.88), sub=1)
        sphere(0.5, (0, 0.1, 1.16), coat, (0.76, 1.25, 0.78), sub=1)
        sphere(0.5, (0, 0.5, 1.22), coat, (0.84, 0.9, 0.86), sub=1)
        cyl(0.4, 0.42, 0.1, (0, 0.05, 1.63), K.TRIBU(), v=32, bevel=0.03)                  # silla
        box((0.1, 0.12, 0.14), (0, -0.3, 1.72), K.TRIBU_D(), bevel=0.04)
        box((1.0, 0.8, 0.05), (0, 0.05, 1.56), K.TRIBU_D(), bevel=0.02)                   # manta
        box((1.0, 0.04, 0.06), (0, -0.35, 1.56), K.GOLD(), bevel=0.01)
        box((1.0, 0.04, 0.06), (0, 0.45, 1.56), K.GOLD(), bevel=0.01)
        if armor:
            sphere(0.5, (0, -0.6, 1.25), K.STEEL(), (0.88, 0.55, 0.8), sub=1)              # pechera
            g = cyl(0.47, 0.52, 0.55, (0, 0.2, 1.05), K.TRIBU(), v=32)                    # gualdrapa
            g.scale = (1, 1.75, 1)
            t = torus(0.52, 0.035, (0, 0.2, 0.78), K.GOLD())
            t.scale = (1, 1.75, 1)
            box((0.08, 0.05, 0.4), (0, -0.72, 1.22), K.TRIBU(), bevel=0.01)
            box((0.3, 0.05, 0.08), (0, -0.72, 1.3), K.TRIBU(), bevel=0.01)
    for bone, (sx, y, back) in LEGS.items():
        with Part(bone):
            x = sx * 0.25
            sphere(0.22 if back else 0.19, (x, y + (0.03 if back else 0), 0.98), coat, (0.9, 1.1, 1.3), sub=1)
            cyl(0.15, 0.1, 0.5, (x, y, 0.62), coat, v=16)
            sphere(0.105, (x, y, 0.38), coat)
            cyl(0.1, 0.11, 0.24, (x, y, 0.26), coat, v=16)
            sphere(0.12, (x, y - 0.01, 0.17), muzzle if blaze else coat, (1, 1, 0.8))
            cyl(0.14, 0.16, 0.15, (x, y - 0.02, 0.075), BLACK(), v=16, bevel=0.03)
    with Part("cuello"):
        cyl(0.3, 0.22, 0.75, (0, -0.68, 1.62), coat, rot=(R(-35), 0, 0), v=24, sub=1)
        for k in range(5):
            t = k / 4
            sphere(0.13 - 0.02 * t, (0, -0.86 + 0.42 * t, 2.2 - 0.62 * t), mane, (0.75, 1.3, 1.0),
                   rot=(R(-40), 0, 0), sub=1)
    with Part("cabeza_c"):
        sphere(0.3, (0, -0.95, 2.02), coat, (0.86, 1.05, 0.95), sub=1)
        sphere(0.24, (0, -1.25, 1.88), muzzle, (0.9, 1.15, 0.82), rot=(R(20), 0, 0), sub=1)
        if blaze:
            box((0.1, 0.05, 0.42), (0, -1.16, 2.04), WHITE(), rot=(R(-58), 0, 0), bevel=0.04)
        for sx in (-1, 1):
            sphere(0.085, (sx * 0.22, -1.08, 2.08), WHITE(), (0.7, 1, 1))
            sphere(0.06, (sx * 0.25, -1.11, 2.08), BLACK(), (0.7, 1, 1))
            sphere(0.02, (sx * 0.27, -1.15, 2.11), WHITE())
            cyl(0.075, 0.0, 0.24, (sx * 0.15, -0.86, 2.34), coat, rot=(R(-8), R(sx * 18), 0), v=10)
            sphere(0.04, (sx * 0.1, -1.47, 1.86), BLACK(), (1, 0.6, 1.2))
            box((0.03, 0.04, 0.3), (sx * 0.24, -1.2, 1.95), LEATHER(), rot=(R(30), 0, 0), bevel=0.01)
            sphere(0.04, (sx * 0.25, -1.3, 1.82), K.GOLD())
            tube([(sx * 0.26, -1.3, 1.82), (sx * 0.33, -1.0, 1.72), (sx * 0.3, -0.62, 1.78)], 0.022, LEATHER())
        box((0.5, 0.04, 0.04), (0, -1.13, 2.13), LEATHER(), bevel=0.01)
        sphere(0.12, (0, -0.95, 2.32), mane, (0.9, 1.0, 0.9), rot=(R(30), 0, 0), sub=1)
        if armor:
            sphere(0.26, (0, -1.04, 2.07), K.STEEL(), (0.8, 1.05, 0.7), rot=(R(25), 0, 0), sub=1)
            cyl(0.06, 0.0, 0.2, (0, -1.08, 2.32), K.STEEL(), rot=(R(-30), 0, 0), v=8)
    with Part("cola"):
        for dx, dz in ((0, 0), (-0.06, -0.05), (0.06, -0.05)):
            tube([(dx * 0.5, 0.88, 1.38), (dx, 1.1, 1.15 + dz), (dx * 1.5, 1.08, 0.72 + dz)], 0.085, mane)
    return 1.66


def sit_rots(lance=False):
    return {
        "upperleg.r": [("X", -80), ("Z", -28)],
        "upperleg.l": [("X", -80), ("Z", 28)],
        "lowerleg.r": [("X", 85)],
        "lowerleg.l": [("X", 85)],
        "upperarm.l": [("Y", 72)],
        "upperarm.r": [("Y", -72)],
        "lowerarm.l": [("X", -70)],
        "lowerarm.r": [("X", -110 if lance else -70)],
    }


def cmb(*ds):
    """Junta poses: los giros de cada hueso se aplican en orden."""
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, []) + list(v)
    return out


def rider_actions(lance):
    import kk_anims as A
    arm = L.S["arm"]
    sit = sit_rots(lance)
    # Reposo: el caballo respira, mueve la cabeza y la cola
    A.keyed_action(arm, "Montado", [
        (1, sit),
        (30, cmb(sit, {"cuello": [("X", 7)], "cola": [("Z", 14)], "chest": [("X", 3)]}),
         {"caballo": (0, 0, -0.02)}),
        (60, sit),
    ])
    # Galope (ciclo)
    keys = []
    n = 8
    for k in range(n + 1):
        t = k / n * math.tau
        rots = cmb(sit, {
            "pata_dd": [("X", -38 * math.cos(t))], "pata_di": [("X", -38 * math.cos(t + 0.5))],
            "pata_td": [("X", 34 * math.cos(t + 0.9))], "pata_ti": [("X", 34 * math.cos(t + 1.4))],
            "caballo": [("X", 5 * math.sin(t))], "cuello": [("X", -8 * math.sin(t))],
            "cola": [("X", -20 + 10 * math.sin(t))], "chest": [("X", 10)]})
        keys.append((1 + k * 2, rots, {"caballo": (0, 0, 0.1 * abs(math.sin(t)))}))
    A.keyed_action(arm, "Galope", keys)
    # Golpe recibido
    A.keyed_action(arm, "Golpe_Montado", [
        (1, sit),
        (5, cmb(sit, {"chest": [("X", -18)], "head": [("X", -10)], "caballo": [("X", -6)],
                      "cuello": [("X", -20)]})),
        (16, sit),
    ])
    if lance:
        back = cmb(sit, {"lowerarm.r": [("X", 70)], "upperarm.r": [("X", 40)], "chest": [("Z", -15)]})
        thrust = cmb(sit, {"lowerarm.r": [("X", 80)], "upperarm.r": [("X", 22)], "chest": [("X", 15), ("Z", 10)],
                           "pata_dd": [("X", -40)], "pata_di": [("X", -25)], "cuello": [("X", 12)]})
        A.keyed_action(arm, "Ataque_Montado", [
            (1, sit), (9, back), (14, thrust, {"caballo": (0, -0.3, 0)}),
            (19, thrust, {"caballo": (0, -0.3, 0)}), (32, sit)])
    else:
        rear = cmb(sit, {"caballo_raiz": [("X", -20)], "pata_dd": [("X", -60)], "pata_di": [("X", -45)],
                         "cuello": [("X", -15)], "lowerarm.r": [("X", 40)], "upperarm.r": [("X", -100)],
                         "chest": [("Z", -20)]})
        strike = cmb(sit, {"caballo_raiz": [("X", 4)], "pata_dd": [("X", 15)], "pata_di": [("X", 10)],
                           "lowerarm.r": [("X", 110)], "upperarm.r": [("X", -10)], "chest": [("X", 15), ("Z", 25)]})
        A.keyed_action(arm, "Ataque_Montado", [
            (1, sit), (10, rear), (15, strike), (20, strike), (32, sit)])


# ---------------------------------------------------------------------------------------
# Tropas

def caballero():
    L.reset("Caballero")
    L.load_char("Knight", KNIGHT)
    mn, mx = L.kk_bounds("Helmet")
    on("head", plume, (0, 0.08, mx.z - 0.06), size=1.5)
    on("hips", tabard)
    L.finalize()
    return L.export("caballero")


def escudero():
    L.reset("Escudero")
    L.load_char("Knight", KNIGHT + ["HelmetVisor"])
    L.S["team_extra"] = [(3, 0), (3, 1)]       # la armadura toma el color de la tribu
    mn, mx = L.kk_bounds("Helmet")

    def crest():
        box((0.14, 0.95, 0.38), (0, 0.04, mx.z + 0.04), K.TRIBU(), bevel=0.07)
    on("head", crest)
    for sx, bone in ((1, "upperarm.l"), (-1, "upperarm.r")):
        def pad(sx=sx):
            sphere(0.27, (sx * 0.4, 0, 1.22), K.TRIBU(), (1.05, 1.0, 0.78), sub=1)
            torus(0.24, 0.035, (sx * 0.4, 0, 1.13), K.GOLD())
            for dx in (-0.1, 0.1):
                cyl(0.06, 0.0, 0.2, (sx * 0.4 + dx, 0, 1.42), K.STEEL(), v=8)
        on(bone, pad)
    on("hips", tabard, width=0.5)
    L.finalize()
    return L.export("escudero")


def arquero():
    L.reset("Arquero")
    L.load_char("Rogue_Hooded", BODY + ["Cape"])

    def quiver():
        q = [cyl(0.13, 0.15, 0.75, (0, 0, 0), K.LEATHER(), bevel=0.01),
             torus(0.14, 0.025, (0, 0, 0.3), K.LEATHER_D())]
        for k in range(4):
            a = k * math.tau / 4
            q.append(cyl(0.015, 0.015, 0.4, (math.cos(a) * 0.06, math.sin(a) * 0.06, 0.55), K.WOOD()))
            q.append(cyl(0.05, 0.0, 0.14, (math.cos(a) * 0.06, math.sin(a) * 0.06, 0.78), K.TRIBU(), v=4))
        K._group(q, (0.18, 0.45, 1.0), (R(-15), R(-25), 0))
    on("chest", quiver)
    L.finalize()
    return L.export("arquero")


def _rider(name, visor, coat, mane, muzzle, armor, lance, blaze=True):
    L.reset(name)
    L.load_char("Knight", KNIGHT + (["HelmetVisor"] if visor else []))
    mn, mx = L.kk_bounds("Helmet")
    on("head", plume, (0, 0.08, mx.z - 0.06), size=1.4)
    seat = horse(coat(), mane(), muzzle(), armor=armor, blaze=blaze)
    L.move_rig((0, 0.08, seat - 0.38))
    L.add_bones(HORSE_BONES, reparent={"root": "caballo"})
    rider_actions(lance)
    L.finalize()
    return L.export(name.lower(), animations=True)


def jinete():
    return _rider("Jinete", False, lambda: mat("Caballo", "8a5230", 0.75), lambda: mat("Crin", "3a2416", 0.8),
                  lambda: mat("Hocico", "c08a5c", 0.8), False, False)


def jinete_lancero():
    return _rider("Jinete_lancero", True, lambda: mat("CaballoGris", "4a4440", 0.7), K.BLACK,
                  lambda: mat("HocicoGris", "6e6560", 0.8), True, True, blaze=False)


def capitan():
    L.reset("Capitan")
    L.load_char("Rogue", BODY + ["Cape"])
    mn, mx = L.kk_bounds("Head")

    def hat():
        z = mx.z - 0.3
        cyl(0.95, 0.95, 0.12, (0, 0.05, z), K.BLACK(), v=3, rot=(0, 0, R(-90)), bevel=0.05)  # ala
        torus(0.84, 0.04, (0, 0.05, z + 0.07), K.GOLD(), seg=3, rot=(0, 0, R(-90)))
        sphere(0.6, (0, 0.05, z + 0.05), K.BLACK(), (1, 1, 0.68), sub=1)                    # copa
        sphere(0.1, (0.0, -0.53, z + 0.28), K.WHITE(), (1, 0.5, 1))                         # calavera
        plume((0.4, 0.25, z + 0.38), size=1.4)

    def face():
        sphere(0.16, (0, -0.52, 1.3), K.WHITE(), (1.3, 0.6, 1.0), sub=1)    # barbita
        box((0.36, 0.07, 0.07), (0, -0.58, 1.48), K.WHITE(), bevel=0.03)     # bigote
        sphere(0.11, (-0.21, -0.55, 1.62), K.BLACK(), (1, 0.35, 1))          # parche
    on("head", hat)
    on("head", face)
    on("hips", tabard, top=0.62, bottom=0.12, width=0.62, y=-0.37)
    L.finalize()
    return L.export("capitan")


def catapulta():
    import bpy
    import kk_anims as A
    L.reset("Catapulta")
    L.load_char("Ranger", BODY)
    mn, mx = L.kk_bounds("Head")
    F = 2.0                                   # escala de la catapulta
    before = K.mark()
    WOOD, WOOD_D, STEEL_D = K.WOOD, K.WOOD_D, K.STEEL_D
    for sx in (-1, 1):
        box((0.08, 1.1, 0.1), (sx * 0.35, 0, 0.3), WOOD(), bevel=0.015)
        box((0.08, 0.08, 1.05), (sx * 0.3, -0.05, 0.85), WOOD(), bevel=0.015)
        for y in (-0.38, 0.38):
            cyl(0.17, 0.17, 0.07, (sx * 0.45, y, 0.18), WOOD_D(), rot=(0, R(90), 0), v=24, bevel=0.01)
            cyl(0.06, 0.06, 0.09, (sx * 0.45, y, 0.18), STEEL_D(), rot=(0, R(90), 0))
            torus(0.17, 0.02, (sx * 0.49, y, 0.18), STEEL_D(), rot=(0, R(90), 0))
    for y in (-0.45, 0.45):
        box((0.78, 0.09, 0.09), (0, y, 0.3), WOOD(), bevel=0.015)
    box((0.7, 0.1, 0.12), (0, -0.05, 1.35), WOOD(), bevel=0.015)              # tope
    sphere(0.08, (0, -0.0, 1.35), mat("Cuero2", "6b4224"), (3.5, 1, 1))       # acolchado del tope
    cyl(0.12, 0.12, 0.6, (0, 0.2, 0.42), WOOD_D(), rot=(0, R(90), 0))        # tambor
    for k in range(5):
        torus(0.13, 0.025, (-0.2 + k * 0.1, 0.2, 0.42), mat("Cuerda", "c9a86a"), rot=(0, R(90), 0))
    box((0.7, 0.05, 0.18), (0, -0.5, 0.42), K.TRIBU(), bevel=0.01)
    cyl(0.03, 0.03, 0.35, (0.42, 0.2, 0.42), STEEL_D(), rot=(0, R(90), 0))     # palanca
    box((0.04, 0.04, 0.3), (0.58, 0.2, 0.55), WOOD_D(), bevel=0.01)
    frame = L.since(before)
    L.scale_objs(frame, F)
    L.static(frame)
    # Brazo (se mueve con el hueso "brazo_cat")
    before = K.mark()
    box((0.09, 0.09, 0.78), (0, 0.52, 0.52), WOOD_D(), rot=(R(-73), 0, 0), bevel=0.015)
    sphere(0.17, (0, 0.86, 0.66), WOOD_D(), (1, 1, 0.5))
    sphere(0.14, (0, 0.86, 0.76), mat("Roca", "8c8c8c", 0.9), sub=1)
    torus(0.07, 0.02, (0, 0.24, 0.43), STEEL_D(), rot=(0, R(90), 0))
    arm_objs = L.since(before)
    L.scale_objs(arm_objs, F)
    L.on_bone(arm_objs, "brazo_cat", world=True)

    def cap():
        sphere(0.6, (0, 0.02, mx.z - 0.22), K.LEATHER(), (1.0, 1.0, 0.62), sub=1)
        cyl(0.62, 0.62, 0.08, (0, 0.02, mx.z - 0.3), K.LEATHER_D(), v=32)
        plume((0, 0.3, mx.z + 0.1), size=0.9)
    on("head", cap)
    L.move_rig((1.45, 0.65, 0))
    L.add_bones([("brazo_cat", (0, 0.2 * F, 0.42 * F), (0, 0.86 * F, 0.66 * F), None)])

    # Pose de reposo de KayKit para el operador
    before_objs = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(A.ANIM_DIR, "Rig_Medium_General.glb"))
    idle = bpy.data.actions["Idle_A"]
    arm = L.S["arm"]
    base = A.capture_pose(arm, idle, 1)
    for o in set(bpy.data.objects) - before_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)
    reach = {"chest": [("X", 18), ("Z", -25)], "spine": [("X", 8)],
             "upperarm.r": [("X", -50), ("Z", -30)], "upperarm.l": [("X", -40), ("Z", -20)]}
    pull = {"chest": [("X", -12), ("Z", -20)], "upperarm.r": [("X", 10), ("Z", -20)],
            "upperarm.l": [("X", 5), ("Z", -10)], "head": [("X", -15), ("Z", 30)]}
    A.keyed_action(arm, "Disparo", [
        (1, {}),
        (8, reach, {"hips": (-0.05, 0, -0.06)}),
        (11, cmb(pull, {"brazo_cat": [("X", 0)]}), {"hips": (0, 0.06, 0)}),
        (14, cmb(pull, {"brazo_cat": [("X", 78)]}), {"hips": (0, 0.06, 0)}),
        (22, cmb(pull, {"brazo_cat": [("X", 72)]}), {"hips": (0, 0.06, 0)}),
        (45, {}),
    ], base)
    L.finalize()
    return L.export("catapulta", animations=True)


def super_caballero():
    L.reset("Super_caballero")
    L.load_char("Knight", KNIGHT + ["HelmetVisor"])
    mn, mx = L.kk_bounds("Helmet")

    def crown():
        z = mx.z - 0.1
        cyl(0.36, 0.38, 0.16, (0, 0.02, z), K.GOLD(), v=32, bevel=0.02)
        for k in range(6):
            a = k * math.tau / 6
            cyl(0.07, 0.0, 0.2, (math.cos(a) * 0.33, 0.02 + math.sin(a) * 0.33, z + 0.17), K.GOLD(), v=6)
            sphere(0.035, (math.cos(a) * 0.37, 0.02 + math.sin(a) * 0.37, z), mat("Gema", "e0303a", 0.2))
        plume((0, 0.12, z + 0.12), size=1.7)
    on("head", crown)
    for sx, bone in ((1, "upperarm.l"), (-1, "upperarm.r")):
        def pad(sx=sx):
            sphere(0.25, (sx * 0.4, 0, 1.2), K.STEEL(), (1.05, 1.0, 0.75), sub=1)
            torus(0.22, 0.04, (sx * 0.4, 0, 1.12), K.GOLD())
        on(bone, pad)
    on("hips", tabard, width=0.5, bottom=0.12)
    L.finalize()
    return L.export("super_caballero")


def sacerdote():
    L.reset("Sacerdote")
    L.load_char("Mage", BODY + ["Cape"])
    mn, mx = L.kk_bounds("Head")

    def mitre():
        z = mx.z - 0.3
        cyl(0.44, 0.3, 0.8, (0, 0.02, z + 0.4), K.WHITE(), v=32, sub=1)
        torus(0.43, 0.04, (0, 0.02, z + 0.04), K.GOLD())
        box((0.1, 0.06, 0.62), (0, -0.4, z + 0.38), K.TRIBU(), rot=(R(-9), 0, 0), bevel=0.02)
        box((0.36, 0.06, 0.1), (0, -0.38, z + 0.5), K.TRIBU(), rot=(R(-9), 0, 0), bevel=0.02)
        sphere(0.08, (0, 0.02, z + 0.85), K.GOLD())

    def beard():
        sphere(0.32, (0, -0.4, 1.32), K.WHITE(), (1.2, 0.65, 1.15), sub=1)
    on("head", mitre)
    L.finalize()
    return L.export("sacerdote")


def bote():
    """Bote que aparece debajo de cualquier tropa que navega (sin esqueleto)."""
    import bpy, bmesh
    L.reset("Bote")
    WOOD, WOOD_D = K.WOOD, K.WOOD_D
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=16, location=(0, 0, 0.35))
    o = bpy.context.object
    o.scale = (0.55, 1.15, 0.45)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0.0),
                           plane_no=(0, 0, 1), clear_outer=True)
    bm.to_mesh(o.data); bm.free()
    K._fin(o, WOOD())
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.06
    box((0.66, 1.5, 0.04), (0, 0, 0.16), WOOD_D(), bevel=0.0)
    for y in (-0.5, 0.5):
        box((0.86, 0.12, 0.05), (0, y, 0.3), WOOD_D(), bevel=0.01)
    cyl(0.04, 0.035, 1.6, (0, 0.1, 1.05), WOOD_D())
    cyl(0.025, 0.025, 1.0, (0, 0.1, 1.75), WOOD_D(), rot=(0, R(90), 0))
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=8, size=1, location=(0, 0.05, 1.3),
                                    rotation=(R(90), 0, 0))
    sail = bpy.context.object
    sail.scale = (0.95, 0.9, 1)
    for v in sail.data.vertices:
        v.co.z += -0.18 * (1 - (v.co.x * 2) ** 2) * (1 - (v.co.y * 2) ** 2)
    K._fin(sail, K.TRIBU())
    md = sail.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.02
    box((0.06, 0.06, 0.12), (0, 1.12, 0.45), K.TRIBU(), bevel=0.01)
    cyl(0.04, 0.0, 0.2, (0, -1.15, 0.5), WOOD_D(), rot=(R(-70), 0, 0), v=8)
    L.finalize()
    return L.export("bote")


def _ring(rx, ry, h, z, m, thick=0.05, y=0.0):
    """Borda: anillo elíptico abierto arriba y abajo."""
    import bpy
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=1, depth=h, location=(0, y, z),
                                        end_fill_type="NOTHING")
    o = bpy.context.object
    o.scale = (rx, ry, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    K._fin(o, m)
    md = o.modifiers.new("grosor", "SOLIDIFY")
    md.thickness = thick
    return o


def _sail(w, h, loc, m, billow=0.16):
    import bpy
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=8, size=1, location=loc,
                                    rotation=(R(90), 0, 0))
    o = bpy.context.object
    o.scale = (w, h, 1)
    for v in o.data.vertices:
        v.co.z += -billow * (1 - (v.co.x * 2) ** 2) * (1 - (v.co.y * 2) ** 2) - 0.04 * (v.co.y + 0.5)
    K._fin(o, m)
    md = o.modifiers.new("grosor", "SOLIDIFY")
    md.thickness = 0.02
    return o


def barco():
    """Galeón del capitán (aparece cuando el capitán está en el agua). Mira hacia -Y."""
    import bpy, bmesh
    L.reset("Barco")
    WOOD = lambda: mat("CascoOscuro", "6b3a1f", 0.8)
    WOOD_L = lambda: mat("Cubierta", "b47a45", 0.8)
    WOOD_O = lambda: mat("MaderaNaranja", "d9893a", 0.7)
    ROPE = lambda: mat("Cuerda", "c9a86a")
    # Casco: medio elipsoide
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=40, ring_count=20, location=(0, 0, 0.6))
    o = bpy.context.object
    o.scale = (0.62, 1.45, 0.62)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0.0),
                           plane_no=(0, 0, 1), clear_outer=True)
    for v in bm.verts:                       # proa un poco más afilada y alta
        if v.co.y < -0.6:
            v.co.x *= 1 - 0.35 * (-v.co.y - 0.6)
            v.co.z += 0.12 * (-v.co.y - 0.6)
    bm.to_mesh(o.data); bm.free()
    K._fin(o, WOOD())
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.05
    t = torus(1.0, 0.035, (0, 0, 0.5), K.WHITE()); t.scale = (0.6, 1.4, 1)            # franja blanca
    t = torus(1.0, 0.03, (0, 0, 0.6), K.GOLD()); t.scale = (0.62, 1.45, 1)           # borde dorado
    _ring(0.6, 1.4, 0.22, 0.7, WOOD_O(), thick=0.05)                                   # borda
    d = cyl(1.0, 1.0, 0.04, (0, 0, 0.58), WOOD_L(), v=40); d.scale = (0.58, 1.38, 1)  # cubierta
    # Castillo de popa con ventanas y de proa
    box((1.0, 0.62, 0.42), (0, 1.0, 0.82), WOOD_O(), bevel=0.04)
    box((1.04, 0.66, 0.06), (0, 1.0, 1.05), K.GOLD(), bevel=0.02)
    for x in (-0.25, 0.0, 0.25):
        box((0.14, 0.04, 0.14), (x, 1.32, 0.82), mat("Ventana", "f6d27a", 0.3), bevel=0.02)
    for sx in (-1, 1):
        box((0.04, 0.5, 0.12), (sx * 0.5, 1.0, 1.14), WOOD_O(), bevel=0.01)          # baranda
    box((0.8, 0.4, 0.22), (0, -1.05, 0.78), WOOD_O(), bevel=0.04)
    cyl(0.045, 0.03, 1.0, (0, -1.75, 1.05), WOOD(), rot=(R(-65), 0, 0))              # bauprés
    # Cañones
    for sx in (-1, 1):
        for y in (-0.45, 0.05, 0.55):
            cyl(0.07, 0.06, 0.3, (sx * 0.6, y, 0.42), K.BLACK(), rot=(0, R(90), 0))
            torus(0.075, 0.015, (sx * 0.62, y, 0.42), K.GOLD(), rot=(0, R(90), 0))
    # Ancla
    cyl(0.025, 0.025, 0.3, (0.48, -0.95, 0.55), K.STEEL_D())
    tube([(0.43, -0.98, 0.42), (0.48, -1.0, 0.38), (0.55, -0.97, 0.42)], 0.025, K.STEEL_D())
    # Mástiles, velas y banderas
    for y, h, sails in ((-0.6, 1.9, 2), (0.1, 2.4, 3), (0.72, 1.6, 2)):
        cyl(0.05, 0.04, h, (0, y, 0.6 + h / 2), WOOD())
        top = 0.6 + h
        for k in range(sails):
            sh = 0.5 if sails == 3 else 0.55
            sw = 1.0 - 0.15 * k
            zc = top - 0.35 - k * (sh + 0.06)
            cyl(0.02, 0.02, sw + 0.15, (0, y, zc + sh / 2 + 0.03), WOOD(), rot=(0, R(90), 0))   # verga
            _sail(sw, sh, (0, y - 0.02, zc), K.TRIBU())
        box((0.03, 0.32, 0.16), (0, y + 0.16, top + 0.12), K.TRIBU(), bevel=0.0)              # bandera
        cyl(0.03, 0.03, 0.2, (0, y, top + 0.1), WOOD())
    torus(0.12, 0.03, (0, 0.1, 2.55), WOOD_O())                                                # cofa
    cyl(0.12, 0.12, 0.06, (0, 0.1, 2.53), WOOD_O())
    # Cuerdas
    for y0, y1, z1 in ((-1.95, -0.6, 2.4), (1.2, 0.72, 2.1), (-0.6, 0.1, 2.9)):
        tube([(0, y0, 1.2 if y0 < -1 else 1.1), (0, y1, z1)], 0.012, ROPE(), smooth_curve=False)
    for sx in (-1, 1):
        tube([(sx * 0.58, 0.1, 0.7), (sx * 0.05, 0.1, 2.5)], 0.012, ROPE(), smooth_curve=False)
        tube([(sx * 0.58, -0.6, 0.7), (sx * 0.05, -0.6, 2.2)], 0.012, ROPE(), smooth_curve=False)
    L.finalize()
    return L.export("barco")


# ---------------------------------------------------------------------------------------
# Armas

def _lanza():
    cyl(0.06, 0.06, 3.4, (0, 0, 0.5), K.WOOD_D())
    cyl(0.1, 0.0, 0.5, (0, 0, 2.45), K.STEEL(), v=8)
    cyl(0.07, 0.07, 0.1, (0, 0, 2.18), K.GOLD())
    cyl(0.07, 0.07, 0.25, (0, 0, 0.0), K.LEATHER())
    box((0.5, 0.02, 0.3), (0.27, 0, 1.95), K.TRIBU(), bevel=0.0)
    cyl(0.17, 0.0, 0.3, (0.6, 0, 1.95), K.TRIBU(), rot=(0, R(90), 0), v=3)


def _sable():
    import bpy
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=2, y_subdivisions=12, size=1)
    o = bpy.context.object
    for v in o.data.vertices:
        t = v.co.y + 0.5                         # 0 abajo, 1 punta
        w = 0.15 * (1 - 0.55 * t ** 3)
        x = v.co.x * 2 * w + 0.35 * t ** 2 * 0.6
        if t > 0.92 and v.co.x < 0:
            x += 0.08 * (t - 0.92) / 0.08
        v.co = (x, 0, 0.25 + t * 1.25)
    K._fin(o, K.STEEL(), smooth=False)
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.04; md.offset = 0
    box((0.36, 0.08, 0.06), (0, 0, 0.2), K.GOLD(), bevel=0.02)
    tube([(0.17, 0, 0.2), (0.2, 0, 0.0), (0.05, 0, -0.18)], 0.025, K.GOLD())
    cyl(0.05, 0.05, 0.32, (0, 0, 0.02), K.LEATHER_D())
    sphere(0.065, (0, 0, -0.17), K.GOLD())


def _garfio():
    cyl(0.12, 0.1, 0.22, (0, 0, 0.0), K.LEATHER_D(), bevel=0.02)
    cyl(0.03, 0.03, 0.2, (0, 0, 0.2), K.STEEL())
    tube([(0, 0, 0.28), (0, 0, 0.45), (0.08, 0, 0.55), (0.18, 0, 0.48), (0.17, 0, 0.38)], 0.03, K.STEEL())


def armas():
    """Armas KayKit pasadas al formato Kolonia y armas propias (se pegan a la mano en Godot)."""
    out = []
    for src, name, tex, extra in (("sword_1handed", "espada", "knight", None),
                                  ("sword_2handed_color", "espadon", "knight", None),
                                  ("shield_spikes_color", "escudo_puas", "knight", [(3, 2), (3, 3)]),
                                  ("shield_round_color", "escudo_redondo", "knight", None),
                                  ("bow_withString", "arco", "ranger", None),
                                  ("staff", "baculo", "mage", None)):
        out.append(L.export_weapon(src, name, tex=tex, extra=extra))
    out.append(L.export_custom_weapon("lanza", _lanza))
    out.append(L.export_custom_weapon("sable", _sable))
    out.append(L.export_custom_weapon("garfio", _garfio))
    return out


TROPAS = (caballero, escudero, arquero, jinete, jinete_lancero, capitan, catapulta,
          super_caballero, sacerdote, bote, barco)


def todas():
    for f in TROPAS:
        print(f.__name__, f())
    print(armas())
