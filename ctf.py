import pygame
import os
from pygame.locals import *
from pygame.color import *
import pymunk
import sounds
import sys

# -- Import from the ctf framework
# The framework needs to be imported after initialisation of pygame
import ai
import images
import gameobjects
import maps
import menu

""" Main file for the game.
"""

# ----- Initialisation ----- #

# -- Initialise the display
pygame.mixer.init()

pygame.init()
pygame.display.set_mode()
os.environ['SDL_VIDEO_CENTERED'] = '1'

# -- Initialise the clock
clock = pygame.time.Clock()

# -- Initialise the physics engine
space = pymunk.Space()
space.gravity = (0.0, 0.0)
space.damping = 0.1  # Adds friction to the ground for all objects
minispace = pymunk.Space()

# -- Constants
FRAMERATE = 50

#   Define the current level
current_map = maps.map0

#  List of all game objects
game_objects_list = []
tanks_list = []
bases_list = []
explosion_list = []
explosion_timer = []
ai_list = []

#   collision cases and collision handlers


def collision_bullet_tank(arb, space, data):
    """Handles what happens during collision between bullet and tank"""
    if arb.shapes[0].parent not in game_objects_list:
        return False
    else:
        if not arb.shapes[1].parent.invincible:
            explode(arb.shapes[0].body.position.x, arb.shapes[0].body.position.y)
            sounds.tank_shot.play()
            game_objects_list.remove(arb.shapes[0].parent)
            space.remove(arb.shapes[0], arb.shapes[0].body)
            for ai in ai_list:
                if ai.tank == arb.shapes[1].parent:
                    ai.reset_cycle()
            arb.shapes[1].parent.respawn(space, current_map, flag)
            return False
        else:
            game_objects_list.remove(arb.shapes[0].parent)
            space.remove(arb.shapes[0], arb.shapes[0].body)
            return False


def collision_bullet_anything(arb, space, data):
    """Handles  what happens during collision between bullet and boxes"""
    if arb.shapes[0].parent not in game_objects_list:
        return False
    else:
        sounds.rock_metal_impact_sfx.play()
        game_objects_list.remove(arb.shapes[0].parent)
        space.remove(arb.shapes[0], arb.shapes[0].body)
        if arb.shapes[1].parent.destructable:
            explode(arb.shapes[0].body.position.x, arb.shapes[0].body.position.y)
            sounds.wood_box_destroyed_sfx.play()
            game_objects_list.remove(arb.shapes[1].parent)
            space.remove(arb.shapes[1], arb.shapes[1].body)
        return False


def collision_bullet_bullet(arb, space, data):
    """Handles what happens during collision between bullet and bullet"""
    if arb.shapes[0].parent not in game_objects_list:
        return False
    else:
        explode(arb.shapes[0].body.position.x, arb.shapes[0].body.position.y)
        sounds.rock_metal_impact_sfx.play()
        game_objects_list.remove(arb.shapes[0].parent)
        space.remove(arb.shapes[0], arb.shapes[0].body)
        game_objects_list.remove(arb.shapes[1].parent)
        space.remove(arb.shapes[1], arb.shapes[1].body)
        return False


# Create all collisionhandlers and pre_solvers
handler = space.add_collision_handler(1, 2)
handler2 = space.add_collision_handler(1, 3)
handler3 = space.add_collision_handler(1, 1)
handler.pre_solve = collision_bullet_tank
handler2.pre_solve = collision_bullet_anything
handler3.pre_solve = collision_bullet_bullet

# Resize the screen to the size of the current level
screen = pygame.display.set_mode(current_map.rect().size)
# -- Generate the background
background = pygame.Surface((screen.get_size()))
# ----- Create menu screens -----
main = menu.Main_Menu(screen, current_map)
mapmen = menu.Map_Menu(screen, current_map, background)

# -- set gamemode to 1 (singleplayer)
gamemode = 1


def create_border():
    """Makes a border around the map consisting of 4 separate static lines"""
    static_body = space.static_body
    static_lines = [
        # Upper border
        pymunk.Segment(static_body, (0, 0), (current_map.width, 0), 0),
        # Left side border
        pymunk.Segment(static_body, (0, 0), (0, current_map.height), 0),
        # Lower border
        pymunk.Segment(static_body, (0, current_map.height), (current_map.width, current_map.height), 0),
        # Rigth side border
        pymunk.Segment(static_body, (current_map.width, 0), (current_map.width, current_map.height), 0),
    ]

    for line in static_lines:
        line.elasticity = 0
        line.friction = 0

    space.add(*static_lines)


def create_grass():
    """Copies the grass tile all over the level area"""
    for x in range(0, current_map.width):
        for y in range(0, current_map.height):
            # The call to the function "blit" will copy the image
            # contained in "images.grass" into the "background"
            # image at the coordinates given as the second argument
            background.blit(images.grass, (x * images.TILE_SIZE, y * images.TILE_SIZE))


