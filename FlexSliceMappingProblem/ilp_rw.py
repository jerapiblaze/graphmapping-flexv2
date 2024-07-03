from .__internals__ import *
from .slice import GetAllPossibleVirtualEdge, GetVLinkReq_safe
import pulp
from .utilities import subsets
from .resources import NodeResource, LinkResource, ZERO_LINK_RESOURCE, ZERO_NODE_RESOURCE

VARIABLE_SURFIXES = ["xNode","xEdge","xSFC","t"]

def ConvertToIlp(prob:SliceMappingProblem) -> pulp.LpProblem:
    PHY = prob.PHY
    SFC_SET = prob.SLICES_SET
    name = prob.name
    problem = pulp.LpProblem(name=name, sense=pulp.LpMinimize)

    xNode, xEdge, xSFC, y, z, p, t = VarsInit(PHY, SFC_SET)
    M = 100
    GAMMA = 0.9999

    # Problem formulation
    problem = pulp.LpProblem(name=f"pfo-{uuid.uuid4().hex[:8]}")
    problem.constraints.clear()

    # C1
    for attr_i in range(len(ZERO_NODE_RESOURCE)):
        for i in PHY.nodes:
            problem += (
                pulp.lpSum(
                    pulp.lpSum(
                        xNode[SFC_SET.index(sfc)][v][i] * nx.get_node_attributes(sfc, "req")[v][attr_i] for v in sfc.nodes
                    ) for sfc in SFC_SET
                )
                <= nx.get_node_attributes(PHY, "cap")[i][attr_i],
                f"C1_{i}_@{attr_i}"
            )

    # C2
    for ij in PHY.edges:
        for attr_i in range(len(ZERO_LINK_RESOURCE)):
            problem += (
                pulp.lpSum(
                    pulp.lpSum(
                        z[SFC_SET.index(sfc)][vw][ij] * GetVLinkReq_safe(sfc, vw)[attr_i] for vw in GetAllPossibleVirtualEdge(sfc)
                    ) for sfc in SFC_SET
                )
                <= nx.get_edge_attributes(PHY, "cap")[ij][attr_i],
                f"C21_{ij}_@{attr_i}"
            )
        for sfc in SFC_SET:
            for vw in GetAllPossibleVirtualEdge(sfc):
                problem += (
                    z[SFC_SET.index(sfc)][vw][ij]
                    <= xEdge[SFC_SET.index(sfc)][vw][ij],
                    f"C22_{SFC_SET.index(sfc)}_{vw}_{ij}"
                )
                problem += (
                    z[SFC_SET.index(sfc)][vw][ij]
                    <= y[SFC_SET.index(sfc)][vw],
                    f"C23_{SFC_SET.index(sfc)}_{vw}_{ij}"
                )
                problem += (
                    xEdge[SFC_SET.index(sfc)][vw][ij] +
                    y[SFC_SET.index(sfc)][vw] - 1
                    <= z[SFC_SET.index(sfc)][vw][ij],
                    f"C24_{SFC_SET.index(sfc)}_{vw}_{ij}"
                )

    # C3
    for i in PHY.nodes:
        for sfc in SFC_SET:
            problem += (
                pulp.lpSum(
                    xNode[SFC_SET.index(sfc)][v][i] for v in sfc.nodes
                )
                <= xSFC[SFC_SET.index(sfc)],
                f"C3_{SFC_SET.index(sfc)}_{i}"
            )

    # C4
    for sfc in SFC_SET:
        for v in sfc.nodes:
            problem += (
                pulp.lpSum(
                    xNode[SFC_SET.index(sfc)][v][i] for i in PHY.nodes
                )
                == xSFC[SFC_SET.index(sfc)],
                f"C4_{SFC_SET.index(sfc)}_{v}"
            )
    # C5
    for i in PHY.nodes:
        for sfc in SFC_SET:
            for vw in GetAllPossibleVirtualEdge(sfc):
                problem += (
                    (
                        pulp.lpSum(
                            xEdge[SFC_SET.index(sfc)][vw].get((i, j)) for j in PHY.nodes
                        )
                        -
                        pulp.lpSum(
                            xEdge[SFC_SET.index(sfc)][vw].get((j, i)) for j in PHY.nodes
                        )
                        -
                        xNode[SFC_SET.index(sfc)][vw[0]][i] +
                        xNode[SFC_SET.index(sfc)][vw[1]][i]
                    )
                    >= -M*(1-y[SFC_SET.index(sfc)][vw]),
                    f"C51_{SFC_SET.index(sfc)}_{vw}_{i}"
                )
                problem += (
                    (
                        pulp.lpSum(
                            xEdge[SFC_SET.index(sfc)][vw].get((i, j)) for j in PHY.nodes
                        )
                        -
                        pulp.lpSum(
                            xEdge[SFC_SET.index(sfc)][vw].get((j, i)) for j in PHY.nodes
                        )
                        -
                        xNode[SFC_SET.index(sfc)][vw[0]][i] +
                        xNode[SFC_SET.index(sfc)][vw[1]][i]
                    )
                    <= M*(1-y[SFC_SET.index(sfc)][vw]),
                    f"C52_{SFC_SET.index(sfc)}_{vw}_{i}"
                )

    # C6
    for sfc in SFC_SET:
        problem += (
            pulp.lpSum(
                y[SFC_SET.index(sfc)][vw] for vw in GetAllPossibleVirtualEdge(sfc)
            )
            == xSFC[SFC_SET.index(sfc)]*(len(sfc.nodes) - 1),
            f"C61_{SFC_SET.index(sfc)}"
        )
        for v in sfc.nodes:
            problem += (
                pulp.lpSum(
                    y[SFC_SET.index(sfc)].get((v,w)) for w in sfc.nodes if not v==w
                )
                <= xSFC[SFC_SET.index(sfc)],
                f"C62_{SFC_SET.index(sfc)}_{v}"
            )
        for w in sfc.nodes:
            problem += (
                pulp.lpSum(
                    y[SFC_SET.index(sfc)].get((v, w)) for v in sfc.nodes if not v == w
                )
                <= xSFC[SFC_SET.index(sfc)],
                f"C63_{SFC_SET.index(sfc)}_{w}"
            )
        for set in subsets(list(sfc.nodes)):
            if (len(set) <= 1):
                continue
            problem += (
                pulp.lpSum(y[SFC_SET.index(sfc)].get((v, w)) for w in set for v in set if not v == w)
                <= xSFC[SFC_SET.index(sfc)]*(len(set)-1),
                f"C64_{SFC_SET.index(sfc)}_{'.'.join([str(s) for s in set])}"
            )

    # C7
    # for sfc in SFC_SET:
    #     for vw in GetAllPossibleVirtualEdge(sfc):
    #         problem += (
    #             pulp.lpSum(xEdge[SFC_SET.index(sfc)][vw][ij] for ij in PHY.edges)
    #             == y[SFC_SET.index(sfc)][vw],
    #             f"C7_{SFC_SET.index(sfc)}_{vw}"
    #         )
    # C8
    for sfc in SFC_SET:
        for v in sfc.nodes:
            problem += (
                p[SFC_SET.index(sfc)][v]
                == pulp.lpSum(pp*t[SFC_SET.index(sfc)][v][pp] for pp in range(len(list(sfc.nodes)))),
                f"C8_{SFC_SET.index(sfc)}_{v}"
            )
    # C9
    for sfc in SFC_SET:
        for vw in GetAllPossibleVirtualEdge(sfc):
            problem += (
                p[SFC_SET.index(sfc)][vw[1]] - p[SFC_SET.index(sfc)][vw[0]]
                <= 1 + M*(1-y[SFC_SET.index(sfc)][vw]),
                f"C91_{SFC_SET.index(sfc)}_{vw}"
            )
            problem += (
                p[SFC_SET.index(sfc)][vw[1]] - p[SFC_SET.index(sfc)][vw[0]]
                >= 1 - M*(1-y[SFC_SET.index(sfc)][vw]),
                f"C92_{SFC_SET.index(sfc)}_{vw}"
            )
    # C10
    for sfc in SFC_SET:
        for pp in range(len(list(sfc.nodes))):
            problem += (
                pulp.lpSum(t[SFC_SET.index(sfc)][v][pp] for v in sfc.nodes)
                == xSFC[SFC_SET.index(sfc)],
                f"C101_{SFC_SET.index(sfc)}_{pp}"
            )
        for v in sfc.nodes:
            problem += (
                pulp.lpSum(t[SFC_SET.index(sfc)][v][pp] for pp in range(len(list(sfc.nodes))))
                == xSFC[SFC_SET.index(sfc)],
                f"C102_{SFC_SET.index(sfc)}_{v}"
            )
    # C11
    for sfc in SFC_SET:
        for vp in sfc.FixedPositions:
            problem += (
                t[SFC_SET.index(sfc)][vp[0]][vp[1]]
                == xSFC[SFC_SET.index(sfc)],
                f"C11_{SFC_SET.index(sfc)}_{vp[0]}_{vp[1]}"
            )
            
    # C12 -- bs fixing
    if (str(PHY.name).__contains__("fattree")):
        for sfc in SFC_SET:
            if (not str(sfc.name).__contains__("bs")):
                continue
            k = SFC_SET.index(sfc)
            bs_nodes = [n for n in list(PHY.nodes) if nx.get_node_attributes(PHY, "kind")[n] == "host"]
            bs_vnodes = [n for n in list(sfc.nodes) if nx.get_node_attributes(sfc, "label")[n] == "BS"]
            for i in list(PHY.nodes):
                if i in bs_nodes:
                    continue
                for v in bs_vnodes:
                    problem += (
                        xNode[k][v][i] == 0,
                        f"C12_{k}_{v}_{i}"
                    )
            # problem += (
            #     pulp.lpSum(
            #         xNode[k][v][i]
            #         for v in sfc.nodes if v in bs_vnodes
            #         for i in PHY.nodes if not i in bs_nodes
            #     ) == 0,
            #     f"C12_{k}"
            # )
            
    # Objective function
    problem += (
        - pulp.lpSum(
            xSFC[SFC_SET.index(sfc)] for sfc in SFC_SET
        ) * GAMMA
        + pulp.lpSum(
            pulp.lpSum(
                pulp.lpSum(
                    xEdge[SFC_SET.index(sfc)][vlink][link]
                    for link in PHY.edges
                )
                for vlink in GetAllPossibleVirtualEdge(sfc)
            )
            for sfc in SFC_SET
        )
        * (1 - GAMMA)
    )

    return problem

