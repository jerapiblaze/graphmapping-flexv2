import argparse
import multiprocessing as mp
import os

from utilities.config import ConfigParser
from utilities.multiprocessing import MultiProcessing, IterToQueue
from utilities.dir import RecurseListDir, CleanDir
from FlexSliceMappingProblem import LoadProblem, SaveProblem
from FlexSliceMappingProblem.validate import ValidateSolution


# =======================
# RL worker: per-phy weight
# =======================
def RLSolvePerPhyWorker(
    queue: mp.Queue,
    Solver,
    weight_dir: str,
    solution_setpath: str,
    log_setpath: str,
    timelimit: int,
    ndigits: int,
):
    while queue.qsize():
        problem_path = queue.get()
        problem = LoadProblem(problem_path)

        # ---- extract phy index ----
        # example: C135_ABI_10_004.pkl.gz -> 004
        problem_id = (
            os.path.basename(problem_path)
            .replace(".pkl.gz", "")
            .split("_")[-1]
        )

        # ---- find corresponding weight ----
        checkpoint_path = None
        for f in os.listdir(weight_dir):
            if (
                f.startswith(f"C135_COS_30_{problem_id}_")
                and f.endswith(".pkl.gz")
            ):
                checkpoint_path = os.path.join(weight_dir, f)
                break

        if checkpoint_path is None:
            raise FileNotFoundError(
                f"[QL_PER_PHY] No weight found for problem {problem_id}"
            )

        # ---- solve ----
        model = Solver(
            problem=problem,
            saved_agent_path=checkpoint_path,
            logpath=log_setpath,
            timelimit=timelimit,
        )

        solved_problem = model.Solve()
        validated_problem = ValidateSolution(
            solved_problem, debug=True, ndigits=ndigits
        )

        savepath = os.path.join(
            solution_setpath, f"{validated_problem.name}.pkl.gz"
        )
        SaveProblem(savepath, validated_problem)

    exit()
def RLSolveQLCLCMultiWorker(
    queue: mp.Queue,
    Solver,
    weight_dir: str,
    solution_setpath: str,
    log_setpath: str,
    timelimit: int,
    ndigits: int,
):
    while queue.qsize():
        problem_path = queue.get()
        problem = LoadProblem(problem_path)

        # ---- extract problem id ----
        problem_id = (
            os.path.basename(problem_path)
            .replace(".pkl.gz", "")
            .split("_")[-1]
        )

        # ---- find corresponding QL+CLC weight ----
        checkpoint_path = None
        for f in os.listdir(weight_dir):
            if (
                f.startswith(f"C135_COS_30_{problem_id}_")
                and f.endswith(".pkl.gz")
            ):
                checkpoint_path = os.path.join(weight_dir, f)
                break

        if checkpoint_path is None:
            raise FileNotFoundError(
                f"[QL_CLC_MULTI] No QL+CLC weight found for problem {problem_id}"
            )

        # ---- solve ----
        model = Solver(
            problem=problem,
            saved_agent_path=checkpoint_path,
            logpath=log_setpath,
            timelimit=timelimit,
        )

        solved_problem = model.Solve()
        validated_problem = ValidateSolution(
            solved_problem, debug=True, ndigits=ndigits
        )

        savepath = os.path.join(
            solution_setpath, f"{validated_problem.name}.pkl.gz"
        )
        SaveProblem(savepath, validated_problem)

    exit()



# =======================
# Main solve logic
# =======================
def Main(config: dict):
    print(config)

    PROBLEM_SETNAME = config["PROBLEM_SETNAME"]
    PROBLEM_SETPATH = os.path.join(
        "./data/multi_1/problems", PROBLEM_SETNAME
    )
    problem_set = RecurseListDir(PROBLEM_SETPATH, ["*.pkl.gz"])

    SOLVER = str(config["SOLVER"]).split("@")
    timelimit = config["TIMELIMIT"]
    ndigits = config["NDIGITS"]

    q = IterToQueue(problem_set)

    match SOLVER[0]:
        case "QL_PER_PHY":
            from Solvers.QLearn import Solver

            WEIGHT_DIR = SOLVER[1]

            SOLUTION_SETPATH = os.path.join(
                "./data/multi_1/solutions",
                f"{PROBLEM_SETNAME}@QL_PER_PHY",
            )
            CleanDir(SOLUTION_SETPATH)

            LOG_SETPATH = os.path.join(
                "./data/multi_1/logs",
                f"{PROBLEM_SETNAME}@QL_PER_PHY",
            )
            CleanDir(LOG_SETPATH)

            args = (
                q,
                Solver,
                WEIGHT_DIR,
                SOLUTION_SETPATH,
                LOG_SETPATH,
                timelimit,
                ndigits,
            )

            MultiProcessing(
                RLSolvePerPhyWorker,
                args,
                4,
            )

        case "QL_CLC_MULTI":
            from Solvers.QLearn_CLC import Solver

            WEIGHT_DIR = SOLVER[1]

            SOLUTION_SETPATH = os.path.join(
                "./data/multi_1/solutions",
                f"{PROBLEM_SETNAME}@QL_CLC_MULTI",
            )
            CleanDir(SOLUTION_SETPATH)

            LOG_SETPATH = os.path.join(
                "./data/multi_1/logs",
                f"{PROBLEM_SETNAME}@QL_CLC_MULTI",
            )
            CleanDir(LOG_SETPATH)

            args = (
                q,
                Solver,
                WEIGHT_DIR,
                SOLUTION_SETPATH,
                LOG_SETPATH,
                timelimit,
                ndigits,
            )

            MultiProcessing(
                RLSolveQLCLCMultiWorker,
                args,
                4,
            )

        case _:
            raise Exception(f"[Invalid solver] {SOLVER[0]}")



# =======================
# Multiprocess config runner
# =======================
def MpWorker(queue: mp.Queue):
    while queue.qsize():
        item = queue.get()
        Main(item)
    exit()


if __name__ == "__main__":
    mp.set_start_method("spawn")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        default="./configs/SolveSettings/dummy_multi.yaml",
    )
    args = parser.parse_args()

    config_list = ConfigParser(args.config)
    q = IterToQueue(config_list)

    MultiProcessing(MpWorker, (q,), 2)
