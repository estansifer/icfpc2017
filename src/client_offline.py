import sys
import json

import game_state

def receive_message():
    size = 0
    while True:
        c = sys.stdin.read(1)
        if c == ':':
            break
        else:
            size = 10 * size + int(c)

    message = sys.stdin.read(size)
    return json.loads(message)

def send_message(j):
    message = json.dumps(j)
    full_message = str(len(message)) + ':' + message
    sys.stdout.write(full_message)
    sys.stdout.flush()

class Client:
    def __init__(self, name = "This is an albatrocity!"):
        send_message({'me' : name})
        receive_message()
        j = receive_message()

        self.waiting_for_move = False

        if 'punter' in j:
            self.game = game_state.Game.from_json_setup(j)
            self.ready()

        if 'state' in j:
            self.game = game_state.Game.from_json_offline(j['state'])

            if 'move' in j:
                self.game.apply_moves(j)
                self.waiting_for_move = True

            if 'stop' in j:
                self.game.apply_moves({'move' : j['stop']})

    def ready(self):
        send_message({'ready' : self.game.me, 'state' : self.game.to_json_offline()})


    def make_move(self, edge):
        move = self.game.make_move(edge)
        move['state'] = self.game.to_json_offline()
        send_message(move)
