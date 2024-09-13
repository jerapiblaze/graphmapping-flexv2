import sys
import os
import time
import pickle
from Solvers.Greedy.greedy import MapSlice
class QLearningSolver:
    def __init__(self, agent, env):
        self.agent = agent
        self.env = env
        

    def load_q_table(self, filepath):
        with open(filepath, 'rb') as f:
            self.agent.q_table = pickle.load(f)

    
    def solve(self, PHY, SLICES_SET):
        solution = dict()
        obs = 0
        while obs <= self.env.observation_space_size:
            action = self.agent.choose_action(obs, trainmode=False)
            action = action -1
            if action == -1:
                obs += 1
            else:
                config = SLICES_SET[obs][action]
                _phy, nodeMap, linkMap, info = MapSlice(PHY, config)
                if nodeMap == None or linkMap == None:
                    return solution
                obs += 1
                solution.update({f"pi_{obs}":1})
                solution.update({f"phi_{obs}_{action}":1})
                solution.update({f"xNode_{obs}_{action}_{n[0]}_{n[1]}":1 for n in nodeMap})
                solution.update({f"xEdge_{obs}_{action}_({l[0][0]},_{l[0][1]})_({l[1][0]},_{l[1][1]})":1 for l in linkMap})
                PHY = _phy
        return solution
            
        