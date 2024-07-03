import os
import sys
import networkx as nx
import matplotlib.pyplot as plt

from PFPGraphMappingProblem import GraphMappingProblem, LoadProblem

def SegmentSet(sfc: nx.DiGraph):
    subseg_nodes_set = nx.weakly_connected_components(sfc)
    subseg = []
    for subseg_nodes in subseg_nodes_set:
        subseg.append(nx.subgraph(sfc, subseg_nodes))
    return subseg

def getVar(sol: dict):
    vars = []
    i = 0
    tmp = []
    for key, value in sol.items():
        var = key.split('_')
        if var[1] == str(i):
            tmp.append(key)
        else:
            vars.append(tmp)
            i = i + 1
            tmp = []
            tmp.append(key)
    if not len(tmp) == 0:
        vars.append(tmp)
    return vars

def draw(varList, outputPath):
    for vars in varList:
        plt.figure()
        g = nx.DiGraph()
        id = 0
        for var in vars:
            element = var.split('_')
            id = element[1]
            if element[0] == 'xNode':
                i_node = "i_" + element[3]
                v_node = "v_" + element[2]
                if g.has_edge(v_node, i_node):
                    continue
                g.add_edge(v_node, i_node)
            if element[0] == 'y':
                tmp = tuple(element[-1].removeprefix("(").removesuffix(")").split(","))
                v_node_1 = "v_" + tmp[0]
                v_node_2 = "v_" + tmp[1]
                if g.has_edge(v_node_1, v_node_2):
                    continue
                g.add_edge(v_node_1, v_node_2)
            if element[0] == 'xEdge':
                tmp = tuple(element[-1].removeprefix("(").removesuffix(")").split(","))
                i_node_1 = "i_" + tmp[0]
                i_node_2 = "i_" + tmp[1]
                if g.has_edge(i_node_1, i_node_2):
                    continue
                g.add_edge(i_node_1, i_node_2)
        node_size = 800
        node_colors = []
        for node in g.nodes():
            if node.startswith("i"):
                node_colors.append("gray")
            else:
                node_colors.append("blue")
        pos = nx.spring_layout(g)
        nx.draw_kamada_kawai(g, node_color = node_colors, with_labels=True, font_weight='bold', node_size = node_size)
        plt.savefig(f"{outputPath}/result_sfc_{id}.png")

def outPhy(phy: nx.DiGraph, outputPath: str):
    plt.figure()
    nx.draw_kamada_kawai(phy, with_labels=True, font_weight='bold', node_size = 800)
    plt.savefig(f"{outputPath}/phy.png")
    return

def outSfcs(sfc_set: list[nx.DiGraph], outputPath: str):
    id = 1
    for sfc in sfc_set:
        plt.figure()
        segments = SegmentSet(sfc)
        for seg in segments:
            nx.draw(seg, with_labels=True, font_weight='bold', node_size = 800)
        plt.savefig(f"{outputPath}/sfc_{id}.png")
        id = id + 1
    return

def outSolution(sol: dict, outputPath: str):
    varsList = getVar(sol)
    draw(varsList, outputPath)
    return

def Out(path: str, outputPathPhy: str, outputPathSfcs: str, outputPathSol: str):
    problemStatus = LoadProblem(path)
    phy = problemStatus.PHY
    sfc_set = problemStatus.SFC_SET
    sol = problemStatus.solution
    outPhy(phy, outputPathPhy)
    outSfcs(sfc_set, outputPathSfcs)
    outSolution(sol, outputPathSol)
    return