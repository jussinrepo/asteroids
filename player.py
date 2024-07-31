"""
Asteroid Game - Player Module

This module contains the Player class, managing the player's ship. 
It handles player movement, shooting, and interactions with other game objects.

Related Modules:
- bullet.py: Manages bullets fired by the player.
- main.py: Entry point of the game.
"""

import pygame
import random

from utils import *
from sound import * 

class Ship(GameObject):
    def __init__(self):
        super().__init__(BASE_WIDTH // 2, BASE_HEIGHT // 2, 10)
        self.angle = 0
        self.thrusting = False
        self.shield = False
        self.shield_hits = 0
        self.shield_effect = 0
        self.triple_shot = False
        self.longshot = False
        self.rapid_fire = False
        self.last_shot_time = 0
        self.rapid_fire_coold = RAPID_FIRE_COOLDOWN
        self.big_shot = False

    def rotate(self, angle):
        self.angle += angle

    def thrust(self):
        self.dx += math.cos(math.radians(self.angle)) * SHIP_ACCELERATION
        self.dy -= math.sin(math.radians(self.angle)) * SHIP_ACCELERATION
        self.thrusting = True

        # Limit speed to SHIP_MAX_SPEED
        speed = math.sqrt(self.dx**2 + self.dy**2)
        if speed > SHIP_MAX_SPEED:
            factor = SHIP_MAX_SPEED / speed
            self.dx *= factor
            self.dy *= factor

    def draw(self, screen):
        points = [
            (self.x + self.size * math.cos(math.radians(self.angle)),
             self.y - self.size * math.sin(math.radians(self.angle))),
            (self.x + self.size * math.cos(math.radians(self.angle + 140)),
             self.y - self.size * math.sin(math.radians(self.angle + 140))),
            (self.x + self.size * math.cos(math.radians(self.angle + 220)),
             self.y - self.size * math.sin(math.radians(self.angle + 220)))
        ]
        pygame.draw.polygon(screen, WHITE, points, 2) # change the last number to 0 for filled polygon!

        # Draw shield if active
        if self.shield:
            shield_thickness = SHIELD_MAX_HITS - self.shield_hits
            pygame.draw.circle(screen, (0, 255, 255), (int(self.x), int(self.y)), SHIELD_RADIUS, shield_thickness)

        # Draw shield effect when hit
        if self.shield_effect > 0:
            intensity = self.shield_effect / SHIELD_EFFECT_DURATION
            color = (int(255 * intensity), int(255 * intensity), 255)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), SHIELD_RADIUS, 3)
            self.shield_effect -= 1

        # Draw thrust flame if accelerating
        if self.thrusting:
            flame_length = THRUST_FLAME_LENGTH
            flame_width = THRUST_FLAME_WIDTH
            
            # Calculate the base of the flame (middle of the ship's base)
            base_x = self.x - self.size * math.cos(math.radians(self.angle))
            base_y = self.y + self.size * math.sin(math.radians(self.angle))
            
            # Calculate the tip of the flame
            tip_x = base_x - flame_length * math.cos(math.radians(self.angle))
            tip_y = base_y + flame_length * math.sin(math.radians(self.angle))
            
            # Calculate the two base points of the isosceles triangle
            left_x = base_x + flame_width/2 * math.sin(math.radians(self.angle))
            left_y = base_y + flame_width/2 * math.cos(math.radians(self.angle))
            right_x = base_x - flame_width/2 * math.sin(math.radians(self.angle))
            right_y = base_y - flame_width/2 * math.cos(math.radians(self.angle))
            
            flame_points = [
                (left_x, left_y),
                (tip_x, tip_y),
                (right_x, right_y)
            ]
            pygame.draw.polygon(screen, (255, 165, 0), flame_points)  # Orange flame

        self.thrusting = False

    def shoot(self, current_time):
        if self.rapid_fire:
            if current_time - self.last_shot_time < self.rapid_fire_coold:
                return []
            self.last_shot_time = current_time

        bullet_lifespan = BULLET_LIFESPAN * 2 if self.longshot else BULLET_LIFESPAN
        if self.triple_shot:
            if sound_state.on:
                player_tripleshoot_sound.play()  # Play the shoot sound
            return [
                Bullet(self.x, self.y, self.angle, bullet_lifespan, self.big_shot),
                Bullet(self.x, self.y, self.angle + 15, bullet_lifespan, self.big_shot),
                Bullet(self.x, self.y, self.angle - 15, bullet_lifespan, self.big_shot)
            ]
        elif self.big_shot:
            if sound_state.on:
                player_bigshoot_sound.play()  # Play the shoot sound  
            return [Bullet(self.x, self.y, self.angle, bullet_lifespan, self.big_shot)]
        else:
            if sound_state.on:
                player_shoot_sound.play()  # Play the shoot sound
            return [Bullet(self.x, self.y, self.angle, bullet_lifespan, self.big_shot)]
    
    def shoot_omnishot(self, angle):
        bullet_lifespan = BULLET_LIFESPAN
        return Bullet(self.x, self.y, angle, bullet_lifespan, False) # Blast bullets are never big or longshot

