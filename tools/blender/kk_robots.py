# Tribu de los Robots: cuerpos de metal (sobre el esqueleto KayKit, que parece un
# endoesqueleto), cabezas con pantalla y luces de energía. Montan caballos mecánicos.
# Héroes: la Máquina de asedio (rayo láser en línea) y el Ingeniero (repara y mejora).
import math
import kolonia_lib as K
import kk_lib as L
import kk_tribus_comun as C
from kolonia_lib import R, sphere, cyl, box, torus, tube, mat
from kk_tropas import on

MET = lambda: mat("Metal", "8a939e", 0.4, 0.8)
MET_D = lambda: mat("MetalOscuro", "4c535c", 0.4, 0.8)
COPPER = lambda: mat("Cobre", "c87a3a", 0.35, 0.8)
GLOW = lambda: mat("Luz", "35e0ff", 0.2)
SCREEN = lambda: mat("Pantalla", "141a22", 0.2)
RUBBER = lambda: mat("Goma", "26282c", 0.8)
SKEL = ["ArmLeft", "ArmRight", "Body", "LegLeft", "LegRight"]
# Esqueleto: huesos (1,2/1,3) de metal, mandíbula/barba (2,4/2,5) de metal oscuro
RECOLOR = {(1, 2): "9aa3ad", (1, 3): "76808a", (2, 4): "5c636c", (2, 5): "464c54", (2, 2): "5c636c",
           (2, 3): "464c54", (0, 2): "6a717a", (0, 3): "50565e", (3, 4): "6a717a", (3, 5): "50565e",
           (1, 4): "35e0ff", (1, 5): "1ab0d0"}


def setup(keep=None):
    L.recolor(RECOLOR)
    L.S["team_only"] = []
    L.load_char("Skeleton_Warrior", keep or SKEL)


def robot_head(kind="visor", antenna=True, size=1.0):
    """Cabeza de robot: caja con pantalla y ojos que brillan."""
    k = size
    box((0.92 * k, 0.82 * k, 0.74 * k), (0, 0.0, 1.72), MET(), bevel=0.16)
    box((0.96 * k, 0.86 * k, 0.1), (0, 0.0, 1.42), MET_D(), bevel=0.04)          # cuello/borde
    if kind == "visor":
        box((0.72 * k, 0.06, 0.34 * k), (0, -0.41 * k, 1.74), SCREEN(), bevel=0.06)
        for sx in (-1, 1):
            box((0.16 * k, 0.04, 0.09 * k), (sx * 0.16 * k, -0.45 * k, 1.76), GLOW(), bevel=0.03)
        box((0.18 * k, 0.04, 0.035), (0, -0.45 * k, 1.64), GLOW(), bevel=0.01)       # boca
    elif kind == "lente":
        cyl(0.22 * k, 0.22 * k, 0.12, (0, -0.42 * k, 1.74), MET_D(), rot=(R(90), 0, 0))
        cyl(0.16 * k, 0.16 * k, 0.14, (0, -0.43 * k, 1.74), GLOW(), rot=(R(90), 0, 0))
        cyl(0.07 * k, 0.07 * k, 0.16, (0, -0.44 * k, 1.74), SCREEN(), rot=(R(90), 0, 0))
        torus(0.22 * k, 0.03, (0, -0.48 * k, 1.74), K.TRIBU(), rot=(R(90), 0, 0))
    elif kind == "casco":
        box((0.8 * k, 0.06, 0.16 * k), (0, -0.42 * k, 1.75), GLOW(), bevel=0.05)
        box((1.0 * k, 0.9 * k, 0.2 * k), (0, 0.0, 2.08), K.TRIBU(), bevel=0.06)
        box((0.14, 0.95 * k, 0.12), (0, 0.0, 2.22), MET_D(), bevel=0.03)
    for sx in (-1, 1):                                                     # "orejas"
        cyl(0.12 * k, 0.12 * k, 0.1, (sx * 0.5 * k, 0, 1.74), MET_D(), rot=(0, R(90), 0))
        cyl(0.06 * k, 0.06 * k, 0.12, (sx * 0.5 * k, 0, 1.74), K.TRIBU(), rot=(0, R(90), 0))
    if antenna:
        cyl(0.025, 0.025, 0.35, (0.22 * k, 0.1, 2.2), MET_D())
        sphere(0.07, (0.22 * k, 0.1, 2.4), K.TRIBU())
    box((0.5 * k, 0.04, 0.12), (0, -0.42 * k, 2.0), K.TRIBU(), bevel=0.02)        # franja de la tribu


