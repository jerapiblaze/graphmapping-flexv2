import argparse
import multiprocessing as mp
import os
import uuid

from utilities.config import ConfigParser
from utilities.multiprocessing import MultiProcessing, IterToQueue
from utilities.dir import RecurseListDir, CleanDir
from FlexSliceMappingProblem import SliceMappingProblem, SaveProblem, LoadProblem
from FlexSliceMappingProblem.validate import ValidateSolution


def ILPSolveMpWorker(queue: mp.Queue, Solver, solution_setpath: str, log_setpath: str, timelimit: int, ndigits: int):
    while queue.qsize():
        problem_path = queue.get()
        model = Solver(problem=LoadProblem(problem_path), logpath=log_setpath, timelimit=timelimit)
        solved_problem = model.Solve()
        validated_problem = ValidateSolution(solved_problem, debug=True, ndigits=ndigits)
        savepath = os.path.join(solution_setpath, f"{validated_problem.name}.pkl.gz")
        SaveProblem(savepath, validated_problem)
    exit()


def HeuristicsSolveMpWorker(queue: mp.Queue, Solver, solution_setpath: str, log_setpath: str, timelimit: int, ndigits: int):
    while queue.qsize():
        problem_path = queue.get()
        model = Solver(problem=LoadProblem(problem_path), logpath=log_setpath, timelimit=timelimit)
        solved_problem = model.Solve()
        validated_problem = ValidateSolution(solved_problem, debug=True, ndigits=ndigits)
        savepath = os.path.join(solution_setpath, f"{validated_problem.name}.pkl.gz")
        SaveProblem(savepath, validated_problem)
    exit()


def Main(config: dict):
    print(config)
    PROBLEM_SETNAME = config["PROBLEM_SETNAME"]
    PROBLEM_SETPATH = os.path.join("./data/problems", PROBLEM_SETNAME)
    problem_set = RecurseListDir(PROBLEM_SETPATH, ["*.pkl.gz"])

    SOLVER = str(config["SOLVER"]).split("@")
    timelimit = config["TIMELIMIT"]
    ndigits = config["NDIGITS"]
    target = None
    args = ()

    q = IterToQueue(problem_set)

    match SOLVER[0]:
        case "ILP":
            target = ILPSolveMpWorker
            match SOLVER[1]:
                case "CBC":
                    from Solvers.ILP.cbc import Solver
                case "SCIP":
                    from Solvers.ILP.scip import Solver
                case "CPLEX":
                    from Solvers.ILP.cplex import Solver
                case "GUROBI":
                    from Solvers.ILP.gurobi import Solver
                case _:
                    raise Exception(f"[Invalid config] SOLVER=ILP_{SOLVER[1]}")
            SOLUTION_SETPATH = os.path.join("./data/solutions", f"{PROBLEM_SETNAME}@{'_'.join(SOLVER)}")
            CleanDir(SOLUTION_SETPATH)
            LOG_SETPATH = os.path.join("./data/logs", f"{PROBLEM_SETNAME}@{'_'.join(SOLVER)}")
            CleanDir(LOG_SETPATH)
            args = (q, Solver, SOLUTION_SETPATH, LOG_SETPATH, timelimit, ndigits)
        case "GREEDY":
            target=HeuristicsSolveMpWorker
            from Solvers.Greedy import Solver
            SOLUTION_SETPATH = os.path.join("./data/solutions", f"{PROBLEM_SETNAME}@{'_'.join(SOLVER)}")
            CleanDir(SOLUTION_SETPATH)
            LOG_SETPATH = os.path.join("./data/logs", f"{PROBLEM_SETNAME}@{'_'.join(SOLVER)}")
            CleanDir(LOG_SETPATH)
            args = (q, Solver, SOLUTION_SETPATH, LOG_SETPATH, timelimit, ndigits)
        case _:
            raise Exception(f"[Invalid config] SOLVER={SOLVER[0]}")

    MultiProcessing(target, args, 4)


def MpWorker(queue: mp.Queue):
    while queue.qsize():
        item = queue.get()
        Main(item)
    exit()


if __name__ == "__main__":
    mp.set_start_method("spawn")
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-c", "--config", default="./configs/SolveSettings/dummy.yaml")
    args = argparser.parse_args()
    config_list = ConfigParser(args.config)
    q = IterToQueue(config_list)
    MultiProcessing(MpWorker, (q,), 2)
