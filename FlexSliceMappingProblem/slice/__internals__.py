import os
import sys
import networkx as nx
import random as rd

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from resources import NodeResource, LinkResource, ZERO_LINK_RESOURCE, ZERO_NODE_RESOURCE

class SliceGenerator:
    def __init__(self,)->None:
        pass
    def Generate(self,)->list[nx.DiGraph]:
        pass
    def GenerateSet(self, n:int)->list[list[nx.DiGraph]]:
        pass
    def Seed(x=None)->None:
        rd.seed(x)


def GetAllPossibleVirtualEdge(sfc, name="req"):
    temp_graph = nx.DiGraph()
    temp_graph.add_nodes_from(sfc.nodes)
    link_store = nx.get_edge_attributes(sfc, name)

    for v in temp_graph.nodes:
        for w in temp_graph.nodes:
            if (v == w):
                continue
            link_req = GetVLinkReq_safe(sfc, (v, w))
            temp_graph.add_edge(v, w, weight=link_req)

    return temp_graph.edges


def GetVLinkReq_safe(sfc, vw, name="req"):
    link_store = sfc.LinkRequirement
    link = link_store.get(vw, ZERO_LINK_RESOURCE)
    return link
