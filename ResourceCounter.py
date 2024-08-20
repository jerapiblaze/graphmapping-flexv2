import networkx as nx
import os
import datetime
import multiprocessing as mp
import numpy as np
from collections import Counter
from utilities.dir import RecurseListDir
from utilities.multiprocessing import MultiProcessing, IterToQueue


from FlexSliceMappingProblem import SliceMappingProblem, LoadProblem
from FlexSliceMappingProblem.resources import ZERO_NODE_RESOURCE, ZERO_LINK_RESOURCE
from FlexSliceMappingProblem.slice import GetVLinkReq_safe, GetAllPossibleVirtualEdge

def NodeUsageCounter(problem:SliceMappingProblem) -> tuple[tuple[float,float],tuple[float,float],tuple[float,float]]:
    obj_value = len([var for var in problem.solution.keys() if str(var).startswith("pi_") and problem.solution[var] == 1]) if problem.solution_status == 1 else 0
    node_usage = dict()
    caps = nx.get_node_attributes(problem.PHY, "cap")
    for node in list(problem.PHY.nodes):
        usage = ZERO_NODE_RESOURCE
        for sfc in problem.SLICES_SET:
            s = problem.SLICES_SET.index(sfc)
            for config in problem.SLICES_SET[s]:
                k = problem.SLICES_SET[s].index(config)
                if not (problem.solution.get(f"pi_{s}", 0)):
                    continue
                if not (round(problem.solution.get(f"phi_{s}_{k}", 0))):
                    continue
                reqs = nx.get_node_attributes(config, "req")
                for vnode in list(config.nodes):
                    if not (round(problem.solution.get(f"xNode_{s}_{k}_{vnode}_{node}", 0))):
                        continue
                    usage += reqs[vnode]
        # res[node] = (caps[node],usage)
        node_usage[node] = [usage.resources[i]/obj_value if not (caps[node].resources[i] == 0) else 0 for i in range(3)]
    node_cpu_usage = [node_usage[k][0] for k in list(node_usage.keys()) if node_usage[k][0] > 0]
    node_mem_usage = [node_usage[k][1] for k in list(node_usage.keys()) if node_usage[k][1] > 0]
    node_sto_usage = [node_usage[k][2] for k in list(node_usage.keys()) if node_usage[k][2] > 0]
    if len(node_cpu_usage) == 0:
        node_cpu_usage = [0]
    if len(node_mem_usage) == 0:
        node_mem_usage = [0]
    if len(node_sto_usage) == 0:
        node_sto_usage = [0]
    cpu_mean, cpu_std = np.mean(node_cpu_usage), np.std(node_cpu_usage)
    mem_mean, mem_std = np.mean(node_mem_usage), np.std(node_mem_usage)
    sto_mean, sto_std = np.mean(node_sto_usage), np.std(node_sto_usage)
    return ((cpu_mean, cpu_std), (mem_mean, mem_std), (sto_mean, sto_std))
    pass

def LinkUsageCounter(problem:SliceMappingProblem) -> tuple[tuple[float,float]]:
    obj_value = len([var for var in problem.solution.keys() if str(var).startswith("pi_") and problem.solution[var] == 1]) if problem.solution_status == 1 else 0
    link_usage = dict()
    caps = nx.get_edge_attributes(problem.PHY, "cap")
    for link in list(problem.PHY.edges):
        usage = ZERO_LINK_RESOURCE
        for sfc in problem.SLICES_SET:
            s = problem.SLICES_SET.index(sfc)
            for config in problem.SLICES_SET[s]:
                k = problem.SLICES_SET[s].index(config)
                if not (problem.solution.get(f"pi_{s}", 0)):
                    continue
                if not (round(problem.solution.get(f"phi_{s}_{k}", 0))):
                    continue
                vlink_req = nx.get_edge_attributes(config, "req")
                for vlink in list(config.edges):
                    if not (round(problem.solution.get(f"xEdge_{s}_{k}_{vlink}_{link}".replace(", ", ",_"), 0))):
                        continue
                    usage += vlink_req[vlink]
        link_usage[link] = [usage.resources[i]/obj_value if not (caps[link].resources[i] == 0) else 0 for i in range(1)]
    link_bw_usage = [link_usage[k][0] for k in list(link_usage.keys()) if link_usage[k][0] > 0]
    if len(link_bw_usage) == 0:
        link_bw_usage = [0]
    bw_mean, bw_std = np.mean(link_bw_usage), np.std(link_bw_usage)
    return ((bw_mean, bw_std),)

# def Main():
#     problem = LoadProblem("./data/solutions/DUMMY@GREEDY/graphmapping_071b340b.pkl.gz")
#     c = ConfigCounter(problem)
#     print(c)
    
def MpWorker(queue:mp.Queue, result_file:str):
    while queue.qsize():
        solved_problem_path = queue.get()
        solved_problem = LoadProblem(solved_problem_path)
        prob_set_info = str(os.path.basename(os.path.dirname(solved_problem_path))).split("@")
        set_name = prob_set_info[0]
        solver_name = prob_set_info[1]
        problem_name = solved_problem.name
        node_usage = NodeUsageCounter(solved_problem)
        link_usage = LinkUsageCounter(solved_problem)
        solution_status = solved_problem.solution_status
        obj_value = len([var for var in solved_problem.solution.keys() if str(var).startswith("pi_") and solved_problem.solution[var] == 1]) if solution_status == 1 else 0
        with open(result_file, "at") as f:
            f.write(f"{set_name},{solver_name},{problem_name},{obj_value},{node_usage[0][0]},{node_usage[0][1]},{node_usage[1][0]},{node_usage[1][1]},{node_usage[2][0]},{node_usage[2][1]},{link_usage[0][0]},{link_usage[0][1]}\n")
    pass

def Main():
    solved_problem_paths = RecurseListDir("./data/solutions", ["*.pkl.gz"])
    result_file = os.path.join(f"./data/results/resources_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(result_file, "wt") as f:
        f.write(f"setname,solvername,problemname,objvalue,cpu_mean,cpu_std,mem_mean,mem_std,sto_mean,sto_std,bw_mean,bw_std\n")
    q = IterToQueue(solved_problem_paths)
    MultiProcessing(MpWorker, (q, result_file), 1)

if __name__=="__main__":
    Main()
    pass