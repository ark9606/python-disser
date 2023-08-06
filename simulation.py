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
SPEED = 120


MAP_ORES_COUNT = 1
MAP_ROCKS_COUNT = 5
MAP_TRUCKS_COUNT = 1

class Simulation:
  def __init__(self):
    self.display = pygame.display.set_mode(const.SCREENSIZE)
    pygame.display.set_caption('Simulation')
    self.clock = pygame.time.Clock()
    self.actors = []
    self.simulation_running = False
    self.ores_location = [] # ores in all simulation
    self.frame_iteration = 0
    self.map = None
    self.reset()

  
  def reset(self):
    self.actors = []
    self.simulation_running = False
    self.ores_location = [] # ores in all simulation
    self.frame_iteration = 0
    self.map = self.generate_map()
    self.place_ore()

  def make_step(self, action):
    self.frame_iteration += 1
    # 1. check user input
    self.check_input()


    # now it works only for one truck, change to accumulate res from different trucks
    reward = 0
    finished = False
    score = 0

    # 2. move (update state of objects)
    for row in range(len(self.map)):
      for column in range(len(self.map[row])):
          obj = self.map[column][row]
          if isinstance(obj, DumpTruck):
            obj.perform_action(action)
            reward, finished, score = obj.calc_score(self.frame_iteration)

    if finished:
      return reward, finished, score

    if reward > 0:
      self.frame_iteration = 0
      self.place_ore()

    self.update_ui()
    self.clock.tick(SPEED)
    return reward, finished, score
    

  def generate_map(self):
    cell_map = []
    for i in range(GRID_CELLS):
      row = []
      for k in range(GRID_CELLS):
        row.append(None)
      cell_map.append(row)

    all_coordinates = self.generate_coordinates(0, GRID_CELLS - 1, MAP_ROCKS_COUNT + MAP_TRUCKS_COUNT)
    for i in range(0, MAP_ROCKS_COUNT):
      x, y = all_coordinates.pop()
      cell_map[x][y] = Rock(x, y)

    for i in range(0, MAP_TRUCKS_COUNT):
      x, y = all_coordinates.pop()
      truck = DumpTruck(x, y)
      cell_map[x][y] = truck
      self.actors.append(truck)
      print('- truck placed at', truck.X, truck.Y)


    # self.truck = DumpTruck(5, 7)
    # cellMAP[5][7] = self.truck
    # self.actors.append(self.truck)
    # print('- truck placed at', self.truck.X, self.truck.Y)
    return cell_map

  def generate_coordinates(self, min, max, count):
    coordinates = set()
    while len(coordinates) < count:
      x, y = random.randint(min, max), random.randint(min, max)
      coordinates.add((x, y))
    return coordinates


  def place_ore(self):
    # removing previous ore, if needed
    if len(self.ores_location) > 0:
      curr_pos = self.ores_location[0]
      self.map[curr_pos.x][curr_pos.y] = None

    new_ore_pos = Point(random.randint(0, GRID_CELLS - 1), random.randint(0, GRID_CELLS - 1))
    while True:
      same_pos_actor = None
      for actor in self.actors:
        if actor.X == new_ore_pos.x and actor.Y == new_ore_pos.y:
          same_pos_actor = actor
          break
      if same_pos_actor:
        new_ore_pos = Point(random.randint(0, GRID_CELLS - 1), random.randint(0, GRID_CELLS - 1))
      else:
        break


    new_ore = Ore(new_ore_pos.x, new_ore_pos.y)
    self.map[new_ore_pos.x][new_ore_pos.y] = new_ore
    self.ores_location = [new_ore_pos]
    for actor in self.actors:
      actor.set_ores([new_ore])



  def get_actors(self):
    return self.actors

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
        self.simulation_running = False
        pygame.quit()
        sys.exit()
      elif event.type == KEYDOWN and event.key == K_r:
        self.reset()
