import sys
import os

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Solvers import SliceMappingSolver
from FlexSliceMappingProblem import SliceMappingProblem
from FlexSliceMappingProblem.slice import GetVLinkReq_safe
from FlexSliceMappingProblem.resources import *
from utilities.profiler import StopWatch
from utilities.exceptions import get_exception_traceback_str
from Solvers.Greedy_RR.greedy_rr import GreedyRR


class Solver(SliceMappingSolver):
    def __init__(self, problem: SliceMappingProblem, logpath: str = None, timelimit: int = None, verbose: bool = False):
        self.problem = problem
        self.logpath = logpath
        self.timelimit = timelimit
        self.verbose = verbose
        self.__profiler__ = StopWatch(f"[se_eigenstar] {self.problem.name}", verbose)
        self.GreedyRR = GreedyRR

    def Solve(self,) -> SliceMappingProblem:
        self.__profiler__.start()
        sol = {}
        sta = 0
        obj = 0
        tim = 0
        try:
            sol = self.GreedyRR(PHY=self.problem.PHY, SLICE_SET=self.problem.SLICES_SET, profiler=self.__profiler__, timelimit=self.timelimit)
            obj = len([var for var in sol.keys() if str(var).startswith("pi") and sol[var] == 1])
            if obj == 0:
                sta = 0
            else:
                sta = 1
            self.__profiler__.add_stop("finished result converting")
        except Exception as e:
            error = get_exception_traceback_str(e)
            self.__profiler__.add_stop(f"ERROR: {error}")
            obj = 0
            sta = -1
        self.__profiler__.end()
        tim = self.__profiler__.total_time()
        if self.logpath:
            self.__profiler__.write_to_file(filepath=os.path.join(self.logpath, f"{self.problem.name}.log"), mode="wt")
            with open(os.path.join(self.logpath, f"{self.problem.name}.sol"), "wt") as f:
                for k in sol.keys():
                    f.write(f"{k}:{sol[k]}\n")
        self.problem.solution = sol
        self.problem.status = sta
        self.problem.solution_time = tim
        self.problem.obj_value = obj
        return self.problem
    