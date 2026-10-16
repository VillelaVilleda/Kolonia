# Tribu del Desierto: estilo egipcio. Lino blanco, oro, lapislázuli y arena. Montan
# camellos. Héroes: el Gólem de arena y Anubis (que convierte enemigos en momias).
import math
import kolonia_lib as K
import kk_lib as L
import kk_tribus_comun as C
from kolonia_lib import R, sphere, cyl, box, torus, tube, mat
from kk_tropas import on

BODY = C.BODY
SKIN = "a86b42"
LINEN = lambda: mat("Lino", "efe6cf", 0.7)
LAPIS = lambda: mat("Lapislazuli", "1f4fa0", 0.4)
SAND = lambda: mat("Arena", "d9b77a", 0.85)
SAND_D = lambda: mat("ArenaOscura", "a8844a", 0.85)
TURQ = lambda: mat("Turquesa", "34b8b0", 0.4)
BLACK = K.BLACK
GOLD = K.GOLD
# Ranger: túnica (6,0/6,1) de lino, pañuelo (0,2/0,3) del color de la tribu, botas = sandalias
RECOLOR = {(0, 0): SKIN, (0, 1): SKIN, (1, 0): "3a2a1e", (1, 1): "2e2016",
           (6, 0): "efe6cf", (6, 1): "d9cfb0", (1, 4): "8a5a30", (1, 5): "6a4020"}
TEAM = [(0, 2), (0, 3)]
# Rogue con capucha y máscara: ropa de arena (nómada del desierto)
RECOLOR_HOOD = {(0, 0): SKIN, (0, 1): SKIN, (1, 0): "1c1714", (1, 1): "1c1714",
                (0, 2): "d9b77a", (0, 3): "b8955a", (1, 4): "8a5a30", (1, 5): "6a4020"}


def setup(char="Ranger", keep=None, recolor=None, team=None):
    L.recolor(recolor or RECOLOR)
    L.S["team_only"] = team if team is not None else TEAM
    L.load_char(char, keep or (BODY + ["Cape"]))


def nemes(stripes=True, uraeus=True, color2=None):
    """Tocado de faraón: casquete y dos paños que caen sobre los hombros, a rayas."""
    c2 = color2 or GOLD
    C.cap(K.TRIBU, r=0.71, front_z=2.04, back_z=1.25, rim=c2, rim_r=0.05)
    for sx in (-1, 1):
        for k in range(5):
            m = K.TRIBU if k % 2 == 0 else c2
            box((0.3, 0.1, 0.09), (sx * 0.52, -0.12, 1.55 - k * 0.09), m(), rot=(0, 0, R(sx * 6)), bevel=0.02)
    box((0.3, 0.18, 0.5), (0, 0.55, 1.35), K.TRIBU(), bevel=0.05)        # cola del tocado
    if uraeus:
        sphere(0.06, (0, -0.62, 1.97), GOLD(), (0.8, 0.6, 1.4))
        sphere(0.05, (0, -0.66, 2.06), GOLD(), (1.1, 0.7, 0.8))


def collar():
    """Collar ancho (usekh) de oro y lapislázuli."""
    for k, (r, m) in enumerate(((0.36, GOLD), (0.42, LAPIS), (0.48, GOLD))):
        t = torus(r, 0.04, (0, -0.02, 1.13 - k * 0.03), m())
        t.scale = (1, 0.85, 1)
    for k in range(10):
        a = R(-160 + k * 15.5)
        sphere(0.035, (math.sin(a) * 0.5, -math.cos(a) * 0.43 * 0.85 - 0.02, 1.06), TURQ())


def kilt(z_top=0.62, z_bot=0.3, r=0.36):
    """Faldellín (shendyt) de lino con cinturón dorado y panel del color de la tribu."""
    h = z_top - z_bot
    cyl(r, r * 1.15, h, (0, 0, z_bot + h / 2), LINEN(), v=24)
    cyl(r + 0.02, r + 0.02, 0.07, (0, 0, z_top), GOLD(), v=24)
    box((0.22, 0.05, h * 0.95), (0, -r * 1.06, z_bot + h / 2), K.TRIBU(), bevel=0.01)
    for k in range(4):
        box((0.22, 0.055, 0.025), (0, -r * 1.07, z_bot + 0.05 + k * h / 4), GOLD(), bevel=0.0)


