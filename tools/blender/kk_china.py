# Tribu China: armaduras laqueadas del color de la tribu con oro, cascos con borla
# roja, sombreros cónicos de bambú y estandartes. Montan caballos con arreos chinos.
# Héroes: el Dragón (vuela y quema) y Sun Wukong, el rey mono (y su copia).
import math
import kolonia_lib as K
import kk_lib as L
import kk_tribus_comun as C
from kolonia_lib import R, sphere, cyl, box, torus, tube, mat
from kk_tropas import on, Part

BODY = C.BODY
SKIN = "e3a97e"
GOLD = K.GOLD
JADE = lambda: mat("Jade", "2fa58f", 0.4)
LACQUER = lambda: mat("Laca", "1e1a1a", 0.3)
SILK = lambda: mat("Seda", "f2ecdf", 0.6)
BAMBOO = lambda: mat("Bambu", "c9a95a", 0.7)
BAMBOO_D = lambda: mat("BambuOscuro", "8a7034", 0.75)
TASSEL = lambda: mat("Borla", "d8202a", 0.7)
# Caballero (Knight): armadura (3,0/3,1) del color de la tribu, ribetes (7,0) de oro,
# cinturón (6,0) negro, cuello (4,0) de seda.
RECOLOR_KNIGHT = {(0, 0): SKIN, (0, 1): SKIN, (7, 0): "e0b040", (7, 1): "b08a2a", (6, 0): "1e1a1a",
                  (6, 1): "141010", (4, 0): "f2ecdf", (4, 1): "d8d0c0", (2, 0): "1c1714", (2, 1): "1c1714"}
TEAM_KNIGHT = [(3, 0), (3, 1)]
# Ranger: túnica (6,0) de seda, pañuelo (0,2) del color de la tribu
RECOLOR = {(0, 0): SKIN, (0, 1): SKIN, (1, 0): "1c1714", (1, 1): "1c1714",
           (6, 0): "f2ecdf", (6, 1): "d8d0c0", (1, 4): "1e1a1a", (1, 5): "141010"}
TEAM = [(0, 2), (0, 3)]


def setup_knight(keep=None):
    L.recolor(RECOLOR_KNIGHT)
    L.S["team_only"] = TEAM_KNIGHT
    L.load_char("Knight", keep or BODY)


def setup(char="Ranger", keep=None):
    L.recolor(RECOLOR)
    L.S["team_only"] = TEAM
    L.load_char(char, keep or (BODY + ["Cape"]))


def helmet(big=False):
    """Casco chino: laca negra con borde de oro, punta y borla roja, cubrenuca."""
    k = 1.06 if big else 1.0
    C.cap(LACQUER, r=0.67 * k, front_z=1.95, back_z=1.4, rim=GOLD, rim_r=0.05)
    cyl(0.12, 0.08, 0.16, (0, 0.02, 2.28 * k ** 0.2 + 0.0), GOLD(), v=12)
    cyl(0.03, 0.0, 0.3, (0, 0.02, 2.5), GOLD(), v=8)
    for kk in range(7):                                          # borla roja
        a = kk * math.tau / 7
        sphere(0.07, (math.cos(a) * 0.08, 0.02 + math.sin(a) * 0.08, 2.32), TASSEL(), (0.6, 0.6, 1.6), sub=1)
    sphere(0.12, (0, 0.02, 2.38), TASSEL(), sub=1)
    for sx in (-1, 1):                                          # protectores
        box((0.08, 0.36, 0.42), (sx * 0.58 * k, 0.05, 1.55), LACQUER(), rot=(0, 0, R(sx * 6)), bevel=0.03)
        box((0.09, 0.37, 0.04), (sx * 0.58 * k, 0.05, 1.36), GOLD(), bevel=0.01)
    box((0.7, 0.12, 0.38), (0, 0.55, 1.45), LACQUER(), rot=(R(-12), 0, 0), bevel=0.04)    # cubrenuca
    box((0.12, 0.05, 0.1), (0, -0.62, 1.95), GOLD(), bevel=0.02)
    if big:
        for sx in (-1, 1):
            box((0.05, 0.2, 0.38), (sx * 0.3, -0.45, 2.15), GOLD(), rot=(0, R(sx * -20), 0), bevel=0.02)


