import pulp as pl
import networkx as nx
from pulp import *

from FlexSliceMappingProblem.resources import NodeResource, LinkResource, ZERO_LINK_RESOURCE, ZERO_NODE_RESOURCE

def extract_mapping_result(lp_problem, K, PHY, xEdge ):
    node_mapping = {}
    edge_mapping = {}
    reward = value(lp_problem.objective)

    # Extract node mappings
    for s in range(len(K)):
        for k in range(len(K[s])):
            for v in K[s][k].nodes:
                for i in PHY.nodes:
                    var_name = f"xNode_{s}_{k}_{v}_{i}"

                    var = lp_problem.variablesDict().get(var_name)
                    if var and var.varValue == 1:
                        if (s, k) not in node_mapping:
                            node_mapping[(s, k)] = {}
                        node_mapping[(s, k)][v] = i
                        break

    for s in range(len(K)):
        # edge_mapping[s] = {}
        for k in range(len(K[s])):
            for phy_link in PHY.edges:
                for vlink in K[s][k].edges:
                    a = xEdge[s][k][vlink][phy_link].name
                    var = lp_problem.variablesDict().get(a)
                    if var and var.varValue == 1:
                        if (s, k) not in edge_mapping:
                            edge_mapping[(s, k)] = {}
                        edge_mapping[(s, k)][vlink] = phy_link
                        break
    return reward ,{'node_mapping': node_mapping, 'link_mapping': edge_mapping}

VARIABLE_SURFIXES = ["xNode","xEdge","pi","phi"]
M = 100
GAMMA = 0.9999

def ConvertToILP(PHY, K) -> pulp.LpProblem:
    PHY = PHY
    SLICES_SET = K
    name = "SE_Fixed problem"
    problem = pulp.LpProblem(name=name, sense=pulp.LpMinimize)
    problem.constraints.clear()    
    xNode, xEdge, phi, pi, z = VarInit(PHY, SLICES_SET)
    # C1: Node Capacity
    for attr_i in range(len(ZERO_NODE_RESOURCE)):
        for i in PHY.nodes:
            problem += (
                pulp.lpSum(
                    xNode[s][k][v][i] * SLICES_SET[s][k].nodes[v]["req"][attr_i]
                    for s in range(len(SLICES_SET))
                    for k in range(len(SLICES_SET[s])) 
                    for v in SLICES_SET[s][k].nodes
                ) 
                <= PHY.nodes[i]["cap"][attr_i], 
                f"C1_{i}_@{attr_i}"
            )
    # C2: Link Capacity
    for attr_i in range(len(ZERO_LINK_RESOURCE)):
        for (i,j) in PHY.edges:
            problem += (
                pulp.lpSum(
                    xEdge[s][k][(v,w)][(i,j)] * SLICES_SET[s][k].edges[(v,w)]["req"][attr_i]
                    for s in range(len(SLICES_SET))
                    for k in range(len(SLICES_SET[s]))
                    for (v,w) in SLICES_SET[s][k].edges
                ) <= PHY.edges[(i,j)]["cap"][attr_i], 
                f"C2_{(i,j)}_@{attr_i}"
            )
    # C3: Map Once
    for s in range(len(SLICES_SET)):
        for k in range(len(SLICES_SET[s])):
            for i in PHY.nodes:
                problem += (
                    pulp.lpSum(
                        xNode[s][k][v][i]  
                        for v in SLICES_SET[s][k].nodes
                    ) 
                    <= z[s][k], 
                    f"C3_{s}_{k}_{i}"
                )
    # C4: Map All
    for s in range(len(SLICES_SET)):
        for k in range(len(SLICES_SET[s])):
            for v in SLICES_SET[s][k].nodes:
                problem += (
                    pulp.lpSum(
                        xNode[s][k][v][i] 
                        for i in PHY.nodes
                    ) 
                    == z[s][k], 
                    f"C4_{s}_{k}_{v}"
                )
    # C5: Flow Conservation
    for s in range(len(SLICES_SET)):
        for k in range(len(SLICES_SET[s])):
            for i in PHY.nodes:
                for (v,w) in SLICES_SET[s][k].edges:
                    problem += (
                        pulp.lpSum(
                            (xEdge[s][k][(v,w)][(i,j)]-xEdge[s][k][(v,w)][(j,i)])
                            for j in PHY.nodes if (i,j) in PHY.edges
                        )  
                        - (xNode[s][k][v][i] - xNode[s][k][w][i])
                        <= M*(1-phi[s][k]), 
                        f"C5_1_{s}_{k}_{i}_{(v,w)}"
                    ) 
                    problem += (
                        pulp.lpSum(
                            (xEdge[s][k][(v,w)][(i,j)]-xEdge[s][k][(v,w)][(j,i)])
                            for j in PHY.nodes if (i,j) in PHY.edges
                        )  
                        - (xNode[s][k][v][i] - xNode[s][k][w][i])
                        >= -M*(1-phi[s][k]), 
                        f"C5_2_{s}_{k}_{i}_{(v,w)}"
                    )
    # C6: One config
    for s in range(len(SLICES_SET)):
        problem += (
            pulp.lpSum(
                phi[s][k] 
                for k in range(len(SLICES_SET[s])) 
            ) 
            == pi[s],
            f"C6_{s}"  
        )
    # C7: Linearization
    for s in range(len(SLICES_SET)):
        for k in range(len(SLICES_SET[s])):
            problem += (
                z[s][k] <= pi[s], 
                f"C7_1_{s}_{k}"
            )
            problem += (
                z[s][k] <= phi[s][k], 
                f"C7_2_{s}_{k}"
            )
            problem += (
                z[s][k] >= pi[s] + phi[s][k] - 1, 
                f"C7_3_{s}_{k}"
            )
    # OBJECTIVE
    problem += (
        - GAMMA*pulp.lpSum(
            pi[s] for s in range(len(SLICES_SET))
        ) 
        + (1-GAMMA)*pulp.lpSum(
            xEdge[s][k][(v,w)][(i,j)] 
            for s in range(len(SLICES_SET)) 
            for k in range(len(SLICES_SET[s]))
            for (i,j) in PHY.edges
            for (v,w) in SLICES_SET[s][k].edges
        )
    )
    return problem, xNode, xEdge, phi, pi, z