def turban(gem=True):
    C.cap(K.TRIBU, r=0.7, front_z=1.98, back_z=1.62, scale=(1.0, 1.04, 1.02))
    for k, (z, r) in enumerate(((1.84, 0.6), (1.97, 0.6), (2.1, 0.55))):
        t = torus(r, 0.11, (0, 0.03, z), [K.TRIBU, LINEN][k % 2](), rot=(R(-6 + k * 3), 0, 0))
    sphere(0.5, (0, 0.05, 2.2), K.TRIBU(), (1, 1, 0.5), sub=1)
    if gem:
        sphere(0.08, (0, -0.55, 1.98), TURQ(), sub=1)
        torus(0.08, 0.02, (0, -0.56, 1.98), GOLD(), rot=(R(90), 0, 0))
        sphere(0.07, (0.05, -0.5, 2.18), LINEN(), (0.5, 0.4, 1.6), rot=(R(-20), 0, 0))


def war_crown():
    """Corona de guerra (khepresh): casco alto de lapislázuli con discos de oro."""
    C.cap(LAPIS, r=0.71, front_z=2.06, back_z=1.3, rim=GOLD, rim_r=0.05)
    o = sphere(0.46, (0, 0.22, 2.3), LAPIS(), (0.85, 1.15, 1.05), sub=1)
    o.rotation_euler = (R(-28), 0, 0)
    for k in range(12):
        a = k * math.tau / 12
        sphere(0.045, (math.cos(a) * 0.36, 0.22 + math.sin(a) * 0.4, 2.3 + math.sin(a) * 0.2), GOLD(), (1, 1, 0.5))
    sphere(0.07, (0, -0.55, 2.02), GOLD(), (0.8, 0.6, 1.4))
    sphere(0.06, (0, -0.6, 2.13), GOLD(), (1.1, 0.7, 0.8))
    for sx in (-1, 1):
        box((0.06, 0.4, 0.06), (sx * 0.55, 0.0, 1.62), K.TRIBU(), bevel=0.02)


# ---------------------------------------------------------------------------------------
# Tropas

def guerrero_nilo():
    """Caballero: tocado a rayas, collar de oro, faldellín y espada curva (khopesh)."""
    L.reset("Guerrero_nilo")
    setup()
    on("head", nemes)
    on("chest", collar)
    on("hips", kilt)
    L.finalize()
    C.arma("guerrero_nilo", "khopesh", "handslot.r")
    return L.export("guerrero_nilo")


def guardia_templo():
    """Escudero: corona de guerra, escudo alto con el ojo de Horus y lanza."""
    L.reset("Guardia_templo")
    setup(keep=BODY)
    on("head", war_crown)
    on("chest", collar)
    on("hips", kilt, r=0.38)
    for sx, bone in ((1, "upperarm.l"), (-1, "upperarm.r")):
        def pad(sx=sx):
            sphere(0.22, (sx * 0.4, 0, 1.2), GOLD(), (1.05, 1.0, 0.7), sub=1)
            torus(0.2, 0.035, (sx * 0.4, 0, 1.13), LAPIS())
        on(bone, pad)
    L.finalize()
    C.arma("guardia_templo", "lanza_desierto", "handslot.r")
    C.arma("guardia_templo", "escudo_horus", "handslot.l")
    return L.export("guardia_templo")


