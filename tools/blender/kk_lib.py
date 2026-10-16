# Arma tropas de Kolonia sobre los personajes KayKit (esqueleto "Rig_Medium").
#
# Idea: el cuerpo (cabeza, brazos, piernas) sale de KayKit Adventurers y ya trae
# esqueleto, así que todas las tropas comparten las mismas animaciones. Encima se
# agregan piezas propias (cascos, plumas, capas, caballos...) hechas con kolonia_lib.
# Cada pieza propia se "pega" a un hueso (cabeza, pecho...) para que se mueva con él.
#
# Al final todo se pinta con UNA textura (atlas):
#   - mitad izquierda: la textura KayKit del personaje, con las zonas del color de la
#     tribu pasadas a gris.
#   - mitad derecha: una paleta con un cuadro (degradado) por cada color de las piezas propias.
# y DOS materiales: "K_Base" y "K_Tribu". Godot multiplica "K_Tribu" por el color del
# jugador, así que el gris se vuelve rojo, azul, etc.
import bpy, bmesh, math, os, colorsys
from mathutils import Vector, Matrix
import kolonia_lib as K

ROOT = os.environ.get("KOLONIA_ROOT", r"C:\Personal\Kolonia")
EXTRAS = os.environ.get("KOLONIA_EXTRAS", os.path.join(ROOT, "assets", "Extras"))
OUT = os.environ.get("KOLONIA_OUT", os.path.join(ROOT, "assets", "tropas"))
KK = os.path.join(EXTRAS, "KayKit_Adventurers_2.0_FREE")
KK_SKELETONS = os.path.join(EXTRAS, "KayKit_Skeletons_1.1_FREE", "characters", "gltf")

# Zonas (en cuadros de 128 px) de cada textura KayKit que toman el color de la tribu.
TEAM_CELLS = {
    "knight": [(0, 2), (0, 3), (2, 4), (2, 5)],
    "ranger": [(0, 2), (0, 3), (1, 4), (1, 5)],
    "rogue": [(0, 2), (0, 3), (1, 2), (1, 3), (1, 4), (1, 5)],
    "mage": [(0, 2), (0, 3), (1, 2), (1, 3), (7, 2), (7, 3), (2, 2), (2, 3), (1, 4), (1, 5)],
    "barbarian": [(0, 2), (0, 3)],
    "skeleton": [],
}
ATLAS_W, ATLAS_H = 2048, 1024
CELL_W, CELL_H = 128, 256          # cuadros de la paleta propia (8 x 4)

S = {}


