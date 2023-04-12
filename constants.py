import sys
import math
import random
import pygame
import opensimplex

FPS = 60
BLOCK_SIZE = 16
WIDTH, HEIGHT = 800, 800
GRID_WIDTH = WIDTH // BLOCK_SIZE
GRID_HEIGHT = HEIGHT // BLOCK_SIZE

PALETTE = {
    "mblu": (26 ,42 ,145,255),
    "dblu": (15 ,26 ,89 ,255),
    "lgrn": (95 ,169,85 ,255),
    "dgrn": (21 ,83 ,21 ,255),
    "tann": (223,208,112,255),
    "ston": (233,223,201,1  )
}

NOWALK_TERRAINS = ['ocean', 'deep_ocean']
NOWALK_COLORS = [PALETTE["dblu"], PALETTE["mblu"], PALETTE["dgrn"]]

MIN_BLOCK_HEAT = 1
MAX_BLOCK_HEAT = 32
AMPLITUDE = MAX_BLOCK_HEAT / 2
FREQUENCY = 0.05
OCTAVES = 3
LACUNARITY = 2
PERSISTENCE = 0.2