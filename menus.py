"""
Asteroid Game - Menus Module

This module contains the Main menu class, handling the game's main menu. 

Related Modules:
- utils.py: Manages game constants and other general things.
- enemies.py: Manages enemies such as asteroids, which are drawn at the background of the menu screen
- main.py: Entry point of the game.
"""

import pygame
import random
import math

from enemies import *
from utils import *

# The cool looking ASTEROIDS logo 
def draw_asteroids_logo(surface, x, y, width, height):
    letters = "ASTEROIDS"
    letter_width = width // len(letters)
    stroke_width = max(1, int(letter_width * 0.05)) # change last number to 0.1 or even 0.15 for thicker stroke
    gap = int(letter_width * 0.1)

    def draw_letter(letter, index):
        lx = x + index * letter_width
        points = []
        if letter == 'A':
            points = [
                [(lx + gap, y + height), (lx + letter_width//2, y), (lx + letter_width - gap, y + height)],
                [(lx + letter_width//4, y + height//2), (lx + 3*letter_width//4, y + height//2)]
            ]
        elif letter == 'S':
            points = [[(lx + letter_width - gap, y), (lx + gap, y + height//3), 
                       (lx + letter_width - gap, y + 2*height//3), (lx + gap, y + height)]]
        elif letter == 'T':
            points = [
                [(lx + gap, y), (lx + letter_width - gap, y)],
                [(lx + letter_width//2, y), (lx + letter_width//2, y + height)]
            ]
        elif letter == 'E':
            points = [
                [(lx + letter_width - gap, y), (lx + gap, y), (lx + gap, y + height), (lx + letter_width - gap, y + height)],
                [(lx + gap, y + height//2), (lx + letter_width - gap, y + height//2)]
            ]
        elif letter == 'R':
            points = [
                [(lx + gap, y), (lx + gap, y + height)],
                [(lx + gap, y), (lx + letter_width - gap, y), (lx + letter_width - gap, y + height//2), (lx + gap, y + height//2)],
                [(lx + letter_width//2, y + height//2), (lx + letter_width - gap, y + height)]
            ]
        elif letter == 'O':
            points = [[(lx + gap, y), (lx + letter_width - gap, y), 
                       (lx + letter_width - gap, y + height), (lx + gap, y + height), (lx + gap, y)]]
        elif letter == 'I':
            points = [[(lx + letter_width//2, y), (lx + letter_width//2, y + height)]]
        elif letter == 'D':
            points = [[(lx + gap, y), (lx + letter_width - gap, y + height//4), 
                       (lx + letter_width - gap, y + 3*height//4), (lx + gap, y + height), (lx + gap, y)]]
        
        for point_set in points:
            pygame.draw.lines(surface, (255, 255, 255), False, point_set, stroke_width)

    for i, letter in enumerate(letters):
        draw_letter(letter, i)

# Return an explanation for the acronym ASTEROIDS - displayed on the main menu under the title
def get_random_acronym():
    acronyms = [
        "Ancient Stellar Travelers Explore Regions Of Infinite Darkness, Silently",
        "Anonymous Spaceship Traverses Eternal Realms, Obliterating Interstellar Debris Smoothly",
        "Astral Stones Tumble Endlessly, Rotating On Infinite Darkness, Shimmering",
        "Ancient Stellar Travelers Explore Realms Of Infinite Darkness, Silently",
        "Astronauts Steadily Track Errant Rocks, Observing Interplanetary Dangers Swiftly",
        "Across Starlit Terrain, Eerie Rogue Objects Invade Distant Systems",
        "Astronomical Sentinels Travel Effortlessly, Roaming Our Immense Dimension's Secrets",
        "Alien Stones Tell Enigmatic Riddles, Orbiting Idly Distant Suns",
        "Amidst Stellar Tapestry, Ethereal Rocks Orbit, Illustrating Destiny's Serpentine",
        "Aeons-old Stony Travelers Endure Rough Odysseys In Deepest Space",
        "Asteroids Silently Thread Emptiness, Revealing Our Inexplicable Dimensional Secrets",
        "Adrift Stardust Tells Epic Romances Of Interstellar Debris, Swirling",
        "Awakened Stellar Titans Effortlessly Roam Our Infinite Domain, Sparkling",
        "Across Space-Time, Enigmatic Rocks Orbit Idly, Defying Spaceships",
        "Astral Sentinels Traverse Emptiness, Reminding Onlookers Infinity Defines Space",
        "Aimless Stone Travelers Embrace Remote Orbits, Inspiring Deep Speculation",
        "Ageless Stellar Tokens Endure, Revealing Omnipresent Interstellar Dust Streams",
        "Adventurous Spacefarers Track Elusive Rocks, Observing Interplanetary Debris Scatter",
        "Among Stars, Timeless Entities Revolve, Offering Insights: Destiny's Secrets",
        "Arcane Stones Trace Elegant Revolutions, Outlining Infinite Celestial Designs",
        "Aside Shimmering Twilight, Ethereal Rocks Outline Immense, Distant Spheres"
    ]
    return random.choice(acronyms)

# Return a space poem
def get_random_space_poem():
    poems = [
        "Floating through the void, Ancient rocks whisper secrets — Stars watch silently.",
        "Cosmic dance unfolds, Asteroids paint the night sky — Silent space explorers.",
        "Stardust and stone spin, Echoes of creation's song — Asteroid ballet.",
        "Celestial wanderers, Carrying tales of old cosmos — Rocks through eternity.",
        "Rocky travelers, Through the cosmic sea they glide — Silent, cold, alone.",
        "Dust and metal swirl, Fragments of a distant past — Echoes in the night.",
        "Space's rugged paths, Asteroids wander freely — Timeless journey's call",
        "In the vastness wide, Stones of history drift by — Stories left untold.",
        "Lonely travelers, Guardians of ancient time — Watchers of the stars.",
        "Celestial dance, Orbits carved in endless space — Silent witnesses.",
        "Fragments of old worlds, Drifting through the starlit sky — Eternal silence.",
        "Galactic wanderers, Shaped by eons' gentle touch — Cosmic symphony.",
        "Mysteries untold, Asteroids whisper through time — In the night they roam.",
        "Silent space nomads, Drifting through star-speckled dark — Asteroid whispers."
    ]
    return random.choice(poems)

# Main Menu class
class MainMenu:
    def __init__(self, level_manager):
        self.level_manager = level_manager
        self.options = ["Start Game", "Level Select: 1", "Sound: On", "Info", "Quit"]
        self.selected = 0
        self.levels_index = 0
        self.level_cheat = False
        self.powerup_cheat = False
        self.floating_asteroids = [Asteroid(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.choice(ASTEROID_SIZES)) for _ in range(5)] # put max 5 asteroids to float in the background
        self.info_screen = InfoScreen()
        self.current_acronym = get_random_acronym()  # Store the current acronym

    def update(self):
        for asteroid in self.floating_asteroids:
            asteroid.update()

    # Set the level in the menu
    def set_level_select(self, level):
        unlocked_levels = list(range(1, self.level_manager.highest_unlocked_level + 1))
        if level in unlocked_levels:
            self.levels_index = unlocked_levels.index(level)
            self.options[1] = f"Level Select: {level}"

    def update_level_options(self):
        unlocked_levels = list(range(1, self.level_manager.highest_unlocked_level + 1))
        self.levels_index = min(self.levels_index, len(unlocked_levels) - 1)
        self.options[1] = f"Level Select: {unlocked_levels[self.levels_index]}"

    # CHEAT: Checks how many levels the game has and unlocks them all
    def unlock_all_levels(self):
        self.level_manager.highest_unlocked_level = len(self.level_manager.levels)
        self.level_cheat = True
        # return Explosion(random.randint(0, WIDTH), random.randint(0, HEIGHT), 40)

    # CHEAT: Adds powerups at the beginning of each level
    def unlock_powerups(self):
        self.powerup_cheat = True
        # return Explosion(random.randint(0, WIDTH), random.randint(0, HEIGHT), 40)
        
    def draw(self, surface):
        surface.fill(BLACK)

        # Draw floating asteroids
        for asteroid in self.floating_asteroids:
            asteroid.draw(surface)

        # Draw title
        draw_asteroids_logo(surface, 100, 100, 600, 100)  # Adjust position and size as needed

        # Draw menu options
        font = pygame.font.Font(None, 36)
        for i, option in enumerate(self.options):
            color = YELLOW if i == self.selected else WHITE
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2 + i * 50))
            surface.blit(text, text_rect)

        # Credits
        font = pygame.font.Font(None, 24)
        font_italic = pygame.font.SysFont(None, 24, bold=False, italic=True)
        text1 = font_italic.render(self.current_acronym, True, WHITE)  # Use the stored acronym
        if self.level_cheat and not self.powerup_cheat:
            text2 = font.render("Cheat mode! All levels available", True, RED)
        elif self.powerup_cheat and not self.level_cheat:
            text2 = font.render("Cheat mode! Powerups added", True, RED)
        elif self.powerup_cheat and self.level_cheat:
            text2 = font.render("Cheat mode! Levels unlocked and Powerups added", True, RED)
        else:
            text2 = font.render("Made by Jussi & Claude 3.5", True, CYAN)
        text_rect1 = text1.get_rect(center=(BASE_WIDTH // 2, 230))
        text_rect2 = text2.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT - 20))
        surface.blit(text1, text_rect1)
        surface.blit(text2, text_rect2)

    def refresh_acronym(self):
        self.current_acronym = get_random_acronym()  # Method to get a new acronym

    # def refresh_poem(self):
    #     self.current_acronym = get_random_space_poem()  # Method to get a new poem

    def modify_option(self, direction):
        if self.selected == 1:  # Level selection
            unlocked_levels = list(range(1, self.level_manager.highest_unlocked_level + 1))
            self.levels_index = (self.levels_index + direction) % len(unlocked_levels)
            self.options[1] = f"Level Select: {unlocked_levels[self.levels_index]}"

    def handle_input(self, event):
        global WIDTH, HEIGHT, scale_factor, screen
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_LEFT:
                self.modify_option(-1)
            elif event.key == pygame.K_RIGHT:
                self.modify_option(1)
            elif event.key == pygame.K_l:
                self.unlock_all_levels() # Cheat button L unlocks all levels!
            elif event.key == pygame.K_c:
                self.unlock_powerups() # Cheat button C unlocks powerups!
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.selected == 0:
                    unlocked_levels = list(range(1, self.level_manager.highest_unlocked_level + 1))
                    return PLAYING, unlocked_levels[self.levels_index]
                elif self.selected == 2:
                    if sound_state.on:
                        self.options[2] = "Sound: Off" # Turned sounds off
                        pygame.mixer.stop()  # Stop all sounds
                    else:
                        self.options[2] = "Sound: On" # Turned sounds on
                    toggle_sound()
                elif self.selected == 3:
                    return INFO, None
                elif self.selected == 4:
                    return None, None  # Quit the game
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                return None, None  # Quit the game
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
        return MENU, None

class InfoScreen:
    def __init__(self):
        self.asteroid_rotation = 0
        self.ufo_x_offset = 0
        self.ufo_direction = 1
        self.mine_rotation = 0
        self.mine_flash_timer = 0
        self.comet_flame_timer = 0
        # Create persistent enemy instances
        self.example_asteroid = Asteroid(WIDTH // 2 - 50, 132, 20)
        self.example_ufo = UFO(WIDTH // 2 - 50, 176)
        self.example_comet = Comet(WIDTH // 2 - 50, 220)
        self.example_mine = MagneticMine(WIDTH // 2 - 50, 264)

        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        self.info1_text = [
            "CONTROLS:",
            "Arrow or WAD keys - Move ship",
            "No braking in vacuum!",
            "Space or LCtrl - Shoot",
            "P - Pause game",
            "ESC - Exit to menu",
            "",
            "POWERUPS:",
            "      Protects from three direct hits",
            "      Fire three bullets at once",
            "      Bullets travel longer",
            "      Fire in all directions",
            "      Continuous shooting",
            "      Larger, more damaging bullets",
            "",
            "THE POINT: Win all 20 levels with increasing difficulty. Boss battles every 5 levels"
        ]

        self.info2_text = [
            "ENEMIES:",
            "Asteroids: Break into smaller pieces when shot",
            "UFO: Shoots at the player, comes in different sizes",
            "Comet: Fast-moving, leaves a deadly trail",
            "Magnetic Mine: Starts chasing when activated",
            "BOSSES:",
            "Daddy Asteroid: Breaks into shrapnels when shot",
            "Rocket: Chases the player relentlessly",
            "Gravity Well: Sucks the player in",
            "The Seven: Requires the eyes to be killed first"
        ]
    
    def draw(self, surface):
        surface.fill(BLACK)

        title = self.title_font.render("Game Information", True, WHITE)
        surface.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 20))

        # First column
        y = 80
        for line in self.info1_text:
            text = self.font.render(line, True, WHITE)
            surface.blit(text, (30, y))
            y += 30

        # Second column
        y = 80        
        for line in self.info2_text:
            text = self.font.render(line, True, WHITE)
            surface.blit(text, (BASE_WIDTH // 2 - 20, y))
            y += 44

        press_key = self.font.render("Press any key to return to the main menu", True, WHITE)
        surface.blit(press_key, (BASE_WIDTH // 2 - press_key.get_width() // 2, 570))

        # Draw example enemies and powerups
        self.draw_examples(surface)

    def draw_examples(self, screen):
        # Asteroid
        self.example_asteroid.rotation = self.asteroid_rotation
        self.example_asteroid.draw(screen)
        self.asteroid_rotation = (self.asteroid_rotation + 1) % 360

        # UFO
        self.example_ufo.x = BASE_WIDTH // 2 - 50 + self.ufo_x_offset
        self.example_ufo.draw(screen)
        self.ufo_x_offset += self.ufo_direction / 2
        if abs(self.ufo_x_offset) > 10:
            self.ufo_direction *= -1

        # Comet
        self.example_comet.angle = math.pi / 5  # Rotate some 60 degrees clockwise
        self.example_comet.trail_timer = self.comet_flame_timer
        self.example_comet.draw(screen)
        self.comet_flame_timer = (self.comet_flame_timer + 1) % COMET_TRAIL_FREQUENCY

        # Magnetic Mine
        self.example_mine.activated = True
        self.example_mine.rotation_angle = self.mine_rotation
        self.example_mine.flash_timer = self.mine_flash_timer
        self.example_mine.draw(screen)
        self.mine_rotation = (self.mine_rotation + 2.5) % 360  # Slow rotation speed
        self.mine_flash_timer += 1

        # Draw example powerups
        powerup_y = 328
        self.font2 = pygame.font.Font(None, 20)
        for power_type, color in POWERUP_COLORS.items():
            pygame.draw.circle(screen, color, (36, powerup_y), 10, 1)
            text = self.font2.render(power_type[0].upper(), True, color)
            screen.blit(text, (32, powerup_y - 7))
            powerup_y += 30

    def handle_input(self, event):
        global WIDTH, HEIGHT, scale_factor, screen
        if event.type == pygame.KEYDOWN:
            return MENU, None
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
        return INFO, None