def reset(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = 30
    K.C.clear()
    K.new_unit(name)
    S.clear()
    S.update(name=name, acc=[], static=[], kk=[], arm=None, tex=None)


def load_char(char, keep):
    """Importa un personaje KayKit y deja solo las partes de 'keep'
    (sufijos como "Head", "Body", "ArmLeft"...). Los esqueletos (Skeleton_*) salen
    del paquete KayKit Skeletons, que usa el mismo esqueleto Rig_Medium."""
    skeleton = char.startswith("Skeleton_")
    folder = KK_SKELETONS if skeleton else os.path.join(KK, "Characters", "gltf")
    path = os.path.join(folder, char + ".glb")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    arm = None
    for o in new:
        if o.type == "ARMATURE":
            arm = o
    for o in new:
        if o.type != "MESH":
            continue
        suffix = o.name.rsplit("_", 1)[-1] if "_" in o.name else o.name
        if o.parent != arm or suffix not in keep:
            bpy.data.objects.remove(o, do_unlink=True)
        else:
            S["kk"].append(o)
    arm.name = "Rig_Medium"
    arm.data.name = "Rig_Medium"
    S["arm"] = arm
    S["tex_name"] = char.lower().split("_")[0]
    S["tex"] = os.path.join(folder, S["tex_name"] + "_texture.png")
    return arm


def bone_pos(bone, at="head"):
    arm = S["arm"]
    b = arm.data.bones[bone]
    return arm.matrix_world @ (b.head_local if at == "head" else b.tail_local)


def kk_bounds(part):
    """Caja (min, max) de una parte KayKit, para acomodar sombreros, etc."""
    for o in S["kk"]:
        if o.name.endswith(part):
            pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
            return (Vector([min(p[i] for p in pts) for i in range(3)]),
                    Vector([max(p[i] for p in pts) for i in range(3)]))
    return None


def on_bone(objs, bone, world=False):
    """Piezas propias que se mueven con un hueso.
    world=True: la pieza ya está en su lugar final (no se mueve con move_rig)."""
    for o in objs:
        o["bone"] = bone
        o["world"] = world
        S["acc"].append(o)


def add_bones(specs, reparent=None):
    """Agrega huesos propios al esqueleto (por ejemplo, el caballo).
    specs: [(nombre, cabeza_mundo, cola_mundo, padre)]; reparent: {hueso_existente: nuevo_padre}."""
    arm = S["arm"]
    off = arm.location.copy()
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.data.edit_bones
    for name, head, tail, parent in specs:
        b = eb.new(name)
        b.head = Vector(head) - off
        b.tail = Vector(tail) - off
        if parent:
            b.parent = eb[parent]
    for child, parent in (reparent or {}).items():
        eb[child].use_connect = False
        eb[child].parent = eb[parent]
    bpy.ops.object.mode_set(mode="OBJECT")


def since(before):
    return [o for o in K.C["col"].objects if o not in before]


def static(objs):
    """Piezas que no se animan con el esqueleto (caballo, catapulta, bote)."""
    for o in objs:
        S["static"].append(o)


def scale_objs(objs, f, pivot=(0, 0, 0)):
    m = Matrix.Translation(Vector(pivot)) @ Matrix.Scale(f, 4) @ Matrix.Translation(-Vector(pivot))
    for o in objs:
        o.matrix_world = m @ o.matrix_world


def move_rig(offset):
    """Mueve el esqueleto entero (por ejemplo, para subir al jinete al caballo)."""
    S["arm"].location = Vector(offset)
    S["rig_offset"] = Vector(offset)


# ---------------------------------------------------------------------------------------
# Textura (atlas)

def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def recolor(cells_hex):
    """Repinta cuadros de la textura KayKit: {(cx, cy): "rrggbb"} (ver cuadros en la textura)."""
    S.setdefault("recolor", {}).update(cells_hex)


def _srgb(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _mat_rgb(m):
    b = m.node_tree.nodes.get("Principled BSDF") if m.use_nodes else None
    col = b.inputs["Base Color"].default_value if b else m.diffuse_color
    return [_srgb(col[i]) for i in range(3)]


def _build_atlas(flat_mats):
    """Crea la imagen del atlas y devuelve {nombre_material: (u, v0, v1)}."""
    import numpy as np
    W, H = ATLAS_W, ATLAS_H
    px = np.ones((H, W, 4), dtype=np.float32)
    # KayKit (mitad izquierda), con las zonas de tribu en gris
    if S["tex"]:
        img = bpy.data.images.load(S["tex"])
        a = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)  # abajo->arriba
        a = a[::-1]  # arriba->abajo
        assert a.shape[0] == 1024 and a.shape[1] == 1024
        # Cada tribu puede repintar cuadros de la textura KayKit (piel, ropa, metal...)
        # conservando el degradado: {(cx, cy): "rrggbb"}
        for (cx, cy), hexrgb in S.get("recolor", {}).items():
            blk = a[cy * 128:(cy + 1) * 128, cx * 128:(cx + 1) * 128, :3]
            v = blk.max(axis=2)
            vmax = max(float(v.max()), 1e-3)
            g = np.clip(v / vmax, 0, 1)[..., None]
            rgb = np.array([int(hexrgb[i:i + 2], 16) / 255 for i in (0, 2, 4)], dtype=np.float32)
            a[cy * 128:(cy + 1) * 128, cx * 128:(cx + 1) * 128, :3] = np.clip(g * rgb * 1.08, 0, 1)
        for (cx, cy) in _team_list():
            blk = a[cy * 128:(cy + 1) * 128, cx * 128:(cx + 1) * 128, :3]
            v = blk.max(axis=2)
            vmax = max(float(v.max()), 1e-3)
            g = np.clip(v / vmax * 0.97, 0, 1)
            a[cy * 128:(cy + 1) * 128, cx * 128:(cx + 1) * 128, :3] = g[..., None]
        px[:, :1024] = a
        bpy.data.images.remove(img)
    # Paleta propia (mitad derecha): degradado claro arriba -> oscuro abajo
    cells = {}
    for i, m in enumerate(flat_mats):
        cx, cy = i % 8, i // 8
        assert cy < 4, "demasiados colores"
        rgb = _mat_rgb(m)
        team = m.name.startswith("K_Tribu")
        if team:
            base = 0.62 if m.name.startswith("K_TribuOscuro") else 0.97
            rgb = [base] * 3
        x0, y0 = 1024 + cx * CELL_W, cy * CELL_H
        for y in range(CELL_H):
            t = y / (CELL_H - 1)
            f = 1.12 - 0.42 * t            # un poco más claro arriba, más oscuro abajo
            px[y0 + y, x0:x0 + CELL_W, :3] = [min(1.0, c * f) for c in rgb]
        u = (x0 + CELL_W / 2) / W
        cells[m] = (u, (y0 + 20) / H, (y0 + CELL_H - 20) / H)
    img = bpy.data.images.new(S["name"] + "_atlas", W, H, alpha=False)
    img.pixels[:] = px[::-1].reshape(-1)
    img.file_format = "PNG"
    img.pack()
    return img, cells


def _materials(img):
    out = []
    for name, rough in (("K_Base", 0.85), ("K_Tribu", 0.8)):
        old = bpy.data.materials.get(name)
        if old:
            old.name = name + "_plano"
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        b = nt.nodes["Principled BSDF"]
        b.inputs["Roughness"].default_value = rough
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = img
        nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
        out.append(m)
    return out


def _team_list():
    if "team_only" in S:     # la tribu decide qué cuadros de la textura toman su color
        return list(S["team_only"])
    return list(TEAM_CELLS.get(S.get("tex_name", ""), [])) + list(S.get("team_extra", []))


def _team_cell_set():
    return set(_team_list())


def _prep_acc(o, cells):
    """Convierte una pieza propia en malla con UV en la paleta."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    if o.type != "MESH":
        bpy.ops.object.convert(target="MESH")
        o = bpy.context.object
    for md in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=md.name)
    o.data.transform(o.matrix_world)
    o.matrix_world = Matrix()
    me = o.data
    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])
    uv = me.uv_layers.new(name="UVMap")
    zs = [v.co.z for v in me.vertices] or [0]
    z0, z1 = min(zs), max(zs)
    span = max(z1 - z0, 1e-4)
    team_flags = []
    for p in me.polygons:
        m = me.materials[p.material_index] if me.materials else None
        u, va, vb = cells[m]
        for li in p.loop_indices:
            z = me.vertices[me.loops[li].vertex_index].co.z
            t = 1 - (z - z0) / span          # arriba claro
            uv.data[li].uv = (u, 1 - (va + (vb - va) * t))
        team_flags.append(m.name.startswith("K_Tribu"))
    return o, team_flags


def _assign(o, flags, mats):
    me = o.data
    me.materials.clear()
    for m in mats:
        me.materials.append(m)
    for p, f in zip(me.polygons, flags):
        p.material_index = 1 if f else 0


def _join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def finalize():
    arm = S.get("arm")
    acc, static_objs = S["acc"], S["static"]
    # Las piezas sin hueso ni "static" se pegan al pecho (o quedan fijas si no hay esqueleto)
    for o in list(K.C["col"].objects):
        if o not in acc and o not in static_objs:
            if arm:
                o["bone"] = "chest"
                acc.append(o)
            else:
                static_objs.append(o)
    flat = []
    for o in acc + static_objs:
        for m in o.data.materials:
            if m and m not in flat:
                flat.append(m)
    img, cells = _build_atlas(flat)
    mats = _materials(img)
    teams = _team_cell_set()

    parts = []
    for o in S["kk"]:
        me = o.data
        uv = me.uv_layers.active
        flags = []
        for p in me.polygons:
            cu = sum(uv.data[li].uv[0] for li in p.loop_indices) / p.loop_total
            cv = sum(uv.data[li].uv[1] for li in p.loop_indices) / p.loop_total
            cell = (min(7, int(cu * 8)), min(7, int((1 - cv) * 8)))
            flags.append(cell in teams)
        for d in uv.data:
            d.uv[0] *= 0.5
        uv.name = "UVMap"
        _assign(o, flags, mats)
        parts.append(o)

    skinned = []
    for o in acc:
        if S.get("rig_offset") and not o.get("world"):
            o.location += S["rig_offset"]
        bone = o.get("bone", "chest")
        o2, flags = _prep_acc(o, cells)
        _assign(o2, flags, mats)
        vg = o2.vertex_groups.new(name=bone)
        vg.add(list(range(len(o2.data.vertices))), 1.0, "REPLACE")
        skinned.append(o2)

    body = None
    if parts or skinned:
        first = (parts + skinned)[0]
        if not parts:
            md = first.modifiers.new("Armature", "ARMATURE")
            md.object = arm
            first.parent = arm
        body = _join(parts + skinned, S["name"])

    st = None
    if static_objs:
        prepared = []
        for o in static_objs:
            o2, flags = _prep_acc(o, cells)
            _assign(o2, flags, mats)
            prepared.append(o2)
        st = _join(prepared, S["name"] + "_fijo")
    return body, st


def pose_action(name, bone_rots, root_offset=(0, 0, 0)):
    """Crea una pose fija (acción de 2 cuadros) girando huesos.
    bone_rots: {hueso: (eje 'X'|'Y'|'Z' en espacio del esqueleto, grados)}."""
    arm = S["arm"]
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="POSE")
    act = bpy.data.actions.new(name)
    arm.animation_data_create()
    arm.animation_data.action = act
    order = []

    def walk(b):
        order.append(b.name)
        for c in b.children:
            walk(c)
    for b in arm.data.bones:
        if b.parent is None:
            walk(b)
    for bn in order:
        pb = arm.pose.bones[bn]
        if bn in bone_rots:
            rots = bone_rots[bn]
            if isinstance(rots, tuple):
                rots = [rots]
            m = pb.matrix.copy()
            loc = m.to_translation()
            r = Matrix()
            for axis, deg in rots:
                r = Matrix.Rotation(math.radians(deg), 4, axis) @ r
            m = Matrix.Translation(loc) @ r @ Matrix.Translation(-loc) @ m
            pb.matrix = m
            bpy.context.view_layer.update()
        if bn == "root" and any(root_offset):
            pb.location = (0, 0, 0)
            m = pb.matrix.copy()
            m.translation += Vector(root_offset)
            pb.matrix = m
            bpy.context.view_layer.update()
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        for f in (1, 30):
            pb.keyframe_insert("rotation_quaternion", frame=f)
            pb.keyframe_insert("location", frame=f)
    bpy.ops.object.mode_set(mode="OBJECT")
    return act


def export(file_name, animations=False):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, file_name + ".glb")
    bpy.ops.object.select_all(action="SELECT")
    for o in bpy.context.scene.objects:
        if o.type not in ("MESH", "ARMATURE"):
            o.select_set(False)
    kw = dict(filepath=path, export_format="GLB", use_selection=True, export_apply=False,
              export_animations=animations)
    try:
        bpy.ops.export_scene.gltf(export_image_format="AUTO", **kw)
    except TypeError:
        bpy.ops.export_scene.gltf(**kw)
    return path


# ---------------------------------------------------------------------------------------
# Armas (para pegarlas en la mano dentro de Godot, hueso "handslot.r" / "handslot.l")

def export_weapon(src_name, out_name, team_cells=None, tex="knight", extra=None):
    """Pasa un arma KayKit al formato Kolonia (textura + K_Tribu)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    K.C.clear()
    path = os.path.join(KK, "Assets", "gltf", src_name + ".gltf")
    bpy.ops.import_scene.gltf(filepath=path)
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    S.clear()
    S.update(name=out_name, tex=os.path.join(KK, "Assets", "gltf", tex + "_texture.png"), tex_name=tex,
             team_extra=extra or [])
    if team_cells is not None:
        TEAM_CELLS[tex] = team_cells
    img, cells = _build_atlas([])
    mats = _materials(img)
    teams = _team_cell_set()
    for o in objs:
        me = o.data
        uv = me.uv_layers.active
        flags = []
        for p in me.polygons:
            cu = sum(uv.data[li].uv[0] for li in p.loop_indices) / p.loop_total
            cv = sum(uv.data[li].uv[1] for li in p.loop_indices) / p.loop_total
            flags.append((min(7, int(cu * 8)), min(7, int((1 - cv) * 8))) in teams)
        for d in uv.data:
            d.uv[0] *= 0.5
        _assign(o, flags, mats)
    os.makedirs(os.path.join(OUT, "armas"), exist_ok=True)
    p = os.path.join(OUT, "armas", out_name + ".glb")
    bpy.ops.export_scene.gltf(filepath=p, export_format="GLB")
    return p


def export_custom_weapon(name, build):
    """Arma hecha con piezas propias. Se modela en Blender con la hoja hacia +Z y el
    mango en el origen (así queda igual que las armas KayKit al pegarla a la mano)."""
    reset(name)
    build()
    finalize()
    os.makedirs(os.path.join(OUT, "armas"), exist_ok=True)
    p = os.path.join(OUT, "armas", name + ".glb")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=p, export_format="GLB", use_selection=True)
    return p
