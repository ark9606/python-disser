import numpy as np
import constants as const
import pygame
from enum import IntEnum
from collections import namedtuple

GRID_CELLS = const.GRID_CELLS
GRID_ORIGIN = const.GRID_ORIGIN
CELL_SIZE = const.CELL_SIZE
GRID_CODE = const.GRID_CODE_TRUCK

truckImg = pygame.image.load('./static/truck3.png')
truckImg = pygame.transform.scale(truckImg, (CELL_SIZE, CELL_SIZE))

TRUCK_DEFAULT_FUEL_CELLS = 999999


Point = namedtuple('Point', 'x, y')

class Angle(IntEnum):
  LEFT = 0
  UP = -90
  RIGHT = -180
  DOWN = 90

class Rotation(IntEnum):
  LEFT = -90
  RIGHT = 90

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

# states
STATE_IDLE = 1
STATE_GOTO_LOAD = 2
STATE_LOAD_WEIGHT = 3
STATE_GOTO_THROW = 4
STATE_THROW_WEIGHT = 5

# actions
# [1, 0, 0] - straight
# [0, 1, 0] - right
# [0, 0, 1] - left
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

class DumpTruck:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        self.img = truckImg
        # self.look = LEFT
        # self.angle = Angle.LEFT
        self.degree = Degree.UP
        self.direction = Direction.UP
        self.fuel_cells = TRUCK_DEFAULT_FUEL_CELLS
        # self.turn_to(Angle.LEFT)
        self.activeState = None
        # self.brain = FSM()
        # self.brain.push_state(STATE_GOTO_LOAD)
        # self.map = []
        self.ores_location = []

    def set_data(self, gridOrigin):
        self.gridOrigin = gridOrigin

    # def set_map(self, map):
    #     self.map = map

    def set_ores_location(self, location):
      self.ores_location = location

    def get_code(self):
        return GRID_CODE

    def __repr__(self):
        return str(self.get_code())
    
    def draw(self, surf):
      X = GRID_ORIGIN[0] + (CELL_SIZE * self.X)
      Y = GRID_ORIGIN[1] + (CELL_SIZE * self.Y)
      surf.blit(self.img, (X, Y))

    def update(self, action):
      if np.array_equal(action, [1, 0, 0]):
        self.moveForward()
      # todo: fix rotation
      elif np.array_equal(action, [0, 1, 0]):
        self.rotate_to(1)
        self.moveForward()
      elif np.array_equal(action, [0, 0, 1]):
        self.rotate_to(-1)
        self.moveForward()


    def get_state(self):
      point_left = Point(self.X - 1, self.Y)
      point_right = Point(self.X + 1, self.Y)
      point_up = Point(self.X, self.Y - 1)
      point_down = Point(self.X, self.Y + 1)

      # dir_left = self.degree == Degree.LEFT
      # dir_right = self.degree == Degree.RIGHT
      # dir_up = self.degree == Degree.UP
      # dir_down = self.degree == Degree.DOWN

      dir_left = self.direction == Direction.LEFT
      dir_right = self.direction == Direction.RIGHT
      dir_up = self.direction == Direction.UP
      dir_down = self.direction == Direction.DOWN

      # TODO change to array of ores
      ore = self.ores_location[0]

      border_straight = (dir_right and self.is_collision(point_right)) or (dir_left and self.is_collision(point_left)) or (dir_up and self.is_collision(point_up)) or (dir_down and self.is_collision(point_down))
      border_right = (dir_right and self.is_collision(point_down)) or (dir_left and self.is_collision(point_up)) or (dir_up and self.is_collision(point_right)) or (dir_down and self.is_collision(point_left))
      border_left = (dir_right and self.is_collision(point_up)) or (dir_left and self.is_collision(point_down)) or (dir_up and self.is_collision(point_left)) or (dir_down and self.is_collision(point_right))

      ore_left = ore.x < self.X
      ore_right = ore.x > self.X
      ore_up = ore.y < self.Y
      ore_down = ore.y > self.Y
      state = [
        # danger (border) straight
        border_straight,

        # danger (border) right
        border_right,

        # danger (border) left
        border_left,

        # Move direction
        dir_left,
        dir_right,
        dir_up,
        dir_down,

        # Ore location
        ore_left,   # ore left
        ore_right,   # ore right
        ore_up,   # ore up
        ore_down    # ore down
      ]
      return np.array(state, dtype = int)

    def is_collision(self, point = None):
      if point is None:
        point = Point(self.X, self.Y)

      # hits boundary
      if point.x > (GRID_CELLS - 1) or point.x < 0 or point.y > (GRID_CELLS - 1) or point.y < 0:
        return True

      return False
    # def go_to_load(self):
    #   # turning at borders of map
    #   if self.angle == Angle.LEFT and self.X == 0:
    #     self.turn_to(Angle.UP)
    #
    #   elif self.angle == Angle.UP and self.Y == 0:
    #     self.turn_to(Angle.RIGHT)
    #
    #   elif self.angle == Angle.RIGHT and self.X == GRID_CELLS - 1:
    #     self.turn_to(Angle.DOWN)
    #
    #   elif self.angle == Angle.DOWN and self.Y == GRID_CELLS - 1:
    #     self.turn_to(Angle.LEFT)
    #
    #   self.moveForward()

    def moveRight(self):
      # if self.X < (GRID_CELLS - 1) and self.fuel_cells > 0:
      self.X += 1
      self.fuel_cells -= 1

    def moveLeft(self):
      # if self.X > 0 and self.fuel_cells > 0:
      self.X -= 1
      self.fuel_cells -= 1

    def moveUp(self):
      # if self.Y > 0 and self.fuel_cells > 0:
      self.Y -= 1
      self.fuel_cells -= 1

    def moveDown(self):
      # if self.Y < (GRID_CELLS - 1) and self.fuel_cells > 0:
      self.Y += 1
      self.fuel_cells -= 1

    
    def moveForward(self):
      if self.direction == Direction.RIGHT:
        self.moveRight()
      elif self.direction == Direction.DOWN:
        self.moveDown()
      elif self.direction == Direction.LEFT:
        self.moveLeft()
      elif self.direction == Direction.UP:
        self.moveUp()
      # if self.degree == Degree.RIGHT:
      #   self.moveRight()
      # elif self.degree == Degree.DOWN:
      #   self.moveDown()
      # elif self.degree == Degree.LEFT:
      #   self.moveLeft()
      # elif self.degree == Degree.UP:
      #   self.moveUp()
    
    def turn_to(self, new_angle):
      rotate = (360 - int(self.angle) + int(new_angle))
      self.angle = new_angle
      self.img = pygame.transform.rotate(self.img, rotate)

    def rotate_to(self, new_direction):
      # rotate = (360 - int(self.degree) + int(new_degree))
      # rotate = new_degree
      # self.degree = new_degree
      self.direction = (self.direction + new_direction) % 4
      self.img = pygame.transform.rotate(self.img, new_direction * -90)
