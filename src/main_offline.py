import sys
import json

import ai
import client_offline

name = "This is an albatrocity!"

def main(choose_move):
    client = client_offline.Client()

    if client.waiting_for_move:
        client.make_move(choose_move(client.game))

if __name__ == "__main__":
    if len(sys.argv) == 2:
        choose_move = ai.lookup_ai(sys.argv[1])
        if choose_move is None:
            sys.exit(1)
    else:
        sys.exit(1)
    main(choose_move)
