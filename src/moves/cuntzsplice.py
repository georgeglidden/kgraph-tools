from .k1move import K1Move
from .cycles_interface import CycleFinder, CycleIntersection

class CuntzSplice(K1Move):
    # move (C)

    def __init__(self, skeleton):
        """
        :param skeleton: a ColoredDigraph object.
        """
        self.graph = skeleton

        # associates every vertex to the cycles it supports.
        self.cyclefinder = CycleFinder(self.graph)
        # an undirected graph: nodes are cycles, edges correspond to cycles
        # whose paths intersect.
        self.cycleintersection = CycleIntersection(self.graph, self.cyclefinder)

        self.viable = self._check()
        self.active = (len(self.viable) > 0)

    def condition_C(self, v):
        """
        :param v: a vertex
        :return: boolean, true when v supports at least two return paths
        """
        cycles_at_v = self.cyclefinder[v]
        nb_cycles = len(cycles_at_v)
        if (nb_cycles == 0):
            return False
        elif (nb_cycles == 1):
            if (len(self.cyclefinder.cycles[cycles_at_v[0]]) == 1):
                # loop(s) - are there at least two?
                return (len([w for w in self.graph.adj(v)[0]
                             if w == v]) >= 2)
            else:
                # one non-loop cycle - does it intersect with any others?
                mu = cycles_at_v[0]
                return (len(self.cycleintersection.intersect(mu)) > 0)
        else:
            # >= 2 return paths
            return True

    def _viable(self, component):
        """
        :param component: one or more vertices
        :return: boolean, true when every vertex in `component` satisfies
        condition C.
        """
        if (type(component) == int):
            component = [component]
        try:
            return all([self.condition_C(v) for v in component])
        except TypeError as e:
            raise e
        except:
            raise ValueError("received a non-vertex element in `component`.")

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph.
        :return: list of vertices which support two return paths.
        """
        return [v for v in self.graph.vertices()
                if self.condition_C(v)]

    def _action(self, component):
        """
        :param component: one or more vertices
        :return: a function which Cuntz splices a graph at the component.
        """

        def _cuntzsplice(graph, component=component):
            v = component
            w1 = graph.add_vertex()
            w2 = graph.add_vertex()
            graph.add_edge(v,w1,color=0)
            graph.add_edge(w1,v,color=0)
            graph.add_edge(w1,w1,color=0)
            graph.add_edge(w1,w2,color=0)
            graph.add_edge(w2,w1,color=0)
            graph.add_edge(w2,w2,color=0)
            return graph, (v,w1,w2)

        return _cuntzsplice

class CuntzSpliceInverse(CuntzSplice):

    def c1(self, x, out_adj_x, in_adj_x):
        """
        checks condition (i)
        :param x: a vertex
        :param out_adj_x: vertices connected to x by outgoing edges
        :param in_adj_x: vertices connected to x by incoming edges
        :return: boolean, true if x supports only a loop and a 2-cycle.
        """
        # indegree = outdegree
        if (len(out_adj_x) == len(in_adj_x) == 2):
            if x in out_adj_x:
                i = out_adj_x.index(x)
            else:
                i = -1
            # has a loop
            if ((i >= 0) and (x in in_adj_x)):
                y = out_adj_x[i-1]
                # has a 2-cycle with y
                return ((y!=x) and (y in in_adj_x))
            else:
                return False
        else:
            return False

    def c2(self, x, out_adj_x, in_adj_x):
        """
        checks condition (ii)
        :param x: a vertex
        :param out_adj_x: vertices connected to x by outgoing edges
        :param in_adj_x: vertices connected to x by incoming edges
        :return: boolean, true when x supports only a loop and two 2-cycles.
        """
        # indegree = outdegree
        if (len(out_adj_x) == len(in_adj_x) == 3):
            if x in out_adj_x:
                i = out_adj_x.index(x)
            else:
                i = -1
            # has a loop
            if ((i >= 0) and (x in in_adj_x)):
                y = out_adj_x[i-1]
                z = out_adj_x[i-2]
                # has a 2 cycle with y,z
                return ((y!=x) and (y in in_adj_x) and
                        (z!=x) and (z in in_adj_x))
            else:
                return False
        else:
            return False

    def c3(self, x, omit, cyclefinder, cycleintersection, graph):
        """
        checks condition (iii)
        :param x: a vertex
        :param omit: vertices to ignore
        :param cyclefinder: maps vertices to cycles and cycles to vertices.
        :param cycleintersection: a graphlike object describing the intersection
        of cycles in `cyclefinder`.
        :param graph: the graph within which all the other objects ^ exist.
        :return: boolean, true when `x` has at least two return paths that do
        not traverse any vertex in `omit`.
        """
        # cycles restricting the contents of `omit`
        cycles_at_x = [c for c in cyclefinder[x]
                       if all((o not in cyclefinder.cycles[c])
                              for o in omit)]
        nb_cycles = len(cycles_at_x)
        if (nb_cycles == 0):
            return False
        elif (nb_cycles == 1):
            # cycle is a loop - how many loops?
            if (len(cyclefinder.cycles[cycles_at_x[0]]) == 1):
                return (len([
                    w for w in graph.adj(x)[0] if (w == x)
                    ]) >= 2)
            else:
                # one non-loop cycle - how many intersections?
                mu = cycles_at_x[0]
                filter = lambda v: all((v!=o) for o in omit)
                mu_adj = cycleintersection.intersect(mu, filter)
                return (len(mu_adj) > 0)
        else:
            return True

    def motif(self, v):
        """
        tries to find a (C)-motif, a tuple of vertices (u,w,v) such that
         (i)    v has a self loop, two more edges going to and from a vertex w,
                and no other edges.
         (ii)   w has a self loop, two edges going to and from v, and two
                verties going to and from a vertex u.
         (iii)  u has at least two return paths that do not traverse v or w.
        :param v: a vertex
        :return: the (C)-motif at `v`, or an empty tuple.
        """
        out_adj_v, in_adj_v = self.graph.adj(v)
        # condition (i)
        if self.c1(v, out_adj_v, in_adj_v):
            w = next(x for x in out_adj_v
                     if (x!=v))
            out_adj_w, in_adj_w = self.graph.adj(w)
            # condition (ii)
            if self.c2(w, out_adj_w, in_adj_w):
                u = next(x for x in self.graph.adj(w)[0]
                         if ((x!=v) and (x!=w)))
                # condition (iii)
                if self.c3(u, (w,v),
                           self.cyclefinder,
                           self.cycleintersection,
                           self.graph):
                    return (u,w,v)
        return ()

    def _viable(self, component):
        """
        :param component: list of tuples of three vertices w, v1, v2
        :return: boolean, true when (w, v1, v2) is the (C)-motif at v2
        """
        if (type(component) == tuple):
            component = [component]
        return all((m == self.motif(m[-1]))
                   for m in component)

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph.
        :return: a list of all (C)-motifs in the graph.
        """
        motifs = []
        for v in self.graph.vertices():
            motif_at_v = self.motif(v)
            if (len(motif_at_v) == 3):
                motifs.append(motif_at_v)
        return motifs

    def _action(self, component):
        """
        :param component: a (C)-motif (w, v1, v2)
        :return: a function which inverse Cuntz splices a graph at the
        component.
        """

        def _cuntzspliceinverse(graph, component=component):
            w, v1, v2 = component
            graph.del_vertex(v1)
            graph.del_vertex(v2)
            return graph, w

        return _cuntzspliceinverse
