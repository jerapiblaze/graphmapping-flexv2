from networkx.classes import DiGraph
from .__internals__ import *

import sys
import os
import numpy as np

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from resources import NodeResource, LinkResource, ZERO_LINK_RESOURCE, ZERO_NODE_RESOURCE

class FatTreeGraphGenerator(PhysicalGraphGenerator):
    def __init__(
            self, 
            k:int, 
            host_nodecap:tuple[float, float, float], edge_nodecap:tuple[float, float, float], aggr_nodecap:tuple[float, float, float], core_nodecap:tuple[float, float, float], 
            hostedge_linkcap:tuple[float], edgeaggr_linkcap:tuple[float], aggrcore_linkcap:tuple[float]
        ):
        self.k = k
        self.host_nodecap = NodeResource(*host_nodecap)
        self.edge_nodecap = NodeResource(*edge_nodecap)
        self.aggr_nodecap = NodeResource(*aggr_nodecap)
        self.core_nodecap = NodeResource(*core_nodecap)
        self.hostedge_linkcap = LinkResource(*hostedge_linkcap)
        self.edgeaggr_linkcap = LinkResource(*edgeaggr_linkcap)
        self.aggrcore_linkcap = LinkResource(*aggrcore_linkcap)
        self.basename = f"{k}_fattree"
        pass
    
    def Generate(self) -> DiGraph:
        '''
        Initialization
        '''

        k = self.k
        
        s = []     # Start points
        t = []     # Termination points
        
        # Core-Aggr link  
        linkCoreAggr_s = []   
        linkCoreAggr_t = []   

        # Aggr-Edge link 
        linkAggrEdge_s = []   
        linkAggrEdge_t = []   

        # Edge-Host link
        linkEdgeHost_s = []   
        linkEdgeHost_t = [] 
        
        if k == 2:
            # Switch number at each layer
            num_core = 2
            num_aggr = 4
            num_edge = 4
            num_host = 8

            # Create each NodeLayer(Num, Id, X, Y)
            core = NodeLayer(num_core, 
                            np.arange(num_core),
                            np.arange(num_core), 
                            4*np.ones(num_core, dtype = int))

            aggr = NodeLayer(num_aggr, 
                            np.arange(num_core, num_core+num_aggr),
                            np.arange(num_aggr), 
                            3*np.ones(num_aggr, dtype = int))

            edge = NodeLayer(num_edge, 
                            np.arange(num_core+num_aggr, num_core+num_aggr+num_edge),
                            np.arange(num_edge), 
                            2*np.ones(num_edge, dtype = int))

            host = NodeLayer(num_host, 
                            np.arange(num_core+num_aggr+num_edge, num_core+num_aggr+num_edge+num_host),
                            np.arange(num_host), 
                            1*np.ones(num_host, dtype = int))

            # Link connections
            s = [0,0,1,1, 2,2,3,3,4,4,5,5, 6,6,7,7,8,8,9,9]
            t = [2,4,3,5, 6,7,6,7,8,9,8,9, 10,11,12,13,14,15,16,17]

            # Core-Aggr link
            linkCoreAggr_s = [0,0,1,1, 2,4,3,5]							
            linkCoreAggr_t = [2,4,3,5, 0,0,1,1]								

            # Aggr-Edge link 
            linkAggrEdge_s	= [2,2,3,3,4,4,5,5, 6,7,6,7,8,9,8,9]
            linkAggrEdge_t	= [6,7,6,7,8,9,8,9, 2,2,3,3,4,4,5,5]

            # Edge-Host link
            linkEdgeHost_s	= [6,6,7,7,8,8,9,9, 10,11,12,13,14,15,16,17]
            linkEdgeHost_t	= [10,11,12,13,14,15,16,17, 6,6,7,7,8,8,9,9]   

        else:
            # Switch number at each layer
            num_core = (k**2)//4
            num_aggr = (k**2)//2
            num_edge = (k**2)//2
            num_host = (k**3)//4

            # Create each NodeLayer(Num, Id, X, Y)
            core = NodeLayer(num_core, 
                            np.arange(num_core),
                            np.arange(num_core), 
                            4*np.ones(num_core, dtype = int))

            aggr = NodeLayer(num_aggr, 
                            np.arange(num_core, num_core+num_aggr),
                            np.arange(num_aggr), 
                            3*np.ones(num_aggr, dtype = int))

            edge = NodeLayer(num_edge, 
                            np.arange(num_core+num_aggr, num_core+num_aggr+num_edge),
                            np.arange(num_edge), 
                            2*np.ones(num_edge, dtype = int))

            host = NodeLayer(num_host, 
                            np.arange(num_core+num_aggr+num_edge, num_core+num_aggr+num_edge+num_host),
                            np.arange(num_host), 
                            1*np.ones(num_host, dtype = int))
            
            # Edge-Host link
            for x in range(num_edge):
                for y in range(k//2):
                
                    EH_s = edge.Id[x]
                    EH_t = host.Id[y+(k//2)*x]
    
                    s.append(EH_s)
                    t.append(EH_t)
    
                    linkEdgeHost_s.append(EH_s)
                    linkEdgeHost_t.append(EH_t)
    
            # Core-Aggr-Edge link
            for x in range(k):
                for y in range(k//2):
                    for z in range(k//2):
                        # Aggr to Edge
                        AE_s = aggr.Id[y+(k//2)*x]
                        AE_t = edge.Id[z+(k//2)*x]
    
                        linkAggrEdge_s.append(AE_s)
                        linkAggrEdge_t.append(AE_t)
    
                        # Core to Aggr
                        CA_s = core.Id[z+(k//2)*y]
                        CA_t = aggr.Id[y+(k//2)*x]
    
                        linkCoreAggr_s.append(CA_s)
                        linkCoreAggr_t.append(CA_t)
    
                        # Append to s and t
                        s.extend([AE_s, CA_s])
                        t.extend([AE_t, CA_t])
    

        # Total nb of nodes
        list_nodes = range(num_core+num_aggr+num_edge+num_host)

        # Total nb of edges
        num_linkCoreAggr = len(linkCoreAggr_s)
        num_linkAggrEdge = len(linkAggrEdge_s)
        num_linkEdgeHost = len(linkEdgeHost_s)

        # print(list_nodes)


        '''
        CREATE INFRASTRUCTURE GRAPH Gs
        '''

        Gs = nx.DiGraph()

        # Add nodes
        j = 0
        for i in range(num_core):
            Gs.add_node(j, cap=self.core_nodecap, kind="core")
            j += 1
        for i in range(num_aggr):
            Gs.add_node(j, cap=self.aggr_nodecap, kind="aggr")
            j += 1
        for i in range(num_edge):
            Gs.add_node(j, cap=self.edge_nodecap, kind="edge")
            j += 1
        for i in range(num_host):
            Gs.add_node(j, cap=self.host_nodecap, kind="host")
            j += 1

        # Gs.add_nodes_from(list_nodes)

        # Add Core-Aggr links
        for i in range(num_linkCoreAggr):
            Gs.add_edge(linkCoreAggr_s[i], linkCoreAggr_t[i], cap=self.aggrcore_linkcap)
            Gs.add_edge(linkCoreAggr_t[i], linkCoreAggr_s[i], cap=self.aggrcore_linkcap)

        # Add Aggr-Edge links
        for i in range(num_linkAggrEdge):
            Gs.add_edge(linkAggrEdge_s[i], linkAggrEdge_t[i], cap=self.edgeaggr_linkcap)
            Gs.add_edge(linkAggrEdge_t[i], linkAggrEdge_s[i], cap=self.edgeaggr_linkcap)

        # Add Edge-Host links
        for i in range(num_linkEdgeHost):
            Gs.add_edge(linkEdgeHost_s[i], linkEdgeHost_t[i], cap=self.hostedge_linkcap)
            Gs.add_edge(linkEdgeHost_t[i], linkEdgeHost_s[i], cap=self.hostedge_linkcap)

        # Add node coordinates
        for i, ni in enumerate(core.Id):
            Gs.nodes[ni]['pos'] = (core.X[i], core.Y[i])

        for i, ni in enumerate(aggr.Id):
            Gs.nodes[ni]['pos'] = (aggr.X[i], aggr.Y[i])

        for i, ni in enumerate(edge.Id):
            Gs.nodes[ni]['pos'] = (edge.X[i], edge.Y[i])

        for i, ni in enumerate(host.Id):
            Gs.nodes[ni]['pos'] = (host.X[i], host.Y[i])

        Gs.NodeLocations = nx.get_node_attributes(Gs, 'pos')
        Gs.name = f"{self.basename}_{len(list(Gs.nodes))}nodes_{len(list(Gs.edges))}links_{uuid.uuid4().hex[:8]}"
        return Gs
    
# Class for node layer
class NodeLayer(object):
    def __init__(self, Num, Id, X, Y):
        self.Num = Num
        self.Id = Id
        self.X = X
        self.Y = Y