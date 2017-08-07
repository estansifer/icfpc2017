import json
import random

class Board:
    def __init__(self):
        self.n = 0 # number of nodes

        # node data
        self.siteids = []
        self.s2n = {} # mapping from siteid to nodeid
        self.xy = [] # list of (x, y) pairs
        self.ismine = [] # list of True/False
        self.mines = [] # list of nodeids

        # edge data
        self.edges = []
        self.num_edges = 0

    def add_node(self, siteid = None, ismine = False, x = None, y = None):
        nodeid = self.n

        self.siteids.append(siteid)
        if siteid is not None:
            self.s2n[siteid] = nodeid
        self.ismine.append(ismine)
        if ismine:
            self.mines.append(nodeid)
        if x is None or y is None:
            self.xy.append(None)
        else:
            self.xy.append((x, y))

        self.edges.append([])
        self.n += 1

    # source, target are given as nodeids
    def add_edge(self, source, target):
        self.edges[source].append(target)
        self.edges[target].append(source)
        self.num_edges += 1

    def from_json(j):
        self = Board()

        for s in j['sites']:
            if 'x' in s:
                self.add_node(s['id'], False, s['x'], s['y'])
            else:
                self.add_node(s['id'], False)

        for r in j['rivers']:
            self.add_edge(self.s2n[r['source']], self.s2n[r['target']])

        for m in j['mines']:
            a = self.s2n[m]
            self.ismine[a] = True
            self.mines.append(a)

        return self

    def from_json_file(mapfile):
        with open(mapfile, 'r') as f:
            j = json.load(f)
        return Board.from_json(j)

    def summary(self):
        return '{} nodes, {} edges, {} mines'.format(self.n,
                self.num_edges, len(self.mines))

    def layout_initial(self):
        for i in range(self.n):
            self.xy[i] = (random.random(), random.random())

    def layout_relax(self, numsteps = 10):
        import numpy as np
        n = self.n

        x = np.array([xy[0] for xy in self.xy])
        y = np.array([xy[1] for xy in self.xy])
        connected = np.zeros((n, n), dtype = bool)
        diag = np.identity(n, dtype = bool)

        for i in range(n):
            for j in self.edges[i]:
                connected[i, j] = True

        xlow = np.min(x)
        xhigh = np.max(x)
        ylow = np.min(y)
        yhigh = np.max(y)

        x = np.sqrt(n) * (x - xlow) / (xhigh - xlow)
        y = np.sqrt(n) * (y - ylow) / (yhigh - ylow)

        for i in range(numsteps):
            dx = np.zeros((n,))
            dy = np.zeros((n,))

            dd = (x[:, None] - x[None, :]) ** 2 + (y[:, None] - y[None, :]) ** 2
            dd[diag] = 1

            force_a = np.log(dd)
            # force_b = -1 / dd
            force_b = -1 / np.sqrt(dd)
            force_a[~connected] = 0
            force_b[connected] = 0
            force = force_a + force_b
            force[diag] = 0

            dx = np.sum(force * (x[None, :] - x[:, None]) / np.sqrt(dd), axis = 1)
            dy = np.sum(force * (y[None, :] - y[:, None]) / np.sqrt(dd), axis = 1)
            x += 0.1 * dx
            y += 0.1 * dy

        # Normalize positions to (0, 1)

        xlow = np.min(x)
        xhigh = np.max(x)
        ylow = np.min(y)
        yhigh = np.max(y)

        x = (x - xlow) / (xhigh - xlow)
        y = (y - ylow) / (yhigh - ylow)

        for i in range(n):
            self.xy[i] = (x[i], y[i])

    def layout_normalize(self):
        xs = [xy[0] for xy in self.xy]
        ys = [xy[1] for xy in self.xy]

        xlow = min(xs)
        xhigh = max(xs)
        ylow = min(ys)
        yhigh = max(ys)

        for i in range(self.n):
            self.xy[i] = ((self.xy[i][0] - xlow) / (xhigh - xlow),
                    (self.xy[i][1] - ylow) / (yhigh - ylow))
