
from pulp import *

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



