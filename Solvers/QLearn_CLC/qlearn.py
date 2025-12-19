import sys
import os
import time
import pickle
from Solvers.Greedy.greedy import mapSlice
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
        n_slices = self.env.observation_space_size

        while obs < n_slices:

            # chọn action từ Q-table
            action = self.agent.choose_action(obs, trainmode=False)
            action = action - 1  # 0=skip, 1=cfg0,2=cfg1,3=cfg2

            # ----------- skip -----------
            if action == -1:
                obs += 1
                continue

            # ----------- check valid config index -----------
            if action >= len(SLICES_SET[obs]):
                # agent chọn cấu hình không tồn tại → skip
                obs += 1
                continue

            config = SLICES_SET[obs][action]

            # ----------- run greedy embedding -----------
            _phy, nodeMap, linkMap, info = mapSlice(PHY, config)
            if not info["isSuccess"]:
                # fail mapping → kết thúc (giống greedy)
                return solution

            # ----------- update solution -----------
            obs += 1
            solution.update({f"pi_{obs}":1})
            solution.update({f"phi_{obs}_{action}":1})
            solution.update({f"xNode_{obs}_{action}_{n[0]}_{n[1]}":1 for n in nodeMap})
            solution.update({f"xEdge_{obs}_{action}_({l[0][0]},_{l[0][1]})_({l[1][0]},_{l[1][1]})":1 for l in linkMap})

            # ----------- update PHY -----------
            PHY = _phy

        return solution

            
        