def arquero_dunas():
    """Arquero: nómada encapuchado con la cara tapada, arco compuesto."""
    L.reset("Arquero_dunas")
    setup("Rogue_Hooded", BODY + ["Cape", "Mask"], recolor=RECOLOR_HOOD, team=[(1, 2), (1, 3)])

    def cord():
        sphere(0.07, (0, -0.58, 1.98), GOLD(), (1, 0.6, 1))
        sphere(0.04, (0, -0.62, 1.98), TURQ())
    on("head", cord)

    def quiver():
        q = [cyl(0.12, 0.14, 0.72, (0, 0, 0), K.LEATHER(), bevel=0.01),
             torus(0.13, 0.025, (0, 0, 0.3), GOLD())]
        for k in range(4):
            a = k * math.tau / 4
            q.append(cyl(0.015, 0.015, 0.4, (math.cos(a) * 0.06, math.sin(a) * 0.06, 0.55), K.WOOD()))
            q.append(cyl(0.05, 0.0, 0.14, (math.cos(a) * 0.06, math.sin(a) * 0.06, 0.78), K.TRIBU(), v=4))
        K._group(q, (0.18, 0.45, 1.0), (R(-15), R(-25), 0))
    on("chest", quiver)
    L.finalize()
    C.arma("arquero_dunas", "arco_compuesto", "handslot.l", (0, 0, 180))
    return L.export("arquero_dunas")


CAMEL = lambda: mat("Camello", "c99a5c", 0.85)


def jinete_camello():
    """Jinete: turbante, sobre un camello con mantas y borlas."""
    def head():
        on("head", turban)

    def extra():
        on("chest", collar)
    path = C.rider("Jinete_camello", "Ranger", BODY + ["Cape"], lambda: C.camello(CAMEL()), False,
                   headgear=head, extra=extra, recolor=RECOLOR, team_only=TEAM)
    C.arma("jinete_camello", "cimitarra", "handslot.r")
    return path


def lancero_camello():
    """Jinete lancero: corona de guerra, camello acorazado con oro y lino."""
    def head():
        on("head", war_crown)

    def extra():
        on("chest", collar)
    path = C.rider("Lancero_camello", "Ranger", BODY, lambda: C.camello(mat("CamelloClaro", "dcb47a", 0.85), armor=True),
                   True, headgear=head, extra=extra, recolor=RECOLOR, team_only=TEAM)
    C.arma("lancero_camello", "lanza_desierto_larga", "handslot.r")
    return path


def trebuchet():
    """Catapulta: trabuquete de madera clara con contrapeso de piedra y toldo."""
    WOOD = lambda: mat("MaderaClara", "c9a26a", 0.75)
    WOOD_D = lambda: mat("MaderaDesierto", "8a6236", 0.8)

    def frame():
        for sx in (-1, 1):
            box((0.08, 1.15, 0.1), (sx * 0.35, 0, 0.3), WOOD(), bevel=0.015)
            for dy in (-0.25, 0.25):
                box((0.07, 0.07, 1.1), (sx * 0.3, 0.2 + dy * 0.6, 0.85), WOOD_D(), rot=(R(-dy * 50), 0, 0), bevel=0.01)
            for y in (-0.38, 0.38):
                C.wheel(sx * 0.45, y, 0.18, 0.17, WOOD_D(), SAND_D(), GOLD())
        for y in (-0.45, 0.45):
            box((0.78, 0.09, 0.09), (0, y, 0.3), WOOD(), bevel=0.015)
        cyl(0.05, 0.05, 0.75, (0, 0.2, 1.33), GOLD(), rot=(0, R(90), 0))       # eje
        # Toldo a rayas
        for k in range(5):
            box((0.16, 0.7, 0.03), (-0.32 + k * 0.16, -0.25, 0.95), [K.TRIBU, LINEN][k % 2](), rot=(R(12), 0, 0), bevel=0.0)
        for sx in (-1, 1):
            cyl(0.025, 0.025, 0.7, (sx * 0.38, -0.55, 0.6), WOOD_D())
        box((0.7, 0.05, 0.18), (0, -0.5, 0.42), K.TRIBU(), bevel=0.01)
        sphere(0.06, (0, -0.53, 0.42), GOLD(), (1, 0.5, 1))

    def arm():
        box((0.08, 0.08, 1.1), (0, 0.52, 0.62), WOOD_D(), rot=(R(-60), 0, 0), bevel=0.015)
        box((0.32, 0.3, 0.3), (0, 0.2, 0.36), SAND(), bevel=0.04)             # contrapeso
        for k in range(3):
            box((0.34, 0.31, 0.02), (0, 0.2, 0.26 + k * 0.1), SAND_D(), bevel=0.0)
        sphere(0.14, (0, 0.95, 0.88), K.LEATHER(), (1, 1, 0.45))
        sphere(0.12, (0, 0.95, 0.96), mat("Roca", "c2a77a", 0.9), sub=1)

    def operator():
        on("head", turban, gem=False)
        on("hips", kilt)
    return C.siege("Trabuquete", "Ranger", BODY, frame, arm, operator, recolor=RECOLOR, team_only=TEAM)