def conical_hat(size=1.0):
    """Sombrero cónico de bambú (douli)."""
    s = size
    C.cap(K.TRIBU, r=0.62, front_z=1.95, back_z=1.6)
    z0 = 2.12
    cyl(0.85 * s, 0.05, 0.42 * s, (0, 0.02, z0 + 0.21 * s), BAMBOO(), v=32)
    for k in range(4):
        torus(0.2 + k * 0.17 * s, 0.015, (0, 0.02, z0 + 0.4 * s - k * 0.1 * s), BAMBOO_D())
    sphere(0.06, (0, 0.02, z0 + 0.43 * s), K.TRIBU())
    for sx in (-1, 1):                                            # cinta bajo la barbilla
        tube([(sx * 0.48, 0.0, 1.92), (sx * 0.4, -0.25, 1.4), (0, -0.4, 1.22)], 0.015, K.TRIBU())


def sash(z=0.62, r=0.36):
    cyl(r + 0.02, r + 0.02, 0.12, (0, 0, z), K.TRIBU(), v=24)
    sphere(0.08, (0.2, -r, z), K.TRIBU(), sub=1)
    tube([(0.2, -r - 0.02, z - 0.02), (0.25, -r - 0.05, z - 0.3)], 0.04, K.TRIBU())
    tube([(0.17, -r - 0.02, z - 0.02), (0.12, -r - 0.05, z - 0.27)], 0.04, K.TRIBU())
    box((0.12, 0.05, 0.1), (0, -r - 0.02, z), GOLD(), bevel=0.02)


def back_flag():
    """Estandarte a la espalda (como los generales de la ópera china)."""
    cyl(0.025, 0.025, 1.0, (0, 0.38, 1.55), LACQUER())
    box((0.32, 0.02, 0.5), (0.0, 0.42, 1.8), K.TRIBU(), bevel=0.0)
    cyl(0.0, 0.18, 0.12, (0, 0.42, 1.5), GOLD(), v=3, rot=(R(90), 0, 0))
    sphere(0.05, (0, 0.38, 2.08), GOLD())


# ---------------------------------------------------------------------------------------
# Tropas

def guardia_imperial():
    """Caballero: armadura laqueada, casco con borla y espada dao."""
    L.reset("Guardia_imperial")
    setup_knight(BODY + ["Cape"])
    on("head", helmet)
    L.finalize()
    C.arma("guardia_imperial", "dao", "handslot.r")
    return L.export("guardia_imperial")


def guardia_tigre():
    """Escudero: casco grande con alas, escudo redondo de mimbre con cara de tigre y alabarda."""
    L.reset("Guardia_tigre")
    setup_knight()
    on("head", helmet, True)
    for sx, bone in ((1, "upperarm.l"), (-1, "upperarm.r")):
        def pad(sx=sx):
            sphere(0.24, (sx * 0.42, 0, 1.2), GOLD(), (1.05, 1.0, 0.7), sub=1)
            sphere(0.08, (sx * 0.55, -0.12, 1.15), K.TRIBU(), (0.6, 1, 1))
        on(bone, pad)
    on("chest", back_flag)
    L.finalize()
    C.arma("guardia_tigre", "alabarda", "handslot.r")
    C.arma("guardia_tigre", "escudo_tigre", "handslot.l")
    return L.export("guardia_tigre")


def ballestero():
    """Arquero: sombrero cónico de bambú y ballesta de repetición."""
    L.reset("Ballestero")
    setup()
    on("head", conical_hat)
    on("hips", sash)
    L.finalize()
    C.arma("ballestero", "ballesta_repeticion", "handslot.l", (0, 0, 180))
    return L.export("ballestero")


