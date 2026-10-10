# Cada función arma una tropa (usa kolonia_lib).

def caballero():
    new_unit("Caballero")
    legs(PANTS(), LEATHER(), STEEL())
    cyl(0.27, 0.29, 0.14, (0, 0, 0.56), PANTS())
    torso(TRIBU(), z=0.82, w=0.95, d=0.8)
    sphere(0.34, (0, -0.03, 0.85), STEEL(), (1.05, 0.85, 0.98), sub=1)   # peto
    box((0.42, 0.02, 0.025), (0, -0.3, 0.86), STEEL_D(), bevel=0.005)
    belt(0.62, 0.31)
    box((0.2, 0.03, 0.26), (0, -0.3, 0.47), TRIBU(), bevel=0.01)          # faldón
    for sx in (-1, 1):
        hp = arm(sx, TRIBU(), glove=LEATHER(), hand_pos=(sx * 0.44, -0.16, 0.64) if sx > 0 else None)
        cyl(0.1, 0.11, 0.16, (hp.x, hp.y + 0.02, hp.z + 0.12), STEEL(), bevel=0.01)
    head(1.3, 0.3)
    knight_helmet(1.3, 0.3, open_face=True)
    sword((0.44, -0.16, 0.64), 0.58, rot=(R(-55), 0, R(-20)), wide=0.11)


def escudero():
    new_unit("Escudero")
    legs(TRIBU(), TRIBU_D(), TRIBU_D(), spread=0.15)
    cyl(0.3, 0.31, 0.14, (0, 0, 0.56), CHAIN())
    for k in range(5):
        sphere(0.08, (-0.2 + k * 0.1, -0.25, 0.5), CHAIN(), (1, 0.6, 1.2))
    torso(TRIBU(), z=0.84, w=1.12, d=0.9, h=1.0, r=0.36)
    box((0.42, 0.04, 0.03), (0, -0.31, 0.92), TRIBU_D(), bevel=0.005)
    belt(0.64, 0.33)
    for sx in (-1, 1):
        sphere(0.17, (sx * 0.42, 0, 1.02), TRIBU(), (1, 1, 0.85))
        cyl(0.04, 0.0, 0.1, (sx * 0.5, 0, 1.13), STEEL(), rot=(0, R(sx * 40), 0), v=8)
        arm(sx, TRIBU(), glove=TRIBU_D())
    cyl(0.32, 0.3, 0.52, (0, 0, 1.36), TRIBU(), v=32, bevel=0.02)          # casco cubeta
    sphere(0.3, (0, 0, 1.62), TRIBU(), (1.05, 1.05, 0.35))
    box((0.36, 0.06, 0.07), (0, -0.3, 1.38), BLACK(), bevel=0.01)
    box((0.06, 0.06, 0.3), (0, -0.31, 1.28), TRIBU_D(), bevel=0.01)
    for sx in (-1, 1):
        box((0.1, 0.05, 0.035), (sx * 0.1, -0.32, 1.47), TRIBU_D(), rot=(0, R(-15 * sx), 0), bevel=0.01)  # ceño
    round_shield((-0.5, -0.22, 0.78), 0.34, rot=(R(90), 0, R(-25)))


def arquero():
    new_unit("Arquero")
    legs(PANTS(), LEATHER(), LEATHER())
    cyl(0.25, 0.27, 0.14, (0, 0, 0.56), PANTS())
    torso(LEATHER(), z=0.82, w=0.95, d=0.82)
    box((0.08, 0.03, 0.45), (0, -0.28, 0.83), LEATHER_D(), rot=(0, R(35), 0), bevel=0.01)
    belt(0.62, 0.29)
    cyl(0.36, 0.48, 0.75, (0, 0.12, 0.72), TRIBU(), v=32, sub=1)            # capa
    sphere(0.36, (0, 0.06, 1.0), TRIBU(), (1.05, 0.85, 0.5), sub=1)
    for sx in (-1, 1):
        arm(sx, LEATHER(), glove=LEATHER_D(), hand_pos=(sx * 0.45, -0.2, 0.75) if sx < 0 else None)
    sphere(0.33, (0, 0.12, 1.38), TRIBU(), (1.0, 1.0, 1.05), sub=1)        # capucha (atrás de la cara)
    head(1.3, 0.28)
    torus(0.27, 0.05, (0, -0.16, 1.33), TRIBU(), rot=(R(80), 0, 0))       # borde de la capucha
    cyl(0.04, 0.0, 0.25, (0, 0.3, 1.62), TRIBU(), rot=(R(40), 0, 0), v=12)
    tube([(-0.48, -0.2, 1.25), (-0.62, -0.28, 0.76), (-0.48, -0.2, 0.27)], 0.03, WOOD_D())
    tube([(-0.48, -0.2, 1.25), (-0.44, -0.16, 0.76), (-0.48, -0.2, 0.27)], 0.006, WHITE(), smooth_curve=False)
    cyl(0.09, 0.08, 0.45, (0.12, 0.3, 1.0), LEATHER_D(), rot=(R(-15), R(20), 0))
    for k in range(3):
        cyl(0.012, 0.012, 0.25, (0.08 + k * 0.04, 0.36, 1.32), WOOD(), rot=(R(-15), R(20), 0))
        cyl(0.04, 0.0, 0.08, (0.08 + k * 0.04, 0.4, 1.46), TRIBU(), rot=(R(-15), R(20), 0), v=4)


