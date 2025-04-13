import sys
import pygame
import audiovisualizer
from audiovisualizer import update_spectrum
import visualizergui

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