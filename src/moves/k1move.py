from .move import Move

class K1Move(Move):
    """
    base class for the six ME-preserving moves on 1-graphs.
    """

    def _check(self):
        """
        preliminary check against higher-rank graphs.
        """
        if (self.graph.k() != 1):
            return []
        else:
            return self._secondary_check()

    def _secondary_check(self):
        """
        determines if there are any legal moves on the graph. ideally it should
        calculate the set (or a sufficient subset) of viable components.
        :return: a list that is non-empty when there are viable subgraphs.
        """
        raise NotImplementedError()
