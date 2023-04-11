import pygame
from constants import *

class NPC:
    def __init__(self, name, img):
        self.name = name
        self.img = pygame.image.load(img).convert_alpha()
        self.current_block = None
        self.talking = False
        self.current_message = self.update_speak()
        self.frame_count = 0

    def update_speak(self):
        pass

    def move(self, dx, dy, grid):
        new_x = self.current_block.x + dx
        new_y = self.current_block.y + dy

        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
            return False
        
        if grid[new_y][new_x].content or grid[new_y][new_x].color in NOWALK_COLORS:
            return False
        
        self.current_block.content = None
        grid[new_y][new_x].content = self
        self.current_block = grid[new_y][new_x]
        
        return True

    def draw(self, surface, x, y):
        surface.blit(self.img, (x, y))


all_NPCs = {
            "gwendolina": NPC(name="Gwendolina", img='assets/png/npc2.png'),
            "omar": NPC(name="Omar", img='assets/png/npc3.png')
            }

#--------------------------------------------------
#           NPC LOGIC
#--------------------------------------------------

def gwendolina_speak():
    message = 'good to see you, golfer'
    return message

    if player.courses_completed >= 4:
        message = 'you might have what it takes\n\ngood work'
        game.flags["game_complete"] = True
    elif game.flags["first_talked_to_gwendolina"] == False:
        message = 'welcome to the desert of the real\n\nthere is no going back'
        game.flags["first_talked_to_gwendolina"] = True
    elif player.courses_completed == 1:
        message = 'you\'ve completed your first course! impressive'
    elif game.flags["first_talked_to_gwendolina"]:
        message = 'it is good to see you, golfer'
    
    

def omar_speak():
    message = 'hey, golfer'
    return message

    if not game.flags["first_talked_to_omar"]:
        message = 'hey, golfer. i am omar'
        game.flags["first_talked_to_omar"] = True
    elif game.flags["first_talked_to_omar"]:
        message = 'you need gear? here is what i have.\n\n'
        for item in game.current_store_items.values():
            message += f'{item.name} for {str(item.price)}\n'

    