def capitan_desierto():
    """Capitán: turbante grande con pluma, chaleco y sable curvo con garfio."""
    L.reset("Capitan_desierto")
    setup()

    def head():
        turban()
        sphere(0.09, (0.25, -0.35, 2.3), LINEN(), (0.4, 0.3, 2.0), rot=(R(-25), R(20), 0))

    def face():
        sphere(0.11, (-0.21, -0.55, 1.62), BLACK(), (1, 0.35, 1))          # parche
        for sx in (-1, 1):
            torus(0.06, 0.015, (sx * 0.58, -0.02, 1.45), GOLD(), rot=(0, R(90), 0))
    on("head", head)
    on("head", face)

    def vest():
        for sx in (-1, 1):
            box((0.22, 0.06, 0.5), (sx * 0.2, -0.33, 0.9), K.TRIBU(), rot=(0, 0, R(sx * -6)), bevel=0.03)
            box((0.03, 0.065, 0.48), (sx * 0.1, -0.34, 0.9), GOLD(), bevel=0.0)
    on("chest", vest)
    on("hips", kilt, z_top=0.62, z_bot=0.2, r=0.37)
    L.finalize()
    C.arma("capitan_desierto", "cimitarra", "handslot.r")
    C.arma("capitan_desierto", "garfio", "handslot.l")
    return L.export("capitan_desierto")


def barco_desierto():
    """Barco: falucho de papiro con vela latina triangular y el ojo de Horus en la proa."""
    def build():
        PAPYRUS = lambda: mat("Papiro", "c9b56a", 0.8)
        PAPYRUS_D = lambda: mat("PapiroOscuro", "8f7a3a", 0.8)
        h = C.hull(0.62, 1.55, 0.55, PAPYRUS(), z=0.55, sharp=0.55, raise_bow=0.35)
        for k in range(7):                                  # atados de papiro
            box((1.26 * (1 - abs(k - 3) * 0.07), 0.07, 0.06), (0, -1.1 + k * 0.37, 0.62), PAPYRUS_D(), bevel=0.02)
        # proa y popa curvas hacia arriba
        tube([(0, -1.4, 0.75), (0, -1.75, 1.05), (0, -1.75, 1.45), (0, -1.6, 1.6)], 0.11, PAPYRUS())
        tube([(0, 1.4, 0.75), (0, 1.8, 1.0), (0, 1.9, 1.45), (0, 1.75, 1.7)], 0.11, PAPYRUS())
        sphere(0.12, (0, -1.6, 1.62), K.TRIBU(), (1, 1, 0.8))
        sphere(0.14, (0, 1.75, 1.72), K.TRIBU(), (1, 1, 0.8))
        for sx in (-1, 1):                                   # ojo de Horus
            sphere(0.08, (sx * 0.3, -1.25, 0.82), K.WHITE(), (0.3, 1.4, 0.8))
            sphere(0.05, (sx * 0.33, -1.25, 0.82), BLACK(), (0.3, 1, 1))
            tube([(sx * 0.32, -1.1, 0.74), (sx * 0.31, -1.18, 0.68), (sx * 0.29, -1.28, 0.7)], 0.015, BLACK())
        d = cyl(1.0, 1.0, 0.04, (0, 0, 0.58), mat("Cubierta", "a07a45", 0.8), v=40)
        d.scale = (0.55, 1.35, 1)
        # Cabina con toldo a rayas
        box((0.7, 0.6, 0.35), (0, 0.65, 0.78), mat("MaderaClara", "c9a26a", 0.75), bevel=0.04)
        for k in range(5):
            box((0.16, 0.75, 0.03), (-0.32 + k * 0.16, 0.65, 1.0), [K.TRIBU, LINEN][k % 2](), bevel=0.0)
        # Mástil y vela latina (triangular)
        cyl(0.06, 0.05, 2.8, (0, -0.15, 1.95), mat("MaderaDesierto", "8a6236", 0.8))
        tube([(0, 1.25, 0.95), (0, -0.15, 2.4), (0, -1.6, 3.6)], 0.04, mat("MaderaDesierto", "8a6236", 0.8),
             smooth_curve=False)
        C.flat_sail([(0, 1.15, 1.05), (0, -1.5, 3.5), (0, -0.9, 0.95)], K.TRIBU())
        C.flat_sail([(0.03, 0.55, 1.35), (0.03, -0.75, 2.6), (0.03, -0.55, 1.3)], LINEN())
        box((0.03, 0.34, 0.18), (0, -1.45, 3.7), K.TRIBU(), bevel=0.0)
        # remos
        for sx in (-1, 1):
            for y in (-0.5, 0.0):
                tube([(sx * 0.55, y, 0.65), (sx * 1.05, y + 0.15, 0.15)], 0.025, mat("MaderaDesierto", "8a6236", 0.8),
                     smooth_curve=False)
    return C.static_model("Barco_desierto", build)


