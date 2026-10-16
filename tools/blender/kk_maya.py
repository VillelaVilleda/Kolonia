# Tribu Maya: guerreros jaguar y águila, jade, oro, plumas de quetzal y armadura de
# algodón. Montan jaguares. Héroes: Quetzalcóatl (serpiente emplumada que vuela) y
# Balam, el rey jaguar.
import math
import kolonia_lib as K
import kk_lib as L
import kk_tribus_comun as C
from kolonia_lib import R, sphere, cyl, box, torus, tube, mat
from kk_tropas import on

BODY = C.BODY
SKIN = "9c6440"
JADE = lambda: mat("Jade", "2fa58f", 0.4)
QUETZAL = lambda: mat("Quetzal", "1f9a5a", 0.5)
QUETZAL_D = lambda: mat("QuetzalOscuro", "116b3c", 0.55)
COTTON = lambda: mat("Algodon", "f0e8d4", 0.8)
JAG = lambda: mat("Jaguar", "e3a33a", 0.75)
JAG_SPOT = lambda: mat("ManchaJaguar", "2a1a10", 0.8)
JAG_BELLY = lambda: mat("JaguarClaro", "f6e2b8", 0.75)
OBSIDIAN = lambda: mat("Obsidiana", "1c1c24", 0.15, 0.3)
STONE = lambda: mat("PiedraMaya", "9a958a", 0.85)
GOLD = K.GOLD
PLUMA_ORO = lambda: mat("PlumaOro", "f2b52a", 0.5)
PLUMA_BLANCA = lambda: mat("PlumaBlanca", "f4efe2", 0.6)
# Ranger: túnica (6,0) de algodón, pañuelo (0,2) del color de la tribu
RECOLOR = {(0, 0): SKIN, (0, 1): SKIN, (1, 0): "1c1714", (1, 1): "1c1714",
           (6, 0): "f0e8d4", (6, 1): "d6ccb2", (1, 4): "7a4a26", (1, 5): "5a3418"}
TEAM = [(0, 2), (0, 3)]


def setup(char="Ranger", keep=None, recolor=None, team=None):
    L.recolor(recolor or RECOLOR)
    L.S["team_only"] = team if team is not None else TEAM
    L.load_char(char, keep or (BODY + ["Cape"]))


def loincloth(z_top=0.62, z_bot=0.28, r=0.36):
    """Faja y taparrabo del color de la tribu con borde de jade."""
    cyl(r + 0.02, r + 0.02, 0.09, (0, 0, z_top), COTTON(), v=24)
    for y, w in ((-r * 1.02, 0.3), (r * 1.02, 0.3)):
        box((w, 0.05, z_top - z_bot), (0, y, (z_top + z_bot) / 2), K.TRIBU(), bevel=0.01)
        box((w + 0.02, 0.06, 0.05), (0, y, z_bot + 0.02), JADE(), bevel=0.01)
    for sx in (-1, 1):
        sphere(0.05, (sx * 0.2, -r * 1.05, z_top), JADE())


def ear_spools():
    for sx in (-1, 1):
        cyl(0.07, 0.07, 0.05, (sx * 0.6, 0.0, 1.62), JADE(), rot=(0, R(90), 0))
        cyl(0.03, 0.03, 0.06, (sx * 0.6, 0.0, 1.62), GOLD(), rot=(0, R(90), 0))


