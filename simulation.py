import sys
import threading as th
import pygame
from pygame.locals import KEYDOWN, K_q, K_r, K_ESCAPE
import constants as const
from dump_truck import DumpTruck
from blocks import Ore, Rock
import time
from utils import Point
import random

pygame.init()
GRID_CELLS = const.GRID_CELLS
GRID_ORIGIN = const.GRID_ORIGIN
CELL_SIZE = const.CELL_SIZE

LINE_WIDTH = const.LINE_WIDTH
LINE_COLOR = const.LINE_COLOR
SPEED = 70


class Simulation:
  def __init__(self):
    self.display = pygame.display.set_mode(const.SCREENSIZE)
    pygame.display.set_caption('Simulation')
    self.clock = pygame.time.Clock()
    self.reset()

  
  def reset(self):
    # TODO: move to truck after train check
    self.score = 0
    self.running = False
    self.ores_location = []
    self.map = self.generate_map()
    self.place_ore()
    self.frame_iteration = 0

  def make_step(self, action):
    self.frame_iteration += 1
    # 1. check user input
    self.check_input()

    # 2. move (update state of objects)
    for row in range(len(self.map)):
      for column in range(len(self.map[row])):
          obj = self.map[column][row]
          if obj:
            obj.update(action)

    # todo: loop over all objects
    # 3. check if simulation is finished
    # temp check of finished for check training, todo: change this after train check
    # temp calc of reward for check training, todo: change this after train check
    reward = 0
    finished = False
    # meet the borders, TODO make depends on how big score (how far simulation goes)
    if self.get_truck().is_collision(None) or self.frame_iteration > 100:
      finished = True
      reward = -10
      reason = 'iter max' if self.frame_iteration > 200 else 'hit border'
      print('Reason', reason, 'iterations', self.frame_iteration)
      return reward, finished, self.score
    if self.score > 100:
      finished = True
      reward = 10
      reason = 'score max'
      print('Reason', reason, 'iterations', self.frame_iteration)
      return reward, finished, self.score

    # 4. place new ore
    # todo make communication between trucks, and choose closer ore (on path)
    # todo: now truck is ON ore, change to being near the ore
    if self.get_truck().X == self.get_ore().X and self.get_truck().Y == self.get_ore().Y:
      self.score += 1
      reward = 10
      self.frame_iteration = 0
      self.place_ore()

    self.update_ui()
    self.clock.tick(SPEED)
    return reward, finished, self.score
    

  def generate_map(self):
    cellMAP = []
    for i in range(GRID_CELLS):
      row = []
      for k in range(GRID_CELLS):
        row.append(None)
      cellMAP.append(row)
    self.truck = DumpTruck(5, 7)
    cellMAP[5][7] = self.truck

    return cellMAP

  def place_ore(self):
    if len(self.ores_location) > 0:
      curr_pos = self.ores_location[0]
      self.map[curr_pos.x][curr_pos.y] = None

    truck = self.get_truck()
    x = truck.X
    y = truck.Y
    while x == truck.X and y == truck.Y:
      x = random.randint(0, GRID_CELLS - 1)
      y = random.randint(0, GRID_CELLS - 1)

    self.map[x][y] = Ore(x, y)
    self.ores_location = [Point(x, y)]
    self.get_truck().set_ores_location(self.ores_location)


  # temp method for check training, todo: remove this after train check
  def get_truck(self):
    return self.truck

  # temp method for check training, todo: remove this after train check
  def get_ore(self):
    curr_pos = self.ores_location[0]
    ore = self.map[curr_pos.x][curr_pos.y]
    return ore
    # return self.map[15][15]


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
