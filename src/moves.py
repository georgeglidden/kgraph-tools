from kgraph import ColoredDigraph
from cycles_interface import CycleFinder, CycleIntersection

class Move:
    """
    base class for a k-graph rewriting system
    """
    def __init__(self, skeleton):
        """
        :param skeleton: a ColoredDigraph object.
        """
        self.graph = skeleton
        self.viable = self._check()
        self.active = (len(self.viable) > 0)

    def _viable(self, component):
        """
        generally, this method decides if the component permits a legal move.
        :param component: a subgraph of `self.graph`.
        :return: boolean, True iff the move is allowed on `component`.
        """
        raise NotImplementedError()

    def _check(self):
        """
        determines if there are any legal moves on the graph. ideally, it should
        calculate the set (or subset) of viable components.
        :return: a list that is non-empty when there are viable subgraphs.
        """
        raise NotImplementedError()

    def _action(self, component):
        """
        performs an action on the graph, with respect to certain properties of
        the subgraph.
        :param component: a viable subgraph.
        """
        raise NotImplementedError()

    def __call__(self, component, in_place=True):
        """
        performs the move if `component` is viable, and if the object is active.
        :param component: the subgraph on which the move is performed. must be
        viable, as defined by the implementation.
        :param in_place: (to be implemented) when False, `self.graph` will not be modified.
        """
        if (not self.active):
            return self.graph
        else:
            if (self._viable(component)):
                return self._action(component)
            else:
                raise ValueError("received a non-viable component.")

class K1Move(Move):
    """
    base class for the six ME-preserving moves on 1-graphs.
    """

    def _check(self):
        """
        preliminary check against higher-rank graphs.
        """
        if (self.graph.k() != 1):
            return []
        else:
            return self._secondary_check()

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph.
        :return: boolean, True iff there is a viable component in `self.graph`
        """
        raise NotImplementedError()

class SinkDelete(K1Move):

    def sink(self, v):
        """
        :param v: a vertex
        :return: boolean, True iff the vertex has no outgoing edges and at
        least one incoming edge.
        """
        adj_out, adj_in = self.graph.adj(v)
        return ((len(adj_out)==0) and
                (len(adj_in)>=1))

    def _viable(self, component):
        """
        :param component: one or more vertices
        :return: boolean, True iff every vertex in `component` is a sink.
        """
        if (type(component) == int):
            component = [component]
        try:
            return all([self.sink(v) for v in component])
        except TypeError as e:
            raise e
        except:
            raise ValueError("received a non-vertex element in `component`.")

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph.
        :return: list of sinks.
        """
        return [v for v in self.graph.vertices() if self.sink(v)]

    def _action(self, component):
        """
        :param component: one or more sinks
        :return: a ColoredDigraph with every vertex from `component` deleted.
        """
        if (type(component) == int):
            component = [component]
        try:
            for v in component:
                self.graph.del_vertex(v)
        except TypeError as e:
            raise e
        except:
            raise ValueError("received a non-vertex element in `component`.")
        return self.graph

