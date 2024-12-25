import os
import pygame

from constants import *

class GameEnvironment():

    def __init__(self, width, height):
        # Initialize PyGame and create a surface
        self.keep_running = True
        os.environ['SDL_VIDEO_CENTERED'] = '1' # Center the PyGame window
        pygame.display.set_caption("NEAT Car Simulator")
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()


    def get_screen(self):
        return self.screen


    def get_clock(self):
        return self.clock


    def quit(self):
        pygame.quit()