def chest_plate(w=1.0, team=True):
    box((0.62 * w, 0.42, 0.5), (0, -0.04, 0.9), MET(), bevel=0.1)
    if team:
        box((0.4 * w, 0.06, 0.26), (0, -0.25, 0.94), K.TRIBU(), bevel=0.03)
    cyl(0.07, 0.07, 0.05, (0, -0.28, 0.94), GLOW(), rot=(R(90), 0, 0))
    for sx in (-1, 1):
        cyl(0.03, 0.03, 0.06, (sx * 0.24 * w, -0.26, 0.75), COPPER(), rot=(R(90), 0, 0))


def hip_plate():
    cyl(0.3, 0.33, 0.2, (0, 0, 0.55), MET_D(), v=8, bevel=0.03)
    box((0.3, 0.05, 0.22), (0, -0.33, 0.45), K.TRIBU(), bevel=0.02)


def shoulder(bone, sx, big=False):
    def b():
        s = 1.25 if big else 1.0
        sphere(0.2 * s, (sx * 0.4, 0, 1.18), MET(), (1.0, 1.0, 0.8), sub=1)
        box((0.12 * s, 0.3 * s, 0.05), (sx * 0.48, 0, 1.3), K.TRIBU(), bevel=0.02)
        if big:
            cyl(0.04, 0.04, 0.2, (sx * 0.4, 0.15, 1.38), COPPER())
    on(bone, b)


# ---------------------------------------------------------------------------------------
# Tropas

def androide():
    """Caballero: androide con pantalla de visor y espada de energía."""
    L.reset("Androide")
    setup()
    on("head", robot_head)
    on("chest", chest_plate)
    on("hips", hip_plate)
    shoulder("upperarm.r", -1)
    shoulder("upperarm.l", 1)
    L.finalize()
    C.arma("androide", "espada_energia", "handslot.r")
    return L.export("androide")


def blindado():
    """Escudero: robot pesado con casco y escudo de energía hexagonal."""
    L.reset("Blindado")
    setup()
    on("head", robot_head, "casco", False, 1.08)
    on("chest", chest_plate, 1.25)
    on("hips", hip_plate)
    shoulder("upperarm.r", -1, True)
    shoulder("upperarm.l", 1, True)
    for sx, bone in ((1, "lowerleg.l"), (-1, "lowerleg.r")):
        def shin(sx=sx):
            box((0.22, 0.22, 0.3), (sx * 0.15, -0.05, 0.22), MET(), bevel=0.05)
        on(bone, shin)
    L.finalize()
    C.arma("blindado", "baston_electrico", "handslot.r")
    C.arma("blindado", "escudo_energia", "handslot.l")
    return L.export("blindado")


def francotirador():
    """Arquero: robot de un solo ojo (lente) con rifle láser."""
    L.reset("Francotirador")
    setup()
    on("head", robot_head, "lente")
    on("chest", chest_plate, 0.9)
    on("hips", hip_plate)

    def pack():
        box((0.4, 0.22, 0.5), (0, 0.32, 0.95), MET_D(), bevel=0.06)
        for k in range(3):
            cyl(0.05, 0.05, 0.42, (-0.12 + k * 0.12, 0.42, 0.95), GLOW())
    on("chest", pack)
    L.finalize()
    C.arma("francotirador", "rifle_laser", "handslot.l", (0, 0, 180))
    return L.export("francotirador")


def jinete_robot():
    """Jinete: androide sobre un caballo mecánico."""
    def head():
        on("head", robot_head)

    def extra():
        on("chest", chest_plate)
    path = C.rider("Jinete_robot", "Skeleton_Warrior", SKEL, lambda: C.robocaballo(), False,
                   headgear=head, extra=extra, recolor=RECOLOR, team_only=[])
    C.arma("jinete_robot", "espada_energia", "handslot.r")
    return path


def lancero_robot():
    """Jinete lancero: robot con casco sobre un caballo mecánico blindado, lanza de energía."""
    def head():
        on("head", robot_head, "casco", False)

    def extra():
        on("chest", chest_plate, 1.15)
    path = C.rider("Lancero_robot", "Skeleton_Warrior", SKEL, lambda: C.robocaballo(armor=True), True,
                   headgear=head, extra=extra, recolor=RECOLOR, team_only=[])
    C.arma("lancero_robot", "lanza_energia", "handslot.r")
    return path