def jaguar_helmet():
    """Casco de cabeza de jaguar: la cara asoma entre las fauces."""
    C.cap(JAG, r=0.64, front_z=1.98, back_z=1.25, rim=JAG_SPOT, rim_r=0.03)
    C.ellipsoid_spots((0, 0.05, 1.8), (0.62, 0.64, 0.58), 16, JAG_SPOT(), size=0.06, seed=21, zmin=0.25)
    # Hocico sobre la frente, con colmillos
    sphere(0.3, (0, -0.48, 2.1), JAG(), (1.0, 0.85, 0.6), sub=1)
    sphere(0.2, (0, -0.7, 2.04), JAG_BELLY(), (1.1, 0.8, 0.6), sub=1)
    sphere(0.06, (0, -0.85, 2.1), JAG_SPOT(), (1.3, 0.8, 0.8))
    for sx in (-1, 1):
        cyl(0.035, 0.0, 0.16, (sx * 0.13, -0.78, 1.93), K.WHITE(), v=8, rot=(R(10), 0, 0))
        sphere(0.07, (sx * 0.18, -0.6, 2.24), mat("OjoFelino", "f2c230", 0.3), (0.9, 0.6, 0.8))
        sphere(0.035, (sx * 0.18, -0.65, 2.24), K.BLACK())
        sphere(0.13, (sx * 0.35, -0.2, 2.3), JAG(), (0.9, 0.45, 0.9))
        sphere(0.07, (sx * 0.35, -0.23, 2.3), JAG_BELLY(), (0.8, 0.4, 0.8))
    # Piel que cae por la espalda
    box((0.5, 0.1, 0.6), (0, 0.6, 1.3), JAG(), bevel=0.06)
    for k in range(3):
        sphere(0.05, (-0.12 + k * 0.12, 0.66, 1.4 - k * 0.12), JAG_SPOT(), (1, 0.4, 1))
    ear_spools()


def eagle_helmet():
    """Casco de águila: pico abierto sobre la frente y plumas blancas y cafés."""
    WHITE_F = lambda: mat("PlumaBlanca", "f4efe2", 0.6)
    BROWN_F = lambda: mat("PlumaCafe", "7a5232", 0.7)
    C.cap(BROWN_F, r=0.64, front_z=1.98, back_z=1.25)
    for k in range(12):                                    # plumas sobre el casco
        a = k * math.tau / 12
        sphere(0.12, (math.cos(a) * 0.42, 0.05 + math.sin(a) * 0.42, 2.05), [WHITE_F, BROWN_F][k % 2](),
               (0.5, 1.1, 0.3), rot=(0, R(30), a))
    sphere(0.3, (0, -0.42, 2.1), WHITE_F(), (0.95, 0.9, 0.62), sub=1)
    # Pico amarillo
    cyl(0.17, 0.0, 0.38, (0, -0.72, 2.03), mat("Pico", "f2b52a", 0.4), rot=(R(-100), 0, 0), v=16)
    cyl(0.12, 0.0, 0.25, (0, -0.68, 1.92), mat("Pico", "f2b52a", 0.4), rot=(R(-80), 0, 0), v=16)
    for sx in (-1, 1):
        sphere(0.07, (sx * 0.2, -0.55, 2.22), mat("OjoAguila", "e8a020", 0.3), (0.8, 0.6, 0.8))
        sphere(0.035, (sx * 0.2, -0.6, 2.22), K.BLACK())
    # Cresta de plumas del color de la tribu
    for k in range(5):
        o = sphere(0.09, (0, 0.05 + k * 0.12, 2.38 - k * 0.04), K.TRIBU(), (0.35, 0.5, 1.9), sub=1)
        o.rotation_euler = (R(-30 - k * 8), 0, 0)
    ear_spools()


def quetzal_headdress(size=1.0, center=None):
    """Tocado de plumas de quetzal (largas y verdes) con una pluma de la tribu al centro."""
    C.brow_band(GOLD, z=1.88, width=0.52, front=-0.53, thick=0.06)
    sphere(0.09, (0, -0.58, 1.95), JADE(), sub=1)
    for k in range(7):
        a = R(-60 + k * 20)
        col = K.TRIBU if k == 3 else (QUETZAL if k % 2 else QUETZAL_D)
        x, y = math.sin(a) * 0.38, 0.12 + math.cos(a) * 0.1
        L_ = 2.6 * size * (1.0 if k == 3 else 0.85 - abs(k - 3) * 0.04)
        o = sphere(0.11, (x, y, 2.15 + 0.12 * size * L_), col(), (0.35, 0.22, L_), sub=1)
        o.rotation_euler = (R(-22), a * 0.55, 0)


# ---------------------------------------------------------------------------------------
# Tropas

