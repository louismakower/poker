from rl_utils import DQN, ReplayBuffer, greedy_action, epsilon_greedy, update_target, loss
import torch
import torch.optim as optim
from environment import Environment
from player import RLPlayer

def decay_epsilon(epsilon, episode_number, start_decay, end_decay, E, min_epsilon, initial_epsilon):
    decay_constant = (initial_epsilon - min_epsilon) / (E*(end_decay - start_decay))
    if episode_number > start_decay*E:
        epsilon = max(min_epsilon, epsilon - decay_constant)
    return epsilon

NUM_RUNS = 10 # this was 10

A = 70 # size of hidden layers
B = 1 # num hidden layers
C = 0.005 # learning rate in gradient descent
D = 10000 # size of replay buffer
E = 300 # num episodes
F = 1 # initial epsilon
G = 1 # not sure - just seems to scale rewards
H = 72 # batch size
I = 10 # how many steps before we update the target policy thing

start_decay = 0.
end_decay = 0.5

min_epsilon = 0.

runs_results = []
policy_nets = []

initial_money = 100

for run in range(NUM_RUNS):
    print(f"Starting run {run + 1} of {NUM_RUNS}")
    layers = [15] + [A] * B + [1]
    policy_net = DQN(layers)
    target_net = DQN(layers)
    update_target(target_net, policy_net)
    target_net.eval()

    rl_player = RLPlayer('RL player', initial_money, policy_net)
    rl_env = Environment(rl_player, 3, initial_money)

    optimizer = optim.SGD(policy_net.parameters(), lr=C)
    memory = ReplayBuffer(D)

    steps_done = 0

    epsilon = F
    epsilons = []

    episode_durations = []

    for i_episode in range(E):
        if (i_episode + 1) % 50 == 0:
            print("episode ", i_episode + 1, "/ ", E)

        state = rl_env.reset()
        # print(epsilon)

        epsilon = decay_epsilon(epsilon, i_episode, start_decay, end_decay, E, min_epsilon, F)
        epsilons.append(epsilon)
        terminated = False
        t = 0
        while not terminated:
            # Select and perform an action
            action = rl_player.place_bet(state)
            action = [float(num) if not num is None else 0. for num in action]

            state, reward, terminated = rl_env.step(action[0], action[1])
            reward = torch.tensor([reward]) / G
            action = torch.tensor([action])
            next_state = torch.tensor(state).reshape(-1).float()

            memory.push([state, action, next_state, reward, torch.tensor([terminated])])

            # Move to the next state
            state = next_state

            # Perform one step of the optimization (on the policy network)
            if not len(memory.buffer) < H:
                transitions = memory.sample(H)
                state_batch, action_batch, nextstate_batch, reward_batch, dones = (torch.stack(x) for x in
                                                                                   zip(*transitions))
                # Compute loss
                mse_loss = loss(policy_net, target_net, state_batch, action_batch, reward_batch, nextstate_batch, dones)
                # Optimize the model
                optimizer.zero_grad()
                mse_loss.backward()
                optimizer.step()

            if terminated:
                # if done:
                episode_durations.append(t + 1)
            t += 1
            steps_done += 1
        # Update the target network, copying all weights and biases in DQN
        if i_episode % I == 0:
            update_target(target_net, policy_net)

    runs_results.append(episode_durations)
    policy_nets.append(policy_net)
print('Complete')