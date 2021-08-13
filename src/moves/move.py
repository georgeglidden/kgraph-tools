class Move:
    """
    base class for a k-graph rewriting system
    """
    def __init__(self, skeleton):
        """
        :param skeleton: a ColoredDigraph object.
        """
        self.graph = skeleton
        self.viable = self._check()
        self.active = (len(self.viable) > 0)

    def _viable(self, component):
        """
        generally, this method decides if the component permits a legal move.
        :param component: a subgraph of `self.graph`.
        :return: boolean, True iff the move is allowed on `component`.
        """
        raise NotImplementedError()

    def _check(self):
        """
        determines if there are any legal moves on the graph. ideally, it should
        calculate the set (or a sufficient subset) of viable components.
        :return: a list that is non-empty when there are viable subgraphs.
        """
        raise NotImplementedError()

    def _action(self, component):
        """
        performs an action on the graph, with respect to certain properties of
        the subgraph.
        :param component: a viable subgraph.
        :return: the graph formed by action on the component.
        """
        raise NotImplementedError()

    def __call__(self, component, in_place=True):
        """
        performs the move if `component` is viable, and if the object is active.
        :param component: the subgraph on which the move is performed. must be
        viable, as defined by the implementation.
        :param in_place: (to be implemented) when False, `self.graph` will not be modified.
        :return: the graph formed by action on the component.
        """
        if (not self.active):
            return self.graph
        else:
            if (self._viable(component)):
                return self._action(component)
            else:
                raise ValueError("received a non-viable component.")
