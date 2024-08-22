import pygame
import random
import numpy as np

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

# Define note frequencies
notes = {
    'C2': 65.41, 'C#2': 69.30, 'D2': 73.42, 'D#2': 77.78, 'E2': 82.41, 'F2': 87.31, 'F#2': 92.50, 'G2': 98.00, 'G#2': 103.83, 'A2': 110.00, 'A#2': 116.54, 'B2': 123.47,
    'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56, 'E3': 164.81, 'F3': 174.61, 'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00, 'A#3': 233.08, 'B3': 246.94,
    'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
    'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25, 'E5': 659.25, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77,
    'C6': 1046.50
}

# Function where all the songs are generated
def create_melody(melody_sequence, bass_sequence, tempo):
    sample_rate = 44100
    beat_duration = 60 / tempo
    
    melody_duration = sum(length for _, length in melody_sequence)
    bass_duration = sum(length for _, length in bass_sequence)
    total_duration = max(melody_duration, bass_duration) # whichever is longer

    t = np.linspace(0, total_duration * beat_duration, int(sample_rate * total_duration * beat_duration), False)
    
    melody = np.zeros_like(t)
    bass = np.zeros_like(t)
    
    def add_note(sequence, output):
        current_time = 0
        for note, length in sequence:
            if note != 'R':  # 'R' represents a rest
                freq = notes[note]
                end_time = current_time + length * beat_duration
                output[(t >= current_time) & (t < end_time)] += np.sin(2 * np.pi * freq * (t[(t >= current_time) & (t < end_time)] - current_time))
            current_time += length * beat_duration
    
    add_note(melody_sequence, melody)
    add_note(bass_sequence, bass)
    
    return melody + 0.5 * bass  # Combine melody and bass

# Main Theme music, played in the main menu
def create_main_theme(volume=0.4):
    tempo = 120  # beats per minute
    
    melody_sequence = [
        ('C4', 1), ('E4', 1), ('G4', 1), ('R', 1),
        ('C4', 1), ('G4', 1), ('E4', 1), ('R', 1),
        ('F4', 1), ('A4', 1), ('C4', 1), ('R', 1),
        ('G4', 1), ('E4', 1), ('C4', 1), ('R', 1)
    ]
    
    bass_sequence = [
        ('C3', 2), ('R', 2), ('G3', 2), ('R', 2),
        ('F3', 2), ('R', 2), ('C3', 2), ('R', 2)
    ]
    
    theme = create_melody(melody_sequence, bass_sequence, tempo)
    theme = np.int16(theme * 32767 * volume)
    stereo_theme = np.column_stack((theme, theme))
    return pygame.sndarray.make_sound(stereo_theme)


# Alternavite melodies
# Upbeat Space Adventure
def create_main_theme_2(volume=0.4):
    tempo = 140
    
    melody_sequence = [
        ('C4', 1), ('E4', 1), ('G4', 1), ('C5', 1),
        ('B4', 1), ('G4', 1), ('E4', 1), ('C4', 1),
        ('F4', 1), ('A4', 1), ('C5', 1), ('F5', 1),
        ('E5', 1), ('C5', 1), ('A4', 1), ('F4', 1)
    ]
    
    bass_sequence = [
        ('C3', 2), ('G3', 2), ('F3', 2), ('C3', 2),
        ('A3', 2), ('F3', 2), ('G3', 2), ('C3', 2)
    ]

    theme = create_melody(melody_sequence, bass_sequence, tempo)
    theme = np.int16(theme * 32767 * volume)
    stereo_theme = np.column_stack((theme, theme))
    return pygame.sndarray.make_sound(stereo_theme)

# Mysterious Space Exploration
def create_main_theme_3(volume=0.4):
    tempo = 100
    
    melody_sequence = [
        ('E4', 1.5), ('G4', 0.5), ('A4', 1.5), ('B4', 0.5),
        ('C5', 2), ('R', 1), ('D5', 1),
        ('B4', 1.5), ('G4', 0.5), ('A4', 1.5), ('F#4', 0.5),
        ('E4', 2), ('R', 2)
    ]
    
    bass_sequence = [
        ('E3', 3), ('A3', 3), ('C3', 2), 
        ('G3', 3), ('D3', 3), ('E3', 2)
    ]

    theme = create_melody(melody_sequence, bass_sequence, tempo)
    theme = np.int16(theme * 32767 * volume)
    stereo_theme = np.column_stack((theme, theme))
    return pygame.sndarray.make_sound(stereo_theme)