def mortero():
    """Catapulta: mortero sobre orugas; el tubo se levanta al disparar."""
    def frame():
        for sx in (-1, 1):
            box((0.18, 1.1, 0.3), (sx * 0.38, 0, 0.18), RUBBER(), bevel=0.12)       # orugas
            for y in (-0.38, -0.12, 0.12, 0.38):
                cyl(0.11, 0.11, 0.2, (sx * 0.38, y, 0.17), MET_D(), rot=(0, R(90), 0))
        box((0.65, 0.95, 0.22), (0, 0, 0.42), MET(), bevel=0.06)
        box((0.4, 0.05, 0.16), (0, -0.48, 0.42), K.TRIBU(), bevel=0.02)
        for sx in (-1, 1):
            box((0.08, 0.18, 0.3), (sx * 0.2, 0.2, 0.68), MET_D(), bevel=0.02)       # soportes del tubo
            cyl(0.06, 0.06, 0.06, (sx * 0.38, -0.45, 0.48), GLOW(), rot=(0, R(90), 0))
        cyl(0.06, 0.06, 0.5, (0, 0.2, 0.75), COPPER(), rot=(0, R(90), 0))           # eje
        box((0.3, 0.3, 0.2), (0, 0.42, 0.6), MET_D(), bevel=0.05)                   # caja de munición
        cyl(0.05, 0.05, 0.08, (0, 0.42, 0.72), K.TRIBU())

    def arm():
        # tubo del mortero (gira con el hueso "brazo_cat")
        cyl(0.13, 0.15, 0.7, (0, 0.5, 0.95), MET(), rot=(R(-35), 0, 0))
        torus(0.15, 0.03, (0, 0.67, 1.22), K.TRIBU(), rot=(R(-35), 0, 0))
        cyl(0.09, 0.09, 0.05, (0, 0.71, 1.29), SCREEN(), rot=(R(-35), 0, 0))
        torus(0.14, 0.025, (0, 0.38, 0.77), COPPER(), rot=(R(-35), 0, 0))

    def operator():
        on("head", robot_head, "visor", True)
        on("chest", chest_plate)
    return C.siege("Mortero", "Skeleton_Warrior", SKEL, frame, arm, operator, recolor=RECOLOR, team_only=[],
                   arm_bone=("brazo_cat", (0, 0.2 * 2.0, 0.75 * 2.0), (0, 0.7 * 2.0, 1.29 * 2.0), None))


def capitan_robot():
    """Capitán: robot con sombrero de capitán metálico, ojo parche de luz y garfio."""
    L.reset("Capitan_robot")
    setup()

    def head():
        robot_head("visor", False)
        cyl(0.62, 0.62, 0.1, (0, 0.05, 2.12), MET_D(), v=3, rot=(0, 0, R(-90)), bevel=0.04)
        torus(0.55, 0.035, (0, 0.05, 2.18), K.GOLD(), seg=3, rot=(0, 0, R(-90)))
        sphere(0.38, (0, 0.05, 2.18), MET_D(), (1, 1, 0.62), sub=1)
        box((0.18, 0.05, 0.12), (0, -0.33, 2.3), K.TRIBU(), bevel=0.02)
        box((0.18, 0.05, 0.1), (-0.16, -0.46, 1.76), K.TRIBU(), bevel=0.02)       # parche
    on("head", head)
    on("chest", chest_plate)
    on("hips", hip_plate)
    L.finalize()
    C.arma("capitan_robot", "espada_energia", "handslot.r")
    C.arma("capitan_robot", "garfio", "handslot.l")
    return L.export("capitan_robot")