class Reduction(K1Move):

    def reducible(self, v):
        """
        :param v: a vertex
        :return: boolean, True iff (1) all outgoing edges go to the same vertex,
        and there is only one incoming edge and (2) there are no self loops
        """
        adj_out, adj_in = self.graph.adj(v)
        # (1)
        if (len(set(adj_out)) == len(adj_in) == 1):
            # (2)
            return (adj_out[0] != v)
        else:
            return False

    def _viable(self, component):
        """
        :param component: one or more vertices
        :return: boolean, True iff every vertex in `component` is reducible.
        """
        if (type(component) == int):
            component = [component]
        try:
            return all([self.reducible(v) for v in component])
        except TypeError as e:
            raise e
        except:
            raise ValueError("received a non-vertex element in `component`.")

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph.
        :return: list of reducible vertices.
        """
        return [v for v in self.graph.vertices() if self.reducible(v)]

    def _action(self, component):
        """
        :param component: one or more reducible vertices
        :return: a ColoredDigraph with every vertex in `component` deleted, and
        updated edges to preserve connectivity.
        """
        if (type(component) == int):
            component = [component]
        try:
            for v in component:
                # get the relevant edges
                adj_out, adj_in = self.graph.adj(v)
                # delete v and its edges
                self.graph.del_vertex(v)
                # per `reducible`, we know there is only one incoming edge.
                w = adj_in[0]
                # similarly, we know that `adj_out`=[x,x,...,x].
                # create new edges from w to x, for each edge v to x.
                for x in adj_out:
                    self.graph.add_edge(w,x,color=0)
        except TypeError as e:
            raise e
        except:
            raise ValueError("received a non-vertex element in `component`.")
        return self.graph

class Insplit(K1Move):

    def splittable(self, v):
        adj_in = self.graph.adj(v)[1]
        return (len(set(adj_in)) >= 2)

    def _viable(self, component):
        """
        :param component: a three-tuple containing a splittable vertex, and two
        adjacency tables which partition its incoming edge set.
        :return: boolean, True iff component satisfies the definition.
        """
        v, E1, E2 = component
        if (not self.splittable(v)):
            return False
        else:
            for w in self.graph.adj(v)[1]:
                in_E1 = (E1[w] != 0)
                in_E2 = (E2[w] != 0)
                # not a partition
                if ((in_E1 and in_E2) or (not (in_E1 or in_E2))):
                    return False
        return True

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph.
        :return: list of splittable vertices with arbitrary partitions of their
        incoming edge sets.
        """
        components = []
        for v in self.graph.vertices():
            if self.splittable(v):
                adjacency_table = dict((v,0) for v in self.graph.vertices())
                E1, E2 = adjacency_table.copy(), adjacency_table.copy()
                for w in self.graph.adj(v)[1]:
                    adjacency_table[w] += 1
                x = next(i for i in adjacency_table
                         if (adjacency_table[i]!=0))
                for w in self.graph.adj(v)[1]:
                    if (w == x):
                        E1[w] = adjacency_table[w]
                    else:
                        E2[w] = adjacency_table[w]
                components.append((v,E1,E2))
        return components

    def _action(self, component):
        """
        :param component: a three-tuple containing a splittable vertex, and two
        adjacency tables which partition its incoming edge set.
        :return: a graph, insplit at the component.
        """
        # unpack the component
        v, E1, E2 = component
        # record the edges of the vertex, then delete the vertex and its edges.
        adj_out, adj_in = self.graph.adj(v)
        self.graph.del_vertex(v)
        # add two new vertices
        v1 = self.graph.add_vertex()
        v2 = self.graph.add_vertex()
        # add new outgoing edges - duplicate old outgoing edges between v1,v2.
        for w in adj_out:
            if (w != v):
                self.graph.add_edge(v1,w,color=0)
                self.graph.add_edge(v2,w,color=0)
        # add new incoming edges - eponymously, split the old incoming edges.
        for w in adj_in:
            in_E1 = (E1[w] != 0)
            in_E2 = (E2[w] != 0)
            if (w == v):
                w = (v1 if in_E1 else v2)
                x = (v2 if in_E1 else v1)
                self.graph.add_edge(x,w,color=0)
            if in_E1:
                self.graph.add_edge(w,v1,color=0)
            elif in_E2:
                self.graph.add_edge(w,v2,color=0)
            else:
                assert False, 'viability check failed: malformed partition'
        return self.graph

