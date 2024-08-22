'''

Separate executable script to compose music for Asteroids game. Able to generate a melody that you can copy-paste into the game sound.py easily.

'''

import pygame
import pygame_gui
import numpy as np
import time
import threading

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Magnificient Music Maker")

manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# Define font for the note being played
font_size = 72
font = pygame.font.SysFont(None, font_size)
text_color = (76, 80, 82) # Dark grey color
current_note_text = ""

# Function to render text
def render_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

# Define musical notes and their frequencies: A=440
notes = {
    'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13, 'E': 329.63, 'F': 349.23,
    'F#': 369.99, 'G': 392.00, 'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
}

# Map keyboard keys to musical notes
key_mapping = {
    pygame.K_z: ('C', 0), pygame.K_s: ('C#', 0), pygame.K_x: ('D', 0), pygame.K_d: ('D#', 0),
    pygame.K_c: ('E', 0), pygame.K_v: ('F', 0), pygame.K_g: ('F#', 0), pygame.K_b: ('G', 0),
    pygame.K_h: ('G#', 0), pygame.K_n: ('A', 0), pygame.K_j: ('A#', 0), pygame.K_m: ('B', 0),
    pygame.K_COMMA: ('C', 1),
    pygame.K_q: ('C', 1), pygame.K_2: ('C#', 1), pygame.K_w: ('D', 1), pygame.K_3: ('D#', 1),
    pygame.K_e: ('E', 1), pygame.K_r: ('F', 1), pygame.K_5: ('F#', 1), pygame.K_t: ('G', 1),
    pygame.K_6: ('G#', 1), pygame.K_y: ('A', 1), pygame.K_7: ('A#', 1), pygame.K_u: ('B', 1),
    pygame.K_i: ('C', 2)
}

# Create UI elements
pygame_gui.elements.UIButton(relative_rect=pygame.Rect(50, 50, 100, 50), text='RECORD', manager=manager)
pygame_gui.elements.UIButton(relative_rect=pygame.Rect(200, 50, 100, 50), text='STOP', manager=manager)
pygame_gui.elements.UIButton(relative_rect=pygame.Rect(350, 50, 100, 50), text='SAVE FILE', manager=manager)
pygame_gui.elements.UIButton(relative_rect=pygame.Rect(500, 50, 100, 50), text='PLAY', manager=manager)
octave_up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(650, 50, 100, 50), text='Octave +', manager=manager)
octave_down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(800, 50, 100, 50), text='Octave -', manager=manager)
octave_range_box = pygame_gui.elements.UITextBox("C3-C5", relative_rect=pygame.Rect(950, 50, 200, 50), manager=manager)
output_box = pygame_gui.elements.UITextBox("", relative_rect=pygame.Rect(800, 150, 750, 200), manager=manager)

# Define piano key dimensions and positions
white_key_width, white_key_height = 40, 200
black_key_width, black_key_height = 30, 120
start_x, start_y = 50, 300

white_keys = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
black_keys = ['C#', 'D#', 'F#', 'G#', 'A#']

