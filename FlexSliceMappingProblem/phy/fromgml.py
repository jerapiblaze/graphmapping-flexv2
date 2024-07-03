from .__internals__ import *

import sys
import os

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from resources import NodeResource, LinkResource, ZERO_LINK_RESOURCE, ZERO_NODE_RESOURCE

class FromGmlGraphGenerator(PhysicalGraphGenerator):
    def __init__(self, gml_path:str, nodecap:tuple[float, float, float], linkcap:tuple[float]) -> None:
        self.__graph__ = nx.DiGraph(nx.read_gml(gml_path))
        self.nodecap = NodeResource(*nodecap)
        self.linkcap = LinkResource(*linkcap)
        self.basename = os.path.basename(gml_path)

    def Generate(self) -> nx.DiGraph:
        nodes = list(self.__graph__.nodes)
        links = [(nodes.index(e[0]), nodes.index(e[1])) for e in list(self.__graph__.edges)]
        PHY_nodes = [(nodes.index(node),{"cap":self.nodecap, "kind":"host"}) for node in nodes]
        PHY_links = [(link[0], link[1],{"cap":self.linkcap}) for link in links]
        PHY = nx.DiGraph(name=f"{self.basename}_{len(PHY_nodes)}nodes_{len(PHY_links)}_{uuid.uuid4().hex[:8]}")
        PHY.add_nodes_from(PHY_nodes)
        PHY.add_edges_from(PHY_links)
        x_loc = nx.get_node_attributes(self.__graph__, "x")
        y_loc = nx.get_node_attributes(self.__graph__, "y")
        loc = {nodes.index(n):(x_loc[n],y_loc[n]) for n in nodes}
        PHY.NodeLocations = loc
        return PHY