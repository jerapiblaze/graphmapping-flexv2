from .__internals__ import *

class Solver(ILPSolver):
    def __init__(self, problem: SliceMappingProblem, logpath: str = None, timelimit: int = None, verbose: bool = False):
        super().__init__(problem, logpath, timelimit, verbose)
        logfile = os.path.join(logpath, f"{problem.name}.log") if logpath else None
        self.SOLVER = pulp.PULP_CBC_CMD(
            msg=verbose,
            timeLimit=timelimit,
            logPath=logfile
        )
