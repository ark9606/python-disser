import constants as const
from utils import Point
import pygame

GRID_ORIGIN = const.GRID_ORIGIN
CELL_SIZE = const.CELL_SIZE
GRID_CODE = const.GRID_CODE_TRUCK

oreImg = pygame.image.load('./static/ore.png')
oreImg = pygame.transform.scale(oreImg, (CELL_SIZE, CELL_SIZE))

rockImg = pygame.image.load('./static/rock3.png')
rockImg = pygame.transform.scale(rockImg, (CELL_SIZE, CELL_SIZE))

unloadImg = pygame.image.load('./static/unload2.png')
unloadImg = pygame.transform.scale(unloadImg, (CELL_SIZE, CELL_SIZE))

class Block:
    def __init__(self, X, Y, img, code):
        self.X = X
        self.Y = Y
        self.img = img
        self.code = code

    def get_code(self):
        return self.code

    def __repr__(self):
        return str(self.get_code())
    
    def draw(self, surf):
        X = GRID_ORIGIN[0] + (CELL_SIZE * self.X)
        Y = GRID_ORIGIN[1] + (CELL_SIZE * self.Y)
        surf.blit(self.img, (X, Y))

    def update(self, action = None):
        pass

    def point(self):
        return Point(self.X, self.Y)

class Ore(Block):
    def __init__(self, X, Y):
        Block.__init__(self, X, Y, oreImg, const.GRID_CODE_ORE)
        self.amount = 500

class Rock(Block):
    def __init__(self, X, Y):
        Block.__init__(self, X, Y, rockImg, const.GRID_CODE_ROCK)

class Unload(Block):
    def __init__(self, X, Y):
        Block.__init__(self, X, Y, unloadImg, const.GRID_CODE_UNLOAD)
