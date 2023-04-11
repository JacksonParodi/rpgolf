from constants import *

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

class ColorBlock:
    def __init__(self, x, y, color=[0,0,128], size=BLOCK_SIZE):
        self.x = x
        self.y = y
        self.color = pygame.Color(color[0], color[1], color[2])
        self.is_changing_color = False
        self.size = size
        self.content = None

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

class TerrainBlock:
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