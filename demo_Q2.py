import networkx as nx
import matplotlib.pyplot as plt
import FlexSliceMappingProblem as FSMP
import Solvers
from Solvers.Greedy import Solver as GreedySolver
from FlexSliceMappingProblem import ilp as ILP
from pulp import *
from helper_minh import extract_mapping_result
from Solvers.QLearn.env_Q2 import StaticMapping2Env
from Solvers.QLearn import agent_Q2

from Solvers.Greedy.ultilities import physicalNodeConnect, nodeOrdersToLinks

phy_generator = FSMP.phy.kfat.FatTreeGraphGenerator(
    4, 
    host_nodecap=[10.0000001, 10.0000001, 10.0000001],
    edge_nodecap=[20.0000001, 20.0000001, 20.0000001],
    aggr_nodecap=[50.0000001, 50.0000001, 50.0000001],
    core_nodecap=[100.0000001, 100.0000001, 100.0000001],
    hostedge_linkcap=[5.0000001],
    edgeaggr_linkcap=[10.0000001],
    aggrcore_linkcap=[100.0000001]
)

PHY = phy_generator.Generate()

slice_generator = FSMP.slice.flex.FlexSliceGenerator("_1_2_",1,1)

# print(slice_generator.Generate())     # tao ra slice
# print(slice_generator.GenerateSet(3)) # tao ra slice set

slice_config3 = slice_generator.Generate()[1]
# print(slice_config3)
K = [slice_config3]
print(K)
big_m = 1500
beta = 20
env = StaticMapping2Env(PHY, K, {"node_req": "req", "link_req": "req", "node_cap": "cap", "link_cap": "cap"}, big_m, beta )
agent = agent_Q2.QLearningAgent(env.obs_space_size, env.action_space_size,  alpha=0.009, gamma=0.8, epsilon_max=1, 
                                        epsilon_min=0.01, epsilon_decay=0.000198)

trained_agent, rewards = agent_Q2.TrainAgent(agent, env, nepisode=10, verbose=True, liveview=True)