def _china_horse(armor=False):
    coat = mat("CaballoBlanco", "eee6d8", 0.7) if not armor else mat("CaballoNegro", "2a2626", 0.7)
    mane = mat("CrinNegra", "1c1714", 0.8) if not armor else mat("CrinRoja", "a8302a", 0.8)
    seat, bones = C.caballo(coat, mane, mat("Hocico", "c9b8a8", 0.8) if not armor else mat("HocicoGris", "4a4242", 0.8),
                            armor=armor, blaze=not armor)
    # Adornos: borla roja en la frente y borlas que cuelgan de la manta
    with Part("cabeza_c"):
        for k in range(5):
            a = k * math.tau / 5
            sphere(0.06, (math.cos(a) * 0.06, -0.95 + math.sin(a) * 0.06, 2.4), TASSEL(), (0.6, 0.6, 1.6))
        sphere(0.09, (0, -0.95, 2.44), TASSEL(), sub=1)
    with Part("caballo"):
        for sx in (-1, 1):
            for y in (-0.25, 0.1, 0.45):
                sphere(0.05, (sx * 0.52, y, 1.5), GOLD())
                cyl(0.035, 0.06, 0.16, (sx * 0.52, y, 1.38), TASSEL(), v=8)
    return seat, bones


def jinete_chino():
    """Jinete: caballo blanco con arreos rojos y dorados, jinete con casco de borla."""
    def head():
        on("head", helmet)
    path = C.rider("Jinete_chino", "Knight", BODY + ["Cape"], lambda: _china_horse(False), False,
                   headgear=head, recolor=RECOLOR_KNIGHT, team_only=TEAM_KNIGHT)
    C.arma("jinete_chino", "dao", "handslot.r")
    return path


def lancero_chino():
    """Jinete lancero: general con estandarte sobre caballo acorazado, con guandao."""
    def head():
        on("head", helmet, True)

    def extra():
        on("chest", back_flag)
    path = C.rider("Lancero_chino", "Knight", BODY, lambda: _china_horse(True), True,
                   headgear=head, extra=extra, recolor=RECOLOR_KNIGHT, team_only=TEAM_KNIGHT)
    C.arma("lancero_chino", "guandao", "handslot.r")
    return path


def lanzacohetes():
    """Catapulta: carro lanzacohetes; el armazón de tubos se inclina al disparar."""
    WOOD = lambda: mat("MaderaRoja", "8a2e22", 0.7)
    WOOD_D = lambda: mat("MaderaRojaOscura", "5a1a14", 0.75)

    def frame():
        for sx in (-1, 1):
            box((0.08, 1.15, 0.1), (sx * 0.35, 0, 0.3), WOOD(), bevel=0.015)
            for y in (-0.38, 0.38):
                C.wheel(sx * 0.45, y, 0.18, 0.17, LACQUER(), GOLD(), GOLD())
            box((0.08, 0.08, 0.5), (sx * 0.3, 0.2, 0.55), WOOD_D(), bevel=0.01)
        for y in (-0.45, 0.45):
            box((0.78, 0.09, 0.09), (0, y, 0.3), WOOD(), bevel=0.015)
        box((0.7, 0.05, 0.18), (0, -0.5, 0.42), K.TRIBU(), bevel=0.01)
        for x in (-0.22, 0.22):
            sphere(0.05, (x, -0.53, 0.42), GOLD())
        cyl(0.04, 0.04, 0.7, (0, 0.2, 0.78), GOLD(), rot=(0, R(90), 0))      # eje del armazón
        for k in range(3):                                                   # cohetes de repuesto
            cyl(0.03, 0.03, 0.5, (-0.15 + k * 0.15, 0.45, 0.42), BAMBOO(), rot=(R(90), 0, 0))

    def arm():
        # armazón de tubos para cohetes, apuntando hacia adelante y arriba
        box((0.62, 0.12, 0.5), (0, 0.3, 1.0), WOOD(), rot=(R(-30), 0, 0), bevel=0.02)
        for i in range(4):
            for j in range(3):
                x = -0.22 + i * 0.147
                z = 0.88 + j * 0.13
                cyl(0.035, 0.035, 0.25, (x, 0.22 - j * 0.075, z), LACQUER(), rot=(R(60), 0, 0), v=8)
                cyl(0.0, 0.035, 0.06, (x, 0.09 - j * 0.075, z + 0.08), K.TRIBU(), rot=(R(60), 0, 0), v=8)

    def operator():
        on("head", conical_hat, 0.9)
        on("hips", sash)
    return C.siege("Lanzacohetes", "Ranger", BODY, frame, arm, operator, recolor=RECOLOR, team_only=TEAM,
                   arm_bone=("brazo_cat", (0, 0.2 * 2.0, 0.78 * 2.0), (0, 0.0, 1.2 * 2.0), None))