def guerrero_jaguar():
    """Caballero: guerrero jaguar con macuahuitl (garrote con filos de obsidiana)."""
    L.reset("Guerrero_jaguar")
    setup()
    on("head", jaguar_helmet)
    on("hips", loincloth)

    def chest():
        sphere(0.36, (0, -0.02, 0.92), COTTON(), (1.05, 0.85, 0.85), sub=1)
        for k in range(3):
            t = torus(0.3, 0.025, (0, -0.02, 0.75 + k * 0.14), JADE())
            t.scale = (1.15, 0.95, 1)
    on("chest", chest)
    L.finalize()
    C.arma("guerrero_jaguar", "macuahuitl", "handslot.r")
    return L.export("guerrero_jaguar")


def guerrero_aguila():
    """Escudero: guerrero águila con escudo redondo de plumas (chimalli) y lanza."""
    L.reset("Guerrero_aguila")
    setup(keep=BODY)
    on("head", eagle_helmet)
    on("hips", loincloth, r=0.38)

    def chest():
        sphere(0.37, (0, -0.02, 0.92), COTTON(), (1.08, 0.88, 0.88), sub=1)
        sphere(0.1, (0, -0.33, 0.98), GOLD(), (1, 0.4, 1))
    on("chest", chest)
    for sx, bone in ((1, "upperarm.l"), (-1, "upperarm.r")):
        def pad(sx=sx):
            for k in range(4):
                sphere(0.1, (sx * 0.42, -0.12 + k * 0.08, 1.15), [K.TRIBU, PLUMA_BLANCA][k % 2](),
                       (0.5, 0.4, 1.3), rot=(0, R(sx * 40), 0))
        on(bone, pad)
    L.finalize()
    C.arma("guerrero_aguila", "lanza_obsidiana", "handslot.r")
    C.arma("guerrero_aguila", "chimalli", "handslot.l")
    return L.export("guerrero_aguila")


def arquero_maya():
    """Arquero: tocado de plumas de quetzal y arco de madera roja."""
    L.reset("Arquero_maya")
    setup()
    on("head", quetzal_headdress, 0.6)
    on("head", ear_spools)
    on("hips", loincloth)

    def quiver():
        q = [cyl(0.12, 0.14, 0.72, (0, 0, 0), JAG(), bevel=0.01)]
        for z in (-0.15, 0.15):
            q.append(sphere(0.05, (0.0, -0.12, z), JAG_SPOT(), (1, 0.4, 1)))
        for k in range(4):
            a = k * math.tau / 4
            q.append(cyl(0.015, 0.015, 0.4, (math.cos(a) * 0.06, math.sin(a) * 0.06, 0.55), K.WOOD()))
            q.append(sphere(0.05, (math.cos(a) * 0.06, math.sin(a) * 0.06, 0.76), QUETZAL(), (0.4, 0.4, 1.5)))
        K._group(q, (0.18, 0.45, 1.0), (R(-15), R(-25), 0))
    on("chest", quiver)
    L.finalize()
    C.arma("arquero_maya", "arco_maya", "handslot.l", (0, 0, 180))
    return L.export("arquero_maya")


def jinete_jaguar():
    """Jinete: montado en un jaguar, con tocado corto de plumas y macuahuitl."""
    def head():
        on("head", quetzal_headdress, 0.45)
        on("head", ear_spools)

    def extra():
        on("hips", loincloth)
    path = C.rider("Jinete_jaguar", "Ranger", BODY + ["Cape"], lambda: C.jaguar(JAG(), JAG_SPOT(), JAG_BELLY()),
                   False, headgear=head, extra=extra, recolor=RECOLOR, team_only=TEAM)
    C.arma("jinete_jaguar", "macuahuitl", "handslot.r")
    return path


def lancero_jaguar():
    """Jinete lancero: guerrero águila sobre un jaguar con armadura de jade y plumas."""
    def head():
        on("head", eagle_helmet)

    def extra():
        on("hips", loincloth)

        def chest():
            sphere(0.36, (0, -0.02, 0.92), COTTON(), (1.05, 0.85, 0.85), sub=1)
        on("chest", chest)
    path = C.rider("Lancero_jaguar", "Ranger", BODY, lambda: C.jaguar(mat("JaguarOscuro", "c98a2a", 0.75), JAG_SPOT(),
                   JAG_BELLY(), armor=True), True, headgear=head, extra=extra, recolor=RECOLOR, team_only=TEAM)
    C.arma("lancero_jaguar", "lanza_obsidiana_larga", "handslot.r")
    return path