def barco_robot():
    """Barco: barco de vapor de hierro con chimenea, ruedas de paletas y faros."""
    def build():
        IRON = lambda: mat("Hierro", "5a626c", 0.45, 0.8)
        C.hull(0.62, 1.55, 0.6, IRON(), z=0.6, sharp=0.5, raise_bow=0.15)
        import kk_tropas as T
        T._ring(0.6, 1.5, 0.22, 0.72, MET(), thick=0.05)
        t = torus(1.0, 0.04, (0, 0, 0.45), K.TRIBU()); t.scale = (0.6, 1.5, 1)
        for y in (-1.0, -0.5, 0.0, 0.5, 1.0):                                   # remaches
            for sx in (-1, 1):
                sphere(0.03, (sx * 0.6 * math.sqrt(max(0.0, 1 - (y / 1.55) ** 2)), y, 0.55), COPPER())
        d = cyl(1.0, 1.0, 0.04, (0, 0, 0.62), MET_D(), v=40); d.scale = (0.58, 1.48, 1)
        # puente de mando con ventanas que brillan
        box((0.75, 0.7, 0.45), (0, 0.55, 0.88), MET(), bevel=0.06)
        for x in (-0.22, 0.0, 0.22):
            box((0.14, 0.04, 0.12), (x, 0.19, 0.92), GLOW(), bevel=0.02)
        box((0.8, 0.75, 0.06), (0, 0.55, 1.13), K.TRIBU(), bevel=0.02)
        # chimeneas
        for k, y in enumerate((-0.1, 0.25)):
            cyl(0.15, 0.17, 0.9, (0, y, 1.4 - k * 0.1), MET_D())
            torus(0.16, 0.03, (0, y, 1.8 - k * 0.1), K.TRIBU())
            for j in range(3):
                sphere(0.13 + j * 0.04, (0.05 * j, y + 0.1 * j, 2.0 + j * 0.22 - k * 0.1),
                       mat("Humo", "c8ccd2", 0.9), sub=1)
        # ruedas de paletas
        for sx in (-1, 1):
            cyl(0.42, 0.42, 0.2, (sx * 0.7, 0.05, 0.6), MET_D(), rot=(0, R(90), 0), v=24)
            for k in range(8):
                a = k * math.tau / 8
                box((0.22, 0.06, 0.4), (sx * 0.7, 0.05 + math.cos(a) * 0.25, 0.6 + math.sin(a) * 0.25), MET(),
                    rot=(a, 0, 0), bevel=0.01)
            cyl(0.08, 0.08, 0.24, (sx * 0.7, 0.05, 0.6), K.TRIBU(), rot=(0, R(90), 0))
        # faro y cañón de proa
        cyl(0.08, 0.1, 0.22, (0, -1.2, 0.8), MET_D())
        sphere(0.08, (0, -1.25, 0.95), GLOW())
        cyl(0.07, 0.06, 0.5, (0, -0.85, 0.82), MET(), rot=(R(-80), 0, 0))
        # mástil con bandera
        cyl(0.03, 0.03, 1.2, (0, 0.95, 1.5), MET_D())
        box((0.03, 0.34, 0.2), (0, 1.13, 1.98), K.TRIBU(), bevel=0.0)
    return C.static_model("Barco_robot", build)


# ---------------------------------------------------------------------------------------
# Héroes

def maquina_asedio():
    """Máquina de asedio (héroe criatura): caminante de cuatro patas con un cañón láser
    que golpea a todo lo que esté en la línea entre ella y su objetivo."""
    def build():
        # cuerpo
        box((1.2, 1.4, 0.55), (0, 0.1, 1.3), MET(), bevel=0.18)
        box((1.0, 1.2, 0.2), (0, 0.1, 1.0), MET_D(), bevel=0.06)
        for sx in (-1, 1):
            box((0.06, 0.8, 0.3), (sx * 0.6, 0.1, 1.32), K.TRIBU(), bevel=0.02)
            for y in (-0.2, 0.15, 0.5):
                cyl(0.05, 0.05, 0.06, (sx * 0.62, y, 1.15), GLOW(), rot=(0, R(90), 0))
        # cabina con ojo
        sphere(0.38, (0, -0.55, 1.45), MET(), (1.0, 0.9, 0.75), sub=1)
        cyl(0.17, 0.17, 0.1, (0, -0.9, 1.45), SCREEN(), rot=(R(90), 0, 0))
        cyl(0.11, 0.11, 0.12, (0, -0.91, 1.45), mat("OjoRojo", "ff3a3a", 0.2), rot=(R(90), 0, 0))
        torus(0.17, 0.03, (0, -0.95, 1.45), K.TRIBU(), rot=(R(90), 0, 0))
        # cañón láser encima (gira en la torreta)
        cyl(0.35, 0.38, 0.2, (0, 0.2, 1.68), MET_D(), v=24)
        box((0.5, 0.6, 0.35), (0, 0.15, 1.95), MET(), bevel=0.08)
        cyl(0.13, 0.15, 1.1, (0, -0.55, 2.0), MET(), rot=(R(-90), 0, 0))
        for k in range(3):
            torus(0.16, 0.035, (0, -0.25 - k * 0.25, 2.0), [K.TRIBU, COPPER, K.TRIBU][k](), rot=(R(90), 0, 0))
        cyl(0.1, 0.1, 0.06, (0, -1.11, 2.0), GLOW(), rot=(R(90), 0, 0))
        for sx in (-1, 1):
            tube([(sx * 0.25, 0.4, 1.95), (sx * 0.35, 0.0, 2.1), (sx * 0.15, -0.6, 2.12)], 0.035, COPPER())
        # cuatro patas articuladas
        for sx in (-1, 1):
            for y in (-0.4, 0.6):
                hip = (sx * 0.6, y, 1.1)
                knee = (sx * 1.05, y + (-0.15 if y < 0 else 0.15), 1.25)
                foot = (sx * 1.15, y + (-0.3 if y < 0 else 0.3), 0.08)
                sphere(0.16, hip, MET_D(), sub=1)
                tube([hip, knee], 0.1, MET())
                sphere(0.14, knee, K.TRIBU(), sub=1)
                tube([knee, foot], 0.08, MET())
                box((0.32, 0.36, 0.12), (foot[0], foot[1], 0.06), MET_D(), bevel=0.04)
                cyl(0.04, 0.04, 0.4, (foot[0] - sx * 0.05, foot[1], 0.6), COPPER(), rot=(0, R(sx * 8), 0))
        # antena y bandera
        cyl(0.025, 0.025, 0.6, (0.4, 0.65, 1.8), MET_D())
        box((0.03, 0.28, 0.18), (0.4, 0.8, 2.02), K.TRIBU(), bevel=0.0)
    return C.static_model("Maquina_asedio", build)


