from .__internals__ import *

class Solver(ILPSolver):
    def __init__(self, problem: SliceMappingProblem, logpath: str = None, timelimit: int = None, verbose: bool = False):
        super().__init__(problem, logpath, timelimit, verbose)
        logfile = os.path.join(logpath, f"{problem.name}.log") if logpath else None
        self.SOLVER = pulp.GUROBI_CMD(
            msg=verbose,
            timeLimit=timelimit,
            logPath=logfile,
            # options=[("Heuristics", "0.25"), ("NodeLimit", "100000"), ("ConcurrentMIP", "4"), ("MIPGap", "2.5e-2")]
            options=[
                # ("Heuristics", "0.25"), 
                ("NodeLimit", "500000"), 
                # ("ConcurrentMIP", "4"), 
                ("MIPGap", "0.5e-2")
            ]
        )
