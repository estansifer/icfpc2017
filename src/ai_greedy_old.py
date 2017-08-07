from debug import db

def main(game):
    k = game.k
    # edge.owner is -1 if nobody claimed, else id of owner
    # game.me is our id

    comp = [-1] * k
    comp_nodes = [None] * k

    i = 0
    for j in range(k):
        if comp[j] >= 0:
            continue
        comp[j] = i
        comp_nodes[i] = [j]
        to_visit = [j]

        while len(to_visit) > 0:
            n1 = to_visit.pop()
            for n2, e in game.nodes[n1].edges.items():
                if e.owner == game.me and comp[n2] < 0:
                    to_visit.append(n2)
                    comp[n2] = i
                    comp_nodes[i].append(n2)

        i += 1


    comp_mines = [[] for i in range(k)] # c: mines of c

    for m in game.mines:
        comp_mines[comp[m]].append(m)

    db("The comps are:")
    db(comp)
    db(comp_mines)

    max_val = 0
    max_e = -1
    for e in game.edges:
        if e.owner != -1:
            continue
        comp1 = comp[e.source]
        comp2 = comp[e.target]

        if comp1 == comp2:
            continue

        val = 0
        for m in comp_mines[comp1]:
            for n in comp_nodes[comp2]:
                val += game.dists[m][n] ** 2
        for m in comp_mines[comp2]:
            for n in comp_nodes[comp1]:
                val += game.dists[m][n] ** 2

        if val > max_val:
            max_val = val
            max_e = e

    if max_val == 0:
        for e in game.edges:
            if e.owner == -1:
                return e

    db ("max added value is: " + str(max_val))
    db ("with edge: "+ str(max_e.source) + ' ' + str(max_e.target))
    return max_e

if __name__ == "__main__":
    import json
    import game_state as GS
    with open("../maps/official/sample.json", 'r') as f:
        j = json.load(f)

    message = {'punters' : 2, 'punter' : 0, 'map' : j}
    g = GS.Game.from_json_setup(message)
    for e in g.edges:
        print("Source: " + str(e.source) + ", Target: " + str(e.target))
    g.edges[0].owner = g.me
    g.edges[1].owner = g.me
    main(g)
