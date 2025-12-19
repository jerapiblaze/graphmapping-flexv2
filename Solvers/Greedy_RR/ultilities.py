import copy
import networkx as nx
import itertools

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

MAX_HOPS = 10   # nếu bạn muốn giới hạn hop, đặt đây; không muốn thì set None

def mapSliceRR(_phy:nx.DiGraph, _sfc:nx.DiGraph):
    phy = copy.deepcopy(_phy)
    first_vnode = [n for n in nx.topological_sort(_sfc)][0]

    # Round Robin pointer
    pnodes = list(phy.nodes)
    rr_cycle = itertools.cycle(pnodes)   # vòng quay RR

    used_node = []
    node_mappings = []
    link_mappings = []
    nhops = 0

    vnode_reqs = nx.get_node_attributes(_sfc, "req")
    vlink_reqs = nx.get_edge_attributes(_sfc, "req")

    for e in nx.edge_dfs(_sfc, first_vnode):
        v, w = e

        node_caps = nx.get_node_attributes(phy, "cap")
        link_caps = nx.get_edge_attributes(phy, "cap")

        i = __getNodeMapping(node_mappings, v)
        j = __getNodeMapping(node_mappings, w)

        # ---------------------------------------------------
        # 1. Map vnode v bằng ROUND ROBIN
        # ---------------------------------------------------
        if i is None:
            attempt = 0
            while attempt < len(pnodes):
                cand = next(rr_cycle)  # pick node RR
                if cand not in used_node and node_caps[cand] >= vnode_reqs[v]:
                    i = cand
                    break
                attempt += 1
            if i is None:
                return (_phy, None, None, {"isSuccess": False})
            
            used_node.append(i)
            node_caps[i] -= vnode_reqs[v]
            nx.set_node_attributes(phy, node_caps, "cap")
            node_mappings.append((v, i))

        # ---------------------------------------------------
        # 2. Map vnode w bằng ROUND ROBIN
        # ---------------------------------------------------
        if j is None:
            attempt = 0
            while attempt < len(pnodes):
                cand = next(rr_cycle)
                if cand not in used_node and node_caps[cand] >= vnode_reqs[w]:
                    j = cand
                    break
                attempt += 1
            if j is None:
                return (_phy, None, None, {"isSuccess": False})

            used_node.append(j)
            node_caps[j] -= vnode_reqs[w]
            nx.set_node_attributes(phy, node_caps, "cap")
            node_mappings.append((w, j))

        # ---------------------------------------------------
        # 3. Connect i → j bằng Dijkstra
        # ---------------------------------------------------
        try:
            hops = nx.shortest_path(phy, source=i, target=j, weight=None)
        except:
            return (_phy, None, None, {"isSuccess": False})

        # giới hạn hop nếu cần
        if MAX_HOPS is not None:
            if len(hops) - 1 > MAX_HOPS:
                return (_phy, None, None, {"isSuccess": False})

        links = nodeOrdersToLinks(hops)

        # Trừ cap link
        req = vlink_reqs[e]
        for link in links:
            if link_caps[link] < req:
                return (_phy, None, None, {"isSuccess": False})

        for link in links:
            link_caps[link] -= req
            link_mappings.append((e, link))

        nx.set_edge_attributes(phy, link_caps, "cap")
        nhops += len(links)

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