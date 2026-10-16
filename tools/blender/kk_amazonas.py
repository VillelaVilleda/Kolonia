# Tribu de las Amazonas: guerreras de la selva. Bronce, pieles de leopardo, hojas y
# plumas. Montan ciervos. Héroes: la Araña gigante y la Reina Amazona.
import math
import kolonia_lib as K
import kk_lib as L
import kk_tribus_comun as C
from kolonia_lib import R, sphere, cyl, box, torus, tube, mat
from kk_tropas import on, Part

BODY, KNIGHT = C.BODY, C.KNIGHT
SKIN = "c98d63"
BRONZE = lambda: mat("Bronce", "b06a2a", 0.4, 0.7)
BRONZE_D = lambda: mat("BronceOscuro", "6e4018", 0.45, 0.7)
LEAF = lambda: mat("Hoja", "4f8a2e", 0.7)
LEAF_D = lambda: mat("HojaOscura", "2f5a1e", 0.75)
LEOPARD = lambda: mat("Leopardo", "d08e3a", 0.75)
SPOT = lambda: mat("ManchaLeopardo", "3a2416", 0.8)
FEATHER_W = lambda: mat("PlumaBlanca", "f4efe2", 0.6)
VINE = lambda: mat("Liana", "6d7a2c", 0.8)
# Textura KayKit: piel (0,0/0,1), pelo (1,0/1,1), ropa (0,2/0,3), ribetes (1,2/1,3),
# botas (1,4/1,5). Solo los ribetes toman el color de la tribu; la ropa es de cuero.
RECOLOR = {(0, 0): SKIN, (0, 1): SKIN, (1, 0): "3a2416", (1, 1): "3a2416",
           (0, 2): "8a5a34", (0, 3): "6e4426", (1, 4): "7a4a26", (1, 5): "5a3418"}
TEAM = [(1, 2), (1, 3)]
RECOLOR_MAGE = dict(RECOLOR)
RECOLOR_MAGE.update({(0, 2): "4f8a2e", (0, 3): "3d6e22"})


def setup(char="Rogue", keep=None, recolor=None):
    L.recolor(recolor or RECOLOR)
    L.S["team_only"] = TEAM
    L.load_char(char, keep or (BODY + ["Cape"]))


def head_box():
    mn, mx = L.kk_bounds("Head")
    return mn, mx


def leopard_skirt(z_top=0.62, z_bot=0.3, r=0.36, seed=2):
    """Falda de piel de leopardo con borde de hojas (va en la cadera)."""
    h = z_top - z_bot
    s = cyl(r, r * 1.18, h, (0, 0, z_bot + h / 2), LEOPARD(), v=24)
    C.ellipsoid_spots((0, 0, z_bot + h / 2), (r * 1.1, r * 1.1, h * 0.45), 18, SPOT(), size=0.055,
                      seed=seed, zmin=-0.9, flat=0.25)
    for k in range(12):
        a = k * math.tau / 12
        o = sphere(0.075, (math.cos(a) * r * 1.14, math.sin(a) * r * 1.14, z_bot - 0.04),
                   [LEAF, LEAF_D][k % 2](), (0.75, 0.22, 1.6), sub=1)
        o.rotation_euler = (R(-18), 0, a + R(90))
    cyl(r + 0.01, r + 0.01, 0.06, (0, 0, z_top), BRONZE(), v=24)
    return s


def feather_band(top_z, y=0.0, n=5, size=1.0, colors=None):
    """Cinta en la frente con plumas paradas atrás."""
    colors = colors or [K.TRIBU, FEATHER_W]
    for k in range(n):
        a = R(-40 + k * 80 / max(n - 1, 1))
        c = colors[k % len(colors)]
        x = math.sin(a) * 0.22 * size
        sphere(0.07 * size, (x, y + 0.18 * size, top_z + 0.12 * size), c(), (0.45, 0.4, 2.0),
               rot=(R(-20), a * 0.6, 0), sub=1)
        cyl(0.012, 0.012, 0.18 * size, (x, y + 0.18 * size, top_z - 0.05 * size), K.WHITE(), v=6)


