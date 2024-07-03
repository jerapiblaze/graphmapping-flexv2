import copy
import networkx as nx

def nodeOrdersToLinks(orders:list) -> list[tuple[int,int]]:
    links = list()
    for i in range(len(orders)-1):
        links.append((orders[i], orders[i+1]))
    return links

def __permute__(ans, a, l, r):
    if l == r:
        return ans.append(a)
    else:
        a = copy.deepcopy(a)
        for i in range(l, r):
            a[l], a[i] = a[i], a[l]
            __permute__(ans, a, l+1, r)
            a[l], a[i] = a[i], a[l]

def __getPermutations(l:list) -> list[list]:
    n  = len(l)
    permutations = []
    __permute__(permutations, l, 0, n)
    return permutations

def physicalNodeConnect(graph:nx.DiGraph, start, end, requirement, attr_key):
    tmp_graph = nx.restricted_view(
        graph,
        [],
        tuple((x, y) for x, y, attr in graph.edges(data=True) if attr[attr_key] <= requirement)
    )
    try:
        path = nx.shortest_path(tmp_graph, start, end, attr_key)
    except nx.NetworkXNoPath:
        path = None
    except nx.NetworkXUnfeasible:
        path = None
    return path