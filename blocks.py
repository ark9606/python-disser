import constants as const
import pygame

GRID_ORIGIN = const.GRID_ORIGIN
CELL_SIZE = const.CELL_SIZE
GRID_CODE = const.GRID_CODE_TRUCK

oreImg = pygame.image.load('./static/ore.png')
oreImg = pygame.transform.scale(oreImg, (CELL_SIZE, CELL_SIZE))

rockImg = pygame.image.load('./static/rock2.png')
rockImg = pygame.transform.scale(rockImg, (CELL_SIZE, CELL_SIZE))

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

class Ore(Block):
    def __init__(self, X, Y):
        Block.__init__(self, X, Y, oreImg, const.GRID_CODE_ORE)

class Rock(Block):
    def __init__(self, X, Y):
        Block.__init__(self, X, Y, rockImg, const.GRID_CODE_ORE)
