import constants as const
import pygame
import random

GRID_CELLS = const.GRID_CELLS
GRID_ORIGIN = const.GRID_ORIGIN
CELL_SIZE = const.CELL_SIZE
GRID_CODE = const.GRID_CODE_TRUCK

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

class DumpTruck:
    def __init__(self, X, Y, img):
        self.X = X
        self.Y = Y
        self.img = img
        self.look = LEFT
        self.activeState = None
        print('init look ', self.look)

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
        if self.activeState:
            self.activeState()

        # side = random.randint(0, 4)
        # self.turnTo(side)
        # if self.look != side:
            # self.turnTo(side)
            # return
        # self.moveForward()

    def moveRight(self):
        # self.turnTo(RIGHT)
        if self.X < (GRID_CELLS - 1):
            self.X += 1

    def moveLeft(self):
        # self.turnTo(LEFT)
        if self.X > 0:
            self.X -= 1
    
    def moveUp(self):
        # self.turnTo(UP)
        if self.Y > 0:
            self.Y -= 1

    def moveDown(self):
        # self.turnTo(DOWN)
        if self.Y < (GRID_CELLS - 1):
            self.Y += 1
    
    def moveForward(self):
        if self.look == RIGHT:
            self.moveRight()
        elif self.look == DOWN:
            self.moveDown()
        elif self.look == LEFT:
            self.moveLeft()
        elif self.look == UP:
            self.moveUp()
    
    def turnTo(self, to):
        diff = self.look - to
        if diff == 0:
            return
        
        direction = 1 if diff > 0 else -1
        self.img = pygame.transform.rotate(self.img, 90 * direction)
        self.look += (direction * -1)