# Epic Space Battle
def create_main_theme_4(volume=0.4):
    tempo = 160
    
    melody_sequence = [
        ('C4', 0.5), ('C4', 0.5), ('G4', 1), ('F4', 0.5), ('E4', 0.5), ('D4', 1),
        ('C4', 0.5), ('C4', 0.5), ('A4', 1), ('G4', 0.5), ('F4', 0.5), ('E4', 1),
        ('D4', 0.5), ('D4', 0.5), ('B4', 1), ('A4', 0.5), ('G4', 0.5), ('F4', 1),
        ('E4', 0.5), ('E4', 0.5), ('C5', 1), ('B4', 0.5), ('A4', 0.5), ('G4', 1)
    ]
    
    bass_sequence = [
        ('C3', 2), ('F3', 2), ('G3', 2), ('C3', 2),
        ('A2', 2), ('D3', 2), ('G3', 2), ('C3', 2)
    ]

    theme = create_melody(melody_sequence, bass_sequence, tempo)
    theme = np.int16(theme * 32767 * volume)
    stereo_theme = np.column_stack((theme, theme))
    return pygame.sndarray.make_sound(stereo_theme)

# Unfinished Song
def create_unfinished_song(volume=0.4):
    tempo = 90
    
    melody_sequence = [('C5', 0.25), ('R', 0.25), ('C5', 0.25), ('R', 0.25), ('G5', 0.25), ('R', 0.25), ('G5', 0.25), ('R', 0.25), ('A5', 0.25), ('R', 0.25), ('A5', 0.25), ('R', 0.25), ('G5', 0.75), ('R', 0.75), ('F5', 0.25), ('R', 0.25), ('F5', 0.25), ('R', 0.25), ('E5', 0.25), ('R', 0.25), ('E5', 0.25), ('R', 0.25), ('D5', 0.25), ('R', 0.25), ('D5', 0.25), ('R', 0.25), ('C5', 0.5), ('R', 0.75), ('G5', 0.25), ('R', 0.25), ('G5', 0.25), ('R', 0.25), ('F5', 0.25), ('R', 0.25), ('F5', 0.25), ('R', 0.25), ('E5', 0.25), ('R', 0.25), ('E5', 0.25), ('R', 0.25), ('D5', 0.75), ('R', 0.75), ('G5', 0.25), ('R', 0.25), ('G5', 0.25), ('R', 0.25), ('F5', 0.25), ('R', 0.25), ('F5', 0.25), ('R', 0.25), ('E5', 0.25), ('R', 0.25), ('E5', 0.25), ('R', 0.25), ('D5', 0.75), ('R', 0.5), ('C5', 0.25), ('R', 0.25), ('C5', 0.25), ('R', 0.25), ('G5', 0.25), ('R', 0.5), ('G5', 0.25), ('R', 0.5), ('A5', 0.25), ('R', 0.25), ('C6', 0.25), ('R', 0.25), ('A5', 0.25), ('R', 0.25), ('G5', 0.75), ('R', 0.5), ('F5', 0.5), ('R', 0.25), ('F5', 0.25), ('R', 0.5), ('E5', 0.25), ('R', 0.25), ('E5', 0.25), ('R', 0.25), ('E5', 0.25), ('R', 0.5), ('D5', 0.25), ('R', 0.25), ('D5', 0.25), ('R', 0.25), ('E5', 0.25), ('R', 0.25), ('D5', 0.25), ('R', 0.25), ('C5', 0.75), ('R', 0.75), ('C6', 0.5)]

    theme = create_melody(melody_sequence, [], tempo)
    theme = np.int16(theme * 32767 * volume)
    stereo_theme = np.column_stack((theme, theme))
    return pygame.sndarray.make_sound(stereo_theme)

