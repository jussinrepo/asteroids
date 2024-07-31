"""
Asteroid Game - Utility Module

This module contains functions , constants, and the base class GameObject.
It includes particle effects, common game constants, and helper functions.

Related Modules:
- player.py, bullet.py, enemies.py, powerups.py, menu.py, game.py, main.py
"""

import pygame
import math
import random

# Constants and Game Configuration
GAME_VERSION = 1.4
BASE_WIDTH, BASE_HEIGHT = 800, 600
GAME_ASPECT_RATIO = BASE_WIDTH / BASE_HEIGHT
WIDTH, HEIGHT = BASE_WIDTH, BASE_HEIGHT
scale_factor = 1
FPS = 60
LEVEL_TRANSITION_TIME = 3000 # how long between level changes in ms
EXPLOSION_DURATION = 45  # Increase duration for more impact
EXPLOSION_PARTICLES = 30  # Increase particles for a denser effect
EXPLOSION_COLORS = [(255, 255, 255), (255, 255, 0), (255, 165, 0), (255, 69, 0)]  # White, Yellow, Orange, Red-Orange

# Colors
LETTERBOX_COLOR = (50, 50, 50)
WHITE = (255, 255, 255)
GREY = (150, 150, 150)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
PURPLE = (255, 100 , 255)
CYAN = (100, 255 , 255)
ORANGE = (255, 150, 70)
COMET_COLOR1 = (255, 255, 0)
COMET_COLOR2 = (255, 192, 0)

# Player Ship
SHIP_TURN_SPEED = 5
SHIP_ACCELERATION = 0.1
SHIP_MAX_SPEED = 5
THRUST_FLAME_LENGTH = 15
THRUST_FLAME_WIDTH = 8
BULLET_SPEED = 5
BULLET_LIFESPAN = 60
SHIP_SAFE_RADIUS = 100  # Safe radius around the ship

# Asteroids
ASTEROID_SIZES = [10, 20, 30, 45, 75] # easy to add even huge asteroids
ASTEROID_SPEED_RANGE = (0.1, 1) # how fast asteroids appear to fly once created
ASTEROID_ROTATION_RANGE = (0.5, 2.0)  # how fast asteroids spin, degrees per frame
ASTEROID_SAFE_RADIUS = 60  # Safe radius around other asteroids
MIN_SPLIT_ANGLE = 45  # Minimum angle difference between split asteroids
MAX_SPLIT_ANGLE = 120  # Maximum angle difference between split asteroids
SPLIT_SPEED_FACTOR = 1.2
MAX_SPLIT_ATTEMPTS = 10
SAFE_DISTANCE_FACTOR = 1.2  # Multiplier for minimum safe distance between asteroids
PUSH_FORCE = 0.5  # Strength of the push when placing new asteroids
MIN_PUSH_DISTANCE = 5  # Minimum distance to apply push

# Other Enemies
UFO_TYPES = ['triangle', 'diamond', 'saucer']
UFO_FREQUENCIES = ["None", "Rare", "Frequent", "Rampant"]
COMET_FREQUENCIES = ["None", "Rare", "Frequent", "Rampant"]
COMET_SPEED = 3
COMET_TRAIL_FREQUENCY = 2 # frame interval betweel trail dust
COMET_TRAIL_LIFESPAN = 1 * FPS # 1 second at 60 FPS
MINE_LIMIT = 5 # Maximum number of mines on screen
MINE_MAX_SPEED = 4 # the max speed the Mine can accelerate
MINE_ACCELERATION = 0.02 # the gradual acceleration speed of Mine
MINE_DISTANCE = 150 # the distance where the Mine gets activated
MINE_EXPLOSION_PARTICLES = 80  # Increase particles for a denser effect
MINE_EXPLOSION_COLORS = [(255, 255, 255), (255, 0, 0), (200, 0, 0), (170, 0, 0)]

# Boss variables
BOSSASTEROID_HEALTH = 40
BOSSASTEROID_SHOOT_CHANCE = 0.02 # 2% chance to shoot a splinter each frame
BOSSCHASER_HEALTH = 20
BOSSCHASER_SPEED = 4 
BOSSCHASER_TURNRATE = 0.02 # Adjust this to control how quickly it can turn
GRAVITYWELLBOSS_HEALTH = 25
GRAVITYWELLBOSS_PULL_STRENGTH = 0.1 # the strength of the gravitational pull
GRAVITYWELLBOSS_PULL_RADIUS = 340 # distance of the pull
OCTOBOSS_HEALTH = 30
OCTOBOSS_SPEED = 0.2 # default rotation speed
OCTOBOSS_APPENDAGE_COUNT = 7 # seven appendages
OCTOBOSS_APPENDAGE_HEALTH  = 2 # health points for each appendage
OCTOBOSS_APPENDAGE_INTERVAL = 30 * FPS # Appendages regeneration rate is 30 seconds
OCTOBOSS_BUBBLE_INTERVAL = 4 * FPS # fires homing bubbles every 4 seconds
OCTOBOSS_BUBBLE_LIFESPAN = 6 * FPS # bubbles chase player for 6 seconds
OCTOBOSS_BUBBLE_SPEED = 2 # bubble speed
OCTOBOSS_LASER_CHARGE_TIME = 3 * FPS  # 3 seconds at 60 FPS
OCTOBOSS_LASER_SWEEP_SPEED = math.pi / 360  # 90 degrees in 3 seconds at 60 FPS
OCTOBOSS_LASER_FIRING_INTERVAL = 5 * FPS  # 5 seconds at 60 FPS

