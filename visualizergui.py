import pygame

pygame.init()

# Constants
WHITE = (255, 255, 255)
GREEN = (50, 150, 50)
BLACK = (0, 0, 0)

# To be made adjustable soon...
WIDTH, HEIGHT = 960, 400
START_COLOR = (200 , 0, 0)
END_COLOR = (0, 0, 200)
FONT = pygame.font.SysFont('franklingothicmedium', 16)

# UI Elements
text_boxes = {
    "threshold": pygame.Rect(200, 10, 100, 25),
    "min_bar_height": pygame.Rect(200, 40, 100, 25),
    "smoothing_factor": pygame.Rect(200, 70, 100, 25)
}

# default values
user_input = {
    "threshold": "2.5",
    "min_bar_height": "5",
    "smoothing_factor": "0.25"
}

active_box = None
cursor_pos = {key: len(user_input[key]) for key in text_boxes}  # Cursor position per box
start_button = pygame.Rect(500, 150, 150, 40)

# Draw the UI, including text boxes and the blinking cursor.
def draw_ui(screen):
    screen.fill(BLACK)

    labels = {
        "threshold": "Minimum Threshold %:",
        "min_bar_height": "Min Bar Height in pixels:",
        "smoothing_factor": "Smoothing Factor (0 to 1):"
    }

    for key, rect in text_boxes.items():
        label = FONT.render(labels[key], True, WHITE)
        screen.blit(label, (10, rect.y + 5))
        pygame.draw.rect(screen, WHITE, rect, 2)

        # Render text
        text_surface = FONT.render(user_input[key], True, WHITE)
        screen.blit(text_surface, (rect.x + 5, rect.y + 5))

        # Cursor blinking logic
        if key == active_box:
            time_elapsed = pygame.time.get_ticks() // 500  # Blinks every 500ms
            if time_elapsed % 2 == 0:
                cursor_x = rect.x + 5 + FONT.size(user_input[key][:cursor_pos[key]])[0]
                pygame.draw.line(screen, WHITE, (cursor_x, rect.y + 5), (cursor_x, rect.y + 20), 2)

    # Draw Start Button
    pygame.draw.rect(screen, GREEN, start_button)
    start_text = FONT.render("Click to Start!", True, WHITE)
    screen.blit(start_text, (start_button.x + 25, start_button.y + 10))

    pygame.display.flip()


def handle_ui_events():
    """Handle user input, including text input and button clicks."""
    global active_box
    start_program = False

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                pygame.quit()
                exit()
            case pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    start_program = True
                for key, rect in text_boxes.items():
                    if rect.collidepoint(event.pos):
                        active_box = key
                        cursor_pos[key] = len(user_input[key])  # Place cursor at end
                        break
                else:
                    active_box = None
            case pygame.KEYDOWN if active_box:
                match event.key:
                    case pygame.K_RETURN:
                        active_box = None
                    case pygame.K_BACKSPACE:
                        if cursor_pos[active_box] > 0:
                            user_input[active_box] = user_input[active_box][:cursor_pos[active_box] - 1] + user_input[
                                                                                                               active_box][
                                                                                                           cursor_pos[
                                                                                                               active_box]:]
                            cursor_pos[active_box] -= 1
                    case pygame.K_LEFT:
                        if cursor_pos[active_box] > 0:
                            cursor_pos[active_box] -= 1
                    case pygame.K_RIGHT:
                        if cursor_pos[active_box] < len(user_input[active_box]):
                            cursor_pos[active_box] += 1
                    case _ if event.unicode.isdigit() or (
                                event.unicode in {'.', '-'} and event.unicode not in user_input[active_box]):
                        user_input[active_box] = user_input[active_box][:cursor_pos[active_box]] + event.unicode + \
                                                 user_input[active_box][cursor_pos[active_box]:]
                        cursor_pos[active_box] += 1

    # Check for empty input fields before assigning values.
    try:
        threshold = (float(user_input["threshold"]) / 100) if user_input["threshold"] else 0.025
        min_bar_height = float(user_input["min_bar_height"]) if user_input["min_bar_height"] else 5
        smoothing_factor = float(user_input["smoothing_factor"]) if user_input["smoothing_factor"] else 0.25
    except ValueError:
        threshold, min_bar_height, smoothing_factor = 0.025, 5, 0.25  # Default values in case of invalid input

    return threshold, min_bar_height, smoothing_factor, start_program


def run_ui():
    """Runs the UI and returns user settings when 'Start' is clicked."""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Audio Spectrum Visualizer - Settings")

    while True:
        draw_ui(screen)
        threshold, min_bar_height, smoothing_factor, start_program = handle_ui_events()

        if start_program:
            # Proceed only if the inputs are valid
            if threshold and min_bar_height and smoothing_factor:
                return threshold, min_bar_height, smoothing_factor