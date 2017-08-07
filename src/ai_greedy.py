from debug import db

def main(gs):
    e = gs.greedy_edge()
    if e is None:
        for i in range(gs.N):
            if len(gs.raw_edges[i]) > 0:
                a = i
                b = gs.raw_edges[i][0]
    else:
        a, b = gs.find_raw_edge(*e)
    return gs.claim(a, b)
