# Piezas comunes para las tribus nuevas (amazonas, desierto, maya, robots, china).
# Cada tribu tiene las mismas tropas que la tribu base (mismas estadísticas) con otro
# estilo, más dos héroes propios. Los modelos salen en assets/tribus/<tribu>/.
#
# Las monturas usan los mismos huesos que el caballo de la tribu base
# (caballo_raiz, caballo, pata_dd/di/td/ti, cuello, cabeza_c, cola), así que las
# animaciones de jinete (Montado, Galope, Ataque_Montado...) sirven para todas.
import math, os, json
import kolonia_lib as K
import kk_lib as L
import kk_tropas as T
from kolonia_lib import R, sphere, cyl, box, torus, tube, mat
from kk_tropas import Part, on, cmb

ROOT = os.environ.get("KOLONIA_ROOT", r"C:\Personal\Kolonia")
TRIBUS_DIR = os.environ.get("KOLONIA_TRIBUS", os.path.join(ROOT, "assets", "tribus"))
KNIGHT, BODY = T.KNIGHT, T.BODY

# Armas que lleva cada tropa de la tribu (para Godot): tropa -> [[arma, hueso, giro?]]
WEAPONS = {}


def tribu(name):
    """Los modelos que se exporten desde aquí van a assets/tribus/<name>."""
    L.OUT = os.path.join(TRIBUS_DIR, name)
    os.makedirs(os.path.join(L.OUT, "armas"), exist_ok=True)
    WEAPONS.clear()


