import pygame
from simulation import Simulation


def main():
  pygame.init()

  simulation = Simulation()
  # simulation.run()
  while True:
    reward, finished, score = simulation.make_step(1)
      
    if finished == True:
        break
  
  pygame.quit()


if __name__ == '__main__':
    main()