def lanzapiedras():
    """Catapulta: lanzapiedras de madera tallada con jade y plumas; lanza una piedra
    labrada como el calendario."""
    WOOD = lambda: mat("MaderaRoja", "8a4a2a", 0.75)
    WOOD_D = lambda: mat("MaderaRojaOscura", "5e2e1a", 0.8)

    def frame():
        for sx in (-1, 1):
            box((0.08, 1.1, 0.1), (sx * 0.35, 0, 0.3), WOOD(), bevel=0.015)
            box((0.1, 0.1, 1.05), (sx * 0.3, -0.05, 0.85), WOOD(), bevel=0.015)
            for z in (0.55, 0.85, 1.15):
                box((0.12, 0.12, 0.05), (sx * 0.3, -0.05, z), JADE(), bevel=0.01)
            for y in (-0.38, 0.38):
                C.wheel(sx * 0.45, y, 0.18, 0.17, STONE(), JADE(), None)
                for k in range(8):
                    a = k * math.tau / 8
                    box((0.02, 0.04, 0.04), (sx * 0.5, y + math.cos(a) * 0.12, 0.18 + math.sin(a) * 0.12),
                        mat("PiedraOscura", "6a665c", 0.85), bevel=0.0)
            sphere(0.09, (sx * 0.3, -0.05, 1.42), QUETZAL(), (0.4, 0.4, 2.2))
        for y in (-0.45, 0.45):
            box((0.78, 0.09, 0.09), (0, y, 0.3), WOOD(), bevel=0.015)
        box((0.7, 0.1, 0.12), (0, -0.05, 1.35), WOOD_D(), bevel=0.015)
        cyl(0.12, 0.12, 0.6, (0, 0.2, 0.42), WOOD_D(), rot=(0, R(90), 0))
        for k in range(5):
            torus(0.13, 0.025, (-0.2 + k * 0.1, 0.2, 0.42), mat("Cuerda", "c9a86a"), rot=(0, R(90), 0))
        box((0.7, 0.05, 0.18), (0, -0.5, 0.42), K.TRIBU(), bevel=0.01)
        for k in range(5):
            box((0.06, 0.055, 0.06), (-0.24 + k * 0.12, -0.53, 0.42), GOLD(), bevel=0.01)

    def arm():
        box((0.09, 0.09, 0.78), (0, 0.52, 0.52), WOOD_D(), rot=(R(-73), 0, 0), bevel=0.015)
        sphere(0.17, (0, 0.86, 0.66), WOOD(), (1, 1, 0.5))
        cyl(0.13, 0.13, 0.08, (0, 0.86, 0.76), STONE(), v=16, bevel=0.02)
        cyl(0.06, 0.06, 0.09, (0, 0.86, 0.76), JADE(), v=12)

    def operator():
        on("head", quetzal_headdress, 0.4)
        on("hips", loincloth)
    return C.siege("Lanzapiedras", "Ranger", BODY, frame, arm, operator, recolor=RECOLOR, team_only=TEAM)


def capitan_maya():
    """Capitán: tocado alto de plumas, capa de jaguar, macuahuitl y garfio."""
    L.reset("Capitan_maya")
    setup()
    on("head", quetzal_headdress, 0.75)
    on("head", ear_spools)

    def face():
        sphere(0.11, (-0.21, -0.55, 1.62), K.BLACK(), (1, 0.35, 1))
    on("head", face)
    on("hips", loincloth, z_top=0.62, z_bot=0.2)
    L.finalize()
    C.arma("capitan_maya", "macuahuitl", "handslot.r")
    C.arma("capitan_maya", "garfio", "handslot.l")
    return L.export("capitan_maya")


