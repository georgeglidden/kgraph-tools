from .cuntzsplice import CuntzSplice

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
