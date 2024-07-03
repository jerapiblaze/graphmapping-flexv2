import sys
import os
import pulp

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from FlexSliceMappingProblem import SliceMappingProblem
from FlexSliceMappingProblem.ilp import ConvertToIlp, VARIABLE_SURFIXES
from Solvers import SliceMappingSolver

class ILPSolver(SliceMappingSolver):
    def __init__(self, problem: SliceMappingProblem, logpath:str=None, timelimit:int=None, verbose:bool=False):
        self.SOLVER = pulp.LpSolver()
        self.PROBLEM = problem
        self.ILP_PROBLEM = ConvertToIlp(self.PROBLEM)
        self.logpath = logpath
        if self.logpath:
            self.ILP_PROBLEM.writeLP(f"{os.path.join(self.logpath, problem.name)}.lp")
        pass

    def Solve(self) -> SliceMappingProblem:
        self.ILP_PROBLEM.solve(solver=self.SOLVER)
        solution = {str(var): pulp.value(var) 
                    for var in self.ILP_PROBLEM.variables() 
                    if not pulp.value(var) == 0 and any(str(var).startswith(filter) for filter in VARIABLE_SURFIXES)}
        obj_value = len([var for var in solution.keys() if str(var).startswith("xSFC") and solution[var] == 1])
        solver_runtime = self.ILP_PROBLEM.solutionTime
        solver_status = self.ILP_PROBLEM.status
        self.PROBLEM.solution = solution
        if self.logpath:
            with open(os.path.join(self.logpath, f"{self.PROBLEM.name}.sol"), "wt") as f:
                for k in solution.keys():
                    f.write(f"{k}:{solution[k]}\n")
        self.PROBLEM.status = solver_status
        self.PROBLEM.obj_value = obj_value
        self.PROBLEM.solution_time = solver_runtime
        return self.PROBLEM