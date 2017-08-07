import json
import collections

# GameState1
#
# A representation of the game state suitable for use during actual play
#
# Reasonably quick to serialize / deserialize
#
# Does not need to be especially quick to apply moves, since this only happens
# once per actual move.
#
# "component" -- maximal set of nodes which are mutually reachable via
#   rivers that we have already claimed
# "raw node" / "raw edge" -- features of the original graph
#
# Each raw node is given a consecutive ID number. Components which contain
# only a single node have the same number as the node it contains. When
# two components are merged, the one with more nodes retains its number.
#
# As components are removed (by being merged into other components), the corresponding
# values in the various arrays that track component data become invalid.
#
# Attributes:
#   players -- number of players
#   me -- index of us
#   n -- number of components
#   N -- number of raw nodes
#   siteids -- the SiteID of each raw node
#   s2n -- mapping from SiteID to node id
#   comp -- comp[i] is the component that raw node i lies in.
#       It is guaranteed that comp[comp[i]] == comp[i]
#   component_size -- the number of raw nodes in component i
#   edges -- edges[i] is a list of edges that come from component i.
#       Each edge is a list [j, num] where j is the target component and num
#       is the number of raw edges from i to j.
#   value -- value[i][i] is the score we have gotten from component i
#       value[i][j] is the score we would gain by connecting component i to
#       component j, due to the mines in those components (for i != j)
#   raw_edges -- raw_edges[i] is a list of all raw nodes that are adjacent
#       to raw node i. Only includes edges that are still unclaimed
#
#   (not actually present:)
#   dists -- dists[i][j] is the least distance between raw nodes i and j,
#       or a large number of no connection is possible
#   raw_nodes -- a list of the raw nodes in component i
#