class ShipDeathAnimation:
    def __init__(self, ship):
        self.x = ship.x
        self.y = ship.y
        self.lines = self.create_lines(ship)
        self.explosion = Explosion(self.x, self.y, ship.size * 2)
        self.duration = 120  # 2 seconds at 60 FPS

    def create_lines(self, ship):
        points = [
            (ship.x + ship.size * math.cos(math.radians(ship.angle)),
             ship.y - ship.size * math.sin(math.radians(ship.angle))),
            (ship.x + ship.size * math.cos(math.radians(ship.angle + 140)),
             ship.y - ship.size * math.sin(math.radians(ship.angle + 140))),
            (ship.x + ship.size * math.cos(math.radians(ship.angle + 220)),
             ship.y - ship.size * math.sin(math.radians(ship.angle + 220)))
        ]
        lines = []
        for i in range(3):
            start = points[i]
            end = points[(i + 1) % 3]
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            rotation = random.uniform(-2, 2)
            lines.append({
                'start': start,
                'end': end,
                'dx': dx,
                'dy': dy,
                'rotation': rotation
            })
        return lines

    def update(self):
        self.duration -= 1
        self.explosion.update()
        for line in self.lines:
            line['start'] = (line['start'][0] + line['dx'], line['start'][1] + line['dy'])
            line['end'] = (line['end'][0] + line['dx'], line['end'][1] + line['dy'])
            # Rotate the line
            center_x = (line['start'][0] + line['end'][0]) / 2
            center_y = (line['start'][1] + line['end'][1]) / 2
            line['start'] = self.rotate_point(line['start'], (center_x, center_y), line['rotation'])
            line['end'] = self.rotate_point(line['end'], (center_x, center_y), line['rotation'])

    def rotate_point(self, point, center, angle):
        x, y = point
        cx, cy = center
        radians = math.radians(angle)
        cos_rad = math.cos(radians)
        sin_rad = math.sin(radians)
        qx = cx + cos_rad * (x - cx) - sin_rad * (y - cy)
        qy = cy + sin_rad * (x - cx) + cos_rad * (y - cy)
        return (qx, qy)

    def draw(self, screen):
        self.explosion.draw(screen)
        for line in self.lines:
            pygame.draw.line(screen, WHITE, line['start'], line['end'], 2)

    def is_finished(self):
        return self.duration <= 0

# Player's bullet
class Bullet(GameObject):
    def __init__(self, x, y, angle, lifespan, is_big=False):
        super().__init__(x, y, 2)
        speed = BULLET_SPEED * 0.75 if is_big else BULLET_SPEED # Big shot is slower        
        self.dx = math.cos(math.radians(angle)) * speed
        self.dy = -math.sin(math.radians(angle)) * speed
        self.lifespan = lifespan
        self.is_big = is_big
        self.damage = 3 if is_big else 1

    def update(self):
        self.move()
        self.lifespan -= 1
    
    def draw(self, screen):
        color = GREY if self.is_big else WHITE
        bullet_size = 4 if self.is_big else self.size # Big shot is visually bigger and grey in color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), bullet_size)
