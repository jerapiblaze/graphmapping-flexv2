from .__internals__ import *

import sys
import os

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from resources import NodeResource, LinkResource, ZERO_LINK_RESOURCE, ZERO_NODE_RESOURCE

class RandomGraphGenerator(PhysicalGraphGenerator):
    def __init__(self, nodecount:int|tuple[int, int], linkdisconnectrate:float=0) -> None:
        self.nodecap = NodeResource(100,0,100)
        self.linkcap = LinkResource(100)
        self.nodecount = nodecount
        self.linkdisconnectrate = linkdisconnectrate

    def Generate(self) -> nx.DiGraph:
        nodecount = self.nodecount if type(self.nodecount) == int else rd.randint(self.nodecount[0], self.nodecount[1])
        PHY = nx.DiGraph()
        for i in range(nodecount):
            nodecap = self.nodecap
            PHY.add_node(i, cap=nodecap, kind="host")
        for n in PHY.nodes:
            for nn in PHY.nodes:
                if n == nn:
                    continue
                if (PHY.edges.get((n, nn), None)):
                    continue
                linkcap = self.linkcap
                PHY.add_edge(n, nn, cap=linkcap)
                linkcap = self.linkcap
                PHY.add_edge(nn, n, cap=linkcap)
        linkcount = len(list(PHY.edges))
        for i in range(int(linkcount * self.linkdisconnectrate)):
            link = rd.choice(list(PHY.edges))
            PHY.remove_edge(link[0], link[1])
        PHY.name = f"randomphy_{len(list(PHY.nodes))}nodes_{len(list(PHY.edges))}links_{uuid.uuid4().hex[:8]}"
        return PHY
