
from lark import Tree 

def draw_png(tree: Tree, filename: str, rankdir: 'Literal["TB", "LR", "BT", "RL"]'="LR", **kwargs) -> None:
    graph = pydot__tree_to_graph(tree, rankdir, **kwargs)
    graph.write_png(filename)


def pydot__tree_to_graph(tree, rankdir="LR", **kwargs):
    """Creates a colorful image that represents the tree (data+children, without meta)

    Possible values for `rankdir` are "TB", "LR", "BT", "RL", corresponding to
    directed graphs drawn from top to bottom, from left to right, from bottom to
    top, and from right to left, respectively.

    `kwargs` can be any graph attribute (e. g. `dpi=200`). For a list of
    possible attributes, see https://www.graphviz.org/doc/info/attrs.html.
    """

    import pydot  # type: ignore
    graph = pydot.Dot(graph_type='digraph', rankdir=rankdir, **kwargs)

    i = [0]

    def new_leaf(leaf):
        node = pydot.Node(i[0], label=repr(leaf))
        i[0] += 1
        graph.add_node(node)
        return node

    def _to_pydot(subtree):
        color = hash(subtree.data) & 0xffffff
        color |= 0x808080

        subnodes = [_to_pydot(child) if isinstance(child, Tree) else new_leaf(child)
                    for child in subtree.children]
        node = pydot.Node(i[0], style="filled", shape="Mrecord",fillcolor="#%x" % color, label=subtree.data+' | '+str(subtree.type))
        i[0] += 1
        graph.add_node(node)

        for subnode in subnodes:
            graph.add_edge(pydot.Edge(node, subnode))

        return node

    _to_pydot(tree)
    return graph
