import pyaudio
import os
import sys
import sys
import pyaudio
import pygame
from audiovisualizer import update_spectrum
from visualizergui import run_ui

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

# Initialize PyAudio
p = pyaudio.PyAudio()

# Get default input device info
device_info = p.get_default_input_device_info()
device_name = device_info['name']  # Get the device name


def main():
    # Call the UI and get the values
    threshold, min_bar_height, smoothing_factor = run_ui()

    # Now you have threshold, min_bar_height, and smoothing_factor with the user settings
    print(f"Threshold: {threshold}, Min Bar Height: {min_bar_height}, Smoothing Factor: {smoothing_factor}")

    # Set the window title to the input device name
    pygame.display.set_caption(f"Audio Spectrum Visualizer - Input: {device_name}")
    clock = pygame.time.Clock()

    # Now you can proceed with the rest of the program (visualizer, etc.) with these values
    try:
        update_spectrum(threshold, min_bar_height, smoothing_factor)
    finally:
        # Ensure Pygame is properly quit after the program ends
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
