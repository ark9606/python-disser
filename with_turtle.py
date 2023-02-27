import turtle
import random

# Define the constants
GRID_SIZE = 16
CELL_SIZE = 50
GRID_WIDTH = GRID_SIZE * CELL_SIZE
GRID_HEIGHT = GRID_SIZE * CELL_SIZE
GRID_TOP_LEFT_X = -GRID_WIDTH / 2
GRID_TOP_LEFT_Y = GRID_HEIGHT / 2
NUM_CELLS_TO_FILL = 20

# Define the colors
GRID_COLOR = "black"
BACKGROUND_COLOR = "white"
FILL_COLOR = "green"

# Set up the turtle
t = turtle.Turtle()
t.speed(0)
t.penup()
t.goto(GRID_TOP_LEFT_X, GRID_TOP_LEFT_Y)
t.pendown()

# Set the background color
turtle.bgcolor(BACKGROUND_COLOR)

# Draw the grid
t.pencolor(GRID_COLOR)
for i in range(4):
    t.forward(GRID_WIDTH)
    t.right(90)
    
for i in range(GRID_SIZE + 1):
    t.penup()
    t.goto(GRID_TOP_LEFT_X, GRID_TOP_LEFT_Y - i*CELL_SIZE)
    t.pendown()
    t.forward(GRID_WIDTH)
    
    t.penup()
    t.goto(GRID_TOP_LEFT_X + i*CELL_SIZE, GRID_TOP_LEFT_Y)
    t.pendown()
    t.right(90)
    t.forward(GRID_HEIGHT)
    t.left(90)

# Fill random cells with green color
t.fillcolor(FILL_COLOR)
for i in range(NUM_CELLS_TO_FILL):
    row = random.randint(0, GRID_SIZE - 1)
    col = random.randint(0, GRID_SIZE - 1)
    cell_top_left_x = GRID_TOP_LEFT_X + col*CELL_SIZE
    cell_top_left_y = GRID_TOP_LEFT_Y - row*CELL_SIZE
    t.penup()
    t.goto(cell_top_left_x, cell_top_left_y + CELL_SIZE)
    t.pendown()
    t.begin_fill()
    for j in range(4):
        t.forward(CELL_SIZE)
        t.right(90)
    t.end_fill()
    
# Hide the turtle
t.hideturtle()

# Keep the window open until it is closed manually
turtle.done()
