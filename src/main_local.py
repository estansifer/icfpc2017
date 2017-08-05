import json
import sys

import game_state as GS
import ai

def main(mapfile, ais, display = False):
    n = len(ais)
    print("Playing a game on {} with {} AIs.".format(mapfile, n))

    with open(mapfile, 'r') as f:
        m = json.load(f)

    games = []
    for i in range(n):
        games.append(GS.Game.from_json_setup({'punters' : n, 'punter' : i, 'map' : m}))

    k = games[0].k

    for i in range(k):
        edge = ais[i % n](games[i % n])

        if edge.owner != -1:
            print("Trying to claim an edge that is already claimed!")
            print("AI {} is trying to take {}'s edge.".format(i % n, edge.owner))
            sys.exit(1)

        for game in games:
            game.nodes[edge.source].edges[edge.target].owner = i % n

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
