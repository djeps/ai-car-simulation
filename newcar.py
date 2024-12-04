# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)

import math
import random
import sys
import os
import argparse
import configparser

import neat
import pygame

# ---
# Constants
# ---
# ---
CONFIG_FILE              = "./config.ini"
# ---
WIDTH                    = 1920
HEIGHT                   = 1080
# ---
CAR_SIZE_X               = 60
CAR_SIZE_Y               = 60
# ---
BORDER_COLOR             = (255, 255, 255, 255) # Color To Crash on Hit
MAX_RADAR_SENSING_LENGTH = 500
DEF_RADAR_SENSING_LENGTH = 300
# ---
MAX_GENERATIONS          = 1000
MAX_INPUTS               = 12
# ---
VIEW_ANGLE               = 180
L_VIEW_ANGLE             = -int(VIEW_ANGLE / 2)
R_VIEW_ANGLE             = int(VIEW_ANGLE / 2)
# ---

current_generation = 0 # Generation counter
args = None


def parse_arguments():
    # Returns parsed arguments
    args = None

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-g", "--generations", type=int, help="Number of generations", default=MAX_GENERATIONS)
    parser.add_argument("-i", "--inputs", type=int, help="Number of inputs", default=0)
    parser.add_argument("-r", "--display_radars", help="Display radars", action='store_true')
    parser.add_argument("-V", "--verbose", help="Verbose mode", action='store_true')
    parser.add_argument("-l", "--sensing_length", type=int, help="Maximum radar sensing length", default=DEF_RADAR_SENSING_LENGTH)
    
    args = parser.parse_args()

    # Read out the NEAT config file so we can update it if needed
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    if args.generations > MAX_GENERATIONS:
        args.generations = MAX_GENERATIONS
    
    # The number of inputs was specified from the command line
    if args.inputs:
        # It's different from the current value in the config file
        if args.inputs !=  int(config["DefaultGenome"]["num_inputs"]):
            if args.inputs > MAX_INPUTS:
                args.inputs = MAX_INPUTS
            
            # We therefore need to update it
            config["DefaultGenome"]["num_inputs"] = str(args.inputs)
            with open(CONFIG_FILE, "w") as config_file:
                config.write(config_file)
    else:
        args.inputs =  int(config["DefaultGenome"]["num_inputs"]) # Otherwise, keep the config value

    if args.sensing_length > MAX_RADAR_SENSING_LENGTH:
        if args.verbose:
            print(f"=> Overriding radar sensing length: {args.sensing_length} (given) to {MAX_RADAR_SENSING_LENGTH} (max)")
        args.sensing_length = MAX_RADAR_SENSING_LENGTH

    if args.sensing_length <= 0:
        if args.verbose:
            print(f"=> Overriding radar sensing length: {args.sensing_length} (given) to {DEF_RADAR_SENSING_LENGTH} (default)")
        args.sensing_length = DEF_RADAR_SENSING_LENGTH

    return args


class Car:

    def __init__(self, display_radars):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('car.png').convert() # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite 

        # self.position = [690, 740] # Starting Position
        self.position = [830, 920] # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False # Flag For Default Speed Later on

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2] # Calculate Center

        self.radars = [] # List For Sensors / Radars
        self.drawing_radars = [] # Radars To Be Drawn
        self.border_distances = [0] * args.inputs # The 'distances' read by the 'sensors'

        self.alive = True # Boolean To Check If Car is Crashed

        self.distance = 0 # Distance Driven
        self.time = 0 # Time Passed

        self.display_radars = args.display_radars


    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position) # Draw Sprite
        self.draw_radar(screen) #OPTIONAL FOR SENSORS


    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        if self.display_radars:
            for radar in self.radars:
                position = radar[0]
                pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
                pygame.draw.circle(screen, (0, 255, 0), position, 5)


    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break


    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < args.sensing_length:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
    

    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 10
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1
        
        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        # Calculate Four Corners
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        sensor_angles = self.get_radar_sensor_angles(args.inputs)
        for d in sensor_angles:
            self.check_radar(d, game_map)

    def get_radar_sensor_angles(self, num_inputs):
        angles = []
        angle_step = int(R_VIEW_ANGLE / int(args.inputs / 2))

        if num_inputs % 2 == 0:
            angle = int(angle_step / 2)
            angles.append(-angle)
        else:
            angle = 0

        angles.append(angle)

        for i in range(0, int(args.inputs / 2)):
            angle = angle + angle_step
            if angle <= R_VIEW_ANGLE:
                angles.append(angle)
                angles.append(-angle)

        angles.sort()
        return angles

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        for i, radar in enumerate(radars):
            self.border_distances[i] = int(radar[1] / 30)

        return self.border_distances


    def is_alive(self):
        # Basic Alive Function
        return self.alive


    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)


    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


def run_simulation(genomes, config):
    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car(args.display_radars))

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load('map02.png').convert() # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        for event in pygame.event.get():
            # Exit On Quit Event
            if event.type == pygame.QUIT:
                if args.verbose:
                    print("=> Quitting simulation")
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                # Exit when the Q button is pressed
                if event.key == pygame.K_q:
                    if args.verbose:
                        print("=> Quitting simulation")
                    sys.exit(0)
                # Display the menu when the M button is pressed
                elif event.key == pygame.K_m:
                    if args.verbose:
                        print("=> Display menu")
                elif event.key == pygame.K_r:
                    args.display_radars = args.display_radars ^ True
                    
                    if args.verbose:
                        print(f"=> Activate radar display: {args.display_radars}")
                else:
                    if args.verbose:
                        print("=> Unrecognized keystroke detected")

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            action = output.index(max(output))
            
            # Turn Left
            if action == 0:
                car.angle += 10 # Left
            # Turn Right
            elif action == 1:
                car.angle -= 10 # Right
            # Slow Down
            elif action == 2:
                if(car.speed - 2 >= 12):
                    car.speed -= 2 # Slow Down
            # Speed Up
            else:
                car.speed += 2 # Speed Up
            
            car.display_radars = args.display_radars
        
        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40: # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)
        
        # Display Info
        text = generation_font.render("Generation: " + str(current_generation), True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60) # 60 FPS

if __name__ == "__main__":
    args = parse_arguments()

    # Load Config
    config_path = CONFIG_FILE
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    # Initialize PyGame And The Display
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Run Simulation
    if args.verbose:
        print(f"=> Running simulation with max: {args.generations} generations")
    population.run(run_simulation, args.generations)
