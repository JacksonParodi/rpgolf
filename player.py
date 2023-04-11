from constants import *

class Player:
    def __init__(self, x = (WIDTH // 2), y = (HEIGHT // 2)):
        self.name = ''
        self.img = pygame.image.load('assets/png/player.png').convert_alpha()
        self.inventory = []
        self.exp = 0
        self.last_earned_exp = 0
        self.current_block = None
        self.shot_power = 1
        self.current_stroke_count = 0
        self.current_course_difficulty = 0
        self.courses_completed = 0

    def earn_exp_from_course(self):
        # difficulty is int 0-9, higher is harder
        exp_gained = (100 * (self.current_course_difficulty + 1)) - (self.current_stroke_count * 25)
        if exp_gained < 0:
            exp_gained = 0
        self.exp += exp_gained
        self.last_earned_exp = exp_gained
        return exp_gained

    def get_neighbors(self, grid):
        """
        returns list of Blocks neighboring player
        """
        neighbors = []
        
        if self.x < GRID_WIDTH - 2:
            neighbors.append(grid[self.y][self.x+1])
        if self.x > 1:
            neighbors.append(grid[self.y][self.x-1])
        if self.y < GRID_HEIGHT - 2:
            neighbors.append(grid[self.y+1][self.x])
        if self.y > 1:
            neighbors.append(grid[self.y-1][self.x])
        
        return neighbors

    def draw(self, surface, x, y):
        surface.blit(self.img, (x, y))