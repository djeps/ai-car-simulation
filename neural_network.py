import os

# We need to set this environment variable before importing pygame
# in order to completely disable the access/initializtion of the sound engine
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import random
import glob
import neat
import pygame
import pickle
import visualize

from constants import *
from args import *
from car import *
from game import *
from obstacle import *

from neat.checkpoint import Checkpointer

class TerminationException(Exception):
    pass


class NeatAlgo:

    def __init__(self, args, game_env):
        self.args = args
        self.game_env = game_env
        
        if not isinstance(args, Args):
            raise TypeError("'args' is not of type 'Args'!")
        
        self.keep_running = False
        
        self.pygame_is_initialized = pygame.get_init()

        if self.pygame_is_initialized:
            if not isinstance(game_env, GameEnvironment):
                raise TypeError("'game_env' is not of type 'GameEnvironment'!")
            
            self.TIMER_EVENT = pygame.USEREVENT + 1
            pygame.time.set_timer(self.TIMER_EVENT, 1000)
            self.tick_second = False

            self.screen = self.game_env.get_screen()
            self.clock = self.game_env.get_clock()

            self.generations_remaining = 0
            self.keep_running = True
            self.use_obstacles = False
        
            self.neat_config = self.__load_config__(CONFIG_FILE)
            self.trained_nn = None
            self.obstacles = dict()
            self.bz_backgrounds = list()

            self.game_map = pygame.image.load(f"images/tracks/{self.args.track_map}").convert()
        else:
            raise Exception("PyGame is not initialized!")


    def __load_config__(self, config_file):
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
        
        return config


    def __get_checkpoint__(self):
        file_name_pattern = "neat-checkpoint-"
        all_files = glob.glob(os.path.join("", "*"))

        self.checkpoint_number = 0
        self.checkpoint_file = None

        for file in all_files:
            if file_name_pattern in os.path.basename(file):
                self.checkpoint_file = file
                self.checkpoint_number = int(self.checkpoint_file.split("-", maxsplit=3)[2])
                break

        return (self.checkpoint_number, self.checkpoint_file)


    def __create_population__(self, config, new_training=True):
        if new_training:
            population = neat.Population(config)
        else:
            checkpoint = self.__get_checkpoint__()

            if checkpoint[0] != 0:
                population = Checkpointer.restore_checkpoint(checkpoint[1])
            else:
                population = neat.Population(config)

        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)
        population.add_reporter(Checkpointer(generation_interval=self.args.generation_interval, time_interval_seconds=self.args.time_interval_seconds, filename_prefix='neat-checkpoint-'))
        
        return population


    def __training_run__(self, genomes, config):
        # Empty Collections For Nets and Cars
        nets = []
        cars = []

        # Simple Counter To Roughly Limit Time (Not Good Practice)
        counter = 0

        keep_running = True

        # For All Genomes Passed Create A New Neural Network
        for i, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            g.fitness = 0

            cars.append(Car(self.args))

        # Clock Settings
        # Font Settings & Loading Map
        generation_font = pygame.font.SysFont("Open Sans", 14)
        alive_font = pygame.font.SysFont("Open Sans", 14)
        radar_status_font = pygame.font.SysFont("Open Sans", 14)

        self.generations_remaining -= 1

        game_map = self.game_map

        while keep_running:
            # --- Event processing ---
            for event in pygame.event.get():
                # Exit On Quit Event
                if event.type == pygame.QUIT:
                    if self.args.verbose:
                        print("=> Quitting training")
                    
                    keep_running = False
                    raise TerminationException("=> Desired fitness achieved! Aborting further training...")
                
                elif event.type == pygame.KEYDOWN:
                    # Exit when the Q button is pressed
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        if self.args.verbose:
                            print("=> Quitting training")
                        
                        keep_running = False
                        raise TerminationException("=> Desired fitness achieved! Aborting further training...")
                    
                    elif event.key == pygame.K_r:
                        self.args.display_radars = self.args.display_radars ^ True
                        
                        if self.args.verbose:
                            print(f"=> Activate radar display: {self.args.display_radars}")
                    else:
                        if self.args.verbose:
                            print("=> Unrecognized keystroke detected")

                elif event.type == self.TIMER_EVENT:
                    self.tick_second = True

            self.screen.blit(game_map, (0, 0))
            
            # For Each Car Get The Acton It Takes
            for i, car in enumerate(cars):
                output = nets[i].activate(car.get_data())
                nn_action = output.index(max(output))
                car.action(nn_action)
                car.display_radars = self.args.display_radars
            
            # Check If Car Is Still Alive
            # Increase Fitness If Yes And Break Loop If Not
            still_alive = 0
            for i, car in enumerate(cars):
                if car.is_alive():
                    still_alive += 1
                    car.update(game_map)
                    genomes[i][1].fitness += car.get_reward()

            if still_alive == 0:
                keep_running = False

            counter += 1
            if counter == 30 * 40: # Stop After About 20 Seconds
                keep_running = False

            # Draw Map And All Cars That Are Alive
            for car in cars:
                if car.is_alive():
                    car.draw(self.screen)
            
            if self.args.enable_obstacles:                
                self.__display_obstacles__(game_map)

            # --- Updating the display/text info ---
            text = generation_font.render(f"Generations remaining: {str(self.generations_remaining)}/{str(self.args.generations)}", True, (0,0,0))
            text_rect = text.get_rect()
            text_pos_y = TEXT_POS_Y
            text_rect.topleft = (TEXT_POS_X, TEXT_POS_Y)
            self.screen.blit(text, text_rect)

            text = alive_font.render(f"Cars still driving: {str(still_alive)}", True, (0, 0, 0))
            text_rect = text.get_rect()
            text_pos_y += 20
            text_rect.topleft = (TEXT_POS_X, text_pos_y)
            self.screen.blit(text, text_rect)

            text = radar_status_font.render(f"Radars visible: {'ON' if self.args.display_radars else 'OFF'}", True, (0, 0, 0))
            text_rect = text.get_rect()
            text_pos_y += 20
            text_rect.topleft = (TEXT_POS_X, text_pos_y)
            self.screen.blit(text, text_rect)

            # --- Updating the display ---
            pygame.display.flip()
            self.clock.tick(60) # 60 FPS


    def train_nn(self, sprite, map, new_training=True, neat_generations=0):
        # When new training is started
        self.neat_generations = self.args.generations
        self.generations_remaining = self.neat_generations
        
        # When continuing a training
        # We pass the the max generations number when the training was first initiated
        # through the 'next_generations' argument and from there,
        # we subtract the number of the last checkpoint generation
        if not new_training:
            self.neat_generations = neat_generations - self.__get_checkpoint__()[0]
            self.generations_remaining = self.neat_generations

        self.generations_remaining += 1
        self.neat_population = self.__create_population__(self.neat_config, new_training)

        # Start/continue a model training
        if self.args.verbose:
            print(f"=> Running training with: {self.generations_remaining} generations remaining")

        winner = None
        if self.pygame_is_initialized:
            try:
                # The winner neural network after the training has completed 
                winner = self.neat_population.run(self.__training_run__, self.neat_generations)
                
                # Save the winner genome
                with open("nn_winner.pkl", "wb") as f:
                    pickle.dump(winner, f)
                
                self.recent_nn_winner = True
            except TerminationException as e:
                print(f"=> Evolution terminated: {e}")
        else:
            raise Exception("PyGame is NOT initialized!")
        
        return winner


    def get_num_inputs(self, genome):
        if not genome.connections:  # If there are no connections, we can't infer inputs
            return 0
        
        all_nodes = set()
        output_nodes = set()
        
        for key, conn in genome.connections.items():
            input_node, output_node = key
            all_nodes.add(input_node)
            all_nodes.add(output_node)
            output_nodes.add(output_node)
        
        input_nodes = all_nodes - output_nodes

        return len(input_nodes)


    def __copy_bz_background__(self, surface, x, y, width, height):
        # Get a copy of the surface before drawing the bounding zone        
        bz_copy = pygame.Surface((width, height))
        bz_copy.blit(self.game_map, (0, 0), (x, y, width, height))
        self.bz_backgrounds.append((x, y, bz_copy))


    def __draw_obstacle__(self, surface, obstacle):
        bz_center = obstacle.get_center()
        bz_radius = obstacle.get_height() // 2
        bz_pen_width = 7

        # Draw a bounding zone around the obstacle
        pygame.draw.circle(surface, OBSTACLE_BORDER_COLOR, bz_center, bz_radius, bz_pen_width)

        self.screen.blit(obstacle.sprite, obstacle.get_rect())


    def __display_obstacles__(self, game_map):
        if self.args.track_map in self.obstacles:

            # Check and update on each second what obstacle needs to be displayed
            if self.tick_second:
                # Create a SystemRandom instance
                system_random = random.SystemRandom()
                # .. and using that instance as an entropy source, generate a random number
                random_number = system_random.randint(0, len(self.obstacles[self.args.track_map]) - 1)

                for i in range(0, len(self.obstacles[self.args.track_map])):
                    o = self.obstacles[self.args.track_map][i]
                    o.draw = False

                    if o.enabled:
                        if o.elapsed > o.time:
                            o.elapsed = 0
                        else:
                            if (o.elapsed == 0 and random_number == i) or o.elapsed > 0:
                                o.elapsed += 1
                                o.draw = True
                    
                    # Update the list element
                    self.obstacles[self.args.track_map][i] = o

                # We reset until the next 1s event is triggered
                self.tick_second = False
            
            # Then go through all obstalces once again and display only those which are flagged
            for i in range(0, len(self.obstacles[self.args.track_map])):
                # Redraw the backgrounds before the bounding zones
                bz_copy = self.bz_backgrounds[i][2]
                x = self.bz_backgrounds[i][0]
                y = self.bz_backgrounds[i][1]
                self.game_map.blit(bz_copy, (x, y))

                o = self.obstacles[self.args.track_map][i]
                
                if o.draw:
                    self.__draw_obstacle__(game_map, o)


    def __test_run__(self, sprite, map, winner):
        keep_running = True
        
        self.trained_nn = neat.nn.FeedForwardNetwork.create(winner, self.neat_config)

        # Get the number of inputs directly from the winning genome (trained neural network)
        num_inputs = self.get_num_inputs(winner)

        radar_status_font = pygame.font.SysFont("Open Sans", 14)

        car = Car(self.args)

        while keep_running:
            # --- Re-drawing the game map/surface ---
            game_map = self.game_map
            self.screen.fill(BACKGROUND)
            self.screen.blit(self.game_map, (0, 0))

            # --- Event processing ---
            for event in pygame.event.get():
                # Exit On Quit Event
                if event.type == pygame.QUIT:
                    if self.args.verbose:
                        print("=> Quitting simulation")
                    
                    keep_running = False
                elif event.type == pygame.KEYDOWN:
                    # Exit when the Q button is pressed
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        if self.args.verbose:
                            print("=> Quitting simulation")
                        
                        keep_running = False
                    elif event.key == pygame.K_r:
                        self.args.display_radars = self.args.display_radars ^ True
                        
                        if self.args.verbose:
                            print(f"=> Activate radar display: {self.args.display_radars}")

                    else:
                        if self.args.verbose:
                            print("=> Unrecognized keystroke detected")
                
                elif event.type == self.TIMER_EVENT:
                        self.tick_second = True
            
            # Car actions according to the trained model
            nn_output = self.trained_nn.activate(car.get_data())
            nn_action = nn_output.index(max(nn_output))
            car.action(nn_action)
            car.display_radars = self.args.display_radars # Update in case the user toggles this option during the run

            # --- Updating the car on the screen ---
            if car.is_alive():
                car.update(game_map)
                car.draw(self.screen)
            else:
                keep_running = False

                if (self.args.verbose):
                    print("=> GAME OVER!")

            # --- Updating the obstacles ---
            if self.args.enable_obstacles:                
                self.__display_obstacles__(game_map)
            
            # --- Updating the display/text info ---
            text = radar_status_font.render(f"Radars visible: {'ON' if self.args.display_radars else 'OFF'}", True, (0, 0, 0))
            text_rect = text.get_rect()
            text_pos_y = TEXT_POS_Y
            text_rect.topleft = (TEXT_POS_X, text_pos_y)
            self.screen.blit(text, text_rect)

            # --- Updating the display ---
            pygame.display.flip()
            self.clock.tick(60) # 60 FPS

    
    def test_nn(self, sprite, map, winner):
        if not self.pygame_is_initialized:
            raise Exception("PyGame is NOT initialized!")
        
        if winner is None:
            raise Exception("No previous training has been found! Aborting.")
        
        self.__test_run__(self.args.car_sprite, self.args.track_map, winner)
    

    def __update_obstacles__(self, obstacle):
        obstacle_count = 0

        if self.args.track_map in self.obstacles:
            obstacle_count = len(self.obstacles[self.args.track_map])

        if obstacle.position[0] and obstacle.position[1]:
            if self.args.track_map not in self.obstacles:
                self.obstacles[self.args.track_map] = [obstacle]
                obstacle_count = 1
            else:
                self.obstacles[self.args.track_map].append(obstacle)
                obstacle_count += 1

        return obstacle_count


    def __set_track_obstacles__(self, track_map):
        keep_running = True

        obstacles_count = len(self.obstacles[self.args.track_map]) if (self.args.track_map in self.obstacles) else 0
        obstacle = Obstacle(4, 10, True, (0, 0))
        obstacles_font = pygame.font.SysFont("Open Sans", 14)


        while keep_running:
            # --- Re-drawing the game map/surface ---
            game_map = self.game_map
            self.screen.fill(BACKGROUND)
            self.screen.blit(game_map, (0, 0))

            # --- Event processing ---
            for event in pygame.event.get():
                # Exit On Quit Event
                if event.type == pygame.QUIT:
                    if self.args.verbose:
                        print("=> Done setting obstacles")
                    keep_running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    obstacle.set_position(pygame.mouse.get_pos())

                elif event.type == pygame.KEYDOWN:
                    # Exit when the Q button is pressed
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        if self.args.verbose:
                            print("=> Done setting obstacles")
                        keep_running = False

                    elif event.key == pygame.K_e:
                        self.use_obstacles = self.use_obstacles ^ True # Toggle using obstacles
                        if self.args.verbose:
                            print(f"=> Using obstacles: {self.use_obstacles}")

                    elif event.key == pygame.K_RIGHT:
                        obstacle.size += 1
                        if obstacle.size > 8:
                            obstacle.size = 8
                        obstacle.rescale_sprite()

                    elif event.key == pygame.K_LEFT:
                        obstacle.size -= 1
                        if obstacle.size < 0:
                            obstacle.size = 0
                        obstacle.rescale_sprite()

                    elif event.key == pygame.K_UP:
                        obstacle.time += 5

                    elif event.key == pygame.K_DOWN:
                        obstacle.time -= 5
                        if obstacle.time < 0:
                            obstacle.time = 0

                    elif event.key == pygame.K_s:
                        obstacle.enabled = obstacle.enabled ^ True

                    elif event.key == pygame.K_n:
                        bz_x = obstacle.get_x()
                        bz_y = obstacle.get_y()
                        bz_w = obstacle.get_width()
                        bz_h = obstacle.get_height()
                        self.__copy_bz_background__(self.game_map, bz_x, bz_y, bz_w, bz_h)
                        obstacles_count = self.__update_obstacles__(obstacle)
                        
                        obstacle = Obstacle(4, 10, True, (0, 0))
                    else:
                        if self.args.verbose:
                            print("=> Unrecognized keystroke detected")

            # --- Updating the obstacle sprites ---
            if obstacle.position[0] and obstacle.position[1]:
                self.__draw_obstacle__(self.screen, obstacle)

            if self.args.track_map in self.obstacles:
                for o in self.obstacles[self.args.track_map]:
                    self.__draw_obstacle__(self.screen, o)

            # --- Updating the display/text info ---
            text = obstacles_font.render(f"Using obstacles for the next training session: {self.use_obstacles}", True, (0,0,0))
            text_rect = text.get_rect()
            text_pos_y = TEXT_POS_Y
            text_rect.topleft = (TEXT_POS_X, text_pos_y)
            self.screen.blit(text, text_rect)

            text = obstacles_font.render(f"Total obstacles: {obstacles_count}", True, (0,0,0))
            text_rect = text.get_rect()
            text_pos_y += 20
            text_rect.topleft = (TEXT_POS_X, text_pos_y)
            self.screen.blit(text, text_rect)

            text = obstacles_font.render(f"Current obstacle size: {obstacle.size}", True, (0,0,0))
            text_rect = text.get_rect()
            text_pos_y += 20
            text_rect.topleft = (TEXT_POS_X, text_pos_y)
            self.screen.blit(text, text_rect)

            text = obstacles_font.render(f"Current obstacle time (s): {obstacle.time}", True, (0,0,0))
            text_rect = text.get_rect()
            text_pos_y += 20
            text_rect.topleft = (TEXT_POS_X, text_pos_y)
            self.screen.blit(text, text_rect)
            
            text = obstacles_font.render(f"Current obstacle X position: {obstacle.position[0]}", True, (0,0,0))
            text_rect = text.get_rect()
            text_pos_y += 20
            text_rect.topleft = (TEXT_POS_X, text_pos_y)
            self.screen.blit(text, text_rect)

            text = obstacles_font.render(f"Current obstacle Y position: {obstacle.position[1]}", True, (0,0,0))
            text_rect = text.get_rect()
            text_pos_y += 20
            text_rect.topleft = (TEXT_POS_X, text_pos_y)
            self.screen.blit(text, text_rect)

            text = obstacles_font.render(f"Current obstacle enabled: {obstacle.enabled}", True, (0,0,0))
            text_rect = text.get_rect()
            text_pos_y += 20
            text_rect.topleft = (TEXT_POS_X, text_pos_y)
            self.screen.blit(text, text_rect)

            # --- Updating the display ---
            pygame.display.flip()
            self.clock.tick(60) # 60 FPS


    def set_track_obstacles(self, track_map):
        if self.pygame_is_initialized:
            self.__set_track_obstacles__(track_map)
        else:
            raise Exception("PyGame is NOT initialized!")


    def __clear_track_obstacles__(self, track_map):
        self.game_map = pygame.image.load(f"images/tracks/{track_map}").convert()
        
        if track_map in self.obstacles:
            if len(self.obstacles):
                del self.obstacles[track_map]
                del self.bz_backgrounds[:]


    def clear_track_obstacles(self, track_map):
        if self.pygame_is_initialized:
            self.__clear_track_obstacles__(track_map)
        else:
            raise Exception("PyGame is NOT initialized!")


    def generate_nn_image(self, winner, recent=True):
        node_names = {0: "Left", 1: "Right", 2: "Brake", 3: "Accelerate"}
        
        for i in range(-self.args.inputs, 0):
            node_names[i] = "S" + str(abs(i))

        if recent:
            if self.args.verbose:
                print("=> Successfully generated an image of the neural network topology")
            
            visualize.draw_net(self.neat_config, winner, view=False, node_names=node_names, filename="nn_winner", fmt="png")
        else:
            if self.args.verbose:
                print("=> Caution! The generated image of the neural network topology is NOT from a recent training run")

            visualize.draw_net(self.neat_config, winner, view=False, filename="nn_winner", fmt="png")


