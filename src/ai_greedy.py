from debug import db

def main(game):
    # edge.owner is -1 if nobody claimed, else id of owner
    # game.me is our id

    # first lets find the neighbours in our_graph

    our_graph = {n:[] for n in game.nodes}
    full_graph = {n:[] for n in game.nodes}
    for e in game.edges:
        if e.owner == game.me:
            our_graph[e.source].append(e.target)
            our_graph[e.target].append(e.source)
        full_graph[e.source].append(e.target)
        full_graph[e.target].append(e.source)

    comp = {n:-1 for n in game.nodes} # the component of each node
    comp_nodes = {} # the nodes of each component ie c:nodes of c

    i = 0
    #dist[(m,n)]
    for n in game.nodes:
        if comp[n]>=0:
            continue
        comp[n] = i
        comp_nodes[i] = [n]
        to_visit = [n]

        while len(to_visit)>0:
            n1 = to_visit.pop()
            for n2 in our_graph[n1]:
                if comp[n2]<0:
                    to_visit.append(n2)
                    comp[n2] = i
                    comp_nodes[i].append(n2)

        i += 1


    comp_mines = {c:[] for c in comp_nodes} # c: mines of c

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

        val=0
        for m in comp_mines[comp1]:
            for n in comp_nodes[comp2]:
                val += game.dists[(m,n)]*game.dists[(m,n)]
        for m in comp_mines[comp2]:
            for n in comp_nodes[comp1]:
                val += game.dists[(m,n)]*game.dists[(m,n)]

        if val>max_val:
            max_val = val
            max_e = e
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
    for n in g.nodes:
        print (n)
    for e in g.edges:
        print("Source: " + str(e.source) + ", Target: " + str(e.target))
    g.edges[0].owner = g.me
    g.edges[1].owner = g.me
    main(g)
