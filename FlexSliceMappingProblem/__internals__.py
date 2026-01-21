import pickle
import pulp
import uuid
import networkx as nx
import gzip

class SliceMappingProblem:
    def __init__(self, phy:nx.DiGraph, slices_set:list[list[nx.DiGraph]], name: str | None = None) -> None:
        self.name = name if name is not None else f"graphmapping_{uuid.uuid4().hex[:8]}"
        self.PHY = phy
        self.SLICES_SET = slices_set
        self.solution = None
        self.solution_time = None
        self.obj_value = None
        self.status = None # None=Unsolved, 1=Solved, 0=SolvedNoSolution, -1=ErrorOnSolve
        self.solution_status = None # None=Unsolved, 1=OK, 0=NoSolution, -1=Invalid
    

def SaveProblem(path:str, problem:SliceMappingProblem) -> None:
    with gzip.open(path, "wb") as f:
        pickle.dump(problem, f)

def LoadProblem(path:str) -> SliceMappingProblem:
    problem = None
    with gzip.open(path, "rb") as f:
        problem = pickle.load(f)
    return problem
