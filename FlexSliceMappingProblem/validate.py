from .__internals__ import *
from .slice import GetAllPossibleVirtualEdge, GetVLinkReq_safe
from .resources import NodeResource, LinkResource, ZERO_LINK_RESOURCE, ZERO_NODE_RESOURCE
from .ilp import VarInit, M, GAMMA

import pulp
import networkx as nx
import copy

from typing import Any

class SolutionData:
    def __init__(self, sol_dict:dict):
        self.data = sol_dict
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        name = str(args[0])
        if name.startswith("z"):
            return self.__get_z(name)
        value = round(self.data.get(name, 0))
        return value
    def __get_z(self, name):
        nameparts = name.split("_")
        s = int(nameparts[1])
        k = int(nameparts[2])
        phi = round(self.data.get(f"phi_{s}_{k}", 0))
        pi = round(self.data.get(f"pi_{s}", 0))
        return phi*pi
    
def ValidateSolution(prob: SliceMappingProblem, debug:bool=False, ndigits:int=5) -> SliceMappingProblem:
    PHY = prob.PHY
    SLICES_SET = prob.SLICES_SET
    solution = prob.solution
    result = validatesolution(PHY, SLICES_SET, solution, ndigits)
    prob.solution_status = result
    return prob

def validatesolution(PHY:nx.DiGraph, SLICES_SET:list[list[nx.DiGraph]], solution:dict[str,float], ndigits:int) -> str|int:
    if (not len(solution)):
        return 0
    sol = SolutionData(solution)
    xNode, xEdge, phi, pi, z = VarInit(PHY, SLICES_SET)
    # C1: Node Capacity
    for attr_i in range(len(ZERO_NODE_RESOURCE)):
        for i in PHY.nodes:
            if not (
                sum(
                    sol(xNode[s][k][v][i]) * SLICES_SET[s][k].nodes[v]["req"][attr_i]
                    for s in range(len(SLICES_SET))
                    for k in range(len(SLICES_SET[s])) 
                    for v in SLICES_SET[s][k].nodes
                ) 
                <= PHY.nodes[i]["cap"][attr_i]
            ):
                return f"C1_{i}_@{attr_i}"
    # C2: Link Capacity
    for attr_i in range(len(ZERO_LINK_RESOURCE)):
        for (i,j) in PHY.edges:
            if not (
                sum(
                    sol(xEdge[s][k][(v,w)][(i,j)]) * SLICES_SET[s][k].edges[(v,w)]["req"][attr_i]
                    for s in range(len(SLICES_SET))
                    for k in range(len(SLICES_SET[s]))
                    for (v,w) in SLICES_SET[s][k].edges
                ) <= PHY.edges[(i,j)]["cap"][attr_i]
            ):
                return f"C2_{(i,j)}_@{attr_i}"
    # C3: Map One
    for s in range(len(SLICES_SET)):
        for k in range(len(SLICES_SET[s])):
            for i in PHY.nodes:
                if not (
                    sum(
                        sol(xNode[s][k][v][i])  
                        for v in SLICES_SET[s][k].nodes
                    ) 
                    <= sol(z[s][k])
                ):
                    return f"C3_{s}_{k}_{i}"
    # C4: Map All
    for s in range(len(SLICES_SET)):
        for k in range(len(SLICES_SET[s])):
            for v in SLICES_SET[s][k].nodes:
                if not (
                    sum(
                        sol(xNode[s][k][v][i]) 
                        for i in PHY.nodes
                    ) 
                    == sol(z[s][k])
                ):
                    return f"C4_{s}_{k}_{v}"
    # C5: Flow Conservation
    for s in range(len(SLICES_SET)):
        for k in range(len(SLICES_SET[s])):
            for i in PHY.nodes:
                for (v,w) in SLICES_SET[s][k].edges:
                    if not (
                        sum(
                            sol(xEdge[s][k][(v,w)][(i,j)])-sol(xEdge[s][k][(v,w)][(j,i)])
                            for j in PHY.nodes if (i,j) in PHY.edges
                        ) 
                        - (sol(xNode[s][k][v][i]) - sol(xNode[s][k][w][i])) 
                        <= M*(1-sol(phi[s][k]))
                    ):
                        return f"C5_1_{s}_{k}_{i}_{(v,w)}"
                    if not (
                        sum(
                            sol(xEdge[s][k][(v,w)][(i,j)])-sol(xEdge[s][k][(v,w)][(j,i)])
                            for j in PHY.nodes if (i,j) in PHY.edges
                        ) 
                        - (sol(xNode[s][k][v][i]) - sol(xNode[s][k][w][i])) 
                        >= -M*(1-sol(phi[s][k]))
                    ):
                        return f"C5_2_{s}_{k}_{i}_{(v,w)}"
    # C6: One config
    for s in range(len(SLICES_SET)):
        if not (
            sum(
                sol(phi[s][k]) 
                for k in range(len(SLICES_SET[s])) 
            ) 
            == sol(pi[s])
        ):
            return f"C6_{s}" 
    # C7: Linearization
    for s in range(len(SLICES_SET)):
        for k in range(len(SLICES_SET[s])):
            if not (
                sol(z[s][k]) <= sol(pi[s])
            ):
                return f"C7_1_{s}_{k}"
            if not (
                sol(z[s][k]) <= sol(phi[s][k])
            ):
                return f"C7_2_{s}_{k}"
            if not (
                sol(z[s][k]) >= sol(pi[s]) + sol(phi[s][k]) - 1
            ):
                return f"C7_3_{s}_{k}"
    # ALL PASSED
    return 1