import numpy as np
import pyaudio
import pygame
import visualizergui
from visualizergui import handle_ui_events

# Initialize Pygame and PyAudio
pygame.init()
WIDTH, HEIGHT = visualizergui.WIDTH, visualizergui.HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
p = pyaudio.PyAudio()

# Get default audio input info
device_info = p.get_default_input_device_info()
device_name = device_info['name']  # Get the device name

# Default audio config
FORMAT = pyaudio.paInt16
CHUNK = 1024  # Buffer size
CHANNELS = int(device_info['maxInputChannels'])  # Get the number of channels from the device
RATE = int(device_info['defaultSampleRate'])  # Sampling rate of input
NUM_BARS = WIDTH // 5  # Number of bars in visualization
font = pygame.font.SysFont('franklingothicmedium', 13)

# Audio stream setup
def create_stream():
    return p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=0, frames_per_buffer=CHUNK)

# Function to update the spectrum based on audio input
def update_spectrum(threshold, min_bar_height, smoothing_factor):
    stream = create_stream()
    smoothed_spectrum = np.zeros(NUM_BARS)
    running = True
    clock = pygame.time.Clock()  # Limit the frame rate

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            threshold, min_bar_height, smoothing_factor, start_program = handle_ui_events()

            if start_program:
                running = False

        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        audio_data = audio_data - np.mean(audio_data)  # Remove DC offset

        if CHANNELS > 1:
            audio_data = audio_data[0::CHANNELS]

        # Apply FFT to the audio data
        fft_data = np.abs(np.fft.rfft(audio_data))
        fft_data /= np.max(fft_data) + 1e-6  # Normalize
        fft_data = np.log(fft_data + 1)  # Apply log scaling

        indices = np.linspace(0, len(fft_data) - 1, NUM_BARS).astype(int)
        new_spectrum = fft_data[indices]
        smoothed_spectrum = (smoothing_factor * new_spectrum) + ((1 - smoothing_factor) * smoothed_spectrum)

        # Apply threshold and minimum bar height
        min_magnitude = min_bar_height / (HEIGHT - 50)
        smoothed_spectrum = np.where(smoothed_spectrum <= threshold, min_magnitude, smoothed_spectrum)

        # Draw the spectrum on screen
        draw_spectrum(smoothed_spectrum, min_bar_height)

        # Limit the frame rate to 60 FPS
        clock.tick(60)

    stream.stop_stream()
    stream.close()
    p.terminate()

def draw_spectrum(spectrum, min_bar_height):
    """Draw the audio spectrum on the screen with logarithmically spaced frequency labels."""
    screen.fill((0, 0, 0))
    bar_width = WIDTH // NUM_BARS

    # Define label positions for frequencies
    label_positions = np.linspace(0, NUM_BARS - 1, WIDTH // 100, dtype=int)
    label_y = 10

    # Draw frequency labels
    for i in label_positions:

        freq = (i * (RATE / 2)) / (NUM_BARS - 1)
        freq_text = font.render(f'{int(freq)} Hz', True, (255, 255, 255))
        text_width = freq_text.get_width()
        label_x = min(i * bar_width + 2, WIDTH - text_width - 5)
        screen.blit(freq_text, (label_x, label_y))  # Keep labels at the top

        # Draw the vertical line next to label
        pygame.draw.line(screen, (64, 64, 64), (label_x - 4, label_y),
                         (label_x - 4, HEIGHT), 2)

    # Draw the bars representing the spectrum
    for i, magnitude in enumerate(spectrum):
        height = int(magnitude * (HEIGHT - 50))  # Scale bars within max area
        height = max(height, min_bar_height)  # Ensure minimum size for the bars
        color = get_color_for_frequency(i, NUM_BARS)  # Color based on frequency
        pygame.draw.rect(screen, color, (i * bar_width, HEIGHT - height, bar_width - 2, height))

    pygame.display.flip()

#blends two colors together for gradient
def get_color_for_frequency(frequency_index, num_bars):
    start_color = visualizergui.START_COLOR
    end_color = visualizergui.END_COLOR

    ratio = frequency_index / (num_bars - 1) if num_bars > 1 else 0
    return tuple(
        int(start_c * (1 - ratio) + end_c * ratio)
        for start_c, end_c in zip(start_color, end_color)
    )
