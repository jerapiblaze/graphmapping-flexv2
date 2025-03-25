import torch
import pickle
import gzip as gz
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors as colors
from collections import defaultdict


from env3k import RLen3

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
        # print ("for check: ", self.epsilon)
        if np.random.uniform(0, 1) < self.epsilon and trainmode: 
            return self.action_space.sample()
        else:
            return np.argmax(self.q_table[state])

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        new_q = (1-self.learning_rate ) * self.q_table[state][action] + self.learning_rate * (reward + self.discount_factor * self.q_table[next_state][best_next_action])
        self.q_table[state][action] = new_q

    def end_episode(self, reset=False):
        if reset:
            self.epsilon = self.epsilon_max
        else:
            # print("self.epsilon_decay: ", self.epsilon_decay)
            new_epsilon = self.epsilon * self.epsilon_decay
            # print("new_epsilon", new_epsilon)
            # print("self.epsilon_min", self.epsilon_min)
            self.epsilon = max(new_epsilon, self.epsilon_min)
            # print("self.epsilon: ", self.epsilon)
        # print("for check 2:", self.epsilon)

    def plot_duration(self, show_result=False):
        duration_t = torch.tensor(self.episode_duration, dtype=torch.float)
        
        if show_result:
            plt.title("QL-Result")
        else:
            plt.clf()
            plt.title("QL-Training")
        
        plt.xlabel("Episode")
        plt.ylabel("Cumulative reward")
        plt.plot(duration_t.numpy(), color='silver')  # Vẽ phần thưởng tích lũy

        # Cập nhật cửa sổ trung bình động là 10 tập
        window_size = 100  
        if len(duration_t) >= window_size:
            means = duration_t.unfold(0, window_size, 1).mean(1).view(-1)
            plt.plot(range(window_size - 1, len(duration_t)), means.numpy(), color='k')  # Vẽ đường trung bình động màu đen
        
        plt.pause(0.001)

        if IS_IPYTHON:
            if not show_result:
                display.display(plt.gcf())
                display.clear_output(wait=True)
            else:
                display.display(plt.gcf())  
        

def TrainAgent(agent: QLearningAgent, env: RLen3, nepisode: int, verbose: bool = False, liveview: bool = False) -> tuple[QLearningAgent, list[float]]:
    reward_list = []
    # reset=True
    agent.epsilon = 1
    # print("aloooooo")

    for ep in range(nepisode):
        # print ("epersoi: ",ep)
        print("épsilon: ",agent.epsilon)
        obs, info = env.reset()
        terminated = False
        truncated = False
        rw_list = []
        while not terminated and not truncated:
            action = agent.choose_action(obs)
            # print("bf: ",action)
            next_obs, reward, terminated, truncated, info = env.step(action)
            # print("info: ",next_obs, reward, terminated, truncated, info)
            if reward == 0:
                action = 0 
            # print("af: ",action)
            
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
            agent.plot_duration()
        # print("end of 1 eps \n")
    plt.savefig("q_learning_training_result.png", dpi=300)
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