def greek_helmet(mn=None, mx=None, crest=True, cheek=True, size=1.0):
    """Casco de bronce griego (deja ver la cara) con cresta del color de la tribu."""
    k = size
    C.cap(BRONZE, r=0.6 * k, front_z=1.92, back_z=1.38, rim=BRONZE_D)
    box((0.08, 0.06, 0.24), (0, -0.6 * k, 1.86), BRONZE(), bevel=0.02)            # nasal
    if cheek:
        for sx in (-1, 1):
            box((0.07, 0.3, 0.38), (sx * 0.56 * k, -0.18, 1.6), BRONZE(), rot=(0, 0, R(sx * 8)), bevel=0.03)
    if crest:
        top = 1.72 + 0.6 * k * 0.95
        box((0.07, 0.9 * k, 0.06), (0, 0.0, top + 0.02), BRONZE_D(), bevel=0.01)
        for i in range(9):
            t = i / 8
            y = -0.42 * k + t * 0.88 * k
            hgt = 0.32 * k * (1 - 0.35 * abs(t - 0.35))
            box((0.11, 0.12, hgt), (0, y, top + 0.04 + hgt / 2), K.TRIBU(), bevel=0.04)
        tube([(0, 0.46 * k, top + 0.2), (0, 0.66 * k, top - 0.1), (0, 0.66 * k, top - 0.55)], 0.065, K.TRIBU())


def shoulder_leaves(bone, sx, z=1.22, x=0.4):
    def build():
        for k, (dy, dz, rz) in enumerate(((-0.08, 0.02, 0), (0.08, 0.02, 0), (0, 0.08, 0))):
            sphere(0.12, (sx * x, dy, z + dz), [LEAF, LEAF_D, LEAF][k](), (0.9, 0.45, 1.3),
                   rot=(0, R(sx * 60), 0), sub=1)
        torus(0.16, 0.03, (sx * x, 0, z - 0.1), BRONZE(), rot=(0, R(sx * 90), 0))
    on(bone, build)


def bronze_bracers():
    for sx, bone in ((1, "lowerarm.l"), (-1, "lowerarm.r")):
        def b(sx=sx):
            cyl(0.1, 0.1, 0.18, (sx * 0.62, 0, 1.05), BRONZE(), rot=(0, R(90), 0))
        on(bone, b)


# ---------------------------------------------------------------------------------------
# Tropas

def guerrera():
    """Caballero: guerrera con casco de bronce, falda de leopardo y espada corta."""
    L.reset("Guerrera")
    setup()
    on("head", greek_helmet)
    on("hips", leopard_skirt)
    shoulder_leaves("upperarm.r", -1)
    L.finalize()
    C.arma("guerrera", "xifos", "handslot.r")
    return L.export("guerrera")


def hoplita():
    """Escudero: armadura de bronce completa, casco cerrado y escudo de media luna."""
    L.reset("Hoplita")
    setup(keep=BODY)
    on("head", greek_helmet, size=1.04)

    def cuirass():
        sphere(0.36, (0, -0.02, 0.92), BRONZE(), (1.05, 0.85, 0.85), sub=1)
        for sx in (-1, 1):
            sphere(0.08, (sx * 0.15, -0.3, 1.0), BRONZE_D(), (1, 0.4, 1))
        box((0.12, 0.05, 0.04), (0, -0.32, 0.8), BRONZE_D(), bevel=0.01)
    on("chest", cuirass)
    on("hips", leopard_skirt, z_top=0.6, z_bot=0.28, r=0.38, seed=4)
    for sx, bone in ((1, "upperarm.l"), (-1, "upperarm.r")):
        def pad(sx=sx):
            sphere(0.24, (sx * 0.4, 0, 1.2), BRONZE(), (1.05, 1.0, 0.75), sub=1)
            torus(0.22, 0.035, (sx * 0.4, 0, 1.12), K.TRIBU())
        on(bone, pad)
    L.finalize()
    C.arma("hoplita", "lanza_corta", "handslot.r")
    C.arma("hoplita", "pelta", "handslot.l")
    return L.export("hoplita")


