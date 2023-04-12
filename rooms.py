from constants import *
from npc import all_NPCs
from rpgfeature import all_rpg_features

OVERWORLD_PNG = pygame.image.load('assets\png\maps\overworld.png').convert_alpha()

class RPGRoom:
    def __init__(self, x, y, npcs=[], features=[]):
        self.x = x
        self.y = y
        self.img = OVERWORLD_PNG
        self.selector_rect = pygame.Rect(x * GRID_WIDTH, y * GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT)
        self.subsurface = self.img.subsurface(self.selector_rect)
        self.npcs = npcs
        self.features = features
        self.color_grid = self.get_color_grid()

    def get_color_grid(self):
        color_grid = []
        room_width = self.subsurface.get_width()
        room_height = self.subsurface.get_height()

        for y in range(room_height):
            row = []
            for x in range(room_width):
                row.append(self.subsurface.get_at((x,y)))
            color_grid.append(row)

        return color_grid

#--------------------------------------------------
#           OVERWORLD INIT
#--------------------------------------------------

OVERWORLD = []

for x in range(4):
    row = []
    for y in range(4):
        row.append(RPGRoom(x=x, y=y))
    OVERWORLD.append(row)

OVERWORLD[2][1].npcs = [all_NPCs["gwendolina"]]