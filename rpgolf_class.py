import pygame
import opensimplex
from rpgolf_const import *

class Game:
    def __init__(self):
        self.possible_game_states = [0,1,2,3]
        # 0 = main menu / 1 = RPG / 2 = golf / 3 = results
        self.game_state = self.possible_game_states[0]
        self.menu_text = ['welcome to golfing', 'press 1 to golf']
        self.current_NPCs = []
        self.all_NPCs = {}
        self.all_golf_features = {}
        self.current_golf_course = None
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('C:\\Windows\\Fonts\\CascadiaMono.ttf', 16)
        self.menu_grid = None
        self.menu_blocks_to_color = []
        self.new_blocks_to_color = []
        self.gradient_frame_offset = 0
        self.rpg_grid = None
        self.flags = {
            "first_talked_to_gwendolina": False,
            "first_talked_to_omar": False,
            "no_move": False,
            "can_shift_modes": True,
            "current_course_won": False,
            "getting_ball_trajectory": False
            }

class FracNoiseAlgo:
    def __init__(self):
        self.seed = opensimplex.random_seed()
        self.min_block_heat = MIN_BLOCK_HEAT
        self.max_block_heat = MAX_BLOCK_HEAT
        self.amplitude = AMPLITUDE
        self.frequency = FREQUENCY
        self.octaves = OCTAVES
        self.lacunarity = LACUNARITY
        self.persistence = PERSISTENCE

class MenuBlock:
    def __init__(self, x, y, color=[0,0,128], size=BLOCK_SIZE):
        self.x = x
        self.y = y
        self.color = pygame.Color(color[0], color[1], color[2])
        self.is_changing_color = False
        self.size = size

    def get_neighbors(self, grid):
        neighbors = []
        if self.x < GRID_WIDTH - 1:
            neighbors.append(grid[self.x + 1][self.y])
        if self.x > 0:
            neighbors.append(grid[self.x - 1][self.y])
        if self.y < GRID_HEIGHT - 1:
            neighbors.append(grid[self.x][self.y + 1])
        if self.y > 0:
            neighbors.append(grid[self.x][self.y - 1])
        return neighbors

    def draw(self, surface):
        block_rect = pygame.Rect((self.x * BLOCK_SIZE, self.y * BLOCK_SIZE), (self.size, self.size))
        pygame.draw.rect(surface=surface, color=self.color, rect=block_rect)

class Block:
    def __init__(self, x, y, heat=AMPLITUDE, size=BLOCK_SIZE):
        self.x = x
        self.y = y
        self.size = size
        self.heat = heat
        self.terrain = self.get_block_terrain(self.heat)
        self.color = self.get_block_color(self.terrain)
        self.content = None

    def heat_update(self):
        self.terrain = self.get_block_terrain(self.heat)
        self.color = self.get_block_color(self.terrain)

    def get_block_color(self, terrain):
        if terrain == 'deep_ocean':
            color = 'darkblue'
        if terrain == 'ocean':
            color = 'midnightblue'
        if terrain == 'beach':
            color = 'tan'
        if terrain == 'grassland':
            color = 'forestgreen'
        return color

    def get_block_terrain(self, heat):
        heat_percent = int((heat / MAX_BLOCK_HEAT) * 100)
        if heat_percent < 20:
            terrain = 'deep_ocean'
        elif heat_percent < 50:
            terrain = 'ocean'
        elif heat_percent < 58:
            terrain = 'beach'
        elif heat_percent >= 58:
            terrain = 'grassland'    
        else:
            terrain = 'error'
        return terrain

    def draw(self, surface):
        block_rect = pygame.Rect((self.x * BLOCK_SIZE, self.y * BLOCK_SIZE), (self.size, self.size))
        pygame.draw.rect(surface=surface, color=self.color, rect=block_rect)
        if self.content:
            self.content.draw(surface=surface, x=self.x * BLOCK_SIZE, y=self.y * BLOCK_SIZE)

class Player:
    def __init__(self, x = (WIDTH // 2), y = (HEIGHT // 2)):
        self.x = x
        self.y = y
        self.img = pygame.image.load('assets/png/player.png').convert_alpha()
        self.inventory = []
        self.exp = 0
        self.last_earned_exp = 0
        self.current_block = None
        self.shot_power = None
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

    def draw(self, surface, x, y):
        surface.blit(self.img, (x, y))

class NPC:
    def __init__(self, name, img, speak_func):
        self.name = name
        self.img = pygame.image.load(img).convert_alpha()
        self.current_block = None
        self.speak_func = speak_func
        self.talking = False
        self.current_message = 'hello golfer'

    def draw(self, surface, x, y):
        surface.blit(self.img, (x, y))

    def update_current_message(self):
        self.current_message = self.speak_func()

    def draw_speech(self, message, game):
        draw_message = game.font.render(message, False, 'white', 'black')
        game.text_hopper = draw_message

class GolfFeature:
    def __init__(self, name, img):
        self.name = name
        self.img = pygame.image.load(img).convert_alpha()
    
    def draw(self, surface, x, y):
        surface.blit(self.img, (x*BLOCK_SIZE, y*BLOCK_SIZE))

class GolfCourse:
    def __init__(self, grid, difficulty = 0):
        self.grid = grid
        self.difficulty = difficulty
        self.tee = None
        self.tee_x, self.tee_y = 0,0
        self.ball = None
        self.ball_x, self.ball_y = 0,0
        self.flag = None
        self.flag_x, self.flag_y = 0,0
        self.new_ball_x, self.new_ball_y = 0,0
        self.trajectory_frame_offset = 0
        self.ball_trajectory_points = []