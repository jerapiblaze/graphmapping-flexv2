import networkx as nx
import copy
import uuid

def GraphClone(target: nx.DiGraph):
    cloned = copy.deepcopy(target)
    cloned.name = f"{target.name}_cloned_{uuid.uuid4().hex[:8]}"
    return cloned

def subsets(s):  
    if len(s) == 0:  
        return [[]]  
    x = subsets(s[:-1])  
    return x + [[s[-1]] + y for y in x]

def ComposeLinearNodeOrder(sfc: nx.DiGraph):
    order = []
    for vnode in nx.topological_sort(sfc):
        order.append(vnode)
    return order