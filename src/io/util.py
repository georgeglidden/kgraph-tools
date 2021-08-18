from ..kgraph import ColoredDigraph

def save_kgraph(skeleton, path):
    graph_string = skeleton.to_string()
    with open(path, 'w+') as f:
        f.write(graph_string)

def from_string(graphstring):
    lines = graphstring.split('\n')
    #print("lines",lines)
    line_VEk, line_vertices = lines[:2]
    V, E, k = line_VEk.split(' ')
    V, E, k = int(V), int(E), int(k)
    vertices = line_vertices.split(' ')
    vertices = [int(v) for v in vertices]
    #print("V E K",V,E,k)
    #print("verices",vertices)
    skeleton = ColoredDigraph(vertices, [], k)
    for i in range(min(len(lines)-2,len(vertices))):
        v = vertices[i]
        adj_v = lines[i+2].split(',')
        assert (len(adj_v) == k), "color consistency"
        for color in range(k):
            adj = [int(w) for w in adj_v[color].split(' ')
                   if (w != '')]
            for w in adj:
                skeleton.add_edge(v,w,color)
    #print(f"string1:\n{graphstring}")
    #print(f"string2:\n{skeleton.to_string()}")
    str1 = str.strip(graphstring)
    str2 = str.strip(skeleton.to_string())
    min_len = min(len(str1),len(str2))
    assert (str1[:min_len] == str2[:min_len]), "explicit isomorphism" + str1 + '\n' + str2
    return skeleton

def load_kgraph(path):
    # todo - buffered loading for Very Large Graphs
    with open(path, 'r') as f:
        return from_string(f.read())