class Outsplit(K1Move):

    def splittable(self, v):
        adj_out = self.graph.adj(v)[0]
        return (len(set(adj_out)) >= 2)

    def _viable(self, component):
        """
        :param component: a three-tuple containing a splittable vertex, and two
        adjacency tables which partition its incoming edge set.
        :return: boolean, True iff component satisfies the definition.
        """
        v, E1, E2 = component
        if (not self.splittable(v)):
            return False
        else:
            for w in self.graph.adj(v)[0]:
                in_E1 = (E1[w] != 0)
                in_E2 = (E2[w] != 0)
                # not a partition
                if ((in_E1 and in_E2) or (not (in_E1 or in_E2))):
                    return False
        return True

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph.
        :return: list of splittable vertices with arbitrary partitions of their
        incoming edge sets.
        """
        components = []
        for v in self.graph.vertices():
            if self.splittable(v):
                adjacency_table = dict((v,0) for v in self.graph.vertices())
                E1, E2 = adjacency_table.copy(), adjacency_table.copy()
                for w in self.graph.adj(v)[0]:
                    adjacency_table[w] += 1
                x = next(i for i in adjacency_table
                         if (adjacency_table[i]!=0 and i!=v))
                # the i!=v condition isn't strictly necessary, but since these
                # partitions are arbitrary anways, i want them to look nice ):<
                for w in self.graph.adj(v)[0]:
                    if (w == x):
                        E1[w] = adjacency_table[w]
                    else:
                        E2[w] = adjacency_table[w]
                components.append((v,E1,E2))
        return components

    def _action(self, component):
        """
        :param component: a three-tuple containing a splittable vertex, and two
        adjacency tables which partition its incoming edge set.
        :return: a graph, insplit at the component.
        """
        # unpack the component
        v, E1, E2 = component
        # record the edges of the vertex, then delete the vertex and its edges.
        adj_out, adj_in = self.graph.adj(v)
        self.graph.del_vertex(v)
        # add two new vertices
        v1 = self.graph.add_vertex()
        v2 = self.graph.add_vertex()
        # add new incoming edges - duplicate old incoming edges between v1,v2.
        for w in adj_in:
            if (w != v):
                self.graph.add_edge(w,v1,color=0)
                self.graph.add_edge(w,v2,color=0)
        # add new outgoing edges - eponymously, split the old outgoing edges.
        for w in adj_out:
            in_E1 = (E1[w] != 0)
            in_E2 = (E2[w] != 0)
            if (w == v):
                w = (v1 if in_E1 else v2)
                x = (v2 if in_E1 else v1)
                self.graph.add_edge(x,w,color=0)
            if in_E1:
                self.graph.add_edge(v1,w,color=0)
            elif in_E2:
                self.graph.add_edge(v2,w,color=0)
            else:
                assert False, 'viability check failed: malformed partition'
        return self.graph

class CuntzSplice(K1Move):

    def __init__(self, skeleton):
        """
        :param skeleton: a ColoredDigraph object.
        """
        self.graph = skeleton
        self.cyclefinder = CycleFinder(self.graph)
        self.cycleintersection = CycleIntersection(self.graph, self.cyclefinder)
        self.viable = self._check()
        self.active = (len(self.viable) > 0)

    def condition_C(self, v):
        """
        :param v: a vertex
        :return: boolean, True iff v supports at least two return paths
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
                # non-loop cycle
                mu = cycles_at_v[0]
                if (len(self.cycleintersection.intersect(mu)) == 0):
                    return False
                else:
                    nu = self.cycleintersection.intersect(mu)[0]
                    # exactly two return paths when component {mu,nu} ~= K_2
                    return (len(self.cycleintersection.intersect(nu))==1)
        elif (nb_cycles == 2):
            # two cycles; at least one is not a loop.
            mu1,mu2 = cycles_at_v
            # exactly two return paths when mu1 and mu2 only intersect eachother
            return (self.cycleintersection)
        else:
            # > 2 return paths
            return True

    def _viable(self, component):
        """
        :param component: one or more vertices
        :return: boolean, True iff every vertex in `component` satisfies the
        condition.
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
        :return: a graph with the Cuntz Splice performed on every vertex in
        `component`.
        """
        if (type(component) == int):
            component = [component]
        try:
            for v in component:
                w1 = self.graph.add_vertex()
                w2 = self.graph.add_vertex()
                self.graph.add_edge(v,w1,color=0)
                self.graph.add_edge(w1,v,color=0)
                self.graph.add_edge(w1,w1,color=0)
                self.graph.add_edge(w1,w2,color=0)
                self.graph.add_edge(w2,w1,color=0)
                self.graph.add_edge(w2,w2,color=0)
        except TypeError as e:
            raise e
        except:
            raise ValueError("received a non-vertex element in `component`.")
        return self.graph