def create_boxes():
    """Creates the boxes for the current map"""
    for x in range(0, current_map.width):
        for y in range(0, current_map.height):
            # Get the type of boxes
            box_type = current_map.boxAt(x, y)
            # If the box type is not 0 (aka grass tile), create a box
            if box_type != 0:
                # Create a "Box" using the box_type, aswell as the x,y coordinates,
                # and the pymunk space
                box = gameobjects.get_box_with_type(x, y, box_type, space)
                game_objects_list.append(box)


def create_tanks():
    """Creates tanks and AI"""
    # Loop over the starting poistion
    for i in range(0, len(current_map.start_positions)):
        # Get the starting position of the tank "i"
        pos = current_map.start_positions[i]
        # Create the tank, images.tanks contains the image representing the tank
        tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[i], space)
        # Add the tank to the list of tanks
        tanks_list.append(tank)

    # create AI depending on gamemode
    for i in range(gamemode, len(current_map.start_positions)):
        pos = current_map.start_positions[i]
        a_i = ai.Ai(tanks_list[i], game_objects_list, tanks_list, space, current_map)
        ai_list.append(a_i)


def create_flag():
    """Creates the flag and adds to game_objects_list"""
    global flag
    flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
    game_objects_list.append(flag)


def create_bases():
    """Create the bases using tanks start positions"""
    for i in range(0, len(current_map.start_positions)):
        # Get the starting position of the tank "i"
        pos = current_map.start_positions[i]
        # Create the tank, images.tanks contains the image representing the tank
        base = gameobjects.Base(pos[0], pos[1], images.bases[i])
        # Add the tank to the list of tanks
        bases_list.append(base)


def explode(x, y):
    """Create an explosion at target location"""
    explosion = gameobjects.Explosion(x, y, images.explosion)
    explosion_list.append(explosion)
    explosion_timer.append(pygame.time.get_ticks() + 1500)


def reset():
    """Used to reset the game"""
    # Return tanks to start position
    for tank in tanks_list:
        for ai in ai_list:
            if ai.tank == tank:
                ai.reset_cycle()
        tank.respawn(space, current_map, flag)
    # Destroy all non grass tiles - hitboxes and visuals
    for object in game_objects_list:
        if not object == flag:
            space.remove(object.shape, object.body)
    game_objects_list.clear()
    # Recreate the map
    create_boxes()
    flag.respawn_flag(current_map)


def change_map():
    """used to change map, clears all objects and recreates them for the new map"""
    game_objects_list.clear()
    tanks_list.clear()
    bases_list.clear()
    ai_list.clear()
    for shape in space.shapes:
        space.remove(shape)
    create_border()
    create_grass()
    create_boxes()
    create_flag()
    create_tanks()
    create_bases()


# Create all objects and map
create_border()
create_grass()
create_boxes()
create_flag()
create_tanks()
create_bases()


# Create font for text
font = pygame.font.SysFont(None, 30)


def scoreboard():
    """Creates and displays scoreboard text upon round end """
    spacing = 10
    for tank_index, tank in enumerate(tanks_list):
        player_text = 'Player ' + str(tank_index + 1) + ': ' + str(tank.point) + ' points'
        score_text = font.render(player_text, True, (255, 255, 255))
        screen.blit(score_text, (100, spacing))
        spacing += 40


def check_keyboard_input():
    """Used to check keyboard inputs and handle those events"""
    # Check if we receive a QUIT event (for instance, if the user press the
    # close button of the window) or if the user press the escape key.
    global running
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                tanks_list[0].accelerate()
            elif event.key == K_DOWN:
                tanks_list[0].decelerate()
            elif event.key == K_RIGHT:
                tanks_list[0].turn_right()
            elif event.key == K_LEFT:
                tanks_list[0].turn_left()
            elif event.key == K_RETURN:
                if not tanks_list[0].recent_shot:
                    bullet = tanks_list[0].shoot(space)
                    game_objects_list.append(bullet)
                    sounds.shoot_sfx.play()
        elif event.type == KEYUP:
            if event.key == K_UP or event.key == K_DOWN:
                tanks_list[0].stop_moving()
            elif event.key == K_RIGHT or event.key == K_LEFT:
                tanks_list[0].stop_turning()

        # We only need to handle the second players inputs if gamemode is multiplayer
        if gamemode == 2:
            if event.type == KEYDOWN:
                if event.key == K_w:
                    tanks_list[1].accelerate()
                elif event.key == K_s:
                    tanks_list[1].decelerate()
                elif event.key == K_d:
                    tanks_list[1].turn_right()
                elif event.key == K_a:
                    tanks_list[1].turn_left()
                elif event.key == K_SPACE:
                    if not tanks_list[1].recent_shot:
                        bullet = tanks_list[1].shoot(space)
                        game_objects_list.append(bullet)
                        sounds.shoot_sfx.play()
            elif event.type == KEYUP:
                if event.key == K_w or event.key == K_s:
                    tanks_list[1].stop_moving()
                elif event.key == K_d or event.key == K_a:
                    tanks_list[1].stop_turning()


