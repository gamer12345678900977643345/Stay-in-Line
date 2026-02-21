import pygame
import pygame

breedte = 1280
hoogte = 800
lane = 1/3  # geen afronding
lane_one_pos = 0
lane_two_pos = breedte * lane
lane_tree_pos = breedte * 2 * lane  # laatste lane start hier, pak rest bij tekenen
lane_pic = pygame.image.load("lane.png")
tile_pic = pygame.image.load("tile.png")
motor_pic = pygame.image.load("motor.png")
auto_b = pygame.image.load("auto_baluw.png")
auto_g = pygame.image.load("auto_groen.png")
auto_p = pygame.image.load("auto_paars.png")
auto_r = pygame.image.load("auto_rood.png")
truck_b = pygame.image.load("truck_blauw.png")
truck_g = pygame.image.load("truck_groen.png")
truck_p = pygame.image.load("truck_paars.png")
truck_r = pygame.image.load("truck_rood.png")
print(breedte, hoogte, lane, lane_one_pos, lane_two_pos, lane_tree_pos)