def cazadora():
    """Arquera: pelo largo suelto, plumas en la frente, carcaj de bambú."""
    L.reset("Cazadora")
    setup("Mage", recolor=RECOLOR_MAGE)

    def band():
        C.brow_band(K.TRIBU, z=1.86, width=0.52, front=-0.52)
        feather_band(1.95, y=0.08, n=5, size=1.1)
    on("head", band)

    def quiver():
        q = [cyl(0.12, 0.12, 0.75, (0, 0, 0), mat("Bambu", "b9a24a", 0.6), bevel=0.01)]
        for z in (-0.2, 0.0, 0.2):
            q.append(torus(0.125, 0.02, (0, 0, z), mat("BambuOscuro", "6f5f22", 0.7)))
        for k in range(5):
            a = k * math.tau / 5
            q.append(cyl(0.015, 0.015, 0.35, (math.cos(a) * 0.06, math.sin(a) * 0.06, 0.52), K.WOOD()))
            q.append(sphere(0.05, (math.cos(a) * 0.06, math.sin(a) * 0.06, 0.72), FEATHER_W() if k % 2 else K.TRIBU(),
                            (0.4, 0.4, 1.5)))
        K._group(q, (0.18, 0.45, 1.0), (R(-15), R(-25), 0))
    on("chest", quiver)
    on("hips", leopard_skirt, z_top=0.6, z_bot=0.34, r=0.34, seed=6)
    L.finalize()
    C.arma("cazadora", "arco_liana", "handslot.l", (0, 0, 180))
    return L.export("cazadora")


def _amazon_head_rider():
    on("head", greek_helmet, crest=True, cheek=False)


def jinete_ciervo():
    """Jinete: amazona sobre un ciervo, con espada corta."""
    def extra():
        on("hips", leopard_skirt, seed=8)
    path = C.rider("Jinete_ciervo", "Rogue", BODY + ["Cape"],
                   lambda: C.ciervo(mat("Ciervo", "b06a34", 0.75), mat("CiervoClaro", "f1dcb4", 0.75)),
                   False, headgear=_amazon_head_rider, extra=extra, recolor=RECOLOR, team_only=TEAM)
    C.arma("jinete_ciervo", "xifos", "handslot.r")
    return path


def jinete_alce():
    """Jinete lancero: amazona con armadura sobre un ciervo grande con cornamenta enorme."""
    def head():
        on("head", greek_helmet, size=1.04)

    def extra():
        on("hips", leopard_skirt, seed=9)

        def cuirass():
            sphere(0.36, (0, -0.02, 0.92), BRONZE(), (1.05, 0.85, 0.85), sub=1)
        on("chest", cuirass)
    path = C.rider("Jinete_alce", "Rogue", BODY, lambda: C.ciervo(mat("Alce", "6e4426", 0.75),
                   mat("AlceClaro", "d9c09a", 0.75), armor=True, big=True), True,
                   headgear=head, extra=extra, recolor=RECOLOR, team_only=TEAM)
    C.arma("jinete_alce", "lanza_plumas", "handslot.r")
    return path