def _rider_upper(top, sleeve, glove, helmet):
    """Torso, brazos y cabeza del jinete a la altura normal (después se sube al caballo)."""
    torso(top, z=0.82, w=0.92, d=0.8)
    belt(0.62, 0.29)
    hands = []
    for sx in (-1, 1):
        hands.append(arm(sx, sleeve, glove=glove, hand_pos=(sx * 0.3, -0.3, 0.7)))
    head(1.3, 0.28)
    helmet()
    return hands


def jinete():
    new_unit("Jinete")
    horse(mat("Caballo", "8a5230", 0.75), mat("Crin", "3a2416", 0.8))
    m = mark()
    sphere(0.3, (0, 0, 0.82), CHAIN(), (1.0, 0.85, 1.05), sub=1)             # malla
    def helm():
        sphere(0.3, (0, 0.02, 1.43), STEEL(), (1.05, 1.05, 0.75))
        cyl(0.36, 0.36, 0.03, (0, 0.02, 1.38), STEEL(), v=32)
        plume((0, 0.05, 1.63), size=0.8)
    _rider_upper(TRIBU(), CHAIN(), LEATHER(), helm)
    shift_since(m, (0, 0.05, 0.55))
    rider_legs(PANTS(), LEATHER())
    sword((0.32, -0.25, 1.25), 0.5, rot=(R(-35), 0, R(-35)))


def jinete_lancero():
    new_unit("Jinete_lancero")
    horse(mat("CaballoGris", "5f6268", 0.7), BLACK(), armor=True)
    m = mark()
    def helm():
        knight_helmet(1.3, 0.28)
    hands = _rider_upper(STEEL(), STEEL(), STEEL_D(), helm)
    box((0.06, 0.02, 0.32), (0, -0.27, 0.86), TRIBU(), bevel=0.005)          # cruz roja
    box((0.26, 0.02, 0.06), (0, -0.27, 0.92), TRIBU(), bevel=0.005)
    shift_since(m, (0, 0.05, 0.55))
    rider_legs(STEEL_D(), STEEL())
    # lanza con banderín
    cyl(0.03, 0.03, 2.0, (0.34, -0.4, 1.6), WOOD_D(), rot=(R(-12), 0, 0))
    cyl(0.07, 0.0, 0.3, (0.34, -0.61, 2.62), STEEL(), rot=(R(-12), 0, 0), v=8)
    cyl(0.08, 0.08, 0.12, (0.34, -0.21, 0.92), STEEL(), rot=(R(-12), 0, 0))
    box((0.02, 0.3, 0.16), (0.34, -0.45, 2.38), TRIBU(), rot=(R(-12), 0, 0), bevel=0.0)


