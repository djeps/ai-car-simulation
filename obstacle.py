import pygame

from constants import *

class Circle(pygame.sprite.Sprite):
    
    def __init__(self, color, x, y, radius, pen=3):
        super().__init__()

        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        
        pygame.draw.circle(self.image, color, (radius, radius), radius, pen)
        self.rect = self.image.get_rect(center=(x, y))


class Obstacle:

    def __init__(self, size, time, enabled, position):
        self.size = size
        self.time = time
        self.enabled = enabled
        self.position = position
        self.elapsed = 0
        self.draw = False

        self.sprite = pygame.image.load(f"images/obstacles/obstacle01.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (OBSTACLE_SIZES[self.size], OBSTACLE_SIZES[self.size]))
        self.sprite_rect = self.sprite.get_rect()


    def get_rect(self):
        return self.sprite_rect


    def set_position(self, position):
        self.position = position
        self.sprite_rect.center = position


    def rescale_sprite(self):
        self.sprite = pygame.image.load(f"images/obstacles/obstacle01.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (OBSTACLE_SIZES[self.size], OBSTACLE_SIZES[self.size]))
        self.sprite_rect = self.sprite.get_rect()
        self.sprite_rect.center = self.position
    

    def get_center(self):
        return self.sprite_rect.center


    def get_x(self):
        return self.sprite_rect.left
    

    def get_y(self):
        return self.sprite_rect.top
    

    def get_width(self):
        return self.sprite_rect.width
    

    def get_height(self):
        return self.sprite_rect.height
    