# Create virtual piano keys
piano_keys = {}
for octave in range(2):
    for i, key in enumerate(white_keys):
        x = start_x + (i + octave * 7) * white_key_width
        piano_keys[f'{key}{octave+3}'] = pygame.Rect(x, start_y, white_key_width, white_key_height)

    for i, key in enumerate(black_keys):
        x = start_x + (i * white_key_width + white_key_width // 2) + octave * 7 * white_key_width
        if i > 1:
            x += white_key_width
        piano_keys[f'{key}{octave+3}'] = pygame.Rect(x, start_y, black_key_width, black_key_height)

# Add the final C key
piano_keys['C5'] = pygame.Rect(start_x + 14 * white_key_width, start_y, white_key_width, white_key_height)

recording = False
playing = False
recorded_notes = []
start_time = 0
current_note = None
note_start_time = 0
base_octave = 3
active_keys = set()

def play_recorded_notes():
    global playing, current_note_text
    for note, duration in recorded_notes:
        if not playing:
            break
        if note != "R":
            sounds[note].play()
            current_note_text = note
        time.sleep(duration)
        if note != "R":
            sounds[note].stop()
    playing = False
    current_note_text = ""

def play_note(note):
    """Generate and return a pygame Sound object for a given note"""
    frequency = notes[note[:-1]] * (2 ** (int(note[-1]) - 4))
    sample_rate = 44100
    t = np.linspace(0, 1, sample_rate, False)
    wave = np.sin(2 * np.pi * frequency * t)
    sound = np.int16(wave * 32767)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

def quantize_time(t):
    """Quantize time to the nearest eighth note, ensuring a minimum duration"""
    beat_duration = 60 / 120  # Assuming 120 BPM
    eighth_note = beat_duration / 2
    return max(round(t / eighth_note) * eighth_note, eighth_note)

# Generate sounds for all notes
sounds = {f"{note}{octave}": play_note(f"{note}{octave}") for note in notes for octave in range(8)}
active_sounds = {}

clock = pygame.time.Clock()
running = True
last_note_end_time = 0

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                recording = not recording
                if recording:
                    start_time = time.time()
                    recorded_notes = []
                    last_note_end_time = 0
                    output_box.html_text = "Recording started..."
                    output_box.rebuild()
                else:
                    output_box.html_text = f"Recorded notes: {recorded_notes}"
                    output_box.rebuild()
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                base_octave = min(base_octave + 1, 6)
                octave_range_box.html_text = f"C{base_octave}-C{base_octave+2}"
                octave_range_box.rebuild()
            elif event.key == pygame.K_MINUS:
                base_octave = max(base_octave - 1, 0)
                octave_range_box.html_text = f"C{base_octave}-C{base_octave+2}"
                octave_range_box.rebuild()
            elif event.key in key_mapping:
                note_name, octave_offset = key_mapping[event.key]
                octave = base_octave + octave_offset
                note = f"{note_name}{octave}"
                sounds[note].play(-1)
                active_sounds[event.key] = sounds[note]
                active_keys.add(event.key)
                if recording:
                    current_time = time.time() - start_time
                    if current_time - last_note_end_time > 0.1:  # Add rest if pause is significant
                        rest_duration = quantize_time(current_time - last_note_end_time)
                        recorded_notes.append(("R", rest_duration))
                    current_note = note
                    note_start_time = current_time
                current_note_text = note

        if event.type == pygame.KEYUP:
            if event.key in key_mapping:
                if event.key in active_sounds:
                    active_sounds[event.key].stop()
                    del active_sounds[event.key]
                active_keys.remove(event.key)
                if recording and current_note:
                    duration = quantize_time(time.time() - start_time - note_start_time)
                    recorded_notes.append((current_note, duration))
                    current_note = None
                    last_note_end_time = time.time() - start_time
                if not active_keys:
                    current_note_text = ""

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == 'RECORD':
                recording = True
                start_time = time.time()
                recorded_notes = []
                last_note_end_time = 0
                output_box.html_text = "Recording started..."
                output_box.rebuild()
            elif event.ui_element.text == 'STOP':
                recording = False
                playing = False
                output_box.html_text = f"Recorded notes: {recorded_notes}"
                output_box.rebuild()
                for sound in active_sounds.values():
                    sound.stop()
                active_sounds.clear()
                active_keys.clear()
                current_note_text = ""
            elif event.ui_element.text == 'SAVE FILE':
                with open('recorded_melody.txt', 'w') as f:
                    f.write(str(recorded_notes))
                output_box.html_text += "<br>Melody saved to file."
                output_box.rebuild()
            elif event.ui_element.text == 'PLAY':
                if recorded_notes and not playing:
                    playing = True
                    threading.Thread(target=play_recorded_notes, daemon=True).start()
            elif event.ui_element == octave_up_button:
                base_octave = min(base_octave + 1, 6)
                octave_range_box.html_text = f"C{base_octave}-C{base_octave+2}"
                octave_range_box.rebuild()
            elif event.ui_element == octave_down_button:
                base_octave = max(base_octave - 1, 0)
                octave_range_box.html_text = f"C{base_octave}-C{base_octave+2}"
                octave_range_box.rebuild()

        manager.process_events(event)

    manager.update(time_delta)

    screen.fill((200, 200, 200))
    manager.draw_ui(screen)

    # Render the current note text
    render_text(current_note_text, font, text_color, screen, 300, 180)

    # Draw piano keys and highlight active keys
    for note, rect in piano_keys.items():
        color = (0, 0, 0) if '#' in note else (255, 255, 255)
        note_name, note_octave = note[:-1], int(note[-1])
        if any(key for key in active_keys if key_mapping[key][0] == note_name and key_mapping[key][1] == note_octave - base_octave):
            color = (255, 0, 0) if '#' in note else (255, 200, 200)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)

    pygame.display.update()
    pygame.display.flip()

pygame.quit()