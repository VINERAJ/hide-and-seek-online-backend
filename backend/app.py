from flask import Flask, request
from flask_cors import CORS
from game import Game

app = Flask(__name__)
CORS(app)

games = {}
passcodes = {}

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/start')
def start_game():
    global game
    game = Game()
    return "game created"

@app.route('/hide', methods=['POST'])
def hide():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    game_id = data.get('id')
    game = games.get(game_id)
    if not game:
        return {"message": "Game not found"}
    game.store_coords(lat, lon)
    game.hidden = True
    return {"message": "Coordinates stored successfully"}

@app.route('/guess', methods=['POST'])
def guess():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    game_id = data.get('id')
    game = games.get(game_id)
    if not game:
        return {"message": "Game not found", "distance": 0, "found": False}
    distance = game.compare_coords(lat, lon)
    found = game.found_hider(distance)
    direction = game.get_direction(lat, lon)
    return {"message": "Guess received", "distance": distance, "found": found, "direction": direction}

@app.route('/create', methods=['POST'] )
def create():
    data = request.get_json()
    name = data.get('name')
    player = data.get('player')
    if player is None:
        return {"message": "Player name required", "id": 0000}
    if name is None or name=="":
        name = "gamename" + str(len(games) + 1)
    game = Game(name)
    new_player = Game.Player(player)
    game.players[new_player.id] = new_player
    games[game.id] = game
    passcodes[game.name] = (game.passcode, game.id)
    return {"message": "Game created successfully", "id": game.id, "name": game.name, "passcode": game.passcode, "player_id": new_player.id}

@app.route('/join', methods=['POST'])
def join():
    data = request.get_json()
    code = data.get('passcode')
    player = data.get('player')
    name = data.get('name')
    if name not in passcodes:
        return {"message": "Game not found", "id": 0000}
    if int(code) != passcodes[name][0]:
        return {"message": "Incorrect passcode", "id": 0000}
    game_id = passcodes[name][1]
    game = games.get(game_id)
    new_player = Game.Player(player)
    game.players[new_player.id] = new_player
    return {"message": "Joined game successfully", "id": game.id, "name": game.name, "passcode": game.passcode, "player_id": new_player.id}

@app.route('/players', methods=['POST'])
def players():
    data = request.get_json()
    game_id = data.get('id')
    game = games.get(game_id)
    if not game:
        return {"message": "Game not found", "players": []}
    players_list = [player.to_dict() for player in game.players.values()]
    return {"message": "Players retrieved successfully", "players": players_list}

@app.route('/endgame', methods=['POST'])
def endgame():
    data = request.get_json()
    game_id = data.get('id')
    game = games.get(game_id)
    if not game:
        return {"message": "Game not found"}
    del games[game_id]
    return {"message": "Game ended successfully"}

@app.route('/getUser', methods=['POST'])
def get_user():
    data = request.get_json()
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    game = games.get(game_id)
    if not game:
        return {"message": "Game not found", "player": {}}
    player = game.players.get(player_id)
    if not player:
        return {"message": "Player not found", "player": {}}
    return {"message": "Player retrieved successfully", "player": {"id": player.id, "name": player.name, "role": player.role, "points": player.points}}

@app.route('/setRole', methods=['POST'])
def set_role():
    data = request.get_json()
    game_id = data.get('id')
    player_id = data.get('player_id')
    role = data.get('role')
    game = games.get(game_id)
    print(game_id, player_id, role)
    if not game:
        return {"message": "Game not found"}
    player = game.players.get(player_id)
    if not player:
        return {"message": "Player not found"}
    player.role = role
    print("here2")
    return {"message": "Role set successfully"}

@app.route('/checkHidden', methods=['POST'])
def check_hidden():
    data = request.get_json()
    game_id = data.get('id')
    game = games.get(game_id)
    if not game:
        return {"message": "Game not found", "hidden": False}
    return {"message": "Hidden status retrieved successfully", "hidden": game.hidden}