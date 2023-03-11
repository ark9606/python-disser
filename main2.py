import sys
import pygame
from pygame.locals import KEYDOWN, K_q, K_ESCAPE
import numpy as np
import time
import threading as th
import constants as const
import dump_truck
import blocks
import time
from simulation import Simulation

BLACK = const.BLACK
GREY = const.GREY
CELL_SIZE = const.CELL_SIZE

LINE_WIDTH = const.LINE_WIDTH
LINE_COLOR = const.LINE_COLOR


GRID_CELLS = const.GRID_CELLS
GRID_ORIGIN = const.GRID_ORIGIN
# GRID_SIZE = GRID_CELLS * CELL_SIZE
# GRID_ORIGIN = (WIDTH / 2 - GRID_SIZE / 2, WINDOW_MARGIN)
CELL_MARGIN = const.CELL_MARGIN

simulation_running = True

cellMAP = []


_VARS = {
  'surf': False,
  'simulationThread': False,
  'gridCells': GRID_CELLS,
  'map': cellMAP,
}

def run_simulation(ex):
  iterations = 0
  while simulation_running:
    time.sleep(0.1)
    checkEvents()

    for row in range(GRID_CELLS):
      for column in range(GRID_CELLS):
          obj = _VARS['map'][column][row]
          if obj:
            obj.update()
    iterations += 1
    


def main():
  pygame.init()

  simulation = Simulation()

  simulation.run()
  # game loop
  # while True:
  #   simulation_over, score = simulation.make_step()
      
  #   if simulation_over == True:
  #       break
      
  # print('Final Score', score)
  pygame.quit()




if __name__ == '__main__':
    main()