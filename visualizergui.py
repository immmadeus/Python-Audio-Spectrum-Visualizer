import sys
import os
import pygame
import datetime

pygame.init()
now = datetime.datetime.now()

pygame.display.set_caption("Audio Spectrum Visualizer - Settings")

# Function to handle file paths correctly when running as an executable
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

# Load icon with safe path handling
icon_path = resource_path("icon-1628258_1280.ico")
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)

# Constants and initial settings
FONT = pygame.font.SysFont('franklingothicmedium', 20, False, True)
WIDTH, HEIGHT = 1024, 240
WHITE = (255, 255, 255)
GREEN = (50, 150, 50)
BLACK = (0, 0, 0)
start_text = FONT.render("Click here or Press Enter to Start!", True, WHITE)
version_number = FONT.render("v1.0", True, WHITE)
time_stamp = "%a, %b %d, %Y  %I:%M %p"

# UI Element positions and default values
text_boxes = {
    "threshold": pygame.Rect(250, 10, 110, 30),
    "min_bar_height": pygame.Rect(250, 40, 110, 30),
    "smoothing_factor": pygame.Rect(250, 70, 110, 30),
    "fps": pygame.Rect(250, 100, 110, 30),
    "start_color": pygame.Rect(250, 130, 110, 30),
    "end_color": pygame.Rect(250, 160, 110, 30),
}

user_input = {
    "threshold": "2.5",
    "min_bar_height": "5",
    "smoothing_factor": "0.15",
    "fps": "60",
    "start_color": "255,0,0",
    "end_color": "0,0,255",
}

active_box = None
cursor_pos = {key: len(user_input[key]) for key in text_boxes}
start_button = pygame.Rect(WIDTH//2, HEIGHT//2, 325, 50)

# Draw UI elements
def draw_ui(screen):
    screen.fill(BLACK)
    current_time = FONT.render(now.strftime(time_stamp), True, WHITE)

    labels = {
        "threshold": "Minimum Threshold %:",
        "min_bar_height": "Min Bar Height in pixels:",
        "smoothing_factor": "Smoothing Factor (0 to 1):",
        "fps": "FPS:",
        "start_color": "Start Color (R,G,B):",
        "end_color": "End Color (R,G,B):",
    }

    for key, rect in text_boxes.items():
        draw_textbox(screen, key, rect, labels[key])

    # Draw Start Button
    pygame.draw.rect(screen, GREEN, start_button)
    screen.blit(start_text, (start_button.x + 25, start_button.y + 10))

    # Draw version and current time
    screen.blit(version_number, (WIDTH - 110, HEIGHT - 25))
    screen.blit(current_time, (WIDTH - len(time_stamp)*11, 0))

    pygame.display.flip()

def draw_textbox(screen, key, rect, label):
    """Draw a labeled textbox with text input."""
    label_surface = FONT.render(label, True, WHITE)
    screen.blit(label_surface, (10, rect.y + 3))
    pygame.draw.rect(screen, WHITE, rect, 2)

    text_surface = FONT.render(user_input[key], True, WHITE)
    screen.blit(text_surface, (rect.x + 5, rect.y + 3))

    if key == active_box:
        draw_cursor(screen, rect, key)

def draw_cursor(screen, rect, key):
    """Draw blinking cursor in active textbox."""
    time_elapsed = pygame.time.get_ticks() // 500
    if time_elapsed % 2 == 0:
        cursor_x = rect.x + 5 + FONT.size(user_input[key][:cursor_pos[key]])[0]
        pygame.draw.line(screen, WHITE, (cursor_x, rect.y + 5), (cursor_x, rect.y + 20), 2)

# Handle UI events
def handle_ui_events():
    global active_box
    start_program = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            start_program = handle_mouse_click(event)
        elif event.type == pygame.KEYDOWN:
            if not active_box:
                start_program = handle_key_no_focus(event)
            else:
                handle_key_with_focus(event)

    return get_validated_inputs() + (start_program,)

def handle_mouse_click(event):
    global active_box
    if start_button.collidepoint(event.pos):
        return True

    for key, rect in text_boxes.items():
        if rect.collidepoint(event.pos):
            active_box = key
            cursor_pos[key] = len(user_input[key])
            return False

    active_box = None
    return False

def handle_key_no_focus(event):
    return event.key in {pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_KP_ENTER, pygame.K_SPACE}

def handle_key_with_focus(event):
    global active_box
    key = active_box
    if key is None or key not in user_input:
        return

    text = user_input[key]
    pos = cursor_pos[key]

    match event.key:
        case pygame.K_RETURN:
            active_box = None
        case pygame.K_BACKSPACE:
            if pos > 0:
                user_input[key] = text[:pos - 1] + text[pos:]
                cursor_pos[key] -= 1
        case pygame.K_LEFT:
            if pos > 0:
                cursor_pos[key] -= 1
        case pygame.K_RIGHT:
            if pos < len(text):
                cursor_pos[key] += 1
        case _:
            if event.unicode.isdigit() or event.unicode in {'.', '-', ','}:
                user_input[key] = text[:pos] + event.unicode + text[pos:]
                cursor_pos[key] += 1

# Parse color input
def parse_color(value, default):
    try:
        r, g, b = map(int, value.split(','))
        return tuple(max(0, min(255, c)) for c in (r, g, b))
    except:
        return default

# Validate user inputs
def get_validated_inputs():
    try:
        threshold = float(user_input["threshold"]) / 100 or 0.025
        min_bar_height = float(user_input["min_bar_height"]) or 5
        smoothing_factor = float(user_input["smoothing_factor"]) or 0.15
        fps = int(user_input["fps"]) or 60
        start_color = parse_color(user_input["start_color"], (255, 0, 0))
        end_color = parse_color(user_input["end_color"], (0, 0, 255))
    except ValueError:
        threshold, min_bar_height, smoothing_factor = 0.025, 5, 0.15
        fps = 60
        start_color, end_color = (255, 0, 0), (0, 0, 255)

    return threshold, min_bar_height, smoothing_factor, fps, start_color, end_color

# Main UI loop
def run_ui():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    while True:
        draw_ui(screen)
        threshold, min_bar_height, smoothing_factor, fps, start_color, end_color, start_program = handle_ui_events()

        if start_program:
            return threshold, min_bar_height, smoothing_factor, fps, start_color, end_color
