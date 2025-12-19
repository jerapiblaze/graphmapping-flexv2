import os
from time import time
from multiprocessing import Pool, cpu_count

import FlexSliceMappingProblem
import Solvers.QLearn as QLearn
from utilities.config import ConfigParser
from utilities.dir import RecurseListDir, CleanDir

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def TrainOneProblem(args):
    """
    Train Q-learning on exactly ONE network (ONE .pkl.gz file)
    """
    problem_path, config = args

    problem = FlexSliceMappingProblem.LoadProblem(problem_path)
    env = QLearn.env.RLen3(problem.PHY, problem.SLICES_SET)

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

    start_time = time()
    trained_agent, rewards = QLearn.agent.TrainAgent(
        agent,
        env,
        config["N_EPISODES"],
        config["VERBOSE"],
        config["LIVEVIEW"],
    )
    train_time = time() - start_time

    basename = os.path.basename(problem_path).replace(".pkl.gz", "")
    safe_name = f"{basename}_a{config['ALPHA']}_g{config['GAMMA']}_n{config['N_EPISODES']}"

    save_dir = "./data/__internals__/QL_multi"
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

    print(f"[DONE] {basename} | {train_time:.2f}s")


def Main(config):
    print(config)

    if config["DELETE_OLD_DATA"]:
        CleanDir("./data/__internals__/QL_multi")

    problem_dir = f"./data/multi_1/problems/{config['PROBLEM_SETNAME']}"
    problem_path_list = RecurseListDir(problem_dir, ["*.pkl.gz"])

    n_proc = min(10, cpu_count())
    print(f"Running with {n_proc} parallel processes")

    with Pool(processes=n_proc) as pool:
        pool.map(
            TrainOneProblem,
            [(p, config) for p in problem_path_list],
        )


if __name__ == "__main__":
    config_list = ConfigParser("./configs/QLSettings/dummy.yaml")
    for config in config_list:
        Main(config)