def barco_maya():
    """Barco: gran canoa de un tronco con proa de serpiente emplumada y vela con el sol."""
    def build():
        WOOD = lambda: mat("CanoaMaya", "7a4426", 0.8)
        WOOD_L = lambda: mat("CubiertaMaya", "a8743f", 0.8)
        C.hull(0.6, 1.6, 0.55, WOOD(), z=0.55, sharp=0.55, raise_bow=0.2)
        import kk_tropas as T
        T._ring(0.58, 1.5, 0.25, 0.68, WOOD(), thick=0.05)
        t = torus(1.0, 0.04, (0, 0, 0.5), K.TRIBU()); t.scale = (0.58, 1.52, 1)
        t = torus(1.0, 0.03, (0, 0, 0.42), JADE()); t.scale = (0.56, 1.48, 1)
        d = cyl(1.0, 1.0, 0.04, (0, 0, 0.56), WOOD_L(), v=40); d.scale = (0.55, 1.45, 1)
        # Proa: cabeza de serpiente emplumada
        tube([(0, -1.4, 0.7), (0, -1.75, 1.1), (0, -1.7, 1.45)], 0.13, QUETZAL())
        sphere(0.24, (0, -1.85, 1.55), QUETZAL(), (0.85, 1.3, 0.8), sub=1)
        for sx in (-1, 1):
            sphere(0.06, (sx * 0.13, -2.0, 1.65), mat("OjoSerpiente", "f2c230", 0.3))
            cyl(0.03, 0.0, 0.12, (sx * 0.07, -2.1, 1.43), K.WHITE(), v=8)
        for k in range(7):
            a = R(-90 + k * 30)
            o = sphere(0.1, (math.sin(a) * 0.25, -1.68, 1.62 + math.cos(a) * 0.25), [K.TRIBU, QUETZAL_D][k % 2](),
                       (0.3, 0.3, 1.6), sub=1)
            o.rotation_euler = (0, a, 0)
        # Popa con cola de plumas
        tube([(0, 1.45, 0.7), (0, 1.75, 1.05), (0, 1.7, 1.3)], 0.09, QUETZAL())
        for k in range(3):
            sphere(0.1, (-0.12 + k * 0.12, 1.75, 1.4), [K.TRIBU, QUETZAL, K.TRIBU][k](), (0.3, 0.3, 1.5))
        # Mástil y vela cuadrada de algodón con un sol
        cyl(0.05, 0.04, 2.3, (0, -0.1, 1.7), WOOD())
        cyl(0.025, 0.025, 1.4, (0, -0.1, 2.75), WOOD(), rot=(0, R(90), 0))
        sail = C.flat_sail([(-0.65, -0.12, 2.72), (0.65, -0.12, 2.72), (0.6, -0.12, 1.25), (-0.6, -0.12, 1.25)], COTTON())
        cyl(0.3, 0.3, 0.03, (0, -0.15, 1.98), K.TRIBU(), rot=(R(90), 0, 0), v=24)
        for k in range(8):
            a = k * math.tau / 8
            cyl(0.06, 0.0, 0.16, (math.cos(a) * 0.38, -0.15, 1.98 + math.sin(a) * 0.38), GOLD(),
                rot=(0, -a + R(90), 0), v=4)
        cyl(0.12, 0.12, 0.035, (0, -0.17, 1.98), GOLD(), rot=(R(90), 0, 0), v=20)
        # remos
        for sx in (-1, 1):
            for y in (-0.7, -0.1, 0.5):
                tube([(sx * 0.5, y, 0.7), (sx * 1.0, y + 0.15, 0.1)], 0.025, WOOD(), smooth_curve=False)
                sphere(0.07, (sx * 1.02, y + 0.16, 0.08), WOOD(), (0.4, 1, 1.4))
    return C.static_model("Barco_maya", build)


# ---------------------------------------------------------------------------------------
# Héroes

