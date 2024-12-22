import sys
import pygame
import pygame_menu
import pygame_menu.locals

from constants import *
from args import Args
from game import GameEnvironment
from simulation import Simulation

class Menu():
    def __init__(self, args, caption="Main menu_main"):
        self.args = args
        
        #self.simulation = Simulation(self.pygame)

        if not isinstance(args, Args):
            raise TypeError("'args' is not of type 'Args'!")


        # Initialize PyGame and create a surface
        self.game_env = GameEnvironment(WIDTH, HEIGHT)
        self.clock = self.game_env.get_clock()
        self.screen = self.game_env.get_screen()
        #self.keep_running = True
        #pygame.init()
        #self.surface = pygame.display.set_mode((1920, 1080))
        
        self.__create_main_theme__()
        self.__create_arguments_menu__(self.theme)
        self.__create_main_menu__(caption, self.theme)

        self.current_menu = self.menu_main
        self.return_from_arguments_menu = False
    
    def __create_main_theme__(self):
        self.theme = pygame_menu.themes.THEME_DARK
        self.theme.title_font_size = 24
        self.theme.widget_font_size = 18

    def __create_arguments_menu__(self, theme):
        self.arguments_menu = pygame_menu.Menu("Arguments", 400, 420, theme=self.theme)

        self.arguments_menu.add.selector("Verbose mode: ", [("True", True), ("False", False)], default=0 if self.args.verbose else 1, selector_id="verbose")
        self.arguments_menu.add.text_input("No. of Generations: ", default=self.args.generations, maxchar=4, maxwidth=5, textinput_id="generations",input_type=pygame_menu.locals.INPUT_INT, cursor_selection_enable=False)
        self.arguments_menu.add.text_input("No. of sensor inputs: ", default=self.args.inputs, maxchar=2, maxwidth=3, textinput_id="inputs",input_type=pygame_menu.locals.INPUT_INT, cursor_selection_enable=False)
        self.arguments_menu.add.selector("Display radars: ", [("True", True), ("False", False)], default=0 if self.args.display_radars else 1, selector_id="display_radars")
        self.arguments_menu.add.text_input("Sensing length: ", default=self.args.sensing_length, maxchar=3, maxwidth=4, textinput_id="sensing_length",input_type=pygame_menu.locals.INPUT_INT, cursor_selection_enable=False)
        self.arguments_menu.add.selector("Car size: ", [("Tiniest", 0), ("Tiny", 1), ("Smallest", 2), ("Smaller", 3), ("Small", 4), ("Normal", 5), ("Bigger", 6), ("Larger", 7), ("Largest", 8)], default=self.args.car_size, selector_id="car_size")
        self.arguments_menu.add.text_input("Car sprite: ", default=self.args.car_sprite, textinput_id="car_sprite", cursor_selection_enable=False)
        self.arguments_menu.add.text_input("Track map: ", default=self.args.track_map, textinput_id="track_map", cursor_selection_enable=False)
        self.arguments_menu.add.button("Done", self.__return_to_menu_main__)
    
    def __create_main_menu__(self, caption, theme):
        self.caption = caption
        self.menu_main = pygame_menu.Menu(self.caption, 400, 350, theme=self.theme)

        self.menu_main.add.button("New training", self.__menu_item_start_new_training__)
        self.menu_main.add.button("Continue training", self.__menu_item_continue_from_training__)
        self.menu_main.add.button("Display NN", self.__menu_item_display_neural_network__)
        self.menu_main.add.button("Set obstacles", self.__menu_item_set_obstacles__)
        self.menu_main.add.button("Change track", self.__menu_item_set_track__)
        self.menu_main.add.button("Change arguments", self.__menu_item_set_input_arguments__)
        self.menu_main.add.button("Quit", self.__menu_item_quit__)

    def display(self):
        #clock = pygame.time.Clock()
        clock = self.game_env.get_clock()
        screen = self.game_env.get_screen()
        
        # Main loop to run the menu_main
        while self.game_env.keep_running:
            #self.surface.fill((0, 0, 0))  # Black background
            screen.fill((0, 0, 0))

            self.events = pygame.event.get()

            if self.current_menu.is_enabled():
                self.current_menu.update(self.events)
                #self.current_menu.draw(self.surface)
                self.current_menu.draw(self.screen)

                if self.return_from_arguments_menu:
                    self.__on_arguments_menu_close__()

            pygame.display.flip()
            clock.tick(60)
    
    def __update_arguments__(self):
        self.args.verbose = self.arguments_menu.get_widget("verbose").get_value()[0][1]
        self.args.generations = self.arguments_menu.get_widget("generations").get_value()
        self.args.inputs = self.arguments_menu.get_widget("inputs").get_value()
        self.args.display_radars = self.arguments_menu.get_widget("display_radars").get_value()[0][1]
        self.args.sensing_length = self.arguments_menu.get_widget("sensing_length").get_value()
        self.args.car_size = self.arguments_menu.get_widget("car_size").get_value()[0][1]
        self.args.car_sprite = self.arguments_menu.get_widget("car_sprite").get_value()
        self.args.track_map = self.arguments_menu.get_widget("track_map").get_value()
        
    def __update_config__(self):
        self.args.update_config("DefaultGenome", "num_inputs", self.arguments_menu.get_widget("inputs").get_value())

    def __on_arguments_menu_close__(self):
        self.return_from_arguments_menu = False
        self.__update_arguments__()
        self.__update_config__()

    def __return_to_menu_main__(self):
        self.return_from_arguments_menu = True
        self.current_menu = self.menu_main

    def __menu_item_set_input_arguments__(self):
        if self.args.verbose:
            print("=> Changing the input arguments for the simulation")
        self.current_menu = self.arguments_menu

    def __menu_item_set_track__(self):
        if self.args.verbose:
            print("=> Changing the car track used for the simulation")

    def __menu_item_start_new_training__(self):
        if self.args.verbose:
            print("=> Starting a new training session")
    
    def __menu_item_continue_from_training__(self):
        if self.args.verbose:
            print("=> Continue from last training session")

    def __menu_item_display_neural_network__(self):
        if self.args.verbose:
            print("=> Displaying last saved neural network")
    
    def __menu_item_set_obstacles__(self):
        if self.args.verbose:
            print("=> Setting track obstacles")

    def __menu_item_quit__(self):
        #pygame.quit()
        self.game_env.quit()
        sys.exit(EXIT_SUCCESS)
