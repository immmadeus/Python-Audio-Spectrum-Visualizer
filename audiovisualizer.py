import os
import sys

import numpy as np
import pyaudio
import pygame

from visualizergui import handle_ui_events


# Function to handle file paths correctly when running as an executable
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


# Load icon with safe path handling
icon_path = resource_path("icon-1628258_1280.ico")
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
else:
    print("Warning: Icon file not found!")

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1280, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Initialize PyAudio
p = pyaudio.PyAudio()

# Get default input device info
device_info = p.get_default_input_device_info()
device_name = device_info['name']  # Get the device name

# Default config
FORMAT = pyaudio.paInt16
CHUNK = 1024  # Buffer size
CHANNELS = int(device_info['maxInputChannels'])  # Get the number of channels from the device
RATE = int(device_info['defaultSampleRate'])  # Sampling rate of input
NUM_BARS = WIDTH // 5  # Number of bars in visualization
font = pygame.font.SysFont('franklingothicmedium', 12)

# Audio stream setup
def create_stream():
    """Create a persistent audio stream."""
    return p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=0, frames_per_buffer=CHUNK)

# Function to update the spectrum based on audio input
def update_spectrum(threshold, min_bar_height, smoothing_factor):
    """Continuously captures audio and updates the spectrum display with smoothing."""
    stream = create_stream()
    smoothed_spectrum = np.zeros(NUM_BARS)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            threshold, min_bar_height, smoothing_factor, start_program = handle_ui_events()

            # If the user pressed Enter, start the program
            if start_program:
                running = False

        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        audio_data = audio_data - np.mean(audio_data)  # Remove DC offset

        fft_data = np.abs(np.fft.rfft(audio_data))
        fft_data /= np.max(fft_data) + 1e-6  # Normalize
        fft_data = np.log(fft_data + 1)  # Apply log scaling

        indices = np.linspace(0, len(fft_data) - 1, NUM_BARS).astype(int)
        new_spectrum = fft_data[indices]

        smoothed_spectrum = (smoothing_factor * new_spectrum) + ((1 - smoothing_factor) * smoothed_spectrum)
        draw_spectrum(smoothed_spectrum, min_bar_height)

    stream.stop_stream()
    stream.close()
    p.terminate()

def draw_spectrum(spectrum, min_bar_height):
    """Draw the audio spectrum on the screen with logarithmically spaced frequency labels."""
    screen.fill((0, 0, 0))
    bar_width = WIDTH // NUM_BARS

    # Define label positions
    label_positions = np.linspace(0, NUM_BARS - 1, WIDTH // 100, dtype=int)
    label_y = 10  # Label text Y position
    max_bar_area = HEIGHT - 50  # Leave space at the top for labels

    for i in label_positions:
        freq = (i * (RATE / 2)) / (NUM_BARS - 1)
        freq_text = font.render(f'{int(freq)} Hz', True, (255, 255, 255))
        text_width = freq_text.get_width()
        label_x = min(i * bar_width + 2, WIDTH - text_width - 5)
        screen.blit(freq_text, (label_x, label_y))  # Keep labels at the top

        # Draw the vertical white line next to the label
        pygame.draw.line(screen, (64, 64, 64), (label_x - 4, label_y),
                         (label_x - 4, HEIGHT), 2)

    for i, magnitude in enumerate(spectrum):
        height = int(magnitude * (HEIGHT - 50))  # Scale bars within max area
        height = max(height, min_bar_height)  # Ensure minimum size
        color = get_color_for_frequency(i, NUM_BARS)
        pygame.draw.rect(screen, color, (i * bar_width, HEIGHT - height, bar_width - 2, height))

    pygame.display.flip()

def get_color_for_frequency(frequency_index, num_bars):
    """Returns an RGB color based on frequency index, with a gradient between two colors."""
    ratio = frequency_index / (num_bars - 1)
    red = int(255 * (1 - ratio) + 0 * ratio)
    green = int(0 * (1 - ratio) + 0 * ratio)
    blue = int(0 * (1 - ratio) + 255 * ratio)
    return red, green, blue
