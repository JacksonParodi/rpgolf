import sys
import time
import math
import random
import pygame
import opensimplex
from rpgolf_util import *
from rpgolf_class import *
from rpgolf_const import *

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill('blue')
pygame.display.set_caption('rpgolf')
WATER_TERRAINS = ['ocean', 'deep_ocean']

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
    if game.flags["first_talked_to_gwendolina"] == False:
        message = 'welcome to the desert of the real'
        game.flags["first_talked_to_gwendolina"] = True
    elif player.courses_completed == 1:
        message = 'you\'ve completed your first course! how charming'
        game.flags["can_shift_modes"] = True
    elif game.flags["first_talked_to_gwendolina"]:
        message = 'there is no going back. press 2 to golf'
        game.flags["can_shift_modes"] = True
    return message

def omar_speak():
    if game.flags["first_talked_to_omar"] == False:
        message = 'hey, golfer. i\'m omar'
        game.flags["first_talked_to_omar"] = True
    elif game.flags["first_talked_to_omar"]:
        message = 'what\'s up, golfer'
    return message

def shift_to_rpg():
    game.flags["no_move"] = False
    game.flags["can_shift_modes"] = False

    game.rpg_grid = gen_country_club()

    player.current_block = game.rpg_grid[GRID_WIDTH // 2][GRID_HEIGHT // 2]
    player.x, player.y = player.current_block.x, player.current_block.y
    player.current_block.content = player

    if game.all_NPCs["gwendolina"] not in game.current_NPCs:
        game.current_NPCs.append(game.all_NPCs["gwendolina"])
    
    game.current_NPCs[0].current_block = game.rpg_grid[(GRID_WIDTH // 2) + 4][GRID_HEIGHT // 2]
    game.current_NPCs[0].x, game.current_NPCs[0].y = game.current_NPCs[0].current_block.x, game.current_NPCs[0].current_block.y
    game.current_NPCs[0].current_block.content = game.current_NPCs[0]

    game.game_state = game.possible_game_states[1]

def shift_to_golf():
    game.flags["can_shift_modes"] = False
    player.current_stroke_count = 0
    player.current_course_difficulty = 0

    for each_npc in game.current_NPCs:
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

def draw_text_box(screen, message):
    text_surface = game.font.render(message, False, 'silver')
    text_rect = text_surface.get_rect()
    text_rect.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, 'black', (text_rect.left - 5, text_rect.top - 5, text_rect.width + 10, text_rect.height + 10))
    screen.blit(text_surface, text_rect)

def draw_results():
    for row in game.menu_grid:
        for block in row:
            block.draw(screen)

    two_color_gradient_anim(start_color=[128,0,0], end_color=[32,128,0], game=game)

    draw_text_box(screen=screen, message=f'you won in {player.current_stroke_count} strokes and earned {player.last_earned_exp} exp! press backspace to return')

def get_ball_trajectory_points(course):

    """Bresenham's Line Algorithm
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

def draw_golf():
    for row in game.current_golf_course.grid:
        for block in row:
            block.draw(screen)

    game.current_golf_course.flag.draw(surface=screen, x=game.current_golf_course.flag_x, y=game.current_golf_course.flag_y)
    game.current_golf_course.ball.draw(surface=screen, x=game.current_golf_course.ball_x, y=game.current_golf_course.ball_y)
    if (game.current_golf_course.ball_x, game.current_golf_course.ball_y) != (game.current_golf_course.tee_x, game.current_golf_course.tee_y):
        game.current_golf_course.tee.draw(surface=screen, x=game.current_golf_course.tee_x, y=game.current_golf_course.tee_y)

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
            print('in the drink')
            game.current_golf_course.ball_x, game.current_golf_course.ball_y = game.current_golf_course.tee_x, game.current_golf_course.tee_y
        elif game.current_golf_course.ball_x == game.current_golf_course.flag_x and game.current_golf_course.ball_y == game.current_golf_course.flag_y:
            print('you win')
            game.flags["current_course_won"] = True
            game.flags["can_shift_modes"] = True

    if player.shot_power != None:
        draw_text_box(screen=screen, message=f'shot power = {player.shot_power}')

    if game.flags["current_course_won"]:
        draw_text_box(screen=screen, message='you win! press space for results')

def draw_rpg():
    for row in game.rpg_grid:
        for block in row:
            block.draw(screen)

    for NPC in game.current_NPCs:
        if NPC.talking:
            message = NPC.current_message
            draw_text_box(screen=screen, message=message)

def draw_menu():
    for row in game.menu_grid:
        for block in row:
            block.draw(screen)

    two_color_gradient_anim(start_color=[0,96,128], end_color=[0,128,96], game=game)

    line_y = 0
    for line in game.menu_text:
        rendered_line = game.font.render(line, False, 'silver')
        line_width, line_height = rendered_line.get_width(), rendered_line.get_height()
        screen.blit(rendered_line, (((WIDTH // 2) - (line_width // 2)), ((HEIGHT // 2) + (2* line_y))))
        line_y += line_height

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

game = Game()
player = Player()
game.menu_grid = gen_menu_grid()

game.all_golf_features = {
                        "ball": GolfFeature(name="ball", img='assets/png/golf_ball.png'),
                        "flag": GolfFeature(name="flag", img='assets/png/flag.png'),
                        "tee": GolfFeature(name="tee", img='assets/png/tee.png')
                        }

game.all_NPCs = {
                "gwendolina": NPC(name="Gwendolina", img='assets/png/npc2.png', speak_func=gwendolina_speak),
                "omar": NPC(name="Omar", img='assets/png/npc3.png', speak_func=omar_speak)
                }

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
                    shift_to_rpg()

            ### RPG MODE ###

            if game.game_state == game.possible_game_states[1]:
                new_player_x = player.x
                new_player_y = player.y

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
                    for each_npc in game.current_NPCs:
                        if each_npc.talking:
                            each_npc.talking = False
                            game.flags["no_move"] = False
                        elif each_npc.talking == False:
                            for y in [-1,0,1]:
                                for x in [-1,0,1]:
                                    if game.rpg_grid[new_player_y + y][new_player_x + x].content:
                                        if isinstance(game.rpg_grid[new_player_y + y][new_player_x + x].content, NPC):
                                            game.rpg_grid[new_player_y + y][new_player_x + x].content.talking = True
                                            game.rpg_grid[new_player_y + y][new_player_x + x].content.update_current_message()
                                            game.flags["no_move"] = True

                if game.rpg_grid[new_player_y][new_player_x].terrain not in WATER_TERRAINS and game.rpg_grid[new_player_y][new_player_x].content == None and game.flags["no_move"] == False:
                    player.x, player.y = new_player_x, new_player_y
                    player.current_block.content = None
                    player.current_block = game.rpg_grid[new_player_y][new_player_x]
                    player.current_block.content = player

                if keys[pygame.K_2]:
                    if game.flags["can_shift_modes"]:
                        shift_to_golf()

            ### GOLF MODE ###

            if game.game_state == game.possible_game_states[2]:
                
                if keys[pygame.K_KP_0]:
                    if player.shot_power == None:
                        player.shot_power = 0
                    elif player.shot_power == 0:
                        player.shot_power = 100
                    elif player.shot_power >= 1 and player.shot_power <= 9:
                        player.shot_power = player.shot_power * 10
                if keys[pygame.K_KP1]:
                    if player.shot_power == None:
                        player.shot_power = 1
                    elif player.shot_power >=0 and player.shot_power <= 9:
                        player.shot_power = (player.shot_power * 10) + 1
                if keys[pygame.K_KP2]:
                    if player.shot_power == None:
                        player.shot_power = 2
                    elif player.shot_power >=0 and player.shot_power <= 9:
                        player.shot_power = (player.shot_power * 10) + 2
                if keys[pygame.K_KP3]:
                    if player.shot_power == None:
                        player.shot_power = 3
                    elif player.shot_power >=0 and player.shot_power <= 9:
                        player.shot_power = (player.shot_power * 10) + 3
                if keys[pygame.K_KP4]:
                    if player.shot_power == None:
                        player.shot_power = 4
                    elif player.shot_power >=0 and player.shot_power <= 9:
                        player.shot_power = (player.shot_power * 10) + 4
                if keys[pygame.K_KP5]:
                    if player.shot_power == None:
                        player.shot_power = 5
                    elif player.shot_power >=0 and player.shot_power <= 9:
                        player.shot_power = (player.shot_power * 10) + 5
                if keys[pygame.K_KP6]:
                    if player.shot_power == None:
                        player.shot_power = 6
                    elif player.shot_power >=0 and player.shot_power <= 9:
                        player.shot_power = (player.shot_power * 10) + 6
                if keys[pygame.K_KP7]:
                    if player.shot_power == None:
                        player.shot_power = 7
                    elif player.shot_power >=0 and player.shot_power <= 9:
                        player.shot_power = (player.shot_power * 10) + 7
                if keys[pygame.K_KP8]:
                    if player.shot_power == None:
                        player.shot_power = 8
                    elif player.shot_power >=0 and player.shot_power <= 9:
                        player.shot_power = (player.shot_power * 10) + 8
                if keys[pygame.K_KP9]:
                    if player.shot_power == None:
                        player.shot_power = 9
                    elif player.shot_power >=0 and player.shot_power <= 9:
                        player.shot_power = (player.shot_power * 10) + 9

                if keys[pygame.K_SPACE]:
                    if game.flags["current_course_won"]:
                        shift_to_results()
                    if player.shot_power:
                        x_part, y_part = swing(power=player.shot_power,
                                                ball_x=game.current_golf_course.ball_x, ball_y=game.current_golf_course.ball_y,
                                                flag_x=game.current_golf_course.flag_x, flag_y = game.current_golf_course.flag_y)
                        player.shot_power = None
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
        draw_menu()
    if game.game_state == game.possible_game_states[1]:
        draw_rpg()
    if game.game_state == game.possible_game_states[2]:
        draw_golf()
    if game.game_state == game.possible_game_states[3]:
        draw_results()

    print(game.flags["getting_ball_trajectory"])
    pygame.display.update()
    game.clock.tick(FPS)