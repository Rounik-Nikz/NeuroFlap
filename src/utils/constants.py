import os

# Get the absolute path to the project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Asset paths
SPRITE_DIR = os.path.join(ROOT_DIR, 'src', 'sprites')
AUDIO_DIR = os.path.join(ROOT_DIR, 'src', 'audio')

# Bird sprites
BIRD_UPFLAP = os.path.join(SPRITE_DIR, 'redbird-upflap.png')
BIRD_MIDFLAP = os.path.join(SPRITE_DIR, 'redbird-midflap.png')
BIRD_DOWNFLAP = os.path.join(SPRITE_DIR, 'redbird-downflap.png')

# Other sprites
PIPE_SPRITE = os.path.join(SPRITE_DIR, 'pipe-green.png')
BACKGROUND_SPRITE = os.path.join(SPRITE_DIR, 'background-day.png')
GAMEOVER_SPRITE = os.path.join(SPRITE_DIR, 'gameover.png')

# Sound effects
SOUND_DIE = os.path.join(AUDIO_DIR, 'die.wav')
SOUND_HIT = os.path.join(AUDIO_DIR, 'hit.wav')
SOUND_POINT = os.path.join(AUDIO_DIR, 'point.wav')
SOUND_WING = os.path.join(AUDIO_DIR, 'wing.wav')

# Number sprites for score
NUMBER_SPRITES = {
    i: os.path.join(SPRITE_DIR, f'{i}.png') for i in range(10)
}

# Game states
STATE_PLAYING = 'playing'
STATE_GAME_OVER = 'game_over'

# Animation constants
ANIMATION_SPEED = 5  # frames between sprite changes

# Physics constants
GRAVITY = 0.5
FLAP_STRENGTH = -8
BIRD_MAX_VEL = 10

# Bird constants
BIRD_WIDTH = 50
BIRD_HEIGHT = 35

# Pipe constants
PIPE_SPEED = 3
PIPE_SPAWN_TIME = 2000  # milliseconds
PIPE_GAP = 200
PIPE_WIDTH = 70

# Colors (for fallbacks)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235)

# Create sprites directory if it doesn't exist
os.makedirs(SPRITE_DIR, exist_ok=True)

# Models directory inside rl module
MODELS_DIR = os.path.join(ROOT_DIR, 'src', 'rl', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)