def honda_gigante():
    """Catapulta: un tronco doblado con lianas que lanza piedras (la opera una amazona)."""
    BAMBOO = lambda: mat("Bambu", "b9a24a", 0.6)
    BAMBOO_D = lambda: mat("BambuOscuro", "6f5f22", 0.7)
    LOG = lambda: mat("Tronco", "7a5532", 0.8)

    def frame():
        for sx in (-1, 1):
            box((0.1, 1.15, 0.12), (sx * 0.34, 0, 0.28), LOG(), bevel=0.03)
            for y in (-0.38, 0.38):
                cyl(0.18, 0.18, 0.08, (sx * 0.46, y, 0.18), mat("Rodaja", "c49a62", 0.8),
                    rot=(0, R(90), 0), v=20, bevel=0.01)
                torus(0.18, 0.025, (sx * 0.5, y, 0.18), LOG(), rot=(0, R(90), 0))
                cyl(0.05, 0.05, 0.1, (sx * 0.47, y, 0.18), BAMBOO_D(), rot=(0, R(90), 0))
            # postes de bambú en A
            for dy in (-0.15, 0.15):
                cyl(0.04, 0.04, 1.05, (sx * 0.3, -0.05 + dy, 0.82), BAMBOO(), rot=(R(dy * 60), 0, 0))
                for z in (0.55, 0.85, 1.1):
                    torus(0.045, 0.012, (sx * 0.3, -0.05 + dy * (1 - (z - 0.82) * 0.1), z), BAMBOO_D())
        for y in (-0.45, 0.45):
            box((0.78, 0.09, 0.09), (0, y, 0.3), LOG(), bevel=0.02)
        cyl(0.04, 0.04, 0.72, (0, -0.05, 1.33), BAMBOO(), rot=(0, R(90), 0))
        sphere(0.08, (0, -0.05, 1.33), LEAF(), (3.8, 1, 1))
        cyl(0.12, 0.12, 0.6, (0, 0.2, 0.42), LOG(), rot=(0, R(90), 0))
        for k in range(5):
            torus(0.13, 0.025, (-0.2 + k * 0.1, 0.2, 0.42), VINE(), rot=(0, R(90), 0))
        box((0.7, 0.05, 0.18), (0, -0.5, 0.42), K.TRIBU(), bevel=0.01)
        for k in range(6):
            sphere(0.06, (-0.3 + k * 0.12, -0.53, 0.3), LEAF(), (0.6, 0.4, 1.2))

    def arm():
        tube([(0, 0.2, 0.42), (0, 0.5, 0.48), (0, 0.84, 0.64)], 0.05, BAMBOO())
        for t in (0.35, 0.6):
            torus(0.055, 0.012, (0, 0.2 + 0.64 * t, 0.43 + 0.2 * t), BAMBOO_D(), rot=(R(70), 0, 0))
        sphere(0.17, (0, 0.86, 0.66), LEAF_D(), (1, 1, 0.45), sub=1)          # cesta de hojas
        for k in range(6):
            a = k * math.tau / 6
            sphere(0.07, (math.cos(a) * 0.15, 0.86 + math.sin(a) * 0.15, 0.7), LEAF(), (0.6, 0.6, 1.2))
        sphere(0.13, (0, 0.86, 0.76), mat("Coco", "6b4a2a", 0.8), sub=1)

    def operator():
        def band():
            C.brow_band(K.TRIBU, z=1.86, width=0.5, front=-0.5)
            feather_band(1.95, y=0.08, n=3, size=0.9)
        on("head", band)
        on("hips", leopard_skirt, seed=10)
    return C.siege("Honda_gigante", "Rogue", BODY, frame, arm, operator, recolor=RECOLOR, team_only=TEAM)


def capitana():
    """Capitana: pañuelo con plumas, faja de leopardo, sable y garfio (como el capitán base)."""
    L.reset("Capitana")
    setup()

    def bandana():
        C.cap(K.TRIBU, r=0.61, front_z=1.95, back_z=1.5)
        sphere(0.11, (0.3, 0.55, 1.62), K.TRIBU(), sub=1)
        tube([(0.3, 0.6, 1.58), (0.38, 0.75, 1.35)], 0.05, K.TRIBU())
        tube([(0.26, 0.6, 1.58), (0.25, 0.72, 1.3)], 0.05, K.TRIBU())
        feather_band(2.05, y=0.1, n=3, size=1.2, colors=[FEATHER_W, LEAF, FEATHER_W])
        for sx in (-1, 1):
            torus(0.06, 0.015, (sx * 0.58, -0.02, 1.45), K.GOLD(), rot=(0, R(90), 0))
    on("head", bandana)
    on("hips", leopard_skirt, z_top=0.62, z_bot=0.22, r=0.37, seed=12)
    L.finalize()
    C.arma("capitana", "xifos", "handslot.r")
    C.arma("capitana", "garfio", "handslot.l")
    return L.export("capitana")


