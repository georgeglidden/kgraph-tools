from itertools import chain
from collections import deque

class ColoredDigraph:
    """
    a mutable directed graph with k-colored edges
    """
    def __init__(self, vertices=[0], edges=[], k=1, adj=None):
        """
        constructs a mutable digraph with edges in k colors
        :param vertices: initial set of vertex labels
        :param edges: iterable of integer triplets defining edges with (source,
        range, color)
        :param k: number of edge colors
        :param adj: a preconstructed adjacency table. UNSAFE! use only when
        instantiating subgraphs from a well-defined ColoredDigraph object.
        """
        self._k = k
        self._vertices = []
        self._E = 0
        if (adj==None):
            self._adj = [{} for color in range(self.k())]
            for v in vertices:
                if (type(v) != int):
                    raise ValueError(f"expected integer vertex labels, not", type(v))
                self.add_vertex(v)
            for v,w,color in edges:
                self.add_edge(v,w,color)
        elif (set(adj.keys()) == set(self.colors())):
            # unsafe - only for instantiating subgraphs
            self._adj = adj
            self._vertices = vertices
        else:
            raise ValueError(f"the constructor received an adjacency table with keys {list(adj.keys())}, but a {k}-graph requires {k} numerically-keyed adjacency lists.")

    def _flip(self, v):
        """
        :param v: vertex to be flipped
        :return: (-1)*(v+1)
        """
        return (-1)*(v+1)

    def V(self):
        """
        :return: number of vertices
        """
        return len(self._vertices)

    def E(self):
        """
        :return: number of edges
        """
        return self._E

    def k(self):
        """
        :return: number of edge colors
        """
        return self._k

    def colors(self):
        """
        :return: edge colors as an interable
        """
        return range(self.k())

    def vertices(self):
        """
        :return: vertex labels
        """
        return self._vertices

    def add_vertex(self, v=None):
        """
        creates a new vertex & its adjacency lists
        :param v: the vertex label, defaults to V if undefined.
        """
        if (v==None):
            v = max(self.vertices()) + 1
        for color in self.colors():
            self._adj[color][v] = []
        self._vertices.append(v)
        return v

    def add_edge(self, v, w, color):
        """
        creates a new edge in one or more colors
        :param v: the source of the edge
        :param w: the range of the edge
        :param color: an integer or iterable of integers, giving the
        color(s) of edge to be created
        """
        if (type(color) == int):
            self._adj[color][v].append(w)
            self._adj[color][w].append(self._flip(v))
            self._E += 1
        else:
            try:
                for c in color:
                    self.add_edge(v,w,c)
            except:
                raise TypeError("expected an integer or iterable color, not", color)

    def adj(self, v, color=None, symmetric=False):
        """
        the weakly connected degree one neighborhood of a vertex
        :param v: the vertex whose edges are considered
        :param color: an integer or an iterable of integers, giving the
        color(s) on which to restrict edges. defaults to None; consider all
        edges regardless of color
        :param symmetric: if True, outgoing and incoming edge sets are merged.
        :return: a tuple (r(s^{-1}), s(r^{-1}) of vertices connected to `v` by,
        respectively, outgoing and incoming `color` edges. if the `symmetric`
        flag is True, a single list of vertices is returned.
        """
        if (color == None):
            color = self.colors()
        if (type(color) == int):
            adj_out = [w for w in self._adj[color][v]
                       if w >= 0]
            adj_in = [self._flip(z) for z in self._adj[color][v]
                      if z < 0]
        else:
            try:
                aggregate_out, aggregate_in = zip(*[self.adj(v, c)
                                                    for c in color])
                adj_out = list(chain(*aggregate_out))
                adj_in = list(chain(*aggregate_in))
            except:
                raise TypeError("expected an integer or iterable color, not", color)
        if (symmetric):
            return adj_out + adj_in
        else:
            return (adj_out, adj_in)

    def deg(self, v, color=None):
        """
        the number of edges incident to a vertex in one or more colors
        :param v: the vertex whose edges are considered
        :param color: an integer or an iterable of integers, giving the
        color(s) on which to restrict edges. defaults to None; consider all
        edges regardless of color
        :return: magnitude of the multiset of `color` edges incident to `v`
        """
        if (color == None):
            color = self.colors()
        if (type(color) == int):
            adj_out, adj_in = self.adj(v, color)
            return len(adj_out) + len(adj_in)
        else:
            try:
                return sum([self.deg(v, c) for c in color])
            except:
                raise TypeError("expected an integer or iterable color, not", color)

    def del_edge(self, v, w, color):
        """
        removes an edge in one or more colors
        :param v: the source of the edge
        :param w: the range of the edge
        :param color: an integer or an iterable of integers, giving the
        color(s) on which to remove an edge vw
        """
        if (type(color) == int):
            i = self._adj[color][v].index(w)
            del self._adj[color][v][i]
            j = self._adj[color][w].index(self._flip(v))
            del self._adj[color][w][j]
            self._E -= 1
        else:
            try:
                for c in color:
                    self.del_edge(v,w,c)
            except:
                raise TypeError("expected an integer or iterable color, not", color)

    def del_vertex(self, v):
        """
        removes a vertex, all edges sourced or ranged at the vertex, and its
        adjacency lists
        :param v: the vertex to delete
        """
        for color in self.colors():
            adj_out, adj_in = self.adj(v,color)
            for w in adj_out:
                self.del_edge(v,w,color)
            for x in adj_in:
                if (x == v):
                    continue
                self.del_edge(x,v,color)
            del self._adj[color][v]
        i = self._vertices.index(v)
        del self._vertices[i]

    def restrict_colors(self, colors):
        """
        :param colors: an ordered subset of {1,...,k}
        :return: a subgraph with edges restricted to `colors`
        """
        if (len(set(colors).intersection(set(range(self.k())))) == len(colors)):
            return ColoredDigraph(vertices=self.vertices(),
                                  adj={(color,self._adj[color])
                                       for color in colors},
                                  k=len(colors))
        else:
            raise ValueError("the restriction set must be a subset of {1,...,k}")

    def to_string(self):
        """
        :return: a string representation of the graph
        """
        l1 = f"{self.V()} {self.E()} {self.k()}"
        l2 = ' '.join(map(str,self.vertices()))
        adjacency_strings = [
            ','.join([
                ' '.join(map(str, self.adj(v,color)[0]))
                for color in self.colors()
            ]) for v in self.vertices()
        ]
        return '\n'.join([l1,l2]+adjacency_strings)

