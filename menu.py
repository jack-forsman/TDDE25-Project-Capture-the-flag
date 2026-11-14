import pygame
import os
from pygame.locals import *
from pygame.color import *
import pymunk
import sounds
import sys
import images
import maps
import gameobjects


class Menu():
    """ Class used to create the basics of a menu-screen and will be extended to create different types of menus"""
    def __init__(self, screen):
        """function used to initialize different variables such as gamestate and font"""
        self.screen = screen
        self.buttons = []
        self.color = (255, 255, 255)

        self.text_font = pygame.font.SysFont(None, 30)

    def update(self, event):
        """function used to update menu for events in game"""
        # If we quit in any menu it should quit the game
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    def update_screen(self, screen):
        """function used to draw everything in menu-screen"""
        # All menus should fill screen with color and all buttons change color if they are hovered
        self.screen.fill((155, 155, 155))

        for button in self.buttons:
            if button.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (255, 0, 0), button)
            else:
                pygame.draw.rect(screen, (255, 255, 255), button)


class Main_Menu(Menu):
    """Extends menu class and handles everything for the main menu such as changing modes and changing screen"""
    def __init__(self, screen, current_map):
        super().__init__(screen)

        # Create all buttons used in main menu
        self.start_button = pygame.Rect(screen.get_width() / 2 - 100, screen.get_height() / 2, 200, 50)
        self.map_button = pygame.Rect(screen.get_width() / 2 - 100, screen.get_height() / 2 + 120, 200, 50)
        self.game_mode1_button = pygame.Rect(screen.get_width() / 2 - 100, screen.get_height() / 2 + 60, 90, 50)
        self.game_mode2_button = pygame.Rect(screen.get_width() / 2 + 10, screen.get_height() / 2 + 60, 90, 50)
        self.buttons.append(self.start_button)
        self.buttons.append(self.map_button)
        self.buttons.append(self.game_mode1_button)
        self.buttons.append(self.game_mode2_button)

        # Create title image
        self.title = images.title

        # Create text for buttons
        self.play_text_surface = self.text_font.render("PLAY", False, (0, 0, 0))
        self.single_text_surface = self.text_font.render("SINGLE", False, (0, 0, 0))
        self.multi_text_surface = self.text_font.render("MULTI", False, (0, 0, 0))
        self.map_text_surface = self.text_font.render("CHOOSE MAP", False, (0, 0, 0))

        # Set variables to values
        self.current_map = current_map
        self.gamemode = 1

    def update(self, event):
        super().update(event)

        # Change game state and gamemode depending on button clicked
        if self.start_button.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.screen = pygame.display.set_mode(self.current_map.rect().size)
                return "play"
        elif self.map_button.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "maps"
        elif self.game_mode1_button.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.gamemode = 1
        elif self.game_mode2_button.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.gamemode = 2
        # if we do not change gamestate, return current state
        return "main"

    def update_screen(self, screen):
        super().update_screen(screen)

        # draw title
        screen.blit(self.title, (screen.get_width() / 2 - 150, 50))

        # draw gamemode buttons in specific color if they are clicked in
        if self.gamemode == 1:
            pygame.draw.rect(screen, (120, 120, 120), self.game_mode1_button)
        elif self.gamemode == 2:
            pygame.draw.rect(screen, (120, 120, 120), self.game_mode2_button)

        # draw buttontext
        screen.blit(self.play_text_surface, (screen.get_width() / 2 - 23, 195))
        screen.blit(self.single_text_surface, (screen.get_width() / 2 - 92, 255))
        screen.blit(self.multi_text_surface, (screen.get_width() / 2 + 25, 255))
        screen.blit(self.map_text_surface, (screen.get_width() / 2 - 70, 315))


