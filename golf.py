from constants import *

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

all_golf_features = {
    "ball": GolfFeature(name="ball", img='assets/png/golf_ball.png'),
    "flag": GolfFeature(name="flag", img='assets/png/flag.png'),
    "tee": GolfFeature(name="tee", img='assets/png/tee.png')
    }