class CC(ColoredDigraph):
    def __init__(self, pairs):
        flat_pairs = chain(*pairs)
        unique_terms = set(flat_pairs)
        super().__init__(vertices=unique_terms,
                             edges=[(x,y,0) for (x,y) in pairs],
                             k=1)

    def components(self, filter=None):
        """
        implements connected components via breadth firsth search.
        :param filter: any boolean function on the vertex set
        :return CC: lists of connected vertices for each component
        :return connectivity: an array associating vertices to their compenent
        index in `CC.`
        """
        if (filter==None):
            filter = lambda v: True
        CC = []
        connectivity = [-1 for v in self.vertices()]
        condition = lambda v: ((connectivity[v] == -1) and filter(v))
        for u in self.vertices():
            if condition(u):
                connectivity[u] = len(CC)
                CC.append([])
                deq = deque([u])
                while len(deq) != 0:
                    CC[-1].append(deq.popleft())
                    v = CC[-1][-1]
                    for w in self.adj(v,symmetric=True):
                        if condition(w):
                            connectivity[w] = connectivity[v]
                            deq.append(w)
        return CC, connectivity

def main():
    vtc = [0,1,2,3,4,5]
    k2c3_edges = [(vtc[0],vtc[1],0),(vtc[1],vtc[2],0),(vtc[2],vtc[0],0),
                  (vtc[3],vtc[4],0),(vtc[4],vtc[5],0),(vtc[5],vtc[3],0),
                  (vtc[0],vtc[3],1),(vtc[1],vtc[4],1),(vtc[2],vtc[5],1)]
    E = ColoredDigraph(vertices=vtc,
                       edges=k2c3_edges,
                       k=2)
    print(E.to_string(),'\n')
    v = E.add_vertex()
    E.add_edge(v,vtc[1],0)
    E.add_edge(vtc[2],v,0)
    E.add_edge(v,vtc[3],1)
    print(E.to_string(),'\n')
    E.del_vertex(vtc[0])
    print(E.to_string(),'\n')

if __name__ == "__main__":
    main()