class GameState1:
    def from_board(board, players = 2, me = 0, settings = None):
        self = GameState1()
        self.players = players
        self.me = me
        self.set_settings(settings)

        n = board.n

        self.n = n
        self.N = n

        self.siteids = list(board.siteids)
        self.s2n = dict(board.s2n)
        self.comp = list(range(n))
        self.component_size = [1] * n
        # self.raw_nodes = [[i] for i in range(n)]
        self.edges = [[[j, 1] for j in ei] for ei in board.edges]
        self.value = None

        self.raw_edges = [list(ei) for ei in board.edges]

        self.compute_values(board)
        return self

    def set_settings(self, settings = None):
        if settings is None:
            settings = {}
        self.settings = settings
        self.futures = settings.get('futures', False)
        self.splurges = settings.get('splurges', False)
        self.options = settings.get('options', False)

    def compute_values(self, board):
        large = self.N + 1
        self.value = [[0 for j in range(self.N)] for i in range(self.N)]
        self.dists = [None] * self.N

        for i in board.mines:
            # Dijkstra's algorithm
            d = [large] * self.N
            d[i] = 0

            q = collections.deque([i])
            while len(q) > 0:
                j = q.popleft()
                for k in board.edges[j]:
                    if d[k] == large:
                        d[k] = d[j] + 1
                        q.append(k)


            # Score for connecting things to the mine at i
            self.dists[i] = d
            for j in range(self.N):
                self.value[i][j] += d[j] ** 2
                self.value[j][i] += d[j] ** 2

    def serialize(self):
        return [self.players, self.me, self.settings, self.n, self.N, self.siteids,
                list(self.s2n.items()), self.comp, self.component_size,
                self.edges, self.value, self.raw_edges]

    def deserialize(j):
        self = GameState1()
        self.players        = j[0]
        self.me             = j[1]
        settings            = j[2]
        self.n              = j[3]
        self.N              = j[4]
        self.siteids        = j[5]
        self.s2n            = dict(j[6])
        self.comp           = j[7]
        self.component_size = j[8]
        self.edges          = j[9]
        self.value          = j[10]
        self.raw_edges      = j[11]

        self.set_settings(settings)
        return self

    # node ids
    def claim_edge(self, a, b):
        self.raw_edges[a].remove(b)
        self.raw_edges[b].remove(a)

        ca = self.comp[a]
        cb = self.comp[b]

        if ca == cb:
            return

        self.n -= 1

        if self.component_size[ca] < self.component_size[cb]:
            ca, cb = cb, ca

        # Update comp

        for i in range(self.N):
            if self.comp[i] == cb:
                self.comp[i] = ca

        # Update component_size

        self.component_size[ca] += self.component_size[cb]

        # Update edges

        edge_ca = {}
        for ea in self.edges[ca]:
            if ea[0] != cb:
                edge_ca[ea[0]] = ea[1]

        for j, x in self.edges[cb]:
            if j == ca:
                continue

            edge_ca[j] = edge_ca.get(j, 0) + x

            edge_j = [[ca, None]]
            z = 0
            for k, y in self.edges[j]:
                if k == ca or k == cb:
                    z += y
                else:
                    edge_j.append([k, y])
            edge_j[0][1] = z
            self.edges[j] = edge_j

        eca = []
        for j in edge_ca:
            eca.append([j, edge_ca[j]])

        self.edges[ca] = eca

        # Update values

        for i in range(self.N):
            self.value[i][ca] += self.value[i][cb]
            self.value[ca][i] = self.value[i][ca]
        self.value[ca][ca] += self.value[cb][cb]

    # node ids
    def remove_edge(self, a, b):
        if b not in self.raw_edges[a]:
            return
        self.raw_edges[a].remove(b)
        self.raw_edges[b].remove(a)

        ca = self.comp[a]
        cb = self.comp[b]

        for i in range(len(self.edges[ca])):
            e = self.edges[ca][i]
            if e[0] == cb:
                if e[1] == 1:
                    self.edges[ca] = self.edges[ca][:i] + self.edges[ca][(i+1):]
                else:
                    e[1] -= 1
                break

        for i in range(len(self.edges[cb])):
            e = self.edges[cb][i]
            if e[0] == ca:
                if e[1] == 1:
                    self.edges[cb] = self.edges[cb][:i] + self.edges[cb][(i+1):]
                else:
                    e[1] -= 1
                break

    # node ids
    def apply_claim(self, who, source, target):
        if who == self.me:
            self.claim_edge(source, target)
        else:
            self.remove_edge(source, target)

    # Given components ca and cb, find a raw edge (a, b) which connects those components
    def find_raw_edge(self, ca, cb):
        if self.component_size[ca] < self.component_size[cb]:
            ca, cb = cb, ca

        for b in range(self.N):
            if self.comp[b] == cb:
                for a in self.raw_edges[b]:
                    if self.comp[a] == ca:
                        return (a, b)

    # component ids
    def greedy_edge(self):
        if self.n == 1:
            return None

        best = None
        best_value = -1

        for i in range(self.N):
            if self.comp[i] != i:
                continue

            for j, x in self.edges[i]:
                if self.value[i][j] > best_value:
                    best_value = self.value[i][j]
                    best = (i, j)

        return best

    def cur_score(self):
        score = 0
        for i in range(self.N):
            if self.comp[i] == i:
                score += self.value[i][i]
        return score

    def distance_histogram(self):
        h = {}
        for x in self.dists:
            if x is None:
                continue
            for y in x:
                if y < self.N:
                    h[y] = 1 + h.get(y, 0)
        return [h[i] for i in range(len(h))]
        # return sorted(list(h.items()))

    def summary(self):
        lines = []
        lines.append('{} punters, we are {}, our score is {}'.format(
                self.players, self.me, self.cur_score()))
        if hasattr(self, 'dists'):
            h = self.distance_histogram()
            lines.append('Distances: ' + str(h))
            lines.append('Max dist ' + str(len(h)))
        return '\n'.join(lines)

    # node ids
    def claim(self, a, b):
        return Move.claim(self, self.siteids[a], self.siteids[b])

    def option(self, a, b):
        return Move.option(self, self.siteids[a], self.siteids[b])

    def pas(self):
        return Move.pas(self)

    # node ids
    def splurge(self, route):
        return Move.splurge(self, [self.siteids[a] for a in route])

    def apply_move(self, who, move):
        if move.name == 'claim':
            self.apply_claim(who, self.s2n[move.source], self.s2n[move.target])
        if move.name == 'splurge':
            for i in range(len(move.route) - 1):
                self.apply_claim(who, self.s2n[move.route[i]], self.s2n[move.route[i + 1]])

class Move:
    def __init__(self, gs, name):
        self.gs = gs
        self.name = name

    # site ids
    def claim(gs, source, target):
        self = Move(gs, 'claim')
        self.source = source
        self.target = target
        return self

    def pas(gs):
        return Move(gs, 'pass')

    # site ids
    def splurge(gs, route):
        self = Move(gs, 'splurge')
        self.route = route
        return self

    def option(gs, source, target):
        self = Move(gs, 'option')
        self.source = source
        self.target = target
        return self

    def to_json(self):
        if self.name == 'claim':
            return {'claim' : {'punter' : self.gs.me, 'source' : self.source, 'target' : self.target}}
        if self.name == 'pass':
            return {'pass' : {'punter' : self.gs.me}}
        if self.name == 'splurge':
            return {'splurge' : {'punter' : self.gs.me, 'route' : self.route}}
        if self.name == 'option':
            return {'option' : {'punter' : self.gs.me, 'source' : self.source, 'target' : self.target}}

    def from_json(gs, j):
        if 'pass' in j:
            return Move.pas(gs)
        if 'claim' in j:
            return Move.claim(gs, j['claim']['source'], j['claim']['target'])
        if 'splurge' in j:
            return Move.splurge(gs, j['claim']['route'])
        if 'option' in j:
            return Move.option(gs, j['option']['source'], j['option']['target'])
