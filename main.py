import sys
import pygame
from pygame.locals import KEYDOWN, K_q, K_ESCAPE
import numpy as np
import time
import threading as th
import dump_truck



SCREENSIZE = WIDTH, HEIGHT = 1024, 768
BLACK = (0, 0, 0)
GREY = (230, 230, 230)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
CELL_SIZE = 40

LINE_WIDTH = 2
LINE_COLOR = BLACK
WINDOW_MARGIN = LINE_WIDTH


# cellMAP = np.random.randint(1, size=(16, 16))
cellMAP = [[None] * 16] * 16
# GRID_CELLS = cellMAP.shape[0]
GRID_CELLS = len(cellMAP)

# GRID_SIZE = (WIDTH if WIDTH < HEIGHT else HEIGHT) - LINE_WIDTH * 2
GRID_SIZE = GRID_CELLS * CELL_SIZE
GRID_ORIGIN = (WIDTH / 2 - GRID_SIZE / 2, WINDOW_MARGIN)

CELL_MARGIN = LINE_WIDTH * 2
# CELL_SIZE = (GRID_SIZE / GRID_CELLS) - (CELL_MARGIN * 2)

_VARS = {
  'surf': False,
  'gridCells': GRID_CELLS,
  'map': cellMAP
}
timer = False
quited = False

def updateState():
  # _VARS['map'] = np.random.randint(3, size=(16, 16))
  # _VARS['map'] = np.random.randint(1, size=(16, 16))
  # _VARS['map'][0][0] = 
  print('tick')
  print(_VARS['map'])



def main():
  pygame.init()
  _VARS['surf'] = pygame.display.set_mode(SCREENSIZE)
  
  # sets all rows in column with truck
  truck = dump_truck.DumpTruck(1, 2)
  _VARS['map'][1][2] = truck

  while True:
    checkEvents()
    _VARS['surf'].fill(GREY)
    drawSquareGrid(GRID_ORIGIN, GRID_SIZE, GRID_CELLS)
    fillCells()
    pygame.display.update()
    updateState()
    pygame.time.delay(500)


# NEW METHOD FOR ADDING CELLS :
def fillCells():
  # GET CELL DIMENSIONS...
  for row in range(GRID_CELLS):
      for column in range(GRID_CELLS):
          obj = _VARS['map'][column][row]

          if not obj:
            continue

          fill = GREY
          if obj.get_code() == 1:
            fill = BLACK
          elif obj.get_code() == 2:
            fill = RED
          
          X = GRID_ORIGIN[0] + (CELL_SIZE * row) + CELL_MARGIN + LINE_WIDTH / 2
          Y = GRID_ORIGIN[1] + (CELL_SIZE * column) + CELL_MARGIN + LINE_WIDTH / 2
          drawSquareCell(X, Y, CELL_SIZE - CELL_MARGIN * 2, CELL_SIZE - CELL_MARGIN * 2, fill)


# Draw filled rectangle at coordinates
def drawSquareCell(x, y, dimX, dimY, color):
  pygame.draw.rect(_VARS['surf'], color, (x, y, dimX, dimY))


def drawSquareGrid(origin, gridWH, cells):

    CONTAINER_WIDTH_HEIGHT = gridWH
    cont_x, cont_y = origin

    # DRAW Grid Border:
    # TOP LEFT TO RIGHT
    pygame.draw.line(
      _VARS['surf'], LINE_COLOR,
      (cont_x, cont_y),
      (CONTAINER_WIDTH_HEIGHT + cont_x, cont_y), LINE_WIDTH)
    # # BOTTOM LEFT TO RIGHT
    pygame.draw.line(
      _VARS['surf'], LINE_COLOR,
      (cont_x, CONTAINER_WIDTH_HEIGHT + cont_y),
      (CONTAINER_WIDTH_HEIGHT + cont_x,
       CONTAINER_WIDTH_HEIGHT + cont_y), LINE_WIDTH)
    # # LEFT TOP TO BOTTOM
    pygame.draw.line(
      _VARS['surf'], LINE_COLOR,
      (cont_x, cont_y),
      (cont_x, cont_y + CONTAINER_WIDTH_HEIGHT), LINE_WIDTH)
    # # RIGHT TOP TO BOTTOM
    pygame.draw.line(
      _VARS['surf'], LINE_COLOR,
      (CONTAINER_WIDTH_HEIGHT + cont_x, cont_y),
      (CONTAINER_WIDTH_HEIGHT + cont_x,
       CONTAINER_WIDTH_HEIGHT + cont_y), LINE_WIDTH)

    # DRAW Grid cells:
    # Get cell size, just one since its a square grid.
    # cellSize = CONTAINER_WIDTH_HEIGHT/cells
    cellSize = CELL_SIZE

    # VERTICAL DIVISIONS: (0,1,2) for grid(3) for example
    for x in range(cells):
        pygame.draw.line(
           _VARS['surf'], LINE_COLOR,
           (cont_x + (cellSize * x), cont_y),
           (cont_x + (cellSize * x), CONTAINER_WIDTH_HEIGHT + cont_y), LINE_WIDTH)
    # HORIZONTAl DIVISIONS
        pygame.draw.line(
          _VARS['surf'], LINE_COLOR,
          (cont_x, cont_y + (cellSize*x)),
          (cont_x + CONTAINER_WIDTH_HEIGHT, cont_y + (cellSize*x)), LINE_WIDTH)


def checkEvents():
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()
      timer.cancel()
      quited = True
    elif event.type == KEYDOWN and (event.key == K_q or event.key == K_ESCAPE):
      pygame.quit()
      sys.exit()
      timer.cancel()
      quited = True




if __name__ == '__main__':
    main()