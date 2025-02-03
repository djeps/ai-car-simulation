import os

# We need to set this environment variable before importing pygame
# in order to completely disable the access/initializtion of the sound engine
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import math
import pygame

from constants import *
from args import *

class Car:

    def __init__(self, args):
        self.args = args
        
        if not isinstance(args, Args):
            raise TypeError("'args' is not of type 'Args'!")
        
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load(f"images/sprites/{self.args.car_sprite}").convert_alpha() # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZES[self.args.car_size], CAR_SIZES[self.args.car_size]))
        self.rotated_sprite = self.sprite 

        self.position = [900, 910] # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False # Flag For Default Speed Later on

        self.center = [self.position[0] + int(CAR_SIZES[self.args.car_size] / 2), self.position[1] + int(CAR_SIZES[self.args.car_size] / 2)] # Calculate Center

        self.radars = [] # List For Sensors / Radars
        self.drawing_radars = [] # Radars To Be Drawn
        self.border_distances = [0] * self.args.inputs # The 'distances' read by the 'sensors'

        self.alive = True # Boolean To Check If Car is Crashed

        self.distance = 0 # Distance Driven
        self.time = 0 # Time Passed

        self.display_radars = self.args.display_radars


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
            pixel_color = game_map.get_at((int(point[0]), int(point[1])))
            if pixel_color == TRACK_BORDER_COLOR or pixel_color == OBSTACLE_BORDER_COLOR:
                self.alive = False

                break


    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While We Don't Hit TRACK_BORDER_COLOR AND length < self.args.sensing_length (just a max) -> go further and further
        pixel_color = game_map.get_at((x, y))
        while not (pixel_color == TRACK_BORDER_COLOR or pixel_color == OBSTACLE_BORDER_COLOR) and length < self.args.sensing_length:
            pixel_color = game_map.get_at((x, y)) # Update the pixel_color for the next iteration of the loop
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
        # Don't Let The Car Go Closer Than 60px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 60)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1
        
        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 60)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [int(self.position[0]) + int(CAR_SIZES[self.args.car_size] / 2), int(self.position[1]) + int(CAR_SIZES[self.args.car_size] / 2)]

        # Calculate Four Corners
        # Length Is Half The Side
        length = int(0.5 * CAR_SIZES[self.args.car_size])
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 50))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 50))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 130))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 130))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 230))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 230))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 310))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 310))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        sensor_angles = self.get_radar_sensor_angles(self.args.inputs)
        for d in sensor_angles:
            self.check_radar(d, game_map)


    def get_radar_sensor_angles(self, num_inputs):
        angles = []

        r_view_angle = int(self.args.view_angle / 2)
        angle_step = int(r_view_angle/ int(self.args.inputs / 2))

        if num_inputs % 2 == 0:
            angle = int(angle_step / 2)
            angles.append(-angle)
        else:
            angle = 0

        angles.append(angle)

        for i in range(0, int(self.args.inputs / 2)):
            angle = angle + angle_step
            if angle <= r_view_angle:
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
        return self.distance / (int(CAR_SIZES[self.args.car_size] / 2))


    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        
        return rotated_image


    def action(self, nn_action):
        if nn_action == 0:
            self.angle += 10 # Turn LEFT
        elif nn_action == 1:
            self.angle -= 10 # Turn RIGHT
        elif nn_action == 2:
            if(self.speed - 2 >= 10):
                self.speed -= 2 # Slow DOWN
        else:
            self.speed += 2 # Speed UP
            if self.speed > 100:
                self.speed = 100
