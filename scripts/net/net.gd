class_name Net
extends Node
## Juego en red por Wi-Fi local (sin servidor).
##
## Un teléfono crea la partida (anfitrión) y es el que manda: tiene la partida "de
## verdad", juega los bots y aplica las acciones. Los demás (invitados) le mandan lo
## que quieren hacer y reciben, después de cada cambio, una copia del estado y la
## lista de eventos para animarlos.
##
## Para encontrar partidas, el anfitrión anuncia la suya por la red local cada segundo
## (UDP de difusión) y los invitados escuchan esos anuncios. Si un teléfono no recibe
## anuncios (algunos los bloquean), se puede escribir la dirección del anfitrión.

signal games_found_changed
signal lobby_changed
signal game_started(state: PackedByteArray, my_player: int)
signal state_received(state: PackedByteArray, events: Array)
signal action_requested(player: int, action: String, args: Array)
signal peer_left(player: int)
signal connection_failed
signal host_lost

const PORT := 47317
const DISCOVERY_PORT := 47318
const MAX_PEERS := 7
const ANNOUNCE_EVERY := 1.0
const FORGET_AFTER := 4.0

enum Mode { OFF, HOST, CLIENT }
var mode := Mode.OFF

## Sala de espera: peer -> índice de color. El anfitrión es el peer 1.
var lobby := {}
var lobby_order: Array = []  ## peers en orden de llegada (el anfitrión primero)
## En partida: jugador -> peer (solo humanos) y peer -> jugador.
var player_peers := {}
var peer_players := {}
var in_game := false
## Partidas encontradas: ip -> {"nombre", "jugadores", "visto"}
var found := {}

var _peer: ENetMultiplayerPeer
var _udp: PacketPeerUDP
var _announce_timer := 0.0
var _last_sent := PackedByteArray()
var host_name := ""


func _ready() -> void:
	multiplayer.peer_connected.connect(_on_peer_connected)
	multiplayer.peer_disconnected.connect(_on_peer_disconnected)
	multiplayer.connected_to_server.connect(_on_connected)
	multiplayer.connection_failed.connect(func(): close(); connection_failed.emit())
	multiplayer.server_disconnected.connect(_on_server_lost)


func is_host() -> bool:
	return mode == Mode.HOST


func is_client() -> bool:
	return mode == Mode.CLIENT


func is_online() -> bool:
	return mode != Mode.OFF


func my_id() -> int:
	return multiplayer.get_unique_id() if is_online() else 1


# --- Crear / unirse / salir ------------------------------------------------------------

func host(color_index: int, name_text: String) -> Error:
	stop_search()
	close()
	_peer = ENetMultiplayerPeer.new()
	var err := _peer.create_server(PORT, MAX_PEERS)
	if err != OK:
		_peer = null
		return err
	multiplayer.multiplayer_peer = _peer
	mode = Mode.HOST
	host_name = name_text
	lobby = {1: color_index}
	lobby_order = [1]
	in_game = false
	_udp = PacketPeerUDP.new()
	_udp.set_broadcast_enabled(true)
	_udp.bind(0)
	lobby_changed.emit()
	return OK


func join(ip: String) -> Error:
	stop_search()
	close()
	_peer = ENetMultiplayerPeer.new()
	var err := _peer.create_client(ip, PORT)
	if err != OK:
		_peer = null
		return err
	multiplayer.multiplayer_peer = _peer
	mode = Mode.CLIENT
	in_game = false
	return OK


func close() -> void:
	if _peer != null:
		_peer.close()
	_peer = null
	multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()
	mode = Mode.OFF
	lobby.clear()
	lobby_order.clear()
	player_peers.clear()
	peer_players.clear()
	in_game = false
	_last_sent = PackedByteArray()
	if _udp != null and not _searching:
		_udp.close()
		_udp = null


# --- Buscar partidas ---------------------------------------------------------------------

var _searching := false


func is_searching() -> bool:
	return _searching


func start_search() -> void:
	stop_search()
	_udp = PacketPeerUDP.new()
	if _udp.bind(DISCOVERY_PORT) != OK:
		push_warning("No se pudo escuchar anuncios de partidas")
	_searching = true
	found.clear()
	games_found_changed.emit()


func stop_search() -> void:
	if _searching and _udp != null:
		_udp.close()
		_udp = null
	_searching = false


## Direcciones a las que se anuncia la partida: la de difusión general y la de cada
## red local del teléfono (sirve también cuando el anfitrión comparte su internet).
static func broadcast_addresses() -> Array:
	var out := ["255.255.255.255"]
	for ip in local_ips():
		var parts: PackedStringArray = ip.split(".")
		out.append("%s.%s.%s.255" % [parts[0], parts[1], parts[2]])
	return out


## Direcciones IPv4 de la red local de este teléfono (para escribirlas a mano).
static func local_ips() -> Array:
	var out := []
	for ip in IP.get_local_addresses():
		if ip.count(".") != 3 or ip.begins_with("127.") or ip.begins_with("169.254."):
			continue
		if ip.begins_with("10.") or ip.begins_with("192.168.") or _is_172_private(ip):
			out.append(ip)
	return out


static func _is_172_private(ip: String) -> bool:
	if not ip.begins_with("172."):
		return false
	var second := int(ip.split(".")[1])
	return second >= 16 and second <= 31


