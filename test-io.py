from src import kgraph, io

def main():
    x = kgraph.ColoredDigraph(vertices=[1,2,3,4],
                              edges=[(1,2,0),
                                     (2,3,0),
                                     (3,4,0),
                                     (4,1,0),
                                     (4,4,0),
                                     (4,2,0)],
                              k=1)
    print("graph to be saved:\n" + x.to_string())
    io.save_kgraph(x, 'test.sk')
    x2 = io.load_kgraph('test.sk')
    print("graph loaded from file:\n" + x2.to_string())
if __name__ == "__main__":
    main()
