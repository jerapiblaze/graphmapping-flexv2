from .__internals__ import *

import sys
import os

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from resources import NodeResource, LinkResource, ZERO_LINK_RESOURCE, ZERO_NODE_RESOURCE

class FromGmlGraphGenerator(PhysicalGraphGenerator):
    def __init__(self, gml_path:str, nodecap:tuple[float, float, float], linkcap:tuple[float], nodecap_min:tuple[float,float,float]=None, linkcap_min:tuple[float]=None) -> None:
        self.__graph__ = nx.DiGraph(nx.read_gml(gml_path))
        self.nodecap = NodeResource(*nodecap)
        self.linkcap = LinkResource(*linkcap)
        self.basename = os.path.basename(gml_path)
        self.nodecap_min = NodeResource(*nodecap_min) if nodecap_min is not None else ZERO_NODE_RESOURCE
        self.linkcap_min = LinkResource(*linkcap_min) if linkcap_min is not None else ZERO_LINK_RESOURCE

    def Generate(self) -> nx.DiGraph:
        nodes = list(self.__graph__.nodes)
        links = [(nodes.index(e[0]), nodes.index(e[1])) for e in list(self.__graph__.edges)]
        PHY_nodes = [(nodes.index(node),{"cap":self.nodecap if self.nodecap_min == ZERO_NODE_RESOURCE else NodeResource.random_uniform((self.nodecap_min.cpu, self.nodecap.cpu), (self.nodecap_min.memory, self.nodecap.memory), (self.nodecap_min.storage, self.nodecap.storage)), "kind":"host"}) for node in nodes]
        PHY_links = [(link[0], link[1],{"cap":self.linkcap if self.linkcap_min == ZERO_LINK_RESOURCE else LinkResource.random_uniform((self.linkcap_min.bandwidth, self.linkcap.bandwidth))}) for link in links]
        PHY = nx.DiGraph(name=f"{self.basename}_{len(PHY_nodes)}nodes_{len(PHY_links)}_{uuid.uuid4().hex[:8]}")
        PHY.add_nodes_from(PHY_nodes)
        PHY.add_edges_from(PHY_links)
        x_loc = nx.get_node_attributes(self.__graph__, "x")
        y_loc = nx.get_node_attributes(self.__graph__, "y")
        loc = {nodes.index(n):(x_loc[n],y_loc[n]) for n in nodes}
        PHY.NodeLocations = loc
        return PHY