def pivot(edges, adj_edges, edge_color, v, adj_vec):
    print(f"v{v}")
    # edges connected to v
    incident_to_v = adj_edges[v]
    # neighborhood of v
    N_v = [edges[i][1] for i in incident_to_v]
    # adjacency vector of v
    for w in N_v:
        adj_vec[w] += 1
    for w in N_v:
        if (w == v):
            # loop
            continue
        # edges connected to w
        incident_to_w = adj_edges[w]
        # neighborhood of w
        N_w = [edges[i][1] for i in incident_to_w]
        for x in N_w:
            if (x == w):
                # loop
                continue
            elif (x == v):
                # two-cycle
                continue
            elif (adj_vec[x] != 0):
                print(f"triangle [{v}, {w}, {x}]")
                continue
            # edges connected to x
            incident_to_x = adj_edges[x]
            # neighborhood of x
            N_x = [edges[i][1] for i in incident_to_x]
            for z in N_x:
                if (z == x):
                    # loop
                    continue
                elif (z == w):
                    # two-cycle
                    continue
                elif (adj_vec[z] != 0):
                    print(f"pivot square [{v}, {w}, {x}, {z}]")
    for w in N_v:
        adj_vec[w] -= 1

V = 12
E = 24
edges = [(0, 1), (0, 3), (0, 6), (0, 2), (1, 2), (1, 4), (1, 7), (1, 0), (2, 0), (2, 5), (2, 8), (2, 1), (3, 4), (3, 9), (3, 0), (3, 5), (4, 5), (4, 10), (4, 1), (4, 3), (5, 3), (5, 11), (5, 2), (5, 4), (6, 7), (6, 9), (6, 0), (6, 8), (7, 8), (7, 10), (7, 1), (7, 6), (8, 6), (8, 11), (8, 2), (8, 7), (9, 10), (9, 3), (9, 6), (9, 11), (10, 11), (10, 4), (10, 7), (10, 9), (11, 9), (11, 5), (11, 8), (11, 10)]
assert len(edges) == 2*E
assert all((0 <= min([v,w]) <= max([v,w]) < V) for v,w in edges)
edge_color = [-1 for _ in range(2*E)]
adj_edges = [[] for _ in range(V)]
for i in range(2*E):
    v = edges[i][0]
    adj_edges[v].append(i)
v = 0
adj_vec = [0 for _ in range(V)]
pivot(edges, adj_edges, edge_color, v, adj_vec)
