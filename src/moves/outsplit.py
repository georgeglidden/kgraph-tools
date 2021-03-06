from .k1move import K1Move

class Outsplit(K1Move):
    # move (O)

    def splittable(self, v):
        """
        :param v: a vertex
        :return: boolean, true when v has at least two out-adjacent neighbors.
        """
        adj_out = self.graph.adj(v)[0]
        return (len(set(adj_out)) >= 2)

    def _viable(self, component):
        """
        :param component: a three-tuple containing a splittable vertex, and two
        adjacency tables which partition its outgoing edge set.
        :return: boolean, true when the component satisfies its definition.
        """
        v, E1, E2 = component
        if (not self.splittable(v)):
            return False
        else:
            for w in self.graph.adj(v)[0]:
                # not a partition
                if (((w in E1) and (w in E2)) or
                    (not ((w in E1) or (w in E2)))):
                    return False
        return True

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph.
        :return: list of splittable vertices with arbitrary partitions of their
        outgoing edge sets. this list is sufficient, as all other partitions
        can be constructed by shuffling around the arbitrary partition.
        """
        components = []
        for v in self.graph.vertices():
            if self.splittable(v):
                E1, E2 = set(), set()
                x = next(w for w in self.graph.adj(v)[0] if (w != v))
                # the w!=v condition isn't strictly necessary, but since these
                # partitions are arbitrary anways, i want them to look nice.
                for w in self.graph.adj(v)[0]:
                    if (w == x):
                        E1.add(w)
                    else:
                        E2.add(w)
                components.append((v,E1,E2))
        return components

    def _action(self, component):
        """
        :param component: a three-tuple containing a splittable vertex, and two
        adjacency tables which partition its incoming edge set.
        :return: a function which outsplits a graph at the component.
        """
        def _outsplit(graph, component=component):
            # unpack the component
            v, E1, E2 = component
            # record the edges of the vertex, then delete the vertex and its edges.
            adj_out, adj_in = graph.adj(v)
            graph.del_vertex(v)
            # add two new vertices
            v1 = graph.add_vertex()
            v2 = graph.add_vertex()
            # add new incoming edges - duplicate old incoming edges between v1,v2.
            for w in adj_in:
                if (w != v):
                    graph.add_edge(w,v1,color=0)
                    graph.add_edge(w,v2,color=0)
            # add new outgoing edges - eponymously, split the old outgoing edges.
            for w in adj_out:
                if (w == v):
                    w = (v1 if (w in E1) else v2)
                    x = (v2 if (w in E1) else v1)
                    graph.add_edge(w,x,color=0)
                    if (v in E1):
                        graph.add_edge(v1,w,color=0)
                    elif (v in E2):
                        graph.add_edge(v2,w,color=0)
                    else:
                        assert False, f"{adj_in} != {E1} + {E2}"
                else:
                    if (w in E1):
                        graph.add_edge(v1,w,color=0)
                    elif (w in E2):
                        graph.add_edge(v2,w,color=0)
                    else:
                        assert False, f"{adj_in} != {E1} + {E2}"
            return graph, (v1,v2)
        return _outsplit

class OutsplitInverse(K1Move):

    def __init__(self, skeleton):
        self._out_adj_table = dict((v,0) for v in skeleton.vertices())
        self._in_adj_table = dict((v,0) for v in skeleton.vertices())
        super().__init__(skeleton)

    def split(self,v,w):
        """
        checks if a pair of vertices have been (in)split:
         (i)    v and w have identical incoming edges / in-neighbours,
         (ii)   v and w have no outgoing edges / out-neighbors in common,
         (iii)  v and w have at least one outgoing edge each.
        :param v: a vertex
        :param w: one or more vertices
        :return: every vertex w such that (v,w) satisfies (i)-(iii).
        """
        def c1(X, arr, omit):
            val = True
            #print(f"\t\t\tchecking {X} against {arr}; are they the same?")
            # consume the adjacency vector
            #print("before", arr)
            for i in range(len(X)):
                x = X[i]
                #print(x, arr[x])
                if (x==omit):
                    continue
                arr[x] -= 1
                if (arr[x] < 0):
                    val = False
                    break
            # regenerate the adjacency vector
            #print("after", arr)
            for j in range(i+1):
                x = X[j]
                arr[x] += 1
            #print("regen", arr)
            return val

        def c2(X, arr, omit):
            #print(f"\t\t\tchecking {X} against {arr}; are they disjoint?")
            return all(arr[x] == 0 for x in X if (x!=omit))

        if (type(w) == int):
            W = [w]
        else:
            W = w
        #print(f"is {v} split with any element of {W}?")
        # set the adjacency tables with v
        out_adj_v, in_adj_v = self.graph.adj(v)
        for x in out_adj_v:
            self._out_adj_table[x] += 1
        for x in in_adj_v:
            self._in_adj_table[x] += 1
        # filter W
        pairs = set()
        for w in W:
            #print(f"\tis {v} split with {w}?")
            out_adj_w, in_adj_w = self.graph.adj(w)
            #print(f"\tin of {v}: {in_adj_v}\n\tin of {w}: {in_adj_w}")
            #print(f"\tout of {v}: {out_adj_v}\n\tout of {w}: {out_adj_w}")
            # condition (iii) and a preliminary of (i)
            if ((len(out_adj_v) >= 1 and len(out_adj_w) >= 1)
                and (len(in_adj_v) == len(in_adj_w))):
                #print("\t\tpassed (iii)")
                # apply conditions (i) and (ii)
                if (not c1(in_adj_w, self._in_adj_table, v)):
                    #print("\t\tfailed on (i)")
                    continue
                elif c2(out_adj_w, self._out_adj_table, v):
                    #print("\t\tpassed (i) and (ii)")
                    pairs.add(w)
                #else:
                #    print("\t\tfailed (ii)")
        # reset adjacency tables
        for x in out_adj_v:
            self._out_adj_table[x] -= 1
        for x in in_adj_v:
            self._in_adj_table[x] -= 1
        return pairs

    def _viable(self, component):
        """
        checks if a pair of vertices is 1. well formed and 2. the result of
        move (I) as given by conditions (i)-(iii).
        :param component: two vertices
        :return: boolean, true when the vertices are a valid pair.
        """
        v,w = component
        if (self.graph.is_vertex(v) and self.graph.is_vertex(v)):
            return (len(self.split(v,w))>0)
        else:
            raise ValueError("expected a pair of vertices")

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph.
        :return: list of vertex pairs that have been split.
        """
        pairs = set()
        adj_table = dict((v,0) for v in self.graph.vertices())
        #print("="*100)
        #print("OUTSPLIT INVERSE SECONDARY CHECK")
        for v in self.graph.vertices():
            #print("checking candidates at", v)
            in_adj = self.graph.adj(v)[1]
            #print("\tout adj:", in_adj, len(in_adj))
            # first pass - each out-neighbor votes to keep their in-neighbors
            for x in in_adj:
                for z in self.graph.adj(x)[0]:
                    adj_table[z] += 1
            #print("\tadj table", adj_table)
            # second pass - filter each vertex that doesn't have 100% vote
            candidates = set()
            for x in in_adj:
                candidates.update([z for z in self.graph.adj(x)[0]
                                   if ((z!= v) and
                                       (adj_table[z] == len(in_adj)))])
            for x in in_adj:
                for z in self.graph.adj(x)[0]:
                    adj_table[z] -= 1
            #print("\tcandidates", candidates)
            # find viable pairs
            pairs.update([(min(v,w),max(v,w))
                          for w in self.split(v,candidates)
                          if self._viable((min(v,w),max(v,w)))])
        #print("="*100)
        return list(pairs)

    def _action(self, component):
        """
        :param component: two vertices (v,w) that satisfy conditions (i)-(iii)
        :return: a function which inverse outsplits a graph at the component.
        """

        def _outsplitinverse(graph, component=component):
            w1,w2 = component
            out_adj_1, in_adj = graph.adj(w1)
            out_adj_2 = graph.adj(w2)[0]
            graph.del_vertex(w1)
            graph.del_vertex(w2)
            w = graph.add_vertex()
            for v in in_adj:
                if ((v!=w1) and (v!=w2)):
                    graph.add_edge(v,w,color=0)
                else:
                    graph.add_edge(w,w,color=0)
            for v in (out_adj_1 + out_adj_2):
                if ((v!=w1) and (v!=w2)):
                    graph.add_edge(w,v,color=0)
            E1 = set(out_adj_1)
            E2 = set(out_adj_2)
            for E_ in [E1,E2]:
                for w_ in [w1,w2]:
                    if (w_ in E_):
                        E_.remove(w_)
                        E_.add(w)
            return graph, (w, E1, E2)

        return _outsplitinverse