def barco_amazonas():
    """Barco de la capitana: canoa de guerra doble (catamarán) con velas de hojas."""
    def build():
        WOOD = lambda: mat("CascoSelva", "6e4426", 0.8)
        WOOD_L = lambda: mat("CubiertaBambu", "9a7a3a", 0.75)
        for sx in (-1, 1):
            h = C.hull(0.34, 1.6, 0.55, WOOD(), z=0.5, sharp=0.5, raise_bow=0.25)
            h.location.x = sx * 0.6
            t = torus(1.0, 0.03, (sx * 0.6, 0, 0.42), K.TRIBU()); t.scale = (0.3, 1.55, 1)
            # proa de serpiente
            tube([(sx * 0.6, -1.5, 0.8), (sx * 0.6, -1.8, 1.2), (sx * 0.6, -1.7, 1.45)], 0.08, LEAF_D())
            sphere(0.12, (sx * 0.6, -1.78, 1.5), LEAF_D(), (0.8, 1.3, 0.8), sub=1)
            for ex in (-1, 1):
                sphere(0.03, (sx * 0.6 + ex * 0.07, -1.88, 1.55), mat("OjoSerpiente", "f2c230", 0.3))
        # cubierta de bambú entre las dos canoas
        for k in range(9):
            cyl(0.045, 0.045, 1.5, (0, -0.8 + k * 0.2, 0.55), WOOD_L(), rot=(0, R(90), 0))
        box((1.3, 1.8, 0.04), (0, 0, 0.58), WOOD_L(), bevel=0.0)
        # Mástiles con velas de hojas grandes
        for y, hgt in ((-0.3, 2.0), (0.6, 1.6)):
            cyl(0.05, 0.04, hgt, (0, y, 0.6 + hgt / 2), mat("Bambu", "b9a24a", 0.6))
            top = 0.6 + hgt
            C.flat_sail([(-0.65, y + 0.02, top - 0.15), (0.65, y + 0.02, top - 0.15),
                         (0.55, y + 0.02, top - hgt * 0.75), (-0.55, y + 0.02, top - hgt * 0.75)], K.TRIBU())
            for k in range(4):
                z = top - 0.25 - k * hgt * 0.15
                cyl(0.015, 0.015, 1.3, (0, y + 0.04, z), mat("Bambu", "b9a24a", 0.6), rot=(0, R(90), 0))
            for sx in (-1, 1):
                sphere(0.2, (sx * 0.6, y + 0.03, top - 0.1), LEAF(), (0.5, 0.15, 1.2), rot=(0, R(sx * 30), 0))
            box((0.03, 0.3, 0.16), (0, y + 0.16, top + 0.12), K.TRIBU(), bevel=0.0)
        # escudos colgados en los costados
        for sx in (-1, 1):
            for y in (-0.6, 0.0, 0.6):
                cyl(0.16, 0.16, 0.04, (sx * 0.92, y, 0.55), BRONZE(), rot=(0, R(90), 0), v=20)
                cyl(0.06, 0.06, 0.05, (sx * 0.94, y, 0.55), K.TRIBU(), rot=(0, R(90), 0))
    return C.static_model("Barco_amazonas", build)


# ---------------------------------------------------------------------------------------
# Héroes

