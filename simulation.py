import sys
import threading as th
import pygame
from pygame.locals import KEYDOWN, K_q, K_r, K_ESCAPE
import constants as const
from dump_truck import DumpTruck
from blocks import Ore, Rock
import time
from utils import Point

pygame.init()
GRID_CELLS = const.GRID_CELLS
GRID_ORIGIN = const.GRID_ORIGIN
CELL_SIZE = const.CELL_SIZE

LINE_WIDTH = const.LINE_WIDTH
LINE_COLOR = const.LINE_COLOR
SPEED = 10


class Simulation:
  def __init__(self):
    self.display = pygame.display.set_mode(const.SCREENSIZE)
    pygame.display.set_caption('Simulation')
    self.clock = pygame.time.Clock()
    self.reset()
  
  def reset(self):
    self.score = 0
    self.running = False
    self.map = self.get_map()
    self.frame_iteration = 0

  def make_step(self, action):
    self.check_input()

    for row in range(len(self.map)):
      for column in range(len(self.map[row])):
          obj = self.map[column][row]
          if obj:
            obj.update(action)

    reward = 0
    # TODO calc reward
    # TODO check if simulation is over

    self.update_ui()
    self.clock.tick(SPEED)
    finished = False
    return reward, finished, self.score
    

  def get_map(self):
    cellMAP = []
    for i in range(GRID_CELLS):
      row = []
      for k in range(GRID_CELLS):
        row.append(None)
      cellMAP.append(row)
    truck = DumpTruck(5, 7)
    truck.set_data(GRID_ORIGIN)
    cellMAP[5][7] = truck

    # truck1 = DumpTruck(10, 8)
    # truck1.set_data(GRID_ORIGIN)
    # cellMAP[10][8] = truck1

    cellMAP[15][15] = Ore(15, 15)
    cellMAP[3][3] = Rock(3, 3)

    # truck.set_map(cellMAP)
    truck.set_ores_location([Point(15, 15)])
    return cellMAP

  def update_ui(self):
    self.display.fill(const.GREY)
    self.draw_grid(GRID_ORIGIN, const.GRID_SIZE, GRID_CELLS)
    self.draw_objects()
    pygame.display.flip()

  def draw_objects(self):
    for row in range(GRID_CELLS):
      for column in range(GRID_CELLS):
        obj = self.map[column][row]
        if obj:
          obj.draw(self.display)

  def draw_grid(self, origin, gridWH, cells):

    CONTAINER_WIDTH_HEIGHT = gridWH
    cont_x, cont_y = origin

    # DRAW Grid Border:
    # TOP LEFT TO RIGHT
    pygame.draw.line(
      self.display, LINE_COLOR,
      (cont_x, cont_y),
      (CONTAINER_WIDTH_HEIGHT + cont_x, cont_y), LINE_WIDTH)
    # # BOTTOM LEFT TO RIGHT
    pygame.draw.line(
      self.display, LINE_COLOR,
      (cont_x, CONTAINER_WIDTH_HEIGHT + cont_y),
      (CONTAINER_WIDTH_HEIGHT + cont_x,
       CONTAINER_WIDTH_HEIGHT + cont_y), LINE_WIDTH)
    # # LEFT TOP TO BOTTOM
    pygame.draw.line(
      self.display, LINE_COLOR,
      (cont_x, cont_y),
      (cont_x, cont_y + CONTAINER_WIDTH_HEIGHT), LINE_WIDTH)
    # # RIGHT TOP TO BOTTOM
    pygame.draw.line(
      self.display, LINE_COLOR,
      (CONTAINER_WIDTH_HEIGHT + cont_x, cont_y),
      (CONTAINER_WIDTH_HEIGHT + cont_x,
       CONTAINER_WIDTH_HEIGHT + cont_y), LINE_WIDTH)

    cellSize = CELL_SIZE

    # VERTICAL DIVISIONS: (0,1,2) for grid(3) for example
    for x in range(cells):
      pygame.draw.line(
           self.display, LINE_COLOR,
           (cont_x + (cellSize * x), cont_y),
           (cont_x + (cellSize * x), CONTAINER_WIDTH_HEIGHT + cont_y), LINE_WIDTH)
    # HORIZONTAl DIVISIONS
      pygame.draw.line(
          self.display, LINE_COLOR,
          (cont_x, cont_y + (cellSize*x)),
          (cont_x + CONTAINER_WIDTH_HEIGHT, cont_y + (cellSize*x)), LINE_WIDTH)
  
  def check_input(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT or (event.type == KEYDOWN and (event.key == K_q or event.key == K_ESCAPE)):
        self.running = False
        pygame.quit()
        sys.exit()
      elif event.type == KEYDOWN and event.key == K_r:
        self.reset()

  # def run(self):
  #   self.running = True
  #   self.logic_thread = th.Thread(target=self.run_logic, name='logic_thread')
  #   self.logic_thread.start()
  #
  #   while self.running:
  #     self.check_input()
  #     self.update_ui()
  #
  # def run_logic(self):
  #   iterations = 0
  #   while self.running:
  #     time.sleep(0.2)
  #
  #     for row in range(GRID_CELLS):
  #       for column in range(GRID_CELLS):
  #           obj = self.map[column][row]
  #           if obj:
  #             obj.update()
  #     iterations += 1

        