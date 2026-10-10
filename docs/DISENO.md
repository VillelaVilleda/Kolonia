# Kolonia — Documento de diseño

Juego de estrategia por turnos para Android. Mapa de hexágonos en vista 2.5D,
gráficos 3D, de 2 a 8 jugadores (en línea o contra bots).

## Partida
- De 2 a 8 jugadores, por turnos.
- **Partida normal:** termina cuando un jugador conquista todas las ciudades o los rivales se rinden.
- **Partida avanzada:** permite ajustar el tamaño del mapa, la condición de victoria, los recursos iniciales, etc.
- Un jugador eliminado puede quedarse a ver la partida o salir.
- **Niebla de guerra:** solo se ve lo que está cerca de tus tropas y ciudades.

## Recursos
| Recurso | Uso | Cómo se obtiene |
|---|---|---|
| Comida | Crear tropas | Casillas de una sola cosecha + edificios que producen por turno |
| Madera | Construcciones | Casillas de una sola cosecha + edificios que producen por turno |
| Oro | Mejorar ciudades | Automático cada turno, según la cantidad de ciudades y su nivel |

- Las casillas de **una sola cosecha** sirven para el inicio y evitan que alguien se quede bloqueado.
- Las zonas con edificios de extracción dan recursos **cada turno**.
- **No hay comercio** entre jugadores.
- La ciudad inicial y las ciudades abandonadas siempre tienen recursos suficientes para subir del nivel 1.

## Economía (valores del prototipo)
- Cada ciudad da por turno: comida = nivel + 1 y oro = nivel + 1.
- **Recursos de una sola cosecha:**
  - Frutos (llanura): +3 comida y +1 punto de mejora.
  - Troncos (bosque): +3 madera y +1 punto de mejora.
- **Zonas para edificios:**
  - Campo fértil → Granja (cuesta 3 madera): +1 comida por turno y +2 puntos.
  - Arboleda → Aserradero (cuesta 2 oro): +1 madera por turno y +2 puntos.
- **Subir de nivel una ciudad:** necesita nivel × 2 puntos y cuesta nivel × 5 oro. Cada nivel aumenta en 1 el límite de tropas.

## Caminos y puertos (valores del prototipo)
- **Camino:** cuesta 1 de madera. Se construye en tierra fuera del territorio enemigo, pegado a tu territorio, a tu ciudad o a otro camino tuyo.
  - Cualquier tropa que avance de camino a camino gasta la mitad del movimiento. Las ciudades cuentan como camino.
  - En un bosque, el camino evita que se pierda todo el movimiento.
- **Puerto:** cuesta 3 de madera y da +1 punto. Se construye en el agua dentro del territorio de una ciudad.
  - Dos puertos tuyos en la misma agua quedan conectados.
- **Conexión:** cuando dos ciudades tuyas quedan unidas por caminos y puertos, cada una gana +2 puntos de mejora. Pasa una sola vez por cada pareja.
  - Una ciudad ajena en medio corta la conexión.
- **Mapa:** un río cruza de norte a sur junto a las dos ruinas, con 3 vados para cruzarlo a pie.

## Árbol de mejoras (valores del prototipo)
Se compran con oro, una sola vez por jugador. Algunas requieren otra antes. El árbol está en `scripts/core/techs.gd`, así que es fácil agregar ramas nuevas.

| Rama | Mejora | Costo | Requiere | Efecto |
|---|---|---|---|---|
| Ejército | Escudos | 5 | — | Caballero con escudo |
| Ejército | Lanzas | 8 | Escudos | Jinete lancero |
| Ejército | Pólvora | 12 | Lanzas | Cañonero |
| Agua | Barcos | 6 | — | Las tropas suben al barco en un puerto propio. En el agua avanzan el doble y pueden desembarcar en cualquier orilla |
| Montaña | Escalada | 6 | — | Se pueden subir montañas, y subir gasta todo el movimiento. Arriba, las tropas de distancia tienen +1 de alcance (y más visión cuando exista la niebla) |
| Ciudades | Fronteras | 8 | — | Cada ciudad puede ampliar su territorio a 2 casillas por 5 oro (+1 punto) |

## Ciudades
- Solo obtienen recursos de los hexágonos **adyacentes**. Una mejora amplía ese territorio.
- Suben de nivel con **puntos de mejora**, que se ganan construyendo, mejorando construcciones y conectando ciudades con caminos.
- Cada ciudad tiene un **límite de tropas**, que crece con su nivel.
- **Ciudades abandonadas:** no son de nadie y se conquistan igual que las enemigas.
- **Puertos:** solo se construyen dentro de la zona de una ciudad que tenga agua cerca. Conectan ciudades por agua, como si fueran caminos.

