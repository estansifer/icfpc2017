import random

# Takes an instance of Game and returns an instance of Edge, namely the
# edge we have chosen.
def main(gs):
    e = []
    for i in range(gs.N):
        for j in gs.raw_edges[i]:
            e.append((i, j))
    a, b = random.choice(e)
    return gs.claim(a, b)
