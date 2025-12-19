import FlexSliceMappingProblem
import Solvers.QLearn_CLC as QLearn
import gymnasium as gym
from utilities.config import ConfigParser
from utilities.dir import RecurseListDir, CleanDir
from time import time

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def Main(config):
    print(config)
    if config["DELETE_OLD_DATA"]:
        CleanDir("./data/__internals__/QL_CLC")
    problemset_name = config["PROBLEM_SETNAME"]
    save_reward = config["SAVE_REWARDS"]
    liveview, verbose = config["LIVEVIEW"], config["VERBOSE"]
    problem_dir = os.path.join(f"./data/problems/{problemset_name}")
    n_episode = config["N_EPISODES"]
    alpha = config["ALPHA"]
    gamma = config["GAMMA"]
    epsilon_start, epsilon_end, epsilon_decay = config["EPSILON_START"], config["EPSILON_END"], config["EPSILON_DECAY"]
    big_m, beta = config["BIG_M"], config["BETA"]
    problem_path_list = RecurseListDir(problem_dir, ["*.pkl.gz"])
    for problem_path in problem_path_list:
        problem = FlexSliceMappingProblem.LoadProblem(problem_path)
        env = QLearn.env.RLen3(problem.PHY, problem.SLICES_SET)
        # env = QLearn.env.StaticMapping2Env(problem.PHY, problem.SFC_SET, {"node_req": "req", "link_req": "req", "node_cap": "cap", "link_cap": "cap"}, big_m, beta)
        agent = QLearn.agent.QLearningAgent(env.action_space, env.observation_space, env.observation_space_size, env.action_space_size,
                                        learning_rate=alpha, discount_factor=gamma, epsilon_max=epsilon_start, 
                                        epsilon_min=epsilon_end, epsilon_decay=epsilon_decay)
        # ----- measure training time -----
        start_time = time()
        trained_agent, rewards = QLearn.agent.TrainAgent(agent, env, n_episode, verbose, liveview)
        train_time = time() - start_time
        print(f"Training time for {problem.name}: {train_time:.2f} seconds")
        safe_name = f"{problem.name}_n{problemset_name}_a{alpha}_g{gamma}_n{n_episode}envNew"
        model_save_path = os.path.join("./data/__internals__/QL_CLC",  f"{safe_name}.pkl.gz")
        QLearn.agent.SaveAgent(model_save_path, trained_agent)
        if not save_reward:
            continue
        rewards_save_path = os.path.join("./data/__internals__/QL_CLC", f"{safe_name}_rewards.csv")
        #rewards_save_path = os.path.join("./data/__internals__/QL", f"{problem.name}_a{alpha}_g{gamma}"_rewards.csv")
        print("done")
        with open(rewards_save_path, "wt") as f:
            f.write("ep, reward\n")
            for r in rewards:
                f.write(f"{r[0]}, {r[1]}\n")


if __name__=="__main__":
    config_list = ConfigParser("./configs/QLSettings/dummy.yaml")
    for config in config_list:
        Main(config)