# Power-ups
POWERUP_SIZE = 15 # collectable item size
POWERUP_LIFESPAN = 10 * FPS  # collectable item duration in seconds
POWERUP_SHRINK_DURATION = 2 * FPS  # 2 seconds to shrink
POWERUP_ICON_SIZE = 30
POWERUP_ICON_MARGIN = 10
POWERUP_BLINK_DURATION = 3 * FPS  # 3 seconds
POWERUP_BLINK_INTERVAL = 15  # Blink every 15 frames
SHIELD_MAX_HITS = 3
SHIELD_RADIUS = 20
SHIELD_EFFECT_DURATION = 30  # Duration of the shield flashing effect when hit
OMNISHOT_BULLET_COUNT = 32  # Number of bullets in the omnishot
RAPID_FIRE_COOLDOWN = 150 # milliseconds between shots when rapid_fire is active
POWERUP_RATES = ["None", "Scarce", "Rare", "Common", "Abundant"]
POWERUP_COLORS = {
    'shield': CYAN,
    'triple_shot': YELLOW,
    'longshot': PURPLE,
    'omnishot': ORANGE,
    'rapid_fire': RED,
    'big_shot': GREY
} 

# Define power-up lifespans in seconds
POWERUP_LIFESPANS = {
    'shield': 20 * FPS,
    'triple_shot': 10 * FPS,
    'longshot': 20 * FPS,
    'rapid_fire': 10 * FPS,
    'big_shot': 15 * FPS
}

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
INFO = 4

# Sound configuration and it's check function
class SoundState:
    def __init__(self):
        self.on = True

sound_state = SoundState()

def toggle_sound():
    sound_state.on = not sound_state.on

# Function to check if a position is safe. Used for asteroid placement
def is_safe_position(x, y, safe_objects, safe_radius):
    for obj in safe_objects:
        distance = math.sqrt((x - obj.x)**2 + (y - obj.y)**2)
        if distance < safe_radius + obj.size:
            return False
    return True

# Classes
class GameObject:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.dx = 0
        self.dy = 0

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.x %= BASE_WIDTH
        self.y %= BASE_HEIGHT

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 1)

    def collides_with(self, other):
        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        return distance < (self.size + other.size)

class Particle:
    def __init__(self, x, y, color, speed, size, lifespan):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.size = size
        self.lifespan = lifespan
        self.angle = random.uniform(0, 2 * math.pi)

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.lifespan -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particles(self, x, y, color, count, speed_range, size_range, lifespan_range):
        for _ in range(count):
            speed = random.uniform(*speed_range)
            size = random.uniform(*size_range)
            lifespan = random.randint(*lifespan_range)
            self.particles.append(Particle(x, y, color, speed, size, lifespan))

    def update(self):
        self.particles = [p for p in self.particles if p.lifespan > 0]
        for particle in self.particles:
            particle.update()

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

class Explosion:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.max_radius = size * 2  # Maximum radius of the explosion
        self.particles = []
        for _ in range(EXPLOSION_PARTICLES):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            radius = random.uniform(0, self.max_radius)
            color = random.choice(EXPLOSION_COLORS)
            self.particles.append({
                'angle': angle,
                'speed': speed,
                'radius': radius,
                'color': color,
                'size': random.uniform(1, 3) * (size / 20)  # Particle size scales with asteroid size
            })
        self.duration = EXPLOSION_DURATION

    def update(self):
        self.duration -= 1
        for particle in self.particles:
            particle['radius'] += particle['speed']

    def draw(self, screen):
        intensity = self.duration / EXPLOSION_DURATION
        for particle in self.particles:
            if particle['radius'] <= self.max_radius:
                x = self.x + particle['radius'] * math.cos(particle['angle'])
                y = self.y + particle['radius'] * math.sin(particle['angle'])
                color = [int(c * intensity) for c in particle['color']]
                size = int(particle['size'] * intensity)
                pygame.draw.circle(screen, color, (int(x), int(y)), size)

class MineExplosion:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.max_radius = size * 1.2  # Maximum radius of the explosion
        self.particles = []
        for _ in range(MINE_EXPLOSION_PARTICLES):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            radius = random.uniform(0, self.max_radius)
            color = random.choice(MINE_EXPLOSION_COLORS)
            self.particles.append({
                'angle': angle,
                'speed': speed,
                'radius': radius,
                'color': color,
                'size': random.uniform(1, 3) * (size / 20)  # Particle size scales with asteroid size
            })
        self.duration = EXPLOSION_DURATION

    def update(self):
        self.duration -= 1
        for particle in self.particles:
            particle['radius'] += particle['speed']

    def draw(self, screen):
        intensity = self.duration / EXPLOSION_DURATION
        for particle in self.particles:
            if particle['radius'] <= self.max_radius:
                x = self.x + particle['radius'] * math.cos(particle['angle'])
                y = self.y + particle['radius'] * math.sin(particle['angle'])
                color = [int(c * intensity) for c in particle['color']]
                size = int(particle['size'] * intensity)
                pygame.draw.circle(screen, color, (int(x), int(y)), size)
