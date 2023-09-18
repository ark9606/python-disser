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
SPEED = 5

font = pygame.font.Font('./static/RobotoMono-Regular.ttf', 16)
font2 = pygame.font.Font('./static/RobotoMono-Regular.ttf', 18)

MAP_ORES_COUNT = 1
MAP_ROCKS_COUNT = 15
MAP_TRUCKS_COUNT = 1
# TODO: improve check for fuel refill - now they return back for refilling
class Simulation:
  def __init__(self):
    self.display = pygame.display.set_mode(const.SCREENSIZE)
    pygame.display.set_caption('Simulation')
    self.clock = pygame.time.Clock()
    self.actors = []
    self.simulation_running = False
    self.ores = [] # ores in all simulation
    self.frame_iteration = 0
    self.ticks = 0
    self.map = None
    self.graph = None
    self.reset()
    self.unload = None
    self.done = False
    self.start_btn = None

  
  def reset(self):
    self.actors = []
    self.simulation_running = False
    self.ores = [] # ores in all simulation
    self.unload = None
    self.frame_iteration = 0
    self.ticks = 0
    # self.map = self.generate_map()
    self.init_map()
    self.done = False

    # self.place_ore()

  def make_step(self, action):
    reward = 0
    finished = False
    score = 0

    # 1. check user input
    self.check_input()

    if not self.simulation_running:
      self.update_ui()
      self.clock.tick(SPEED)
      return reward, finished, score

    self.frame_iteration += 1
    self.ticks = self.ticks if self.done else self.ticks + 1


    # 2. move (update state of objects)
    for row in range(len(self.map)):
      for column in range(len(self.map[row])):
          obj = self.map[column][row]
          if isinstance(obj, DumpTruck):
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
          if isinstance(obj, Unload):
            self.unload = self.map[column][row]
          # if isinstance(obj, FuelStation):
          #   for actor in self.actors:
          #     actor.set_data(self.map)

    all_ores_empty = True
    for ore in self.ores:
      if ore.amount > 0:
        all_ores_empty = False
    if all_ores_empty:
      self.done = True

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

    ores = []
    for r in range(GRID_CELLS):
      for c in range(GRID_CELLS):
        if cell_map[r][c] == 0:
          cell_map[r][c] = None
        elif cell_map[r][c] == const.GRID_CODE_ROCK:
          cell_map[r][c] = Rock(r, c)
        elif cell_map[r][c] == const.GRID_CODE_UNLOAD:
          cell_map[r][c] = Unload(r, c)
          self.unload = cell_map[r][c]
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
    self.ores = ores
    # print('INIT unload', self.unload)
    graph = self.build_graph()

    for actor in self.actors:
      actor.set_data(cell_map)
      actor.set_graph(graph)

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

  def format_log_cell(self, value, cell_length):
    new_value = str(value)
    return new_value + ' ' * (cell_length - len(new_value))

  def prepare_state_log(self):
    log = []
    log.append('|-----------------------|')
    log.append('| Ores                  |')
    log.append('|-----------------------|')
    log.append('| Id   | Pos   | Amount |')
    log.append('|------|-------|--------|')

    for i in range(len(self.ores)):
      ore = self.ores[i]
      id = self.format_log_cell(ore.id, 4)
      pos = self.format_log_cell(str(ore.X) + '-' + str(ore.Y), 5)
      amount = self.format_log_cell(ore.amount, 6)
      log.append(f'| {id} | {pos} | {amount} |')
      if i == len(self.ores) - 1:
        log.append('|-----------------------|')
      else:
        log.append('|------|-------|--------|')



    log.append('')
    log.append('|-----------------------------------|')
    log.append('| Trucks                            |')
    log.append('|-----------------------------------|')
    log.append('| Id   | Pos   | Aim | Load | Fuel  |')
    log.append('|------|-------|-----|------|-------|')

    fuel_used = 0
    for i in range(len(self.actors)):
      actor = self.actors[i]
      id = self.format_log_cell(actor.id, 4)
      pos = self.format_log_cell(str(actor.X) + '-' + str(actor.Y), 5)
      aim = self.format_log_cell(actor.get_curr_aim(), 3)
      load = self.format_log_cell(actor.loaded, 4)
      fuel = self.format_log_cell(actor.fuel_cells, 5)
      log.append(f'| {id} | {pos} | {aim} | {load} | {fuel} |')
      if i == len(self.actors) - 1:
        log.append('|-----------------------------------|')
      else:
        log.append('|------|-------|-----|------|-------|')
      fuel_used += actor.fuel_used

    log.append('')
    log.append(f' Delivered: {self.unload.amount if self.unload else 0} ')
    log.append(f' Ticks: {self.ticks} ')
    log.append(f' Fuel: {fuel_used} ')

    return log

  def update_ui(self):
    self.display.fill(const.GREY)
    self.draw_grid(GRID_ORIGIN, const.GRID_SIZE, GRID_CELLS)
    self.draw_objects()
    white = (255, 255, 255)
    green = (0, 255, 0)
    blue = (0, 0, 128)
    state_log_list = self.prepare_state_log()
    for i in range(len(state_log_list)):
      text = font.render(state_log_list[i], True, (0,0,0), const.GREY2)
      text_rect = text.get_rect()
      text_rect.left = const.LABEL_POSITION[0]
      text_rect.top = const.LABEL_POSITION[1] + i * text_rect.height
      self.display.blit(text, text_rect)
    pause = '        Pause        '
    start = '        Start        '
    self.start_btn = button(self.display, const.START_BTN_POSITION, pause if self.simulation_running else start)
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

  def on_start_btn_click(self):
    self.simulation_running = not self.simulation_running

  def check_input(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT or (event.type == KEYDOWN and (event.key == K_q or event.key == K_ESCAPE)):
        self.simulation_running = False
        pygame.quit()
        sys.exit()
      elif event.type == KEYDOWN and event.key == K_r:
        self.reset()
      elif event.type == pygame.MOUSEBUTTONDOWN:
        if self.start_btn.collidepoint(pygame.mouse.get_pos()):
          self.on_start_btn_click()

def button(screen, position, text):
  text_render = font2.render(text, True, (0, 0, 255))
  x, y, w, h = text_render.get_rect()
  x, y = position
  pygame.draw.line(screen, (230, 230, 230), (x, y), (x + w, y), 5)
  pygame.draw.line(screen, (230, 230, 230), (x, y - 2), (x, y + h), 5)
  pygame.draw.line(screen, (150, 150, 150), (x, y + h), (x + w, y + h), 5)
  pygame.draw.line(screen, (150, 150, 150), (x + w, y + h), [x + w, y], 5)
  pygame.draw.rect(screen, (200, 200, 200), (x, y, w, h))
  return screen.blit(text_render, (x, y))  # this is a rect pygame.Rect