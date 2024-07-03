import matplotlib.pyplot as plt
import FlexSliceMappingProblem as FSMP
import networkx as nx
from FlexSliceMappingProblem.validate import validatesolution
from Solvers.Greedy.greedy import Greedy
from utilities.profiler import StopWatch
# problem = FSMP.LoadProblem("./data/solutions/MIXED_EZ@ILP_CPLEX/graphmapping_9da4f355.pkl.gz")

# print(problem.solution_status)
# print(problem)

# profiler = StopWatch("Demo", True)
# profiler.start()

# a = Greedy(problem.PHY, problem.SLICES_SET, profiler, 10)

# profiler.end()

# print(a)

# a = validatesolution(problem.PHY, problem.SLICES_SET, problem.solution, 5)
# print(a)

g = FSMP.phy.kfat.FatTreeGraphGenerator(
    2,
    (10,10,10), (10,10,10), (10,10,10), (10,10,10), (10,), (10,), (10,)
)

g = g.Generate()

print(g)

plt.figure(figsize=(16,10))
nx.draw_networkx(g, g.NodeLocations)
plt.savefig("./2fat.png")
plt.show()