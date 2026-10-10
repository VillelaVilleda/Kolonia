extends SceneTree
## Prueba automática: enfrenta bot contra bot en varias partidas y revisa
## que las reglas no se rompan. Se ejecuta desde la línea de comandos:
##   godot --headless --script res://tests/test_bots.gd

func _initialize() -> void:
	_run()


func _run() -> void:
	var wins := {}
	var events := {}
	var count := func(text: String):
		for key in ["Elige una recompensa", "Nueva mejora", "amplió", "ve a", "oro por turno", "conectadas", "puerto", "invocado", "Embestida", "curó", "Muralla", "quemado", "subió a nivel", "Construiste", "Cosechaste", "conquistó", "ocupó"]:
			if text.contains(key):
				events[key] = events.get(key, 0) + 1
	var max_turns := 150
	for game in 30:
		var gs := GameState.new()
		gs.message.connect(count)
		gs.setup(1000 + game)
		for p in gs.players:
			p.is_bot = true
		while gs.winner == GameState.NO_PLAYER and gs.turn <= max_turns:
			await SimpleBot.play_turn(gs, self, func(): pass, 0.0)
			_check(gs)
			gs.end_turn()
			_check(gs)
		var key := "empate" if gs.winner == GameState.NO_PLAYER else gs.players[gs.winner].name
		wins[key] = wins.get(key, 0) + 1
		print("Partida %d: %s en el turno %d" % [game, key, gs.turn])
	print("Resultados: ", wins)
	print("Eventos: ", events)
	quit()


func _check(gs: GameState) -> void:
	var seen := {}
	for u in gs.units.values():
		assert(not seen.has(u.pos), "Dos tropas en la misma casilla")
		seen[u.pos] = true
		var t: String = gs.tiles[u.pos]
		assert(t != "montana" or gs.has_tech(u.owner, "exploracion"), "Tropa en montaña sin Exploración")
		assert(t != "agua" or gs.has_tech(u.owner, "navegacion"), "Tropa en agua sin Navegación")
		assert(u.hp > 0, "Tropa con vida <= 0")
		assert(gs.cities[u.home].owner == u.owner, "Tropa de una ciudad que no es de su dueño")
	for c in gs.cities.values():
		if c.owner != GameState.NO_PLAYER:
			var normal := 0
			for u in gs.units.values():
				if u.home == c.pos and not u.is_hero():
					normal += 1
			assert(normal <= c.max_units(), "Ciudad pasada de su límite")
	for p in gs.players:
		for k in p.res:
			assert(p.res[k] >= 0, "Recurso negativo")
