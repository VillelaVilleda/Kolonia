# Kolonia
Juego de estrategia multijugador por turnos en un mapa hexagonal, para Android, hecho con Godot 4.7.2. Se juega en vertical u horizontal: gira el teléfono y la pantalla se adapta.

## Cómo abrirlo
1. Abre Godot y pulsa **Importar**.
2. Elige el archivo `project.godot` de esta carpeta.
3. Pulsa **F5** (o el botón ▶) para jugar.

## Controles
- **Tocar o hacer clic** en una tropa tuya para seleccionarla. Las casillas blancas son a dónde se puede mover; las rojas, a quién puede atacar.
- **Tocar tu ciudad** (sin tropa encima) para entrenar tropas.
- **Arrastrar** para mover la cámara.
- **Rueda del ratón o pellizcar** para hacer zoom.
- En la PC, la ventana abre en vertical; puedes estirarla a lo ancho para probar el modo horizontal.

## Estructura
| Ruta | Contenido |
|---|---|
| `scripts/core/` | Reglas del juego, sin gráficos (`game_state.gd`, `hex.gd`, `unit_types.gd`) |
| `scripts/ai/` | Bot |
| `scripts/view/` | Dibujo del tablero en 3D |
| `scripts/main.gd` | Cámara, controles e interfaz |
| `tests/` | Prueba automática de bot contra bot: `godot --headless --script res://tests/test_bots.gd` |
| `docs/DISENO.md` | Documento de diseño |