def quetzalcoatl():
    """Quetzalcóatl (héroe criatura): serpiente emplumada con alas. Vuela sobre lagos y
    montañas; su habilidad salta de enemigo en enemigo (1 a 3 veces)."""
    def build():
        SCALE = QUETZAL
        SCALE_D = QUETZAL_D
        BELLY = lambda: mat("VientreSerpiente", "f2d26a", 0.6)
        # Cola enroscada en el suelo y cuerpo que se levanta como una cobra
        pts = []
        for k in range(10):
            a = k / 9 * math.tau * 0.85
            r = 0.62 - k * 0.025
            pts.append((math.cos(a) * r, 0.35 + math.sin(a) * r, 0.2 + k * 0.012))
        pts += [(0.3, 0.2, 0.55), (0.05, -0.05, 1.1), (-0.05, -0.3, 1.7), (0.0, -0.55, 2.2)]
        tube(pts, 0.22, SCALE())
        import mathutils
        curve = [mathutils.Vector(p) for p in pts]
        for i in range(len(curve) - 1):
            p = curve[i].lerp(curve[i + 1], 0.5)
            d = curve[i + 1] - curve[i]
            o = torus(0.22, 0.035, tuple(p), [SCALE_D, BELLY][i % 2]())
            o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        # cascabel/plumas en la cola
        for k in range(4):
            sphere(0.09, (0.62 + 0.04 * k, 0.3 + k * 0.06, 0.25 + k * 0.05), [K.TRIBU, SCALE][k % 2](),
                   (0.3, 0.3, 1.5), rot=(R(-30), 0, 0))
        top_before = K.mark()
        # Collar de plumas alrededor del cuello
        for k in range(14):
            a = k * math.tau / 14
            o = sphere(0.12, (math.cos(a) * 0.32, -0.75 + math.sin(a) * 0.2, 1.75 + math.sin(a) * 0.12),
                       [K.TRIBU, PLUMA_ORO, SCALE][k % 3](), (0.3, 0.3, 1.7), sub=1)
            o.rotation_euler = (math.sin(a) * 0.9, -math.cos(a) * 0.9, 0)
        # Cabeza
        sphere(0.3, (0, -0.95, 2.02), SCALE(), (0.9, 1.25, 0.8), sub=1)
        sphere(0.22, (0, -1.22, 1.95), SCALE(), (0.85, 1.1, 0.6), sub=1)         # hocico
        sphere(0.16, (0, -1.18, 1.83), BELLY(), (0.9, 1.1, 0.4), sub=1)          # mandíbula
        for sx in (-1, 1):
            sphere(0.08, (sx * 0.18, -1.05, 2.15), mat("OjoSerpiente", "f2c230", 0.3), (0.8, 0.8, 0.9))
            sphere(0.035, (sx * 0.2, -1.1, 2.16), K.BLACK(), (0.5, 0.6, 1.2))
            cyl(0.03, 0.0, 0.14, (sx * 0.08, -1.35, 1.8), K.WHITE(), v=8)
            sphere(0.05, (sx * 0.24, -0.9, 2.2), K.TRIBU(), (0.6, 0.6, 1.2))   # cejas de pluma
        # cresta de plumas
        for k in range(5):
            o = sphere(0.1, (0, -0.85 + k * 0.1, 2.3 - k * 0.02), [K.TRIBU, PLUMA_ORO][k % 2](),
                       (0.3, 0.4, 2.0), sub=1)
            o.rotation_euler = (R(-35 - k * 10), 0, 0)
        tube([(0, -1.4, 1.88), (0, -1.55, 1.82), (-0.06, -1.62, 1.86)], 0.015, mat("Lengua", "d8344a", 0.5))
        # Alas de plumas
        for sx in (-1, 1):
            root = (sx * 0.3, -0.35, 1.4)
            for k in range(7):
                ang = R(15 + k * 11)
                length = 1.45 - k * 0.07
                tip = (sx * (0.3 + math.cos(ang) * length), -0.35 + k * 0.08, 1.4 + math.sin(ang) * length)
                col = [SCALE, SCALE_D, K.TRIBU, PLUMA_ORO][k % 4]
                mid = tuple((root[i] + tip[i]) / 2 for i in range(3))
                o = sphere(length * 0.5, mid, col(), (1.0, 0.12, 0.17), sub=1)
                o.rotation_euler = (0, -sx * ang, 0)
            sphere(0.12, root, SCALE_D(), sub=1)
        # Todo lo de arriba (cabeza, collar, alas) se sube hasta la punta del cuerpo
        from mathutils import Vector
        for o in L.since(top_before):
            o.location += Vector((0.0, 0.2, 0.45))
    return C.static_model("Quetzalcoatl", build)