def reina():
    """Reina Amazona: corona de plumas doradas, armadura de oro, capa y arco de oro.
    Habilidad: dispara hasta 3 flechas a enemigos distintos."""
    L.reset("Reina_amazona")
    setup("Mage", recolor=RECOLOR_MAGE)
    cy = 0.0

    def crown():
        C.brow_band(K.GOLD, z=1.86, width=0.52, front=-0.53, thick=0.065)
        sphere(0.08, (0, -0.55, 1.93), mat("Esmeralda", "1fae5f", 0.2), sub=1)
        # Abanico de plumas paradas detrás de la cabeza
        for k in range(9):
            a = R(-72 + k * 18)
            col = [K.TRIBU, K.GOLD, FEATHER_W][k % 3]
            x, y = math.sin(a) * 0.42, 0.18 + math.cos(a) * 0.12
            o = sphere(0.1, (x, y, 2.28 - abs(k - 4) * 0.05), col(), (0.38, 0.22, 2.4), sub=1)
            o.rotation_euler = (R(-12), a * 0.5, 0)
    on("head", crown)

    def armor():
        sphere(0.36, (0, -0.02, 0.92), K.GOLD(), (1.05, 0.85, 0.85), sub=1)
        sphere(0.09, (0, -0.32, 0.95), mat("Esmeralda", "1fae5f", 0.2), (1, 0.5, 1))
    on("chest", armor)
    on("hips", leopard_skirt, z_top=0.62, z_bot=0.18, r=0.38, seed=14)
    for sx, bone in ((1, "upperarm.l"), (-1, "upperarm.r")):
        def pad(sx=sx):
            sphere(0.22, (sx * 0.4, 0, 1.2), K.GOLD(), (1.05, 1.0, 0.72), sub=1)
            for k in range(3):
                sphere(0.07, (sx * 0.52, -0.1 + k * 0.1, 1.08), FEATHER_W(), (0.4, 0.4, 1.4))
        on(bone, pad)
    L.finalize()
    C.arma("reina_amazona", "arco_oro", "handslot.l", (0, 0, 180))
    return L.export("reina_amazona")