def VarInit(PHY:nx.DiGraph, SLICES_SET:list[list[nx.DiGraph]]) -> tuple[dict, dict, dict, dict, dict]:
    # x_{i}^{v,k,s}
    xNode=dict()
    for s in range(len(SLICES_SET)):
        node_s = dict()
        for k in range(len(SLICES_SET[s])):
            xNode_k = pulp.LpVariable.dicts(
                name=f"xNode_{s}_{k}",
                indices = (SLICES_SET[s][k].nodes, PHY.nodes),
                cat=pulp.LpBinary
            )
            node_s[k] = xNode_k
        xNode[s] = node_s
    # x_{ij}^{vw,k,s}
    xEdge=dict()
    # tao bien xEdge
    for s in range(len(SLICES_SET)):
        edge_s = dict()
        for k in range(len(SLICES_SET[s])):
            xEdge_k = pulp.LpVariable.dicts(
                name=f"xEdge_{s}_{k}",
                indices=(SLICES_SET[s][k].edges, PHY.edges),
                cat=pulp.LpBinary
            )
            edge_s[k] = xEdge_k
        xEdge[s] = edge_s
    # \phi_{s}^{k}
    phi = dict()
    for s in range(len(SLICES_SET)):
        phi_s = pulp.LpVariable.dicts(
            name=f"phi_{s}",
            indices = [
                k 
                for k in range(len(SLICES_SET[s]))
            ],
            cat=pulp.LpBinary
        )
        phi[s] = phi_s
    # \pi_{s}
    pi = pulp.LpVariable.dicts(
        name="pi",
        indices = [
            s 
            for s in range(len(SLICES_SET))
        ],
        cat=pulp.LpBinary
    )
    # z_{s}^{k}
    z = dict()
    for s in range(len(SLICES_SET)):
        z_s = pulp.LpVariable.dicts(
            name=f"z_{s}",
            indices = [
                k 
                for k in range(len(SLICES_SET[s]))
            ],
            cat=pulp.LpBinary
        )
        z[s] = z_s
    return xNode, xEdge, phi, pi, z


