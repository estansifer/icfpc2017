import json
import socket

import game_state

url = 'punter.inf.ed.ac.uk'
buffer_size = 4096

class Client:
    def __init__(self, port, name = "This is an albatrocity!"):
        self.socket = socket.create_connection((url, port))
        self.buffer = bytes()

        print("Beginning handshake")
        self.send_message({'me' : name})
        self.receive_message()
        print("Receiving map")
        setup = self.receive_message()
        self.game = game_state.Game.from_json_setup(setup)
        print("Received map")
        self.send_message(self.game.message_ready())
        self.listen()

    def listen(self):
        self.waiting_for_move = False
        j = self.receive_message()
        if 'move' in j:
            self.game.apply_moves(j['move'])
            self.waiting_for_move = True

        if 'stop' in j:
            self.game.apply_moves(j['stop'])
            self.scores = j['stop']['scores']

    def make_move(self, edge):
        self.send_message(self.game.message_move(edge))
        self.listen()

    def read(self, nbytes):
        result = bytes()
        while len(result) + len(self.buffer) < nbytes:
            result = result + self.buffer
            self.buffer = self.socket.recv(buffer_size)

        k = nbytes - len(result)
        result = result + self.buffer[:k]
        self.buffer = self.buffer[k:]

        return result.decode('utf-8')

    def receive_message(self):
        size = 0
        while True:
            c = self.read(1)
            if c == ':':
                break
            else:
                size = 10 * size + int(c)

        message = self.read(size)
        return json.loads(message)

    def send_message(self, j):
        message = json.dumps(j)
        full_message = str(len(message)) + ':' + message
        self.socket.sendall(full_message.encode('utf-8'))
