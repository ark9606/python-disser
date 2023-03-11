import constants as const
import pygame
import random
from enum import IntEnum

GRID_CELLS = const.GRID_CELLS
GRID_ORIGIN = const.GRID_ORIGIN
CELL_SIZE = const.CELL_SIZE
GRID_CODE = const.GRID_CODE_TRUCK

truckImg = pygame.image.load('./static/truck2.png')
truckImg = pygame.transform.scale(truckImg, (CELL_SIZE, CELL_SIZE))

TRUCK_DEFAULT_FUEL_CELLS = 999999

class Angle(IntEnum):
  LEFT = 0
  UP = -90
  RIGHT = -180
  DOWN = 90

# states
STATE_IDLE = 1
STATE_GOTO_LOAD = 2
STATE_LOAD_WEIGHT = 3
STATE_GOTO_THROW = 4
STATE_THROW_WEIGHT = 5
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
        self.angle = Angle.LEFT
        self.fuel_cells = TRUCK_DEFAULT_FUEL_CELLS
        self.rotate_to(Angle.LEFT)
        self.activeState = None
        self.brain = FSM()
        self.brain.push_state(STATE_GOTO_LOAD)

    def set_data(self, gridOrigin):
        self.gridOrigin = gridOrigin

    def get_code(self):
        return GRID_CODE

    def __repr__(self):
        return str(self.get_code())
    
    def draw(self, surf):
        X = GRID_ORIGIN[0] + (CELL_SIZE * self.X)
        Y = GRID_ORIGIN[1] + (CELL_SIZE * self.Y)
        surf.blit(self.img, (X, Y))

    def update(self):
        current_state = self.brain.get_current_state()
        if current_state == STATE_IDLE:
            pass
        elif current_state == STATE_GOTO_LOAD:
            self.go_to_load()

        # side = random.randint(0, 4)
        # self.turnTo(side)
        # if self.look != side:
            # self.turnTo(side)
            # return
        # self.moveForward()

    def go_to_load(self):
      # turning at borders of map
      if self.angle == Angle.LEFT and self.X == 0:
        self.rotate_to(Angle.UP)

      elif self.angle == Angle.UP and self.Y == 0:
        self.rotate_to(Angle.RIGHT)

      elif self.angle == Angle.RIGHT and self.X == GRID_CELLS - 1:
        self.rotate_to(Angle.DOWN)

      elif self.angle == Angle.DOWN and self.Y == GRID_CELLS - 1:
        self.rotate_to(Angle.LEFT)

      self.moveForward()

    def moveRight(self):
        # self.turnTo(RIGHT)
        if self.X < (GRID_CELLS - 1) and self.fuel_cells > 0:
            self.X += 1
            self.fuel_cells -= 1

    def moveLeft(self):
        # self.turnTo(LEFT)
        if self.X > 0 and self.fuel_cells > 0:
            self.X -= 1
            self.fuel_cells -= 1

    
    def moveUp(self):
        # self.turnTo(UP)
        if self.Y > 0 and self.fuel_cells > 0:
            self.Y -= 1
            self.fuel_cells -= 1


    def moveDown(self):
      # self.turnTo(DOWN)
      if self.Y < (GRID_CELLS - 1) and self.fuel_cells > 0:
        self.Y += 1
        self.fuel_cells -= 1

    
    def moveForward(self):
      if self.angle == Angle.RIGHT:
        self.moveRight()
      elif self.angle == Angle.DOWN:
        self.moveDown()
      elif self.angle == Angle.LEFT:
        self.moveLeft()
      elif self.angle == Angle.UP:
        self.moveUp()
    
    def rotate_to(self, new_angle):
      rotate = (360 - int(self.angle) + int(new_angle))
      self.angle = new_angle
      self.img = pygame.transform.rotate(self.img, rotate)
