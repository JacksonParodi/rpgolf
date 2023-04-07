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
            row.append(Block(x=x, y=y, heat=1))
        grid.append(row)
    return grid

def gen_menu_grid():
    grid = []
    for y in range(0, GRID_HEIGHT):
        row = []
        for x in range(0, GRID_WIDTH):
            row.append(MenuBlock(x=x, y=y, gradient_index=0))
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
            # int(max(fnoise.min_block_heat, min(elevation, fnoise.max_block_heat)))
            row.append(Block(x=x, y=y, heat=heat))
        grid.append(row)
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
        message = 'hello, golfer. my name is Gwendolina'
        game.flags["first_talked_to_gwendolina"] = True
    elif player.courses_completed == 1:
        message = 'you\'ve completed your first course! how charming'
        game.flags["can_shift_modes"] = True
    elif game.flags["first_talked_to_gwendolina"]:
        message = 'good to see you again, golfer. press 2 to golf'
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
    game.game_state = game.possible_game_states[1]
    if not game.rpg_grid:
        game.rpg_grid = gen_fnoise_grid()
        player.current_block = get_random_nonwater_block_from_grid(game.rpg_grid)
        player.x, player.y = player.current_block.x, player.current_block.y
        player.current_block.content = player

        game.current_NPCs.append(game.all_NPCs["gwendolina"])
        for npc in game.current_NPCs:
            block = get_random_nonwater_block_from_grid(game.rpg_grid)
            npc.x, npc.y = block.x, block.y
            block.content = npc

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

    draw_text_box(screen=screen, message=f'you won in {player.current_stroke_count} strokes and earned {player.last_earned_exp} exp! press backspace to return')

def draw_golf():
    for row in game.current_golf_course.grid:
        for block in row:
            block.draw(screen)

    game.current_golf_course.flag.draw(surface=screen, x=game.current_golf_course.flag_x, y=game.current_golf_course.flag_y)
    game.current_golf_course.ball.draw(surface=screen, x=game.current_golf_course.ball_x, y=game.current_golf_course.ball_y)
    if (game.current_golf_course.ball_x, game.current_golf_course.ball_y) != (game.current_golf_course.tee_x, game.current_golf_course.tee_y):
        game.current_golf_course.tee.draw(surface=screen, x=game.current_golf_course.tee_x, y=game.current_golf_course.tee_y)

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
 
    start_color=[0,96,128]
    end_color=[0,128,96]

    color_gradient = get_2color_gradient(start_color=start_color, end_color=end_color, steps=128)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            game.gradient_frame_offset = game.gradient_frame_offset % len(color_gradient)
            color_index = y + x + game.gradient_frame_offset
            color_index = color_index % len(color_gradient)
            game.menu_grid[y][x].color = color_gradient[color_index]
    game.gradient_frame_offset += 1

    line_y = 0
    for line in game.menu_text:
        rendered_line = game.font.render(line, False, 'silver')
        line_width, line_height = rendered_line.get_width(), rendered_line.get_height()
        screen.blit(rendered_line, (((WIDTH // 2) - (line_width // 2)), ((HEIGHT // 2) + (2* line_y))))
        line_y += line_height

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
                    print('power', player.shot_power)
                    if player.shot_power:
                        print('pre-shot', game.current_golf_course.ball_x, game.current_golf_course.ball_y)
                        x_part, y_part = swing(power=player.shot_power,
                                                ball_x=game.current_golf_course.ball_x, ball_y=game.current_golf_course.ball_y,
                                                flag_x=game.current_golf_course.flag_x, flag_y = game.current_golf_course.flag_y)
                        player.shot_power = None
                        player.current_stroke_count += 1

                        new_ball_x = game.current_golf_course.ball_x + x_part
                        new_ball_y = game.current_golf_course.ball_y + y_part
                        new_ball_x = clamp_to_int(new_ball_x, 0, GRID_WIDTH - 1)
                        new_ball_y = clamp_to_int(new_ball_y, 0, GRID_HEIGHT - 1)

                        if game.current_golf_course.grid[new_ball_y][new_ball_x].terrain in WATER_TERRAINS:
                            print('in the drink')
                            game.current_golf_course.ball_x, game.current_golf_course.ball_y = game.current_golf_course.tee_x, game.current_golf_course.tee_y
                        else:
                            game.current_golf_course.ball_x, game.current_golf_course.ball_y = new_ball_x, new_ball_y
                        print('post-shot', game.current_golf_course.ball_x, game.current_golf_course.ball_y)
                        if game.current_golf_course.ball_x == game.current_golf_course.flag_x and game.current_golf_course.ball_y == game.current_golf_course.flag_y:
                            print('you win')
                            
                            game.flags["can_shift_modes"] = True
                            shift_to_results()

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

    pygame.display.update()
    game.clock.tick(FPS)