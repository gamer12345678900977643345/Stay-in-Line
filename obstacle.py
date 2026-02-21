import pygame


class Obstacle:
    def __init__(self, lane_index, lane_positions, image, speed, start_y, override_x=None):
        """
        lane_index  : 0, 1 of 2
        lane_positions: lijst met x-posities van lanes
        image       : pygame surface (al geschaald)
        speed       : snelheid naar beneden
        start_y     : beginpositie (meestal negatief, boven scherm)
        override_x  : optioneel — gebruik deze x in plaats van lane_positions[lane_index]
                      (handig voor gecentreerde obstakels binnen een lane)
        """
        self.lane_index = lane_index
        self.x = override_x if override_x is not None else lane_positions[lane_index]
        self.y = float(start_y)

        self.image = image
        self.speed = speed

        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update(self, scale_y=1):
        self.y += self.speed * scale_y
        self.rect.topleft = (self.x, int(self.y))

    def draw(self, screen):
        screen.blit(self.image, (self.x, int(self.y)))

    def is_off_screen(self, screen_height):
        return self.y > screen_height