import sys
import time
import math
import random
import pygame
import opensimplex
from util import *
from classes import *
from constants import *
from resources import *

pygame.init()
game = Game()
player = Player()
game.screen.fill('black')
pygame.display.set_caption('rpgolf')

pix_font = pygame.image.load('assets/png/font.png').convert_alpha()
pix_font_rect = pix_font.get_rect()

def gen_flat_grid():
    grid = []
    for y in range(0, GRID_HEIGHT):
        row = []
        for x in range(0, GRID_WIDTH):
            row.append(Block(x=x, y=y))
        grid.append(row)
    return grid

def gen_menu_grid():
    grid = []
    for y in range(0, GRID_HEIGHT):
        row = []
        for x in range(0, GRID_WIDTH):
            row.append(MenuBlock(x=x, y=y))
        grid.append(row)
    return grid

def gen_fnoise_grid():
    fnoise = FracNoiseAlgo()
    grid = []
    for y in range(0, GRID_HEIGHT):
        row = []
        for x in range(0, GRID_WIDTH):
            elevation = fnoise.amplitude
            t_freq = fnoise.frequency
            t_amp = fnoise.amplitude
            for k in range(fnoise.octaves):
                sample_x = x * t_freq
                sample_y = y * t_freq
                elevation += opensimplex.noise2(x = sample_x, y = sample_y) * t_amp
                t_freq *= fnoise.lacunarity
                t_amp *= fnoise.persistence
            heat = clamp_to_int(elevation, fnoise.min_block_heat, fnoise.max_block_heat)
            row.append(Block(x=x, y=y, heat=heat))
        grid.append(row)
    return grid

def gen_country_club():
    grid = gen_flat_grid()

    for row in grid:
        for block in row:
            block.heat = MAX_BLOCK_HEAT // 2
            if block.x in range(4) or block.x in range((GRID_WIDTH - 4), GRID_WIDTH) or block.y in range(4) or block.y in range((GRID_HEIGHT - 4), GRID_HEIGHT):
                block.heat = 1
                block.heat_update()

    return grid

def gen_golf_features(course):
    game.current_golf_course.tee = game.all_golf_features["tee"]
    game.current_golf_course.ball = game.all_golf_features["ball"]
    game.current_golf_course.flag = game.all_golf_features["flag"]

    tee_block = get_random_nonwater_block_from_grid(course.grid)
    flag_block = get_random_nonwater_block_from_grid(course.grid)
    while tee_block == flag_block:
        flag_block = get_random_nonwater_block_from_grid(course.grid)

    course.tee_x, course.tee_y = tee_block.x, tee_block.y
    course.ball_x, course.ball_y = tee_block.x, tee_block.y
    course.flag_x, course.flag_y = flag_block.x, flag_block.y
    return course

def get_random_nonwater_block_from_grid(grid):
    random_row = random.choice(grid)
    random_block = random.choice(random_row)
    while random_block.terrain in WATER_TERRAINS or random_block.content:
        random_row = random.choice(grid)
        random_block = random.choice(random_row)
    return random_block

def gwendolina_speak():
    message = 'good to see you, golfer'

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
    
    return message

def omar_speak():
    message = 'hey, golfer'

    if not game.flags["first_talked_to_omar"]:
        message = 'hey, golfer. i am omar'
        game.flags["first_talked_to_omar"] = True
    elif game.flags["first_talked_to_omar"]:
        message = 'what is up, golfer'

    return message

def shift_to_rpg():
    game.flags["no_move"] = False
    game.flags["can_shift_modes"] = False
    game.game_state = game.possible_game_states[1]

def shift_to_golf():
    game.flags["can_shift_modes"] = False
    player.current_stroke_count = 0
    player.current_course_difficulty = 0

    for each_npc in game.current_NPCs.values():
        each_npc.talking = False
    
    grid = gen_fnoise_grid()
    game.current_golf_course = GolfCourse(grid=grid)
    game.current_golf_course = gen_golf_features(game.current_golf_course)

    game.game_state = game.possible_game_states[2]

def shift_to_results():
    game.flags["can_shift_modes"] = True
    game.flags["current_course_won"] = False
    player.earn_exp_from_course()
    player.courses_completed += 1

    game.game_state = game.possible_game_states[3]

