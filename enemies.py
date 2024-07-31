"""
Asteroid Game - Enemies Module

This module contains classes for various enemies, such as Asteroid, UFO, Comet and Magnetic Mine. 
It handles enemy behaviors, movement, and interactions with other game objects.

Enemy types:
- Asteroid: The common enemy type in the game. Asteroids split to two smaller pieces when shot until they get destroyed completely. They leave valuable powerups for the player when destroyed. The bigger they are, the more hits they require.
- UFO: Special type of enemy that occurs depending on the level settings. UFOs have three different appearances which require 1-3 hits depending on type. They fire bullets at player and move in an irrational way.
- Comet: Special enemy that flies with high speed across the space in curves and leaves a deadly trail of comet dust behind it. Bumping into either comet or it's dust kills the player.
- Magnetic Mine: Special enemy that stays stationary until player flies too close. Then it chases player for 5 seconds before going off in a big explosion. 

Related Modules:
- player.py: Manages the player's ship and bullets.
- main.py: Entry point of the game.
- utils.py: Contains utility functions, constants, and particle effects.
"""

import pygame
import random

from utils import *
from sound import *

# Basic Asteroid enemy class
class Asteroid(GameObject):
    @classmethod
    def create_safe(cls, safe_objects, safe_radius, size, max_attempts=100):
        for _ in range(max_attempts):
            x = random.randint(0, BASE_WIDTH)
            y = random.randint(0, BASE_HEIGHT)
            if is_safe_position(x, y, safe_objects, safe_radius):
                return cls(x, y, size)
        return None  # Return None if we couldn't find a safe position

    def __init__(self, x, y, size, speed=None, angle=None):
        super().__init__(x, y, size)
        if speed is None:
            speed = random.uniform(*ASTEROID_SPEED_RANGE)
        if angle is None:
            angle = random.uniform(0, 2 * math.pi)
        self.dx = speed * math.cos(angle)
        self.dy = speed * math.sin(angle)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(*ASTEROID_ROTATION_RANGE)
        self.shape_type = random.choice([0, 1])  # 0 or 1 for two different shapes
        self.points = self.generate_shape()
        
        # Set initial strength based on size (larger asteroids are stronger)
        self.max_strength = ASTEROID_SIZES.index(self.size) + 1
        self.strength = self.max_strength

    def generate_shape(self):
        num_points = random.randint(7, 12)
        points = []
        for i in range(num_points):
            angle = i * (2 * math.pi / num_points)
            distance = self.size * random.uniform(0.7, 1.1)
            if self.shape_type == 0:
                # More angular shape
                if i % 2 == 0:
                    distance *= 0.8
            else:
                # More rounded shape
                if i % 3 == 0:
                    distance *= 1.2
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            points.append((x, y))
        return points

    def rotate_point(self, point):
        x, y = point
        rad = math.radians(self.rotation)
        cos_rad = math.cos(rad)
        sin_rad = math.sin(rad)
        return (x * cos_rad - y * sin_rad, x * sin_rad + y * cos_rad)

    def draw(self, screen):
        rotated_points = [self.rotate_point(point) for point in self.points]
        screen_points = [(self.x + x, self.y + y) for x, y in rotated_points]
        
        # Calculate line thickness based on remaining strength
        pygame.draw.polygon(screen, WHITE, screen_points, self.strength)

        # DEBUG: Add a number in the middle to indicate asteroid strength
        # font = pygame.font.Font(None, 20)
        # strength_text = font.render(f"{self.strength}", True, WHITE)
        # text_rect = strength_text.get_rect(center=(int(self.x), int(self.y)))
        # screen.blit(strength_text, text_rect)

    def update(self):
        super().move()
        self.rotation += self.rotation_speed
        self.rotation %= 360

    def hit(self):
        # New: Reduce strength when hit
        self.strength -= 1
        return self.strength <= 0

    def split(self, game_objects):
        if self.size > ASTEROID_SIZES[0]:
            new_size = ASTEROID_SIZES[ASTEROID_SIZES.index(self.size) - 1]
            new_asteroids = []
            
            for _ in range(2):
                angle = random.uniform(0, 2 * math.pi)
                distance = self.size * 0.75
                new_x = self.x + distance * math.cos(angle)
                new_y = self.y + distance * math.sin(angle)
                
                new_asteroid = Asteroid(new_x, new_y, new_size)
                new_asteroid.dx = self.dx + random.uniform(-0.5, 0.5)
                new_asteroid.dy = self.dy + random.uniform(-0.5, 0.5)
                
                new_asteroids.append(new_asteroid)
            
            return new_asteroids, Explosion(self.x, self.y, self.size)

        return [], Explosion(self.x, self.y, self.size)

