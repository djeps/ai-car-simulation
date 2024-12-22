# Files
CONFIG_FILE    = "./config.ini"
DEFAULT_SPRITE = "car01.png"
DEFAULT_MAP    = "map01.png"

# Exit codes
EXIT_SUCCESS      = 0
ERROR_SPRITE_LOAD = 2
ERROR_TRACK_LOAD  = 2

# Screen size
WIDTH = 1920
HEIGHT = 1080

# Sprite size and position
CAR_SIZES                = (10, 20, 30, 40, 50, 60, 70, 80, 90)
CAR_SIZE_X               = 60
CAR_SIZE_Y               = 60

# Simultation
BORDER_COLOR                 = (255, 255, 255, 255)
MAX_RADAR_SENSING_LENGTH     = 500
DEFAULT_RADAR_SENSING_LENGTH = 300
MAX_GENERATIONS              = 1000

# Sensors
DEFAULT_INPUTS = 5
MAX_INPUTS     = 36
VIEW_ANGLE     = 180
L_VIEW_ANGLE   = -int(VIEW_ANGLE / 2)
R_VIEW_ANGLE   = int(VIEW_ANGLE / 2)

# Starting text position
TEXT_POS_X = 5
TEXT_POS_Y = 5