class Eclose(CuntzSplice):

    def condition_P(self, v):
        """
        :param v: a vertex
        :return: boolean, True iff v has one loop and no other return path, and
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
        :return: boolean, True iff every vertex in `component` satisfies the
        condition.
        """
        if (type(component) == int):
            u = component
            if self.condition_P(u):
                return all(self.condition_C(w)
                           for w in self.graph.adj(u)[0] if (w!=u))
            else:
                return False
        else:
            raise TypeError("the component vertex was not of type int")

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
        :return: a graph, formed by performing move (P) on the component vertex.
        """
        if (type(component) == int):
            u = component
            S = [w for w in self.graph.adj(u)[0] if (w!=u)]
            for v in S:
                # Cuntz Splice at every vertex of `S`
                w1 = self.graph.add_vertex()
                w2 = self.graph.add_vertex()
                self.graph.add_edge(v,w1,color=0)
                self.graph.add_edge(w1,v,color=0)
                self.graph.add_edge(w1,w1,color=0)
                self.graph.add_edge(w1,w2,color=0)
                self.graph.add_edge(w2,w1,color=0)
                self.graph.add_edge(w2,w2,color=0)
                # eclose the cycle at `u`
                self.graph.add_edge(w2,u,color=0)
                self.graph.add_edge(w2,u,color=0)
            return self.graph
        else:
            raise TypeError("the component vertex was not of type int")

def main():
    print("\nSINK DELETION")
    g1 = ColoredDigraph(vertices=[0,1,2,3,4],
                        edges=[(0,1,0),(1,2,0),(1,3,0),(4,3,0)])
    print("initial graph")
    print(g1.to_string())
    SD = SinkDelete(g1)
    print("viable:", SD.viable)
    print("final graph")
    print(SD(SD.viable).to_string())
    print("\nREDUCTION")
    g2 = ColoredDigraph(vertices=[0,1,2,3,4],
                        edges=[(0,1,0),(1,2,0),(1,2,0),(2,3,0),(3,4,0),(4,0,0)])
    print("initial graph")
    print(g2.to_string())
    R = Reduction(g2)
    print("viable:", R.viable)
    print("final graph")
    print(R(R.viable).to_string())
    print("\nINSPLIT")
    g3 = ColoredDigraph(vertices=[0,1,2,3,4],
                        edges=[(0,2,0),(1,2,0),(2,3,0),(2,4,0)])
    print("initial graph")
    print(g3.to_string())
    I = Insplit(g3)
    print("viable:", I.viable)
    print("final graph")
    print(I(I.viable[0]).to_string())
    print("\nOUTSPLIT")
    g4 = ColoredDigraph(vertices=[0,1,2,3,4],
                        edges=[(0,2,0),(1,2,0),(2,3,0),(2,4,0),(2,2,0)])
    print("initial graph")
    print(g4.to_string())
    O = Outsplit(g4)
    print("viable:", O.viable)
    print("final graph")
    print(O(O.viable[0]).to_string())
    print("\nCUNTZ SPLICE")
    g5 = ColoredDigraph(vertices=[0,1],edges=[(0,0,0),(0,1,0),(1,0,0)])
    print("initial graph")
    print(g5.to_string())
    C = CuntzSplice(g5)
    print("viable:", C.viable)
    print("final graph")
    print(C(C.viable[-1]).to_string())
    print("\nECLOSE")
    g6 = ColoredDigraph(vertices=[0,1,2],edges=[(0,0,0),(0,1,0),
                                                (1,0,0),(1,1,0),
                                                (2,0,0),(2,1,0),(2,2,0)])
    print("initial graph")
    print(g6.to_string())
    P = Eclose(g6)
    print("viable:", P.viable)
    print("final graph")
    g6_2 = P(P.viable[-1])
    print(g6_2.to_string())

if __name__ == "__main__":
    main()