# Level start melody
def create_level_start_melody(volume=0.5):
    tempo = 160
    
    melody_sequence = [
        ('A4', 0.5), ('C#5', 0.5), ('E5', 0.5)
    ]
    
    melody = create_melody(melody_sequence, [], tempo)
    melody *= np.exp(-np.linspace(0, len(melody)/44100, len(melody)) * 3)  # Apply decay
    melody = np.int16(melody * 32767 * volume)
    stereo_melody = np.column_stack((melody, melody))
    return pygame.sndarray.make_sound(stereo_melody)

# Level complete melody
def create_level_complete_melody(volume=0.5):
    tempo = 180
    
    melody_sequence = [
        ('C5', 0.25), ('R', 0.5), ('C5', 0.25), ('G5', 0.75)
    ]
    
    melody = create_melody(melody_sequence, [], tempo)
    melody *= np.exp(-np.linspace(0, len(melody)/44100, len(melody)) * 2)  # Apply decay
    melody = np.int16(melody * 32767 * volume)
    stereo_melody = np.column_stack((melody, melody))
    return pygame.sndarray.make_sound(stereo_melody)

# Game over melody
def create_game_over_melody(volume=0.5):
    tempo = 120
    
    melody_sequence = [
        ('G4', 1), ('F4', 1), ('E4', 1), ('D4', 1)
    ]
    
    melody = create_melody(melody_sequence, [], tempo)
    melody *= np.exp(-np.linspace(0, len(melody)/44100, len(melody)) * 2)  # Apply decay
    melody = np.int16(melody * 32767 * volume)
    stereo_melody = np.column_stack((melody, melody))
    return pygame.sndarray.make_sound(stereo_melody)

# Boss appearing melody
def create_boss_appear_melody(volume=0.5):
    tempo = 120
    
    melody_sequence = [
        ('C3', 1), ('A#2', 1), ('G2', 1), ('F2', 1)
    ]
    
    melody = create_melody(melody_sequence, [], tempo)
    melody *= np.exp(-np.linspace(0, len(melody)/44100, len(melody)) * 1)  # Apply decay
    melody = np.int16(melody * 32767 * volume)
    stereo_melody = np.column_stack((melody, melody))
    return pygame.sndarray.make_sound(stereo_melody)

# Regular shooting sound
def create_shoot_sound(volume=0.5):
    duration = 0.1
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    frequency = 440
    waveform = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 20)
    waveform = np.int16(waveform * 32767 * volume)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Triple shot sound - higher tone
def create_tripleshoot_sound(volume=0.5):
    duration = 0.1
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    frequency = 440
    waveform = np.sin(2.5 * np.pi * frequency * t) * np.exp(-t * 20)
    waveform = np.int16(waveform * 32767 * volume)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Big shot sound - lower tone
def create_bigshoot_sound(volume=0.5):
    duration = 0.1
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    frequency = 440
    waveform = np.sin(1.5 * np.pi * frequency * t) * np.exp(-t * 20)
    waveform = np.int16(waveform * 32767 * volume)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Generic explosion
def create_explosion_sound(volume=0.5):
    duration = 0.5
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    waveform = np.random.normal(0, 0.5, int(sample_rate * duration)) * np.exp(-t * 5)
    waveform = np.int16(waveform * 32767 * volume)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Mine explosion
def create_mine_explosion_sound(volume=0.5):
    duration = 0.8
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    waveform = np.random.normal(0, 1, int(sample_rate * duration)) * np.exp(-t * 4)
    waveform += 0.5 * np.sin(2 * np.pi * 100 * t) * np.exp(-t * 3)  # Add low frequency rumble
    waveform = np.int16(waveform * 32767 * volume)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Boss explosion
def create_boss_explosion_sound(volume=0.5):
    duration = 2
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    waveform = np.random.normal(0, 1, int(sample_rate * duration)) * np.exp(-t * 2)
    waveform += np.sin(2 * np.pi * 50 * t) * np.exp(-t * 1)  # Add very low frequency rumble
    waveform = np.int16(waveform * 32767 * volume)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Powerup created
def create_powerup_sound(volume=0.5):
    duration = 0.1
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sweep = np.geomspace(400, 1000, int(sample_rate * duration))
    waveform = np.sin(2 * np.pi * sweep * t) * (1 - t / duration)
    waveform = np.int16(waveform * 32767 * volume)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Shield being hit by asteroids, ufo bullets, shrapnels or bubbles
def create_shield_hit_sound(volume=0.5):
    duration = 0.2
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 20)
    sound = np.int16(wave * 32767 * volume)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Ufo flying sound