# ---------------------------------------------------------------------------------------
# Héroes

def anubis():
    """Anubis: cuerpo fuerte, cabeza de chacal negro con orejas altas, collar, faldellín
    y cetro de oro. Ataca a distancia; si mata a un enemigo, lo vuelve momia aliada."""
    L.reset("Anubis")
    L.recolor({(0, 0): "6a4228", (0, 1): "5a3420", (2, 2): "efe6cf", (2, 3): "d9cfb0"})
    L.S["team_only"] = []
    L.load_char("Barbarian", ["ArmLeft", "ArmRight", "Body", "LegLeft", "LegRight"])
    FUR = lambda: mat("Chacal", "1e1a1c", 0.6)
    FUR_L = lambda: mat("ChacalClaro", "34303a", 0.6)

    def jackal():
        sphere(0.5, (0, 0.04, 1.72), FUR(), (0.95, 1.0, 1.0), sub=1)
        # hocico largo
        sphere(0.24, (0, -0.55, 1.58), FUR(), (0.8, 1.6, 0.75), rot=(R(8), 0, 0), sub=1)
        sphere(0.07, (0, -0.92, 1.6), BLACK(), (1.1, 0.8, 0.8))
        box((0.18, 0.08, 0.04), (0, -0.85, 1.47), mat("Boca", "8a3a2a"), bevel=0.02)
        # ojos dorados delineados
        for sx in (-1, 1):
            sphere(0.09, (sx * 0.2, -0.4, 1.82), mat("OjoAnubis", "ffd23f", 0.2), (0.9, 0.5, 0.6))
            sphere(0.04, (sx * 0.21, -0.45, 1.82), BLACK(), (1, 0.5, 1))
            tube([(sx * 0.1, -0.44, 1.82), (sx * 0.3, -0.42, 1.83), (sx * 0.42, -0.3, 1.78)], 0.018, GOLD())
            # orejas altas
            cyl(0.17, 0.0, 0.6, (sx * 0.26, 0.05, 2.38), FUR(), rot=(R(-8), R(sx * 12), 0), v=4)
            cyl(0.1, 0.0, 0.42, (sx * 0.26, -0.03, 2.33), mat("OrejaInterior", "c9726a", 0.6),
                rot=(R(-8), R(sx * 12), 0), v=4)
        # tocado a rayas detrás de la cabeza
        for sx in (-1, 1):
            for k in range(4):
                m = K.TRIBU if k % 2 == 0 else GOLD
                box((0.26, 0.1, 0.09), (sx * 0.45, 0.05, 1.5 - k * 0.09), m(), rot=(0, 0, R(sx * 6)), bevel=0.02)
        box((0.5, 0.12, 0.1), (0, 0.48, 1.62), GOLD(), bevel=0.03)
    on("head", jackal)
    on("chest", collar)
    on("hips", kilt, z_top=0.6, z_bot=0.22, r=0.4)
    for sx, bone in ((1, "lowerarm.l"), (-1, "lowerarm.r")):
        def bracer(sx=sx):
            cyl(0.11, 0.11, 0.2, (sx * 0.62, 0, 1.05), GOLD(), rot=(0, R(90), 0))
            torus(0.11, 0.02, (sx * 0.62, 0, 1.05), LAPIS(), rot=(0, R(90), 0))
        on(bone, bracer)
    L.finalize()
    C.arma("anubis", "cetro_ankh", "handslot.r")
    return L.export("anubis")


