import numpy as np
import pyaudio
import pygame

import visualizergui

# Initialize Pygame and PyAudio
pygame.init()

# Screen setup
WIDTH, HEIGHT = visualizergui.WIDTH, visualizergui.HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# PyAudio setup
p = pyaudio.PyAudio()
device_info = p.get_default_input_device_info()
device_name = device_info['name']
FORMAT = pyaudio.paInt16
CHUNK = 1024
CHANNELS = int(device_info['maxInputChannels'])
RATE = int(device_info['defaultSampleRate'])
NUM_BARS = WIDTH // 5  # Number of bars in visualization
font = pygame.font.SysFont('franklingothicmedium', 13, False, True)


# Audio stream setup
def create_stream():
    return p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=0,
                  frames_per_buffer=CHUNK)


# Draw frequency spectrum
def draw_spectrum(spectrum, min_bar_height, start_color, end_color):
    """Draw the audio spectrum on the screen with logarithmically spaced frequency labels."""
    screen.fill(visualizergui.BLACK)
    bar_width = WIDTH // NUM_BARS

    # Label positions for frequencies
    label_positions = np.linspace(0, NUM_BARS - 1, WIDTH // 100, dtype=int)
    label_y = 3

    # Draw frequency labels and lines
    for i in label_positions:
        freq = (i * (RATE / 2)) / (NUM_BARS - 1)
        draw_frequency_label(i, freq, bar_width, label_y)

    # Draw the bars representing the spectrum
    for i, magnitude in enumerate(spectrum):
        height = max(int(magnitude * (HEIGHT - 50)), min_bar_height)
        color = get_color_for_frequency(i, NUM_BARS, start_color, end_color)
        pygame.draw.rect(screen, color, (i * bar_width, HEIGHT - height, bar_width - 2, height))

    pygame.display.flip()


def draw_frequency_label(i, freq, bar_width, label_y):
    """Draw frequency label and vertical line."""
    freq_text = font.render(f'{int(freq)} Hz', True, visualizergui.WHITE)
    text_width = freq_text.get_width()
    label_x = min(i * bar_width + 2, WIDTH - text_width - 5)
    screen.blit(freq_text, (label_x, label_y))
    pygame.draw.line(screen, (96, 96, 96), (label_x - 3, label_y), (label_x - 3, HEIGHT), bar_width - 2)


# Blends two colors together for gradient
def get_color_for_frequency(frequency_index, num_bars, start_color, end_color):
    ratio = frequency_index / (num_bars - 1) if num_bars > 1 else 0
    return tuple(
        int(start_c * (1 - ratio) + end_c * ratio)
        for start_c, end_c in zip(start_color, end_color)
    )


# Main spectrum update function
def update_spectrum(threshold, min_bar_height, smoothing_factor, fps, start_color, end_color):
    stream = create_stream()
    smoothed_spectrum = np.zeros(NUM_BARS)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_KP_ENTER):
                running = False

        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16) - np.mean(np.frombuffer(data, dtype=np.int16))

        # Mono inputs
        if CHANNELS > 1:
            audio_data = audio_data[0::CHANNELS]

        # Apply hanning window to reduce spectral leakage
        windowed_data = audio_data * np.hanning(len(audio_data))

        # Perform FFT and get spectrum magnitude
        fft_data = np.abs(np.fft.rfft(windowed_data))
        if np.max(fft_data) > 0:
            fft_data /= np.max(fft_data)

        fft_data = np.log1p(fft_data)
        indices = np.linspace(0, len(fft_data) - 1, NUM_BARS).astype(int)
        new_spectrum = fft_data[indices]
        smoothed_spectrum = (smoothing_factor * new_spectrum) + ((1 - smoothing_factor) * smoothed_spectrum)

        # Apply threshold and minimum bar height
        smoothed_spectrum = np.where(smoothed_spectrum <= threshold, min_bar_height / (HEIGHT - 50), smoothed_spectrum)

        # Draw spectrum on screen
        draw_spectrum(smoothed_spectrum, min_bar_height, start_color, end_color)

        # Limit frame rate
        clock.tick(fps)

    stream.stop_stream()
    stream.close()
    p.terminate()
