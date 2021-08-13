from .k1move import K1Move

class Reduction(K1Move):
    # move (R)

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
        :return: a graph with every vertex in `component` deleted, and
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
