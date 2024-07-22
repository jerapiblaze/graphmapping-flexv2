import networkx as nx
import random
import scipy
import copy
import time

from Solvers.Greedy.ultilities import *
from utilities.profiler import StopWatch

def Greedy(PHY:nx.DiGraph, SLICE_SET:list[nx.DiGraph], profiler:StopWatch, timelimit:int=0) -> dict[str, int]:
    start_time = time.time()
    solution = dict()
    current_PHY = PHY
    for sfc in SLICE_SET:
        if not timelimit is None and round(time.time() - start_time - timelimit) >= 0:
            profiler.add_stop("TIME LIMIT REACHED")
            break
        s = SLICE_SET.index(sfc)
        profiler.add_stop(f"Slice {s}")
        configurations = sfc
        profiler.add_stop(f"Slice {s}: {len(configurations)} posible configs")
        phy = copy.deepcopy(current_PHY)
        mappingOptions = {}
        # Try to map configurations
        for config in configurations:
            k = configurations.index(config)
            map_option = __mapSlice(phy, config)
            if map_option[3]["isSuccess"]:
                mappingOptions[k] = map_option
                profiler.add_stop(f"Slice {s}: Config {k} can be mapped: {map_option[3]}")
            else:
                profiler.add_stop(f"Slice {s}: Config {k} failed")
        if (len(mappingOptions) == 0):
            profiler.add_stop(f"Slice {s}: NO CONFIG. SKIP.")
            continue
        # print(mappingOptions)
        profiler.add_stop(f"Slice {s}: {len(mappingOptions)} mappable configs")
        mappingOptions_keys = list(mappingOptions.keys())
        mapping_option_values = [mappingOptions[k] for k in mappingOptions_keys]
        mapRanks = scipy.stats.rankdata([x[3]["nHops"] for x in mapping_option_values], method='min')
        mappingOptions_candidate = [mappingOptions_keys[i] for i in range(len(mappingOptions_keys)) if mapRanks[i] == 1]
        k = random.choice(mappingOptions_candidate)
        _phy, nodeMap, linkMap, info = mappingOptions[k]
        profiler.add_stop(f"Slice {s}: config {k} mapped")
        solution.update({f"pi_{s}":1})
        solution.update({f"phi_{s}_{k}":1})
        solution.update({f"xNode_{s}_{k}_{n[0]}_{n[1]}":1 for n in nodeMap})
        solution.update({f"xEdge_{s}_{k}_({l[0][0]},_{l[0][1]})_({l[1][0]},_{l[1][1]})":1 for l in linkMap})
        current_PHY = _phy
    return solution

def __mapSlice(_phy:nx.DiGraph, _sfc:nx.DiGraph) -> tuple[nx.DiGraph, list[tuple[int,int]], list[tuple[tuple[int,int],tuple[int,int]]], dict]: #(currentPhy, nodeMappings, linkMapping, info)
    phy = copy.deepcopy(_phy)
    first_vnode = [n for n in nx.topological_sort(_sfc)][0]
    
    used_node = []
    node_mappings = []
    link_mappings = []
    
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
    return phy, node_mappings, link_mappings, {"isSuccess":True, "nHops": len(links)}

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