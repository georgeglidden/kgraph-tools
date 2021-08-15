from .k1move import K1Move
from itertools import chain

class SinkDelete(K1Move):
    # move (S)

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
        :return: a graph with every vertex from `component` deleted.
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

class SinkDeleteInverse(K1Move):

    def _viable(self, component):
        """
        :param component: one or more vertices
        :return: boolean, True iff every element in the component is a vertex.
        """
        if (type(component) == int):
            component = [component]
        return all([self.graph.is_vertex(v) for v in component])

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph.
        :return: every vertex in the graph.
        """
        return self.graph.vertices()

    def _action(self, component):
        """
        :param component: one or more vertices
        :return: a graph with a new vertex incident to all vertices in the
        component.
        """
        if (type(component) == int):
            component = [component]
        s = self.graph.add_vertex()
        for v in component:
            self.graph.add_edge(v,s,color=0)
        return self.graph
