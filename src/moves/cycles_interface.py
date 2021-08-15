from itertools import chain

from ..kgraph import CC, ColoredDigraph
from .python_simple_cycles import simple_cycles

class CycleFinder:
    """
    interfaces between qpwo's cycle finder and the ColoredDigraph object
    """

    def __init__(self, skeleton):
        """
        :param skeleton: a ColoredDigraph object.
        """
        if (skeleton.k() != 1):
            raise ValueError()
        self.graph = skeleton
        # find cycles
        skeleton_adj = dict((v,self.graph.adj(v)[0])
                            for v in self.graph.vertices())
        self.cycles = tuple(simple_cycles(skeleton_adj))
        # build \tau
        self._tau = dict((v,set())
                         for v in self.graph.vertices())
        for c in range(self.C()):
            for v in self.cycles[c]:
                self._tau[v].add(c)

    def C(self):
        """
        :return: count cycles in `self.graph`.
        """
        return len(self.cycles)

    def __getitem__(self, v):
        return list(self._tau[v])

class CycleIntersection:

    def __init__(self, skeleton, cyclefinder):
        if (type(skeleton)!=ColoredDigraph):
            raise ValueError
        else:
            self.graph = skeleton
        if (type(cyclefinder)!=CycleFinder):
            raise ValueError
        else:
            self.cyclefinder = cyclefinder
        # find cycle intersections
        self._intersections = set()
        self._adj = [set() for c in range(self.C())]
        for c in range(self.C()):
            for v in self.cyclefinder.cycles[c]:
                for d in self.cyclefinder[v]:
                    if (c != d):
                        self._adj[c].add((d,v))
                        self._adj[d].add((c,v))
                        self._intersections.add((min([c,d]),max([c,d])))
        # find components in the cycle intersection graph
        self._CC = CC(self._intersections, vertices=range(self.C()))
        self._chains, self._connectivity = self._CC.components()
        # initialize the intersection vector
        self._loaded = []
        self._intersection_vector = [0 for _ in self.graph.vertices()]

    def C(self):
        """
        :return: count cycles in `self.graph`.
        """
        return len(self.cyclefinder.cycles)

    def I(self):
        """
        :return: count pairs of intersecting cycles.
        """
        return sum([len(self._adj(c))
                    for c in range(self.C())]) // 2

    def intersect(self, c, restrict=None):
        """
        :param c: the index of a cycle, between 0 and `self.C()`-1.
        :param restrict: a map from vertices to
        boolean values, use to omit vertices from
        the intersection.
        :return: iterable, cycles that intersect `c`.
        """
        if (restrict==None):
            restrict = lambda v: True
        return list(set(d for d,v in self._adj[c] if (not retrict(v))))

    def _set_vector(self, X):
        self._loaded = X
        for x in self._loaded:
            self._intersection_vector[x] += 1

    def _reset_vector(self):
        for x in self._loaded:
            self._intersection_vector[x] -= 1
        self._loaded = []

    def _filter_by_vector(self, X):
        return [x for x in X
                if self._intersection_vector[x] > 0]

    def intersect_vertices(self, c, d):
        """
        :param c: the index of a cycle, between 0 and `self.C()`-1.
        :param d: ""                                            "".
        :return: iterable, vertices shared between cycles `c` and `d`.
        """
        self._reset_vector()
        self._set_vector(self.cyclefinder.cycles[c])
        return self._filter_by_vector(self.cyclefinder.cycles[d])

    def component(self, v, c):
        """
        :param v: a vertex supporting the return path.
        :param c: index of the cycle at which the return path is rooted.
        :return: iterable, cycles traversed by the largest return path of `v`
        at `c`.
        """
        # find all cycles connected to `c`.
        chain = self._chains[self._connectivity[c]]
        # restrict the chain to `c` and all cycles not including `v`.
        filtered_chain = [0 for _ in range(self.C())]
        filtered_chain[c] = 1
        for d in chain:
            self._reset_vector()
            self._set_vector(self.cyclefinder.cycles[d])
            if (self._intersection_vector[v] == 0):
                filtered_chain[d] = 1
        # recompute the component rooted at `c`
        in_path = lambda d: filtered_chain[d]
        restr_CC, restr_connectivity = self._CC.components(filter=in_path)
        return restr_CC[restr_connectivity[c]]