func _process(delta: float) -> void:
	if is_host() and not in_game and _udp != null:
		_announce_timer -= delta
		if _announce_timer <= 0.0:
			_announce_timer = ANNOUNCE_EVERY
			var msg := JSON.stringify({"kolonia": 1, "nombre": host_name, "jugadores": lobby.size(),
				"max": MAX_PEERS + 1}).to_utf8_buffer()
			for addr in broadcast_addresses():
				_udp.set_dest_address(addr, DISCOVERY_PORT)
				_udp.put_packet(msg)
	if _searching and _udp != null:
		var changed := false
		while _udp.get_available_packet_count() > 0:
			var pkt := _udp.get_packet()
			var ip := _udp.get_packet_ip()
			var data: Variant = JSON.parse_string(pkt.get_string_from_utf8())
			if data is Dictionary and data.get("kolonia", 0) == 1:
				if not found.has(ip):
					changed = true
				found[ip] = {"nombre": str(data.get("nombre", "Partida")),
					"jugadores": int(data.get("jugadores", 1)), "visto": Time.get_ticks_msec()}
		var now := Time.get_ticks_msec()
		for ip in found.keys():
			if now - int(found[ip]["visto"]) > FORGET_AFTER * 1000:
				found.erase(ip)
				changed = true
		if changed:
			games_found_changed.emit()


# --- Sala de espera ------------------------------------------------------------------------

func _on_peer_connected(id: int) -> void:
	if not is_host():
		return
	if in_game or lobby.size() >= MAX_PEERS + 1:
		# La partida ya empezó o está llena
		_reject.rpc_id(id, "La partida ya empezó" if in_game else "La partida está llena")
		return
	var free := free_colors()
	lobby[id] = free[0] if not free.is_empty() else 0
	lobby_order.append(id)
	_send_lobby()


func _on_peer_disconnected(id: int) -> void:
	if not is_host():
		return
	if in_game:
		if peer_players.has(id):
			var player: int = peer_players[id]
			peer_players.erase(id)
			player_peers.erase(player)
			peer_left.emit(player)
	elif lobby.has(id):
		lobby.erase(id)
		lobby_order.erase(id)
		_send_lobby()


func _on_connected() -> void:
	lobby_changed.emit()


func _on_server_lost() -> void:
	var was_online := is_online()
	close()
	if was_online:
		host_lost.emit()


func free_colors(except_peer := 0) -> Array:
	var used := {}
	for p in lobby:
		if p != except_peer:
			used[lobby[p]] = true
	var out := []
	for i in MatchConfig.COLORS.size():
		if not used.has(i):
			out.append(i)
	return out


func _send_lobby() -> void:
	lobby_changed.emit()
	_lobby_state.rpc(lobby, lobby_order)


@rpc("authority", "call_remote", "reliable")
func _lobby_state(new_lobby: Dictionary, order: Array) -> void:
	lobby = new_lobby
	lobby_order = order
	lobby_changed.emit()


@rpc("authority", "call_remote", "reliable")
func _reject(reason: String) -> void:
	close()
	connection_failed.emit()
	push_warning(reason)


## Un invitado pide otro color (o el anfitrión lo cambia para sí mismo).
func request_color(index: int) -> void:
	if is_host():
		_set_color(1, index)
	elif is_client():
		_want_color.rpc_id(1, index)


@rpc("any_peer", "call_remote", "reliable")
func _want_color(index: int) -> void:
	if is_host():
		_set_color(multiplayer.get_remote_sender_id(), index)


func _set_color(peer: int, index: int) -> void:
	if not lobby.has(peer) or not index in free_colors(peer):
		return
	lobby[peer] = index
	_send_lobby()


## Colores de los humanos en orden de llegada (el anfitrión primero).
func human_colors() -> Array:
	return lobby_order.map(func(p): return lobby[p])


# --- Partida -------------------------------------------------------------------------------

## El anfitrión empieza: el jugador i de la partida es el humano i de la sala.
func start_game(gs: GameState) -> void:
	in_game = true
	player_peers.clear()
	peer_players.clear()
	for i in lobby_order.size():
		player_peers[i] = lobby_order[i]
		peer_players[lobby_order[i]] = i
	var state := gs.to_bytes()
	_last_sent = state
	for peer in peer_players:
		if peer != 1:
			_start.rpc_id(peer, state, peer_players[peer])


@rpc("authority", "call_remote", "reliable")
func _start(state: PackedByteArray, my_player: int) -> void:
	in_game = true
	game_started.emit(state, my_player)


## El anfitrión manda el estado si cambió (y los eventos para animar).
func broadcast_state(gs: GameState, events: Array) -> void:
	if not is_host() or not in_game:
		return
	var state := gs.to_bytes()
	if state == _last_sent and events.is_empty():
		return
	_last_sent = state
	for peer in peer_players:
		if peer != 1:
			_state.rpc_id(peer, state, events)


@rpc("authority", "call_remote", "reliable")
func _state(state: PackedByteArray, events: Array) -> void:
	state_received.emit(state, events)


## Un invitado pide hacer una acción en su turno.
func send_action(action: String, args: Array) -> void:
	_action.rpc_id(1, action, args)


@rpc("any_peer", "call_remote", "reliable")
func _action(action: String, args: Array) -> void:
	if not is_host():
		return
	var sender := multiplayer.get_remote_sender_id()
	if peer_players.has(sender):
		action_requested.emit(peer_players[sender], action, args)
