import copy
import networkx as nx
import random

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

MAX_HOPS = 10

def mapSliceRS(_phy:nx.DiGraph, _sfc:nx.DiGraph):
    phy = copy.deepcopy(_phy)

    # vnode list
    vnodes = list(nx.topological_sort(_sfc))
    num_v = len(vnodes)

    # physical node caps
    node_caps = nx.get_node_attributes(phy, "cap")
    link_caps = nx.get_edge_attributes(phy, "cap")

    # random physical nodes
    pnodes = list(phy.nodes)
    if len(pnodes) < num_v:
        return _phy, None, None, {"isSuccess": False, "reason": "Not enough physical nodes"}

    chosen = random.sample(pnodes, num_v)
    node_mappings = []

    vnode_reqs = nx.get_node_attributes(_sfc, "req")
    vlink_reqs = nx.get_edge_attributes(_sfc, "req")

    # map nodes + deduct
    for v, p in zip(vnodes, chosen):
        req = vnode_reqs.get(v, 0)
        if node_caps[p] < req:
            return _phy, None, None, {"isSuccess": False, "reason": "Node cap insufficient"}
        node_caps[p] -= req
        node_mappings.append((v, p))
    nx.set_node_attributes(phy, node_caps, "cap")

    # map links
    link_mappings = []
    nhops = 0

    for e in _sfc.edges:
        u, v = e
        pu = __getNodeMapping(node_mappings, u)
        pv = __getNodeMapping(node_mappings, v)

        req = vlink_reqs.get((u, v), 0)

        # shortest path
        try:
            path = nx.shortest_path(phy, source=pu, target=pv, weight=None)
        except:
            return _phy, None, None, {"isSuccess": False, "reason": "No path"}

        # === hop constraint ===
        hops = len(path) - 1
        if hops > MAX_HOPS:
            return _phy, None, None, {"isSuccess": False, "reason": "Hop limit exceeded"}

        # Convert to physical links
        links = [(path[i], path[i+1]) for i in range(len(path)-1)]

        # Check cap
        for link in links:
            if link_caps[link] < req:
                return _phy, None, None, {"isSuccess": False, "reason": "Link cap insufficient"}

        # Deduct
        for link in links:
            link_caps[link] -= req
            link_mappings.append((e, link))

        nhops += hops

    nx.set_edge_attributes(phy, link_caps, "cap")

    return phy, node_mappings, link_mappings, {"isSuccess": True, "nHops": nhops}

def __getNodeMapping(node_mappings:list[tuple[int,int]], vnode:int) -> int|None:
    for nm in node_mappings:
        if nm[0] == vnode:
            return nm[1]
    return None

def __getEdgeMapping(edge_mappings:list[tuple[tuple[int,int],tuple[int,int]]], vlink:tuple[int,int]) -> tuple[int,int]|None:
    for em in edge_mappings:
        if em[0] == vlink:
            return em[1]
    return None