def get_2color_gradient(start_color, end_color, steps):
    gradient = []

    difference = []
    for start_element, end_element in zip(start_color, end_color):
        diff_element = end_element - start_element
        difference.append(diff_element)

    for step in range(steps):
        gradient_color = []
        for start_element, diff_element in zip(start_color, difference):
            gradient_element = start_element + (step * (diff_element / steps))
            gradient_color.append(int(gradient_element))
        gradient.append(gradient_color)

    for step in range(steps):
        gradient_color = []
        for end_element, diff_element in zip(end_color, difference):
            gradient_element = end_element - (step * (diff_element / steps))
            gradient_color.append(int(gradient_element))
        gradient.append(gradient_color)
    
    return gradient

def draw_font_char(char, x, y):
    char = char.lower()
    alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '?', ':', ',', '.', ' ']
    x_offset = 0
    y_offset = 0

    if char in alphabet:
        x_offset = alphabet.index(char) * BLOCK_SIZE
    if char in numbers:
        x_offset = numbers.index(char) * BLOCK_SIZE
        y_offset = 2 * BLOCK_SIZE
    if char in symbols:
        x_offset = symbols.index(char) * BLOCK_SIZE
        y_offset = 4 * BLOCK_SIZE

    selector_rect = pygame.Rect(0,0,BLOCK_SIZE,BLOCK_SIZE)
    selector_rect.x  += x_offset
    selector_rect.y += y_offset
    dest_rect = pygame.Rect(x,y,BLOCK_SIZE, BLOCK_SIZE)
    dest_rect.center = (x,y)
    game.screen.blit(pix_font, dest_rect, area=selector_rect)

