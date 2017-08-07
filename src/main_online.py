import sys
import socket

import ai
import client
import timer
from debug import db

def main(choose_move, port):
    t = timer.Timer()

    c = client.ClientOnline(port)

    while c.waiting_for_move:
        with t:
            move = choose_move(c.gs)
        c.make_move(move)

    print(c.gs.summary())
    print(t.summary())
    print(c.scores)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        port = int(sys.argv[1])
        ainame = sys.argv[2]
        a = ai.lookup_ai(ainame)
        main(a, port)
    else:
        print("Usage: python3 main_online <port> <AI name>")
