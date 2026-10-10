# Biblioteca para armar las tropas de Kolonia en Blender (estilo caricatura "chibi").
# Convenciones: Z arriba, la tropa mira hacia -Y, los pies en z = 0, altura ~1.8.
# Los materiales que empiezan con "K_Tribu" son el color de la tribu: Godot los
# recolorea para cada jugador (rojo, azul...).
import bpy, math, os
from mathutils import Vector
R = math.radians
C = {}
EXPORT_DIR = r"C:\Personal\Kolonia\assets\tropas"


def new_unit(name):
    col = bpy.data.collections.get(name)
    if col:
        for o in list(col.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    else:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    C["col"] = col
    C["name"] = name
    return col


def mat(name, hexrgb, rough=0.6, metal=0.0):
    m = bpy.data.materials.get("K_" + name)
    if m is None:
        m = bpy.data.materials.new("K_" + name)
        m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    srgb = [int(hexrgb[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    b.inputs["Base Color"].default_value = (*lin, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


# Paleta común
SKIN = lambda: mat("Piel", "f2b48c", 0.7)
TRIBU = lambda: mat("Tribu", "c8261c", 0.55)        # rojo de la tribu
TRIBU_D = lambda: mat("TribuOscuro", "8e1610", 0.6)  # rojo oscuro de la tribu
STEEL = lambda: mat("Acero", "a9b0b8", 0.35, 0.85)
STEEL_D = lambda: mat("AceroOscuro", "6d747c", 0.4, 0.8)
LEATHER = lambda: mat("Cuero", "7a4a26", 0.7)
LEATHER_D = lambda: mat("CueroOscuro", "4e2e17", 0.75)
PANTS = lambda: mat("Pantalon", "2b2f38", 0.8)
WOOD = lambda: mat("Madera", "9a6a3c", 0.75)
WOOD_D = lambda: mat("MaderaOscura", "6b4524", 0.8)
GOLD = lambda: mat("Oro", "e0b040", 0.35, 0.7)
WHITE = lambda: mat("Blanco", "f5f5f0", 0.5)
BLACK = lambda: mat("Negro", "1c1714", 0.5)
HAIR = lambda: mat("Pelo", "6b3f22", 0.8)
CHAIN = lambda: mat("Malla", "8d939a", 0.45, 0.7)


def _fin(o, m, smooth=True, sub=0, bevel=0.0):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    C["col"].objects.link(o)
    if hasattr(o.data, "materials"):
        o.data.materials.clear()
        o.data.materials.append(m)
    if smooth and o.type == "MESH":
        for p in o.data.polygons:
            p.use_smooth = True
    if bevel:
        md = o.modifiers.new("bv", "BEVEL")
        md.width = bevel
        md.segments = 2
    if sub:
        md = o.modifiers.new("sd", "SUBSURF")
        md.levels = sub
        md.render_levels = sub
    return o


def sphere(r, loc, m, s=(1, 1, 1), rot=(0, 0, 0), seg=24, sub=0):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, rotation=rot, segments=seg, ring_count=max(8, seg // 2))
    o = bpy.context.object
    o.scale = s
    return _fin(o, m, sub=sub)


def cyl(r1, r2, d, loc, m, rot=(0, 0, 0), v=24, sub=0, bevel=0.0):
    bpy.ops.mesh.primitive_cone_add(vertices=v, radius1=r1, radius2=r2, depth=d, location=loc, rotation=rot)
    return _fin(bpy.context.object, m, sub=sub, bevel=bevel)


def box(s, loc, m, rot=(0, 0, 0), bevel=0.02, smooth=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = s
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _fin(o, m, smooth=smooth, bevel=bevel)


def torus(big, small, loc, m, rot=(0, 0, 0), seg=32):
    bpy.ops.mesh.primitive_torus_add(major_radius=big, minor_radius=small, location=loc, rotation=rot,
                                     major_segments=seg, minor_segments=10)
    return _fin(bpy.context.object, m)


def tube(points, r, m, smooth_curve=True):
    """Tubo que sigue una lista de puntos (cuerdas, arcos, mangos curvos)."""
    cu = bpy.data.curves.new("tubo", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    if smooth_curve:
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(points) - 1)
        for i, p in enumerate(points):
            bp = sp.bezier_points[i]
            bp.co = p
            bp.handle_left_type = bp.handle_right_type = "AUTO"
    else:
        sp = cu.splines.new("POLY")
        sp.points.add(len(points) - 1)
        for i, p in enumerate(points):
            sp.points[i].co = (*p, 1)
    o = bpy.data.objects.new("tubo", cu)
    C["col"].objects.link(o)
    cu.materials.append(m)
    return o


# --- Piezas del cuerpo --------------------------------------------------------------

def head(z, r=0.3, x=0.0, y=0.0, skin=None, brows=True, mouth=True):
    """Cabeza grande con ojos, cejas, nariz, boca y orejas."""
    skin = skin or SKIN()
    sphere(r, (x, y, z), skin, (1.0, 0.95, 1.02), sub=1)
    for sx in (-1, 1):
        sphere(r * 0.2, (x + sx * r * 0.36, y - r * 0.86, z + r * 0.08), WHITE(), (1, 0.55, 1.15))
        sphere(r * 0.11, (x + sx * r * 0.35, y - r * 0.96, z + r * 0.06), BLACK(), (1, 0.6, 1.2))
        sphere(r * 0.035, (x + sx * r * 0.32, y - r * 1.0, z + r * 0.12), WHITE())
        sphere(r * 0.16, (x + sx * r * 0.98, y, z), skin, (0.5, 0.8, 1))  # orejas
        if brows:
            box((r * 0.32, r * 0.08, r * 0.08), (x + sx * r * 0.36, y - r * 0.9, z + r * 0.36), HAIR(),
                rot=(0, R(-12 * sx), 0), bevel=0.01)
    sphere(r * 0.13, (x, y - r * 1.0, z - r * 0.12), skin)  # nariz
    if mouth:
        box((r * 0.3, r * 0.05, r * 0.05), (x, y - r * 0.92, z - r * 0.38), mat("Boca", "8a3a2a"),
            bevel=0.01)


def legs(pants=None, boots=None, toe=None, spread=0.13, z_top=0.55):
    pants = pants or PANTS()
    boots = boots or LEATHER()
    for sx in (-1, 1):
        x = sx * spread
        cyl(0.1, 0.095, z_top - 0.22, (x, 0, 0.22 + (z_top - 0.22) / 2), pants, sub=0)
        cyl(0.115, 0.12, 0.24, (x, 0, 0.12), boots, bevel=0.01)
        cyl(0.135, 0.13, 0.07, (x, 0, 0.25), boots)  # doblez de la bota
        sphere(0.11, (x, -0.08, 0.06), toe or boots, (1, 1.35, 0.6))


def torso(m, z=0.84, w=1.0, d=0.82, h=1.05, r=0.34):
    return sphere(r, (0, 0, z), m, (w, d, h), sub=1)


def arm(sx, sleeve, skin=None, hand=None, glove=None, down=True, hand_pos=None):
    """Brazo: hombro, manga, antebrazo y mano. hand_pos permite moverla (para sujetar cosas)."""
    skin = skin or SKIN()
    sphere(0.13, (sx * 0.37, 0, 0.98), sleeve)
    hp = Vector(hand_pos) if hand_pos else Vector((sx * 0.42, -0.04, 0.58))
    sh = Vector((sx * 0.38, 0, 0.95))
    tube([tuple(sh), tuple((sh + hp) / 2 + Vector((sx * 0.03, 0, 0))), tuple(hp + Vector((0, 0, 0.06)))],
         0.075, sleeve)
    sphere(0.09, tuple(hp), glove or skin, (1, 1, 1.05))
    return hp


def belt(z=0.62, r=0.31, color=None, buckle=None):
    cyl(r, r, 0.07, (0, 0, z), color or LEATHER(), v=32)
    box((0.11, 0.04, 0.08), (0, -r, z), buckle or GOLD(), bevel=0.01)


# --- Armas y accesorios ----------------------------------------------------------------

def sword(base, length=0.62, rot=(R(-80), 0, R(-10)), blade=None, wide=0.09):
    """Espada cuya empuñadura está en 'base'."""
    o = Vector(base)
    grp = []
    grp.append(box((wide, 0.03, length), (0, 0, length / 2 + 0.08), blade or STEEL(), bevel=0.012))
    grp.append(cyl(0.0, wide * 0.72, 0.1, (0, 0, length + 0.13), blade or STEEL(), v=4, rot=(0, 0, R(45))))
    grp.append(box((0.22, 0.05, 0.045), (0, 0, 0.07), GOLD(), bevel=0.01))
    grp.append(cyl(0.025, 0.025, 0.14, (0, 0, -0.01), LEATHER_D()))
    grp.append(sphere(0.04, (0, 0, -0.09), GOLD()))
    _group(grp, o, rot)


def _group(objs, loc, rot):
    """Mueve y gira un grupo de piezas armadas alrededor del origen."""
    from mathutils import Matrix, Euler
    mtx = Matrix.Translation(Vector(loc)) @ Euler(rot).to_matrix().to_4x4()
    for ob in objs:
        ob.matrix_world = mtx @ ob.matrix_world


def round_shield(loc, r=0.3, face=None, rim=None, spikes=True, rot=(R(90), 0, 0)):
    grp = [cyl(r, r, 0.06, (0, 0, 0), face or TRIBU(), v=40, bevel=0.01),
           torus(r, 0.03, (0, 0, 0), rim or STEEL_D())]
    grp.append(sphere(0.08, (0, 0, 0.04), STEEL(), (1, 1, 0.6)))
    if spikes:
        for k in range(8):
            a = k * math.tau / 8
            grp.append(cyl(0.03, 0.0, 0.07, (math.cos(a) * r * 0.75, math.sin(a) * r * 0.75, 0.05), STEEL(), v=8))
    _group(grp, loc, rot)


def plume(loc, color=None, size=1.0):
    color = color or TRIBU()
    for i, (dx, dz, s) in enumerate([(0, 0, 1.0), (0.02, 0.06, 0.85), (-0.02, 0.1, 0.7)]):
        sphere(0.07 * size * s, (loc[0] + dx, loc[1] + 0.04 * i, loc[2] + dz * size), color,
               (0.7, 1.4, 1.2), rot=(R(-25), 0, 0))


def knight_helmet(z, r=0.3, open_face=False):
    """Casco de caballero con rejilla y penacho."""
    cyl(r * 1.06, r * 1.0, r * 0.75, (0, 0.02, z + r * 0.25), STEEL(), v=32)
    sphere(r * 1.02, (0, 0.02, z + r * 0.55), STEEL(), (1, 1, 0.72))
    if open_face:
        # Visera con rejilla levantada sobre la frente y protectores de mejillas
        box((r * 1.3, 0.08, r * 0.3), (0, -r * 0.98, z + r * 0.62), STEEL(), bevel=0.02)
        for x in (-0.1, -0.035, 0.035, 0.1):
            box((0.03, 0.03, r * 0.22), (x, -r * 1.05, z + r * 0.62), BLACK(), bevel=0.005)
        for sx in (-1, 1):
            box((0.06, r * 0.5, r * 0.55), (sx * r * 0.95, -r * 0.35, z - r * 0.05), STEEL(), bevel=0.02)
    else:
        box((r * 1.2, 0.05, r * 0.12), (0, -r * 1.02, z + r * 0.25), STEEL_D(), bevel=0.01)
        for x in (-0.09, 0, 0.09):
            box((0.03, 0.04, r * 0.32), (x, -r * 1.03, z + r * 0.18), STEEL_D(), bevel=0.005)
    plume((0, 0.05, z + r * 1.1))


def mark():
    return set(C["col"].objects)


def shift_since(before, offset):
    """Mueve todo lo creado desde 'before' (para subir al jinete al caballo, etc.)."""
    for o in C["col"].objects:
        if o not in before:
            o.location += Vector(offset)


def horse(coat, mane, armor=False):
    """Caballo mirando hacia -Y; el lomo queda a z ~1.1."""
    sphere(0.38, (0, 0.05, 0.8), coat, (0.78, 1.45, 0.8), sub=1)
    for sx in (-1, 1):
        for y in (-0.33, 0.42):
            cyl(0.095, 0.08, 0.6, (sx * 0.17, y, 0.34), coat)
            cyl(0.085, 0.085, 0.1, (sx * 0.17, y, 0.05), BLACK(), bevel=0.01)
    cyl(0.15, 0.12, 0.5, (0, -0.46, 1.06), coat, rot=(R(-35), 0, 0), sub=1)       # cuello
    sphere(0.17, (0, -0.68, 1.27), coat, (0.8, 1.55, 0.85), rot=(R(25), 0, 0), sub=1)  # cabeza
    sphere(0.13, (0, -0.86, 1.15), coat, (0.95, 1.0, 0.9))                         # hocico
    for sx in (-1, 1):
        sphere(0.04, (sx * 0.12, -0.7, 1.33), BLACK())
        cyl(0.045, 0.0, 0.13, (sx * 0.07, -0.58, 1.47), coat, rot=(R(-15), R(sx * 12), 0), v=8)
        sphere(0.02, (sx * 0.05, -0.97, 1.13), BLACK())
    box((0.06, 0.42, 0.12), (0, -0.42, 1.24), mane, rot=(R(-38), 0, 0), bevel=0.03, smooth=True)  # crin
    tube([(0, 0.6, 0.95), (0, 0.78, 0.75), (0, 0.76, 0.45)], 0.06, mane)          # cola
    cyl(0.3, 0.3, 0.08, (0, 0.02, 1.1), TRIBU(), v=32)                              # silla
    box((0.62, 0.42, 0.04), (0, 0.02, 1.06), TRIBU_D(), bevel=0.02)                 # manta
    if armor:
        sphere(0.4, (0, -0.15, 0.85), STEEL(), (0.82, 0.7, 0.75), sub=1)            # pechera
        sphere(0.18, (0, -0.7, 1.31), STEEL(), (0.84, 1.3, 0.75), rot=(R(25), 0, 0), sub=1)  # testera
        cyl(0.4, 0.45, 0.35, (0, 0.08, 0.68), TRIBU(), v=32)                         # gualdrapa


def rider_legs(pants, boots):
    for sx in (-1, 1):
        tube([(sx * 0.15, 0, 1.15), (sx * 0.34, -0.08, 1.0), (sx * 0.33, -0.1, 0.78)], 0.085, pants)
        cyl(0.1, 0.11, 0.2, (sx * 0.33, -0.1, 0.7), boots)
        sphere(0.095, (sx * 0.33, -0.18, 0.62), boots, (1, 1.4, 0.6))


def export_unit():
    """Convierte todo en una sola malla y la guarda como .glb en assets/tropas."""
    col = C["col"]
    bpy.ops.object.select_all(action="DESELECT")
    objs = list(col.objects)
    for o in objs:
        o.hide_set(False)
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = C["name"]
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    os.makedirs(EXPORT_DIR, exist_ok=True)
    path = os.path.join(EXPORT_DIR, C["name"].lower() + ".glb")
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True)
    return path, len(o.data.polygons)
