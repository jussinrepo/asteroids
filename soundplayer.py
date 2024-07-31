'''

Separate executable script to test out Asteroids game sounds, from the sound.py file. NOT part of the actual game!

'''

import pygame
import pygame_gui
import importlib
import inspect
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroids Sound Player")

# Set up the GUI manager
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

def mono_to_stereo(mono_sound):
    stereo_sound = np.column_stack((mono_sound, mono_sound))
    return stereo_sound

# Function to dynamically load sound functions from sound.py
def load_sound_functions():
    spec = importlib.util.spec_from_file_location("sound", "sound.py")
    sound_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sound_module)

    sound_functions = {}
    for name, obj in inspect.getmembers(sound_module):
        if inspect.isfunction(obj) and name.startswith("create_"):
            try:
                result = obj()
                if isinstance(result, pygame.mixer.Sound):
                    # If the function already returns a Sound object, use it directly
                    sound_functions[name] = result
                else:
                    # If it's a numpy array, process it
                    if result.ndim == 1:
                        result = mono_to_stereo(result)
                    sound_functions[name] = pygame.sndarray.make_sound(result)
            except Exception as e:
                print(f"Error loading {name}: {e}")

    return sound_functions

# Load sound functions
sound_functions = load_sound_functions()

# Create buttons for each sound function
button_width, button_height = 190, 40
buttons_per_row = 6
margin = 20

for i, (name, sound) in enumerate(sound_functions.items()):
    row = i // buttons_per_row
    col = i % buttons_per_row
    x = margin + col * (button_width + margin)
    y = margin + row * (button_height + margin)

    pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(x, y, button_width, button_height),
        text=name.replace("create_", ""),
        manager=manager
    )

# Main game loop
clock = pygame.time.Clock()
running = True

# Create a list of valid key codes
valid_keys = [pygame.K_a + i for i in range(len(sound_functions))]

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pygame.mixer.stop()  # Stop all sounds when SPACE is pressed
            elif event.key == pygame.K_ESCAPE:
                running = False  # Quit the player
            elif event.key in valid_keys:
                index = valid_keys.index(event.key)
                sound_name = list(sound_functions.keys())[index]
                sound_functions[sound_name].play()

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for name, sound in sound_functions.items():
                if event.ui_element.text == name.replace("create_", ""):
                    sound.play()
                    break

        manager.process_events(event)

    manager.update(time_delta)

    screen.fill((0, 0, 0))
    manager.draw_ui(screen)

    # Draw key bindings
    font = pygame.font.Font(None, 24)
    for i, name in enumerate(sound_functions.keys()):
        key = chr(pygame.K_a + i)
        text = font.render(f"{key}: {name.replace('create_', '')}", True, (255, 255, 255))
        screen.blit(text, (10, SCREEN_HEIGHT - 30 * (len(sound_functions) - i)))

    # Draw SPACE instruction
    space_text = font.render("SPACE: Stop all sounds", True, (255, 255, 255))
    screen.blit(space_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 30))

    pygame.display.flip()

pygame.quit()