def save_weapons(extra=None):
    """Guarda armas.json: qué arma va en qué mano de cada tropa (y datos extra del diseño)."""
    data = {"armas": WEAPONS}
    if extra:
        data.update(extra)
    with open(os.path.join(L.OUT, "tribu.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def arma(tropa, nombre, hueso="handslot.r", giro=None):
    w = [nombre, hueso]
    if giro:
        w.append(list(giro))
    WEAPONS.setdefault(tropa, []).append(w)


def skin(hexrgb, extra_cells=()):
    """Color de piel (cuadros 0,0 y 0,1 de todas las texturas KayKit)."""
    cells = {(0, 0): hexrgb, (0, 1): hexrgb}
    for c in extra_cells:
        cells[c] = hexrgb
    L.recolor(cells)


def ellipsoid_spots(center, radii, count, m, size=0.06, seed=1, zmin=-0.2, ymin=-9, ymax=9, flat=0.35):
    """Manchas (de jaguar, de ciervo...) sobre la superficie de un elipsoide."""
    import random
    rnd = random.Random(seed)
    cx, cy, cz = center
    rx, ry, rz = radii
    made = 0
    tries = 0
    while made < count and tries < count * 30:
        tries += 1
        u = rnd.uniform(-1, 1)
        a = rnd.uniform(0, math.tau)
        r = math.sqrt(1 - u * u)
        nx, ny, nz = r * math.cos(a), r * math.sin(a), u
        if nz < zmin or not (ymin <= ny <= ymax):
            continue
        p = (cx + nx * rx, cy + ny * ry, cz + nz * rz)
        s = size * rnd.uniform(0.7, 1.25)
        o = sphere(s, p, m, (1, 1, flat), seg=10)
        # orientar la mancha según la normal
        import mathutils
        nrm = mathutils.Vector((nx / rx, ny / ry, nz / rz)).normalized()
        o.rotation_euler = nrm.to_track_quat("Z", "Y").to_euler()
        made += 1


# ---------------------------------------------------------------------------------------
# Monturas. Todas miran hacia -Y y devuelven la altura de la silla.

def bones_for(seat, neck_base, head, tail, legs_y=(-0.42, 0.55), leg_x=0.25):
    """Huesos de montura con la misma estructura que el caballo."""
    fy, by = legs_y
    hip_z = seat - 0.6
    return [
        ("caballo_raiz", (0, 0.55, 0.0), (0, 0.55, 0.3), None),
        ("caballo", (0, 0.1, seat - 0.46), (0, -0.3, seat - 0.46), "caballo_raiz"),
        ("pata_dd", (-leg_x, fy, hip_z), (-leg_x, fy, 0.1), "caballo"),
        ("pata_di", (leg_x, fy, hip_z), (leg_x, fy, 0.1), "caballo"),
        ("pata_td", (-leg_x, by, hip_z), (-leg_x, by, 0.1), "caballo"),
        ("pata_ti", (leg_x, by, hip_z), (leg_x, by, 0.1), "caballo"),
        ("cuello", neck_base, head, "caballo"),
        ("cabeza_c", head, (head[0], head[1] - 0.45, head[2] - 0.05), "cuello"),
        ("cola", tail, (tail[0], tail[1] + 0.17, tail[2] - 0.58), "caballo"),
    ]


def saddle(z, y=0.05, w=1.0, d=0.8, tribe_cloth=True, trim=None):
    """Silla y manta (va dentro de un Part("caballo"))."""
    cyl(0.4, 0.42, 0.1, (0, y, z + 0.07), K.TRIBU() if tribe_cloth else K.LEATHER(), v=32, bevel=0.03)
    box((0.1, 0.12, 0.14), (0, y - 0.35, z + 0.16), K.TRIBU_D(), bevel=0.04)
    box((w, d, 0.05), (0, y, z), K.TRIBU_D(), bevel=0.02)
    for yy in (y - d / 2 + 0.05, y + d / 2 - 0.05):
        box((w, 0.04, 0.06), (0, yy, z), (trim or K.GOLD)(), bevel=0.01)


def leg_set(coat, hoof, muzzle=None, thick=1.0, hip_z=1.0, y_front=-0.42, y_back=0.55, x=0.25,
            paw=False, digitigrade=False):
    """Cuatro patas pegadas a sus huesos."""
    for bone, (sx, y, back) in {"pata_dd": (-1, y_front, False), "pata_di": (1, y_front, False),
                                "pata_td": (-1, y_back, True), "pata_ti": (1, y_back, True)}.items():
        with Part(bone):
            xx = sx * x
            k = hip_z / 1.0
            sphere((0.22 if back else 0.19) * thick, (xx, y + (0.03 if back else 0), 0.98 * k), coat,
                   (0.9, 1.1, 1.3), sub=1)
            cyl(0.15 * thick, 0.1 * thick, 0.5 * k, (xx, y, 0.62 * k), coat, v=16)
            sphere(0.105 * thick, (xx, y, 0.38 * k), coat)
            cyl(0.1 * thick, 0.11 * thick, 0.24 * k, (xx, y, 0.26 * k), coat, v=16)
            if paw:
                sphere(0.15 * thick, (xx, y - 0.05, 0.09), muzzle or coat, (1, 1.25, 0.6), sub=1)
                for dx in (-0.07, 0, 0.07):
                    sphere(0.035 * thick, (xx + dx * thick, y - 0.2 * thick, 0.07), K.WHITE(), (1, 1, 0.8))
            else:
                if muzzle:
                    sphere(0.12 * thick, (xx, y - 0.01, 0.17), muzzle, (1, 1, 0.8))
                cyl(0.14 * thick, 0.16 * thick, 0.15, (xx, y - 0.02, 0.075), hoof(), v=16, bevel=0.03)


def eyes(sx_list, y, z, r=0.085, x=0.22):
    for sx in sx_list:
        sphere(r, (sx * x, y, z), K.WHITE(), (0.7, 1, 1))
        sphere(r * 0.7, (sx * (x + 0.03), y - 0.03, z), K.BLACK(), (0.7, 1, 1))
        sphere(r * 0.24, (sx * (x + 0.05), y - 0.07, z + 0.03), K.WHITE())


def ciervo(coat, belly, armor=False, big=False):
    """Ciervo (amazonas): patas finas, manchas claras y cornamenta."""
    seat = 1.66
    WHITE, BLACK = K.WHITE, K.BLACK
    with Part("caballo"):
        sphere(0.48, (0, -0.3, 1.22), coat, (0.78, 0.95, 0.86), sub=1)
        sphere(0.48, (0, 0.1, 1.17), coat, (0.72, 1.25, 0.76), sub=1)
        sphere(0.48, (0, 0.5, 1.22), coat, (0.8, 0.9, 0.84), sub=1)
        sphere(0.4, (0, 0.1, 0.98), belly, (0.8, 1.4, 0.5), sub=1)
        ellipsoid_spots((0, 0.15, 1.2), (0.36, 0.62, 0.38), 14, belly, size=0.05, seed=3, zmin=0.2)
        saddle(1.56, trim=K.GOLD)
        if armor:
            sphere(0.5, (0, -0.58, 1.25), K.GOLD(), (0.86, 0.55, 0.78), sub=1)
            for sx in (-1, 1):
                for k in range(3):
                    sphere(0.09, (sx * 0.44, -0.2 + k * 0.28, 1.0), mat("Hoja", "4f8a2e", 0.7), (0.35, 1.6, 0.9),
                           rot=(R(-20), 0, 0))
    leg_set(coat, BLACK, belly, thick=0.75, hip_z=1.0)
    with Part("cuello"):
        cyl(0.24, 0.18, 0.8, (0, -0.66, 1.7), coat, rot=(R(-25), 0, 0), v=24, sub=1)
        sphere(0.2, (0, -0.62, 1.55), belly, (0.8, 0.7, 1.2), sub=1)
        if armor:
            torus(0.24, 0.05, (0, -0.68, 1.75), K.GOLD(), rot=(R(-25), 0, 0))
    with Part("cabeza_c"):
        hz = 2.1
        s = 1.35 if big else 1.1
        sphere(0.27, (0, -0.9, hz), coat, (0.85, 1.05, 0.95), sub=1)
        sphere(0.2, (0, -1.17, hz - 0.12), belly, (0.8, 1.2, 0.8), rot=(R(15), 0, 0), sub=1)
        sphere(0.06, (0, -1.36, hz - 0.13), BLACK(), (1.2, 0.8, 0.9))
        eyes((-1, 1), -1.03, hz + 0.05, r=0.08, x=0.19)
        for sx in (-1, 1):
            sphere(0.12, (sx * 0.3, -0.8, hz + 0.12), coat, (0.5, 0.35, 1.0), rot=(0, R(sx * 50), R(sx * 40)))
            # Cornamenta
            base = (sx * 0.12, -0.86, hz + 0.22)
            top = (sx * 0.42 * s, -0.78, hz + 0.75 * s)
            ANT = lambda: mat("Asta", "d8bf8c", 0.6)
            tube([base, (sx * 0.24 * s, -0.84, hz + 0.45 * s), top], 0.055, ANT())
            for k, (fx, fz) in enumerate(((0.2, 0.4), (0.32, 0.6), (0.4, 0.74))):
                p0 = (sx * fx * s, -0.84, hz + fz * s)
                tube([p0, (sx * (fx + 0.02) * s, -1.02, hz + (fz + 0.16) * s)], 0.04, ANT())
            if big:
                sphere(0.05, top, K.GOLD())
        if armor:
            sphere(0.24, (0, -0.98, hz + 0.08), K.GOLD(), (0.82, 1.0, 0.6), rot=(R(20), 0, 0), sub=1)
        box((0.46, 0.04, 0.04), (0, -1.1, hz + 0.08), K.LEATHER_D(), bevel=0.01)
    with Part("cola"):
        sphere(0.12, (0, 0.92, 1.3), coat, (0.9, 0.6, 1.2), rot=(R(30), 0, 0))
        sphere(0.09, (0, 0.96, 1.26), WHITE(), (0.8, 0.5, 1.0), rot=(R(30), 0, 0))
    return seat, bones_for(seat, (0, -0.5, 1.45), (0, -0.85, 2.05), (0, 0.88, 1.38))


def camello(coat, armor=False):
    """Camello (desierto): patas largas, joroba (la silla va encima) y cuello curvo."""
    seat = 2.05
    WHITE, BLACK = K.WHITE, K.BLACK
    dark = mat("CameloOscuro", "8c6a40", 0.85)
    with Part("caballo"):
        sphere(0.56, (0, -0.25, 1.45), coat, (0.8, 0.95, 0.85), sub=1)
        sphere(0.56, (0, 0.15, 1.4), coat, (0.74, 1.2, 0.78), sub=1)
        sphere(0.54, (0, 0.55, 1.45), coat, (0.8, 0.85, 0.82), sub=1)
        sphere(0.44, (0, 0.1, 1.82), coat, (0.78, 0.9, 0.62), sub=1)        # joroba
        # Silla de camello con mantas y borlas
        box((1.05, 0.9, 0.06), (0, 0.1, 1.95), K.TRIBU_D(), bevel=0.02)
        for sx in (-1, 1):
            box((0.05, 0.9, 0.42), (sx * 0.52, 0.1, 1.74), K.TRIBU(), bevel=0.02)
            for y in (-0.2, 0.1, 0.4):
                sphere(0.05, (sx * 0.55, y, 1.5), K.GOLD())
                cyl(0.03, 0.05, 0.12, (sx * 0.55, y, 1.42), K.TRIBU_D(), v=8)
        cyl(0.36, 0.4, 0.1, (0, 0.1, 2.0), K.TRIBU(), v=32, bevel=0.03)
        box((0.1, 0.12, 0.2), (0, -0.25, 2.12), mat("MaderaClara", "c9a26a", 0.7), bevel=0.04)
        box((0.1, 0.12, 0.2), (0, 0.45, 2.12), mat("MaderaClara", "c9a26a", 0.7), bevel=0.04)
        if armor:
            sphere(0.52, (0, -0.55, 1.45), K.GOLD(), (0.86, 0.5, 0.75), sub=1)
            g = cyl(0.48, 0.52, 0.5, (0, 0.15, 1.18), mat("Lino", "efe6cf", 0.7), v=32)
            g.scale = (1, 1.6, 1)
            t = torus(0.52, 0.035, (0, 0.15, 0.94), K.TRIBU())
            t.scale = (1, 1.6, 1)
    leg_set(coat, lambda: dark, None, thick=0.85, hip_z=1.3, y_front=-0.42, y_back=0.55)
    with Part("cuello"):
        tube([(0, -0.55, 1.6), (0, -1.05, 1.5), (0, -1.25, 2.0), (0, -1.2, 2.6)], 0.2, coat)
        if armor:
            torus(0.23, 0.045, (0, -1.24, 2.15), K.GOLD(), rot=(R(10), 0, 0))
        for z in (1.75, 1.95, 2.15):
            sphere(0.06, (0, -1.0 - (z - 1.75) * 0.5, z), K.TRIBU())
    with Part("cabeza_c"):
        hz = 2.72
        sphere(0.28, (0, -1.22, hz), coat, (0.85, 1.1, 0.9), sub=1)
        sphere(0.2, (0, -1.5, hz - 0.08), coat, (0.85, 1.2, 0.8), sub=1)
        box((0.2, 0.06, 0.04), (0, -1.67, hz - 0.15), dark, bevel=0.02)       # boca
        for sx in (-1, 1):
            sphere(0.08, (sx * 0.2, -1.36, hz + 0.06), K.WHITE(), (0.7, 1, 1))
            sphere(0.055, (sx * 0.23, -1.39, hz + 0.06), K.BLACK(), (0.7, 1, 1))
            box((0.15, 0.03, 0.045), (sx * 0.19, -1.38, hz + 0.12), dark, rot=(0, R(sx * 15), 0), bevel=0.01)  # párpado
            sphere(0.07, (sx * 0.24, -1.1, hz + 0.17), coat, (0.5, 0.8, 1.2))
            sphere(0.028, (sx * 0.07, -1.68, hz - 0.03), BLACK())
        torus(0.23, 0.035, (0, -1.3, hz - 0.02), K.TRIBU(), rot=(R(80), 0, 0))
        sphere(0.06, (0, -1.48, hz + 0.12), K.GOLD())
        if armor:
            sphere(0.23, (0, -1.3, hz + 0.1), K.GOLD(), (0.9, 1.0, 0.5), sub=1)
            for k in range(3):
                sphere(0.07, (0, -1.2 + k * 0.09, hz + 0.28 + k * 0.05), K.TRIBU(), (0.6, 1, 1.6))
    with Part("cola"):
        tube([(0, 0.92, 1.55), (0, 1.0, 1.3), (0, 0.98, 1.05)], 0.05, coat)
        sphere(0.07, (0, 0.98, 1.0), dark, (0.8, 0.8, 1.4))
    return seat, bones_for(seat, (0, -0.5, 1.6), (0, -1.2, 2.65), (0, 0.9, 1.55), legs_y=(-0.42, 0.55))


def jaguar(coat, spots, belly, armor=False):
    """Jaguar (mayas): bajo y fuerte, patas con garras, manchas y cola larga."""
    seat = 1.42
    BLACK, WHITE = K.BLACK, K.WHITE
    with Part("caballo"):
        sphere(0.48, (0, -0.32, 1.0), coat, (0.86, 0.98, 0.84), sub=1)
        sphere(0.48, (0, 0.1, 0.96), coat, (0.78, 1.25, 0.74), sub=1)
        sphere(0.46, (0, 0.5, 1.0), coat, (0.84, 0.92, 0.82), sub=1)
        sphere(0.4, (0, 0.1, 0.8), belly, (0.84, 1.4, 0.5), sub=1)
        ellipsoid_spots((0, 0.1, 0.98), (0.38, 0.66, 0.37), 26, spots, size=0.065, seed=5, zmin=-0.1)
        saddle(1.33, trim=lambda: mat("Jade", "2fa58f", 0.4))
        if armor:
            sphere(0.5, (0, -0.62, 1.05), mat("Jade", "2fa58f", 0.4), (0.86, 0.5, 0.75), sub=1)
            for sx in (-1, 1):
                for k in range(4):
                    sphere(0.08, (sx * 0.45, -0.25 + k * 0.22, 0.85), K.TRIBU(), (0.35, 1.5, 0.8),
                           rot=(R(-30), 0, 0))
    leg_set(coat, BLACK, belly, thick=1.1, hip_z=0.8, paw=True)
    with Part("cuello"):
        cyl(0.32, 0.26, 0.45, (0, -0.68, 1.22), coat, rot=(R(-55), 0, 0), v=24, sub=1)
        ellipsoid_spots((0, -0.68, 1.22), (0.3, 0.25, 0.3), 6, spots, size=0.05, seed=9, zmin=0.0)
        if armor:
            torus(0.3, 0.05, (0, -0.72, 1.28), K.GOLD(), rot=(R(-55), 0, 0))
    with Part("cabeza_c"):
        hz = 1.45
        sphere(0.36, (0, -0.95, hz), coat, (0.95, 0.9, 0.85), sub=1)
        sphere(0.2, (0, -1.22, hz - 0.1), belly, (1.1, 0.8, 0.75), sub=1)
        sphere(0.06, (0, -1.38, hz - 0.03), BLACK(), (1.3, 0.8, 0.8))
        for sx in (-1, 1):
            sphere(0.09, (sx * 0.17, -1.22, hz + 0.08), mat("OjoFelino", "f2c230", 0.3), (0.8, 0.6, 1))
            sphere(0.04, (sx * 0.17, -1.27, hz + 0.08), BLACK(), (0.5, 0.6, 1.2))
            sphere(0.11, (sx * 0.28, -0.85, hz + 0.27), coat, (0.9, 0.45, 0.9))
            sphere(0.06, (sx * 0.28, -0.88, hz + 0.26), belly, (0.8, 0.4, 0.8))
            cyl(0.025, 0.0, 0.12, (sx * 0.08, -1.28, hz - 0.2), WHITE(), v=8)   # colmillos
        ellipsoid_spots((0, -0.92, hz + 0.05), (0.33, 0.3, 0.3), 9, spots, size=0.045, seed=11, zmin=0.2, ymin=-0.3)
        if armor:
            # Tocado de plumas
            for k in range(5):
                a = R(-50 + k * 25)
                cyl(0.06, 0.03, 0.42, (math.sin(a) * 0.18, -0.85 + abs(math.sin(a)) * 0.05, hz + 0.45),
                    [K.TRIBU, lambda: mat("Quetzal", "1f9a5a", 0.5)][k % 2](), rot=(R(-15), a * 0.8, 0), v=8)
            torus(0.3, 0.04, (0, -0.92, hz + 0.2), K.GOLD(), rot=(R(-10), 0, 0))
        box((0.6, 0.04, 0.04), (0, -1.12, hz - 0.05), K.LEATHER_D(), bevel=0.01)
    with Part("cola"):
        tube([(0, 0.88, 1.08), (0, 1.25, 1.0), (0, 1.45, 1.25), (0, 1.5, 1.5)], 0.075, coat)
        for k, t in enumerate((0.3, 0.55, 0.8)):
            sphere(0.08, (0, 1.2 + t * 0.35, 1.02 + t * 0.5), spots, (1, 1, 0.5))
    return seat, bones_for(seat, (0, -0.55, 1.15), (0, -0.9, 1.45), (0, 0.88, 1.08))


def robocaballo(armor=False):
    """Caballo mecánico (robots): placas de metal, articulaciones y ojos brillantes."""
    seat = 1.66
    MET = lambda: mat("Metal", "9aa3ad", 0.35, 0.85)
    MET_D = lambda: mat("MetalOscuro", "4c535c", 0.4, 0.8)
    GLOW = lambda: mat("Luz", "35e0ff", 0.2)
    with Part("caballo"):
        box((0.62, 1.3, 0.55), (0, 0.1, 1.2), MET(), bevel=0.12)
        box((0.5, 1.1, 0.12), (0, 0.1, 0.9), MET_D(), bevel=0.04)
        for y in (-0.3, 0.1, 0.5):
            box((0.66, 0.06, 0.4), (0, y, 1.2), MET_D(), bevel=0.02)
        for sx in (-1, 1):
            box((0.04, 0.5, 0.18), (sx * 0.32, 0.1, 1.25), K.TRIBU(), bevel=0.02)
            cyl(0.06, 0.06, 0.04, (sx * 0.33, 0.45, 1.3), GLOW(), rot=(0, R(90), 0))
        cyl(0.07, 0.06, 0.35, (0.18, 0.62, 1.55), MET_D(), v=12)       # tubos de escape
        cyl(0.07, 0.06, 0.35, (-0.18, 0.62, 1.55), MET_D(), v=12)
        saddle(1.5, trim=lambda: mat("Cobre", "c87a3a", 0.35, 0.8))
        if armor:
            box((0.72, 0.4, 0.62), (0, -0.55, 1.2), K.TRIBU(), bevel=0.1)
            for sx in (-1, 1):
                box((0.06, 1.2, 0.5), (sx * 0.38, 0.1, 1.0), MET_D(), bevel=0.03)
    for bone, (sx, y) in {"pata_dd": (-1, -0.42), "pata_di": (1, -0.42), "pata_td": (-1, 0.55), "pata_ti": (1, 0.55)}.items():
        with Part(bone):
            x = sx * 0.25
            sphere(0.15, (x, y, 0.98), MET_D(), sub=1)
            box((0.16, 0.18, 0.45), (x, y, 0.72), MET(), bevel=0.05)
            sphere(0.1, (x, y, 0.45), MET_D())
            cyl(0.07, 0.07, 0.3, (x, y, 0.28), MET(), v=12)
            box((0.24, 0.3, 0.12), (x, y - 0.03, 0.07), MET_D(), bevel=0.04)
    with Part("cuello"):
        box((0.32, 0.36, 0.75), (0, -0.7, 1.62), MET(), rot=(R(-35), 0, 0), bevel=0.08)
        for k in range(4):
            box((0.06, 0.12, 0.08), (0, -0.55 - k * 0.13, 1.88 + k * 0.1), K.TRIBU(), bevel=0.02)
    with Part("cabeza_c"):
        hz = 2.02
        box((0.42, 0.62, 0.36), (0, -1.05, hz), MET(), rot=(R(15), 0, 0), bevel=0.08)
        box((0.36, 0.2, 0.06), (0, -1.12, hz + 0.12), GLOW(), rot=(R(15), 0, 0), bevel=0.02)   # visor
        for sx in (-1, 1):
            cyl(0.06, 0.0, 0.24, (sx * 0.13, -0.88, hz + 0.3), MET_D(), rot=(R(-10), R(sx * 15), 0), v=6)
        sphere(0.05, (0, -1.38, hz - 0.08), GLOW())
        if armor:
            cyl(0.06, 0.0, 0.45, (0, -1.3, hz + 0.25), mat("Cobre", "c87a3a", 0.35, 0.8),
                rot=(R(-55), 0, 0), v=8)
    with Part("cola"):
        for k in range(4):
            sphere(0.07 - k * 0.01, (0, 0.85 + k * 0.08, 1.35 - k * 0.15), MET_D())
        cyl(0.04, 0.04, 0.14, (0, 1.15, 0.8), GLOW())
    return seat, bones_for(seat, (0, -0.5, 1.4), (0, -0.85, 1.95), (0, 0.88, 1.38))


def caballo(coat, mane, muzzle, armor=False, blaze=True):
    """El caballo de la tribu base (para la tribu china, con adornos propios)."""
    seat = T.horse(coat, mane, muzzle, armor=armor, blaze=blaze)
    return seat, T.HORSE_BONES


def rider(name, char, keep, mount_fn, lance, headgear=None, extra=None, recolor=None, team_extra=None,
          team_only=None):
    """Jinete sobre una montura. mount_fn() -> (altura_silla, huesos)."""
    L.reset(name)
    if recolor:
        L.recolor(recolor)
    if team_extra:
        L.S["team_extra"] = team_extra
    if team_only is not None:
        L.S["team_only"] = team_only
    L.load_char(char, keep)
    if headgear:
        headgear()
    if extra:
        extra()
    seat, bones = mount_fn()
    L.move_rig((0, 0.08, seat - 0.38))
    L.add_bones(bones, reparent={"root": "caballo"})
    T.rider_actions(lance)
    L.finalize()
    return L.export(name.lower(), animations=True)


# ---------------------------------------------------------------------------------------
# Catapultas: el brazo (o lo que se mueva) va en el hueso "brazo_cat", con la misma
# animación "Disparo" de la catapulta base.

def siege(name, char, keep, frame_fn, arm_fn, operator_fn=None, recolor=None, F=2.0, arm_bone=None,
          team_extra=None, team_only=None):
    import bpy
    import kk_anims as A
    L.reset(name)
    if recolor:
        L.recolor(recolor)
    if team_extra:
        L.S["team_extra"] = team_extra
    if team_only is not None:
        L.S["team_only"] = team_only
    L.load_char(char, keep)
    before = K.mark()
    frame_fn()
    frame = L.since(before)
    L.scale_objs(frame, F)
    L.static(frame)
    before = K.mark()
    arm_fn()
    arm_objs = L.since(before)
    L.scale_objs(arm_objs, F)
    L.on_bone(arm_objs, "brazo_cat", world=True)
    if operator_fn:
        operator_fn()
    L.move_rig((1.45, 0.65, 0))
    L.add_bones([arm_bone or ("brazo_cat", (0, 0.2 * F, 0.42 * F), (0, 0.86 * F, 0.66 * F), None)])
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
    return L.export(name.lower(), animations=True)


def wheel(x, y, z, r, m, hub, rim=None, spokes=6, w=0.07):
    cyl(r, r, w, (x, y, z), m, rot=(0, R(90), 0), v=24, bevel=0.01)
    cyl(r * 0.35, r * 0.35, w + 0.02, (x, y, z), hub, rot=(0, R(90), 0))
    if rim:
        torus(r, 0.02, (x + 0.04 * (1 if x > 0 else -1), y, z), rim, rot=(0, R(90), 0))


# ---------------------------------------------------------------------------------------
# Barcos: casco común (medio elipsoide) para que cada tribu le ponga su estilo.

def hull(rx, ry, rz, m, z=0.6, sharp=0.35, raise_bow=0.12, thick=0.05):
    import bpy, bmesh
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=40, ring_count=20, location=(0, 0, z))
    o = bpy.context.object
    o.scale = (rx, ry, rz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0.0),
                           plane_no=(0, 0, 1), clear_outer=True)
    for v in bm.verts:
        if v.co.y < -ry * 0.4:
            k = (-v.co.y - ry * 0.4) / ry
            v.co.x *= 1 - sharp * k * 1.6
            v.co.z += raise_bow * k * 2
    bm.to_mesh(o.data); bm.free()
    K._fin(o, m)
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = thick
    return o