def create_ufo_sound(volume=0.5):
    duration = 0.5
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * 80 * t) + 0.5 * np.sin(2 * np.pi * 160 * t)
    sound = np.int16(wave * 16383 * volume)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Asteroid being shot sound
def create_asteroid_hit_sound(volume=0.5):
    duration = 0.1
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.random.normal(0, 0.3, int(sample_rate * duration)) * np.exp(-t * 30)
    sound = np.int16(wave * 32767 * volume)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Comet rumbling on screen sound
def create_comet_rumble(volume=0.3):
    duration = 2.0
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    rumble = np.random.normal(0, 0.5, int(sample_rate * duration)) * np.sin(2 * np.pi * 20 * t)
    sound = np.int16(rumble * 16383 * volume)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Magnetic Mine beep
def create_magnetic_mine_beep(volume=0.5):
    duration = 0.05
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    beep = np.sin(2 * np.pi * 880 * t) * np.exp(-t * 10)
    beep = np.int16(beep * 32767 * volume)
    stereo_sound = np.column_stack((beep, beep))
    return pygame.sndarray.make_sound(stereo_sound)

# OctoBoss bubble shoot sound
def create_octoboss_bubble(volume=0.5):
    duration = 0.12
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sweep = np.geomspace(400, 1000, int(sample_rate * duration))
    waveform = np.sin(1.3 * np.pi * sweep * t) * (1 - t / duration)
    waveform = np.int16(waveform * 32767 * volume)
    stereo_waveform = np.column_stack((waveform, waveform))
    return pygame.sndarray.make_sound(stereo_waveform)

# Gravity Well Boss sound
def create_gravity_well_rumble(volume=0.5):
    duration = 3.0
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    rumble = np.sin(2 * np.pi * 30 * t) + 0.5 * np.sin(2 * np.pi * 60 * t)
    rumble *= np.random.normal(1, 0.1, int(sample_rate * duration))
    sound = np.int16(rumble * 16383 * volume)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Asteroid Boss Shrapnel shooting sound
def create_boss_asteroid_shrapnel():
    duration = 0.5
    t = np.linspace(0, duration, int(44100 * duration), False)
    shrapnel = np.random.normal(0, 0.5, int(44100 * duration)) * np.exp(-t * 10)
    shrapnel += np.sin(2 * np.pi * 440 * t) * np.exp(-t * 20)
    sound = np.int16(shrapnel * 16383)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Rocket Chaser Boss swoosh sound 
def create_rocket_boss_swoosh():
    duration = 1.0
    t = np.linspace(0, duration, int(44100 * duration), False)
    swoosh = np.sin(2 * np.pi * np.linspace(1000, 100, int(44100 * duration)) * t)
    swoosh *= np.exp(-t * 3)
    sound = np.int16(swoosh * 16383)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Create the melodies
main_theme = create_main_theme()
main_theme_2 = create_main_theme_2()
main_theme_3 = create_main_theme_3()
main_theme_4 = create_main_theme_4()
unfinished_song = create_unfinished_song()
level_start_sound = create_level_start_melody()
level_complete_sound = create_level_complete_melody()
game_over_sound = create_game_over_melody()
boss_appear_sound = create_boss_appear_melody()

# Create the sfx
player_shoot_sound = create_shoot_sound()
player_tripleshoot_sound = create_tripleshoot_sound()
player_bigshoot_sound = create_bigshoot_sound()
explosion_sound = create_explosion_sound()
ship_crash_sound = create_explosion_sound()
powerup_sound = create_powerup_sound()
shield_hit_sound = create_shield_hit_sound()
ufo_sound = create_ufo_sound()
asteroid_hit_sound = create_asteroid_hit_sound()
comet_rumble = create_comet_rumble()
magnetic_mine_beep = create_magnetic_mine_beep()
mine_explosion_sound = create_mine_explosion_sound()
octoboss_bubble_sound = create_octoboss_bubble()
gravity_well_rumble = create_gravity_well_rumble()
boss_asteroid_shrapnel = create_boss_asteroid_shrapnel()
boss_explosion_sound = create_boss_explosion_sound()
rocket_boss_swoosh = create_rocket_boss_swoosh()