def catapulta():
    new_unit("Catapulta")
    for sx in (-1, 1):
        box((0.08, 1.1, 0.1), (sx * 0.35, 0, 0.3), WOOD(), bevel=0.015)        # largueros
        box((0.08, 0.08, 1.05), (sx * 0.3, -0.05, 0.85), WOOD(), bevel=0.015)  # postes
        for y in (-0.38, 0.38):
            cyl(0.17, 0.17, 0.07, (sx * 0.45, y, 0.18), WOOD_D(), rot=(0, R(90), 0), v=24, bevel=0.01)
            cyl(0.06, 0.06, 0.09, (sx * 0.45, y, 0.18), STEEL_D(), rot=(0, R(90), 0))
            torus(0.17, 0.02, (sx * 0.49, y, 0.18), STEEL_D(), rot=(0, R(90), 0))
    for y in (-0.45, 0.45):
        box((0.78, 0.09, 0.09), (0, y, 0.3), WOOD(), bevel=0.015)
    box((0.7, 0.1, 0.12), (0, -0.05, 1.35), WOOD(), bevel=0.015)               # travesaño
    cyl(0.12, 0.12, 0.6, (0, 0.2, 0.42), WOOD_D(), rot=(0, R(90), 0))          # tambor
    for k in range(5):
        torus(0.13, 0.025, (-0.2 + k * 0.1, 0.2, 0.42), mat("Cuerda", "c9a86a"), rot=(0, R(90), 0))
    box((0.09, 0.09, 1.25), (0, 0.15, 0.95), WOOD_D(), rot=(R(-30), 0, 0), bevel=0.015)  # brazo
    sphere(0.17, (0, -0.18, 1.5), WOOD_D(), (1, 1, 0.55))                      # cuchara
    sphere(0.15, (0, -0.18, 1.6), mat("Roca", "8c8c8c", 0.9), sub=1)
    box((0.7, 0.05, 0.18), (0, -0.5, 0.42), TRIBU(), bevel=0.01)               # tela roja
    # el operador al lado
    m = mark()
    legs(PANTS(), LEATHER())
    cyl(0.25, 0.27, 0.14, (0, 0, 0.56), PANTS())
    torso(TRIBU(), z=0.82, w=0.85, d=0.75)
    for sx in (-1, 1):
        arm(sx, TRIBU(), glove=LEATHER(), hand_pos=(sx * 0.3, -0.3, 0.75))
    head(1.28, 0.26)
    sphere(0.27, (0, 0.02, 1.4), LEATHER(), (1.05, 1.05, 0.65))               # gorro de cuero
    plume((0, 0.05, 1.58), size=0.6)
    shift_since(m, (0.75, 0.35, 0.0))


def capitan():
    new_unit("Capitan")
    # pierna normal y pata de palo
    cyl(0.1, 0.095, 0.33, (-0.13, 0, 0.38), PANTS())
    cyl(0.115, 0.12, 0.3, (-0.13, 0, 0.15), BLACK(), bevel=0.01)
    sphere(0.11, (-0.13, -0.08, 0.06), BLACK(), (1, 1.35, 0.6))
    cyl(0.1, 0.095, 0.2, (0.13, 0, 0.45), PANTS())
    cyl(0.05, 0.035, 0.36, (0.13, 0, 0.18), WOOD(), bevel=0.01)
    cyl(0.29, 0.38, 0.62, (0, 0.04, 0.6), TRIBU(), v=32, sub=1)                 # casaca larga
    torso(TRIBU(), z=0.85, w=1.0, d=0.85)
    box((0.22, 0.03, 0.5), (0, -0.3, 0.8), LEATHER_D(), bevel=0.01)            # chaleco
    for sx in (-1, 1):
        box((0.035, 0.02, 0.5), (sx * 0.12, -0.31, 0.8), GOLD(), bevel=0.005)
    cyl(0.31, 0.31, 0.09, (0, 0, 0.66), TRIBU_D(), v=32)                       # faja
    belt(0.72, 0.3)
    hpr = arm(1, TRIBU(), glove=SKIN(), hand_pos=(0.44, -0.12, 0.62))
    arm(-1, TRIBU(), glove=STEEL(), hand_pos=(-0.44, -0.08, 0.62))
    tube([(-0.44, -0.08, 0.56), (-0.44, -0.16, 0.48), (-0.44, -0.12, 0.42)], 0.02, STEEL())  # garfio
    head(1.3, 0.3)
    sphere(0.24, (0, -0.16, 1.14), WHITE(), (1.1, 0.75, 1.1), sub=1)            # barba
    box((0.2, 0.04, 0.05), (0, -0.29, 1.24), WHITE(), bevel=0.02)              # bigote
    sphere(0.07, (0.11, -0.3, 1.33), BLACK(), (1, 0.4, 1))                     # parche
    box((0.5, 0.01, 0.02), (0, -0.25, 1.4), BLACK(), rot=(0, R(20), 0))
    # tricornio
    cyl(0.42, 0.42, 0.05, (0, 0, 1.55), BLACK(), v=3, rot=(0, 0, R(30)), bevel=0.03)
    sphere(0.3, (0, 0, 1.6), BLACK(), (1, 1, 0.6))
    torus(0.36, 0.02, (0, 0, 1.57), GOLD(), seg=3, rot=(0, 0, R(30)))
    plume((0.2, 0.15, 1.72), size=1.1)
    sword((0.44, -0.12, 0.62), 0.55, rot=(R(-160), 0, R(10)))                  # sable hacia abajo