def balam():
    """Balam, el rey jaguar (héroe): cuerpo fuerte con piel de jaguar, cabeza de jaguar
    con corona de jade y garras de obsidiana. Habilidad propuesta: Acecho (en el bosque
    no lo ven y su primer ataque hace el doble de daño)."""
    L.reset("Balam")
    L.recolor({(0, 0): "e3a33a", (0, 1): "c98a2a", (2, 2): "1f9a5a", (2, 3): "116b3c"})
    L.S["team_only"] = []
    L.load_char("Barbarian", ["ArmLeft", "ArmRight", "Body", "LegLeft", "LegRight"])

    def head():
        sphere(0.52, (0, 0.04, 1.72), JAG(), (1.0, 0.95, 0.95), sub=1)
        C.ellipsoid_spots((0, 0.04, 1.72), (0.52, 0.49, 0.49), 14, JAG_SPOT(), size=0.06, seed=31, zmin=-0.1)
        sphere(0.3, (0, -0.45, 1.58), JAG_BELLY(), (1.0, 0.75, 0.7), sub=1)
        sphere(0.08, (0, -0.68, 1.66), JAG_SPOT(), (1.3, 0.8, 0.8))
        box((0.2, 0.06, 0.04), (0, -0.66, 1.46), mat("Boca", "8a3a2a"), bevel=0.02)
        for sx in (-1, 1):
            sphere(0.1, (sx * 0.2, -0.38, 1.85), mat("OjoFelino", "f2c230", 0.3), (0.9, 0.6, 0.8))
            sphere(0.045, (sx * 0.2, -0.44, 1.85), K.BLACK(), (0.5, 0.6, 1.3))
            sphere(0.14, (sx * 0.38, 0.0, 2.15), JAG(), (0.9, 0.5, 0.9))
            sphere(0.08, (sx * 0.38, -0.03, 2.15), JAG_BELLY(), (0.8, 0.4, 0.8))
            cyl(0.035, 0.0, 0.14, (sx * 0.1, -0.62, 1.42), K.WHITE(), v=8)
        # corona de jade y oro
        cyl(0.4, 0.42, 0.14, (0, 0.04, 2.15), GOLD(), v=24, bevel=0.02)
        for k in range(5):
            a = R(-60 + k * 30)
            sphere(0.07, (math.sin(a) * 0.42, 0.04 - math.cos(a) * 0.42, 2.17), JADE(), sub=1)
        quetzal_headdress_small()
    on("head", head)

    def cape():
        box((0.9, 0.08, 1.0), (0, 0.42, 0.75), K.TRIBU(), rot=(R(8), 0, 0), bevel=0.05)
        for k in range(6):
            sphere(0.08, (-0.3 + k * 0.12, 0.47, 0.32), JAG_SPOT(), (1, 0.4, 1))
        for sx in (-1, 1):
            sphere(0.14, (sx * 0.38, 0.0, 1.18), JADE(), sub=1)
    on("chest", cape)
    on("hips", loincloth, z_top=0.6, z_bot=0.22, r=0.42)
    L.finalize()
    C.arma("balam", "garras_obsidiana", "handslot.r")
    C.arma("balam", "garras_obsidiana", "handslot.l")
    return L.export("balam")


def quetzal_headdress_small():
    for k in range(5):
        a = R(-40 + k * 20)
        col = K.TRIBU if k == 2 else (QUETZAL if k % 2 else QUETZAL_D)
        o = sphere(0.1, (math.sin(a) * 0.3, 0.2, 2.6), col(), (0.35, 0.22, 2.2), sub=1)
        o.rotation_euler = (R(-20), a * 0.6, 0)


# ---------------------------------------------------------------------------------------
# Armas

def _macuahuitl():
    WOOD = lambda: mat("MaderaRoja", "8a4a2a", 0.75)
    box((0.16, 0.06, 1.0), (0, 0, 0.62), WOOD(), bevel=0.03)
    for sx in (-1, 1):
        for k in range(6):
            cyl(0.04, 0.0, 0.1, (sx * 0.1, 0, 0.25 + k * 0.15), OBSIDIAN(), rot=(0, R(sx * 90), 0), v=4)
    cyl(0.045, 0.045, 0.3, (0, 0, 0.0), K.LEATHER_D())
    sphere(0.06, (0, 0, -0.16), JADE())
    box((0.2, 0.07, 0.05), (0, 0, 0.12), GOLD(), bevel=0.01)
    for k in range(2):
        sphere(0.05, (0.0, 0, 1.15 + k * 0.08), QUETZAL(), (0.4, 0.4, 1.4))


