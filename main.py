import sys
import pygame
from pygame.locals import KEYDOWN, K_q, K_ESCAPE
import numpy as np
import time
import threading as th
import constants as const
import dump_truck
import time


# SCREENSIZE = WIDTH, HEIGHT = 1024, 768
BLACK = const.BLACK
GREY = const.GREY
# GREY = (230, 230, 230)
# GREEN = (0, 255, 0)
# RED = (255, 0, 0)
CELL_SIZE = const.CELL_SIZE

LINE_WIDTH = const.LINE_WIDTH
LINE_COLOR = const.LINE_COLOR
# WINDOW_MARGIN = LINE_WIDTH

truckImg = pygame.image.load('./static/truck2.png')
truckImg = pygame.transform.scale(truckImg, (CELL_SIZE, CELL_SIZE))

# cellMAP = np.random.randint(1, size=(16, 16))
cellMAP = [
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
  [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
]
GRID_CELLS = const.GRID_CELLS
GRID_ORIGIN = const.GRID_ORIGIN
# GRID_SIZE = GRID_CELLS * CELL_SIZE
# GRID_ORIGIN = (WIDTH / 2 - GRID_SIZE / 2, WINDOW_MARGIN)
CELL_MARGIN = const.CELL_MARGIN

# CELL_SIZE = (GRID_SIZE / GRID_CELLS) - (CELL_MARGIN * 2)

_VARS = {
  'surf': False,
  'simulationThread': False,
  'gridCells': GRID_CELLS,
  'map': cellMAP,
  'exited': False
}
exited = False

def updateState():
  # _VARS['map'] = np.random.randint(3, size=(16, 16))
  # _VARS['map'] = np.random.randint(1, size=(16, 16))
  # _VARS['map'][0][0] = 
  print('tick')
  print(_VARS['map'])

def run_simulation(ex):
  iterations = 0
  while True:
    time.sleep(0.250)
    checkEvents()
    # if ex:
      # break

    for row in range(GRID_CELLS):
      for column in range(GRID_CELLS):
          obj = _VARS['map'][column][row]
          if obj:
            obj.update_state()
    iterations += 1
    # print('iteration ', iterations, _VARS['exited'], ex)
    


def main():
  pygame.init()
  _VARS['surf'] = pygame.display.set_mode(const.SCREENSIZE)
  
  # sets all rows in column with truck
  truck = dump_truck.DumpTruck(5, 7, truckImg)
  truck.set_data(GRID_ORIGIN)
  _VARS['map'][5][7] = truck

  truck1 = dump_truck.DumpTruck(10, 8, truckImg)
  truck1.set_data(GRID_ORIGIN)
  _VARS['map'][10][8] = truck1


  _VARS['simulationThread'] = th.Thread(target=run_simulation, name='simulationThread', args=(_VARS,))
  _VARS['simulationThread'].start()
  while True:
    checkEvents()
    _VARS['surf'].fill(const.GREY)
    drawSquareGrid(GRID_ORIGIN, const.GRID_SIZE, GRID_CELLS)
    fillCells()
    pygame.display.update()
    # updateState()
    # pygame.time.delay(1000)


# NEW METHOD FOR ADDING CELLS :
def fillCells():
  # GET CELL DIMENSIONS...
  for row in range(GRID_CELLS):
      for column in range(GRID_CELLS):
          obj = _VARS['map'][column][row]

          if not obj:
            continue

          obj.draw(_VARS['surf'])
          # obj.update_state()

          # X = GRID_ORIGIN[0] + (CELL_SIZE * row) + CELL_MARGIN + LINE_WIDTH / 2
          # Y = GRID_ORIGIN[1] + (CELL_SIZE * column) + CELL_MARGIN + LINE_WIDTH / 2
          # fill = GREY
          # if obj.get_code() == const.GRID_CODE_TRUCK:
          #   fill = BLACK
          #   X = GRID_ORIGIN[0] + (CELL_SIZE * row)
          #   Y = GRID_ORIGIN[1] + (CELL_SIZE * column)
          #   _VARS['surf'].blit(truckImg, (X, Y))


          # elif obj.get_code() == 2:
          #   fill = RED
          

          # drawSquareCell(X, Y, CELL_SIZE - CELL_MARGIN * 2, CELL_SIZE - CELL_MARGIN * 2, fill)


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
      _VARS['simulationThread'].stop()
      _VARS['exited'] = True
      exited = True
    elif event.type == KEYDOWN and (event.key == K_q or event.key == K_ESCAPE):
      pygame.quit()
      sys.exit()
      _VARS['simulationThread'].stop()
      _VARS['exited'] = True
      exited = True
  print(_VARS['exited'])






if __name__ == '__main__':
    main()