class Map_Menu(Menu):
    """Extends Menu class and handles showing map examples and choosing/changing maps"""
    def __init__(self, screen, current_map, background):
        super().__init__(screen)

        # Create buttons used in map menu
        self.map1_button = pygame.Rect(20, screen.get_height() - 300, 100, 50)
        self.map2_button = pygame.Rect(20, screen.get_height() - 200, 100, 50)
        self.map3_button = pygame.Rect(20, screen.get_height() - 100, 100, 50)
        self.back_button = pygame.Rect(0, 0, 60, 50)
        self.buttons.append(self.map1_button)
        self.buttons.append(self.map2_button)
        self.buttons.append(self.map3_button)
        self.buttons.append(self.back_button)

        # Create text for buttons
        self.back_text_surface = self.text_font.render("BACK", False, (0, 0, 0))
        self.map1_text_surface = self.text_font.render("MAP 1", False, (0, 0, 0))
        self.map2_text_surface = self.text_font.render("MAP 2", False, (0, 0, 0))
        self.map3_text_surface = self.text_font.render("MAP 3", False, (0, 0, 0))

        # Set variables values
        self.current_map = current_map
        self.background = background

        # create space used to get boxes for showcase map
        self.space = pymunk.Space()

    def update(self, event):
        super().update(event)

        # change map depending on which mapbutton is clicked
        if self.map1_button.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.current_map = maps.map0
                self.background = pygame.Surface(maps.map0.rect().size)
        elif self.map2_button.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.current_map = maps.map1
                self.background = pygame.Surface(maps.map1.rect().size)
        elif self.map3_button.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.current_map = maps.map2
                self.background = pygame.Surface(maps.map2.rect().size)
        elif self.back_button.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "main"

        return "maps"

    def update_screen(self, screen):
        super().update_screen(screen)

        # Create surface that will display a showcase version of chosen map
        showcase_map = pygame.Surface(self.current_map.rect().size)

        # Iterate through all tiles on map
        for x in range(0, self.current_map.width):
            for y in range(0, self.current_map.height):
                # blit grass onto showcase_map
                showcase_map.blit(images.grass, (x * images.TILE_SIZE, y * images.TILE_SIZE))

                # Get the type of boxes and blit onto showcase map
                box_type = self.current_map.boxAt(x, y)
                if box_type != 0:
                    showcase_map.blit(gameobjects.get_box_with_type(x, y, box_type, self.space).sprite, (x * images.TILE_SIZE, y * images.TILE_SIZE))

        for i in range(0, len(self.current_map.start_positions)):
            # Get the starting position of the tank "i"
            pos = self.current_map.start_positions[i]
            # Blit bases onto showcase_map
            showcase_map.blit(images.bases[i], (pos[0] * images.TILE_SIZE, pos[1] * images.TILE_SIZE))

        # Transform showcase_map into its right size depending on map
        if self.current_map == maps.map0:
            showcase_map = pygame.transform.scale(showcase_map, (showcase_map.get_width() / 2.5, showcase_map.get_height() / 2.5))
        if self.current_map == maps.map1:
            showcase_map = pygame.transform.scale(showcase_map, (showcase_map.get_width() / 4, showcase_map.get_height() / 4))
        if self.current_map == maps.map2:
            showcase_map = pygame.transform.scale(showcase_map, (showcase_map.get_width() / 2.5, showcase_map.get_height() / 2.5))

        # Copy showcase map onto map_menu screen
        self.screen.blit(showcase_map, (180, 120))

        # Change button color if map is active
        if self.current_map == maps.map0:
            pygame.draw.rect(screen, (120, 120, 120), self.map1_button)
        elif self.current_map == maps.map1:
            pygame.draw.rect(screen, (120, 120, 120), self.map2_button)
        elif self.current_map == maps.map2:
            pygame.draw.rect(screen, (120, 120, 120), self.map3_button)

        # change text depending on map
        if self.current_map == maps.map0:
            map_text_surface = self.text_font.render("Current Map: Map 1", False, (0, 0, 0))
        if self.current_map == maps.map1:
            map_text_surface = self.text_font.render("Current Map: Map 2", False, (0, 0, 0))
        if self.current_map == maps.map2:
            map_text_surface = self.text_font.render("Current Map: Map 3", False, (0, 0, 0))

        # draw current map text
        self.screen.blit(map_text_surface, (150, 100))

        # draw text for buttons
        screen.blit(self.back_text_surface, (0, 16))
        screen.blit(self.map1_text_surface, (40, 75))
        screen.blit(self.map2_text_surface, (40, 175))
        screen.blit(self.map3_text_surface, (40, 275))