def arana():
    """Araña gigante (héroe criatura): lanza telarañas a distancia que inmovilizan a la
    tropa atrapada una ronda; solo ataca cuerpo a cuerpo."""
    def build():
        BODYC = lambda: mat("Arana", "2a2236", 0.6)
        BODYC_L = lambda: mat("AranaClara", "4a3d5c", 0.6)
        HAIR = lambda: mat("PeloArana", "1a1424", 0.8)
        # Abdomen con dibujo del color de la tribu
        sphere(0.62, (0, 0.55, 0.95), BODYC(), (0.95, 1.15, 0.85), sub=1)
        for k, (y, s) in enumerate(((0.25, 0.22), (0.55, 0.18), (0.85, 0.13))):
            sphere(s, (0, y, 1.45 - k * 0.04), K.TRIBU(), (1.3, 0.8, 0.3), sub=1)
        for sx in (-1, 1):
            sphere(0.09, (sx * 0.4, 0.5, 1.28), K.TRIBU(), (1, 1.5, 0.4), rot=(0, R(sx * 30), 0))
        sphere(0.12, (0, 1.2, 0.9), BODYC_L(), (1, 0.8, 1))                       # hilera
        # Cefalotórax y cabeza
        sphere(0.42, (0, -0.25, 0.85), BODYC_L(), (1.0, 1.0, 0.8), sub=1)
        sphere(0.34, (0, -0.62, 0.92), BODYC(), (1.0, 0.9, 0.85), sub=1)
        # Ojos: dos grandes y cuatro chicos
        for sx in (-1, 1):
            sphere(0.11, (sx * 0.13, -0.88, 1.05), mat("OjoAraña", "e83a3a", 0.15), sub=1)
            sphere(0.035, (sx * 0.15, -0.97, 1.09), K.WHITE())
            for k, (dx, dz) in enumerate(((0.27, 1.12), (0.22, 1.24))):
                sphere(0.05, (sx * dx, -0.8, dz), mat("OjoAraña", "e83a3a", 0.15))
        # Colmillos (quelíceros)
        for sx in (-1, 1):
            sphere(0.09, (sx * 0.1, -0.9, 0.78), BODYC_L(), (0.9, 1, 1.2))
            tube([(sx * 0.1, -0.95, 0.72), (sx * 0.08, -1.02, 0.55), (sx * 0.02, -0.97, 0.45)], 0.035,
                 mat("Colmillo", "f1e8d0", 0.4))
        # Corona de la tribu (es un héroe)
        cyl(0.18, 0.2, 0.1, (0, -0.55, 1.25), K.GOLD(), v=16)
        for k in range(5):
            a = k * math.tau / 5
            cyl(0.04, 0.0, 0.12, (math.cos(a) * 0.17, -0.55 + math.sin(a) * 0.17, 1.35), K.GOLD(), v=6)
        # Ocho patas articuladas
        for sx in (-1, 1):
            for k, (ay, reach) in enumerate(((-0.55, 1.05), (-0.3, 1.15), (-0.05, 1.12), (0.2, 1.0))):
                base = (sx * 0.3, ay, 0.9)
                knee = (sx * (0.3 + reach * 0.6), ay - 0.25 + k * 0.17, 1.55 - k * 0.05)
                foot = (sx * (0.3 + reach), ay - 0.55 + k * 0.32, 0.04)
                tube([base, knee], 0.075, BODYC())
                tube([knee, foot], 0.06, BODYC())
                sphere(0.09, knee, BODYC_L())
                for t in (0.3, 0.6):
                    p = [base[i] + (knee[i] - base[i]) * t for i in range(3)]
                    sphere(0.05, (p[0], p[1], p[2] + 0.06), HAIR(), (0.5, 0.5, 1.0))
                mid = [knee[i] + (foot[i] - knee[i]) * 0.55 for i in range(3)]
                torus(0.07, 0.022, tuple(mid), K.TRIBU(), rot=(R(90), 0, 0))
        # Pelitos en el abdomen
        for k in range(10):
            a = k * math.tau / 10
            sphere(0.04, (math.cos(a) * 0.5, 0.55 + math.sin(a) * 0.62, 0.72), HAIR(), (0.5, 0.5, 1.2))
    return C.static_model("Arana_gigante", build)


# ---------------------------------------------------------------------------------------
# Armas

def _xifos():
    blade = lambda: mat("BronceHoja", "d9a050", 0.3, 0.85)
    import bpy
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=2, y_subdivisions=10, size=1)
    o = bpy.context.object
    for v in o.data.vertices:
        t = v.co.y + 0.5
        w = 0.11 * (1 + 0.35 * math.sin(t * math.pi * 0.9)) * (1 - t ** 4)
        v.co = (v.co.x * 2 * w, 0, 0.18 + t * 0.85)
    K._fin(o, blade(), smooth=False)
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.035; md.offset = 0
    box((0.3, 0.07, 0.05), (0, 0, 0.16), BRONZE_D(), bevel=0.02)
    cyl(0.045, 0.045, 0.28, (0, 0, 0.0), K.LEATHER_D())
    sphere(0.06, (0, 0, -0.15), K.TRIBU())


def _lanza_corta():
    cyl(0.05, 0.05, 2.4, (0, 0, 0.3), K.WOOD_D())
    cyl(0.09, 0.0, 0.42, (0, 0, 1.7), BRONZE(), v=8)
    cyl(0.06, 0.06, 0.08, (0, 0, 1.47), K.TRIBU())
    cyl(0.06, 0.03, 0.14, (0, 0, -0.95), BRONZE_D())
    for k in range(3):
        sphere(0.05, (0.06, 0, 1.4 - k * 0.08), FEATHER_W(), (0.4, 0.4, 1.5), rot=(0, R(25), 0))