def momia():
    """Momia: tropa básica que aparece cuando Anubis mata a un enemigo. Vendas, ojos
    brillantes del color de la tribu. No ocupa vivienda y tiene poca vida."""
    L.reset("Momia")
    BAND = "c9b98e"
    L.recolor({(1, 2): BAND, (1, 3): "b8ad8a", (2, 4): "c4b894", (2, 5): "a89c78", (2, 2): BAND, (2, 3): "b8ad8a",
               (0, 2): BAND, (0, 3): "a89c78"})
    L.S["team_only"] = [(1, 4), (1, 5)]          # ojos
    L.load_char("Skeleton_Warrior", ["ArmLeft", "ArmRight", "Body", "Head", "Jaw", "Eyes", "LegLeft", "LegRight"])
    BANDAGE = lambda: mat("Venda", "d2c49c", 0.85)
    BANDAGE_D = lambda: mat("VendaOscura", "a89a70", 0.85)

    def head_wraps():
        for k, (z, tilt) in enumerate(((1.62, 12), (1.78, -10), (1.95, 8))):
            t = torus(0.44, 0.05, (0, 0.0, z), [BANDAGE, BANDAGE_D][k % 2](), rot=(R(tilt), 0, 0))
            t.scale = (1, 1.05, 1)
        tube([(0.35, 0.3, 1.7), (0.5, 0.55, 1.45), (0.45, 0.62, 1.2)], 0.04, BANDAGE())
    on("head", head_wraps)

    def body_wraps():
        for k in range(4):
            t = torus(0.3, 0.045, (0, 0, 0.75 + k * 0.12), [BANDAGE, BANDAGE_D][k % 2](), rot=(R(10 - 6 * k), 0, 0))
        tube([(-0.2, -0.28, 0.95), (-0.35, -0.3, 0.6), (-0.3, -0.25, 0.4)], 0.035, BANDAGE())
    on("chest", body_wraps)
    for sx, bone in ((1, "upperarm.l"), (-1, "upperarm.r"), (1, "lowerarm.l"), (-1, "lowerarm.r")):
        def arm_wrap(sx=sx, bone=bone):
            x = sx * (0.42 if "upper" in bone else 0.62)
            for k in range(2):
                torus(0.09, 0.03, (x + sx * k * 0.08, 0, 1.08), BANDAGE(), rot=(R(15), R(90), 0))
        on(bone, arm_wrap)
    L.finalize()
    return L.export("momia")