def VarsInit(PHY, SFC_SET):
    # Variable stores building

    xNode = list()
    for sfc in SFC_SET:
        xNode.append(
            pulp.LpVariable.dicts(
                name=f"xNode_{SFC_SET.index(sfc)}",
                indices=(sfc.nodes, PHY.nodes),
                cat=pulp.LpBinary
            )
        )

    xEdge = list()
    for sfc in SFC_SET:
        all_possible_virtual_edges = GetAllPossibleVirtualEdge(sfc)
        xEdge.append(
            pulp.LpVariable.dicts(
                name=f"xEdge_{SFC_SET.index(sfc)}",
                indices=(all_possible_virtual_edges, PHY.edges),
                cat=pulp.LpBinary
            )
        )

    xSFC = pulp.LpVariable.dicts(
        name=f"xSFC",
        indices=(range(len(SFC_SET))),
        cat=pulp.LpBinary
    )

    y = list()
    for sfc in SFC_SET:
        all_possible_virtual_edges = GetAllPossibleVirtualEdge(sfc)
        y.append(
            pulp.LpVariable.dicts(
                name=f"y_{SFC_SET.index(sfc)}",
                indices=all_possible_virtual_edges,
                cat=pulp.LpBinary
            )
        )

    z = list()
    for sfc in SFC_SET:
        all_possible_virtual_edges = GetAllPossibleVirtualEdge(sfc)
        z.append(
            pulp.LpVariable.dicts(
                name=f"z_{SFC_SET.index(sfc)}",
                indices=(all_possible_virtual_edges, PHY.edges),
                cat=pulp.LpBinary
            )
        )

    p = list()
    for sfc in SFC_SET:
        p.append(
            pulp.LpVariable.dicts(
                name=f"p_{SFC_SET.index(sfc)}",
                indices=sfc.nodes,
                cat=pulp.LpInteger,
                lowBound=0,
                upBound=len(list(sfc.nodes))-1
            )
        )

    t = list()
    for sfc in SFC_SET:
        t.append(
            pulp.LpVariable.dicts(
                name=f"t_{SFC_SET.index(sfc)}",
                indices=(sfc.nodes, range(len(list(sfc.nodes)))),
                cat=pulp.LpBinary
            )
        )
        pass

    return xNode, xEdge, xSFC, y, z, p, t