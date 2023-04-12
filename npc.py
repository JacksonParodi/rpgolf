import pygame
from constants import *

class NPC:
    def __init__(self, name, img, speak_func=None, x=GRID_WIDTH // 2, y=GRID_HEIGHT // 2):
        self.name = name
        self.x = x
        self.y = y
        self.img = pygame.image.load(img).convert_alpha()
        self.current_block = None
        self.talking = False
        self.speak_func = speak_func
        self.current_message = ''
        self.frame_count = 0

    def update_speak(self):
        self.current_message = self.speak_func()

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