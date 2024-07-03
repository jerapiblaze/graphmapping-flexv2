import os
import sys
import networkx as nx
import matplotlib.pyplot as plt

from PFPGraphMappingProblem import GraphMappingProblem, LoadProblem


def getData(sol: dict):
    keys = sol.keys()
    seen = {}
    nodeCount = 0
    linkCount = 0

    for key in keys:
        var = key.split('_')
        if var[-1] in seen:
            continue
        seen.update({var[-1]: 1})
        if var[0] == "xNode":
            nodeCount = nodeCount + 1
        if var[0] == "xEdge":
            linkCount = linkCount + 1
    ans = [nodeCount, linkCount]
    return ans


def getTotalReq(sol: dict, sfcSet) -> int:
    ansNode = 0
    ansEdge = 0
    keys = list(sol.keys())
    keysSplit = [k.split('_') for k in keys]
    nodesSet = [nx.get_node_attributes(sfc, 'req') for sfc in sfcSet]
    edgesSet = [nx.get_edge_attributes(sfc, 'req') for sfc in sfcSet]

    for key in keysSplit:
        sfcId = int(key[1])
        if key[0] == "xNode":
            sfcNode = int(key[2])
            ansNode = ansNode + nodesSet[sfcId][sfcNode]
        if key[0] == "xEdge":
            sfcEdge = key[2]
            sfcEdge = tuple(sfcEdge.removeprefix("(").removesuffix(")").split(","))
            sfcEdge = (int(sfcEdge[0]), int(sfcEdge[1]))
            ansEdge = ansEdge + edgesSet[sfcId][sfcEdge]

    return ansNode + ansEdge


def GetColumnData(solutionpath):
    solution = LoadProblem(solutionpath)
    prob_set_info = str(os.path.basename(os.path.dirname(solutionpath))).split("@")
    dataSol = getData(solution.solution)
    algoName = prob_set_info[1]
    # getTotalReq(solution.solution, solution.SFC_SET)
    nSfcs = len(solution.SFC_SET)
    nAcc = abs(solution.obj_value)
    if nAcc == 0:
        nNodes = 0
        nLinks = 0
        nLinksPerSfc = 0
    else:
        nNodes = dataSol[0]
        nLinks = dataSol[1]
        nLinksPerSfc = nLinks / nAcc
    time = solution.solution_time
    return {
        "algoName": algoName,
        "nSfcs": nSfcs,
        "nAcc": nAcc,
        "nNodes": nNodes,
        "nLinks": nLinks,
        "nLinksPerSfc": nLinksPerSfc,
        "time": time,
    }
