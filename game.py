from constants import *
from rooms import OVERWORLD

class Game:
    def __init__(self):
        self.possible_game_states = [0,1,2,3]
        # 0 = main menu / 1 = RPG / 2 = golf / 3 = results
        self.game_state = self.possible_game_states[0]
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.menu_text = 'welcome to golfing\n\n\npress 1 to golf'
        self.current_NPCs = {}
        self.current_store_items = {}
        self.all_NPCs = {}
        self.current_rpg_features = {}
        self.all_store_items = {}
        self.current_golf_course = None
        self.clock = pygame.time.Clock()
        self.font = pygame.image.load('assets/png/font.png').convert_alpha()
        self.pix_font_rect = self.font.get_rect()
        self.menu_grid = []
        self.menu_blocks_to_color = []
        self.new_blocks_to_color = []
        self.gradient_frame_offset = 0
        """
        y, x for overworld idx
        """
        self.current_overworld_idx = [2,2]
        self.current_room = OVERWORLD[self.current_overworld_idx[1]][self.current_overworld_idx[0]]
        self.rpg_grid = None
        self.flags = {
            "first_talked_to_gwendolina": False,
            "first_talked_to_omar": False,
            "no_move": False,
            "can_shift_modes": True,
            "current_course_won": False,
            "getting_ball_trajectory": False,
            "showing_status": False,
            "ball_in_water": False,
            "sploosh_sound_played": False,
            "game_complete": False
            }

    def update_current_room(self):
        self.current_room = OVERWORLD[self.current_overworld_idx[1]][self.current_overworld_idx[0]]
        self.current_rpg_color_grid = self.current_room.color_grid