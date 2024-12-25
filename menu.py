import os
import sys
import glob
import pygame
import pygame_menu
import pygame_menu.locals

from constants import *
from args import *
from game import *
from neural_network import *

class Menu():

    def __init__(self, args, caption="Main Menu"):
        self.args = args
        
        if not isinstance(args, Args):
            raise TypeError("'args' is not of type 'Args'!")

        # Initialize PyGame and create a surface
        self.game_env = GameEnvironment(WIDTH, HEIGHT)
        self.neat_algo = NeatAlgo(self.args, self.game_env)
        self.winner_nn = NeuralNetwork(self.args, self.game_env)

        self.theme = self.__create_main_theme__()
        self.__create_select_track_menu__(self.theme)
        self.__create_arguments_menu__(self.theme)
        self.__create_main_menu__(caption, self.theme)

        self.current_menu = self.menu_main
        self.return_from_select_track_menu = False
        self.return_from_arguments_menu = False
        self.winner = None
    

    def __create_main_theme__(self):
        theme = pygame_menu.themes.THEME_DEFAULT
        theme.title_font_size = 24
        theme.widget_font_size = 18

        return theme


    def __create_select_track_menu__(self, theme):
        self.select_track_menu = pygame_menu.Menu("Select track", 400, 150, theme=self.theme)

        self.select_track_menu.add.text_input("Track map: ", default=self.args.track_map, textinput_id="track_map", cursor_selection_enable=False)
        self.select_track_menu.add.button("Done", self.__return_to_menu_main_from_select_track_menu__)


    def __create_arguments_menu__(self, theme):
        self.arguments_menu = pygame_menu.Menu("Arguments", 400, 455, theme=self.theme)

        self.arguments_menu.add.selector("Verbose mode: ", [("True", True), ("False", False)], default=0 if self.args.verbose else 1, selector_id="verbose")
        self.arguments_menu.add.text_input("No. of Generations: ", default=self.args.generations, maxchar=4, maxwidth=5, textinput_id="generations",input_type=pygame_menu.locals.INPUT_INT, cursor_selection_enable=False)
        self.arguments_menu.add.text_input("No. of sensor inputs: ", default=self.args.inputs, maxchar=2, maxwidth=3, textinput_id="inputs",input_type=pygame_menu.locals.INPUT_INT, cursor_selection_enable=False)
        self.arguments_menu.add.selector("Display radars: ", [("True", True), ("False", False)], default=0 if self.args.display_radars else 1, selector_id="display_radars")
        self.arguments_menu.add.text_input("Sensing length: ", default=self.args.sensing_length, maxchar=3, maxwidth=4, textinput_id="sensing_length",input_type=pygame_menu.locals.INPUT_INT, cursor_selection_enable=False)
        self.arguments_menu.add.selector("Car size: ", [("Tiniest", 0), ("Tiny", 1), ("Smallest", 2), ("Smaller", 3), ("Small", 4), ("Normal", 5), ("Bigger", 6), ("Larger", 7), ("Largest", 8)], default=self.args.car_size, selector_id="car_size")
        self.arguments_menu.add.text_input("Car sprite: ", default=self.args.car_sprite, textinput_id="car_sprite", cursor_selection_enable=False)
        self.arguments_menu.add.text_input("Track map: ", default=self.args.track_map, textinput_id="track_map", cursor_selection_enable=False)
        self.arguments_menu.add.text_input("Checkpoint on generations: ", default=self.args.generation_interval, maxchar=3, maxwidth=4, textinput_id="generation_interval",input_type=pygame_menu.locals.INPUT_INT, cursor_selection_enable=False)
        self.arguments_menu.add.text_input("Checkpooint on seconds: ", default=self.args.time_interval_seconds, maxchar=4, maxwidth=5, textinput_id="time_interval_seconds",input_type=pygame_menu.locals.INPUT_INT, cursor_selection_enable=False)
        self.arguments_menu.add.button("Done", self.__return_to_menu_main_from_arguments_menu__)
    

    def __create_main_menu__(self, caption, theme):
        self.caption = caption
        self.menu_main = pygame_menu.Menu(self.caption, 400, 355, theme=self.theme)

        self.menu_main.add.button("New training", self.__menu_item_start_new_training__)
        self.menu_main.add.button("Continue training", self.__menu_item_continue_from_training__)
        self.menu_main.add.button("Test run", self.__menu_item_test_run__)
        self.menu_main.add.button("Display NN", self.__menu_item_display_neural_network__)
        self.menu_main.add.button("Set obstacles", self.__menu_item_set_obstacles__)
        self.menu_main.add.button("Change track", self.__menu_item_set_track__)
        self.menu_main.add.button("Change arguments", self.__menu_item_set_input_arguments__)
        self.menu_main.add.button("Quit", self.__menu_item_quit__)


    def display(self):
        # Main loop to run the menu_main
        while self.game_env.keep_running:
            self.game_env.get_screen().fill(BACKGROUND)

            self.events = pygame.event.get()

            if self.current_menu.is_enabled():
                self.current_menu.update(self.events)
                self.current_menu.draw(self.game_env.get_screen())

                if self.return_from_arguments_menu:
                    self.__on_arguments_menu_close__()
                
                if self.return_from_select_track_menu:
                    self.__on_select_track_menu_close__()

            pygame.display.flip()
            self.game_env.get_clock().tick(60)
    

    def __update_arguments__(self):
        self.args.verbose = self.arguments_menu.get_widget("verbose").get_value()[0][1]
        self.args.generations = self.arguments_menu.get_widget("generations").get_value()
        self.args.inputs = self.arguments_menu.get_widget("inputs").get_value()
        self.args.display_radars = self.arguments_menu.get_widget("display_radars").get_value()[0][1]
        self.args.sensing_length = self.arguments_menu.get_widget("sensing_length").get_value()
        self.args.car_size = self.arguments_menu.get_widget("car_size").get_value()[0][1]
        self.args.car_sprite = self.arguments_menu.get_widget("car_sprite").get_value()
        self.args.track_map = self.arguments_menu.get_widget("track_map").get_value()
        self.args.generation_interval = self.arguments_menu.get_widget("generation_interval").get_value()
        self.args.time_interval_seconds = self.arguments_menu.get_widget("time_interval_seconds").get_value()

        # Update the 'track_map' value when the 'select_track_menu' is displayed
        self.select_track_menu.get_widget("track_map").set_value(self.args.track_map)


    def __update_config__(self):
        self.args.update_config("DefaultGenome", "num_inputs", self.arguments_menu.get_widget("inputs").get_value())


    def __on_select_track_menu_close__(self):
        self.return_from_select_track_menu = False
        self.args.track_map = self.select_track_menu.get_widget("track_map").get_value()

        # Update the 'track_map' value when the 'arguments_menu' is displayed
        self.arguments_menu.get_widget("track_map").set_value(self.args.track_map)


    def __on_arguments_menu_close__(self):
        self.return_from_arguments_menu = False
        self.__update_arguments__()
        self.__update_config__()


    def __return_to_menu_main_from_select_track_menu__(self):
        self.return_from_select_track_menu = True
        self.current_menu = self.menu_main


    def __return_to_menu_main_from_arguments_menu__(self):
        self.return_from_arguments_menu = True
        self.current_menu = self.menu_main


    def __save_generations_number__(self):
        # Create the file if it doesn't exist or overwrite if it does
        with open("neat-generations", "wt") as f:  # Create a new file or overwrite an existing one
            f.write(str(self.args.generations))


    def __read_generations_number__(self):    
        neat_generations = 0
        if os.path.exists("neat-generations"):
            with open("neat-generations", "r") as f:
                neat_generations = int(f.readline())

        return neat_generations


    def __cleanup_checkpoints__(self, all=True):
        file_name_pattern = "neat-checkpoint-"
        all_files = glob.glob(os.path.join("", "*"))
        checkpoint_files = []

        for file in all_files:
            if file_name_pattern in os.path.basename(file):
                checkpoint_files.append(file)
        
        sorted_checkpoint_files = None
        if len(checkpoint_files):
            sorted_checkpoint_files = sorted(checkpoint_files, key=str.lower)

        if sorted_checkpoint_files is not None:
            upper_limit = len(sorted_checkpoint_files)-1
            
            if all:
                upper_limit += 1

            for i in range(0, upper_limit):
                os.remove(sorted_checkpoint_files[i])


    def __menu_item_set_input_arguments__(self):
        if self.args.verbose:
            print("=> Changing the input arguments for the simulation")
        
        self.current_menu = self.arguments_menu


    def __menu_item_set_track__(self):
        if self.args.verbose:
            print("=> Changing the car track used for the simulation")
        self.current_menu = self.select_track_menu


    def __load_nn_winner__(self, winner):
        if winner is None:
            if self.args.verbose:
                print("=> The training did NOT complete")
            
            if os.path.exists("nn_winner.pkl"):
                with open("nn_winner.pkl", "rb") as f:
                    winner = pickle.load(f)
                    self.neat_algo.generate_nn_image(winner, recent=False)

                    if self.args.verbose:
                        print("=> Loading an older winner neural network (nn_winner.pkl)...")
            else:
                if self.args.verbose:
                    print("=> Nothing to load (nn_winner.pkl)!")
        else:
            self.neat_algo.generate_nn_image(winner)


    def __menu_item_start_new_training__(self):
        if self.args.verbose:
            print("=> Starting a new training session")
        
        self.__save_generations_number__()
        self.__cleanup_checkpoints__()

        self.winner = self.neat_algo.train_nn(self.args.car_sprite, self.args.track_map)
        self.__load_nn_winner__(self.winner)


    def __menu_item_continue_from_training__(self):
        if self.args.verbose:
            print("=> Continuing from a previous training session")

        self.__cleanup_checkpoints__(all=False)

        self.winner = self.neat_algo.train_nn(self.args.car_sprite, self.args.track_map, new_training=False, neat_generations=self.__read_generations_number__())
        self.__load_nn_winner__(self.winner)


    def __menu_item_test_run__(self):
        if self.args.verbose:
            print("=> Starting a test run session")
        
        self.neat_algo.test_nn(self.args.car_sprite, self.args.track_map)
        


    def __menu_item_display_neural_network__(self):
        if self.args.verbose:
            print("=> Displaying last saved neural network")
        
        self.winner_nn.display_nn()


    def __menu_item_set_obstacles__(self):
        if self.args.verbose:
            print("=> Setting track obstacles")

        self.neat_algo.set_track_obstacles(self.args.track_map)


    def __menu_item_quit__(self):
        self.game_env.quit()
        sys.exit(EXIT_SUCCESS)
