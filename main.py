"""
Asteroid Game

This module is the entry point of the game, handling initialization and the main game loop. 
It initializes the game window, loads resources, and manages the game states.

Modules:
- boss.py: Manages various boss enemies, appearance, behaviour and projectiles.
- enemies.py: Manages various enemies: asteroids and UFOs.
- levels.py: Manages the game's levels which the player must complete to win the game.
- menus.py: Handles the main menu logic.
- player.py: Manages the player's ship, ship's death and bullets fired by the player.
- powerups.py: Manages different power-ups that the player can pick up to gain bonuses, such as Triple Shot or Shield.
- sound.py: Contains all the sound functions of the game.
- soundplayer.py: Tool to try out different sounds. NOT part of the game.
- utils.py: Contains utility functions such as particle effects and all game constants/variables.
"""

# Import Python modules
import pygame
import numpy as np
import math
import random

# Import other game files
from utils import *
from menus import MainMenu
from levels import LevelManager
from player import Ship, ShipDeathAnimation
from powerups import *
from enemies import *
from boss import *
from sound import * 

# Initialize Pygame and the mixer
pygame.init()

# function to handle the screen scaling and positioning
def scale_maintain_aspect_ratio(surface, target_size):
    target_width, target_height = target_size
    surface_width, surface_height = surface.get_size()
    
    scale = min(target_width / surface_width, target_height / surface_height)
    
    new_width = int(surface_width * scale)
    new_height = int(surface_height * scale)
    
    scaled_surface = pygame.transform.smoothscale(surface, (new_width, new_height))
    
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    
    return scaled_surface, (x_offset, y_offset)

