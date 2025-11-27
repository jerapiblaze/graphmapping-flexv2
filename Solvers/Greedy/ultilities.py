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

def mapSlice(_phy:nx.DiGraph, _sfc:nx.DiGraph) -> tuple[nx.DiGraph, list[tuple[int,int]], list[tuple[tuple[int,int],tuple[int,int]]], dict]: #(currentPhy, nodeMappings, linkMapping, info)
    phy = copy.deepcopy(_phy)
    first_vnode = [n for n in nx.topological_sort(_sfc)][0]
    
    used_node = []
    node_mappings = []
    link_mappings = []
    nhops = 0
    
    vnode_reqs = nx.get_node_attributes(_sfc, "req")
    vlink_reqs = nx.get_edge_attributes(_sfc, "req")
    
    for e in nx.edge_dfs(_sfc, first_vnode):
        v, w = e
        i = __getNodeMapping(node_mappings, v)
        j = __getNodeMapping(node_mappings, w)
        node_caps = nx.get_node_attributes(phy, "cap")    
        link_caps = nx.get_edge_attributes(phy, "cap")
        # Map v if needed
        if (i is None):
            node_list = sorted(node_caps, key=node_caps.get, reverse=True)
            n = 0
            while (node_list[n] in used_node) or (node_caps[n] < vnode_reqs[v]):
                n += 1
                if (n >= len(node_list)):
                    n = -1
                    break
            if n == -1:
                return (_phy, None, None, {"isSuccess":False})
            i = node_list[n]
            used_node.append(i)
            node_caps[i] -= vnode_reqs[v]
            nx.set_node_attributes(phy, node_caps, "cap")
            node_mappings.append((v,i))
        # Map w if needed
        if (j is None):
            node_list = sorted(node_caps, key=node_caps.get, reverse=True)
            # n = 0
            # while (not node_list[n] in nx.neighbors(phy, i)) or (node_list[n] in used_node) or (node_caps[n] < vnode_reqs[w]):
            #     n += 1
            #     if (n >= len(node_list)):
            #         n = 0
            #         while (node_list[n] in used_node) or (node_caps[n] < vnode_reqs[w]):
            #             n += 1
            #             if (n >= len(node_list)):
                            # return (_phy, None, None, {"isSuccess":False})
            node_list = [n for n in node_list if not n in used_node and not node_caps[n] < vnode_reqs[w]]
            if len(node_list) == 0:
                return (_phy, None, None, {"isSuccess":False})
            n = 0
            while (not node_list[n] in nx.neighbors(phy, i)):
                n += 1
                if (n >= len(node_list)):
                    n = 0
                    break
            # if n == -1:
            #     return (_phy, None, None, {"isSuccess":False})
            j = node_list[n]
            used_node.append(j)
            node_caps[j] -= vnode_reqs[w]
            nx.set_node_attributes(phy, node_caps, "cap")
            node_mappings.append((w,j))
        # Connect i and j
        hops = physicalNodeConnect(phy, i, j, vlink_reqs[e], "cap")
        if hops is None:
            return (_phy, None, None, {"isSuccess":False})
        links = nodeOrdersToLinks(hops)
        for link in links:
            link_mappings.append((e, link))
            link_caps[link] -= vlink_reqs[e]
        nx.set_edge_attributes(phy, link_caps, "cap")
        nhops += len(links)
    return phy, node_mappings, link_mappings, {"isSuccess":True, "nHops": nhops}

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