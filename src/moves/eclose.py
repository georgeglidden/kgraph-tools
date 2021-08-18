from .cuntzsplice import CuntzSplice, CuntzSpliceInverse

from itertools import chain

class Eclose(CuntzSplice):
    # move (P)

    def condition_P(self, v):
        """
        :param v: a vertex
        :return: boolean, true when v has one loop and no other return path, and
        the loop has an exit.
        """
        outgoing_v = self.graph.adj(v)[0]
        nb_outgoing = len(outgoing_v)
        loops_at_v = [w for w in outgoing_v if w == v]
        nb_loops = len(loops_at_v)
        cycles_at_v = self.cyclefinder[v]
        nb_cycles = len(cycles_at_v)
        return ((nb_loops == 1) and             # supports a loop
                (nb_cycles == nb_loops) and     # and no other return path,
                (nb_outgoing - nb_loops > 0))   # and the loop has an exit.

    def _viable(self, component):
        """
        :param component: a vertex
        :return: boolean, true when the component vertex satisfies condition P,
        and its outgoing neighbors support condition C.
        """
        if (self.graph.is_vertex(component)):
            u = component
            if self.condition_P(u):
                return all(self.condition_C(w)
                           for w in self.graph.adj(u)[0] if (w!=u))
            else:
                return False
        else:
            raise ValueError("the component must be a vertex")

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph.
        :return: list of vertices whose return paths consists of a single
        loop, and whose outgoing neighbors all support >=2 return paths.
        """
        return [v for v in self.graph.vertices()
                if self._viable(v)]

    def _action(self, component):
        """
        :param component: a vertex
        :return: a function which ecloses a graph at the component.
        """
        def _eclose(graph, component=component):
            u = component
            S = [w for w in graph.adj(u)[0] if (w!=u)]
            for v in S:
                # Cuntz Splice at every vertex of `S`
                w1 = graph.add_vertex()
                w2 = graph.add_vertex()
                graph.add_edge(v,w1,color=0)
                graph.add_edge(w1,v,color=0)
                graph.add_edge(w1,w1,color=0)
                graph.add_edge(w1,w2,color=0)
                graph.add_edge(w2,w1,color=0)
                graph.add_edge(w2,w2,color=0)
                # eclose the cycle at `u`
                graph.add_edge(w2,u,color=0)
                graph.add_edge(w2,u,color=0)
            return graph, u
        return _eclose

class EcloseInverse(CuntzSpliceInverse):

    def condition_P(self, v, omit):
        """
        :param v: a vertex
        :return: boolean, true when v has one loop and no other return path, and
        the loop has an exit.
        """
        #print(f"does vertex {v} meet condition (P)?")
        outgoing_v = self.graph.adj(v)[0]
        nb_outgoing = len(outgoing_v)
        loops_at_v = [w for w in outgoing_v if w == v]
        nb_loops = len(loops_at_v)
        cycles_at_v = [c for c in self.cyclefinder[v]
                       if all((not (c in self.cyclefinder[o]))
                              for o in omit)]
        nb_cycles = len(cycles_at_v)
        return ((nb_loops == 1) and             # supports a loop
                (nb_cycles == nb_loops) and     # and no other return path,
                (nb_outgoing - nb_loops > 0))   # and the loop has an exit.

    def c1(self, x, out_adj_x, in_adj_x):
        """
        checks condition (i)-P
        :param x: a vertex
        :param out_adj_x: vertices connected to x by outgoing edges
        :param in_adj_x: vertices connected to x by incoming edges
        :return: boolean, true if x supports a loop, a 2-cycle, and an exit.
        """
        # indegree = outdegree
        if ((len(out_adj_x) == 4) and (len(in_adj_x) == 2)):
            if x in out_adj_x:
                i = out_adj_x.index(x)
            else:
                i = -1
            # has a loop
            if ((i >= 0) and (x in in_adj_x)):
                z1 = out_adj_x[i-1]
                z2 = out_adj_x[i-2]
                z3 = out_adj_x[i-3]
                if ((z1 == z2) and (z3 != z2)):
                    y = z3
                    u = z1
                elif ((z1 == z3) and (z2 != z3)):
                    y = z2
                    u = z1
                elif ((z2 == z3) and (z1 != z3)):
                    y = z1
                    u = z2
                else:
                    return False
                # has a 2-cycle with y and an exit to elsewhere
                return ((y!=x) and (y!=u) and
                        (y in in_adj_x) and
                        (not (u in in_adj_x)))
            else:
                return False
        else:
            return False

    def motif(self, v):
        """
        tries to find a (P)-motif, a tuple of vertices (u,w,v) such that
         (i)    v has a self loop, two more edges going to and from a vertex w,
                and two outgoing edges to z.
         (ii)   w has a self loop, two edges going to and from v, and two
                verties going to and from a vertex u.
         (iii)  u has at least two return paths that do not traverse v or w.
        :param v: a vertex
        :return: the (P)-motif at `v`, or an empty tuple.
        """
        out_adj_v, in_adj_v = self.graph.adj(v)
        # condition (i)
        #print(f"searching for a (P)-motif at {v} with adj {out_adj_v}, {in_adj_v}")
        if self.c1(v, out_adj_v, in_adj_v):
            w = next(x for x in in_adj_v
                     if (x!=v))
            z = next(x for x in out_adj_v
                     if ((x!=v) and (x!=w)))
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
                    return (u,w,v,z)
        return ()

    def _viable(self, component):
        """
        :param component: a vertex
        :return: boolean, true when the vertex is a bin label and satisfies the
        condition of move (P).
        """
        if (self.graph.is_vertex(component)):
            u = component
            if (u in self._bins):
                v2 = list(chain(m[2] for m in self._bins[u]))
                return self.condition_P(u, omit=v2)
            else:
                return False
        else:
            raise ValueError("the component must be a vertex")

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph. every (P)-motif
        is identified and bucket sorted by its exit vertex.
        :return: list of vertices corresponding to the keys of `self._bins`.
        """
        self._bins = dict()
        motifs = []
        # first pass - find the motifs and construct the bins
        for v in self.graph.vertices():
            #print("checking vertex",v)
            motif_at_v = self.motif(v)
            if (len(motif_at_v) == 4):
                #print(f"motif at {v}: {motif_at_v}")
                u = motif_at_v[3]
                self._bins[u] = []
                motifs.append(motif_at_v)
        #print("motifs", motifs)
        # second pass - sort the motifs by their bin label
        for m in motifs:
            u = m[3]
            self._bins[u].append(m)
        #print("sorted motifs", self._bins)
        # third pass - filter for malformed `u`
        keys = []
        for u in self._bins.keys():
            v2 = list(chain(m[2] for m in self._bins[u]))
            if self.condition_P(u,omit=v2):
                keys.append(u)
        #print("keys:", keys)
        return keys

    def _action(self, component):
        """
        :param component: a vertex that has been eclosed.
        :return: a function which inverse ecloses a graph at the component.
        """
        def _ecloseinverse(graph, component=component):
            motifs = self._bins[component]
            for m in motifs:
                _, v1, v2, u = m
                assert u == component, "it fucking better"
                graph.del_vertex(v1)
                graph.del_vertex(v2)
            return graph, u
        return _ecloseinverse
