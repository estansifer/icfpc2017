import sys
import json
import socket

import board
import game_state

#
# Create and parse messages for passing to and from the server
#
# in_XXX: parses a message from the server
# out_XXX: creates a message to send to the server
#

name = "This is an albatrocity!"

def out_handshake():
    return {'me' : name}

def in_handshake(msg):
    pass

def in_setup(msg):
    b = board.Board.from_json(msg['map'])
    gs = game_state.GameState1.from_board(b,
            players = msg['punters'],
            me = msg['punter'],
            settings = msg.get('settings', {}))
    return (b, gs)

def out_setup_online(gs):
    msg = {'ready' : gs.me}
    if gs.futures:
        msg['futures'] = []
    return msg

def out_setup_offline(gs):
    msg = out_setup_online(gs)
    msg['state'] = gs.serialize()
    return msg

def apply_moves(gs, moves):
    for move in moves['moves']:
        m = move.get('claim', move.get('pass', move.get('splurge', None)))
        who = m['punter']
        gs.apply_move(who, game_state.Move.from_json(gs, move))

# gs is None for offline mode, or a valid game state for online mode
# Returns new game state and None if game is continuing or scores if game is done.
def in_move(msg, gs = None):
    if gs is None:
        gs = game_state.GameState1.deserialize(msg['state'])

    if 'move' in msg:
        apply_moves(gs, msg['move'])
        return (gs, None)

    if 'stop' in msg:
        apply_moves(gs, msg['stop'])
        return (gs, msg['stop']['scores'])

def out_move_online(move):
    return move.to_json()

def out_move_offline(gs, move):
    msg = out_move_online(move)
    msg['state'] = gs.serialize()
    return msg

def wrap(msg):
    s = json.dumps(msg)
    return str(len(s)) + ':' + s

def send_offline(msg):
    sys.stdout.write(wrap(msg))
    sys.stdout.flush()

def read_offline(nbytes):
    return sys.stdin.read(nbytes)

url = 'punter.inf.ed.ac.uk'
buffer_size = 4096
class PipeOnline:
    def __init__(self, port):
        print("Opening socket to port {}".format(port))
        self.socket = socket.create_connection((url, port))
        self.buffer = bytes()

    def send(self, msg):
        self.socket.sendall(wrap(msg).encode('ascii'))

    def read(self, nbytes):
        result = bytes()
        while len(result) + len(self.buffer) < nbytes:
            result = result + self.buffer
            self.buffer = self.socket.recv(buffer_size)

        k = nbytes - len(result)
        result = result + self.buffer[:k]
        self.buffer = self.buffer[k:]

        return result.decode('ascii')

def receive(read):
    size = 0
    while True:
        c = read(1)
        if c == ':':
            break
        else:
            size = 10 * size + int(c)
    return json.loads(read(size))

# Returns game state
def client_offline(choose_move):
    # Handshake
    send_offline(out_handshake())
    in_handshake(receive(read_offline))

    msg = receive(read_offline)

    if 'map' in msg:
        # Setup
        b, gs = in_setup(msg)
        send_offline(out_setup_offline(gs))
        return gs

    if ('move' in msg) or ('stop' in msg):
        gs, scores = in_move(msg)
        if scores is None:
            send_offline(out_move_offline(gs, choose_move(gs)))
        return gs

class ClientOnline:
    def __init__(self, port):
        self.pipe = PipeOnline(port)

        # Handshake
        print("Handshake...")
        self.pipe.send(out_handshake())
        in_handshake(receive(self.pipe.read))

        # Setup
        print("Setup...")
        b, gs = in_setup(receive(self.pipe.read))
        self.pipe.send(out_setup_online(gs))
        print("Board summary", b.summary())

        self.gs = gs
        self.listen()

    def listen(self):
        print("Receiving moves...")
        gs, scores = in_move(receive(self.pipe.read), self.gs)
        self.gs = gs
        self.waiting_for_move = (scores is None)
        if scores is not None:
            self.scores = scores

    def make_move(self, move):
        self.pipe.send(out_move_online(move))
        self.listen()