def capitan_chino():
    """Capitán: sombrero cónico grande, bigote largo, faja y dao con garfio."""
    L.reset("Capitan_chino")
    setup()

    def head():
        conical_hat(1.15)
        sphere(0.11, (-0.21, -0.55, 1.62), K.BLACK(), (1, 0.35, 1))        # parche
        for sx in (-1, 1):
            tube([(sx * 0.06, -0.58, 1.48), (sx * 0.25, -0.58, 1.42), (sx * 0.32, -0.55, 1.2)], 0.025, K.BLACK())
    on("head", head)
    on("hips", sash, 0.62, 0.38)
    L.finalize()
    C.arma("capitan_chino", "dao", "handslot.r")
    C.arma("capitan_chino", "garfio", "handslot.l")
    return L.export("capitan_chino")


def junco():
    """Barco: junco chino con velas de listones, popa alta y un ojo pintado en la proa."""
    def build():
        WOOD = lambda: mat("CascoJunco", "6e3a22", 0.8)
        WOOD_L = lambda: mat("CubiertaJunco", "b07a45", 0.8)
        C.hull(0.66, 1.55, 0.6, WOOD(), z=0.6, sharp=0.3, raise_bow=0.1)
        import kk_tropas as T
        T._ring(0.64, 1.5, 0.22, 0.72, mat("MaderaRoja", "8a2e22", 0.7), thick=0.05)
        t = torus(1.0, 0.04, (0, 0, 0.5), GOLD()); t.scale = (0.64, 1.52, 1)
        d = cyl(1.0, 1.0, 0.04, (0, 0, 0.62), WOOD_L(), v=40); d.scale = (0.6, 1.45, 1)
        # popa alta con techo curvo
        box((1.1, 0.7, 0.55), (0, 1.0, 0.95), mat("MaderaRoja", "8a2e22", 0.7), bevel=0.05)
        box((1.25, 0.85, 0.08), (0, 1.0, 1.26), LACQUER(), bevel=0.03)
        for sx in (-1, 1):
            cyl(0.04, 0.0, 0.25, (sx * 0.62, 1.0, 1.34), LACQUER(), rot=(0, R(sx * -60), 0), v=8)
        for x in (-0.3, 0.0, 0.3):
            box((0.16, 0.04, 0.18), (x, 0.64, 1.0), mat("Ventana", "f6d27a", 0.3), bevel=0.02)
        # ojos en la proa
        for sx in (-1, 1):
            sphere(0.12, (sx * 0.42, -1.15, 0.65), K.WHITE(), (0.25, 1, 1))
            sphere(0.07, (sx * 0.44, -1.17, 0.65), K.BLACK(), (0.25, 1, 1))
        # velas de listones (forma de abanico)
        for y, h, w in ((-0.75, 1.6, 0.95), (0.05, 2.2, 1.25), (0.8, 1.4, 0.8)):
            cyl(0.05, 0.04, h + 0.4, (0, y, 0.6 + (h + 0.4) / 2), WOOD())
            top = 0.6 + h + 0.3
            C.flat_sail([(-w * 0.45, y + 0.04, top), (w * 0.5, y + 0.04, top - 0.1), (w * 0.55, y + 0.04, 0.95),
                         (-w * 0.5, y + 0.04, 0.95)], K.TRIBU())
            for k in range(5):
                z = 0.95 + k * (top - 0.95) / 4
                cyl(0.02, 0.02, w * 1.1, (0.03, y + 0.07, z), LACQUER(), rot=(0, R(90), 0))
            box((0.03, 0.3, 0.16), (0, y + 0.16, top + 0.15), K.TRIBU(), bevel=0.0)
        # farolillos
        for sx in (-1, 1):
            sphere(0.08, (sx * 0.5, 1.4, 1.05), mat("Farol", "e8402a", 0.4), (1, 1, 1.2))
            cyl(0.04, 0.04, 0.04, (sx * 0.5, 1.4, 1.15), GOLD())
    return C.static_model("Junco", build)


# ---------------------------------------------------------------------------------------
# Héroes

