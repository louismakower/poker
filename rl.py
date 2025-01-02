from rl_utils import DQN, ReplayBuffer, update_target, loss
import torch
import torch.optim as optim
from environment import Environment
from player import RLPlayer
import matplotlib.pyplot as plt
import numpy as np
import pickle

def decay_epsilon(epsilon, episode_number, start_decay, end_decay, E, min_epsilon, initial_epsilon):
    decay_constant = (initial_epsilon - min_epsilon) / (E*(end_decay - start_decay))
    if episode_number > start_decay*E:
        epsilon = max(min_epsilon, epsilon - decay_constant)
    return epsilon

NUM_RUNS = 10 # this was 10

# hyperparams
hidden_layer_size = 70
num_hidden_layers = 1
lr = 0.005
replay_buffer_size = 10000
total_num_episodes = 500
initial_epsilon = 1
reward_scaler = 1
batch_size = 72
steps_to_update_target_policy = 500
start_decay = 0.
end_decay = 0.8
min_epsilon = 0.

runs_results = []
policy_nets = []

initial_money = 100

for run in range(NUM_RUNS):
    print(f"Starting run {run + 1} of {NUM_RUNS}")
    layers = [15] + [hidden_layer_size] * num_hidden_layers + [10]
    policy_net = DQN(layers)
    target_net = DQN(layers)
    update_target(target_net, policy_net)
    target_net.eval()

    rl_player = RLPlayer('RL player', initial_money, policy_net)
    rl_env = Environment(rl_player, 3, initial_money, verbose=0, game_length=50)

    optimizer = optim.SGD(policy_net.parameters(), lr=lr)
    memory = ReplayBuffer(replay_buffer_size)

    steps_done = 0

    epsilon = initial_epsilon
    epsilons = []

    episode_return = []

    for i_episode in range(total_num_episodes):
        if (i_episode + 1) % 50 == 0:
            print("episode ", i_episode + 1, "/ ", total_num_episodes)

        state = rl_env.reset()

        epsilon = decay_epsilon(epsilon, i_episode, start_decay, end_decay, total_num_episodes, min_epsilon, initial_epsilon)
        epsilons.append(epsilon)
        terminated = False
        t = 0
        while not terminated:
            # print(f"RL player has {rl_player.money}")
            # Select and perform an action
            action = rl_player.epsilon_greedy(state, epsilon)
            bet, amount = rl_player.place_bet(action)

            state, reward, terminated = rl_env.step(bet, amount)
            reward = torch.tensor([reward]) / reward_scaler
            action = torch.tensor([action])
            next_state = torch.tensor(state).reshape(-1).float()

            memory.push([state, action, next_state, reward, torch.tensor([terminated])])

            # Move to the next state
            state = next_state

            # Perform one step of the optimization (on the policy network)
            if not len(memory.buffer) < batch_size:
                transitions = memory.sample(batch_size)
                state_batch, action_batch, nextstate_batch, reward_batch, dones = (torch.stack(x) for x in
                                                                                   zip(*transitions))
                # Compute loss
                mse_loss = loss(policy_net, target_net, state_batch, action_batch, reward_batch, nextstate_batch, dones)
                # Optimize the model
                optimizer.zero_grad()
                mse_loss.backward()
                optimizer.step()

            if terminated:
                episode_return.append(rl_player.money)
            t += 1
            steps_done += 1
            # Update the target network, copying all weights and biases in DQN

            if steps_done % steps_to_update_target_policy == 0:
                update_target(target_net, policy_net)

    runs_results.append(episode_return)
    policy_nets.append(policy_net)
    # with open(f'dqn{run}.pkl', 'wb') as f:
    #     pickle.dump(policy_net, f)
print('Complete')

# Plotting the learning curve
# Placeholder plot, you are free to modify it
num_episodes = len(runs_results[0])

results = torch.tensor(runs_results)
means = results.float().mean(0)
stds = results.float().std(0)

# for i in range(len(results)):
    # print(results[i])

fig, ax = plt.subplots()
ax.plot(torch.arange(num_episodes), means, label=f'Mean ({NUM_RUNS} runs)')
plt.ylabel("Return")
plt.xlabel("Episode number")
ax.fill_between(np.arange(num_episodes), means, means+stds, alpha=0.3, color='b', label=f'Standard deviation {NUM_RUNS} runs)')
ax.fill_between(np.arange(num_episodes), means, means-stds, alpha=0.3, color='b')
plt.legend()
plt.show()