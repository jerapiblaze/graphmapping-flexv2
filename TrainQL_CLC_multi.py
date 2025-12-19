import os
from time import time
from multiprocessing import Pool, cpu_count

import FlexSliceMappingProblem
import Solvers.QLearn_CLC as QLearn
from utilities.config import ConfigParser
from utilities.dir import RecurseListDir, CleanDir

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def TrainOneProblem_CLC(args):
    """
    Train QL + CLC on exactly ONE problem
    """
    problem_path, config = args

    problem = FlexSliceMappingProblem.LoadProblem(problem_path)

    # ----- QL+CLC ENV -----
    env = QLearn.env.RLen3(problem.PHY, problem.SLICES_SET)

    # ----- QL+CLC AGENT -----
    agent = QLearn.agent.QLearningAgent(
        env.action_space,
        env.observation_space,
        env.observation_space_size,
        env.action_space_size,
        learning_rate=config["ALPHA"],
        discount_factor=config["GAMMA"],
        epsilon_max=config["EPSILON_START"],
        epsilon_min=config["EPSILON_END"],
        epsilon_decay=config["EPSILON_DECAY"],
    )

    # ----- TRAIN -----
    start_time = time()
    trained_agent, rewards = QLearn.agent.TrainAgent(
        agent,
        env,
        config["N_EPISODES"],
        config["VERBOSE"],
        config["LIVEVIEW"],
    )
    train_time = time() - start_time

    # ----- SAVE -----
    basename = os.path.basename(problem_path).replace(".pkl.gz", "")
    safe_name = (
        f"{basename}"
        f"_a{config['ALPHA']}"
        f"_g{config['GAMMA']}"
        f"_n{config['N_EPISODES']}"
        f"_QLCLC"
    )

    save_dir = "./data/__internals__/QL_CLC_multi"
    os.makedirs(save_dir, exist_ok=True)

    QLearn.agent.SaveAgent(
        os.path.join(save_dir, f"{safe_name}.pkl.gz"),
        trained_agent,
    )

    if config["SAVE_REWARDS"]:
        with open(os.path.join(save_dir, f"{safe_name}_rewards.csv"), "w") as f:
            f.write("ep,reward\n")
            for ep, r in rewards:
                f.write(f"{ep},{r}\n")

    print(f"[DONE][QL+CLC] {basename} | {train_time:.2f}s")


def Main(config):
    print(config)

    if config["DELETE_OLD_DATA"]:
        CleanDir("./data/__internals__/QL_CLC_multi")

    problem_dir = f"./data/multi_1/problems/{config['PROBLEM_SETNAME']}"
    problem_path_list = RecurseListDir(problem_dir, ["*.pkl.gz"])

    n_proc = min(10, cpu_count())
    print(f"Running QL+CLC with {n_proc} parallel processes")

    with Pool(processes=n_proc) as pool:
        pool.map(
            TrainOneProblem_CLC,
            [(p, config) for p in problem_path_list],
        )


if __name__ == "__main__":
    config_list = ConfigParser("./configs/QLSettings/dummy.yaml")
    for config in config_list:
        Main(config)