def dragon():
    """Dragón (héroe criatura): vuela y ataca con fuego a distancia; la tropa quemada
    vuelve a recibir daño el turno siguiente."""
    def build():
        SC = K.TRIBU
        BELLY = lambda: mat("VientreDragon", "f2c84a", 0.5)
        MANE = lambda: mat("MelenaDragon", "f2ecdf", 0.6)
        HORN = lambda: mat("Cuerno", "e8d6a8", 0.5)
        # Cuerpo largo y ondulado, flotando
        pts = [(0.2, 2.0, 0.75), (0.6, 1.65, 1.0), (0.55, 1.15, 1.3), (0.0, 0.85, 1.05), (-0.5, 0.5, 1.2),
               (-0.55, 0.0, 1.55), (-0.15, -0.35, 1.75), (0.0, -0.6, 1.9)]
        tube(pts, 0.19, SC())
        import mathutils
        curve = [mathutils.Vector(p) for p in pts]
        for i in range(len(curve) - 1):
            for t in (0.3, 0.7):
                p = curve[i].lerp(curve[i + 1], t)
                d = curve[i + 1] - curve[i]
                o = torus(0.185, 0.035, tuple(p), BELLY())
                o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
                # aleta del lomo
                o2 = cyl(0.06, 0.0, 0.18, (p.x, p.y, p.z + 0.21), mat("AletaDragon", "f2ecdf", 0.6), v=6)
        # cola con mechón
        for k in range(6):
            sphere(0.09, (0.2 + 0.04 * (k - 2), 2.1 + k * 0.04, 0.72 - k * 0.03), MANE(), (0.4, 0.4, 1.7),
                   rot=(R(-50 + k * 15), 0, 0))
        # cuatro patas con garras
        for (x, y, z, sx) in ((0.55, 1.2, 1.25, 1), (0.1, 0.85, 1.05, -1), (-0.55, 0.05, 1.5, -1), (-0.1, -0.35, 1.72, 1)):
            foot = (x + sx * 0.32, y - 0.12, z - 0.5)
            tube([(x, y, z), (x + sx * 0.28, y - 0.05, z - 0.18), foot], 0.055, SC())
            for k in range(3):
                cyl(0.025, 0.0, 0.12, (foot[0] + (k - 1) * 0.05, foot[1] - 0.08, foot[2] - 0.04), HORN(),
                    rot=(R(-100), 0, 0), v=6)
        # Cabeza
        hx, hy, hz = 0.0, -0.85, 2.05
        sphere(0.32, (hx, hy, hz), SC(), (0.9, 1.2, 0.85), sub=1)
        sphere(0.24, (hx, hy - 0.35, hz - 0.08), SC(), (0.9, 1.1, 0.7), sub=1)            # hocico
        sphere(0.18, (hx, hy - 0.33, hz - 0.22), BELLY(), (0.9, 1.1, 0.4), sub=1)       # mandíbula
        sphere(0.07, (hx, hy - 0.6, hz - 0.02), GOLD(), (1.2, 0.7, 0.7))                 # nariz
        for sx in (-1, 1):
            sphere(0.08, (sx * 0.17, hy - 0.2, hz + 0.12), mat("OjoDragon", "f2c230", 0.3), (0.9, 0.8, 0.8))
            sphere(0.035, (sx * 0.19, hy - 0.26, hz + 0.13), K.BLACK(), (0.5, 0.6, 1.2))
            # cuernos de ciervo
            tube([(sx * 0.15, hy + 0.15, hz + 0.25), (sx * 0.3, hy + 0.35, hz + 0.55), (sx * 0.28, hy + 0.55, hz + 0.75)],
                 0.04, HORN())
            tube([(sx * 0.27, hy + 0.32, hz + 0.5), (sx * 0.42, hy + 0.3, hz + 0.62)], 0.03, HORN())
            # bigotes largos
            tube([(sx * 0.12, hy - 0.55, hz - 0.02), (sx * 0.45, hy - 0.6, hz - 0.1), (sx * 0.7, hy - 0.4, hz - 0.35)],
                 0.02, GOLD())
            cyl(0.03, 0.0, 0.12, (sx * 0.08, hy - 0.5, hz - 0.28), K.WHITE(), v=8)
        # melena
        for k in range(9):
            a = R(-80 + k * 20)
            o = sphere(0.1, (math.sin(a) * 0.3, hy + 0.25 + math.cos(a) * 0.05, hz + 0.05 + math.cos(a) * 0.12), MANE(),
                       (0.35, 0.35, 1.5), sub=1)
            o.rotation_euler = (R(50), a * 0.6, 0)
        # perla en la garra delantera
        sphere(0.1, (0.55, -0.55, 1.0), mat("Perla", "e8f0ff", 0.15), sub=1)
        # llamita en la boca
        sphere(0.07, (hx, hy - 0.62, hz - 0.18), mat("Fuego", "ff8a1a", 0.3), (1, 1.4, 0.8))
        # Más grande y volando más alto
        from mathutils import Vector
        allo = list(K.C["col"].objects)
        L.scale_objs(allo, 1.35)
        for o in allo:
            o.location += Vector((0, 0, 0.35))
        # sombra de nube bajo el dragón (para que se lea que vuela)
        for k, (x, y) in enumerate(((0.0, 0.3), (0.5, 0.1), (-0.45, 0.2), (0.15, -0.35))):
            sphere(0.32 - k * 0.04, (x, y, 0.18), mat("Nube", "f4f6fa", 0.8), (1.3, 1.0, 0.55), sub=1)
    return C.static_model("Dragon", build)


