import sys
import threading as th
import pygame
from pygame.locals import KEYDOWN, K_q, K_r, K_ESCAPE
import constants as const
import map as map
from dump_truck import DumpTruck
from blocks import Ore, Rock, Unload, FuelStation
import time

from graph import Graph
from utils import Point
import random

pygame.init()
GRID_CELLS = const.GRID_CELLS
GRID_ORIGIN = const.GRID_ORIGIN
CELL_SIZE = const.CELL_SIZE

LINE_WIDTH = const.LINE_WIDTH
LINE_COLOR = const.LINE_COLOR
SPEED = 7


MAP_ORES_COUNT = 1
MAP_ROCKS_COUNT = 15
MAP_TRUCKS_COUNT = 1
# TODO: check path to next aim if fuel enough for it + path to fuel, then go
# TODO: improve check for fuel refill - now they return back for refilling
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
    self.graph = None
    self.reset()

  
  def reset(self):
    self.actors = []
    self.simulation_running = False
    self.ores_location = [] # ores in all simulation
    self.frame_iteration = 0
    # self.map = self.generate_map()
    self.init_map()
    # self.place_ore()

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
          # print(obj)
          if isinstance(obj, DumpTruck):
            # graph = self.build_graph(obj)
            # obj.set_graph(graph)


            prev_state = obj.get_local_state()
            obj.perform_action(action)
            reward, finished, score = obj.calc_score(self.frame_iteration, prev_state)
          if isinstance(obj, Ore):
            if obj.amount < 1:
              self.map[column][row] = None
              for actor in self.actors:
                actor.set_data(self.map)
                graph = self.build_graph()
                actor.set_graph(graph)
          # if isinstance(obj, FuelStation):
          #   for actor in self.actors:
          #     actor.set_data(self.map)

    if finished:
      self.frame_iteration = 0
      self.place_ore()
      # return reward, finished, score

    # if reward == 20:
    #   print('GOT 20')
    #   self.frame_iteration = 0
    #   self.place_ore()
    #   return reward, finished, score

    # if reward > 0:
    #   self.frame_iteration = 0
    #   self.place_ore()

    self.update_ui()
    self.clock.tick(SPEED)
    return reward, finished, score
    

  def init_map(self):
    cell_map = map.GRID
    # cell_map = np.array(map.GRID).T.tolist()

    ores = []
    for r in range(GRID_CELLS):
      for c in range(GRID_CELLS):
        if cell_map[r][c] == 0:
          cell_map[r][c] = None
        elif cell_map[r][c] == const.GRID_CODE_ROCK:
          cell_map[r][c] = Rock(r, c)
        elif cell_map[r][c] == const.GRID_CODE_UNLOAD:
          cell_map[r][c] = Unload(r, c)
        elif cell_map[r][c] == const.GRID_CODE_FUEL:
          cell_map[r][c] = FuelStation(r, c)
        elif cell_map[r][c] == const.GRID_CODE_ORE:
          cell_map[r][c] = Ore(r, c)
          ores.append(cell_map[r][c])
        elif cell_map[r][c] == const.GRID_CODE_TRUCK:
          truck = DumpTruck(r, c)
          cell_map[r][c] = truck
          self.actors.append(truck)

    self.map = cell_map
    graph = self.build_graph()

    for actor in self.actors:
      actor.set_data(cell_map)
      actor.set_graph(graph)

    # new_ore = Ore(new_ore_pos.x, new_ore_pos.y)
    # self.map[new_ore_pos.x][new_ore_pos.y] = new_ore
    # self.ores_location = [new_ore_pos]

    # for actor in self.actors:
    #   actor.set_ores([new_ore])
    #   todo move to any step to handle collisions with other trucks
      # actor.set_graph(graph)

    # return cell_map

  def generate_map(self):
    cell_map = []
    for i in range(GRID_CELLS):
      row = []
      for k in range(GRID_CELLS):
        row.append(None)
      cell_map.append(row)

    # all_coordinates = self.generate_coordinates(0, GRID_CELLS - 1, MAP_ROCKS_COUNT + MAP_TRUCKS_COUNT)
    all_coordinates = {(28, 17), (7, 27), (24, 17), (16, 0), (26, 12), (19, 7), (7, 16), (12, 0), (9, 26), (7, 0), (14, 6), (29, 2), (4, 27), (21, 4), (6, 22), (20, 21)}
    for i in range(0, MAP_ROCKS_COUNT):
      x, y = all_coordinates.pop()
      cell_map[x][y] = Rock(x, y)

    for i in range(0, MAP_TRUCKS_COUNT):
      x, y = all_coordinates.pop()
      truck = DumpTruck(x, y)
      cell_map[x][y] = truck
      self.actors.append(truck)
      print('- truck placed at', truck.X, truck.Y)

    for actor in self.actors:
      actor.set_data(cell_map)

    return cell_map

  def generate_coordinates(self, min, max, count):
    coordinates = set()
    while len(coordinates) < count:
      x, y = random.randint(min, max), random.randint(min, max)
      coordinates.add((x, y))
    return coordinates


  def build_graph(self):
    objects_for_visits = [const.GRID_CODE_ORE, const.GRID_CODE_UNLOAD, const.GRID_CODE_TRUCK, const.GRID_CODE_FUEL]
    map_graph = Graph()
    for r in range(GRID_CELLS):
      for c in range(GRID_CELLS):
        map_graph.add_vertex(str(r) + '.' + str(c))

    for r in range(GRID_CELLS):
      for c in range(GRID_CELLS):
        cell = self.map[r][c]
        if cell and cell.get_code() == const.GRID_CODE_ROCK:
          continue
        curr_vertex = str(r) + '.' + str(c)
        right_vertex = str(r) + '.' + str(c + 1) if c < GRID_CELLS - 1 else None
        down_vertex = str(r + 1) + '.' + str(c) if r < GRID_CELLS - 1 else None
        if right_vertex:
          right_cell = self.map[r][c + 1]
          if right_cell is None or right_cell.get_code() in objects_for_visits:
            map_graph.add_edge(curr_vertex, right_vertex, 1)

        if down_vertex:
          down_cell = self.map[r + 1][c]
          if down_cell is None or down_cell.get_code() in objects_for_visits:
            map_graph.add_edge(curr_vertex, down_vertex, 1)
    return map_graph

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

    # graph = self.build_graph()
    # for actor in self.actors:
      # actor.set_ores([new_ore])
      # todo move to any step to handle collisions with other trucks
      # actor.set_graph(graph)


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


