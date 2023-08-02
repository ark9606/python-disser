import torch
import random
from collections import deque
from model import LinearQNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001 # learning rate

class Agent:
  def __init__(self, existing_model_file):
    self.simulations_number = 0
    self.epsilon = 0 # randomness
    self.gamma = 0.95 # discount rate
    self.memory = deque(maxlen=MAX_MEMORY)
    self.model = LinearQNet(11, 256, 3, existing_model_file) # 15 states, 3 actions
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

  def get_action_for_training(self, state):
    # random moves: tradeoff exploration / exploitation
    self.epsilon = 80 - self.simulations_number # as more simulations -> less epsilon -> less random moves
    final_move = [0, 0, 0]
    if random.randint(0, 200) < self.epsilon:
      ind = random.randint(0, 2)
      final_move[ind] = 1
    else:
      final_move = self.get_predicted_action(state)
    return final_move

  def get_predicted_action(self, state):
    final_move = [0, 0, 0]
    state0 = torch.tensor(state, dtype=torch.float)
    prediction = self.model(state0)  # predict
    ind = torch.argmax(prediction).item()
    final_move[ind] = 1
    return final_move
