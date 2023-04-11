from constants import *
from npc import all_NPCs
from rpgfeature import all_rpg_features

class RPGRoom:
    def __init__(self, name, img, npcs=[], features=[]):
        self.name = name
        self.img = pygame.image.load(img).convert_alpha()
        self.npcs = npcs
        self.features = features
        self.color_grid = self.get_color_grid()

    def get_color_grid(self):
        color_grid = []
        room_width = self.img.get_width()
        room_height = self.img.get_height()

        for y in range(room_height):
            row = []
            for x in range(room_width):
                row.append(self.img.get_at((x,y)))
            color_grid.append(row)

        return color_grid

#--------------------------------------------------
#           OVERWORLD INIT
#--------------------------------------------------

all_rooms = {
    "blank": RPGRoom(name="blank", img='assets\png\maps\\blank_blue.png'),
    "club": RPGRoom(name="club", img='assets\png\maps\club.png', npcs=[all_NPCs["gwendolina"]]),
    "town": RPGRoom(name="town", img='assets\png\maps\\town_nobridge.png', npcs=[all_NPCs["omar"]]),
    "corridor": RPGRoom(name="corridor", img='assets\png\maps\corridor.png'),
    "cross": RPGRoom(name="cross", img='assets\png\maps\cross.png'),
    "right": RPGRoom(name="right", img='assets\png\maps\\right.png'),
    "tee": RPGRoom(name="tee", img='assets\png\maps\\tee.png'),
    "beach": RPGRoom(name="beach", img='assets\png\maps\\beach.png'),
    "grove": RPGRoom(name="cross", img='assets\png\maps\grove_hand.png')
}

OVERWORLD = []
for y in range(4):
    row = []
    for x in range(4):
        row.append(all_rooms["blank"])
    OVERWORLD.append(row)

OVERWORLD[0][0] = all_rooms["grove"]
OVERWORLD[0][1] = all_rooms["corridor"]
OVERWORLD[0][2] = all_rooms["cross"]
OVERWORLD[1][2] = all_rooms["tee"]