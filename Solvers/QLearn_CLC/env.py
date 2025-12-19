import gymnasium as gym
import networkx as nx
import numpy as np
import copy

from Solvers.Greedy.greedy import mapSlice     # dùng mapSlice greedy thật
import warnings
warnings.filterwarnings("ignore", message="Spaces are not permitted in the name. Converted to '_'")

class RLen3(gym.Env):
    def __init__(self, physical_graph: nx.DiGraph, sfcs_list: list[list[nx.DiGraph]]):
        super(RLen3, self).__init__()
        self.physical_graph = physical_graph
        self.sfcs_list = sfcs_list
        self.num_sfcs = len(sfcs_list)
        self.observation_space = gym.spaces.Discrete(self.num_sfcs + 1)
        self.action_space = gym.spaces.Discrete(4)  # 3 config + skip
        self.__is_truncated = False
        self.observation_space_size = self.num_sfcs
        self.action_space_size = 4

    # -----------------------------
    # Reset environment
    # -----------------------------
    def reset(self):
        self.physical_graph_current = copy.deepcopy(self.physical_graph)
        self.sfc_order_current = 0
        self.mapped_configs = set()
        self.sol = {}
        self.__is_truncated = False
        return (self.sfc_order_current, {"message": "environment reset"})

    # -----------------------------
    # Helper
    # -----------------------------
    def _all_mapped(self):
        return self.sfc_order_current >= self.num_sfcs

    def _confirm_mapping(self):
        self.sfc_order_current += 1

    def _get_action_detail(self, action):
        if action not in [0, 1, 2]:
            return None
        if self.sfc_order_current >= self.num_sfcs:
            return None

        sfc_list = self.sfcs_list[self.sfc_order_current]
        if action >= len(sfc_list):
            return None
        
        return (self.sfc_order_current, action, sfc_list[action])

    # -----------------------------
    # Update resource (Greedy style)
    # -----------------------------
    def _update_resource_greedy(self, nodeMap, linkMap, sfc):
        vnode_req = nx.get_node_attributes(sfc, "req")
        vlink_req = nx.get_edge_attributes(sfc, "req")

        node_caps = nx.get_node_attributes(self.physical_graph_current, "cap")
        edge_caps = nx.get_edge_attributes(self.physical_graph_current, "cap")

        # Update node resources
        for v_node, phy_node in nodeMap:
            req = vnode_req[v_node]
            node_caps[phy_node] -= req

        nx.set_node_attributes(self.physical_graph_current, node_caps, "cap")

        # Update edge resources
        for (v, w), (i,j) in linkMap:
            req = vlink_req[(v,w)]
            edge_caps[(i, j)] -= req
        nx.set_edge_attributes(self.physical_graph_current, edge_caps, "cap")

    # -----------------------------
    # STEP – chạy Greedy mapping
    # -----------------------------
    def step(self, action):
        action = action - 1    # 0=skip, 1,2,3=choose config
        is_last = (self.sfc_order_current == self.num_sfcs - 1)

        # Terminated?
        if self._all_mapped() or self.__is_truncated:
            return self.sfc_order_current, 0, True, True, {"message": "terminated"}

        # Skip case
        if action == -1:
            reward = -0.3
            if is_last:
                self.__is_truncated = True
                return self.sfc_order_current, reward, True, True, {"message": "skip last → end"}
            else:
                self._confirm_mapping()
                done = self._all_mapped()
                return self.sfc_order_current, reward, done, False, {"message": "skip slice"}

        # Config mapping
        sfc_index, config_index, sfc = self._get_action_detail(action)
        if sfc is None:
            return self.sfc_order_current, -1, False, False, {"message": "invalid action"}

        # Already mapped?
        if (sfc_index, config_index) in self.mapped_configs:
            return self.sfc_order_current, -0.3, False, False, {"message": "duplicate config"}

        # ---- Run Greedy mapping ----
        _phy, nodeMap, linkMap, info = mapSlice(self.physical_graph_current, sfc)

        if not info["isSuccess"]:
            # Fail mapping → negative reward
            reward = -1
            if is_last:
                self.__is_truncated = True
                return self.sfc_order_current, reward, True, True, {"message": "fail last config"}
            else:
                self._confirm_mapping()
                return self.sfc_order_current, reward, False, False, {"message": "config failed"}

        # Success mapping → update resources
        self.physical_graph_current = _phy
        self._update_resource_greedy(nodeMap, linkMap, sfc)
        self.mapped_configs.add((sfc_index, config_index))

        reward = +1
        done = False

        # If last slice → terminate
        if is_last:
            self.__is_truncated = True
            return self.sfc_order_current, reward, True, True, {"message": "ALL MAPPED"}

        # Move to next slice
        self._confirm_mapping()
        return self.sfc_order_current, reward, done, False, {"message": "mapped successfully"}

    # -----------------------------
    # Return final solution
    # -----------------------------
    def render(self):
        return self.sol
