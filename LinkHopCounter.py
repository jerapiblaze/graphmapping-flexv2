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
from FlexSliceMappingProblem.utilities import ComposeLinearNodeOrder

def CountTotalLinks(problem:SliceMappingProblem) -> tuple[int,int]:
    solution = problem.solution
    total_vlinks = 0
    total_links = 0
    for s in range(len(problem.SLICES_SET)):
        if (not solution.get(f"pi_{s}", 0)):
            continue
        sfc = problem.SLICES_SET[s]
        len_sfc = len(sfc)
        for k in range(len(sfc)):
            if (not solution.get(f"phi_{s}_{k}", 0)):
                continue
            config = sfc[k]
            total_vlinks += len(list(config.edges))
            total_links += len([v for v in list(solution.keys()) if str(v).startswith(f"xEdge_{s}_{k}_") and round(solution[v]) == 1])
    return total_vlinks, total_links, len_sfc
    
def MpWorker(queue:mp.Queue, result_file:str):
    while queue.qsize():
        solved_problem_path = queue.get()
        solved_problem = LoadProblem(solved_problem_path)
        print("OBJ =", solved_problem.obj_value)
        prob_set_info = str(os.path.basename(os.path.dirname(solved_problem_path))).split("@")
        set_name = prob_set_info[0]
        solver_name = prob_set_info[1]
        problem_name = solved_problem.name
        total_vlinks, total_links, len_sfc = CountTotalLinks(solved_problem)
        hops = round(total_links/total_vlinks, 5) 
        solution_status = solved_problem.solution_status
        obj_value = len([var for var in solved_problem.solution.keys() if str(var).startswith("pi_") and solved_problem.solution[var] == 1]) if solution_status == 1 else 0
        # print(obj_value)
        # print(solved_problem.obj_value)
        # for var in solved_problem.solution.keys():
        #     if str(var).startswith("pi_") and solved_problem.solution[var] == 1:
        #         print(var)
        # L = (0.9999*obj_value - 4.999)/(1-0.9999)
        # print(L)
        with open(result_file, "at") as f:
            f.write(f"{set_name},{solver_name},{problem_name},{obj_value},{total_vlinks},{total_links},{hops}\n")
    pass

def Main():
    solved_problem_paths = RecurseListDir("./data/solu", ["*.pkl.gz"])
    result_file = os.path.join(f"./data/results/linkhop_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(result_file, "wt") as f:
        f.write(f"setname,solvername,problemname,objvalue,totalvirtuallinks,totalphysicallinks,nhops\n")
    q = IterToQueue(solved_problem_paths)
    MultiProcessing(MpWorker, (q, result_file), 1)

if __name__=="__main__":
    Main()
    pass