def golem():
    """Gólem de arena (héroe criatura): bloques de arenisca, runas que brillan del color
    de la tribu. Rueda en línea recta y empuja a la tropa que golpea."""
    def build():
        STONE = SAND
        STONE_D = SAND_D
        RUNE = K.TRIBU
        # piernas cortas y gruesas
        for sx in (-1, 1):
            box((0.42, 0.46, 0.55), (sx * 0.32, 0.05, 0.28), STONE_D(), bevel=0.1)
            box((0.48, 0.55, 0.16), (sx * 0.32, -0.02, 0.08), STONE(), bevel=0.06)
        # torso enorme
        box((1.25, 0.85, 0.9), (0, 0.05, 1.05), STONE(), bevel=0.16)
        box((1.0, 0.72, 0.4), (0, 0.05, 0.55), STONE_D(), bevel=0.12)
        box((1.45, 0.95, 0.42), (0, 0.08, 1.48), STONE_D(), bevel=0.14)          # hombros
        # runas brillantes en el pecho y un escarabajo de oro
        for (x, z, w, h) in ((-0.3, 1.1, 0.06, 0.32), (0.3, 1.1, 0.06, 0.32), (0, 0.9, 0.42, 0.06),
                             (-0.18, 1.25, 0.16, 0.05), (0.18, 1.25, 0.16, 0.05)):
            box((w, 0.04, h), (x, -0.4, z), RUNE(), bevel=0.01)
        sphere(0.16, (0, -0.42, 1.12), GOLD(), (1.0, 0.45, 1.25), sub=1)
        sphere(0.08, (0, -0.48, 1.3), LAPIS(), (1.1, 0.5, 0.7))
        for sx in (-1, 1):
            sphere(0.07, (sx * 0.16, -0.45, 1.12), LAPIS(), (1.3, 0.4, 2.0), rot=(0, R(sx * 20), 0))
        # brazos de piedra apilada con puños enormes
        for sx in (-1, 1):
            box((0.42, 0.45, 0.42), (sx * 0.85, 0.08, 1.45), STONE(), bevel=0.1)
            box((0.36, 0.4, 0.5), (sx * 0.92, 0.0, 1.0), STONE_D(), bevel=0.1)
            box((0.5, 0.52, 0.48), (sx * 0.95, -0.08, 0.5), STONE(), bevel=0.14)
            box((0.06, 0.4, 0.06), (sx * 0.95, -0.35, 0.6), RUNE(), bevel=0.01)
        # cabeza pequeña con ojos que brillan y tocado
        box((0.5, 0.45, 0.42), (0, -0.05, 1.92), STONE(), bevel=0.1)
        for sx in (-1, 1):
            box((0.13, 0.04, 0.07), (sx * 0.12, -0.28, 1.95), RUNE(), bevel=0.01)
        for sx in (-1, 1):
            for k in range(3):
                m = K.TRIBU if k % 2 == 0 else GOLD
                box((0.16, 0.1, 0.08), (sx * 0.3, -0.05, 1.82 - k * 0.08), m(), bevel=0.02)
        box((0.55, 0.5, 0.06), (0, -0.04, 2.15), GOLD(), bevel=0.02)
        # arena que cae y piedras sueltas
        for k, (x, y, z) in enumerate(((0.55, -0.45, 0.06), (-0.6, -0.4, 0.05), (0.2, -0.6, 0.04), (-0.25, 0.55, 0.05))):
            sphere(0.09 + k * 0.01, (x, y, z), STONE_D(), (1, 1, 0.6), sub=1)
    return C.static_model("Golem_arena", build)


# ---------------------------------------------------------------------------------------
# Armas

def _khopesh():
    import bpy
    pts = []
    blade = lambda: mat("BronceHoja", "d9a050", 0.3, 0.85)
    cyl(0.045, 0.045, 0.3, (0, 0, 0.0), K.LEATHER_D())
    sphere(0.06, (0, 0, -0.16), GOLD())
    box((0.06, 0.06, 0.4), (0, 0, 0.35), blade(), bevel=0.01)
    tube([(0, 0, 0.5), (0.05, 0, 0.75), (0.22, 0, 0.92), (0.4, 0, 0.82), (0.42, 0, 0.6)], 0.06, blade())
    torus(0.06, 0.02, (0, 0, 0.17), GOLD(), rot=(0, 0, 0))


def _lanza_desierto(length=2.4):
    cyl(0.05, 0.05, length, (0, 0, length / 2 - 0.9), mat("MaderaDesierto", "8a6236", 0.8))
    top = length - 0.9
    cyl(0.12, 0.0, 0.45, (0, 0, top + 0.2), GOLD(), v=4, rot=(0, 0, R(45)))
    for k in range(3):
        torus(0.06, 0.02, (0, 0, top - 0.06 - k * 0.07), [K.TRIBU, LAPIS, K.TRIBU][k]())


