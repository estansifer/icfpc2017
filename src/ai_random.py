import random

# Takes an instance of Game and returns an instance of Edge, namely the
# edge we have chosen.
def main(game):
    e = []
    for edge in game.edges:
        if edge.owner == -1:
            e.append(edge)
    return random.choice(e)
