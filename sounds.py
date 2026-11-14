import pygame

pygame.mixer.init()

# Adding background music
menu_loop = pygame.mixer.Sound("sounds/menu_loop.wav")

# Adding the shoot sound effect
shoot_sfx = pygame.mixer.Sound("sounds/shoot.wav")

# Wood box destroyed sfx
wood_box_destroyed_sfx = pygame.mixer.Sound("sounds/wood_break.wav")

# Rock or metal box hit but not destroyed
rock_metal_impact_sfx = pygame.mixer.Sound("sounds/rock_metal_impact.wav")

# Tank shot and destroyed
tank_shot = pygame.mixer.Sound("sounds/tank_shot.wav")

# Flag captured
capture_flag_sfx = pygame.mixer.Sound("sounds/grab_flag.wav")
