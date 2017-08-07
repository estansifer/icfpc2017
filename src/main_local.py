import json
import sys

import board
import game_state as GS
import ai

def main(mapfile, ais, settings = {}):
    n = len(ais)
    print("Playing a game on {} with {} AIs.".format(mapfile, n))

    b = board.Board.from_json_file(mapfile)
    print(b.summary())

    games = []
    for i in range(n):
        games.append(GS.GameState1.from_board(b, n, i, settings))

    edges = b.num_edges

    for i in range(edges):
        print("Move {}".format(i))

        move = ais[i % n](games[i % n])

        for game in games:
            game.apply_move(i % n, move)

    print("Game completed!")

def print_usage():
    print("python3 main_local <path-to-mapfile> <list-of-ais>")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_usage()

    mapfile = sys.argv[1]
    ainames = sys.argv[2:]
    ais = []

    for ainame in ainames:
        a = ai.lookup_ai(ainame)
        if a is None:
            print("Couldn't find the AI named '{}'".format(ainame))
        ais.append(a)

    main(mapfile, ais)
