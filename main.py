from simulation import Simulation
from agent import Agent
from helper import plot
import time
import datetime


def train(existing_model_file):
  # todo: move all before loop inside truck
  # todo: in loop train each object
  plot_scores = []
  plot_mean_scores = []
  total_score = 0
  best_score = 0
  agent = Agent(existing_model_file)
  simulation = Simulation()
  started_at = time.time()
  print('Started at', datetime.datetime.now())
  while True:
    actors = simulation.get_actors()
    for actor in actors:
      # get old state
      state_old = actor.get_state()

      # get move
      final_move = agent.get_action_for_training(state_old)
      # final_move = agent.get_predicted_action(state_old)

      # perform move and get new state
      reward, done, score = simulation.make_step(final_move)
      state_new = actor.get_state()

      agent.train_short_memory(state_old, final_move, reward, state_new, done)

      agent.remember(state_old, final_move, reward, state_new, done)

      if done:
        # train long memory (experience), plot result
        simulation.reset()
        agent.simulations_number += 1
        agent.train_long_memory()

        if score >= best_score:
          best_score = score
          agent.model.save()

        seconds = (time.time() - started_at)
        mins = '{:10.2f}'.format(seconds / 60)
        print('Simulation', agent.simulations_number, 'Score', score, 'Best score', best_score)
        print('Total duration', mins, 'm')

        plot_scores.append(score)
        total_score += score
        mean_score = total_score / agent.simulations_number
        plot_mean_scores.append(mean_score)
        plot(plot_scores, plot_mean_scores)
      # time.sleep(0.5)

def work(existing_model_file):
  agent = Agent(existing_model_file)
  simulation = Simulation()
  print('Started at', datetime.datetime.now())
  iter = 0
  while True:
    actors = simulation.get_actors()
    for actor in actors:

      # get old state
      state_old = actor.get_state()

      # get move
      final_move = agent.get_predicted_action(state_old)

      # todo somehow apply different steps from multiple actors
      # perform move and get new state
      reward, done, score = simulation.make_step(final_move)
      iter += 1
      print('score', score)



if __name__ == '__main__':
  # train(None)
  train(existing_model_file = './model_rocks_best_30.pth')
  # work(existing_model_file='model_450_iter.pth')
  # work(existing_model_file='model_15_inputs_251_iter.pth')
