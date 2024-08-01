"""
Asteroid Game - Boss Module

This module contains classes for boss enemies. 
It handles boss behaviors, boss types, movement, and interactions with other game objects.

Current Boss type:
- BossAsteroid: A huge asteroid that floats in the center of the screen, shooting player with splinters randomly and when player hits the asteroid with bullets.
- BossChaser: A rocket shaped enemy that constantly flies towards the player ship, trying to collide with it.
- GravityWellBoss: A black hole sucking in player ship and asteroids, getting stronger the more damage it takes.
- OctoBoss: A seven tentacle boss shooting bubbles. Player needs to kill appendages first to be able to hurt the boss. Appendages regenerate after time and when vulnerable, the boss shoots lasers as well. Good luck!

Related Modules:
- player.py: Manages the player's ship and bullets.
- main.py: Entry point of the game.
- utils.py: Contains utility functions, constants, and particle effects.
"""

import pygame
import random

from utils import *
from sound import octoboss_bubble_sound, gravity_well_rumble, rocket_boss_swoosh

class Boss(GameObject):
    def __init__(self, x, y, size, health):
        super().__init__(x, y, size)
        self.health = health
        self.max_health = health

    def draw_health_bar(self, screen):
        bar_width = 100
        bar_height = 10
        fill_width = int((self.health / self.max_health) * bar_width)
        outline_rect = pygame.Rect(BASE_WIDTH // 2 - bar_width // 2, 20, bar_width, bar_height)
        fill_rect = pygame.Rect(BASE_WIDTH // 2 - bar_width // 2, 20, fill_width, bar_height)
        pygame.draw.rect(screen, RED, fill_rect)
        pygame.draw.rect(screen, WHITE, outline_rect, 2)

    def hit(self, damage):
        self.health -= damage
        return self.health <= 0

class BossChaser(Boss):
    def __init__(self):
        super().__init__(BASE_WIDTH // 2, BASE_HEIGHT // 2, 40, BOSSCHASER_HEALTH)  # Adjust size and health as needed
        self.speed = BOSSCHASER_SPEED
        self.direction = random.uniform(0, 2 * math.pi)
        self.turn_speed = BOSSCHASER_TURNRATE
        if sound_state.on:
            rocket_boss_swoosh.play(-1) # Play on loop

    def update(self, ship):
        # Calculate target direction towards the ship
        target_direction = math.atan2(ship.y - self.y, ship.x - self.x)

        # Calculate the difference between current and target direction
        angle_difference = (target_direction - self.direction + math.pi) % (2 * math.pi) - math.pi

        # Gradually adjust the direction
        if abs(angle_difference) > self.turn_speed:
            if angle_difference > 0:
                self.direction += self.turn_speed
            else:
                self.direction -= self.turn_speed
        else:
            self.direction = target_direction

        # Normalize direction to stay within 0 to 2π
        self.direction %= 2 * math.pi

        # Move the boss
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)

        # Wrap around the screen
        self.x %= BASE_WIDTH
        self.y %= BASE_HEIGHT
    
    def draw(self, screen):
        # Define rocket shape
        rocket_length = self.size * 2
        rocket_width = self.size * 0.8
        
        # Calculate rocket points
        cos_angle = math.cos(self.direction)
        sin_angle = math.sin(self.direction)
        
        # Main body (elongated oval shape)
        body_points = []
        for i in range(21):
            angle = math.pi * i / 10
            rx = rocket_length / 2 * math.cos(angle)
            ry = rocket_width / 2 * math.sin(angle)
            x = self.x + rx * cos_angle - ry * sin_angle
            y = self.y + rx * sin_angle + ry * cos_angle
            body_points.append((x, y))
        
        # Nose cone
        nose_tip = (self.x + rocket_length / 2 * cos_angle, self.y + rocket_length / 2 * sin_angle)
        nose_left = (self.x + rocket_length * 0.4 * cos_angle - rocket_width * 0.3 * sin_angle,
                     self.y + rocket_length * 0.4 * sin_angle + rocket_width * 0.3 * cos_angle)
        nose_right = (self.x + rocket_length * 0.4 * cos_angle + rocket_width * 0.3 * sin_angle,
                      self.y + rocket_length * 0.4 * sin_angle - rocket_width * 0.3 * cos_angle)
        
        # Fins (more backward-facing and positioned further back)
        fin_length = rocket_width * 0.6
        fin_width = rocket_width * 0.3
        left_fin = [
            (self.x - rocket_width * 0.4 * sin_angle - rocket_length * 0.4 * cos_angle,
             self.y + rocket_width * 0.4 * cos_angle - rocket_length * 0.4 * sin_angle),
            (self.x - (rocket_width * 0.4 + fin_width) * sin_angle - (rocket_length * 0.4 + fin_length) * cos_angle,
             self.y + (rocket_width * 0.4 + fin_width) * cos_angle - (rocket_length * 0.4 + fin_length) * sin_angle),
            (self.x - rocket_width * 0.4 * sin_angle - rocket_length * 0.2 * cos_angle,
             self.y + rocket_width * 0.4 * cos_angle - rocket_length * 0.2 * sin_angle)
        ]
        right_fin = [
            (self.x + rocket_width * 0.4 * sin_angle - rocket_length * 0.4 * cos_angle,
             self.y - rocket_width * 0.4 * cos_angle - rocket_length * 0.4 * sin_angle),
            (self.x + (rocket_width * 0.4 + fin_width) * sin_angle - (rocket_length * 0.4 + fin_length) * cos_angle,
             self.y - (rocket_width * 0.4 + fin_width) * cos_angle - (rocket_length * 0.4 + fin_length) * sin_angle),
            (self.x + rocket_width * 0.4 * sin_angle - rocket_length * 0.2 * cos_angle,
             self.y - rocket_width * 0.4 * cos_angle - rocket_length * 0.2 * sin_angle)
        ]
        
        # Draw rocket body
        pygame.draw.polygon(screen, (100, 100, 100), body_points)
        
        # Draw nose cone
        pygame.draw.polygon(screen, (130, 130, 130), [nose_tip, nose_left, nose_right])
        
        # Draw fins
        pygame.draw.polygon(screen, (150, 150, 150), left_fin)
        pygame.draw.polygon(screen, (150, 150, 150), right_fin)
        
        # Draw window
        window_center = (self.x + rocket_length * 0.1 * cos_angle, self.y + rocket_length * 0.1 * sin_angle)
        window_radius = rocket_width * 0.25
        pygame.draw.circle(screen, (150, 0, 0), (int(window_center[0]), int(window_center[1])), int(window_radius))
        
        # Draw engine nozzle (rectangular and better connected to the main body)
        nozzle_width = rocket_width * 0.7
        nozzle_height = rocket_length * 0.15
        nozzle_top_left = (self.x - nozzle_width/2 * sin_angle - rocket_length/2 * cos_angle, 
                           self.y + nozzle_width/2 * cos_angle - rocket_length/2 * sin_angle)
        nozzle_top_right = (self.x + nozzle_width/2 * sin_angle - rocket_length/2 * cos_angle, 
                            self.y - nozzle_width/2 * cos_angle - rocket_length/2 * sin_angle)
        nozzle_bottom_left = (nozzle_top_left[0] - nozzle_height * cos_angle, nozzle_top_left[1] - nozzle_height * sin_angle)
        nozzle_bottom_right = (nozzle_top_right[0] - nozzle_height * cos_angle, nozzle_top_right[1] - nozzle_height * sin_angle)
        pygame.draw.polygon(screen, (100, 100, 100), [nozzle_top_left, nozzle_top_right, nozzle_bottom_right, nozzle_bottom_left])
        
        # Draw engine flames
        flame_length = random.randint(int(rocket_length * 0.1), int(rocket_length * 0.2))
        flame_center = ((nozzle_bottom_left[0] + nozzle_bottom_right[0])/2, (nozzle_bottom_left[1] + nozzle_bottom_right[1])/2)
        flame_tip = (flame_center[0] - flame_length * cos_angle, flame_center[1] - flame_length * sin_angle)
        flame_width = nozzle_width * 0.8
        flame_left = (flame_center[0] - flame_width/2 * sin_angle, flame_center[1] + flame_width/2 * cos_angle)
        flame_right = (flame_center[0] + flame_width/2 * sin_angle, flame_center[1] - flame_width/2 * cos_angle)
        pygame.draw.polygon(screen, (255, 100, 0), [nozzle_bottom_left, nozzle_bottom_right, flame_right, flame_tip, flame_left])
        self.draw_health_bar(screen)

class BossAsteroid(Boss):
    def __init__(self):
        super().__init__(BASE_WIDTH // 2, BASE_HEIGHT // 2, 80, BOSSASTEROID_HEALTH)  # Adjust size and health as needed
        self.rotation = 0
        self.rotation_speed = 0.5
        self.shoot_chance = BOSSASTEROID_SHOOT_CHANCE
        self.shape = self.generate_shape()

    def generate_shape(self):
        num_points = 12
        shape = []
        for i in range(num_points):
            angle = i * (2 * math.pi / num_points)
            distance = self.size * random.uniform(0.8, 1.2)
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            shape.append((x, y))
        return shape

    def increase_splinter_rate(self):
        self.shoot_chance += 0.0025 # slight increase per every hit the boss takes

    def update(self, ship, splinters):
        self.rotation += self.rotation_speed
        self.rotation %= 360
        if random.random() < self.shoot_chance:  
            splinters.append(self.shoot_splinter((self.x, self.y), ship))

    def draw(self, screen):
        rotated_shape = [self.rotate_point(p) for p in self.shape]
        points = [(self.x + x, self.y + y) for x, y in rotated_shape]
        pygame.draw.polygon(screen, BLACK, points)
        pygame.draw.polygon(screen, GREY, points, 3)
        self.draw_health_bar(screen)

    def rotate_point(self, point):
        x, y = point
        rad = math.radians(self.rotation)
        cos_rad = math.cos(rad)
        sin_rad = math.sin(rad)
        return (x * cos_rad - y * sin_rad, x * sin_rad + y * cos_rad)

    def shoot_splinter(self, collision_point, ship):
        # Calculate angle towards the ship
        angle = math.atan2(ship.y - collision_point[1], ship.x - collision_point[0])
        # Add random variation (-10 to +10 degrees)
        angle += math.radians(random.uniform(-10, 10))
        return Splinter(collision_point[0], collision_point[1], angle)

class Splinter(GameObject):
    def __init__(self, x, y, angle):
        super().__init__(x, y, 5)
        self.speed = 3
        self.dx = self.speed * math.cos(angle)
        self.dy = self.speed * math.sin(angle)
        self.lifespan = 180  # 3 seconds at 60 FPS
        self.shape = self.generate_shape()

    def generate_shape(self):
        num_points = 6  # Fewer points for a smaller, simpler shape
        shape = []
        for i in range(num_points):
            angle = i * (2 * math.pi / num_points)
            distance = self.size * random.uniform(0.8, 1.2)
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            shape.append((x, y))
        return shape

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifespan -= 1

    def draw(self, screen):
        points = [(self.x + x, self.y + y) for x, y in self.shape]
        pygame.draw.polygon(screen, GREY, points)

class GravityWellBoss(Boss):
    def __init__(self):
        super().__init__(BASE_WIDTH // 2, BASE_HEIGHT // 2, 60, GRAVITYWELLBOSS_HEALTH)  # x, y, size, health
        self.pull_strength = GRAVITYWELLBOSS_PULL_STRENGTH 
        self.pull_radius = GRAVITYWELLBOSS_PULL_RADIUS 
        self.rotation = 0
        self.rotation_speed = 0.5
        self.shape = self.generate_shape()
        self.pulse_timer = 0
        self.pulse_interval = 180  # 3 seconds at 60 FPS
        self.pulse_radius = 0
        self.max_pulse_radius = 100
        self.boss_color = 255
        if sound_state.on:
            gravity_well_rumble.play(-1) # Play on loop

    # New shape
    def generate_shape(self):
        num_arms = 3
        num_spirals = 9
        points_per_arm = 50
        shape = []
        angle_step = 2 * math.pi / points_per_arm
        
        for i in range(points_per_arm):
            angle = i * angle_step
            distance = self.size * (1 + 0.2 * math.sin(num_spirals * angle))
            for arm in range(num_arms):
                arm_angle = arm * (2 * math.pi / num_arms)
                total_angle = angle + arm_angle
                x = distance * math.cos(total_angle)
                y = distance * math.sin(total_angle)
                shape.append((x, y))
        return shape 

    def update(self, ship, asteroids):
        self.rotation += self.rotation_speed
        self.rotation %= 360

        # Update pulse
        self.pulse_timer += 1
        if self.pulse_timer >= self.pulse_interval:
            self.pulse_timer = 0
            self.pulse_radius = self.max_pulse_radius

        if self.pulse_radius > 0:
            self.pulse_radius -= 2  # Shrink the pulse

        # Apply gravitational pull to ship and asteroids
        self.apply_gravity(ship)
        for asteroid in asteroids:
            self.apply_gravity(asteroid)

    def apply_gravity(self, obj):
        dx = self.x - obj.x
        dy = self.y - obj.y
        distance = math.hypot(dx, dy)
        if distance < self.pull_radius:
            force = self.pull_strength * (1 - distance / self.pull_radius)
            angle = math.atan2(dy, dx)
            obj.dx += force * math.cos(angle)
            obj.dy += force * math.sin(angle)

    def draw(self, screen):
        # Draw the boss
        color = self.boss_color * (1 - self.health / self.max_health)
        rotated_shape = [self.rotate_point(p) for p in self.shape]
        points = [(self.x + x, self.y + y) for x, y in rotated_shape]
        pygame.draw.polygon(screen, (color, color, 200), points, 1) # gets brighter as the boss grows more powerful

        # Draw the gravitational field
        pygame.draw.circle(screen, (0, 0, 10), (int(self.x), int(self.y)), self.pull_radius, 1)

        # Draw the pulse
        if self.pulse_radius > 0:
            pygame.draw.circle(screen, (200, 200, 255, 100), (int(self.x), int(self.y)), int(self.pulse_radius), 2)

        # DEBUG: Add a number in the middle to indicate gravitational pull strength
        # font = pygame.font.Font(None, 32)
        # pull_text = font.render(f"{self.pull_strength}", True, WHITE)
        # text_rect = pull_text.get_rect(center=(int(self.x), int(self.y)))
        # screen.blit(pull_text, text_rect)

        self.draw_health_bar(screen)

    def rotate_point(self, point):
        x, y = point
        rad = math.radians(self.rotation)
        cos_rad = math.cos(rad)
        sin_rad = math.sin(rad)
        return (x * cos_rad - y * sin_rad, x * sin_rad + y * cos_rad)

    def hit(self, damage):
        self.health -= damage
        # Increase pull strength as health decreases
        self.pull_strength = 0.1 + (1 - self.health / self.max_health) * 0.2
        return self.health <= 0

# Final boss of the game aka OctoBoss. The boss has several regenerating appendages (7 by default) that the player needs to destroy before being able to hurt and kill the main body. The appendages regenerate after given time. The boss shoots bubbles chasing the player.
class OctoBoss(Boss):
    def __init__(self):
        super().__init__(BASE_WIDTH // 2, BASE_HEIGHT // 2, 80, OCTOBOSS_HEALTH)  # x, y, size, health
        self.num_appendages = OCTOBOSS_APPENDAGE_COUNT
        self.appendages = [Appendage(self, i) for i in range(self.num_appendages)]
        self.all_appendages_disabled = False
        self.vulnerability_pulse = 0
        self.color = WHITE
        self.rotation = 0
        self.rotation_speed = OCTOBOSS_SPEED
        self.move_timer = 0
        self.shoot_timer = 0
        self.bubbles = []
        self.charge_pulse = 0
        self.charge_ball_pos = (0, 0)
        self.charge_ball_angle = 0
        self.charge_ball_distance = self.size + 20
        self.laser_type = 'blue'
        self.laser_charge = 0
        self.laser_direction = 0
        self.laser_sweep = 0
        self.is_firing_laser = False        
        self.craters = self.generate_craters()

    def update(self, ship):
        # Rotate the boss
        self.rotation += self.rotation_speed
        self.rotation %= 360

        # Move the boss
        self.move_timer += 1
        if self.move_timer >= 180:  # Change direction every 3 seconds
            self.move_timer = 0
            self.dx = random.uniform(-1, 1)
            self.dy = random.uniform(-1, 1)

        self.x += self.dx
        self.y += self.dy

        # Keep the boss away from screen edges
        margin = self.size * 1.5
        self.x = max(margin, min(self.x, BASE_WIDTH - margin))
        self.y = max(margin, min(self.y, BASE_HEIGHT - margin))

        # Update appendages
        for appendage in self.appendages:
            appendage.update(self)

        # Shoot bubbles
        self.shoot_timer += 1
        if self.shoot_timer >= OCTOBOSS_BUBBLE_INTERVAL:  # Shoot every 5 seconds
            self.shoot_timer = 0
            if sound_state.on:
                octoboss_bubble_sound.play()
            self.bubbles.append(SoapBubble(self.x, self.y, ship))

        # Update bubbles
        for bubble in self.bubbles[:]:
            bubble.update(ship)
            if bubble.lifespan <= 0:
                self.bubbles.remove(bubble)

        # Increase speed for each destroyed eye
        destroyed_eyes = sum(1 for appendage in self.appendages if not appendage.active)
        self.rotation_speed = OCTOBOSS_SPEED + (destroyed_eyes * OCTOBOSS_SPEED)

        # Check if all appendages are disabled
        if not self.all_appendages_disabled and all(not appendage.active for appendage in self.appendages):
            self.all_appendages_disabled = True
            self.color = (255, 100, 100)  # Change to a reddish color

        # Go berserk if all appendages are dead!
        if self.all_appendages_disabled:
            self.vulnerability_pulse = (self.vulnerability_pulse + 0.1) % (2 * math.pi)
            if not self.is_firing_laser:
                if self.laser_charge == 0:
                    self.laser_type = 'blue' if random.random() < 0.5 else 'red'
                self.laser_charge += 1
                if self.laser_charge < OCTOBOSS_LASER_CHARGE_TIME - 60:  # Stop following 1 second before firing
                    self.charge_ball_angle = math.atan2(ship.y - self.y, ship.x - self.x)
                self.charge_ball_pos = (
                    self.x + math.cos(self.charge_ball_angle) * self.charge_ball_distance,
                    self.y + math.sin(self.charge_ball_angle) * self.charge_ball_distance
                )
                self.charge_pulse = (self.charge_pulse + 0.2) % (2 * math.pi)
                if self.laser_charge >= OCTOBOSS_LASER_CHARGE_TIME:
                    self.is_firing_laser = True
                    self.laser_direction = self.charge_ball_angle
                    self.laser_sweep = 0
            else:
                sweep_direction = 1 if self.laser_type == 'blue' else -1
                self.laser_sweep += OCTOBOSS_LASER_SWEEP_SPEED * sweep_direction
                if abs(self.laser_sweep) >= math.pi / 2:  # 90 degrees in either direction
                    self.is_firing_laser = False
                    self.laser_charge = 0

    def draw(self, screen):
        # Draw the appendages
        for appendage in self.appendages:
            appendage.draw(screen)

        # Draw the main body
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size, 3)

        if self.all_appendages_disabled:
            # Pulse the body
            glow_size = int(self.size * (1 + 0.1 * math.sin(self.vulnerability_pulse)))
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 0, 0, 100), (glow_size, glow_size), glow_size)
            screen.blit(glow_surface, (int(self.x - glow_size), int(self.y - glow_size)))
            if not self.is_firing_laser:
                charge_percent = self.laser_charge / OCTOBOSS_LASER_CHARGE_TIME
                base_radius = 10 * charge_percent
                pulse_radius = base_radius + 2 * math.sin(self.charge_pulse)
                laser_color = (0, 255, 255) if self.laser_type == 'blue' else (255, 0, 0)
                pygame.draw.circle(screen, laser_color,
                                (int(self.charge_ball_pos[0]), int(self.charge_ball_pos[1])), int(pulse_radius))
                pygame.draw.circle(screen, (255, 255, 255),
                                (int(self.charge_ball_pos[0]), int(self.charge_ball_pos[1])), int(base_radius), 1)
            else:
                # Draw laser beam
                laser_end_x = self.x + math.cos(self.laser_direction + self.laser_sweep) * BASE_WIDTH
                laser_end_y = self.y + math.sin(self.laser_direction + self.laser_sweep) * BASE_HEIGHT
                pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (laser_end_x, laser_end_y), 5)

        # Draw craters
        for crater in self.craters:
            rotated_crater = self.rotate_point((crater[0], crater[1]))
            crater_x = int(self.x + rotated_crater[0])
            crater_y = int(self.y + rotated_crater[1])
            pygame.draw.circle(screen, (100, 100, 100), (crater_x, crater_y), int(crater[2]), 2)    

        # Draw the bubbles
        for bubble in self.bubbles:
            bubble.draw(screen)

        if self.is_firing_laser:
            laser_end_x = self.x + math.cos(self.laser_direction + self.laser_sweep) * BASE_WIDTH
            laser_end_y = self.y + math.sin(self.laser_direction + self.laser_sweep) * BASE_HEIGHT
            laser_color = (0, 0, 255) if self.laser_type == 'blue' else (255, 0, 0)
            pygame.draw.line(screen, laser_color, (self.x, self.y), (laser_end_x, laser_end_y), 5)

        self.draw_health_bar(screen)

    def rotate_point(self, point):
        x, y = point
        rad = math.radians(self.rotation)
        cos_rad = math.cos(rad)
        sin_rad = math.sin(rad)
        return (x * cos_rad - y * sin_rad, x * sin_rad + y * cos_rad)

    def hit(self, damage):
        active_appendages = [app for app in self.appendages if app.active]
        if active_appendages:
            # If any appendages are active, damage is not applied to the main body
            return False
        else:
            # All appendages are destroyed, damage the main body
            self.health -= damage
            return self.health <= 0

    def check_laser_collision(self, ship):
        if self.is_firing_laser:
            laser_angle = self.laser_direction + self.laser_sweep
            ship_angle = math.atan2(ship.y - self.y, ship.x - self.x)
            angle_diff = abs(laser_angle - ship_angle) % (2 * math.pi)
            if angle_diff < 0.1:  # Adjust this value to change the hit detection precision
                return True
        return False

    def generate_craters(self):
        craters = []
        for _ in range(3):
            while True:
                size = random.uniform(12, 25)
                x = random.uniform(-0.5, 0.5) * self.size
                y = random.uniform(-0.5, 0.5) * self.size
                if all(math.hypot(x-c[0], y-c[1]) > size + c[2] for c in craters):
                    craters.append((x, y, size))
                    break
        return craters

class Appendage:
    def __init__(self, boss, index):
        self.boss = boss
        self.index = index
        self.length = boss.size * 1.5
        self.angle = (index / boss.num_appendages) * 2 * math.pi
        self.active = True
        self.health = OCTOBOSS_APPENDAGE_HEALTH
        self.max_health = 2
        self.regeneration_time = OCTOBOSS_APPENDAGE_INTERVAL
        self.regeneration_timer = 0
        self.end_x = 0
        self.end_y = 0
        self.eye_position = (0, 0)  # Initialize eye position
        self.blink_timer = 0
        self.blink_interval = random.randint(60, 180)  # 1-3 seconds at 60 FPS
        self.is_blinking = False
        self.blink_duration = 10  # 10 frames for blink        

    def update(self, boss):
        self.angle = ((self.index / self.boss.num_appendages) * 2 * math.pi) + math.radians(self.boss.rotation)
        self.end_x = self.boss.x + math.cos(self.angle) * self.length
        self.end_y = self.boss.y + math.sin(self.angle) * self.length

        # Update eye position to follow the player
        dx = self.boss.target.x - self.end_x
        dy = self.boss.target.y - self.end_y
        angle = math.atan2(dy, dx)
        eye_distance = 5  # Distance from the center of the appendage end
        self.eye_position = (
            self.end_x + math.cos(angle) * eye_distance,
            self.end_y + math.sin(angle) * eye_distance
        )

        if not self.active:
            self.regeneration_timer += 1
            if self.regeneration_timer >= self.regeneration_time:
                self.regenerate()
                # Reset boss to non-berserk mode and disable laser
                boss.all_appendages_disabled = False
                boss.color = WHITE
                boss.is_firing_laser = False
                boss.laser_charge = 0

        # Update blink
        self.blink_timer += 1
        if self.blink_timer >= self.blink_interval:
            self.is_blinking = True
            self.blink_timer = 0
            self.blink_interval = random.randint(60, 180)
        
        if self.is_blinking:
            self.blink_duration -= 1
            if self.blink_duration <= 0:
                self.is_blinking = False
                self.blink_duration = 10

    def draw(self, screen):
        if not self.active:
            return

        start_x, start_y = self.boss.x, self.boss.y
        pygame.draw.line(screen, (100, 100, 100), (start_x, start_y), (self.end_x, self.end_y), 5)
        pygame.draw.circle(screen, (255, 0, 0), (int(self.end_x), int(self.end_y)), 10)

        # Draw the eye
        if not self.is_blinking:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.eye_position[0]), int(self.eye_position[1])), 3)
        else:
            pygame.draw.line(screen, (255, 255, 255), 
                             (int(self.eye_position[0] - 3), int(self.eye_position[1])),
                             (int(self.eye_position[0] + 3), int(self.eye_position[1])), 2)

    def hit(self, damage):
        if not self.active:
            return False
        self.health -= damage
        if self.health <= 0:
            self.disable()
        return True

    def disable(self):
        self.active = False
        self.regeneration_timer = 0

    def regenerate(self):
        self.active = True
        self.health = self.max_health
        self.regeneration_timer = 0

class SoapBubble(GameObject):
    def __init__(self, x, y, target):
        super().__init__(x, y, 10)
        self.speed = OCTOBOSS_BUBBLE_SPEED * 0.7  # Slower than the original bubble
        self.target = target
        self.lifespan = OCTOBOSS_BUBBLE_LIFESPAN
        self.angle = 0
        self.wobble = 0
        self.wobble_speed = random.uniform(0.1, 0.2)

    def update(self, ship):
        self.angle = math.atan2(ship.y - self.y, ship.x - self.x)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.x += self.dx
        self.y += self.dy
        self.lifespan -= 1
        self.wobble += self.wobble_speed

    def draw(self, screen):
        wobble_factor = math.sin(self.wobble) * 2
        pygame.draw.circle(screen, (200, 200, 255, 150), (int(self.x), int(self.y)), int(self.size + wobble_factor), 2)
        pygame.draw.circle(screen, (255, 255, 255, 100), (int(self.x - self.size/3), int(self.y - self.size/3)), 3)