def _pelta():
    """Escudo de media luna (pelta) de mimbre con borde de bronce."""
    import bpy, bmesh
    # Se modela de frente (mira a -Y) con el centro en la mano
    grp = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=0.5, depth=0.06)
    o = bpy.context.object
    bm = bmesh.new(); bm.from_mesh(o.data)
    # recorte de media luna arriba
    for v in bm.verts:
        x, y = v.co.x, v.co.y
        d = math.hypot(x, y - 0.42)
        if d < 0.32:
            k = (0.32 - d) / 0.32
            v.co.y -= 0.32 * k
    bm.to_mesh(o.data); bm.free()
    K._fin(o, K.TRIBU(), smooth=False)
    grp.append(o)
    grp.append(torus(0.5, 0.035, (0, 0, 0), BRONZE()))
    grp.append(sphere(0.1, (0, 0, 0.04), BRONZE(), (1, 1, 0.6)))
    for k in range(3):
        grp.append(sphere(0.06, (-0.2 + k * 0.2, -0.25, 0.04), LEAF(), (0.5, 1.2, 0.3)))
    K._group(grp, (0, 0, 0), (R(90), 0, 0))


def _arco_liana(gold=False):
    wood = K.GOLD if gold else (lambda: mat("Bambu", "b9a24a", 0.6))
    tube([(0, 0, -0.75), (0.28, 0, -0.35), (0.32, 0, 0.0), (0.28, 0, 0.35), (0, 0, 0.75)], 0.04, wood())
    tube([(0, 0, -0.75), (0, 0, 0.75)], 0.008, K.WHITE(), smooth_curve=False)
    for z in (-0.2, 0.0, 0.2):
        torus(0.05, 0.015, (0.31, 0, z), VINE() if not gold else K.TRIBU(), rot=(R(90), 0, 0))
    for z in (-0.72, 0.72):
        sphere(0.05, (0.02, 0, z), FEATHER_W() if not gold else K.TRIBU(), (0.5, 0.5, 1.3))
    if gold:
        sphere(0.07, (0.33, 0, 0), mat("Esmeralda", "1fae5f", 0.2))


def _lanza_plumas():
    cyl(0.06, 0.06, 3.4, (0, 0, 0.5), K.WOOD_D())
    cyl(0.11, 0.0, 0.55, (0, 0, 2.47), BRONZE(), v=8)
    cyl(0.07, 0.07, 0.1, (0, 0, 2.18), K.GOLD())
    cyl(0.07, 0.07, 0.25, (0, 0, 0.0), K.LEATHER())
    for k in range(5):
        a = k * math.tau / 5
        sphere(0.06, (math.cos(a) * 0.08, math.sin(a) * 0.08, 2.0), [K.TRIBU, FEATHER_W][k % 2](),
               (0.4, 0.4, 1.8), rot=(math.sin(a) * 0.5, math.cos(a) * 0.5, 0))


def armas():
    out = []
    out.append(L.export_custom_weapon("xifos", _xifos))
    out.append(L.export_custom_weapon("lanza_corta", _lanza_corta))
    out.append(L.export_custom_weapon("pelta", _pelta))
    out.append(L.export_custom_weapon("arco_liana", _arco_liana))
    out.append(L.export_custom_weapon("arco_oro", lambda: _arco_liana(gold=True)))
    out.append(L.export_custom_weapon("lanza_plumas", _lanza_plumas))
    return out


TROPAS = {"caballero": guerrera, "escudero": hoplita, "arquero": cazadora, "jinete": jinete_ciervo,
          "jinete_lancero": jinete_alce, "catapulta": honda_gigante, "capitan": capitana,
          "barco": barco_amazonas, "heroe_1": arana, "heroe_2": reina}


def todas():
    C.tribu("amazonas")
    print(armas())
    for f in TROPAS.values():
        print(f.__name__, f())
    C.save_weapons({"nombre": "Amazonas", "tropas": {k: f.__name__ for k, f in TROPAS.items()}})