def draw_font_message(message, x, y):
        """
        parameters:
            message (str)
            x (int)
            y (int)
        """
        message_list = message.splitlines()

        lines = len(message_list)
        chars_wide = 0
        for line in message_list:
            if len(line) > chars_wide:
                chars_wide = len(line)
        
        text_box_bg = pygame.Rect(0, 0, (chars_wide * BLOCK_SIZE) + (2 * BLOCK_SIZE), (lines * BLOCK_SIZE) + (2 * BLOCK_SIZE))
        text_box_bg.center = x, y
        pygame.draw.rect(game.screen, 'black', text_box_bg)

        x, y = (x - ((BLOCK_SIZE // 2) * chars_wide)), (y - ((BLOCK_SIZE // 2) * (lines - 1)))

        y_step = 0
        for line in message_list:
            x_step = 0
            for char in line:
                draw_font_char(char=char, x=x + (x_step * BLOCK_SIZE), y=y + (y_step * BLOCK_SIZE))
                x_step += 1
            y_step += 1

def draw_text_box(message):
    text_surface = game.font.render(message, False, 'silver')
    text_rect = text_surface.get_rect()
    text_rect.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(game.screen, 'black', (text_rect.left - 5, text_rect.top - 5, text_rect.width + 10, text_rect.height + 10))
    game.screen.blit(text_surface, text_rect)

def update_results():
    pass

def draw_results():
    for row in game.menu_grid:
        for block in row:
            block.draw(game.screen)

    two_color_gradient_anim(start_color=[128,0,0], end_color=[32,128,0], game=game)

    if game.flags["game_complete"]:
        draw_font_message(message='wow you won', x=WIDTH // 2, y=HEIGHT // 2)
    else:
        draw_text_box(message=f'you won in {player.current_stroke_count} strokes and earned {player.last_earned_exp} exp! press backspace to return')

def get_ball_trajectory_points(course):
    """
    Bresenham's Line Algorithm
    Produces a list of tuples from start and end

    >>> points1 = get_line((0, 0), (3, 4))
    >>> points2 = get_line((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print points1
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print points2
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = course.ball_x, course.ball_y
    x2, y2 = course.new_ball_x, course.new_ball_y
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points

def update_golf():
    if game.current_golf_course.ball_x == game.current_golf_course.new_ball_x and game.current_golf_course.ball_y == game.current_golf_course.new_ball_y:
        game.flags["getting_ball_trajectory"] = False
        game.current_golf_course.trajectory_frame_offset = 0
        game.current_golf_course.ball_trajectory_points = []

    if game.flags["getting_ball_trajectory"]:
        game.current_golf_course.ball_x, game.current_golf_course.ball_y = game.current_golf_course.ball_trajectory_points[game.current_golf_course.trajectory_frame_offset]
        if game.current_golf_course.trajectory_frame_offset < len(game.current_golf_course.ball_trajectory_points):
            game.current_golf_course.trajectory_frame_offset += 1

    if game.flags["getting_ball_trajectory"] == False:
        if game.current_golf_course.grid[game.current_golf_course.new_ball_y][game.current_golf_course.new_ball_x].terrain in WATER_TERRAINS:
            game.flags["ball_in_water"] = True

            if not game.flags["sploosh_sound_played"]:
                water_sploosh.play()
                game.flags["sploosh_sound_played"] = True
            game.current_golf_course.ball_x, game.current_golf_course.ball_y = game.current_golf_course.tee_x, game.current_golf_course.tee_y
        elif game.current_golf_course.ball_x == game.current_golf_course.flag_x and game.current_golf_course.ball_y == game.current_golf_course.flag_y:
            game.flags["current_course_won"] = True
            game.flags["getting_ball_trajectory"] = False
            game.flags["can_shift_modes"] = True

    player.shot_power = clamp_to_int(input=player.shot_power, min_value=1, max_value=100)

def draw_golf():
    for row in game.current_golf_course.grid:
        for block in row:
            block.draw(game.screen)

    game.current_golf_course.flag.draw(surface=game.screen, x=game.current_golf_course.flag_x, y=game.current_golf_course.flag_y)
    game.current_golf_course.ball.draw(surface=game.screen, x=game.current_golf_course.ball_x, y=game.current_golf_course.ball_y)
    if (game.current_golf_course.ball_x, game.current_golf_course.ball_y) != (game.current_golf_course.tee_x, game.current_golf_course.tee_y):
        game.current_golf_course.tee.draw(surface=game.screen, x=game.current_golf_course.tee_x, y=game.current_golf_course.tee_y)

    if player.shot_power != None:
        draw_text_box(message=f'shot power = {player.shot_power}')

    if game.flags["current_course_won"]:
        draw_text_box(message='you win! press space for results')

def update_rpg():
    if not game.flags["no_move"]:
        if game.flags["game_complete"]:
            shift_to_results()
        for each_npc in game.current_NPCs.values():
            if each_npc.frame_count > 240:
                rand_dx = random.randint(-1,1)
                rand_dy = random.randint(-1,1)
                each_npc.move(dx=rand_dx, dy=rand_dy, grid=game.rpg_grid)
                each_npc.frame_count = 0
            each_npc.frame_count += 1

def draw_rpg():
    for row in game.rpg_grid:
        for block in row:
            block.draw(game.screen)

    for each_npc in game.current_NPCs.values():
        if each_npc.talking:
            draw_font_message(message=each_npc.current_message, x=WIDTH // 2, y=BLOCK_SIZE * 8)

    for each_feature in game.current_rpg_features.values():
        if each_feature.describing:
            draw_font_message(message=each_feature.desc, x=WIDTH // 2, y=BLOCK_SIZE * 8)

    if game.flags["showing_status"]:
        draw_text_box(message=f'player exp: {player.exp} courses completed: {player.courses_completed}')

def update_menu():
    pass

def draw_menu():
    for row in game.menu_grid:
        for block in row:
            block.draw(game.screen)

    two_color_gradient_anim(start_color=[0,96,128], end_color=[0,128,96], game=game)

    draw_font_message(message=game.menu_text, x=(WIDTH // 2), y=(HEIGHT // 2))

def two_color_gradient_anim(start_color, end_color, game):

    color_gradient = get_2color_gradient(start_color=start_color, end_color=end_color, steps=128)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            game.gradient_frame_offset = game.gradient_frame_offset % len(color_gradient)
            color_index = y + x + game.gradient_frame_offset
            color_index = color_index % len(color_gradient)
            game.menu_grid[y][x].color = color_gradient[color_index]
    game.gradient_frame_offset += 1

def swing(power, ball_x, ball_y, flag_x, flag_y):
    angle = math.atan2(flag_y - ball_y, flag_x - ball_x)
    distance = math.dist((0, 0), (GRID_WIDTH, GRID_HEIGHT))
    x_part = int(round(math.cos(angle) * distance * (power / 100)))
    y_part = int(round(math.sin(angle) * distance * (power / 100)))
    return (x_part, y_part)

def game_init(game, player):
    game.menu_grid = gen_menu_grid()
    game.rpg_grid = gen_country_club()

    # game.all_golf_features = 

    game.all_NPCs = {
                    "gwendolina": NPC(name="Gwendolina", img='assets/png/npc2.png', speak_func=gwendolina_speak),
                    "omar": NPC(name="Omar", img='assets/png/npc3.png', speak_func=omar_speak)
                    }


    player.current_block = game.rpg_grid[GRID_WIDTH // 2][GRID_HEIGHT // 2]
    player.x, player.y = player.current_block.x, player.current_block.y
    player.current_block.content = player

    game.current_NPCs["gwendolina"] = game.all_NPCs["gwendolina"]
    game.current_NPCs["gwendolina"].current_block = game.rpg_grid[GRID_WIDTH // 2][(GRID_HEIGHT // 2) + 4]
    game.current_NPCs["gwendolina"].current_block.content = game.current_NPCs["gwendolina"]
    
    game.current_NPCs["omar"] = game.all_NPCs["omar"]
    game.current_NPCs["omar"].current_block = game.rpg_grid[GRID_WIDTH // 2][(GRID_HEIGHT // 2) - 4]
    game.current_NPCs["omar"].current_block.content = game.current_NPCs["omar"]

    game.current_rpg_features["portal1"] = game.all_rpg_features["portal1"]
    game.current_rpg_features["portal1"].current_block = game.rpg_grid[(GRID_WIDTH // 2) - 8][(GRID_HEIGHT // 2) - 6]
    game.current_rpg_features["portal1"].current_block.content = game.current_rpg_features["portal1"]

    game.current_rpg_features["portal2"] = game.all_rpg_features["portal2"]
    game.current_rpg_features["portal2"].current_block = game.rpg_grid[(GRID_WIDTH // 2) - 8][(GRID_HEIGHT // 2) - 2]
    game.current_rpg_features["portal2"].current_block.content = game.current_rpg_features["portal2"]

    game.current_rpg_features["portal3"] = game.all_rpg_features["portal3"]
    game.current_rpg_features["portal3"].current_block = game.rpg_grid[(GRID_WIDTH // 2) - 8][(GRID_HEIGHT // 2) + 2]
    game.current_rpg_features["portal3"].current_block.content = game.current_rpg_features["portal3"]

    game.current_rpg_features["portal4"] = game.all_rpg_features["portal4"]
    game.current_rpg_features["portal4"].current_block = game.rpg_grid[(GRID_WIDTH // 2) - 8][(GRID_HEIGHT // 2) + 6]
    game.current_rpg_features["portal4"].current_block.content = game.current_rpg_features["portal4"]

game_init(game, player)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            keys =  pygame.key.get_pressed()

            ### MAIN MENU MODE ###

            if game.game_state == game.possible_game_states[0]:
                if keys[pygame.K_1]:
                    start_game_chime.play()
                    shift_to_rpg()

            ### RPG MODE ###

            if game.game_state == game.possible_game_states[1]:
                new_player_x = player.x
                new_player_y = player.y

                if keys[pygame.K_i]:
                    game.flags["showing_status"] = not game.flags["showing_status"]
                    game.flags["no_move"] = game.flags["showing_status"]
                        
                if keys[pygame.K_UP]:
                    new_player_y -= 1
                    if new_player_y < 0:
                        new_player_y += GRID_HEIGHT
                    new_player_y = new_player_y % GRID_HEIGHT
                if keys[pygame.K_DOWN]:
                    new_player_y += 1
                    new_player_y = new_player_y % GRID_HEIGHT
                if keys[pygame.K_LEFT]:
                    new_player_x -= 1  
                    if new_player_x < 0:
                        new_player_x += GRID_WIDTH
                    new_player_x = new_player_x % GRID_WIDTH                 
                if keys[pygame.K_RIGHT]:
                    new_player_x += 1
                    new_player_x = new_player_x % GRID_WIDTH

                if keys[pygame.K_SPACE]:
                    for each_npc in game.current_NPCs.values():
                        if each_npc.talking:
                            each_npc.talking = False
                            game.flags["no_move"] = False
                        elif not each_npc.talking:
                            if each_npc.current_block in player.get_neighbors(game.rpg_grid):
                                each_npc.update_speak()
                                each_npc.talking = True
                                game.flags["no_move"] = True
                    for each_feature in game.current_rpg_features.values():
                        if each_feature.describing:
                            each_feature.describing = False
                            game.flags["no_move"] = False
                        elif not each_feature.describing:
                            if each_feature.current_block in player.get_neighbors(game.rpg_grid):
                                each_feature.describing = True
                                game.flags["no_move"] = True

                if game.rpg_grid[new_player_y][new_player_x].content == game.current_rpg_features["portal1"]:
                    shift_to_golf()
                if game.rpg_grid[new_player_y][new_player_x].content == game.current_rpg_features["portal2"] and player.courses_completed >= 1:
                    shift_to_golf()
                if game.rpg_grid[new_player_y][new_player_x].content == game.current_rpg_features["portal3"] and player.courses_completed >= 2:
                    shift_to_golf()
                if game.rpg_grid[new_player_y][new_player_x].content == game.current_rpg_features["portal4"] and player.courses_completed >= 3:
                    shift_to_golf()

                if game.rpg_grid[new_player_y][new_player_x].terrain not in WATER_TERRAINS and game.rpg_grid[new_player_y][new_player_x].content == None and game.flags["no_move"] == False:
                    player.x, player.y = new_player_x, new_player_y
                    player.current_block.content = None
                    player.current_block = game.rpg_grid[new_player_y][new_player_x]
                    player.current_block.content = player

                if keys[pygame.K_2]:
                    if game.flags["can_shift_modes"] and not game.flags["no_move"]:
                        shift_to_golf()

            ### GOLF MODE ###

            if game.game_state == game.possible_game_states[2]:

                if keys[pygame.K_UP]:
                    player.shot_power += 1
                if keys[pygame.K_DOWN]:
                    player.shot_power -= 1
                if keys[pygame.K_RIGHT]:
                    player.shot_power += 10
                if keys[pygame.K_LEFT]:
                    player.shot_power -= 10         

                if keys[pygame.K_SPACE]:
                    if game.flags["current_course_won"]:
                        shift_to_results()
                    elif player.shot_power:
                        game.flags["sploosh_sound_played"] = False
                        x_part, y_part = swing(power=player.shot_power,
                                                ball_x=game.current_golf_course.ball_x, ball_y=game.current_golf_course.ball_y,
                                                flag_x=game.current_golf_course.flag_x, flag_y = game.current_golf_course.flag_y)
                        player.shot_power = 1
                        player.current_stroke_count += 1

                        game.current_golf_course.new_ball_x = game.current_golf_course.ball_x + x_part
                        game.current_golf_course.new_ball_y = game.current_golf_course.ball_y + y_part
                        game.current_golf_course.new_ball_x = clamp_to_int(game.current_golf_course.new_ball_x, 0, GRID_WIDTH - 1)
                        game.current_golf_course.new_ball_y = clamp_to_int(game.current_golf_course.new_ball_y, 0, GRID_HEIGHT - 1)

                        game.flags["getting_ball_trajectory"] = True

                        game.current_golf_course.ball_trajectory_points = get_ball_trajectory_points(game.current_golf_course)
                        
            ### RESULTS MODE ###

            if game.game_state == game.possible_game_states[3]:
                if keys[pygame.K_BACKSPACE]:
                    shift_to_rpg()

    if game.game_state == game.possible_game_states[0]:
        update_menu()
        draw_menu()
    if game.game_state == game.possible_game_states[1]:
        update_rpg()
        draw_rpg()
    if game.game_state == game.possible_game_states[2]:
        update_golf()
        draw_golf()
    if game.game_state == game.possible_game_states[3]:
        update_results()
        draw_results()

    pygame.display.update()
    game.clock.tick(FPS)