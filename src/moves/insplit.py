from .k1move import K1Move

class Insplit(K1Move):
    # move (I)

    def splittable(self, v):
        """
        :param v: a vertex
        :return: boolean, true when v has at least two in-adjacent neighbors.
        """
        adj_in = self.graph.adj(v)[1]
        return (len(set(adj_in)) >= 2)

    def _viable(self, component):
        """
        :param component: a three-tuple containing a splittable vertex, and two
        adjacency tables which partition its incoming edge set.
        :return: boolean, true when the component satisfies its definition.
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
        incoming edge sets. this list is sufficient, as all other partitions
        can be constructed by shuffling around the arbitrary partition.
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
                # the i!=v condition isn't strictly necessary, but since these
                # partitions are arbitrary anways, i want them to look nice.
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
        :return: the graph formed by insplitting at the component.
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