# set gamestate to main_menu
gamestate = "main"

# ----- Main Loop -----#

# -- Controls whether the game runs
running = True

# -- Gamestate checks
game_active = True
round_end = False
game_end = False

skip_update = 0

# Loop menu music during game
sounds.menu_loop.play(loops=-1)

while running:
    # Check gamestates
    if gamestate == "main":
        # If something is clicked change gamestate/map
        for event in pygame.event.get():
            gamestate = main.update(event)
            change_map()
        # Change gamemode, map depending on actions
        main.update_screen(screen)
        gamemode = main.gamemode
        main.current_map = current_map
        pygame.display.flip()

    elif gamestate == "maps":
        # If something is clicked change map/gamestate
        for event in pygame.event.get():
            gamestate = mapmen.update(event)
            change_map()
        # Change map, gamestate depending on actions
        current_map = mapmen.current_map
        background = mapmen.background
        mapmen.update_screen(screen)
        pygame.display.flip()
    else:
        # -- Handle the events
        check_keyboard_input()

        # -- Update physics
        if skip_update == 0:
            # Loop over all the game objects and update their speed in function of their
            # acceleration.
            for obj in game_objects_list:
                obj.update()
            for tanks in tanks_list:
                tanks.update()
            skip_update = 2
        else:
            skip_update -= 1

        #   Check if tank is near flag and tries to grab flag
        if game_active:
            for tank_order, tank in enumerate(tanks_list):
                tank.try_grab_flag(flag)
                if tank.has_won():
                    tank.add_point()
                    # Check if a tank has enough points to win
                    if tank.point > 2:
                        winning_tank = tank_order + 1
                        game_end = True
                    timer_end = pygame.time.get_ticks() + 1500
                    round_end = True
                    game_active = False

        #   Check collisions and update the objects position
        space.step(1 / FRAMERATE)

        #   Update object that depends on another object position (for instance a flag)
        for obj in game_objects_list:
            obj.post_update()

        #   Update ai objects   depending on gamemode
        for index in range(gamemode - 2, len(ai_list)):
            ai_list[index].decide()

        #   Update objects that depends on tank (tank holding flag for instance)
        if game_active:
            for tanks in tanks_list:
                if tanks.invincibility_timer >= 2:
                    tanks.invincible = False
                tanks.post_update()

        # -- Update Display

        # Display the background on the screen
        screen.blit(background, (0, 0))

        # Update the display of the base objects on the screen
        for bases in bases_list:
            bases.update_screen(screen)

        # Update the display of the explosions on the screen
        for exp_index, explosion in enumerate(explosion_list):
            explosion.update_screen(screen)
            # After a time, remove the explosion
            if explosion_timer[exp_index] < pygame.time.get_ticks():
                explosion_list.remove(explosion)
                explosion_timer.remove(explosion_timer[exp_index])

        # Update the display of the tank objects on the screen
        if game_active:
            for tanks in tanks_list:
                tanks.update_screen(screen)

        # Update the display of the game objects on the screen
        for obj in game_objects_list:
            obj.update_screen(screen)

        # Update the display of the flag object on the screen
        if game_active:
            flag.update_screen(screen)

        # Adds screen darkening and scoreboard to update loop after point has been scored
        if round_end:
            flag.respawn_flag(current_map)
            screen_fade = pygame.Surface(current_map.rect().size)
            screen_fade.fill((0, 0, 0))
            screen_fade.set_alpha(120)
            screen.blit(screen_fade, (0, 0))
            current_time = pygame.time.get_ticks()
            if game_end:
                # Ending game if win condition is fulfilled
                winner_text = 'Player ' + str(winning_tank) + ' wins'
                end_text = font.render(winner_text, True, (255, 255, 255))
                screen.blit(end_text, (110, 150))
                # Reset game scoring and checks
                for tank in tanks_list:
                    tank.point = 0
                if timer_end < current_time:
                    game_end = False
                    round_end = False
                    game_active = True
                    main.click = False
                    screen = pygame.display.set_mode(maps.map0.rect().size)
                    # Reset game and change gamestate into main menu
                    gamestate = "main"
                    reset()

            else:
                # Resets round after scoreboard is shown
                scoreboard()
                if timer_end < current_time:
                    round_end = False
                    game_active = True
                    reset()

        #   Redisplay the entire screen (see double buffer technique)
        pygame.display.flip()

        #   Control the game framerate
        clock.tick(FRAMERATE)
