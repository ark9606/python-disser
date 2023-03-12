import torch
import random
from collections import deque
from simulation import Simulation
from model import LinearQNet, QTrainer
from helper import plot
import time

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001 # learning rate

class Agent:
  def __init__(self):
    self.simulations_number = 0
    self.epsilon = 0 # randomness
    self.gamma = 0.9 # discount rate
    self.memory = deque(maxlen=MAX_MEMORY)
    self.model = LinearQNet(11, 256, 3) # 11 states, 3 actions
    self.trainer = QTrainer(self.model, learning_rate = LR, gamma = self.gamma)

  def get_state(self, simulation):
    # TODO get state inside truck
    return simulation.get_truck().get_state()

  def remember(self, state, action, reward, next_state, done):
    # remove from left, if maxlen exceeded
    self.memory.append((state, action, reward, next_state, done))

  def train_long_memory(self):
    mini_sample = []
    if len(self.memory) > BATCH_SIZE:
      mini_sample = random.sample(self.memory, BATCH_SIZE)
    else:
      mini_sample = self.memory

    states, actions, rewards, next_states, dones = zip(*mini_sample)
    self.train_short_memory(states, actions, rewards, next_states, dones)

  def train_short_memory(self, state, action, reward, next_state, done):
    self.trainer.train_step(state, action, reward, next_state, done)

  def get_action(self, state):
    # random moves: tradeoff exploration / exploitation
    self.epsilon = 80 - self.simulations_number # as more simulations -> less epsilon -> less random moves
    final_move = [0, 0, 0]
    if random.randint(0, 200) < self.epsilon:
      ind = random.randint(0, 2)
      final_move[ind] = 1
    else:
      state0 = torch.tensor(state, dtype = torch.float)
      prediction = self.model(state0) # predict
      ind = torch.argmax(prediction).item()
      final_move[ind] = 1
    return final_move




def train():
  plot_scores = []
  plot_mean_scores = []
  total_score = 0
  best_score = 0
  agent = Agent()
  simulation = Simulation()
  while True:
    # get old state
    state_old = agent.get_state(simulation)

    # get move
    final_move = agent.get_action(state_old)

    # perform move and get new state
    reward, done, score = simulation.make_step(final_move)
    state_new = agent.get_state(simulation)

    agent.train_short_memory(state_old, final_move, reward, state_new, done)

    agent.remember(state_old, final_move, reward, state_new, done)

    if done:
      # train long memory (experience), plot result
      simulation.reset()
      agent.simulations_number += 1
      agent.train_long_memory()

      if score > best_score:
        best_score = score
        agent.model.save()

      print('Simulation', agent.simulations_number, 'Score', score, 'Best score', best_score)

      plot_scores.append(score)
      total_score += score
      mean_score = total_score / agent.simulations_number
      plot_mean_scores.append(mean_score)
      plot(plot_scores, plot_mean_scores)
    # time.sleep(0.5)



if __name__ == '__main__':
  train()
