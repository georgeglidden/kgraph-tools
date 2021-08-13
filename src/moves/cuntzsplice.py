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
