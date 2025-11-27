import networkx as nx
import random
import scipy
import copy
import time

from Solvers.Greedy.ultilities import *
from utilities.profiler import StopWatch

def GreedyRS(PHY:nx.DiGraph, SLICE_SET:list[nx.DiGraph], profiler:StopWatch, timelimit:int=0) -> dict[str, int]:
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
        # random-choice config selection
        k = random.choice(range(len(configurations)))
        config = configurations[k]
        _phy, nodeMap, linkMap, info = mapSlice(phy, config)
        if not info['isSuccess']:
            profiler.add_stop(f"Slice {s}: NO CONFIG. SKIP.")
            continue
        profiler.add_stop(f"Slice {s}: config {k} mapped")
        solution.update({f"pi_{s}":1})
        solution.update({f"phi_{s}_{k}":1})
        solution.update({f"xNode_{s}_{k}_{n[0]}_{n[1]}":1 for n in nodeMap})
        solution.update({f"xEdge_{s}_{k}_({l[0][0]},_{l[0][1]})_({l[1][0]},_{l[1][1]})":1 for l in linkMap})
        current_PHY = _phy
    return solution