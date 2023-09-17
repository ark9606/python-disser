import numpy as np
import constants as const
import pygame
from enum import IntEnum
from collections import namedtuple
from blocks import Block

GRID_CELLS = const.GRID_CELLS
GRID_ORIGIN = const.GRID_ORIGIN
CELL_SIZE = const.CELL_SIZE
GRID_CODE = const.GRID_CODE_TRUCK

truckImg = pygame.image.load('./static/truck6.png')
truckImg = pygame.transform.scale(truckImg, (CELL_SIZE, CELL_SIZE))

TRUCK_DEFAULT_FUEL_CELLS = 999999


Point = namedtuple('Point', 'x, y')

# class Angle(IntEnum):
#   LEFT = 0
#   UP = -90
#   RIGHT = -180
#   DOWN = 90
#
# class Rotation(IntEnum):
#   LEFT = -90
#   RIGHT = 90

class Degree(IntEnum):
  UP = 0
  RIGHT = 90
  DOWN = 180
  LEFT = 270

class Direction(IntEnum):
  UP = 0
  RIGHT = 1
  DOWN = 2
  LEFT = 3

class Turn(IntEnum):
  RIGHT = 1
  LEFT = -1

# states
STATE_IDLE = 1
STATE_GOTO_LOAD = 2
STATE_LOAD_WEIGHT = 3
STATE_GOTO_THROW = 4
STATE_THROW_WEIGHT = 5

# actions
# [1, 0, 0] - go to unload
# [0, 1, 0] - go to ore
# [0, 0, 1] - idle
class FSM:
    def __init__(self):
        self.states_stack = []
    
    def push_state(self, new_state):
        current_state = self.get_current_state()
        if current_state != new_state:
            self.states_stack.append(new_state)

    def pop_state(self):
        return self.states_stack.pop()

    def get_current_state(self):
        return self.states_stack[-1] if len(self.states_stack) > 0 else None

