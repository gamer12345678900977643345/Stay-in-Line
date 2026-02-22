import pygame

breedte = 1280
hoogte  = 800
lane    = 1 / 3

lane_one_pos  = 0
lane_two_pos  = breedte * lane
lane_tree_pos = breedte * 2 * lane

road_pic  = pygame.image.load("road.png")   # volledig wegdek (3 lanes, portrait)
motor_pic = pygame.image.load("motor.png")
auto_b    = pygame.image.load("auto_baluw.png")
auto_g    = pygame.image.load("auto_groen.png")
auto_p    = pygame.image.load("auto_paars.png")
auto_r    = pygame.image.load("auto_rood.png")
truck_b   = pygame.image.load("truck_blauw.png")
truck_g   = pygame.image.load("truck_groen.png")
truck_p   = pygame.image.load("truck_paars.png")
truck_r   = pygame.image.load("truck_rood.png")