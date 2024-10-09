import gymnasium as gym
import networkx as nx
import numpy as np
import copy

class RLen2(gym.Env):
    action_space = gym.Space()
    
    observation_space = gym.Space()
    
    physical_graph = nx.DiGraph()
    
    vnf_order = list()
    
    __mapped_sfc = int()
    
    vnf_order_index_current = int()
    link_solution_current = list()

    node_solution_lastgood = list()
    link_solution_lastgood = list()
    
    node_possible_solution_current = list()
    link_possible_solution_current = list()    
    
    node_solution_current = list() # sfc_id, k, vnf_id, node_id
    
    max_config = int()
    
    def __init__(self, physical_graph: nx.DiGraph, sfcs_list: list[list[nx.DiGraph]], M:int, beta:float):
        super(RLen2, self).__init__()
        
        self.physical_graph = physical_graph

        self.sfcs_list = sfcs_list

        self.vnf_order = VNodeMappingOrderCompose(self.sfcs_list) # (s_index, k, vnode)
        self.max_config = 2
        
        self.observation_space = gym.spaces.Discrete(n=len(self.vnf_order), seed=42, start=0)
        self.obs_space_size = len(self.vnf_order)

        self.action_space = gym.spaces.Discrete(len(self.physical_graph.nodes) + 1)
        self.M = M
        self.beta = beta
        self.__is_truncated = False
        
        self.node_solution_current = list()
        self.link_solution_current = list()
        self.node_solution_lastgood = list()
        self.link_solution_lastgood = list()
        self.node_possible_solution_current = list()
        self.link_possible_solution_current = list()

    def reset(self, seed=None, options=None):
        # Initialize state
        self.physical_graph_current = copy.deepcopy(self.physical_graph)
        self.physical_graph_current_cf0= copy.deepcopy(self.physical_graph_current)
        self.physical_graph_current_cf1= copy.deepcopy(self.physical_graph_current)
        self.node_solution = list()
        self.link_solution = list()
        self.sfc_solution = list()
        self.__mapped_sfc = 0
        self.__is_truncated = False
        return (self.vnf_order_index_current, {"message": "environment reset"})
    
    def __execute_node_mapping(self, sfc_id, k, vnf_id, node_id):
        vnode_req = self.__get_vnode_req(sfc_id, k ,vnf_id)
        nodes_cap = self.__get_node_cap(None)
        nodes_cap[node_id] -= vnode_req
        if any(node < 0 for node in nodes_cap):
            raise nx.NetworkXUnfeasible(f"Requested vnode sfc={sfc_id} of config={k} vnf={vnf_id}  has exceed capacity of node={node_id}")
        nx.set_node_attributes(self.physical_graph_current, nodes_cap, "weight")
        self.node_solution_current.append((sfc_id, k, vnf_id, node_id))
    
    def __execute_node_mapping_temp(self, sfc_id, k, vnf_id, node_id):
        vnode_req = self.__get_vnode_req(sfc_id, k ,vnf_id)
        nodes_cap = self.__get_node_cap(None)
        nodes_cap[node_id] -= vnode_req
        if any(node < 0 for node in nodes_cap):
            raise nx.NetworkXUnfeasible(f"Requested vnode sfc={sfc_id} of config={k} vnf={vnf_id}  has exceed capacity of node={node_id}")
        if k == 0:
            nx.set_node_attributes(self.physical_graph_current_cf0, nodes_cap, "weight")
        elif k == 1:
            nx.set_node_attributes(self.physical_graph_current_cf1, nodes_cap, "weight")
        self.node_possible_solution_all_configs[k].append((sfc_id, k, vnf_id, node_id))
        
         
    def __execute_link_mapping(self, sfc_id, k, vlink_id, link_id):
        vlink_req = self.__get_vlink_req(sfc_id, k, vlink_id)
        links_cap = self.__get_link_cap(None)
        links_cap[link_id] += vlink_req
        if any(link < 0 for link in links_cap.values()):
            raise nx.NetworkXUnfeasible(f"Requested vnode sfc={sfc_id} vnf={vlink_id} has exceed capacity of node={link_id}")
        nx.set_edge_attributes(self.physical_graph_current, links_cap, "weight")
        self.link_solution_current.append((sfc_id, k, vlink_id, link_id))    
        
    def __get_action_details(self, action):
        node_id = action
        sfc_id, k, vnf_id = self.vnf_order[self.vnf_order_index_current]
        sfc_id_prev, k_prev, vnf_id_prev = self.vnf_order[self.vnf_order_index_current - 1]
        search_result = [node_sol[3] for node_sol in self.node_solution_current if node_sol[0] == sfc_id_prev and node_sol[2] == vnf_id_prev and node_sol[1 == k_prev]] 
        node_id_prev = search_result[0] if len(search_result) else None
        return node_id, sfc_id, vnf_id, node_id_prev, sfc_id_prev, vnf_id_prev, k, k_prev

    def __is_first_of_sfc(self):
        if (self.__is_reached_termination()):
            return False
        if (self.vnf_order_index_current == 0):
            return True
        sfc_id, k, vnf_id = self.vnf_order[self.vnf_order_index_current]
        sfc_id_prev, k_prev, vnf_id_prev = self.vnf_order[self.vnf_order_index_current - 1]
        if sfc_id == sfc_id_prev and k == k_prev:
            return False
        return True

    def __is_last_of_sfc(self):
        if (self.__is_reached_termination()):
            return True
        if ((self.vnf_order_index_current + 1) >= len(self.vnf_order)):
            return True
        sfc_id, k, vnf_id = self.vnf_order[self.vnf_order_index_current]
        sfc_id_next, k, vnf_id_next = self.vnf_order[self.vnf_order_index_current + 1]
        if sfc_id == sfc_id_next:
            return False
        return True

    def __confirm_mapping(self):
        self.node_solution_lastgood = copy.deepcopy(self.node_solution_current)
        self.link_solution_lastgood = copy.deepcopy(self.link_solution_current)
        self.vnf_order_index_current += 1

    def __abort_mapping(self):  # hủy mapping
        self.node_solution_current = copy.deepcopy(self.node_solution_lastgood)
        self.link_solution_current = copy.deepcopy(self.link_solution_lastgood)

    def is_full_mapping(self):
        if (self.__mapped_sfc == len(self.sfcs_list)):
            return True
        return False

    def __is_reached_termination(self):
        if (self.vnf_order_index_current >= len(self.vnf_order)):
            return True
        return False

    def __validate_action(self, action):
        node_id, sfc_id, vnf_id, node_id_prev, sfc_id_prev, vnf_id_prev, k, k_prev = self.__get_action_details(action)
        node_cap = self.__get_node_cap(node_id)
        vnf_req = self.__get_vnode_req(sfc_id, k, vnf_id)
        if vnf_req > node_cap:
            return f"Requirement of {sfc_id}_{vnf_id} beyound capacity of {node_id}"
        if self.__is_first_of_sfc():
            return None
        # Check if node is used or not
        if any(node_sol[0] == sfc_id and node_sol[1]== k and node_sol[3] == node_id for node_sol in self.node_solution_current):
            return f"node {node_id} used"
    
    def step(self, action):
        action = action - 1
        if (action == -1):
            self.__skip_sfc()
            reward = 0 - self.M
            info = {
                "message": "skip the sfc"
            }
            self.__is_truncated = False
            self.__abort_mapping() 
            return (self.vnf_order_index_current, reward, self.__is_reached_termination(), self.__is_truncated, info)

        # If terminated or failed earlier, do nothing
        if (self.__is_reached_termination() or self.__is_truncated):
            reward = 0
            info = {
                "message": "the env is terminated or truncated"
            }
            self.__is_truncated = True
            return (self.vnf_order_index_current, reward, self.__is_reached_termination(), self.__is_truncated, info)

        # Check if first action and last action
        is_first = self.__is_first_of_sfc()
        is_last = self.__is_last_of_sfc()

        reward = 0
        info = {}
        # If action is invalid
        action_validation = self.__validate_action(action)
        if (action_validation):
            reward = 0 - self.M
            self.__abort_mapping() 
            info = {
                "message": f"action invalid: {action_validation}"
            }
            self.__is_truncated = True
            return (self.vnf_order_index_current, reward, self.__is_reached_termination(), self.__is_truncated, info)

        node_id, sfc_id, vnf_id, node_id_prev, sfc_id_prev, vnf_id_prev, k, k_prev = self.__get_action_details(action)
        
        reward = 0
        reward_dict = {}
        if sfc_id == sfc_id_prev:
            if k == k_prev: 
                ai_t = self.__get_node_cap(node_id)
                rv = self.__get_vnode_req(sfc_id, k, vnf_id)

                try:
                    self.__execute_node_mapping_temp(sfc_id, vnf_id, node_id)
                except nx.NetworkXUnfeasible:
                    self.__abort_mapping()
                    info = {
                        "message": f"no node for {sfc_id}_{vnf_id} ({node_id})"
                    }
                    reward = 0 - self.M
                    self.__is_truncated = True
                    return (self.vnf_order_index_current, reward, self.__is_reached_termination(), self.__is_truncated, info)

                if is_first:
                    self.__confirm_mapping()
                    reward = self.M - (ai_t - rv)
                    info = {"message": "first action success"}
                    reward_dict[k] += reward
                nhops = 0
                try:
                    vlink = (vnf_id_prev, vnf_id)
                    vlink_req = self.__get_vlink_req(sfc_id, k, vlink)
                    paths = PhysicalNodeConnect(self.physical_graph_current, node_id_prev, node_id, vlink_req, self.key_attrs["node_cap"])
                    paths = GetPathListFromPath(paths)
                    for path in paths:
                        self.__execute_link_mapping(sfc_id, vlink, path)
                        nhops += 1
                except nx.NetworkXUnfeasible:
                    self.__abort_mapping()
                    info = {
                        "message": f"no link for {sfc_id_prev}_{vnf_id_prev}-{sfc_id}_{vnf_id} ({node_id_prev}-{node_id})"
                    }
                    reward = 0 - self.M
                    self.__is_truncated = True
                    reward_dict[k] += reward
                    
                self.__confirm_mapping()
                reward = self.M - (ai_t - rv) - self.beta * nhops
                reward_dict[k] += reward
            else:
                self.node_possible_solution_all_configs = {}
                
        else:
            self.physical_graph_current_cf0 = copy.deepcopy(self.physical_graph_current)
            self.physical_graph_current_cf1 = copy.deepcopy(self.physical_graph_current)
        # After calculating rewards for both configurations, compare them
        if reward_dict[0] > reward_dict[1]:
            best_config = 0
            self.physical_graph_current = self.physical_graph_current_cf0
        else:
            best_config = 1 
            self.physical_graph_current = self.physical_graph_current_cf1
        reward = reward_dict[best_config]
        return (self.vnf_order_index_current, reward, self.__is_reached_termination(), self.__is_truncated, info)

    def __get_node_cap(self, node_id): 
        node_caps = nx.get_node_attributes(self.physical_graph_current, "weight")
        if (node_id is None):
            return node_caps
        return node_caps[node_id]
    def __get_link_cap(self, link_id):
        link_caps = nx.get_edge_attributes(self.physical_graph_current, name=self.key_attrs["link_cap"])
        if (link_id is None):
            return link_caps
        return link_caps[link_id]
    def __get_vnode_req(self, sfc_id, k,vnf_id):  
        vnf_reqs = nx.get_node_attributes(self.sfcs_list[sfc_id][k],"weight")
        if (vnf_id is None):
            return vnf_reqs
        return vnf_reqs[vnf_id]
    def __get_vlink_req(self, sfc_id, k,vlink_id):
        vlink_reqs = nx.get_edge_attributes(self.sfcs_list[sfc_id][k], "weight")
        if (vlink_id is None):
            return vlink_reqs
        return vlink_reqs[vlink_id]
    
    
def VNodeMappingOrderCompose(sfcs_list: list[list[nx.DiGraph]]):
    order = []
    for s_index, s in enumerate(sfcs_list):
        for k, config in enumerate(s):
            for vnode in config.nodes:
                order.append((s_index, k, vnode))
    return order 

def PhysicalNodeConnect(graph, start, end, requirement):
    print(start, end, requirement)
    print(graph.name)
    for x, y, data in graph.edges(data=True):
        print(x,y)
        print(data)
    tmp_graph = nx.restricted_view(
        graph,
        [],
        tuple((x, y) for x, y, data in graph.edges(data=True) if data['weight'] <= requirement)
    )
    path = nx.shortest_path(tmp_graph, start, end)
    print(path)
    return path

def GetPathListFromPath(path):
    return [(a, b) for a in path for b in path if path.index(b)-path.index(a) == 1]
