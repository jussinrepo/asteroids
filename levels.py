"""
Asteroid Game - Levels Module

This module contains the Level system and level information. 

Related Modules:
- utils.py: Manages game constants and other general things.
- enemies.py: Manages enemies such as asteroids, which are spawned at the beginning of each level
- main.py: Entry point of the game.
"""

import random

from utils import *
from enemies import Asteroid
from menus import MainMenu

class Level:
    def __init__(self, asteroid_sizes, ufo_frequency, comet_frequency, mine_frequency, powerup_rarity, boss_type=None):
        self.asteroid_sizes = asteroid_sizes # List of 5 integers representing count for each size
        self.ufo_frequency = ufo_frequency
        self.comet_frequency = comet_frequency
        self.mine_frequency = mine_frequency
        self.powerup_rarity = powerup_rarity
        self.boss_type = boss_type

class LevelManager:
    def __init__(self):
        # Level configuration: [tiny, small, medium, big, huge asteroid count], UFO frequency, Comet frequency, Mine frequency, PowerUp rarity, Boss type
        # UFO, Comet and Mine frequencies: "None", "Rare", "Frequent", "Rampant"
        # POWERUP_RATES: "None", "Scarce", "Rare", "Common", "Abundant"
        self.levels = [
            # Level([3, 0, 0, 0, 0], "None", "None", "None", "Abundant"),                 # Level 1
            Level([3, 0, 0, 0, 0], "None", "Rampant", "Rampant", "Abundant"),                 # Level 1
            Level([0, 2, 0, 0, 0], "None", "None", "None", "Abundant"),                 # Level 2
            Level([2, 2, 0, 0, 0], "None", "None", "None", "Common"),                   # Level 3
            Level([0, 0, 2, 0, 0], "None", "None", "None", "Rare"),                     # Level 4
            Level([2, 2, 1, 0, 0], "None", "None", "None", "Common", "BossAsteroid"),   # Level 5 (First Boss)
            Level([0, 0, 0, 2, 0], "Rare", "None", "None", "Abundant"),                 # Level 6
            Level([5, 5, 0, 0, 0], "Rare", "None", "None", "Abundant"),                 # Level 7
            Level([0, 0, 3, 3, 0], "Common", "None", "None", "Common"),                   # Level 8
            Level([4, 0, 0, 0, 1], "Common", "None", "None", "Common"),                   # Level 9
            Level([8, 4, 0, 0, 0], "Common", "None", "None", "Common", "BossChaser"),     # Level 10 (Second Boss)
            Level([20, 0, 0, 0, 0], "Rare", "Common", "None", "Common"),              # Level 11
            Level([2, 10, 0, 0, 0], "Common", "Common", "None", "Abundant"),            # Level 12
            Level([4, 4, 4, 2, 0], "Frequent", "Common", "None", "Common"),               # Level 13
            Level([0, 0, 0, 0, 2], "Frequent", "Frequent", "None", "Rare"),                 # Level 14
            Level([2, 3, 0, 0, 0], "Common", "Common", "None", "Rare", "GravityWellBoss"), # Level 15 (Third Boss)
            Level([0, 0, 0, 2, 2], "Rare", "Rare", "Common", "Common"),                # Level 16
            Level([0, 0, 0, 8, 0], "Rampant", "Rare", "Frequent", "Common"),                # Level 17
            # Level([3, 0, 0, 0, 0], "None", "None", "None", "Abundant"),                 # debug level 1
            # Level([3, 0, 0, 0, 0], "None", "None", "None", "Abundant"),                 # debug level 2
            Level([5, 0, 4, 0, 3], "Rare", "Rampant", "Common", "Rare"),                  # Level 18
            Level([5, 5, 5, 5, 5], "Common", "Common", "Common", "Common"),              # Level 19
            # Level([0, 0, 0, 1, 1], "Common", "Common", "Rare", "None", "OctoBoss")     # Level 20 (Final Boss)
            Level([2, 2, 2, 0, 0], "Common", "Common", "Rare", "None", "OctoBoss")     # Level 20 (Final Boss)
        ]
        self.current_level = 0
        self.highest_unlocked_level = 1  # Start with only the first level unlocked

    def get_current_level(self):
        return self.levels[self.current_level]

    def get_next_level(self):
        next_level = self.current_level + 1
        return self.levels[next_level]

    def next_level(self):
        if self.current_level < len(self.levels) - 1:
            self.current_level += 1
            return True
        return False

    def unlock_next_level(self):
        if self.highest_unlocked_level < len(self.levels):
            self.highest_unlocked_level += 1

    def is_level_unlocked(self, level):
        return level <= self.highest_unlocked_level

    def reset(self):
        self.current_level = 0

    def set_level(self, level):
        if 0 <= level < len(self.levels):
            self.current_level = level

    def is_boss_level(self):
        return self.get_current_level().boss_type is not None

    def is_next_boss_level(self):
        return self.get_next_level().boss_type is not None

    # Check if this was the final level - aka game finished
    def is_final_level(self):
        return self.current_level == len(self.levels) - 1

    # Check if this next level is final
    def is_next_final_level(self):
        return self.current_level == len(self.levels) - 2

    def generate_asteroids(self, ship):
        level = self.get_current_level()
        asteroids = []
        safe_radius = SHIP_SAFE_RADIUS
        max_attempts = 1000  # Maximum total attempts
        attempts = 0

        for size_index, count in enumerate(level.asteroid_sizes):
            size = ASTEROID_SIZES[size_index]
            for _ in range(count):
                asteroid = None
                local_attempts = 0
                while asteroid is None and attempts < max_attempts:
                    asteroid = Asteroid.create_safe([ship] + asteroids, safe_radius, size)
                    attempts += 1
                    local_attempts += 1
                    if local_attempts > 50:  # If we've tried 50 times for this asteroid
                        safe_radius *= 0.9  # Reduce safe radius by 10%
                        if safe_radius < size:  # If safe radius is smaller than asteroid, break
                            break

                if asteroid:
                    asteroids.append(asteroid)
                else:
                    break  # If we couldn't place this asteroid, stop trying to place more

            if attempts >= max_attempts:
                break  # If we've reached max attempts, stop trying to place more asteroids

        # If we couldn't place all asteroids, log a warning
        if sum(level.asteroid_sizes) != len(asteroids):
            print(f"Warning: Could only place {len(asteroids)} out of {sum(level.asteroid_sizes)} asteroids")

        return asteroids