def sun_wukong(copy=False):
    """Sun Wukong, el rey mono (héroe): cara de mono, diadema de oro, plumas de fénix,
    armadura dorada y bastón. Se mueve, ataca y vuelve a moverse; crea una copia de sí
    mismo (misma figura, en el juego se ve transparente) que no ataca."""
    name = "Sun_wukong" + ("_copia" if copy else "")
    L.reset(name)
    FUR = "b07a45"
    L.recolor({(0, 0): FUR, (0, 1): "8a5a30", (1, 0): "6e4426", (1, 1): "5a3418",
               (6, 0): "e0b040", (6, 1): "b08a2a", (1, 4): "1e1a1a", (1, 5): "141010"})
    L.S["team_only"] = [(0, 2), (0, 3)]
    L.load_char("Ranger", ["ArmLeft", "ArmRight", "Body", "LegLeft", "LegRight", "Cape"])
    FACE = lambda: mat("CaraMono", "f2c8a0", 0.7)
    FURM = lambda: mat("PeloMono", "b07a45", 0.8)

    def head():
        sphere(0.52, (0, 0.04, 1.72), FURM(), (1.0, 0.95, 0.98), sub=1)
        sphere(0.36, (0, -0.28, 1.68), FACE(), (1.05, 0.7, 1.0), sub=1)      # cara
        sphere(0.2, (0, -0.48, 1.52), FACE(), (1.2, 0.8, 0.7), sub=1)        # hocico
        sphere(0.04, (0, -0.64, 1.58), K.BLACK(), (1.4, 0.7, 0.7))
        box((0.2, 0.04, 0.035), (0, -0.6, 1.45), mat("Boca", "8a3a2a"), bevel=0.01)
        for sx in (-1, 1):
            sphere(0.09, (sx * 0.15, -0.5, 1.78), K.WHITE(), (0.9, 0.6, 1.1))
            sphere(0.055, (sx * 0.16, -0.55, 1.78), K.BLACK(), (0.9, 0.6, 1.1))
            sphere(0.02, (sx * 0.18, -0.58, 1.82), K.WHITE())
            box((0.16, 0.04, 0.04), (sx * 0.16, -0.52, 1.92), mat("CejaMono", "6e4426", 0.8),
                rot=(0, R(sx * -15), 0), bevel=0.01)
            sphere(0.14, (sx * 0.52, 0.0, 1.72), FACE(), (0.45, 0.8, 1.0))     # orejas
        # diadema de oro (anillo apretado) y plumas de fénix
        C.brow_band(GOLD, z=1.98, width=0.52, front=-0.5, thick=0.06)
        for sx in (-1, 1):
            sphere(0.06, (sx * 0.5, -0.12, 1.98), GOLD())
            tube([(sx * 0.15, -0.3, 2.05), (sx * 0.35, -0.1, 2.6), (sx * 0.55, 0.4, 3.0), (sx * 0.62, 0.8, 3.1)],
                 0.045, mat("PlumaFenix", "e8402a", 0.5))
            sphere(0.05, (sx * 0.62, 0.82, 3.1), GOLD())
    on("head", head)

    def armor():
        sphere(0.36, (0, -0.02, 0.92), GOLD(), (1.05, 0.85, 0.85), sub=1)
        for k in range(3):
            box((0.5, 0.06, 0.04), (0, -0.3, 0.8 + k * 0.1), mat("OroOscuro", "a8822a", 0.4, 0.7), bevel=0.01)
        # capa roja ondeando
        box((0.8, 0.06, 0.9), (0, 0.4, 0.75), K.TRIBU(), rot=(R(10), 0, 0), bevel=0.04)
    on("chest", armor)

    def skirt():
        cyl(0.36, 0.44, 0.32, (0, 0, 0.44), mat("PielTigre", "e8a030", 0.75), v=24)
        for k in range(8):
            a = k * math.tau / 8
            box((0.05, 0.1, 0.22), (math.cos(a) * 0.41, math.sin(a) * 0.41, 0.42), K.BLACK(),
                rot=(0, 0, a), bevel=0.01)
        cyl(0.38, 0.38, 0.08, (0, 0, 0.62), K.TRIBU(), v=24)
    on("hips", skirt)

    def tail():
        tube([(0, 0.35, 0.5), (0.1, 0.7, 0.4), (0.2, 0.85, 0.75), (0.05, 0.8, 1.05)], 0.05, FURM())
    on("hips", tail)
    L.finalize()
    C.arma(name.lower(), "baston_ruyi", "handslot.r")
    return L.export(name.lower())


