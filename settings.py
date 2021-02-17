import pygame as pg

GRID_SIZE = 5

def change_grid_size(new_grid_size):
    global GRID_SIZE
    GRID_SIZE = new_grid_size


SUP_GRID_XY_FAR = 8
SUP_GRID_XZ_FAR = 5
SUP_GRID_YZ_FAR = 8

WIDTH_SCREEN = 1600
HEIGHT_SCREEN = 900
FPS_MAX = 60

CAMERA_STD_POS = [16, 6, 16]
CAMERA_STD_ANGLE = -2.3

CAMERA_SPEED = 0.04
ROTATION_CAMERA_SPEED = 0.01

WORLD_AXES_SIZE = 10

COLOR_TEXT_STD = (0, 0, 0)
SIZE_TEXT_STD = 36
SIZE_TEXT_INPUT_STD = 28

WHITE = pg.Color('white')
BLACK = pg.Color('black')
GREEN = pg.Color('green')
RED = pg.Color('Red')

GREY = (200, 200, 200)

MAX_INPUT_LEN = 3
MARK_COLOR = GREEN
NEED_COLOR = (150, 150, 150)
BAD_COLOR = RED

tap_to_cube = [
    [0, 0, -1],
    [0, 0, 1],
    [-1, 0, 0],
    [1, 0, 0],
    [0, 1, 0],
    [0, -1, 0]
]

LEVEL = False

LEVELS = []
