import sys
import socket

import ai
import client_online
from debug import db

url = 'punter.inf.ed.ac.uk'

def main(choose_move, port):
    print("Connecting to {}".format(port))
    client = client_online.Client(port)

    while client.waiting_for_move:
        edge = choose_move(client.game)
        print("Chose edge from {} to {}".format(edge.source, edge.target))
        client.make_move(edge)

    print('\n'.join(client.game.summary()))
    print(client.scores)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        port = int(sys.argv[1])
        ainame = sys.argv[2]
        a = ai.lookup_ai(ainame)
        main(a, port)
    else:
        print("Usage: python3 main_online <port> <AI name>")

