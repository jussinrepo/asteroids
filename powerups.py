"""
Asteroid Game - Utility Module

This module contains functions for Asteroid game powerups, their behaviour and management.

Related Modules:
- player.py, bullet.py, enemies.py, powerups.py, menu.py, game.py, main.py
"""

import pygame

from utils import *

# PowerUp class
class PowerUp(GameObject):
    def __init__(self, x, y, power_type):
        super().__init__(x, y, POWERUP_SIZE)
        self.power_type = power_type
        self.lifespan = POWERUP_LIFESPAN
        self.original_size = POWERUP_SIZE

    def update(self):
        self.lifespan -= 1
        if self.lifespan <= POWERUP_SHRINK_DURATION:
            shrink_factor = self.lifespan / POWERUP_SHRINK_DURATION
            self.size = int(self.original_size * shrink_factor)

    def draw(self, screen):
        color = POWERUP_COLORS.get(self.power_type, WHITE)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size, 1)
        font = pygame.font.Font(None, self.size)
        text = font.render(self.power_type[0].upper(), True, color)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)

class PowerUpManager:
    def __init__(self):
        self.active_powerups = {}
        self.powerup_effects = {
            'shield': self.activate_shield,
            'triple_shot': self.activate_triple_shot,
            'longshot': self.activate_longshot,
            'omnishot': self.activate_omnishot,
            'rapid_fire': self.activate_rapid_fire,
            'big_shot': self.activate_big_shot
        }

    def activate_powerup(self, power_type, ship):
        if power_type == 'omnishot':
            return self.activate_omnishot(ship)
        else:
            if power_type in self.active_powerups:
                self.active_powerups[power_type] = POWERUP_LIFESPANS[power_type]
            else:
                self.active_powerups[power_type] = POWERUP_LIFESPANS[power_type]
            self.powerup_effects[power_type](ship)
        return []  # Return an empty list for non-omnishot powerups

    def update(self, ship):
        for power_type in list(self.active_powerups.keys()):
            self.active_powerups[power_type] -= 1
            if self.active_powerups[power_type] <= 0:
                del self.active_powerups[power_type]
                self.deactivate_powerup(power_type, ship)

    def activate_omnishot(self, ship):
        new_bullets = []
        angle_step = 360 / OMNISHOT_BULLET_COUNT
        for i in range(OMNISHOT_BULLET_COUNT):
            angle = i * angle_step
            new_bullets.append(ship.shoot_omnishot(angle))
        return new_bullets

    def activate_shield(self, ship):
        ship.shield = True
        ship.shield_hits = 0

    def activate_triple_shot(self, ship):
        ship.triple_shot = True

    def activate_longshot(self, ship):
        ship.longshot = True

    def activate_rapid_fire(self, ship):
        ship.rapid_fire = True

    def activate_big_shot(self, ship):
        ship.big_shot = True
    
    def deactivate_powerup(self, power_type, ship):
        if power_type == 'shield':
            ship.shield = False
        elif power_type == 'triple_shot':
            ship.triple_shot = False
        elif power_type == 'longshot':
            ship.longshot = False
        elif power_type == 'rapid_fire':
            ship.rapid_fire = False
        elif power_type == 'big_shot':
            ship.big_shot = False

    def draw_icons(self, screen, scale_float):
        icon_size = int(POWERUP_ICON_SIZE * scale_float)
        margin = int(POWERUP_ICON_MARGIN * scale_float)
        scale_int = int(scale_float)
        icon_x = WIDTH - margin - icon_size
        icon_y = margin + 60 * max(scale_int, 1) # position the first icon below the Level indicator
        for power_type, time_left in self.active_powerups.items():
            icon_color = POWERUP_COLORS.get(power_type, WHITE)
            if time_left <= 3 * FPS:  # Blink for the last 3 seconds
                if (time_left // 15) % 2 == 0:  # Blink every 15 frames
                    icon_color = (40, 40, 40)  # grey out but don't remove completely from screen
            pygame.draw.circle(screen, icon_color, (icon_x, icon_y), icon_size // 2, max(scale_int, 1))
            font = pygame.font.Font(None, int(20 * scale_float))
            text = font.render(power_type[0].upper(), True, icon_color)
            text_rect = text.get_rect(center=(icon_x, icon_y))
            screen.blit(text, text_rect)
            icon_y += icon_size + margin
