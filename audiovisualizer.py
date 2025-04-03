import numpy as np
import pyaudio
import pygame
import sys
import os
import time

# Function to handle file paths correctly when running as an executable
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Initialize PyAudio
p = pyaudio.PyAudio()

# List available devices (for debugging)
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))

# Get default input device info
device_info = p.get_default_input_device_info()
device_name = device_info['name']  # Get the device name

# Set the window title to the input device name
pygame.display.set_caption(f"Audio Spectrum Visualizer - Input: {device_name}")
clock = pygame.time.Clock()

# Load icon with safe path handling
icon_path = resource_path("icon-1628258_1280.ico")
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
else:
    print("Warning: Icon file not found!")

# Audio stream config
FORMAT = pyaudio.paInt16
CHUNK = 1024  # Buffer size
CHANNELS = 1  # Mono input
RATE = 48000  # Sampling rate of input
NUM_BARS = 256  # Number of bars in visualization
THRESHOLD = 0.1  # Threshold for magnitude (below this, bars will still be shown as small)
MIN_BAR_HEIGHT = 5  # Minimum height for bars below the threshold
SMOOTHING_FACTOR = 0.25  # Smoothing factor for transitions

# Set up font for frequency labels
font = pygame.font.SysFont('franklingothicmedium', 12)

# Initialize smoothed spectrum
smoothed_spectrum = np.zeros(NUM_BARS)

def get_color_for_frequency(frequency_index, num_bars):
    """Returns an RGB color based on frequency index."""
    red = int(255 * (1 - frequency_index / num_bars))
    blue = int(255 * (frequency_index / num_bars))
    return red, 0, blue

def draw_spectrum(spectrum):
    """Draws the audio spectrum on the screen with logarithmically spaced frequency labels."""
    screen.fill((0, 0, 0))
    bar_width = WIDTH // NUM_BARS

    # Define label positions
    label_positions = np.linspace(0, NUM_BARS - 1, 13, dtype=int)
    label_y = 10  # Label text Y position
    max_bar_area = HEIGHT - 50  # Leave space at the top for labels

    for i in label_positions:
        freq = (i * (RATE / 2)) / (NUM_BARS - 1)
        freq_text = font.render(f'{int(freq)} Hz', True, (255, 255, 255))
        text_width = freq_text.get_width()
        label_x = min(i * bar_width + 2, WIDTH - text_width - 5)
        screen.blit(freq_text, (label_x, label_y))  # Keep labels at the top

    for i, magnitude in enumerate(spectrum):
        height = int(magnitude * max_bar_area)  # Scale bars within max area
        height = max(height, MIN_BAR_HEIGHT)  # Ensure minimum size
        height = min(height, max_bar_area)  # Prevent exceeding label area
        color = get_color_for_frequency(i, NUM_BARS)
        pygame.draw.rect(screen, color, (i * bar_width, HEIGHT - height, bar_width - 2, height))

    pygame.display.flip()

def create_stream():
    """Create a persistent audio stream."""
    return p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=0, frames_per_buffer=CHUNK)

# Open the stream once and keep it global
stream = create_stream()

def update_spectrum():
    """Continuously captures audio and updates the spectrum display with smoothing."""
    global stream, smoothed_spectrum
    running = True
    last_time = time.time()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            if stream.is_active():
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)

                audio_data = audio_data - np.mean(audio_data)  # Remove DC offset
                fft_data = np.abs(np.fft.rfft(audio_data))
                fft_data /= np.max(fft_data) + 1e-6  # Normalize
                fft_data = np.log(fft_data + 1)  # Apply log scaling

                indices = np.linspace(0, len(fft_data) - 1, NUM_BARS).astype(int)
                new_spectrum = fft_data[indices]

                # Apply smoothing filter
                smoothed_spectrum = (SMOOTHING_FACTOR * new_spectrum) + ((1 - SMOOTHING_FACTOR) * smoothed_spectrum)

                draw_spectrum(smoothed_spectrum)
            else:
                print("Stream inactive. Restarting...")
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception:
                    pass  # Ignore errors if the stream is already closed
                stream = create_stream()  # Try reopening
                time.sleep(0.5)  # Small delay before retrying
                continue

        except IOError as e:
            print(f"Audio input error: {e}")
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass  # Ignore errors if the stream is already closed
            stream = create_stream()  # Try reopening
            time.sleep(0.5)  # Small delay before retrying
            continue

        except Exception as e:
            print(f"Unexpected error: {e}")
            running = False
            break

        time_diff = time.time() - last_time
        if time_diff < 1 / 24:
            time.sleep(1 / 24 - time_diff)

        last_time = time.time()

    # Cleanup
    try:
        if stream.is_active():
            stream.stop_stream()
            stream.close()
    except Exception as e:
        print(f"Error stopping stream: {e}")
    finally:
        p.terminate()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    update_spectrum()