# ---------------------------------------------------------------------------------------
# Armas

def _dao():
    import bpy
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=2, y_subdivisions=12, size=1)
    o = bpy.context.object
    for v in o.data.vertices:
        t = v.co.y + 0.5
        w = 0.11 * (1 + 0.8 * t) * (1 - t ** 5)
        x = v.co.x * 2 * w + 0.12 * t ** 2
        v.co = (x, 0, 0.22 + t * 0.95)
    K._fin(o, K.STEEL(), smooth=False)
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.035; md.offset = 0
    cyl(0.1, 0.1, 0.05, (0, 0, 0.19), GOLD(), v=16)
    cyl(0.045, 0.045, 0.3, (0, 0, 0.02), LACQUER())
    sphere(0.06, (0, 0, -0.15), GOLD())
    tube([(0, 0, -0.18), (0.06, 0, -0.3), (0.02, 0, -0.45)], 0.03, TASSEL())


def _alabarda(length=2.5):
    cyl(0.05, 0.05, length, (0, 0, length / 2 - 0.9), LACQUER())
    top = length - 0.9
    cyl(0.08, 0.0, 0.4, (0, 0, top + 0.18), K.STEEL(), v=4)
    box((0.35, 0.03, 0.12), (0.18, 0, top - 0.08), K.STEEL(), bevel=0.01)       # hoja lateral
    cyl(0.07, 0.0, 0.2, (-0.12, 0, top - 0.08), K.STEEL(), rot=(0, R(-90), 0), v=4)
    for k in range(5):
        a = k * math.tau / 5
        sphere(0.05, (math.cos(a) * 0.05, math.sin(a) * 0.05, top - 0.25), TASSEL(), (0.6, 0.6, 1.6))


def _guandao():
    cyl(0.06, 0.06, 3.0, (0, 0, 0.4), LACQUER())
    import bpy
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=2, y_subdivisions=10, size=1)
    o = bpy.context.object
    for v in o.data.vertices:
        t = v.co.y + 0.5
        w = 0.14 * (1 + 0.6 * math.sin(t * math.pi)) * (1 - t ** 4)
        x = v.co.x * 2 * w + 0.25 * t ** 2
        v.co = (x, 0, 1.9 + t * 0.8)
    K._fin(o, K.STEEL(), smooth=False)
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.04; md.offset = 0
    cyl(0.09, 0.09, 0.12, (0, 0, 1.88), GOLD())
    sphere(0.12, (0, 0, 1.75), TASSEL(), (0.8, 0.8, 1.4), sub=1)
    box((0.04, 0.02, 0.3), (0.12, 0, 2.4), GOLD(), bevel=0.0)


