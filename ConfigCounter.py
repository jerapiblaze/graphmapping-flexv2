import networkx as nx
import os
import datetime
import multiprocessing as mp
from collections import Counter
from utilities.dir import RecurseListDir
from utilities.multiprocessing import MultiProcessing, IterToQueue


from FlexSliceMappingProblem import SliceMappingProblem, LoadProblem
from FlexSliceMappingProblem.validate import SolutionData
from FlexSliceMappingProblem.utilities import ComposeLinearNodeOrder

def ConfigParser(sfc, key:str=None) -> str:
    order = ComposeLinearNodeOrder(sfc)
    if key is None:
        s = "_".join([str(k) for k in order])
    else:
        s = "_".join([nx.get_node_attributes(sfc,key)[k] for k in order])
    return s

def ConfigCounter(problem:SliceMappingProblem) -> dict[str,int]:
    soldata = SolutionData(problem.solution)
    phis = [str(k).split('_')[-2:] for k in list(problem.solution.keys()) if str(k).startswith("phi_") and round(problem.solution[k]) == 1]
    configs_list = [problem.SLICES_SET[int(phi[0])][int(phi[1])].name.split("_")[2] for phi in phis]
    # assembled_sfcs = assemble_sfc_from_solution(soldata, problem.SFC_SET)
    # configs_list = [ConfigParser(sfc) for sfc in assembled_sfcs if soldata(f"xSFC_{assembled_sfcs.index(sfc)}")]
    counter = Counter(configs_list)
    counter = dict(counter)
    return counter
    
def MpWorker(queue:mp.Queue, result_file:str):
    while queue.qsize():
        solved_problem_path = queue.get()
        solved_problem = LoadProblem(solved_problem_path)
        prob_set_info = str(os.path.basename(os.path.dirname(solved_problem_path))).split("@")
        set_name = prob_set_info[0]
        solver_name = prob_set_info[1]
        problem_name = solved_problem.name
        config_count = ConfigCounter(solved_problem)
        solution_status = solved_problem.solution_status
        obj_value = solved_problem.obj_value if solution_status == 1 else 0
        with open(result_file, "at") as f:
            for k in list(config_count.keys()):
                f.write(f"{set_name},{solver_name},{problem_name},{k},{config_count[k]},{abs(obj_value)}\n")
    pass

def Main():
    solved_problem_paths = RecurseListDir("./data/solutions", ["*.pkl.gz"])
    result_file = os.path.join(f"./data/results/configcount_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(result_file, "wt") as f:
        f.write(f"setname,solvername,problemname,config,configcount,objvalue\n")
    q = IterToQueue(solved_problem_paths)
    MultiProcessing(MpWorker, (q, result_file), 1)

if __name__=="__main__":
    Main()
    pass