import torch
import pickle
import gzip as gz
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors as colors
from collections import defaultdict


from env import RLen3

# set up matplotlib
IS_IPYTHON = 'inline' in matplotlib.get_backend()
if IS_IPYTHON:
    from IPython import display
plt.ion()

class QLearningAgent:
    def __init__(self, action_space, observation_space, state_space_size, action_space_size, learning_rate=0.1, discount_factor=0.99, epsilon=0.1, epsilon_min=0.01, epsilon_decay=0.995, epsilon_max=1.0):
        self.action_space = action_space
        self.observation_space = observation_space
        self.state_space_size = state_space_size
        self.action_space_size = action_space_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.epsilon_max = epsilon_max
        self.q_table = np.random.uniform(0, 1, size=(state_space_size, action_space_size))
        self.episode_duration = []

    def choose_action(self, state, trainmode:int=True):
        if np.random.uniform(0, 1) < self.epsilon and trainmode: 
            return self.action_space.sample()
        else:
            return np.argmax(self.q_table[state])

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        new_q = (1-self.learning_rate) * self.q_table[state][action] + self.learning_rate * (reward + self.discount_factor * self.q_table[next_state][best_next_action])
        self.q_table[state][action] = new_q

    def end_episode(self, reset=False):
        if reset:
            self.epsilon = self.epsilon_max
        else:
            new_epsilon = self.epsilon * self.epsilon_decay
            self.epsilon = max(new_epsilon, self.epsilon_min)

    def plot_duration(self, show_result=False, save_path=None):
        # plt.figure(1)
        duration_t = torch.tensor(self.episode_duration, dtype=torch.float)
        if show_result:
            plt.title("QL-Result")
        else:
            plt.clf()
            plt.title("QL-Training")
        plt.xlabel("Episode")
        plt.ylabel("Cumulative reward")
        plt.plot(duration_t.numpy(), color='silver')  # plot cumulative reward
        if len(duration_t) >= 2:
            means = duration_t.unfold(0, 2, 1).mean(1).view(-1)
            means = torch.cat((torch.zeros(2), means))
            plt.plot(means.numpy(), color='k')  # plot average reward
        # plt.legend()

        # if show_result and save_path is not None:
        #     plt.tight_layout()
        #     plt.savefig(save_path)
        #     plt.close()
        #     return
        plt.pause(0.001)
        if IS_IPYTHON:
            if not show_result:
                display.display(plt.gcf())
                display.clear_output(wait=True)
            else:
                display.display(plt.gcf())
    def save_live_plot(self, filename="live_reward.png"):
        duration_t = torch.tensor(self.episode_duration, dtype=torch.float)

        plt.figure(figsize=(8,4))
        plt.clf()
        plt.title("QL Training (Live View)")
        plt.xlabel("Episode")
        plt.ylabel("Cumulative Reward")

        # draw reward curve
        plt.plot(duration_t.numpy(), color="steelblue")

        # moving average 10 windows
        if len(duration_t) >= 40:
            means = duration_t.unfold(0, 40, 1).mean(1).view(-1)
            means = torch.cat((torch.zeros(39), means))
            plt.plot(means.numpy(), color="k")

        # plt.legend()
        plt.tight_layout()
        plt.savefig(filename)      # overwrite file
        plt.close()                # close fig to avoid memory leak

def TrainAgent(agent: QLearningAgent, env: RLen3, nepisode: int, verbose: bool = False, liveview: bool = False) -> tuple[QLearningAgent, list[float]]:
    reward_list = []

    for ep in range(nepisode):
        obs, info = env.reset()
        terminated = False
        truncated = False
        rw_list = []
        while not terminated and not truncated:
            action = agent.choose_action(obs)
            next_obs, reward, terminated, truncated, info = env.step(action)
            if reward == 0:
                action = 0 
            rw_list.append(reward)
            agent.update_q_table(obs, action, reward, next_obs)
            obs = next_obs
        if verbose:
            print(f"ep_{ep}: {info['message']} {obs} {info}")
        agent.end_episode()
        rw = sum(rw_list)  # cumulative reward
        reward_list.append((ep, rw))
        if liveview:
            agent.episode_duration.append(rw)
            # agent.plot_duration(show_result=False, save_path="final_reward.png")
        # if liveview and (ep % 5 == 0):
        #     agent.save_live_plot("live_reward.png")

        if verbose:
            print(f"ep {ep}: reward={rw}")

    # save final
    if liveview:
        agent.save_live_plot("live_reward_final.png")
    return agent, reward_list

def SaveAgent(path:str, agent:QLearningAgent):
    with gz.open(path, "wb") as f:
        pickle.dump(agent, f)
    return

def LoadAgent(path:str) -> QLearningAgent:
    agent = None
    with gz.open(path, "rb") as f:
        agent = pickle.load(f)
    return agent