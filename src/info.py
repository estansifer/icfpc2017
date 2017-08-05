import json
import os
import os.path

import game_state

maps_dir = os.path.join('..', 'maps', 'official')

for filename in os.listdir(maps_dir):
    with open(os.path.join(maps_dir, filename), 'r') as f:
        print("Examining {}".format(filename))
        j = json.load(f)
        game = game_state.Game.from_json_setup({'punters' : 2, 'punter' : 0, 'map' : j})
        print(game.summary()[0])
