import pygame
import numpy as np

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

# Main Theme music, played in the main menu
def create_main_theme():
    duration = 10.0  # 10 seconds loop
    t = np.linspace(0, duration, int(44100 * duration), False)
    
    # Space-themed melody
    melody = (np.sin(2 * np.pi * 220 * t) * 0.3 +
              np.sin(2 * np.pi * 330 * t) * 0.2 +
              np.sin(2 * np.pi * 440 * t) * 0.1)
    
    # Lo-fi drum beat
    beat = np.zeros_like(t)
    beat_pattern = [1, 0, 0.5, 0, 1, 0, 0.5, 0]
    beat_length = len(beat_pattern) * 0.25  # 2 beats per second
    for i, vol in enumerate(beat_pattern):
        beat[int(i * 0.25 * 44100):int((i + 1) * 0.25 * 44100)] = vol
    
    # Combine melody and beat
    theme = melody + beat * 0.5

    melody = np.int16(theme * 16383)
    stereo_melody = np.column_stack((melody, melody))
    return pygame.sndarray.make_sound(stereo_melody)

# Level start melody
def create_level_start_melody():
    duration = 0.2  # 200 milliseconds per note
    samples = int(44100 * duration)
    t = np.linspace(0, duration, samples, False)
    frequencies = [440, 550, 660]  # A4, C#5, E5
    melody = []
    for freq in frequencies:
        waveform = np.sin(2 * np.pi * freq * t) * np.exp(-t * 5)
        melody.extend(waveform)
    melody = np.int16(np.array(melody) * 32767)
    stereo_melody = np.column_stack((melody, melody))
    return pygame.sndarray.make_sound(stereo_melody)

# Level complete sound
def create_level_complete_sound():
    duration = 2.0
    t = np.linspace(0, duration, int(44100 * duration), False)
    wave = np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 550 * t) + np.sin(2 * np.pi * 660 * t)
    wave *= np.exp(-t * 1)
    sound = np.int16(wave * 10922)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Game over melody
def create_game_over_sound():
    duration = 1.5
    t = np.linspace(0, duration, int(44100 * duration), False)
    wave = np.sin(2 * np.pi * 440 * t) * np.exp(-t * 2) + 0.5 * np.sin(2 * np.pi * 220 * t) * np.exp(-t * 1)
    melody = np.int16(wave * 32767)
    stereo_melody = np.column_stack((melody, melody))
    return pygame.sndarray.make_sound(stereo_melody)

# Regular shooting sound
def create_shoot_sound():
    duration = 0.1  # 100 milliseconds
    samples = int(44100 * duration)
    t = np.linspace(0, duration, samples, False)
    frequency = 440  # 440 Hz
    waveform = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 20)
    waveform = np.int16(waveform * 32767)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Triple shot sound - higher tone
def create_tripleshoot_sound():
    duration = 0.1  # 100 milliseconds
    samples = int(44100 * duration)
    t = np.linspace(0, duration, samples, False)
    frequency = 440  # 440 Hz
    waveform = np.sin(2.5 * np.pi * frequency * t) * np.exp(-t * 20)
    waveform = np.int16(waveform * 32767)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Big shot sound - lower tone
def create_bigshoot_sound():
    duration = 0.1  # 100 milliseconds
    samples = int(44100 * duration)
    t = np.linspace(0, duration, samples, False)
    frequency = 440  # 440 Hz
    waveform = np.sin(1.5 * np.pi * frequency * t) * np.exp(-t * 20)
    waveform = np.int16(waveform * 32767)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Generic explosion
def create_explosion_sound():
    duration = 0.5  # 500 milliseconds
    samples = int(44100 * duration)
    t = np.linspace(0, duration, samples, False)
    waveform = np.random.normal(0, 0.5, samples) * np.exp(-t * 5)
    waveform = np.int16(waveform * 32767)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Mine explosion
def create_mine_explosion_sound():
    duration = 0.8  # 800 milliseconds
    samples = int(44100 * duration)
    t = np.linspace(0, duration, samples, False)
    waveform = np.random.normal(0, 2, samples) * np.exp(-t * 4.5)
    waveform = np.int16(waveform * 32767)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Powerup created
def create_powerup_sound():
    sweep = np.linspace(300, 1200, 4410)
    wave = np.sin(2 * np.pi * sweep * np.linspace(0, 0.1, 4410))
    melody = np.int16(wave * 32767)
    stereo_melody = np.column_stack((melody, melody))
    return pygame.sndarray.make_sound(stereo_melody)

