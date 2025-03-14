import uuid

import networkx as nx

from .__internals__ import *

class FlexSliceGenerator(SliceGenerator):
    def __init__(self, mode:str, nodescale:float, linkscale:float):
        self.mode = mode
        pass
    
    def Generate(self) -> list[nx.DiGraph]:
        name = f"flexslice_{uuid.uuid4().hex[:8]}"
        slice_configs = []
        if self.mode.__contains__("_1_"):
                slice_configs.append(GenerateConfig_1(name))
        if self.mode.__contains__("_2_"):
                slice_configs.append(GenerateConfig_2(name))
        if self.mode.__contains__("_3_"):
                slice_configs.append(GenerateConfig_3(name))
        if self.mode.__contains__("_4_"):
                slice_configs.append(GenerateConfig_4(name))
        return slice_configs
    
    def GenerateSet(self, n:int) -> list[list[nx.DiGraph]]:
        slice_set = []
        for i in range(n):
            slice_set.append(
                self.Generate()
            )
        return slice_set
    
    
def GenerateConfig_1(prefix:str) -> nx.DiGraph:
    NODES = [
        (
            0, {
                "label":"VPN",
                "name":"VirtualPersonalNetwork",
                "req": NodeResource(10, 0, 0)
            }
        ),
        (
            1, {
                "label":"MN",
                "name":"Monitoring",
                "req": NodeResource(10, 0, 0)
            }
        ),
        (
            2, {
                "label":"FW",
                "name":"Firewall",
                "req": NodeResource(10, 0, 0)
            }
        ),
        (
            3, {
                "label":"LB",
                "name":"LoadBalancer",
                "req": NodeResource(20, 0, 0)
            }
        )
    ]
    LINKS = [
        (
            0, 1, {
                "req": LinkResource(10)
            }
        ),
        (
            1, 2 , {
                "req": LinkResource(10)
            }
        ),
        (
            2, 3 , {
                "req": LinkResource(10)
            }
        )
    ]
    graph = nx.DiGraph(name=f"{prefix}_type1_{uuid.uuid4().hex[:8]}")
    graph.add_nodes_from(NODES)
    graph.add_edges_from(LINKS)
    return graph

def GenerateConfig_2(prefix:str) -> nx.DiGraph:
    NODES = [
        (
            0, {
                "label":"IN",
                "req": NodeResource(10, 0, 0)
            }
        ),
        (
            1, {
                "label":"MID1",
                "req": NodeResource(25, 0, 0)
            }
        ),
        (
            2, {
                "label":"MID2",
                "req": NodeResource(5, 0, 0)
            }
        ),
        (
            3, {
                "label":"OUT",
                "req": NodeResource(10, 0, 0)
            }
        )
    ]
    LINKS = [
        (
            0, 1, 
            {
                "req": LinkResource(10)
            }
        ),
        (
            1, 2, 
            {
                "req": LinkResource(15)
            }
        ),
        (
            1, 3, 
            {
                "req": LinkResource(5)
            }
        )
    ]
    graph = nx.DiGraph(name=f"{prefix}_type2_{uuid.uuid4().hex[:8]}")
    graph.add_nodes_from(NODES)
    graph.add_edges_from(LINKS)
    return graph

def GenerateConfig_3(prefix:str) -> nx.DiGraph:
    NODES = [
        (
            0, {
                "label":"VPN",
                "name":"VirtualPersonalNetwork",
                "req": NodeResource(10, 0, 0)
            }
        ),
        (
            1, {
                "label":"MN",
                "name":"Monitoring",
                "req": NodeResource(10, 0, 0)
            }
        ),
        (
            2, {
                "label":"FW",
                "name":"Firewall",
                "req": NodeResource(10, 0, 0)
            }
        ),
        (
            3, {
                "label":"LB",
                "name":"LoadBalancer",
                "req": NodeResource(20, 0, 0)
            }
        )
    ]
    LINKS = [
        (
            0, 1, {
                "req": LinkResource(5)
            }
        ),
        (
            0, 2 , {
                "req": LinkResource(5)
            }
        ),
        (
            1, 3 , {
                "req": LinkResource(10)
            }
        ),
        (
            2, 3 , {
                "req": LinkResource(10)
            }
        )
    ]
    graph = nx.DiGraph(name=f"{prefix}_type3_{uuid.uuid4().hex[:8]}")
    graph.add_nodes_from(NODES)
    graph.add_edges_from(LINKS)
    return graph

def GenerateConfig_4(prefix:str) -> nx.DiGraph:
    NODES = [
        (
            0, {
                "label":"IN",
                "req": NodeResource(10, 0, 0)
            }
        ),
        (
            1, {
                "label":"MID0",
                "req": NodeResource(10, 0, 0)
            }
        ),
        (
            2, {
                "label":"MID1",
                "req": NodeResource(5, 0, 0)
            }
        ),
        (
            3, {
                "label":"MID2",
                "req": NodeResource(5, 0, 0)
            }
        ),
        (
            4, {
                "label":"OUT",
                "req": NodeResource(5, 0, 0)
            }
        )
    ]
    LINKS = [
        (
            0, 1, {
                "req": LinkResource(10)
            }
        ),
        (
            1, 2, {
                "req": LinkResource(5)
            }
        ),
        (
            1, 3, {
                "req": LinkResource(5)
            }
        ),
        (
            3, 4, {
                "req": LinkResource(5)
            }
        ),
        (
            2, 4, {
                "req": LinkResource(5)
            }
        ),
        (
            1, 4, {
                "req": LinkResource(5)
            }
        )
    ]
    graph = nx.DiGraph(name=f"{prefix}_type4_{uuid.uuid4().hex[:8]}")
    graph.add_nodes_from(NODES)
    graph.add_edges_from(LINKS)
    return graph