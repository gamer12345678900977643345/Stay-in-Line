import pygame
from utils import resource_path

breedte = 1280
hoogte  = 800
lane    = 1 / 3

lane_one_pos  = 0
lane_two_pos  = breedte * lane
lane_tree_pos = breedte * 2 * lane

road_pic  = pygame.image.load(resource_path("road.png"))
motor_pic = pygame.image.load(resource_path("motor.png"))
auto_b    = pygame.image.load(resource_path("auto_baluw.png"))
auto_g    = pygame.image.load(resource_path("auto_groen.png"))
auto_p    = pygame.image.load(resource_path("auto_paars.png"))
auto_r    = pygame.image.load(resource_path("auto_rood.png"))
truck_b   = pygame.image.load(resource_path("truck_blauw.png"))
truck_g   = pygame.image.load(resource_path("truck_groen.png"))
truck_p   = pygame.image.load(resource_path("truck_paars.png"))
truck_r   = pygame.image.load(resource_path("truck_rood.png"))