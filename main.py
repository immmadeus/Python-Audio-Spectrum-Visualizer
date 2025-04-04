import os
import sys
import pygame
import audiovisualizer
from audiovisualizer import update_spectrum
import visualizergui

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
else:
    print("Warning: Icon file not found!")

def main():
    # Call the UI and get values
    threshold, min_bar_height, smoothing_factor = visualizergui.run_ui()
    pygame.display.set_caption(f"Audio Spectrum Visualizer - Input: {audiovisualizer.device_name}")
    try:
        update_spectrum(threshold, min_bar_height, smoothing_factor)
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()