# Shield being hit by asteroids, ufo bullets, shrapnels or bubbles
def create_shield_hit_sound():
    duration = 0.2
    t = np.linspace(0, duration, int(44100 * duration), False)
    wave = np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 20)
    sound = np.int16(wave * 32767)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Ufo spawn sound
def create_ufo_sound():
    duration = 0.5
    t = np.linspace(0, duration, int(44100 * duration), False)
    wave = np.sin(2 * np.pi * 80 * t) + 0.5 * np.sin(2 * np.pi * 160 * t)
    sound = np.int16(wave * 16383)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Boss appearing
def create_boss_appear_sound():
    duration = 1.0
    t = np.linspace(0, duration, int(44100 * duration), False)
    wave = np.sin(2 * np.pi * 100 * t) * np.exp(-t * 2) + 0.5 * np.sin(2 * np.pi * 200 * t) * np.exp(-t * 1)
    sound = np.int16(wave * 32767)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Asteroid being shot sound
def create_asteroid_hit_sound():
    duration = 0.1
    t = np.linspace(0, duration, int(44100 * duration), False)
    wave = np.random.normal(0, 0.3, int(44100 * duration)) * np.exp(-t * 30)
    sound = np.int16(wave * 32767)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Comet rumbling on screen sound
def create_comet_rumble():
    duration = 2.0
    t = np.linspace(0, duration, int(44100 * duration), False)
    rumble = np.random.normal(0, 0.5, int(44100 * duration)) * np.sin(2 * np.pi * 30 * t)
    sound = np.int16(rumble * 16383)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Magnetic Mine beep
def create_magnetic_mine_beep():
    duration = 0.05  # 50 milliseconds
    samples = int(44100 * duration)
    t = np.linspace(0, duration, samples, False)
    beep = np.sin(2 * np.pi * 880 * t) * np.exp(-t * 10)
    beep = np.int16(beep * 32767)
    stereo_sound = np.column_stack((beep, beep))
    return pygame.sndarray.make_sound(stereo_sound)

# OctoBoss bubble shoot sound
def create_octoboss_bubble():
    duration = 1.0
    t = np.linspace(0, duration, int(44100 * duration), False)
    bubble = np.sin(2 * np.pi * np.exp(t * 5) * t) * np.exp(-t * 5)
    sound = np.int16(bubble * 16383)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Create the sounds
main_theme = create_main_theme()
level_start_sound = create_level_start_melody()
level_complete_sound = create_level_complete_sound()
game_over_sound = create_game_over_sound()
player_shoot_sound = create_shoot_sound()
player_tripleshoot_sound = create_tripleshoot_sound()
player_bigshoot_sound = create_bigshoot_sound()
explosion_sound = create_explosion_sound()
ship_crash_sound = create_explosion_sound()
powerup_sound = create_powerup_sound()
shield_hit_sound = create_shield_hit_sound()
ufo_sound = create_ufo_sound()
boss_appear_sound = create_boss_appear_sound()
asteroid_hit_sound = create_asteroid_hit_sound()
comet_rumble = create_comet_rumble()
magnetic_mine_beep = create_magnetic_mine_beep()
mine_explosion_sound = create_mine_explosion_sound()
octoboss_bubble_sound = create_octoboss_bubble()

# NOT YET ADDED - fix to stereo before applying
'''
def sine_wave(frequency, duration, volume=0.5):
    t = np.linspace(0, duration, int(44100 * duration), False)
    wave = np.sin(2 * np.pi * frequency * t) * volume
    return np.int16(wave * 32767)

def create_gravity_well_rumble():
    duration = 3.0
    t = np.linspace(0, duration, int(44100 * duration), False)
    rumble = np.sin(2 * np.pi * 40 * t) + 0.5 * np.sin(2 * np.pi * 80 * t)
    rumble *= np.random.normal(1, 0.1, int(44100 * duration))
    return pygame.sndarray.make_sound(np.int16(rumble * 16383))

def create_boss_asteroid_shrapnel():
    duration = 0.5
    t = np.linspace(0, duration, int(44100 * duration), False)
    shrapnel = np.random.normal(0, 0.5, int(44100 * duration)) * np.exp(-t * 10)
    shrapnel += np.sin(2 * np.pi * 440 * t) * np.exp(-t * 20)
    return pygame.sndarray.make_sound(np.int16(shrapnel * 16383))

def create_rocket_boss_swoosh():
    duration = 1.0
    t = np.linspace(0, duration, int(44100 * duration), False)
    swoosh = np.sin(2 * np.pi * np.linspace(1000, 100, int(44100 * duration)) * t)
    swoosh *= np.exp(-t * 3)
    return pygame.sndarray.make_sound(np.int16(swoosh * 16383))

'''