def _lanza_obsidiana(length=2.4):
    WOOD = lambda: mat("MaderaRoja", "8a4a2a", 0.75)
    cyl(0.05, 0.05, length, (0, 0, length / 2 - 0.9), WOOD())
    top = length - 0.9
    cyl(0.12, 0.0, 0.42, (0, 0, top + 0.19), OBSIDIAN(), v=4, rot=(0, 0, R(45)))
    for k in range(4):
        sphere(0.05, (math.cos(k * 1.57) * 0.07, math.sin(k * 1.57) * 0.07, top - 0.1), [K.TRIBU, QUETZAL][k % 2](),
               (0.4, 0.4, 1.5))


def _chimalli():
    grp = [cyl(0.42, 0.42, 0.06, (0, 0, 0), K.TRIBU(), v=40, bevel=0.01),
           torus(0.42, 0.04, (0, 0, 0), GOLD()),
           cyl(0.22, 0.22, 0.07, (0, 0, 0.01), COTTON(), v=32),
           cyl(0.1, 0.1, 0.08, (0, 0, 0.02), JADE(), v=20)]
    for k in range(4):
        a = k * math.tau / 4 + 0.4
        grp.append(cyl(0.035, 0.035, 0.08, (math.cos(a) * 0.32, math.sin(a) * 0.32, 0.03), GOLD(), v=12))
    for k in range(7):                                          # flecos de plumas abajo
        x = -0.3 + k * 0.1
        grp.append(sphere(0.06, (x, -0.48, 0.0), [QUETZAL, K.TRIBU][k % 2](), (0.4, 1.8, 0.3)))
    K._group(grp, (0, 0, 0), (R(90), 0, 0))


def _arco_maya():
    WOOD = lambda: mat("MaderaRoja", "8a4a2a", 0.75)
    tube([(0, 0, -0.75), (0.28, 0, -0.35), (0.32, 0, 0.0), (0.28, 0, 0.35), (0, 0, 0.75)], 0.04, WOOD())
    tube([(0, 0, -0.75), (0, 0, 0.75)], 0.008, K.WHITE(), smooth_curve=False)
    torus(0.05, 0.02, (0.32, 0, 0.0), JADE(), rot=(R(90), 0, 0))
    for z in (-0.72, 0.72):
        sphere(0.05, (0.02, 0, z), QUETZAL(), (0.5, 0.5, 1.3))


def _garras():
    cyl(0.08, 0.09, 0.14, (0, 0, 0.0), GOLD(), bevel=0.02)
    for k in range(3):
        x = -0.06 + k * 0.06
        tube([(x, 0, 0.06), (x, -0.02, 0.22), (x + 0.02, -0.08, 0.32)], 0.025, OBSIDIAN())


def armas():
    return [L.export_custom_weapon("macuahuitl", _macuahuitl),
            L.export_custom_weapon("lanza_obsidiana", _lanza_obsidiana),
            L.export_custom_weapon("lanza_obsidiana_larga", lambda: _lanza_obsidiana(3.4)),
            L.export_custom_weapon("chimalli", _chimalli),
            L.export_custom_weapon("arco_maya", _arco_maya),
            L.export_custom_weapon("garras_obsidiana", _garras)]


TROPAS = {"caballero": guerrero_jaguar, "escudero": guerrero_aguila, "arquero": arquero_maya,
          "jinete": jinete_jaguar, "jinete_lancero": lancero_jaguar, "catapulta": lanzapiedras,
          "capitan": capitan_maya, "barco": barco_maya, "heroe_1": quetzalcoatl, "heroe_2": balam}


def todas():
    C.tribu("maya")
    print(armas())
    for f in TROPAS.values():
        print(f.__name__, f())
    C.save_weapons({"nombre": "Maya", "tropas": {k: f.__name__ for k, f in TROPAS.items()}})