## Conquista
1. Una tropa entra al hexágono de la ciudad y termina su turno ahí.
2. Si sigue viva al empezar tu siguiente turno, la ciudad pasa a ser tuya.
3. Esa tropa no puede hacer nada durante ese turno.
4. Mientras está conquistando, el enemigo puede eliminarla para impedir la conquista.
- Solo cabe **una tropa por hexágono**. Si hay una tropa enemiga dentro de su ciudad, nadie puede entrar hasta eliminarla.
- La tropa conquistadora pasa a ocupar el primer espacio de tropa de la nueva ciudad y libera su espacio en la ciudad de origen.
- Cuando una ciudad es conquistada, **todas las tropas que pertenecían a ella desaparecen, héroes incluidos**.

## Tropas
- Una tropa no puede hacer nada en el turno en que se crea.
- Cada tropa puede moverse y luego atacar. Si ataca primero, ya no puede moverse.
- Si el defensor sobrevive y tiene alcance, contraataca.
- Las mejoras se desbloquean en orden: primero la tropa base y después su versión mejorada. Cada una tiene sus propios puntos fuertes.

| Tropa | Desbloqueo | Vida | Ataque | Defensa | Movimiento | Alcance | Costo (comida) |
|---|---|---|---|---|---|---|---|
| Caballero | Inicial | 10 | 3 | 2 | 1 | 1 | 2 |
| Caballero con escudo | Mejora de Caballero | 12 | 2 | 4 | 1 | 1 | 4 |
| Jinete | Inicial | 10 | 2 | 1 | 2 | 1 | 3 |
| Jinete lancero | Mejora de Jinete | 12 | 4 | 2 | 2 | 1 | 5 |
| Arquero | Inicial | 8 | 2 | 1 | 1 | 2 | 3 |
| Cañonero | Mejora de Arquero | 8 | 4 | 1 | 1 | 3 | 6 |

*Los números son provisionales y se ajustarán probando.*

- **Daño** = ataque × 2 − defensa del objetivo (mínimo 1).
- La defensa sube un 50 % en bosque o dentro de una ciudad propia.

## Héroes
- Se invoca un héroe cuando una ciudad llega a los niveles 3, 5, 7…
- Cada tribu tiene 2 héroes. En cada invocación se elige uno de los dos.
- Se pueden tener varios héroes vivos a la vez.
- Desaparecen si su ciudad es conquistada.
- No ocupan espacio de tropa en la ciudad.
- Cada habilidad usa la acción del turno y tiene un tiempo de espera.

**Tribu roja:**
- **Súper caballero** (vida 20, ataque 5, defensa 3, movimiento 2). *Embestida:* avanza hasta 3 casillas en línea recta y golpea a cada enemigo del camino. Si uno sobrevive, se detiene frente a él. Espera: 3 turnos.
- **Sacerdote** (vida 14, ataque 2, defensa 2, alcance 2).
  - *Curación:* cura 4 de vida a las tropas propias en un radio de 3 hexágonos. Espera: 2 turnos.
  - *Muralla de llamas:* pone llamas en 3 hexágonos en línea, a hasta 3 casillas, durante 2 turnos. Los enemigos no pueden entrar y los que estén dentro pierden 3 de vida al empezar su turno. No se puede usar dos turnos seguidos.

## Terreno
- **Llanura:** se puede pasar normalmente.
- **Bosque:** entrar gasta todo el movimiento y da +50 % de defensa.
- **Montaña:** no se puede pasar hasta comprar la mejora de montaña. Con ella, las tropas en montaña tienen más visión y las de distancia, más alcance.
- **Ríos y lagos:** necesitan la mejora de barcos para moverse por el agua.
- **Caminos:** dan más movimiento a las tropas que se mueven por ellos. Si conectan ciudades, dan puntos de mejora.

## Pendiente por decidir
- Costos de las mejoras y de subir de nivel una ciudad.
- Estadísticas y tiempos de espera de los héroes.
- El resto de tribus (mismas estadísticas, distinto estilo).
- La regla de rendición.

## Estado del prototipo (versión 0.1)
**Hecho:**
- Recursos, granjas y aserraderos.
- Caminos, puertos y conexión entre ciudades.
- Árbol de mejoras: barcos, escalada, tropas mejoradas y fronteras.
- Oro, madera y puntos de mejora.
- Niveles de ciudad e invocación de héroes, con sus 3 habilidades.
- Mapa hexagonal con llanura, bosque, montaña y agua.
- Rojo contra Azul (bot), con 2 ciudades abandonadas.
- Tropas básicas, movimiento, ataque y contraataque.
- Conquista, límite de tropas por ciudad y eliminación de jugadores.
- Comida por turno.

**Falta:**
- Diseñar más ramas y niveles del árbol de mejoras.
- Niebla de guerra.
- Modelos 3D definitivos.
- Multijugador en línea.
