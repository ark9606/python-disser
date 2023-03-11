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


def main():
  pygame.init()

  simulation = Simulation()
  # simulation.run()
  while True:
    finished, score = simulation.make_step()
      
    if finished == True:
        break
  
  pygame.quit()


if __name__ == '__main__':
    main()