class NeuralNetwork:

    def __init__(self, args, game_env):
        self.args = args
        self.game_env = game_env
        
        if not isinstance(args, Args):
            raise TypeError("'args' is not of type 'Args'!")
        
        self.keep_running = False
        self.pygame_is_initialized = pygame.get_init()

        if self.pygame_is_initialized:
            if not isinstance(game_env, GameEnvironment):
                raise TypeError("'game_env' is not of type 'GameEnvironment'!")
        
            self.screen = self.game_env.get_screen()
            self.clock = self.game_env.get_clock()

            self.keep_running = True
        else:
            raise Exception("PyGame is not initialized!")
    
    
    def display_nn(self):
        self.keep_running = True

        screen_width, screen_height = self.screen.get_size()
        
        nn_winner_img = pygame.image.load("nn_winner.png").convert_alpha()

        nn_winner_font = pygame.font.SysFont("Open Sans", 24)
        nn_winner_text = nn_winner_font.render("Winner Neural Network Topology", True, FOREGROUND)
        
        nn_winner_rect = nn_winner_img.get_rect()
        nn_winner_rect.center = (screen_width // 2, screen_height // 2)

        nn_winner_text_rect = nn_winner_text.get_rect()
        nn_winner_text_rect.center = (screen_width // 2, nn_winner_rect.top - TEXT_POS_Y * 8)
        
        while self.keep_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.keep_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        self.keep_running = False
            
            self.screen.fill(BACKGROUND)
                        
            self.screen.blit(nn_winner_text, nn_winner_text_rect)
            self.screen.blit(nn_winner_img, nn_winner_rect)

            pygame.display.flip()
