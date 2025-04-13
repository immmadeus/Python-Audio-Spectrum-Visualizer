import sys
import pygame
from audiovisualizer import update_spectrum
import visualizergui
import audiovisualizer

def main():
    # Call the UI and get values
    threshold, min_bar_height, smoothing_factor, fps, start_color, end_color = visualizergui.run_ui()
    try:
        pygame.display.set_caption(f"Audio Spectrum Visualizer - Input: {audiovisualizer.device_name}")
        update_spectrum(threshold, min_bar_height, smoothing_factor,  fps, start_color, end_color)
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()