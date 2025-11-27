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
            map_option = mapSlice(phy, config)
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