def ingeniero():
    """Ingeniero (héroe): humano con gafas, casco, mochila de herramientas y brazo
    mecánico. Repara a las máquinas de su tribu y mejora por una ronda a un aliado."""
    L.reset("Ingeniero")
    L.recolor({(6, 0): "c87a3a", (6, 1): "9a5a28", (1, 4): "3a3a3a", (1, 5): "2a2a2a"})
    L.S["team_only"] = [(0, 2), (0, 3)]
    L.load_char("Ranger", C.BODY)

    def head():
        C.cap(lambda: mat("CascoObra", "f2b52a", 0.4), r=0.64, front_z=2.02, back_z=1.6, rim=K.TRIBU, rim_r=0.05)
        box((0.14, 0.7, 0.1), (0, 0.0, 2.36), mat("CascoObra", "f2b52a", 0.4), bevel=0.04)
        # gafas sobre el casco
        for sx in (-1, 1):
            cyl(0.13, 0.13, 0.1, (sx * 0.17, -0.55, 2.0), COPPER(), rot=(R(80), 0, 0))
            cyl(0.1, 0.1, 0.12, (sx * 0.17, -0.56, 2.0), GLOW(), rot=(R(80), 0, 0))
        box((0.1, 0.06, 0.05), (0, -0.6, 2.02), COPPER(), bevel=0.01)
    on("head", head)

    def pack():
        box((0.55, 0.3, 0.6), (0, 0.38, 0.95), MET(), bevel=0.08)
        box((0.4, 0.05, 0.2), (0, 0.54, 1.05), K.TRIBU(), bevel=0.02)
        for sx in (-1, 1):
            cyl(0.06, 0.06, 0.5, (sx * 0.2, 0.45, 1.35), COPPER())
            sphere(0.07, (sx * 0.2, 0.45, 1.62), GLOW())
        # brazo mecánico extra que sale de la mochila
        tube([(0.25, 0.45, 1.2), (0.6, 0.5, 1.55), (0.75, 0.1, 1.6)], 0.05, MET_D())
        sphere(0.08, (0.6, 0.5, 1.55), K.TRIBU())
        for k in range(3):
            a = R(-30 + k * 30)
            cyl(0.02, 0.0, 0.14, (0.78 + math.sin(a) * 0.06, 0.02, 1.6 + math.cos(a) * 0.06), MET(), v=6)
    on("chest", pack)

    def belt():
        cyl(0.36, 0.36, 0.1, (0, 0, 0.6), K.LEATHER(), v=24)
        for k, x in enumerate((-0.25, -0.08, 0.1, 0.27)):
            box((0.1, 0.06, 0.16), (x, -0.36, 0.52), [COPPER, MET, K.TRIBU, MET_D][k](), bevel=0.02)
    on("hips", belt)
    L.finalize()
    C.arma("ingeniero", "llave_inglesa", "handslot.r")
    return L.export("ingeniero")