def flat_sail(points, m, thick=0.02):
    """Vela plana a partir de un polígono (lista de puntos 3D)."""
    import bpy, bmesh
    me = bpy.data.meshes.new("vela")
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in points]
    bm.faces.new(vs)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("vela", me)
    K.C["col"].objects.link(o)
    K._fin(o, m, smooth=False)
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = thick
    return o


def static_model(name, build):
    """Modelo sin esqueleto (barcos, héroes criatura): build() arma las piezas."""
    L.reset(name)
    build()
    L.finalize()
    return L.export(name.lower())


# ---------------------------------------------------------------------------------------
# Tocados (cascos, pañuelos, gorros) para las cabezas KayKit (cabeza ~1.1 de ancho,
# centro a z ~1.72). Un "casquete" es una media esfera cortada en diagonal: más alta
# adelante (deja ver la cara) y más baja atrás.

HEAD_C = (0.0, 0.0, 1.72)


def cap(m, r=0.6, front_z=1.93, back_z=1.45, center=HEAD_C, scale=(1.0, 1.04, 0.95), rim=None,
        rim_r=0.045):
    import bpy, bmesh
    from mathutils import Vector
    m = m() if callable(m) else m
    cx, cy, cz = center
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=32, ring_count=16, location=(cx, cy, cz))
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ry = r * scale[1]
    p_front = Vector((0, -ry, front_z - cz))
    p_back = Vector((0, ry, back_z - cz))
    d = (p_back - p_front).normalized()
    nrm = Vector((0, -d.z, d.y))          # perpendicular en el plano YZ, apuntando arriba
    if nrm.z < 0:
        nrm = -nrm
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=p_front,
                           plane_no=nrm, clear_inner=True)
    bm.to_mesh(o.data); bm.free()
    K._fin(o, m)
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.04
    if rim:
        pts = []
        rx = r * scale[0]
        for k in range(33):
            a = k / 32 * math.tau
            y = math.sin(a) * ry
            z = front_z + (back_z - front_z) * (y + ry) / (2 * ry)
            # radio de la esfera a esa altura
            dz = (z - cz) / (r * scale[2])
            f = math.sqrt(max(0.0, 1 - dz * dz))
            pts.append((cx + math.cos(a) * rx * f * 1.01, cy + y * f * 1.01, z))
        tube(pts, rim_r, rim() if callable(rim) else rim, smooth_curve=False)
    return o


def brow_band(m, z=1.9, thick=0.05, width=0.5, front=-0.5):
    """Cinta en la frente (de sien a sien, por delante del pelo)."""
    m = m() if callable(m) else m
    pts = []
    for k in range(9):
        a = R(-70 + k * 140 / 8)
        pts.append((math.sin(a) * width * 1.08, front * math.cos(a) + 0.04, z + 0.04 * math.cos(a)))
    return tube(pts, thick, m)


def head_ring(m, z=1.9, r=0.57, tilt=-8, thick=0.045):
    """Cinta alrededor de la cabeza (frente)."""
    return torus(r, thick, (0, 0.02, z), m() if callable(m) else m, rot=(R(tilt), 0, 0))
