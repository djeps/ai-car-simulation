import pygame

class NeuralNetwork:
    def __init__(self, screen):
        self.keep_running = False
        self.pygame_is_initialized = pygame.get_init()

        if self.pygame_is_initialized:
            if not isinstance(screen, pygame.Surface):
                raise TypeError("'screen' is not of type 'pygame.Surface'!")
        
            self.screen = screen
            self.nn_winner_img = pygame.image.load("nn_winner.png").convert_alpha()
            self.keep_running = True
    
    def display_nn(self):
        self.keep_running = True

        while self.keep_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.keep_running = False
            
            self.screen.fill((255, 255, 255))  # Fill screen with white
            screen_width, screen_height = self.screen.get_size()
            nn_winner_rect = self.nn_winner_img.get_rect()
            nn_winner_rect.center = (screen_width // 2, screen_height // 2)
            self.screen.blit(self.nn_winner_img, nn_winner_rect)
            pygame.display.update()