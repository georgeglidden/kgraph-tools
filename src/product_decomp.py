from numpy import argmin, full
from collections import deque
from itertools import chain
from kgraph import *

class AdjacencyVector:
    """
    wraps an array w/ functions for calculating intersections in linear time
    given the elements are restricted to {0,...,V-1}.
    """
    def __init__(self, V, primary_adj_list=None):
        """
        incurs a one-time cost of O(V) to initialize the zero vector
        :param V: vector dimension
        """
        self._adj_vec = [0 for v in range(V)]
        if (primary_adj_list != None):
            self.set(primary_adj_list)

    def __getitem__(self, i):
        return self._adj_vec[i]

    def set(self, adj_list):
        """
        generates a row of the adjacency matrix in O(d)
        :param adj_list: iterable of d integers restricted to {0,...,V-1}.
        """
        self._adj_list = adj_list
        for v in adj:
            self._adj_vec[v] += 1

    def reset(self):
        """
        clears the previous row in O(d)
        """
        for v in self._adj_list:
            self._adj_vec[v] -= 1

    def intersection(self, secondary_adj_list, primary_adj_list=None):
        """
        intersects two subsets of the multiset {0,...,V-1} in time linear to
        their magnitude
        :param primary_adj_list:
        :param secondary_adj_list: iterable of integers
        """
        if (primary_adj_list != None):
            self.reset()
            self.set(primary_adj_list)
        return [w for w in secondary_adjacency_list
                if (self._adj_vec[w] != 0)]

class CartesianDecomposition:
    """
    a derivative implementation of Wilfried & Imrich 2006 (Recognizing
    Cartesian products in linear time).
    """
    def __init__(self, skeleton):
        """
        initializes the data structures necessary to decompose a kgraph skeleton
        under the cartesian product.
        :param skeleton: a k-colored, directed graph; see `kgraph.py`.
        """
        self.graph = skeleton
        # TODO screen out prime graphs
        self._prime = True
        # setup for decomposition
        self._setup = False
        if (not self._prime):
            # identify a minimum-degree vertex
            i = argmin([self.graph.deg(v) for v in self.graph.vertices()])
            self._v0 = self.graph.vertices()[i]
            # calculate the bfs order and build layers from equivalence classes
            self._bfs_order, self._bfs_distance = self.bfs(self._v0)
            # set decomposition flag
            self.decomposition = None
        else:
            self.decomposition = [self.graph]
        # set init flag
        self._setup = True

    def bfs(self, s, color=None, graph=None):
        """
        a generic breadth first search algorithm.
        TODO - abstract and move to `kgraph.py;` support unification of `bfs,`
        `labels,` and `CC.components.`
        :param s: seed vertex.
        :param color: an integer or iterable of integers, giving the color(s) by
        which to restrict edges. defaults to None; consider all edges regardless
        of color.
        :return: an array associating v -> distance(s, v).
        """
        if (graph == None):
            graph = self.graph
        order = []
        distance = [-1 for v in graph.vertices()]
        distance[s] = 0
        deq = deque([s])
        while len(deq) != 0:
            order.append(deq.popleft())
            v = order[-1]
            for w in graph.adj(v,symmetric=True):
                if (distance[w] == -1):
                    distance[w] = distance[v] + 1
                    deq.append(w)
        return order, distance

    def adj_layer(self, v, distance, level, color=None):
        """
        restricts the neighborhood of a vertex by its up, down, or cross edges,
        as given by the choice of BFS seed.
        :param v: the vertex whose neighborhood is restricted by `level.`
        :param distance: as returned by `bfs;` used to find the layer index of
        a given vertex.
        :param level: 'up,' 'down,' or 'cross' specify whether the neighbors w of `v` should be higher, lower, or equal as evaluated by `distance.`
        """
        if (level == 'up'):
            restriction = lambda w: distance(v) < distance(w)
        elif (level == 'down'):
            restriction = lambda w: distance(v) > distance(w)
        elif (level == 'cross'):
            restriction = lambda w: distance(v) == distance(w)
        else:
            raise ValueError("unrecognized level", level)
        restricted_adj_list = [w
                               for w in self.graph.adj(v, color, symmetric=True)
                               if restriction(w)]
        return restricted_adj_list

    def decompose(self):
        """
        :param s: seed for bfs. defines the unit layers and unit vertices.
        :param layers: vertice equivalence classes given by `distance(v,s).
        :param distance: associates each vertex v to the length of the shortest path from v to `s,` as given by breadth first search.
        """
        # sanity check
        if (not self._setup):
            raise Warning("call to `decompose` without setup flags; was this object initiated incorrectly?")
        # avoid redundant computation
        if (self.decomposition == None):
            # INIT: k-graphs have an implicit coloring that is necessarily finer
            # than or equal to the product coloring. we don't need to generate
            # d(v_0) color labels for L0_up, so we proceed to label L1_cross.
            merged_colors = []

            # INDUCT

            for i in range(1, self._bfs_radius):
                pass
            # extract product factors from the unit layers
            self.decomposition = [self.bfs(self._v0, color_set)
                                  for color_set in merged_colors]
        return self.decomposition

def main():
    vtc = [0,1,2,3,4,5]
    k2c3_edges = [(vtc[0],vtc[1],0),(vtc[1],vtc[2],0),(vtc[2],vtc[0],0),
                  (vtc[3],vtc[4],0),(vtc[4],vtc[5],0),(vtc[5],vtc[3],0),
                  (vtc[0],vtc[3],1),(vtc[1],vtc[4],1),(vtc[2],vtc[5],1)]
    E = ColoredDigraph(vertices=vtc,
                       edges=k2c3_edges,
                       k=2)
    print([e.to_string() for e in CartesianDecomposition(E).decompose()])

    vtc = list(range(12))
    k2k2c3_edges = [(vtc[0],vtc[1],0),(vtc[1],vtc[2],0),(vtc[2],vtc[0],0),
                    (vtc[3],vtc[4],0),(vtc[4],vtc[5],0),(vtc[5],vtc[3],0),
                    (vtc[6],vtc[7],0),(vtc[7],vtc[8],0),(vtc[8],vtc[6],0),
                    (vtc[9],vtc[10],0),(vtc[10],vtc[11],0),(vtc[11],vtc[9],0),
                    (vtc[0],vtc[3],1),(vtc[1],vtc[4],1),(vtc[2],vtc[5],1),
                    (vtc[0],vtc[6],2),(vtc[1],vtc[7],2),(vtc[2],vtc[8],2),
                    (vtc[6],vtc[9],1),(vtc[7],vtc[10],1),(vtc[8],vtc[11],1),
                    (vtc[3],vtc[9],2),(vtc[4],vtc[10],2),(vtc[5],vtc[11],2)]
    F = ColoredDigraph(vertices=vtc,
                       edges=k2k2c3_edges,
                       k=3)
    print([f.to_string() for f in CartesianDecomposition(F).decompose()])

if __name__ == "__main__":
    main()
