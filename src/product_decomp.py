from numpy import argmin, full
from collections import deque
from itertools import chain
from kgraph import *

class AdjacencyVector:
    """
    a utility object for calculating neighborhood intersections in O(d)
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
        :param adj_list: iterable of d integers from the multiset {0,...,V-1}
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
    Cartesian products in linear time). every k-graph has a canonical labeling,
    so checking once and merging is sufficient to perform product decomposition.
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
            self._bfs_order = self.bfs(self._v0)
            self._bfs_radius = max(self._bfs_order)
            self._bfs_layers = self.binsort(items = self.graph.vertices(),
                                        nb_buckets = self._bfs_radius+1,
                                        key = lambda v: self._bfs_order[v])
            # set decomposition flag
            self.decomposition = None
        else:
            self.decomposition = [self.graph]
        # set init flag
        self._setup = True

    def binsort(self, items, nb_buckets, key):
        """
        :param items: a set of items. the domain of `key`
        :param nb_buckets: magnitude of the range of `key`
        :param key: a function sending `items` -> [0,...,`nb_buckets`-1]
        """
        buckets = [[] for _ in range(nb_buckets)]
        for x in items:
            buckets[key(x)].append(x)
        return buckets

    def bfs(self, s, color=None, graph=None):
        """
        a generic breadth first search algorithm.
        TODO - abstract and move to `kgraph.py;` support unification of `bfs,`
        `labels,` and `LazyCC.components.`
        :param s: seed vertex.
        :param color: an integer or iterable of integers, giving the color(s) by
        which to restrict edges. defaults to None; consider all edges regardless
        of color.
        :return: an array associating v -> distance(s, v).
        """
        if (graph == None):
            graph = self.graph
        distance = [-1 for v in graph.vertices()]
        distance[s] = 0
        deq = deque([s])
        while len(deq) != 0:
            v = deq.popleft()
            for w in graph.adj(v,symmetric=True):
                if (distance[w] == -1):
                    distance[w] = distance[v] + 1
                    deq.append(w)
        return distance
"""
    def labels(self, s):
        \"""
        uses a modified breadth first search to assign cartesian coordinates at
        every vertex.
        :param s: seed vertex
        :return: an array associating v to a k-dimensional coordinate vector
        :return: a k-dim array associating each coordinate vector to a vertex
        \"""
        coordinates = [-1 for v in self.graph.vertices()]
        coordinates[s] = [0 for color in self.graph.colors()]
        deq = deque([s])
        while len(deq) != 0:
            v = deq.popleft()
            for color in self.graph.colors():
                color_counts = coordinates[v].copy()
                for w in self.graph.adj(v,color,symmetric=True):
                    if (coordinates[w] == -1):
                        color_counts[color] += 1
                        coordinates[w] = color_counts.copy()
                        deq.append(w)
        for v in self.graph.vertices():
            coordinates[v] = tuple(coordinates[v])
        shape = tuple([max([coord[color] + 1
                            for coord in coordinates])
                       for color in self.graph.colors()])
        lookup = full(shape, -1)
        for v in self.graph.vertices():
            lookup[coordinates[v]] = v
        return coordinates, lookup
"""

    def is_unit(self, coordinate):
        """
        check if a coordinate corresponds to a unit vector
        :param coordinate: a k-dimensional coordinate vector
        :return: True if `coordinate` has only one nonzero element, otherwise
        False
        """
        return (len([z for z in coordinate if z == 0]) == len(coordinate - 1))

    def label_edge(self, coord1, coord2):
        """
        """
        path_colors = [color for color in self.graph.colors()
                       if (coord1[color]-coord2[color] != 0)]
        # test adjacency
        if (len(path_colors) == 1):
            return path_colors[0]
        else:
            return -1

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
        return [w for w in self.graph.adj(v, color, symmetric=True)
                if restriction(w)]
"""
    def consistency(self, layers, distance):
        \"""
        :param layers: vertice equivalence classes given by `distance(v,s).`
        :param distance: as returned by `bfs;` used to find the layer index of
        a given vertex.

        ~~~~

        :param labels: a coordinate labeling of each vertex. the corresponding
        graph is a product iff adjacent edges give rise to isomorphic subgraphs
        in every coordinate.
        :param lookup: an array associating each coordinate vector to a vertex.
        \"""
        k_zeros = [0 for color in graph.colors()]
        labels = [k_zeros.copy() for v in graph.vertices()]
        adj_vectors = [AdjacencyVector() for color in self.graph.colors()]
        # iterate layers
        for i in range(1, len(layers)-1):
"""

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
            # initial vertex labeling
            vertex_labels = [-1 for v in self.graph.vertices()]

            # INIT
            # get color-specific adjacency lists
            vertex_labels[self._v0] = (0 for color in range(self.graph.k()))
            v0_up = [self.adj_layer(self._v0,
                                    self._bfs_order
                                    ,'up',
                                    color)
                     for color in self.graph.colors()]
            # label up edges
            for color in self.graph.colors():
                up = v0_up[color]
                label = list(vertex_labels[self._v0])
                for w in up:
                    label[color] += 1
                    vertex_labels[w] = tuple(label)
            # INDUCT
            # initial color labeling, no merges come from INIT
            color_labels = self.graph.colors()
            merged_colors = []
            for l in range(1, self._bfs_radius):
"""             # pass one: label cross edges
                for v in self._bfs_layers[l]:
                    v_label = vertex_labels[v]
                    for color in self.graph.colors()
                        for w in self.adj_layer(v,
                                                self._bfs_order,
                                                'cross',
                                                color):
                            w_label = vertex_labels[w]
                            vw_label = self.label_edge(v_label, w_label)
                            clr1 = min(color, vw_label)
                            clr2 = max(color, vw_label)
                            if (color_labels[clr2] != clr_labels[clr1]):
                                color_labels[clr2] = clr_labels[clr1]
                                merged_colors.append(clr1, clr2)"""

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