# UFO enemy class
class UFO(GameObject):
    def __init__(self, x, y):
        self.ufo_type = random.choice(UFO_TYPES)
        if self.ufo_type == 'triangle':
            super().__init__(x, y, 10) # UFO size is 10
            self.shape = self.shape1 # Shaped like a triangle
            self.speed = 2 # fastest of the lot
            self.health = 1  # Triangle UFO takes 1 hit to destroy
        elif self.ufo_type == 'diamond':
            super().__init__(x, y, 15) # Mid sized
            self.shape = self.shape2
            self.speed = 1.5
            self.health = 2  # 2 hits to destroy
        else: # Saucer type UFO
            super().__init__(x, y, 20) # Largest
            self.shape = self.shape3
            self.speed = 1
            self.health = 3  # 3 hits to destroy
        self.direction = random.uniform(0, 2 * math.pi)
        self.direction_change_timer = 0
        self.shoot_timer = 90 # 1,5 seconds of grace period before UFO starts shooting
        self.sound_timer = 0
        self.sound_interval = 90  # Play sound every 1,5 seconds

    def update(self, ship):
        # Move the UFO
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)

        # Wrap around the screen
        self.x %= BASE_WIDTH
        self.y %= BASE_HEIGHT

        # Change direction occasionally
        self.direction_change_timer -= 1
        if self.direction_change_timer <= 0:
            self.direction = random.uniform(0, 2 * math.pi)
            self.direction_change_timer = random.randint(60, 180)  # Change direction every 1-3 seconds

        # Update shoot timer
        self.shoot_timer -= 1

        # Update the UFO presence sound
        if sound_state.on:
            self.sound_timer += 1
            if self.sound_timer >= self.sound_interval:
                ufo_sound.play()
                self.sound_timer = 0

    def draw(self, screen):
        self.shape(screen)

    def shape1(self, screen):
        # Triangular shape
        points = [
            (self.x, self.y - self.size),
            (self.x + self.size, self.y + self.size // 2),
            (self.x - self.size, self.y + self.size // 2)
        ]
        pygame.draw.polygon(screen, CYAN, points, 2)
        # Add a line at the bottom for the "cockpit"
        pygame.draw.line(screen, CYAN, (self.x - self.size // 2, self.y + self.size // 4), 
                         (self.x + self.size // 2, self.y + self.size // 4), 2)

    def shape2(self, screen):
        # Diamond shape
        points = [
            (self.x, self.y - self.size),
            (self.x + self.size, self.y),
            (self.x, self.y + self.size),
            (self.x - self.size, self.y)
        ]
        pygame.draw.polygon(screen, CYAN, points, 2)

    def shape3(self, screen):
        # Classic saucer shape
        pygame.draw.ellipse(screen, CYAN, (self.x - self.size, self.y - self.size // 2, self.size * 2, self.size), 2)
        pygame.draw.line(screen, CYAN, (self.x - self.size, self.y), (self.x + self.size, self.y), 2)

    def shoot(self, ship):
        if self.shoot_timer <= 0:
            # Calculate angle to the ship
            angle = math.atan2(ship.y - self.y, ship.x - self.x)
            self.shoot_timer = random.randint(60, 120)  # Shoot every 1-2 seconds
            return UFOBullet(self.x, self.y, angle)
        return None

class UFOBullet(GameObject):
    def __init__(self, x, y, angle):
        super().__init__(x, y, 3)
        self.speed = 4
        self.dx = self.speed * math.cos(angle)
        self.dy = self.speed * math.sin(angle)
        self.lifespan = 180  # 3 seconds at 60 FPS

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifespan -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.size)

# Comet enemy class
class Comet(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 15) # Size of 15, adjust as needed
        self.speed = COMET_SPEED
        self.angle = random.uniform(0, 2 * math.pi)
        self.trail = []
        self.trail_timer = 0
        self.trail_interval = COMET_TRAIL_FREQUENCY # New trail particle every 5 frames
        self.curve_direction = random.choice([-1, 1]) # Turning direction left or right
        self.direction_change_timer = random.randint(60, 240) # Change direction every 1-4 seconds
        self.direction_change_speed = random.uniform(0.005, 0.02) # Gradual direction change
        self.sound_playing = False

    def update(self):
        # Update position
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        
        # Wrap around screen
        self.x %= BASE_WIDTH
        self.y %= BASE_HEIGHT

        if sound_state.on:
            if not self.sound_playing:
                comet_rumble.play(-1)  # Loop the rumble
                self.sound_playing = True

        # Gradual direction change
        self.direction_change_timer -= 1
        if self.direction_change_timer <= 0:
            self.curve_direction = random.choice([-1, 1])
            self.direction_change_speed = random.uniform(0.005, 0.02)
            self.angle += self.direction_change_speed * self.curve_direction
            self.direction_change_timer = random.randint(60, 240)
        else:
            # Update angle for curved movement
            self.angle += self.direction_change_speed * self.curve_direction

        # Add new trail particle
        self.trail_timer += 1
        if self.trail_timer >= self.trail_interval:
            self.trail.append({
                'x': self.x - 15 * math.cos(self.angle),  # Offset to start trail behind comet
                'y': self.y - 15 * math.sin(self.angle),
                'lifespan': COMET_TRAIL_LIFESPAN,
                'size': random.uniform(5, 8)  # Varying sizes for trail particles
            })
            self.trail_timer = 0
        
        # Update trail particles
        for particle in self.trail:
            particle['lifespan'] -= 1
            particle['size'] *= 0.97  # Gradually shrink particles

        # Remove expired trail particles
        self.trail = [p for p in self.trail if p['lifespan'] > 0]

    def draw(self, screen):        
        # Flame properties
        flame_length = 30
        flame_width = 9
        flame_spacing = 1
        # Adjust the vertical position of the flames
        flame_offset = 19

        # Create the Comet surface
        comet_surface = pygame.Surface((self.size * 6, self.size * 6), pygame.SRCALPHA)
        center = (self.size * 3, self.size * 3)

        # Draw the flames
        flame_positions = [
            [center[0] - flame_width - flame_spacing, center[1] + self.size + flame_offset],  # Left flame
            [center[0], center[1] + self.size + flame_offset + 8],  # Middle flame
            [center[0] + flame_width + flame_spacing, center[1] + self.size + flame_offset]  # Right flame
        ]
        for flame_pos in flame_positions:
            flame_tip_pos = [flame_pos[0], flame_pos[1] - flame_length]
            color = random.choice([COMET_COLOR1, COMET_COLOR2]) # animate with colors
            horizontal_shift = random.randint(-2, 2) # animate with horizontal flame tip movement 
            tip_length = random.randint(-10, 10) # animate with varying flame length
            pygame.draw.polygon(comet_surface, color, [
                [flame_pos[0]-horizontal_shift, flame_pos[1]-tip_length],
                [flame_pos[0] - flame_width // 2, flame_tip_pos[1]],
                [flame_pos[0] + flame_width // 2, flame_tip_pos[1]]
            ])

        # Draw trail
        for particle in self.trail:
            color = random.choice([COMET_COLOR1, COMET_COLOR2, RED])
            surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)))
            pygame.draw.circle(surface, color, (int(particle['size']), int(particle['size'])), int(particle['size']))
            screen.blit(surface, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))
        
        # Draw the comet's body
        pygame.draw.circle(comet_surface, BLACK, center, self.size)
        pygame.draw.circle(comet_surface, WHITE, center, self.size, 2)

        # Rotate the entire comet (flames + head)
        rotated_comet = pygame.transform.rotate(comet_surface, -math.degrees(self.angle) - 90)
        comet_rect = rotated_comet.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_comet, comet_rect.topleft)
        
    def collides_with_trail(self, obj):
        for particle in self.trail:
            distance = math.sqrt((obj.x - particle['x'])**2 + (obj.y - particle['y'])**2)
            if distance < obj.size + 1:  # 1 is the radius of trail particles
                return True
        return False

# Magnetic Mine enemy class
class MagneticMine(GameObject):
    @classmethod
    def create_safe(cls, safe_objects, safe_radius):
        while True:
            x = random.randint(0, BASE_WIDTH)
            y = random.randint(0, BASE_HEIGHT)
            if is_safe_position(x, y, safe_objects, safe_radius):
                return cls(x, y)

    def __init__(self, x, y):
        super().__init__(x, y, 15)  # Increased size to 15 for better visibility
        self.speed = 0
        self.max_speed = MINE_MAX_SPEED
        self.acceleration = MINE_ACCELERATION  # Acceleration speed for gradual speed increase
        self.activated = False
        self.activation_distance = MINE_DISTANCE
        self.rotation_speed = 0.2
        self.rotation_angle = 0  # Initialize rotation angle
        self.chase_timer = 0
        self.max_chase_time = 5 * 60  # 5 seconds at 60 FPS
        self.flash_timer = 0
        self.flash_interval = 60  # Flash every 60 frames (1 second) when activated
        self.beep_timer = 0
        self.beep_interval = 30  # Beep initially every 60 frames (1 second) when activated

    # Function to create and add a new Magnetic Mine safely
    def add_magnetic_mine(magnetic_mines, safe_objects):
        safe_radius = SHIP_SAFE_RADIUS + MINE_DISTANCE
        new_mine = MagneticMine.create_safe(safe_objects, safe_radius)
        magnetic_mines.append(new_mine)

    def update(self, ship):
        if not self.activated:
            distance = math.sqrt((self.x - ship.x)**2 + (self.y - ship.y)**2)
            if distance < self.activation_distance:
                self.activated = True
        
        if self.activated:
            self.chase_timer += 1
            self.flash_timer += 1

            # Make the flashing light more intense as detonation gets near
            if self.chase_timer >= self.max_chase_time - 90:
                self.flash_interval = 10
            elif self.chase_timer >= self.max_chase_time - 180:
                self.flash_interval = 20

        # Beep with increasing intensity
        if sound_state.on and self.activated:
            self.beep_timer += 1
            if self.chase_timer >= self.max_chase_time - 90:
                self.beep_interval = 5
            elif self.chase_timer >= self.max_chase_time - 180:
                self.beep_interval = 15
            if self.beep_timer >= self.beep_interval:
                magnetic_mine_beep.play()  # Play mine beep sound
                self.beep_timer = 0

            # Calculate direction to ship
            dx = ship.x - self.x
            dy = ship.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                dx /= distance
                dy /= distance

            # Gradually accelerate towards ship
            self.speed = min(self.speed + self.acceleration, self.max_speed)
            self.x += dx * self.speed
            self.y += dy * self.speed

            # Update rotation angle
            self.rotation_angle = (self.rotation_angle + self.rotation_speed) % 360
            self.rotation_angle *= 1 + (self.acceleration/2)

    def draw(self, screen):
        # Create a surface to draw the mine on
        mine_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        mine_surface = mine_surface.convert_alpha()
        
        # Draw two ellipses on the surface
        pygame.draw.ellipse(mine_surface, WHITE, (0, self.size // 2, self.size * 2, self.size), 2)
        pygame.draw.ellipse(mine_surface, WHITE, (self.size // 2, 0, self.size, self.size * 2), 2)

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(mine_surface, self.rotation_angle)
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))

        # Draw the rotated surface on the screen
        screen.blit(rotated_surface, rotated_rect.topleft)
        
        # Draw blinking red dot in the middle when activated
        if self.activated:
            if self.flash_timer % self.flash_interval < self.flash_interval // 2:
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 3)

    def is_exploding(self):
        return self.activated and self.chase_timer >= self.max_chase_time
