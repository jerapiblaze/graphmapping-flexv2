import sys
import os
import pulp

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from FlexSliceMappingProblem import SliceMappingProblem
from FlexSliceMappingProblem.ilp import ConvertToIlp, VARIABLE_SURFIXES
from utilities.profiler import StopWatch
from utilities.exceptions import get_exception_traceback_str
from Solvers import SliceMappingSolver
from .env import RLen3
from .qlearn import QLearningSolver
from .agent import *

class Solver(SliceMappingSolver):
    def __init__(self, problem: SliceMappingProblem, saved_agent_path:str, logpath: str = None, timelimit: int = None, verbose: bool = False):
        self.problem = problem
        self.logpath = logpath
        self.timelimit = timelimit
        self.verbose = verbose
        self.agent = LoadAgent(saved_agent_path)
        self.env = RLen3(self.problem.PHY, self.problem.SLICES_SET)
        self.__profiler__ = StopWatch(f"[qlearn] {self.problem.name}", verbose)

    def Solve(self,) -> SliceMappingProblem:
        env = self.env
        agent = self.agent
        obs, info = self.env.reset()
        solver = QLearningSolver(agent, env)
        
        self.__profiler__.start()
        sol = {}
        sta = 0
        obj = 0
        tim = 0
        try:
            sol, sol_time = solver.solve()
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