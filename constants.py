# Files
CONFIG_FILE      = "./config.ini"
DEFAULT_SPRITE   = "car01.png"
DEFAULT_MAP      = "map01.png"
DEFAULT_OBSTACLE = "obstacle01.png"

# Exit codes
EXIT_SUCCESS      = 0
ERROR_SPRITE_LOAD = 2
ERROR_TRACK_LOAD  = 2

# Screen
WIDTH       = 1920
HEIGHT      = 1080
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
BACKGROUND  = WHITE_COLOR
FOREGROUND  = BLACK_COLOR

# Sprite size and position
CAR_SIZES                = (10, 20, 30, 40, 50, 60, 70, 80, 90)
CAR_SIZE_X               = 60
CAR_SIZE_Y               = 60
OBSTACLE_SIZES           = (10, 20, 30, 40, 50, 60, 70, 80, 90)
OBSTACLE_SIZE_X          = 60
OBSTACLE_SIZE_Y          = 60

# Simultation
TRACK_BORDER_COLOR           = (255, 255, 255, 255)
OBSTACLE_BORDER_COLOR        = (221, 221, 221, 255)
MAX_RADAR_SENSING_LENGTH     = 500
DEFAULT_RADAR_SENSING_LENGTH = 300
MAX_GENERATIONS              = 1000

# Sensors
DEFAULT_INPUTS     = 5
MAX_INPUTS         = 36
VIEW_ANGLE         = 180
MIN_VIEW_ANGLE     = 30
MAX_VIEW_ANGLE     = 360
DEFAULT_VIEW_ANGLE = VIEW_ANGLE
L_VIEW_ANGLE       = -int(VIEW_ANGLE / 2)
R_VIEW_ANGLE       = int(VIEW_ANGLE / 2)

# Starting text position
TEXT_POS_X = 5
TEXT_POS_Y = 5
