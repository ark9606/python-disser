import sys
import pygame
from pygame.locals import KEYDOWN, K_q, K_ESCAPE
import numpy as np
import time
import threading as th
import constants as const
import dump_truck
import blocks
import time

BLACK = const.BLACK
GREY = const.GREY
CELL_SIZE = const.CELL_SIZE

LINE_WIDTH = const.LINE_WIDTH
LINE_COLOR = const.LINE_COLOR


GRID_CELLS = const.GRID_CELLS
GRID_ORIGIN = const.GRID_ORIGIN
# GRID_SIZE = GRID_CELLS * CELL_SIZE
# GRID_ORIGIN = (WIDTH / 2 - GRID_SIZE / 2, WINDOW_MARGIN)
CELL_MARGIN = const.CELL_MARGIN

simulation_running = True

cellMAP = []
for i in range(GRID_CELLS):
  row = []
  for k in range(GRID_CELLS):
    row.append(None)
  cellMAP.append(row)

_VARS = {
  'surf': False,
  'simulationThread': False,
  'gridCells': GRID_CELLS,
  'map': cellMAP,
}

def run_simulation(ex):
  iterations = 0
  while simulation_running:
    time.sleep(0.1)
    checkEvents()

    for row in range(GRID_CELLS):
      for column in range(GRID_CELLS):
          obj = _VARS['map'][column][row]
          if obj:
            obj.update()
    iterations += 1
    


def main():
  pygame.init()
  _VARS['surf'] = pygame.display.set_mode(const.SCREENSIZE)
  
  # sets all rows in column with truck
  truck = dump_truck.DumpTruck(5, 7)
  truck.set_data(GRID_ORIGIN)
  _VARS['map'][5][7] = truck

  truck1 = dump_truck.DumpTruck(10, 8)
  truck1.set_data(GRID_ORIGIN)
  _VARS['map'][10][8] = truck1
  _VARS['map'][15][15] = blocks.Ore(15, 15)
  _VARS['map'][3][3] = blocks.Rock(3, 3)



  _VARS['simulationThread'] = th.Thread(target=run_simulation, name='simulationThread', args=(_VARS,))
  _VARS['simulationThread'].start()
  while simulation_running:
    checkEvents()
    _VARS['surf'].fill(const.GREY)
    drawSquareGrid(GRID_ORIGIN, const.GRID_SIZE, GRID_CELLS)
    fillCells()
    pygame.display.flip()


def fillCells():
  # GET CELL DIMENSIONS...
  for row in range(GRID_CELLS):
      for column in range(GRID_CELLS):
          obj = _VARS['map'][column][row]

          if not obj:
            continue

          obj.draw(_VARS['surf'])


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
      simulation_running = False
      pygame.quit()
      sys.exit()
      _VARS['simulationThread'].stop()
    elif event.type == KEYDOWN and (event.key == K_q or event.key == K_ESCAPE):
      simulation_running = False
      pygame.quit()
      sys.exit()
      _VARS['simulationThread'].stop()


if __name__ == '__main__':
    main()