# ---------------------------------------------------------------------------------------
# Armas

def _espada_energia():
    cyl(0.05, 0.05, 0.3, (0, 0, 0.0), MET_D())
    box((0.22, 0.08, 0.06), (0, 0, 0.17), K.TRIBU(), bevel=0.02)
    box((0.08, 0.04, 0.95), (0, 0, 0.68), GLOW(), bevel=0.03)
    cyl(0.0, 0.05, 0.12, (0, 0, 1.2), GLOW(), v=4, rot=(R(180), 0, 0))
    sphere(0.06, (0, 0, -0.16), COPPER())


def _escudo_energia():
    grp = [cyl(0.42, 0.42, 0.05, (0, 0, 0), mat("LuzTenue", "7fe9ff", 0.15), v=6, bevel=0.01)]
    grp.append(torus(0.42, 0.04, (0, 0, 0), MET(), seg=6))
    grp.append(cyl(0.12, 0.12, 0.08, (0, 0, 0.02), K.TRIBU(), v=6))
    grp.append(cyl(0.06, 0.06, 0.1, (0, 0, 0.03), GLOW(), v=6))
    K._group(grp, (0, 0, 0), (R(90), 0, R(30)))


def _baston():
    cyl(0.05, 0.05, 0.9, (0, 0, 0.3), MET_D())
    for k in range(3):
        torus(0.06, 0.02, (0, 0, 0.5 + k * 0.12), GLOW())
    sphere(0.08, (0, 0, 0.8), K.TRIBU())


def _rifle_laser():
    # Se sostiene como el arco (mano izquierda): el cañón apunta a +X
    box((0.85, 0.1, 0.14), (0.2, 0, 0.0), MET(), bevel=0.04)
    cyl(0.05, 0.05, 0.5, (0.85, 0, 0.0), MET_D(), rot=(0, R(90), 0))
    cyl(0.04, 0.04, 0.06, (1.1, 0, 0.0), GLOW(), rot=(0, R(90), 0))
    box((0.2, 0.08, 0.3), (-0.12, 0, -0.18), MET_D(), bevel=0.03)
    cyl(0.06, 0.06, 0.3, (0.25, 0, 0.13), SCREEN(), rot=(0, R(90), 0))
    box((0.3, 0.11, 0.04), (0.25, 0, 0.0), K.TRIBU(), bevel=0.01)


def _lanza_energia():
    cyl(0.06, 0.06, 3.2, (0, 0, 0.5), MET_D())
    for k in range(3):
        torus(0.07, 0.02, (0, 0, 1.5 + k * 0.25), K.TRIBU())
    cyl(0.1, 0.0, 0.6, (0, 0, 2.4), GLOW(), v=4)
    cyl(0.09, 0.09, 0.1, (0, 0, 2.08), COPPER())


def _llave():
    cyl(0.04, 0.04, 0.6, (0, 0, 0.2), MET())
    cyl(0.05, 0.05, 0.25, (0, 0, -0.02), K.TRIBU())
    t = torus(0.1, 0.035, (0, 0, 0.58), MET(), rot=(R(90), 0, 0))
    box((0.08, 0.06, 0.12), (0, 0, 0.66), MET_D(), bevel=0.01)


def armas():
    return [L.export_custom_weapon("espada_energia", _espada_energia),
            L.export_custom_weapon("escudo_energia", _escudo_energia),
            L.export_custom_weapon("baston_electrico", _baston),
            L.export_custom_weapon("rifle_laser", _rifle_laser),
            L.export_custom_weapon("lanza_energia", _lanza_energia),
            L.export_custom_weapon("llave_inglesa", _llave)]


TROPAS = {"caballero": androide, "escudero": blindado, "arquero": francotirador, "jinete": jinete_robot,
          "jinete_lancero": lancero_robot, "catapulta": mortero, "capitan": capitan_robot,
          "barco": barco_robot, "heroe_1": maquina_asedio, "heroe_2": ingeniero}


def todas():
    C.tribu("robots")
    print(armas())
    for f in TROPAS.values():
        print(f.__name__, f())
    C.save_weapons({"nombre": "Robots", "tropas": {k: f.__name__ for k, f in TROPAS.items()}})
