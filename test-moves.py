from src.kgraph import CC, ColoredDigraph
from src.moves.insplit import Insplit as I, InsplitInverse as IInverse
from src.moves.cuntzsplice import CuntzSplice as C, CuntzSpliceInverse as CInverse
from src.moves.reduction import Reduction as R, ReductionInverse as RInverse
from src.moves.sinkdelete import SinkDelete as S, SinkDeleteInverse as SInverse

def main():
    print("moves/ module unit test\n")

    print("MOVE (S)")
    g = ColoredDigraph(vertices=[1,2,3],
                       edges=[(1,2,0),
                              (1,3,0),
                              (3,2,0)],
                       k=1)
    print("  pre graph")
    print(g.to_string())
    S_g = S(g)
    print("  viable components")
    print(S_g.viable)
    print("  post graph")
    print(S_g(S_g.viable[0]).to_string())

    print("MOVE (S)^{-1}")
    g = ColoredDigraph(vertices=[1,2,3],
                       edges=[(1,2,0),
                              (1,3,0),
                              (3,2,0)],
                       k=1)
    print("  pre graph")
    print(g.to_string())
    SInverse_g = SInverse(g)
    print("  viable components")
    print(SInverse_g.viable)
    print("  post graph")
    print(SInverse_g(S_g.viable).to_string())

    print("MOVE (R)")
    g = ColoredDigraph(vertices=[1,2,3],
                       edges=[(1,2,0),
                              (1,3,0),
                              (3,2,0)],
                       k=1)
    print("  pre graph")
    print(g.to_string())
    R_g = R(g)
    print("  viable components")
    print(R_g.viable)
    print("  post graph")
    print(R_g(R_g.viable[0]).to_string())

    print("MOVE (R)^{-1}")
    g = ColoredDigraph(vertices=[1,2,3],
                       edges=[(1,2,0),
                              (1,3,0),
                              (3,2,0)],
                       k=1)
    print("  pre graph")
    print(g.to_string())
    RInverse_g = RInverse(g)
    print("  viable components")
    print(RInverse_g.viable)
    print("  post graph")
    print(RInverse_g(RInverse_g.viable[0]).to_string())

    print("MOVE (I)")
    g = ColoredDigraph(vertices=[1,2,3,4],
                       edges=[(1,2,0),
                              (1,3,0),
                              (2,2,0),
                              (3,2,0),
                              (2,4,0)],
                       k=1)
    print("  pre graph")
    print(g.to_string())
    I_g = I(g)
    print("  viable components")
    print(I_g.viable)
    print("  post graph")
    print(I_g(I_g.viable[0]).to_string())

    print("MOVE (I)^{-1}")
    print("  pre graph")
    print(g.to_string())
    IInverse_g = IInverse(g)
    print("  viable components")
    print(IInverse_g.viable)
    print("  post graph")
    print(IInverse_g(IInverse_g.viable[0]).to_string())

    print("MOVE (C)")
    g = ColoredDigraph(vertices=[1],
                       edges=[(1,1,0),
                              (1,1,0)],
                       k=1)
    print("  pre graph")
    print(g.to_string())
    C_g = C(g)
    print("  viable components")
    print(C_g.viable)
    print("  graph (C)")
    print(C_g(C_g.viable[-1]).to_string())
    C_g = C(g)
    print("  viable components")
    print(C_g.viable)
    print("  graph (C) (C)")
    print(C_g(C_g.viable[-1]).to_string())
    C_g = C(g)
    print("  viable components")
    print(C_g.viable)
    print("  graph (C) (C) (C)")
    print(C_g(C_g.viable[-1]).to_string())


    print("MOVE (C)^{-1}")
    print("  pre graph")
    print(g.to_string())
    CInverse_g = CInverse(g)
    print("  viable components")
    print(CInverse_g.viable)
    print("  graph (C)^{-1}")
    print(CInverse_g(CInverse_g.viable[0]).to_string())
    CInverse_g = CInverse(g)
    print("  viable components")
    print(CInverse_g.viable)
    print("  graph (C)^{-1} (C)^{-1}")
    print(CInverse_g(CInverse_g.viable[0]).to_string())
    CInverse_g = CInverse(g)
    print("  viable components")
    print(CInverse_g.viable)
    print("  graph (C)^{-1} (C)^{-1} (C)^{-1}")
    print(CInverse_g(CInverse_g.viable[0]).to_string())

if __name__ == "__main__":
    main()