def bote():
    """Bote que aparece debajo de cualquier tropa que navega."""
    new_unit("Bote")
    import bmesh
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=16, location=(0, 0, 0.35))
    o = bpy.context.object
    o.scale = (0.55, 1.15, 0.45)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0.0),
                           plane_no=(0, 0, 1), clear_outer=True)
    bm.to_mesh(o.data); bm.free()
    _fin(o, WOOD())
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.06
    torus(0.0, 0.0, (0, 0, 0), WOOD())  # (marcador vacío que se borra)
    bpy.data.objects.remove(bpy.context.object, do_unlink=True)
    box((0.66, 1.5, 0.04), (0, 0, 0.16), WOOD_D(), bevel=0.0)                  # piso
    for y in (-0.5, 0.5):
        box((0.86, 0.12, 0.05), (0, y, 0.3), WOOD_D(), bevel=0.01)             # bancas
    cyl(0.04, 0.035, 1.6, (0, 0.1, 1.05), WOOD_D())                             # mástil
    cyl(0.025, 0.025, 1.0, (0, 0.1, 1.75), WOOD_D(), rot=(0, R(90), 0))         # verga
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=8, size=1, location=(0, 0.05, 1.3),
                                    rotation=(R(90), 0, 0))
    sail = bpy.context.object
    sail.scale = (0.95, 0.9, 1)
    for v in sail.data.vertices:
        v.co.z += -0.18 * (1 - (v.co.x * 2) ** 2) * (1 - (v.co.y * 2) ** 2)    # vela inflada
    _fin(sail, TRIBU())
    md = sail.modifiers.new("grosor", "SOLIDIFY"); md.thickness = 0.02
    box((0.06, 0.06, 0.12), (0, 1.12, 0.45), TRIBU(), bevel=0.01)               # banderín popa
    cyl(0.04, 0.0, 0.2, (0, -1.15, 0.5), WOOD_D(), rot=(R(-70), 0, 0), v=8)     # proa


def super_caballero():
    new_unit("Super_caballero")
    legs(STEEL_D(), STEEL(), STEEL(), spread=0.16)
    cyl(0.31, 0.33, 0.14, (0, 0, 0.56), CHAIN())
    cyl(0.4, 0.52, 1.0, (0, 0.18, 0.75), TRIBU(), v=32, sub=1)                  # capa
    torso(STEEL(), z=0.86, w=1.18, d=0.92, h=1.05, r=0.37)
    box((0.08, 0.02, 0.4), (0, -0.33, 0.9), GOLD(), bevel=0.005)
    box((0.3, 0.02, 0.07), (0, -0.33, 0.98), GOLD(), bevel=0.005)
    belt(0.64, 0.34)
    for sx in (-1, 1):
        sphere(0.19, (sx * 0.45, 0, 1.04), STEEL(), (1, 1, 0.85))
        torus(0.15, 0.02, (sx * 0.45, 0, 1.0), GOLD())
        arm(sx, STEEL(), glove=STEEL_D(), hand_pos=(sx * 0.46, -0.16, 0.66) if sx > 0 else None)
    head(1.34, 0.3)
    knight_helmet(1.34, 0.3, open_face=True)
    # corona dorada sobre el casco
    cyl(0.24, 0.26, 0.1, (0, 0.02, 1.72), GOLD(), v=32)
    for k in range(5):
        a = k * math.tau / 5
        cyl(0.04, 0.0, 0.12, (math.cos(a) * 0.23, 0.02 + math.sin(a) * 0.23, 1.82), GOLD(), v=6)
    sword((0.46, -0.18, 0.66), 0.85, rot=(R(-30), 0, R(-15)))


def sacerdote():
    new_unit("Sacerdote")
    cyl(0.25, 0.46, 0.95, (0, 0, 0.48), TRIBU(), v=32, sub=1)                    # túnica
    cyl(0.47, 0.47, 0.06, (0, 0, 0.05), GOLD(), v=32)
    box((0.12, 0.03, 0.75), (0, -0.36, 0.5), GOLD(), rot=(R(10), 0, 0), bevel=0.01)
    torso(TRIBU(), z=0.95, w=0.95, d=0.85, h=1.0, r=0.32)
    cyl(0.33, 0.33, 0.07, (0, 0, 1.18), GOLD(), v=32)                           # cuello dorado
    belt(0.75, 0.3, LEATHER_D(), GOLD())
    for sx in (-1, 1):
        arm(sx, TRIBU(), hand_pos=(sx * 0.42, -0.15, 0.78) if sx > 0 else None)
    head(1.42, 0.28)
    sphere(0.22, (0, -0.15, 1.27), WHITE(), (1.15, 0.7, 1.2), sub=1)            # barba
    sphere(0.29, (0, 0.03, 1.5), HAIR(), (1.02, 1.0, 0.75))                      # pelo
    # báculo con anillo y gema
    cyl(0.03, 0.03, 1.75, (0.42, -0.15, 0.95), GOLD())
    torus(0.15, 0.03, (0.42, -0.15, 1.95), GOLD(), rot=(R(90), 0, 0))
    sphere(0.06, (0.42, -0.15, 1.95), mat("Gema", "4aa3ff", 0.2, 0.0))
