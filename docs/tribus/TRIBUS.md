# Kolonia — Tribus (diseño)

Cinco tribus nuevas además del Reino (la tribu base). Todas tienen **las mismas tropas con las mismas estadísticas**; solo cambia el estilo. Cada tribu tiene **dos héroes propios**, que se invocan al subir una ciudad a nivel 3 (o más).

Estado: **solo diseño**. Los modelos 3D están hechos, pero todavía no se pueden elegir en el juego.
- Modelos: `assets/tribus/<tribu>/` (con `tribu.json`: qué arma lleva cada tropa en qué mano).
- Láminas de vista previa: `docs/tribus/tribu_<tribu>.png`.
- Scripts que generan los modelos: `tools/blender/kk_<tribu>.py` y `kk_tribus_comun.py`.

## Equivalencias de tropas

| Tropa base | Amazonas | Desierto | Maya | Robots | China |
|---|---|---|---|---|---|
| Caballero | Guerrera | Guerrero del Nilo | Guerrero jaguar | Androide | Guardia imperial |
| Escudero | Hoplita | Guardia del templo | Guerrero águila | Blindado | Guardia tigre |
| Arquero | Cazadora | Arquero de las dunas | Arquero | Francotirador | Ballestero |
| Jinete | Jinete de ciervo | Jinete de camello | Jinete de jaguar | Jinete mecánico | Jinete |
| Jinete lancero | Jinete de alce | Lancero de camello | Lancero de jaguar | Lancero mecánico | General |
| Catapulta | Honda gigante | Trabuquete | Lanzapiedras | Mortero | Lanzacohetes |
| Capitán | Capitana | Capitán | Capitán | Capitán | Capitán |
| Barco del capitán | Catamarán | Falucho | Canoa de guerra | Barco de vapor | Junco |

## Estilo de cada tribu
- **Amazonas:** guerreras de la selva. Bronce, falda de leopardo, hojas y plumas. Montan ciervos.
- **Desierto:** estilo egipcio. Lino, oro, lapislázuli y arena. Montan camellos.
- **Maya:** guerreros jaguar y águila. Jade, oro, plumas de quetzal y armadura de algodón. Montan jaguares.
- **Robots:** cuerpos de metal con pantallas y luces de energía. Montan caballos mecánicos.
- **China:** armaduras laqueadas, oro, borlas rojas y bambú. Montan caballos con arreos chinos.

## Héroes (estadísticas propuestas, se ajustarán probando)
Los héroes base para comparar: Súper caballero 20/4/3 mov 2, Sacerdote 15/2/2 alcance 2.

### Amazonas
- **Araña gigante** — vida 18, ataque 4, defensa 2, movimiento 2, alcance 1.
  - Solo ataca cuerpo a cuerpo.
  - *Telaraña* (espera 3): lanza una telaraña a una tropa enemiga a hasta 3 casillas. Esa tropa no puede moverse durante su siguiente turno.
- **Reina Amazona** — vida 15, ataque 3, defensa 2, movimiento 1, alcance 2.
  - *Lluvia de flechas* (espera 3): dispara hasta 3 flechas a enemigos distintos a su alcance. No puede repetir objetivo.

### Desierto
- **Gólem de arena** — vida 24, ataque 3, defensa 4, movimiento 1.
  - *Rodar* (espera 3): avanza en línea recta hasta 4 casillas mientras no haya obstáculos.
  - Si choca con un enemigo, lo golpea y lo empuja 1 casilla (si la casilla de atrás está libre).
- **Anubis** — vida 15, ataque 3, defensa 2, movimiento 1, alcance 2.
  - *Momificar* (siempre activa): cuando mata a un enemigo, en esa casilla aparece una **Momia** aliada.
  - **Momia** — vida 4, ataque 1, defensa 1, movimiento 1.
  - Las momias no ocupan vivienda. Propongo un máximo de 3 vivas a la vez.

### Maya
- **Quetzalcóatl** — vida 18, ataque 3, defensa 2, movimiento 3.
  - Vuela: pasa por agua y montañas sin problema.
  - *Salto de serpiente* (espera 3): salta sobre un enemigo cercano y lo daña. Puede encadenar hasta 3 saltos sobre enemigos distintos y termina junto al último.
- **Balam, el rey jaguar** (lo escogí yo) — vida 20, ataque 4, defensa 3, movimiento 2.
  - *Acecho* (siempre activa): en el bosque los enemigos no lo ven.
  - Si ataca desde un bosque, su primer golpe hace el doble de daño.

### Robots
- **Máquina de asedio** — vida 20, ataque 4, defensa 3, movimiento 1, alcance 3.
  - *Rayo láser*: su ataque daña a todas las tropas enemigas que estén en la línea entre ella y su objetivo.
- **Ingeniero** — vida 14, ataque 2, defensa 2, movimiento 2.
  - *Reparar* (espera 2): cura 6 de vida a una máquina aliada cercana.
  - *Mejora* (espera 2): un aliado cercano gana +5 de vida y +1 de ataque durante una ronda.

### China
- **Dragón** — vida 20, ataque 4, defensa 2, movimiento 3, alcance 2.
  - Vuela.
  - *Aliento de fuego*: daña y deja quemada a la tropa. Al empezar su siguiente turno, la tropa quemada pierde 3 de vida.
- **Sun Wukong** — vida 16, ataque 3, defensa 2, movimiento 2.
  - Puede moverse, atacar y volver a moverse.
  - *Clon* (espera 3): crea una copia de sí mismo junto a él.
  - La copia no ataca, muere con cualquier golpe y se puede mover o dejar quieta. Solo puede haber una copia por héroe y no ocupa vivienda.
  - En el juego, la copia usa el mismo modelo pero transparente.

## Notas para cuando se implementen
- Las monturas nuevas (ciervo, camello, jaguar, caballo mecánico) usan los mismos huesos que el caballo base. Por eso ya traen sus animaciones de montado, galope, golpe y ataque.
- Las catapultas nuevas usan el mismo hueso "brazo_cat" y la animación "Disparo".
- Los héroes humanos (Reina, Anubis, Balam, Ingeniero, Sun Wukong) y la Momia usan el esqueleto normal y las animaciones de las tropas.
- **Faltan animaciones** para los héroes criatura (Araña, Gólem, Quetzalcóatl, Máquina de asedio y Dragón): hoy son modelos sin esqueleto.
- El color de la tribu funciona igual que hoy: las piezas "K_Tribu" se pintan con el color del jugador.
- Al implementarlas, conviene que el juego cargue los modelos según la tribu del jugador (por ejemplo, `assets/tribus/<tribu>/<modelo>.glb`) usando la tabla de equivalencias.