class DumpTruck(Block):
    def __init__(self, X, Y):
        Block.__init__(self, X, Y, truckImg, const.GRID_CODE_ORE)
        self.degree = Degree.UP
        self.direction = Direction.UP
        self.fuel_cells = TRUCK_DEFAULT_FUEL_CELLS
        self.activeState = None
        self.loaded = 0 # percent of load (max 100)
        # self.brain = FSM()
        # self.brain.push_state(STATE_GOTO_LOAD)
        self.map = []
        self.ores = []  # ores in all simulation (same as in simulation class)
        self.score = 0
        self.graph = None
        self.unload = None
        self.path_to_aim = []
        self.aim = None


    def set_data(self, map):
      self.map = map
      ores = []
      for r in range(len(map)):
        for c in range(len(map[r])):
          if map[r][c] and map[r][c].get_code() == const.GRID_CODE_UNLOAD:
            self.unload = map[r][c]
          if map[r][c] and map[r][c].get_code() == const.GRID_CODE_ORE:
            ores.append(map[r][c])
      self.ores = ores


    def set_graph(self, graph):
      self.graph = graph

    def get_code(self):
        return GRID_CODE

    def __repr__(self):
        return str(self.get_code())
    
    def draw(self, surf):
      X = GRID_ORIGIN[0] + (CELL_SIZE * self.X)
      Y = GRID_ORIGIN[1] + (CELL_SIZE * self.Y)
      surf.blit(self.img, (X, Y))

    def perform_action(self, action):
      # print('unload', self.loaded)
      if self.loaded < 100:
        self.go_to_ore()
      else:
        self.go_to_unload()


      # if np.array_equal(action, [1, 0, 0]):
      #   self.go_to_ore()
      #
      # elif np.array_equal(action, [0, 1, 0]) and self.unload:
      #   self.go_to_by_algo(self.unload)
      #   self.aim = const.GRID_CODE_UNLOAD


      # if np.array_equal(action, [1, 0, 0]):
      #   self.move_forward()
      #
      # elif np.array_equal(action, [0, 1, 0]):
      #   self.rotate_to(Turn.RIGHT)
      #   self.move_forward()
      #
      # elif np.array_equal(action, [0, 0, 1]):
      #   self.rotate_to(Turn.LEFT)
      #   self.move_forward()

    def go_to_ore(self):
      self.aim = const.GRID_CODE_ORE
      ores_list = []
      for ore in self.ores:
        path = self.find_path(self, ore)
        ores_list.append({'ore': ore, 'path': path})

      ores_list.sort(key = lambda x: len(x['path']))
      aim_ore = None
      for ore in ores_list:
        if ore['ore'].amount >= (100 - self.loaded):
          aim_ore = ore
          break

      self.path_to_aim = aim_ore['path']
      if len(self.path_to_aim) == 0:
        aim_ore['ore'].amount -= 100
        self.loaded = 100
        return
      self.move_by_path(aim_ore['path'])


    def go_to_unload(self):
      self.aim = const.GRID_CODE_UNLOAD
      self.go_to_by_algo(self.unload)
      if len(self.path_to_aim) == 0:
        self.loaded = 0

    def find_path(self, from_point, to_point):
      vertex_end = str(to_point.X) + '.' + str(to_point.Y)
      vertex_start = str(from_point.X) + '.' + str(from_point.Y)
      path = self.graph.shortest_path(vertex_start, vertex_end)
      if len(path) < 2:
        return []
      return path

    def go_to_by_algo(self, point):
      path = self.find_path(self, point)
      self.path_to_aim = path
      if len(self.path_to_aim) == 0:
        return
      self.move_by_path(path)


    def move_by_path(self, path):
      next_cell = path[1].split('.')
      next_x = int(next_cell[0])
      next_y = int(next_cell[1])

      if self.is_dir_up():
        if next_x < self.X:
          self.rotate_to(Turn.LEFT)
        elif next_x > self.X:
          self.rotate_to(Turn.RIGHT)
        # if next_y < self.Y:
        #   self.rotate_to(Turn.RIGHT)
        #   self.rotate_to(Turn.RIGHT)

      elif self.is_dir_down():
        if next_x < self.X:
          self.rotate_to(Turn.RIGHT)
        elif next_x > self.X:
          self.rotate_to(Turn.LEFT)
        # if next_y > self.Y:
        #   self.rotate_to(Turn.RIGHT)
        #   self.rotate_to(Turn.RIGHT)

      elif self.is_dir_left():
        if next_y < self.Y:
          self.rotate_to(Turn.RIGHT)
        elif next_y > self.Y:
          self.rotate_to(Turn.LEFT)
        # if next_x > self.X:
        #   self.rotate_to(Turn.RIGHT)
        #   self.rotate_to(Turn.RIGHT)

      elif self.is_dir_right():
        if next_y < self.Y:
          self.rotate_to(Turn.LEFT)
        elif next_y > self.Y:
          self.rotate_to(Turn.RIGHT)
        if next_x < self.X:
          self.rotate_to(Turn.RIGHT)
          self.rotate_to(Turn.RIGHT)

      self.X = next_x
      self.Y = next_y


    def calc_score(self, frame_iteration, prev_state):
      # 3. check if simulation is finished
      # temp check of finished for check training, todo: change this after train check
      # temp calc of reward for check training, todo: change this after train check
      reward = 0
      finished = False
      # meet the borders or meet rocks
      curr_pos_block_code = self.get_block_code_at(None)
      # print('curr_pos_block_code', curr_pos_block_code)

      return reward, finished, self.score

      prev_aim = prev_state[2]
      curr_aim = self.aim

      prev_path_to_aim = prev_state[1]
      curr_path_to_aim = self.path_to_aim

      prev_loaded = prev_state[0]
      curr_loaded = self.loaded

      print('curr_aim', curr_aim, 'curr_loaded', curr_loaded)
      # aim
      if curr_loaded < 100 and curr_aim and curr_aim == const.GRID_CODE_ORE:
        reward += 10
        self.score += 1
      elif curr_loaded == 100 and curr_aim and curr_aim != const.GRID_CODE_UNLOAD:
        reward -= 10
        finished = True
        return reward, finished, self.score


      # if curr_aim == const.GRID_CODE_UNLOAD:
      #   if curr_loaded == 100:
      #     reward += 10

      # movement
      if prev_aim == curr_aim:
        if len(curr_path_to_aim) < len(prev_path_to_aim):
          reward += 10
          if len(curr_path_to_aim) <= 1:
            reward += 20
            # todo it somewhere in the action
            # self.loaded = 100
            # finished = True
        else:
          reward -= 10
      elif curr_aim == const.GRID_CODE_UNLOAD:
        print('CHANGED AIM')

      return reward, finished, self.score


      if (self.loaded > 100 and curr_pos_block_code == const.GRID_CODE_ROCK) or frame_iteration > 100:
        finished = True
        reward = -10
        reasons = []
        if frame_iteration > 100:
          reasons.append('max iter')
        if self.is_collision(None):
          reasons.append('hit border')
        if self.get_block_code_at(None) == const.GRID_CODE_ROCK:
          reasons.append('hit rock')

        print('Iter count', frame_iteration, 'Reasons', reasons,)
        return reward, finished, self.score

      if self.score > 100:
        finished = True
        self.score += 1
        self.loaded = 0
        reason = 'score max'
        print('Reason', reason, 'iterations', frame_iteration)
        return reward, finished, self.score

      if self.unload and self.loaded == 100 and self.X == self.unload.point().X and self.Y == self.unload.point().Y:
        reward = 10
        self.score +=1
        self.loaded = 0
        return reward, finished, self.score

      # 4. place new ore
      # todo make communication between trucks, and choose closer ore (on path)
      # todo: now truck is ON ore, change to being near the ore
      if self.loaded == 0 and self.X == self.get_ore().X and self.Y == self.get_ore().Y:
        self.score += 1
        self.loaded += 100
        reward = 10

      return reward, finished, self.score

    def get_ore(self):
      ore = self.ores[0]
      return ore


    def get_local_state(self):
      return [self.loaded, self.path_to_aim, self.aim]

    def get_state(self):
      point_left = Point(self.X - 1, self.Y)
      point_right = Point(self.X + 1, self.Y)
      point_up = Point(self.X, self.Y - 1)
      point_down = Point(self.X, self.Y + 1)

      dir_left = self.direction == Direction.LEFT
      dir_right = self.direction == Direction.RIGHT
      dir_up = self.direction == Direction.UP
      dir_down = self.direction == Direction.DOWN

      block_code_left = self.get_block_code_at(point_left)
      block_code_right = self.get_block_code_at(point_right)
      block_code_up = self.get_block_code_at(point_up)
      block_code_down = self.get_block_code_at(point_down)

      # TODO change to array of ores
      ore = self.ores[0]

      border_straight = (dir_right and self.is_collision(point_right)) or (dir_left and self.is_collision(point_left)) or (dir_up and self.is_collision(point_up)) or (dir_down and self.is_collision(point_down))
      border_right = (dir_right and self.is_collision(point_down)) or (dir_left and self.is_collision(point_up)) or (dir_up and self.is_collision(point_right)) or (dir_down and self.is_collision(point_left))
      border_left = (dir_right and self.is_collision(point_up)) or (dir_left and self.is_collision(point_down)) or (dir_up and self.is_collision(point_left)) or (dir_down and self.is_collision(point_right))


      rock_straight = (dir_right and block_code_right == const.GRID_CODE_ROCK) or (dir_left and block_code_left == const.GRID_CODE_ROCK) or (dir_up and block_code_up == const.GRID_CODE_ROCK) or (dir_down and block_code_down == const.GRID_CODE_ROCK)
      rock_right = (dir_right and block_code_down == const.GRID_CODE_ROCK) or (dir_left and block_code_up == const.GRID_CODE_ROCK) or (dir_up and block_code_right == const.GRID_CODE_ROCK) or (dir_down and block_code_left == const.GRID_CODE_ROCK)
      rock_left = (dir_right and block_code_up == const.GRID_CODE_ROCK) or (dir_left and block_code_down == const.GRID_CODE_ROCK) or (dir_up and block_code_left == const.GRID_CODE_ROCK) or (dir_down and block_code_right == const.GRID_CODE_ROCK)

      ore_left = ore.X < self.X
      ore_right = ore.X > self.X
      ore_up = ore.Y < self.Y
      ore_down = ore.Y > self.Y

      state = [
        self.loaded == 100
        # # danger (border) straight
        # border_straight,
        #
        # # danger (border) right
        # border_right,
        #
        # # danger (border) left
        # border_left,
        #
        #
        # # danger (rock) straight
        # rock_straight,
        #
        # # danger (rock) right
        # rock_right,
        #
        # # danger (rock) left
        # rock_left,
        #
        #
        # # Move direction
        # dir_left,
        # dir_right,
        # dir_up,
        # dir_down,
        #
        # # Ore location
        # ore_left,   # ore left
        # ore_right,   # ore right
        # ore_up,   # ore up
        # ore_down,    # ore down
      ]
      return np.array(state, dtype = int)

    # todo: could be extracted for all active transports
    def is_collision(self, point = None):
      if point is None:
        point = Point(self.X, self.Y)

      # hits boundary
      if point.x > (GRID_CELLS - 1) or point.x < 0 or point.y > (GRID_CELLS - 1) or point.y < 0:
        return True

      return False

    def get_block_code_at(self, point):
      if point is None:
        point = Point(self.X, self.Y)

      # hits boundary
      if point.x > (GRID_CELLS - 1) or point.x < 0 or point.y > (GRID_CELLS - 1) or point.y < 0:
        return None

      code = self.map[point.x][point.y].get_code() if isinstance(self.map[point.x][point.y], Block) else None
      return code

    def get_next_block_code(self):
      next_point = self.get_next_point()
      return self.get_block_code_at(next_point)

    def get_next_point(self):
      if self.is_dir_left():
        return Point(self.X - 1, self.Y)
      if self.is_dir_right():
        return Point(self.X + 1, self.Y)
      if self.is_dir_up():
        return Point(self.X, self.Y - 1)
      return Point(self.X, self.Y + 1)



    def is_dir_right(self):
      return self.direction == Direction.RIGHT

    def is_dir_left(self):
      return self.direction == Direction.LEFT

    def is_dir_up(self):
      return self.direction == Direction.UP

    def is_dir_down(self):
      return self.direction == Direction.DOWN


    def move_right(self):
      self.X += 1
      self.fuel_cells -= 1

    def move_left(self):
      self.X -= 1
      self.fuel_cells -= 1

    def move_up(self):
      self.Y -= 1
      self.fuel_cells -= 1

    def move_down(self):
      self.Y += 1
      self.fuel_cells -= 1

    
    def move_forward(self):
      if self.direction == Direction.RIGHT:
        self.move_right()
      elif self.direction == Direction.DOWN:
        self.move_down()
      elif self.direction == Direction.LEFT:
        self.move_left()
      elif self.direction == Direction.UP:
        self.move_up()
      # print('I\'m on', self.X, self.Y)

    def rotate_to(self, new_direction):
      # rotate = (360 - int(self.degree) + int(new_degree))
      # rotate = new_degree
      # self.degree = new_degree
      self.direction = (self.direction + new_direction) % 4
      self.img = pygame.transform.rotate(self.img, new_direction * -90)