# Main game loop, with MENU, PLAYING, PAUSED and GAME_OVER states
def main():
    global WIDTH, HEIGHT, scale_factor
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption(f"Asteroids v{GAME_VERSION}")
    game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    clock = pygame.time.Clock()
    level_manager = LevelManager()
    menu = MainMenu(level_manager)
    sound_state.on = True  # Initialize sound state
    game_state = MENU
    new_acronym = True
    ship = Ship()
    ship_death_animation = None
    asteroids = []
    ufo = None
    ufo_bullets = []
    ufo_spawn_timer = 180
    comet = None
    comet_spawn_timer = 180
    magnetic_mines = []
    mine_spawn_timer = 180
    boss = None
    splinters = []
    appendages = []
    bubbles = []
    boss_dead = False
    bullets = []
    powerups = []
    explosions = []
    particle_system = ParticleSystem()
    powerup_manager = PowerUpManager()
    score = 0
    level_complete_timer = None
    game_over_timer = 0
    celebration_explosions = []
    celebration_timer = 0
    celebration_interval = 400  # ms between each explosion
    celebration_explosion_count = 0
    win_condition = False

    if sound_state.on:
        main_theme.play()  # Play the game main theme melody

    # Reset game function is called every time a level is loaded
    def reset_game(keep_ship=False, start_level=None):
        nonlocal ship, asteroids, bullets, ufo, ufo_bullets, ufo_spawn_timer, comet, comet_spawn_timer, magnetic_mines, mine_spawn_timer, boss, boss_dead, splinters, appendages, bubbles, particle_system, explosions, celebration_explosions, celebration_explosion_count, level_complete_timer, win_condition, score, powerups, powerup_manager

        if not keep_ship: # reset everything when player starts a new game from menu
            ship = Ship()
            score = 0
            powerups = []
            powerup_manager = PowerUpManager()
            explosions = []

        if sound_state.on:
            pygame.mixer.stop()  # Stop playing the main theme
        
        ufo = None
        ufo_bullets = []
        ufo_spawn_timer = 180
        comet = None
        comet_spawn_timer = 180
        magnetic_mines = []
        mine_spawn_timer = 180
        boss = None
        splinters = []
        appendages = []
        bubbles = []
        boss_dead = False
        bullets = []
        particle_system = ParticleSystem()
        celebration_explosions = []
        celebration_explosion_count = 0
        level_complete_timer = None
        win_condition = False
        
        if start_level is not None:
            level_manager.current_level = start_level - 1  # Subtract 1 because levels are 0-indexed
        
        # Get the level player selected in the menu
        current_level = level_manager.get_current_level()

        # Check if it's a boss level the player starts and move the player away from the center
        if current_level.boss_type and score == 0:
            ship.x = BASE_WIDTH // 6
            ship.y = BASE_HEIGHT // 6

        if sound_state.on:
            if current_level.boss_type:
                boss_appear_sound.play()
            else:
                level_start_sound.play()  # Play the level start melody

        # Generate the level's asteroids
        asteroids = level_manager.generate_asteroids(ship)
        
        # Generate Boss if it's a boss level
        if current_level.boss_type:
            if current_level.boss_type == "BossAsteroid":
                boss = BossAsteroid()
            elif current_level.boss_type == "BossChaser":
                boss = BossChaser()
            elif current_level.boss_type == "GravityWellBoss":
                boss = GravityWellBoss()
            elif current_level.boss_type == "OctoBoss":
                boss = OctoBoss()
                boss.target = ship # Eyes track the player ship
    
        # Cheats - Press C in main mene to give player powerups at the beginning of each level:
        if menu.powerup_cheat:
            powerup_manager.activate_powerup('rapid_fire', ship)
            powerup_manager.activate_powerup('triple_shot', ship)
            powerup_manager.activate_powerup('longshot', ship)
            powerup_manager.activate_powerup('shield', ship)

    def get_ufo_spawn_chance():
        current_level = level_manager.get_current_level() # UFO spawn chance according to the level
        if current_level.ufo_frequency == "None" or boss or not asteroids: # No special enemies during boss fights or if all asteroids are gone
            return 0
        elif current_level.ufo_frequency == "Rare":
            return 0.1  # 10% chance per 5 seconds
        elif current_level.ufo_frequency == "Frequent":
            return 0.4  # 40% chance per 5 seconds
        else: # "Rampant"
            return 0.8  # 80% chance per 5 seconds

    def get_comet_spawn_chance():
        current_level = level_manager.get_current_level()
        if current_level.comet_frequency == "None" or boss or not asteroids:
            return 0
        elif current_level.comet_frequency == "Rare":
            return 0.1
        elif current_level.comet_frequency == "Frequent":
            return 0.3
        else:  # "Rampant"
            return 0.5

    def get_mine_spawn_chance():
        current_level = level_manager.get_current_level()
        if current_level.mine_frequency == "None" or boss or not asteroids:
            return 0
        elif current_level.mine_frequency == "Rare":
            return 0.1
        elif current_level.mine_frequency == "Frequent":
            return 0.3
        else:  # "Rampant"
            return 0.5

    def create_celebration_explosion(x, y):
        colors = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN]
        return Explosion(x, y, 40)  # Larger size for more impact

    def handle_events():
        global WIDTH, HEIGHT, scale_factor, screen
        nonlocal running, game_state, new_acronym
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
            elif event.type == pygame.KEYDOWN:
                if game_state == PLAYING:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_LCTRL:
                        new_bullets = ship.shoot(pygame.time.get_ticks())
                        bullets.extend(new_bullets)
                    elif event.key == pygame.K_p:
                        game_state = PAUSED
                    elif event.key == pygame.K_ESCAPE:
                        new_acronym = True
                        WIDTH, HEIGHT = pygame.display.get_window_size()
                        scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
                        game_state = MENU
                elif game_state == PAUSED and event.key == pygame.K_p:
                    game_state = PLAYING
                elif game_state == GAME_OVER and pygame.time.get_ticks() - game_over_timer >= 2000:
                    new_acronym = True
                    WIDTH, HEIGHT = pygame.display.get_window_size()
                    scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
                    game_state = MENU
                    celebration_explosions.clear()

    def handle_player_input():
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ship.rotate(SHIP_TURN_SPEED)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ship.rotate(-SHIP_TURN_SPEED)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            ship.thrust()
        if (keys[pygame.K_SPACE] or keys[pygame.K_LCTRL]) and ship.rapid_fire:
        # if keys[pygame.K_SPACE] and ship.rapid_fire:
            new_bullets = ship.shoot(pygame.time.get_ticks())
            bullets.extend(new_bullets)

    # Update each game object on screen each frame 
    def update_game_objects():
        ship.move()
        
        # Update all asteroids
        for asteroid in asteroids:
            asteroid.update()

        # Update all bullets
        for bullet in bullets[:]:
            bullet.update()
            if bullet.lifespan <= 0:
                bullets.remove(bullet)
        
        # Update all explosions
        for explosion in explosions[:]:
            explosion.update()
            if explosion.duration <= 0:
                explosions.remove(explosion)

        # Update and draw the UFO if it exists
        if ufo:
            ufo.update(ship)
            new_bullet = ufo.shoot(ship)
            if new_bullet:
                ufo_bullets.append(new_bullet)

        # Update and draw UFO bullets
        for bullet in ufo_bullets[:]:
            bullet.update()
            if bullet.lifespan <= 0:
                ufo_bullets.remove(bullet)

        # Update and draw the Comet if it exists
        if comet:
            comet.update()
            if sound_state.on:
                if not comet.sound_playing:
                    comet_rumble.play()
                    comet.sound_playing = True
            else:
                comet_rumble.stop()

        # Update and draw Magnetic Mines if any exists
        for mine in magnetic_mines[:]:
            mine.update(ship)

        # Update power-ups
        powerup_manager.update(ship)

        for powerup in powerups[:]:
            powerup.update()
            if powerup.lifespan <= 0:
                powerups.remove(powerup)
    
    def handle_collisions():
        nonlocal score, ship_death_animation, game_state, game_over_timer, ufo, comet, magnetic_mines
        
        # Bullet-Asteroid collisions
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                if bullet.collides_with(asteroid):
                    handle_asteroid_hit(asteroid, bullet)
                    break

        # Ship-Asteroid collisions
        for asteroid in asteroids[:]:
            if ship.collides_with(asteroid):
                handle_ship_collision(asteroid)

        # Asteroid-Asteroid collisions
        for i, asteroid1 in enumerate(asteroids):
            for asteroid2 in asteroids[i+1:]:
                if asteroid1.collides_with(asteroid2):
                    temp_dx, temp_dy = asteroid1.dx, asteroid1.dy
                    asteroid1.dx, asteroid1.dy = asteroid2.dx, asteroid2.dy
                    asteroid2.dx, asteroid2.dy = temp_dx, temp_dy
        
        # Ship-Powerup collisions
        for powerup in powerups[:]:
            if ship.collides_with(powerup):
                new_bullets = powerup_manager.activate_powerup(powerup.power_type, ship)
                bullets.extend(new_bullets)
                if powerup.power_type == 'shield':
                    ship.shield_hits = 0
                pucolor = POWERUP_COLORS.get(powerup.power_type, WHITE)
                particle_system.add_particles(powerup.x, powerup.y, pucolor, 15, (1.5, 2.5), (1, 3), (45, 60))
                powerups.remove(powerup)

        # Check for collisions between player bullets and UFO
        if ufo:
            for bullet in bullets[:]:
                if ufo.collides_with(bullet):
                    bullets.remove(bullet)
                    ufo.health -= bullet.damage
                    score += 5
                    if ufo.health <= 0:
                        score += 45 # total of 50 points for killing the UFO
                        # Add large explosion for UFO destruction
                        particle_system.add_particles(ufo.x, ufo.y, random.choice(EXPLOSION_COLORS), 
                                                    50, (1, 3), (2, 5), (60, 90))
                        ufo = None
                        break
                    else:
                        # Add impact particles
                        particle_system.add_particles(bullet.x, bullet.y, YELLOW, 5, (0.5, 1.5), (2, 3), (15, 30))
        
        # Check for collisions between UFO bullets and player ship
        for bullet in ufo_bullets[:]:
            if ship.collides_with(bullet):
                if ship.shield:
                    ship.shield_effect = SHIELD_EFFECT_DURATION
                    ship.shield_hits += 1
                    if sound_state.on:
                        shield_hit_sound.play()  # Play the shield hit sound
                    if ship.shield_hits >= SHIELD_MAX_HITS:
                        ship.shield = False
                        powerup_manager.active_powerups.pop('shield', None)
                    ufo_bullets.remove(bullet)
                else:
                    ship_death_animation = ShipDeathAnimation(ship)
                    if sound_state.on:
                        ship_crash_sound.play()  # Play the ship crash sound
                    game_state = GAME_OVER
                    game_over_timer = pygame.time.get_ticks()
                break

        # Check for collisions with Comet
        if comet:
            # Check for collisions with ship
            if ship.collides_with(comet) or comet.collides_with_trail(ship):
                ship_death_animation = ShipDeathAnimation(ship)
                if sound_state.on:
                    ship_crash_sound.play()  # Play the ship crash sound
                    comet_rumble.stop()
                game_state = GAME_OVER
                game_over_timer = pygame.time.get_ticks()

            # Check for collisions with player bullets
            for bullet in bullets[:]:
                if comet.collides_with(bullet):
                    bullets.remove(bullet)
                    score += 20
                    explosions.append(Explosion(comet.x, comet.y, comet.size))
                    if sound_state.on:
                        explosion_sound.play()  # Play the explosion sound
                        comet_rumble.stop()
                    comet = None
                    break

        # Check collisions for Magnetic Mines
        for mine in magnetic_mines[:]:
            if mine.is_exploding():
                explosion = MineExplosion(mine.x, mine.y, mine.size * 5) # Quadruple explosion size
                explosions.append(explosion)

                if sound_state.on:
                    mine_explosion_sound.play()  # Play the mine explosion sound

                # Check if the ship is within the explosion radius
                distance = math.sqrt((ship.x - mine.x)**2 + (ship.y - mine.y)**2)
                if distance <= explosion.size:
                    ship_death_animation = ShipDeathAnimation(ship)
                    game_state = GAME_OVER
                    game_over_timer = pygame.time.get_ticks()

                magnetic_mines.remove(mine)
                continue

            if ship.collides_with(mine):
                explosions.append(MineExplosion(mine.x, mine.y, mine.size * 5)) # Quintuple explosion size
                magnetic_mines.remove(mine)
                ship_death_animation = ShipDeathAnimation(ship)
                if sound_state.on:
                    mine_explosion_sound.play()  # Play the mine explosion sound
                game_state = GAME_OVER
                game_over_timer = pygame.time.get_ticks()
                break

            for bullet in bullets[:]:
                if mine.collides_with(bullet):
                    bullets.remove(bullet)
                    explosions.append(Explosion(mine.x, mine.y, mine.size))
                    magnetic_mines.remove(mine)
                    score += 15
                    break

        # Check for collisions for OctoBoss Soap Bubbles
        if isinstance(boss, OctoBoss):
            for bubble in boss.bubbles[:]:
                for bullet in bullets[:]:
                    if bubble.collides_with(bullet):
                        boss.bubbles.remove(bubble)
                        bullets.remove(bullet)
                        score += 5
                        particle_system.add_particles(bubble.x, bubble.y, (200, 200, 255), 15, (1.5, 2.5), (1, 3), (45, 60))
                        break

    def handle_asteroid_hit(asteroid, bullet):
        nonlocal score
        asteroid.strength -= bullet.damage
        if asteroid.strength <= 0:
            asteroids.remove(asteroid)
            new_asteroids, explosion = asteroid.split(asteroids + [ship])
            asteroids.extend(new_asteroids)
            if explosion:
                explosions.append(explosion)
            score += 10
        else:
            particle_system.add_particles(bullet.x, bullet.y, GREY, 5, (0.5, 1.5), (1, 2), (15, 30))
            score += 2
        bullets.remove(bullet)
        if sound_state.on:
            asteroid_hit_sound.play()  # Play the asteroid being shot sound
        spawn_powerup(asteroid)

    def handle_ship_collision(asteroid):
        nonlocal ship_death_animation, game_state, game_over_timer, score
        if ship.shield:
            apply_shield_effect()
            new_asteroids, explosion = asteroid.split([ship] + asteroids)
            asteroids.remove(asteroid)
            asteroids.extend(new_asteroids)
            if explosion:
                explosions.append(explosion)
            if sound_state.on:
                shield_hit_sound.play()  # Play the shield hit sound
            score += 10
        else:
            if sound_state.on:
                ship_crash_sound.play()  # Play the ship crash sound
            ship_death_animation = ShipDeathAnimation(ship)
            game_state = GAME_OVER
            game_over_timer = pygame.time.get_ticks()

    def handle_enemy_spawning():
        nonlocal ufo, comet, magnetic_mines, ufo_spawn_timer, comet_spawn_timer, mine_spawn_timer
        # UFO spawning
        if ufo is None:
            ufo_spawn_timer -= 1
            if ufo_spawn_timer <= 0:
                spawn_chance = get_ufo_spawn_chance()
                if random.random() < spawn_chance:
                    edge = random.choice(['top', 'bottom', 'left', 'right'])
                    if edge == 'top':
                        ufo = UFO(random.randint(0, BASE_WIDTH), 0)
                    elif edge == 'bottom':
                        ufo = UFO(random.randint(0, BASE_WIDTH), BASE_HEIGHT)
                    elif edge == 'left':
                        ufo = UFO(0, random.randint(0, BASE_HEIGHT))
                    else:
                        ufo = UFO(BASE_WIDTH, random.randint(0, BASE_HEIGHT))
                ufo_spawn_timer = 300  # Check for UFO spawning every 5 seconds

        # Comet spawning
        if comet is None:
            comet_spawn_timer -= 1
            if comet_spawn_timer <= 0:
                spawn_chance = get_comet_spawn_chance()
                if random.random() < spawn_chance:
                    edge = random.choice(['top', 'bottom', 'left', 'right'])
                    if edge == 'top':
                        comet = Comet(random.randint(0, BASE_WIDTH), 0)
                    elif edge == 'bottom':
                        comet = Comet(random.randint(0, BASE_WIDTH), BASE_HEIGHT)
                    elif edge == 'left':
                        comet = Comet(0, random.randint(0, BASE_HEIGHT))
                    else:
                        comet = Comet(BASE_WIDTH, random.randint(0, BASE_HEIGHT))
                comet_spawn_timer = 300  # Check for comet spawning every 5 seconds

        # Magnetic Mine spawning
        if len(magnetic_mines) < MINE_LIMIT: # Limit the number of mines on screen
            mine_spawn_timer -= 1
            if mine_spawn_timer <= 0:
                spawn_chance = get_mine_spawn_chance()
                if random.random() < spawn_chance:
                    MagneticMine.add_magnetic_mine(magnetic_mines, [ship])
                mine_spawn_timer = 300  # Check for mine spawning every 5 seconds        

    # Shield hit --> Show the visual effect and reduce shield strength
    def apply_shield_effect():
        ship.shield_effect = SHIELD_EFFECT_DURATION
        ship.shield_hits += 1
        if ship.shield_hits >= SHIELD_MAX_HITS:
            ship.shield = False
            powerup_manager.active_powerups.pop('shield', None)

    def spawn_powerup(asteroid):
        if asteroid.size == 10:
            current_level = level_manager.get_current_level()
            spawn_chance = get_powerup_spawn_chance(current_level.powerup_rarity)
            if random.random() < spawn_chance:
                if sound_state.on:
                    powerup_sound.play()  # Play the powerup spawn sound
                power_type = random.choice(['shield', 'triple_shot', 'longshot', 'omnishot', 'rapid_fire', 'big_shot'])
                powerups.append(PowerUp(asteroid.x, asteroid.y, power_type))

    def get_powerup_spawn_chance(rarity):
        return {
            "Abundant": 0.5,
            "Common": 0.3,
            "Rare": 0.2,
            "Scarce": 0.1,
            "None": 0
        }.get(rarity, 0)

    def handle_boss():
        nonlocal boss, boss_dead, score, ship_death_animation, game_state, game_over_timer, splinters
        
        if not boss:
            return
        if isinstance(boss, GravityWellBoss):
            boss.update(ship, asteroids)
        elif isinstance(boss, BossChaser):
            boss.update(ship)
        elif isinstance(boss, BossAsteroid):
            boss.update(ship, splinters)
            # Update and check collisions for splinters
            for splinter in splinters[:]:
                splinter.update()
                if splinter.lifespan <= 0:
                    splinters.remove(splinter)
                elif ship.collides_with(splinter):
                    if ship.shield:
                        ship.shield_effect = SHIELD_EFFECT_DURATION
                        ship.shield_hits += 1
                        if ship.shield_hits >= SHIELD_MAX_HITS:
                            ship.shield = False
                            powerup_manager.active_powerups.pop('shield', None)
                        splinters.remove(splinter)
                        if sound_state.on:
                            shield_hit_sound.play()  # Play the shield hit sound
                    else:
                        ship_death_animation = ShipDeathAnimation(ship)
                        if sound_state.on:
                            ship_crash_sound.play()  # Play the ship crash sound
                        game_state = GAME_OVER
                        game_over_timer = pygame.time.get_ticks()
        elif isinstance(boss, OctoBoss):
            boss.update(ship)
            # Check for collisions between ship and OctoBoss bubbles
            for bubble in boss.bubbles[:]:
                if ship.collides_with(bubble):
                    if ship.shield:
                        ship.shield_effect = SHIELD_EFFECT_DURATION
                        ship.shield_hits += 1
                        if ship.shield_hits >= SHIELD_MAX_HITS:
                            ship.shield = False
                            powerup_manager.active_powerups.pop('shield', None)
                        boss.bubbles.remove(bubble)
                        if sound_state.on:
                            shield_hit_sound.play()  # Play the shield hit sound
                    else:
                        ship_death_animation = ShipDeathAnimation(ship)
                        if sound_state.on:
                            ship_crash_sound.play()  # Play the ship crash sound
                        game_state = GAME_OVER
                        game_over_timer = pygame.time.get_ticks()
                    break

        # Boss-ship collision
        if ship.collides_with(boss):
            handle_ship_boss_collision()

        # Boss-bullet collisions
        for bullet in bullets[:]:
            if handle_boss_bullet_collision(bullet):
                break
        
        # Laser-ship collision
        if isinstance(boss, OctoBoss):
            if boss.check_laser_collision(ship):
                ship_death_animation = ShipDeathAnimation(ship)
                if sound_state.on:
                    ship_crash_sound.play()  # Play the ship crash sound
                game_state = GAME_OVER
                game_over_timer = pygame.time.get_ticks()            

    def handle_ship_boss_collision():
        nonlocal ship_death_animation, game_state, game_over_timer
        ship_death_animation = ShipDeathAnimation(ship)
        if sound_state.on:
            ship_crash_sound.play()  # Play the ship crash sound
        game_state = GAME_OVER
        game_over_timer = pygame.time.get_ticks()

    def handle_boss_bullet_collision(bullet):
        nonlocal boss, boss_dead, score
        if isinstance(boss, OctoBoss):
            return handle_octoboss_bullet_collision(bullet)
        elif boss.collides_with(bullet):
            if boss.hit(bullet.damage):
                score += 500
                explosions.append(Explosion(boss.x, boss.y, boss.size * 2))
                boss_dead = True
                boss = None
            else:
                if isinstance(boss, BossAsteroid):
                    collision_point = (bullet.x, bullet.y)
                    splinter = boss.shoot_splinter(collision_point, ship)
                    splinters.append(splinter)
                    boss.increase_splinter_rate() # more splinter chance every time it gets hurt
                score += 5
                particle_system.add_particles(bullet.x, bullet.y, RED, 20, (0.5, 1), (1, 2), (120, 180))
            bullets.remove(bullet)
            return True
        return False

    def handle_octoboss_bullet_collision(bullet):
        nonlocal boss, boss_dead, score
        hit = False
        for appendage in boss.appendages:
            if appendage.active and math.hypot(bullet.x - appendage.end_x, bullet.y - appendage.end_y) < 10:
                if appendage.hit(bullet.damage):
                    hit = True
                    score += 10
                    particle_system.add_particles(bullet.x, bullet.y, RED, 20, (1, 2), (1, 2.5), (180, 240))
                bullets.remove(bullet)
                return True
        if not hit and boss.collides_with(bullet):
            if boss.hit(bullet.damage):
                score += 500
                explosions.append(Explosion(boss.x, boss.y, boss.size * 2))
                boss_dead = True
                boss = None
            else:
                particle_system.add_particles(bullet.x, bullet.y, GREY, 20, (0.5, 1), (1, 2), (120, 180))
            bullets.remove(bullet)
            return True
        return False

    def check_level_completion():
        nonlocal level_complete_timer, win_condition, game_state, game_over_timer, celebration_timer, ufo_bullets
        current_time = pygame.time.get_ticks()
        
        if level_complete_timer and current_time - level_complete_timer > LEVEL_TRANSITION_TIME:
            if level_manager.next_level():
                level_manager.unlock_next_level()
                menu.update_level_options()
                reset_game(keep_ship=True)
            else:
                win_condition = True
                game_state = GAME_OVER
                game_over_timer = current_time
                celebration_timer = current_time
            level_complete_timer = None
        elif not asteroids and ufo is None and comet is None and not magnetic_mines and boss is None and not win_condition and level_complete_timer is None:
            if level_manager.is_final_level():
                win_condition = True
                game_state = GAME_OVER
                game_over_timer = current_time
                celebration_timer = current_time
            else: # Level complete - move on to the next one
                level_complete_timer = current_time
                if sound_state.on:
                    level_complete_sound.play()  # Play the level complete sound
                ufo_bullets = [] # We dont want to kill the player while level transition


    def handle_boss_death():
        nonlocal boss, boss_dead, splinters, bubbles, win_condition, game_state, game_over_timer, celebration_timer, level_complete_timer
        if boss and boss_dead:
            boss = None
            if level_manager.is_final_level():
                win_condition = True
                game_state = GAME_OVER
                game_over_timer = pygame.time.get_ticks()
                celebration_timer = pygame.time.get_ticks()
            else:
                level_complete_timer = pygame.time.get_ticks()

    def draw_game(surface):
        surface.fill(BLACK)
        
        ship.draw(surface)
        for bullet in bullets:
            bullet.draw(surface)
        if ufo:
            ufo.draw(surface)
        if comet:
            comet.draw(surface)
        for mine in magnetic_mines:
            mine.draw(surface)
        if boss and not boss_dead:
            boss.draw(surface)
            for splinter in splinters:
                splinter.draw(surface)
        for asteroid in asteroids:
            asteroid.draw(surface)
        for bullet in ufo_bullets[:]:
            bullet.draw(surface)
        for explosion in explosions:
            explosion.draw(surface)
        particle_system.update()
        particle_system.draw(surface)
        for powerup in powerups:
            powerup.draw(surface)

        # Draw UI elements directly on the screen
        draw_ui(surface)

    def draw_ui(screen):
        # Draw score
        score_font = pygame.font.Font(None, int(36 * scale_factor))
        score_text = score_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw level indicator
        level_font = pygame.font.Font(None, int(36 * scale_factor))
        level_text = level_font.render(f"Level: {level_manager.current_level + 1}", True, WHITE)
        level_rect = level_text.get_rect(right=BASE_WIDTH - 10, top=10)
        screen.blit(level_text, level_rect)

        # Draw power-up icons
        powerup_manager.draw_icons(screen, scale_factor)

        # Draw transition texts if timers are active
        if level_complete_timer:
            draw_level_complete_text(screen)

        # DEBUG: Draw remaining asteroid and UFO count
        # font = pygame.font.Font(None, 24)
        # remaining_text = font.render(f"Asteroids: {len(asteroids)} | UFO: {'Yes' if ufo else 'No'}", True, WHITE)
        # screen.blit(remaining_text, (300, 10))

    def draw_level_complete_text(screen):
        font = pygame.font.Font(None, 64)
        if level_manager.is_next_final_level():
            text = font.render("FINAL BOSS!", True, RED)
        elif level_manager.is_next_boss_level():
            text = font.render("BOSS IS COMING", True, RED)
        else:
            text = font.render("LEVEL COMPLETE", True, GREEN)
        text_rect = text.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2))
        screen.blit(text, text_rect)
        
        if level_manager.current_level == 3:
            font2 = pygame.font.Font(None, 24)
            text2 = font2.render("You better move away from the center of the screen..", True, RED)
            text_rect2 = text2.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 1.3))
            screen.blit(text2, text_rect2)

    running = True
    while running:
        # Main menu loop
        if game_state == MENU:
            if new_acronym == True:  # Check if we need a new acronym
                menu.refresh_acronym()  # Refresh the acronym
                new_acronym = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                new_state, selected_level = menu.handle_input(event)
                if new_state == PLAYING:
                    level_manager.set_level(selected_level - 1)  # Levels are 0-indexed
                    reset_game(keep_ship=False)
                    WIDTH, HEIGHT = pygame.display.get_window_size()
                    scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
                    game_state = PLAYING
                elif new_state == INFO:
                    game_state = INFO
                elif new_state is None:
                    running = False
                    break

            if running:
                menu.update() # Update floating asteroids
                WIDTH, HEIGHT = pygame.display.get_window_size()
                scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
                game_surface.fill(BLACK)                
                menu.draw(game_surface)
                scaled_surface, blit_position = scale_maintain_aspect_ratio(game_surface, (WIDTH, HEIGHT))
                screen.fill(BLACK) # Menu screen can have black letterboxes..
                screen.blit(scaled_surface, blit_position)

        # Info screen loop
        elif game_state == INFO:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                new_state, _ = menu.info_screen.handle_input(event)
                if new_state == MENU:
                    new_acronym = True
                    WIDTH, HEIGHT = pygame.display.get_window_size()
                    scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
                    game_state = MENU

            if running:
                WIDTH, HEIGHT = pygame.display.get_window_size()
                scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
                game_surface.fill(BLACK)
                menu.info_screen.draw(game_surface)
                scaled_surface, blit_position = scale_maintain_aspect_ratio(game_surface, (WIDTH, HEIGHT))
                screen.fill(BLACK) # Info screen can have black letterboxes..
                screen.blit(scaled_surface, blit_position)

        # Main gameplay loop - split into functions
        elif game_state == PLAYING:
            handle_events()
            handle_player_input()
            update_game_objects()
            handle_collisions()
            handle_enemy_spawning()
            handle_boss()
            check_level_completion()
            handle_boss_death() 

            # Clear the game surface, Draw the game on the game surface and Scale and blit the game surface onto the screen
            game_surface.fill(BLACK)
            draw_game(game_surface)
            scaled_surface, blit_position = scale_maintain_aspect_ratio(game_surface, (WIDTH, HEIGHT))
            screen.fill(LETTERBOX_COLOR) # Edges cannot be black because the play area is
            screen.blit(scaled_surface, blit_position)

        # Game in pause mode
        elif game_state == PAUSED:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or pygame.K_p:
                        WIDTH, HEIGHT = pygame.display.get_window_size()
                        scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
                        game_state = PLAYING
            if running:
                font = pygame.font.Font(None, 64)
                text = font.render("PAUSED", True, WHITE)
                text_rect = text.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2))

                WIDTH, HEIGHT = pygame.display.get_window_size()
                scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
                game_surface.fill(BLACK)
                game_surface.blit(text, text_rect)
                scaled_surface, blit_position = scale_maintain_aspect_ratio(game_surface, (WIDTH, HEIGHT))
                screen.fill(BLACK) # PAUSE screen can have black letterboxes..
                screen.blit(scaled_surface, blit_position)

        # Player died or compeleted a level
        elif game_state == GAME_OVER:
            current_time = pygame.time.get_ticks()
            time_elapsed = current_time - game_over_timer

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and time_elapsed >= 2000:  # Reduced to 2 seconds
                    game_state = MENU
                    WIDTH, HEIGHT = pygame.display.get_window_size()
                    scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
                    ship_death_animation = None
                    celebration_explosions = []
                    if win_condition:
                        menu.set_level_select(len(level_manager.levels))  # Set to final level if won
                    else:
                        menu.set_level_select(level_manager.current_level + 1)  # Set to the level player died on

            screen.fill(BLACK)

            if win_condition:
                # Create celebration explosions in sequence
                if celebration_explosion_count < 8 and len(celebration_explosions) < 3 and current_time - celebration_timer > celebration_interval:
                    x = random.randint(BASE_WIDTH // 6, 5 * BASE_WIDTH // 6)
                    y = random.randint(BASE_HEIGHT // 6, 5 * BASE_HEIGHT // 6)
                    celebration_explosions.append(create_celebration_explosion(x, y))
                    celebration_timer = current_time
                    celebration_explosion_count += 1

                # Create a surface with the base dimensions
                base_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
                base_surface.fill(BLACK)

                # Update and draw celebration explosions
                for explosion in celebration_explosions:
                    explosion.update()
                    explosion.draw(base_surface)

                # Update and draw explosions
                for explosion in explosions[:]:
                    explosion.update()
                    if explosion.duration <= 0:
                        explosions.remove(explosion)
                    explosion.draw(base_surface)
                for bullet in bullets:
                    bullet.draw(base_surface)
                ship.draw(base_surface)

                # Scale the base surface to the current window size
                scaled_surface = pygame.transform.smoothscale(base_surface, (WIDTH, HEIGHT))
                screen.blit(scaled_surface, (0, 0))

                # Remove finished explosions
                celebration_explosions = [exp for exp in celebration_explosions if exp.duration > 0]

            if ship_death_animation:
                # Clear the game surface, Draw the game on the game surface and Scale and blit the game surface onto the screen
                game_surface.fill(BLACK)

                ship_death_animation.update()
                ship_death_animation.draw(game_surface)

                # Update and draw explosions. Also draw asteroids and bullets
                for explosion in explosions[:]:
                    explosion.update()
                    if explosion.duration <= 0:
                        explosions.remove(explosion)
                    explosion.draw(game_surface)
                for asteroid in asteroids:
                    asteroid.draw(game_surface)
                for bullet in bullets:
                    bullet.draw(game_surface)
                if ship_death_animation.is_finished():
                    ship_death_animation = None

                scaled_surface, blit_position = scale_maintain_aspect_ratio(game_surface, (WIDTH, HEIGHT))
                screen.fill(LETTERBOX_COLOR) # Edges cannot be black because the play area is
                screen.blit(scaled_surface, blit_position)

            if time_elapsed >= 2000:  # Show game over text after 2 seconds
                font = pygame.font.Font(None, 64)
                if win_condition:
                    text = font.render("YOU WIN!", True, GREEN)
                else:
                    text = font.render("GAME OVER", True, RED)
                    if sound_state.on:
                        game_over_sound.play()  # Play the game over sound

                # Clear the game surface, Draw the game on the game surface and Scale and blit the game surface onto the screen
                game_surface.fill(BLACK)
                text_rect = text.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2 - 50))
                game_surface.blit(text, text_rect)

                score_font = pygame.font.Font(None, 36)
                score_text = score_font.render(f"Final Score: {score}", True, WHITE)
                score_rect = score_text.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2))
                game_surface.blit(score_text, score_rect)

                continue_font = pygame.font.Font(None, 24)
                continue_text = continue_font.render("Press any key to return to the main menu", True, WHITE)
                continue_rect = continue_text.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2 + 50))
                game_surface.blit(continue_text, continue_rect)

                scaled_surface, blit_position = scale_maintain_aspect_ratio(game_surface, (WIDTH, HEIGHT))
                screen.fill(LETTERBOX_COLOR) # Edges cannot be black because the play area is
                screen.blit(scaled_surface, blit_position)


        if running:
            pygame.display.flip()
            clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
