import networkx as nx
import matplotlib.pyplot as plt
import FlexSliceMappingProblem as FSMP
import Solvers
import Solvers.Greedy

from Solvers.Greedy.ultilities import physicalNodeConnect, nodeOrdersToLinks

phy_generator = FSMP.phy.kfat.FatTreeGraphGenerator(
    4, 
    host_nodecap=[10.0000001, 10.0000001, 10.0000001],
    edge_nodecap=[20.0000001, 20.0000001, 20.0000001],
    aggr_nodecap=[50.0000001, 50.0000001, 50.0000001],
    core_nodecap=[100.0000001, 100.0000001, 100.0000001],
    hostedge_linkcap=[5.0000001],
    edgeaggr_linkcap=[10.0000001],
    aggrcore_linkcap=[100.0000001]
)

PHY = phy_generator.Generate()

slice_generator = FSMP.slice.flex.FlexSliceGenerator()

# SLICES_SET = slice_generator.GenerateSet(100)

# problem = FSMP.SliceMappingProblem(
#     phy=PHY,
#     slices_set=SLICES_SET
# )

# greedyModel = Solvers.Greedy.Solver(
#     problem=problem,
#     logpath="./data/logs",
#     verbose=True,
#     timelimit=100
# )

# greedyModel.Solve()

# plt.show()

slice_config3 = slice_generator.Generate()[3]

first_node = [n for n in nx.topological_sort(slice_config3)][0]

# a = [n for n in nx.dfs_preorder_nodes(slice_config3, first_node)]
edge_order = [e for e in nx.edge_dfs(slice_config3, first_node)]

node_mappings = [] # (v,i)
link_mappings = []

def getNodeMapping(node_mappings:list[tuple[int,int]], vnode:int) -> int|None:
    for nm in node_mappings:
        if nm[0] == vnode:
            return nm[1]
    return None

def getEdgeMapping(edge_mappings:list[tuple[tuple[int,int],tuple[int,int]]], vlink:tuple[int,int]) -> tuple[int,int]|None:
    for em in edge_mappings:
        if em[0] == vlink:
            return em[1]
    return None

used_node = []
vnode_reqs = nx.get_node_attributes(slice_config3, "req")
vlink_reqs = nx.get_edge_attributes(slice_config3, "req")

for e in edge_order:
    v, w = e
    i = getNodeMapping(node_mappings, v)
    j = getNodeMapping(node_mappings, w)
    node_caps = nx.get_node_attributes(PHY, "cap")    
    link_caps = nx.get_edge_attributes(PHY, "cap")
    # Map v -> i
    if (i is None):
        node_list = sorted(node_caps, key=node_caps.get, reverse=True)
        n = 0
        while (node_list[n] in used_node) or (node_caps[n] < vnode_reqs[v]):
            n += 1
            if (n >= len(node_list)):
                n = -1
                break
        if n == -1:
            raise Exception("no node")
        i = node_list[n]
        used_node.append(i)
        node_caps[i] -= vnode_reqs[v]
        nx.set_node_attributes(PHY, node_caps, "cap")
        node_mappings.append((v,i))
    
    # Map w -> j
    if (j is None):
        node_list = sorted(node_caps, key=node_caps.get, reverse=True)
        n = 0
        while (node_list[n] in used_node) or (node_caps[n] < vnode_reqs[w]):
            n += 1
            if (n >= len(node_list)):
                n = -1
                break
        if n == -1:
            raise Exception("no node")
        j = node_list[n]
        used_node.append(j)
        node_caps[j] -= vnode_reqs[w]
        nx.set_node_attributes(PHY, node_caps, "cap")
        node_mappings.append((w,j))
    
    hops = physicalNodeConnect(PHY, i, j, vlink_reqs[e], "cap")
    if hops is None:
        raise Exception("No link")
    links = nodeOrdersToLinks(hops)
    for link in links:
        link_mappings.append((e, link))
        link_caps[link] -= vlink_reqs[e]
    nx.set_edge_attributes(PHY,  link_caps, "cap")


print(node_mappings)
print(link_mappings)

plt.figure()
nx.draw_networkx(PHY, PHY.NodeLocations)
plt.show()

# for e in nx.dfs_edges(slice_config3):
#     v, w = e
#     i = getNodeMapping(node_mappings, v)
#     j = getNodeMapping(node_mappings, w)
#     if (i is None and j is None):
#         raise Exception("SOMETHING WENT WRONG! ONE OF THE NODE MUST BE MAPPED EARLIER!")
    
#     pass