def _escudo_tigre():
    grp = [cyl(0.42, 0.42, 0.06, (0, 0, 0), BAMBOO(), v=40, bevel=0.01),
           torus(0.42, 0.035, (0, 0, 0), K.TRIBU())]
    for k in range(4):
        grp.append(torus(0.1 + k * 0.08, 0.012, (0, 0, 0.03), BAMBOO_D()))
    # cara de tigre
    grp.append(sphere(0.2, (0, 0, 0.04), mat("Tigre", "e8a030", 0.7), (1, 1, 0.3)))
    for sx in (-1, 1):
        grp.append(sphere(0.045, (sx * 0.08, 0.05, 0.1), K.WHITE(), (1, 1, 0.5)))
        grp.append(sphere(0.025, (sx * 0.08, 0.05, 0.12), K.BLACK()))
        grp.append(sphere(0.06, (sx * 0.16, 0.16, 0.06), mat("Tigre", "e8a030", 0.7), (1, 1, 0.4)))
        for k in range(2):
            grp.append(box((0.08, 0.02, 0.02), (sx * 0.13, -0.02 - k * 0.05, 0.1), K.BLACK(), bevel=0.0))
    grp.append(sphere(0.04, (0, -0.04, 0.12), K.BLACK()))
    grp.append(box((0.04, 0.08, 0.02), (0, 0.15, 0.1), K.BLACK(), bevel=0.0))
    K._group(grp, (0, 0, 0), (R(90), 0, 0))


def _ballesta():
    # se sostiene como el arco (mano izquierda): la caja apunta a +X
    WOOD = lambda: mat("MaderaRoja", "8a2e22", 0.7)
    box((0.85, 0.08, 0.1), (0.25, 0, 0), WOOD(), bevel=0.02)
    box((0.35, 0.1, 0.18), (0.45, 0, 0.12), LACQUER(), bevel=0.02)          # cargador de flechas
    for k in range(3):
        cyl(0.012, 0.012, 0.32, (0.45, 0, 0.24 + k * 0.025), BAMBOO(), rot=(0, R(90), 0))
    tube([(0.65, 0, -0.45), (0.7, 0, 0), (0.65, 0, 0.45)], 0.035, BAMBOO())
    tube([(0.65, 0, -0.45), (0.3, 0, 0.0), (0.65, 0, 0.45)], 0.008, K.WHITE(), smooth_curve=False)
    box((0.08, 0.06, 0.3), (-0.05, 0, -0.12), WOOD(), rot=(0, R(20), 0), bevel=0.02)
    sphere(0.04, (0.7, 0, 0), GOLD())


def _baston_ruyi():
    cyl(0.055, 0.055, 2.4, (0, 0, 0.2), mat("BastonRojo", "c8261c", 0.5))
    for z in (-0.95, 1.35):
        cyl(0.075, 0.075, 0.22, (0, 0, z), GOLD())
        torus(0.075, 0.02, (0, 0, z + 0.11), GOLD())


def armas():
    return [L.export_custom_weapon("dao", _dao),
            L.export_custom_weapon("alabarda", _alabarda),
            L.export_custom_weapon("guandao", _guandao),
            L.export_custom_weapon("escudo_tigre", _escudo_tigre),
            L.export_custom_weapon("ballesta_repeticion", _ballesta),
            L.export_custom_weapon("baston_ruyi", _baston_ruyi)]


TROPAS = {"caballero": guardia_imperial, "escudero": guardia_tigre, "arquero": ballestero,
          "jinete": jinete_chino, "jinete_lancero": lancero_chino, "catapulta": lanzacohetes,
          "capitan": capitan_chino, "barco": junco, "heroe_1": dragon, "heroe_2": sun_wukong}


def todas():
    C.tribu("china")
    print(armas())
    for f in TROPAS.values():
        print(f.__name__, f())
    C.save_weapons({"nombre": "China", "tropas": {k: f.__name__ for k, f in TROPAS.items()},
                    "notas": {"sun_wukong_copia": "La copia usa el mismo modelo de Sun Wukong, transparente."}})
