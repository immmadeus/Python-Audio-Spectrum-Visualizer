import os
import sys
import pygame
import audiovisualizer
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

def main():
    # Call the UI and get the values
    threshold, min_bar_height, smoothing_factor = run_ui()
    # Set the window title to the input device name
    pygame.display.set_caption(f"Audio Spectrum Visualizer - Input: {audiovisualizer.device_name}")
    # Now you can proceed with the rest of the program (visualizer, etc.) with these values
    try:
        update_spectrum(threshold, min_bar_height, smoothing_factor)
    finally:
        # Ensure Pygame is properly quit after the program ends
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()