def _escudo_horus():
    grp = []
    grp.append(box((0.62, 0.06, 0.85), (0, 0, -0.05), LINEN(), bevel=0.03))
    grp.append(sphere(0.31, (0, 0, 0.37), LINEN(), (1, 0.1, 0.7)))
    grp.append(box((0.66, 0.05, 0.05), (0, -0.03, -0.48), GOLD(), bevel=0.01))
    for sx in (-1, 1):
        grp.append(box((0.05, 0.05, 0.85), (sx * 0.32, -0.03, -0.05), GOLD(), bevel=0.01))
    grp.append(box((0.5, 0.05, 0.22), (0, -0.04, -0.3), K.TRIBU(), bevel=0.01))
    # Ojo de Horus
    grp.append(sphere(0.1, (0, -0.05, 0.18), K.WHITE(), (1.5, 0.3, 0.8)))
    grp.append(sphere(0.06, (0, -0.07, 0.18), LAPIS(), (1, 0.4, 1)))
    grp.append(tube([(-0.18, -0.06, 0.28), (0, -0.07, 0.32), (0.2, -0.06, 0.27)], 0.02, BLACK()))
    grp.append(tube([(0.0, -0.06, 0.1), (-0.02, -0.06, -0.02), (0.06, -0.06, -0.08)], 0.02, BLACK()))
    K._group(grp, (0, 0, 0), (0, 0, 0))


def _arco_compuesto():
    wood = lambda: mat("MaderaDesierto", "8a6236", 0.8)
    tube([(0.06, 0, -0.72), (0.0, 0, -0.55), (0.24, 0, -0.25), (0.26, 0, 0.0), (0.24, 0, 0.25), (0.0, 0, 0.55),
          (0.06, 0, 0.72)], 0.04, wood())
    tube([(0.06, 0, -0.72), (0.06, 0, 0.72)], 0.008, K.WHITE(), smooth_curve=False)
    for z in (-0.12, 0.12):
        torus(0.05, 0.015, (0.26, 0, z), GOLD(), rot=(R(90), 0, 0))
    torus(0.05, 0.02, (0.26, 0, 0.0), K.TRIBU(), rot=(R(90), 0, 0))


def _cimitarra():
    import bpy
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=2, y_subdivisions=12, size=1)
    o = bpy.context.object
    for v in o.data.vertices:
        t = v.co.y + 0.5
        w = 0.1 * (1 + 0.6 * t) * (1 - t ** 6)
        x = v.co.x * 2 * w + 0.32 * t ** 2
        v.co = (x, 0, 0.22 + t * 1.05)
    K._fin(o, K.STEEL(), smooth=False)
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.035; md.offset = 0
    box((0.32, 0.07, 0.05), (0, 0, 0.19), GOLD(), bevel=0.02)
    cyl(0.045, 0.045, 0.3, (0, 0, 0.02), K.TRIBU())
    sphere(0.06, (0, 0, -0.15), GOLD())


def _cetro_ankh():
    cyl(0.045, 0.045, 1.9, (0, 0, 0.35), GOLD())
    for k in range(5):
        torus(0.05, 0.015, (0, 0, -0.4 + k * 0.35), LAPIS())
    # Ankh arriba
    box((0.08, 0.06, 0.3), (0, 0, 1.45), GOLD(), bevel=0.02)
    box((0.36, 0.06, 0.08), (0, 0, 1.6), GOLD(), bevel=0.02)
    t = torus(0.12, 0.04, (0, 0, 1.78), GOLD(), rot=(R(90), 0, 0))
    t.scale = (0.8, 1, 1.15)
    sphere(0.06, (0, 0, 1.6), K.TRIBU())


def armas():
    return [L.export_custom_weapon("khopesh", _khopesh),
            L.export_custom_weapon("lanza_desierto", _lanza_desierto),
            L.export_custom_weapon("lanza_desierto_larga", lambda: _lanza_desierto(3.4)),
            L.export_custom_weapon("escudo_horus", _escudo_horus),
            L.export_custom_weapon("arco_compuesto", _arco_compuesto),
            L.export_custom_weapon("cimitarra", _cimitarra),
            L.export_custom_weapon("cetro_ankh", _cetro_ankh)]


TROPAS = {"caballero": guerrero_nilo, "escudero": guardia_templo, "arquero": arquero_dunas,
          "jinete": jinete_camello, "jinete_lancero": lancero_camello, "catapulta": trebuchet,
          "capitan": capitan_desierto, "barco": barco_desierto, "heroe_1": golem, "heroe_2": anubis,
          "invocada": momia}


def todas():
    C.tribu("desierto")
    print(armas())
    for f in TROPAS.values():
        print(f.__name__, f())
    C.save_weapons({"nombre": "Desierto", "tropas": {k: f.__name__ for k, f in TROPAS.items()}})
