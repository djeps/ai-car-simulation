import argparse
import configparser
import os
import sys

from constants import *

class Args:

    def __init__(self):
        self.args = None
        self.parser = argparse.ArgumentParser()

        # Read out the NEAT config file so we can update it if needed
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE)

        self.parser.add_argument("-V", "--verbose", help="Verbose mode", action='store_true')
        self.parser.add_argument("-g", "--generations", type=int, help="Number of generations", default=MAX_GENERATIONS)
        self.parser.add_argument("-i", "--inputs", type=int, help="Number of inputs", default=0)
        self.parser.add_argument("-r", "--display_radars", help="Display radars", action='store_true')
        self.parser.add_argument("-l", "--sensing_length", type=int, help="Radar sensing length", default=DEFAULT_RADAR_SENSING_LENGTH)
        self.parser.add_argument("-S", "--car_size", type=int, help="Car size", default=5)
        self.parser.add_argument("-s", "--car_sprite", type=str, help="Car sprite to load", default=DEFAULT_SPRITE)
        self.parser.add_argument("-m", "--track_map", type=str, help="Track map to load", default=DEFAULT_MAP)
        self.parser.add_argument("-G", "--generation_interval", type=int, help="Elapsed generations when creaking a training checkpoint", default=10)
        self.parser.add_argument("-T", "--time_interval_seconds", type=int, help="Elapsed seconds when creaking a training checkpoint", default=300)

        self.args = self.parser.parse_args()

        self.generations = self.args.generations
        self.inputs = self.args.inputs
        self.display_radars = self.args.display_radars
        self.verbose = self.args.verbose
        self.sensing_length = self.args.sensing_length
        self.car_size = self.args.car_size
        self.car_sprite = self.args.car_sprite
        self.track_map = self.args.track_map
        self.generation_interval = self.args.generation_interval
        self.time_interval_seconds = self.args.time_interval_seconds
    
        self.__check_arguments__()


    def __check_arguments__(self):
        self.__check_generations__()
        self.__check_inputs__()
        self.__check_sensing_length__()
        self.__check_car_size__()
        self.__check_car_sprite__()
        self.__check_image_map__()


    def __check_generations__(self):
        if self.generations > MAX_GENERATIONS:
            self.generations = MAX_GENERATIONS


    def __update_config__(self, section, setting, value):
        # The number of inputs was specified from the command line
        if self.args.inputs:
            # It's different from the current value in the config file
            if self.inputs !=  int(self.config[section][setting]):
                if self.inputs > MAX_INPUTS:
                    self.inputs = MAX_INPUTS

                self.config[section][setting] = str(value)
                with open(CONFIG_FILE, "w") as config_file:
                    self.config.write(config_file)
        else:
            self.inputs =  int(self.config[section][setting]) # Otherwise, keep the config value


    def __check_inputs__(self):
        section = "DefaultGenome"
        setting = "num_inputs"

        self.__update_config__(section, setting, self.inputs)


    def update_config(self, section, setting, value):
        self.__update_config__(section, setting, value)


    def __check_sensing_length__(self):
        if self.sensing_length > MAX_RADAR_SENSING_LENGTH:
            if self.verbose:
                print(f"=> Overriding radar sensing length: {self.sensing_length} (given) to {MAX_RADAR_SENSING_LENGTH} (max)")
            self.sensing_length = MAX_RADAR_SENSING_LENGTH

        if self.sensing_length <= 0:
            if self.verbose:
                print(f"=> Overriding radar sensing length: {self.sensing_length} (given) to {DEFAULT_RADAR_SENSING_LENGTH} (default)")
            self.sensing_length = DEFAULT_RADAR_SENSING_LENGTH


    def __check_car_size__(self):
        if self.car_size > len(CAR_SIZES) - 1:
            if self.verbose:
                print(f"=> Overriding car size: {self.car_size} (given) to {len(CAR_SIZES) - 1} (max).")
            self.car_size = len(CAR_SIZES) - 1
        
        if self.car_size <= 0:
            if self.verbose:
                print(f"=> Overriding car size: {self.car_size} (given) to {0} (min).")
            self.car_size = 0
        
        if self.verbose:
            print(f"=> Car size (px) = {CAR_SIZES[self.car_size]}x{CAR_SIZES[self.car_size]}")


    def __check_car_sprite__(self):
        if not os.path.exists(f"images/sprites/{self.car_sprite}"):
            print(f"=> Error! Can't load car sprite file: images/sprites/{self.car_sprite}")
            sys.exit(ERROR_SPRITE_LOAD)


    def __check_image_map__(self):
        if not os.path.exists(f"images/tracks/{self.track_map}"):
            print(f"=> Error! Can't load track map file: images/tracks/{self.track_map}")
            sys.exit(ERROR_TRACK_LOAD)
