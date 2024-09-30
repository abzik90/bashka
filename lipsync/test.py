import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import wave
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Ellipse

# Load and prepare audio
filename = 'audio.wav'
wave_read = wave.open(filename, 'rb')
frame_rate = wave_read.getframerate()
n_frames = wave_read.getnframes()
audio_data = np.frombuffer(wave_read.readframes(n_frames), dtype=np.int16)
wave_read.close()

# Prepare plot
fig, ax = plt.subplots()
ax.set_xlim(-2, 2)
ax.set_ylim(-3, 3)

# Draw robot face
face = plt.Circle((0, 0), 2, color='lightgrey')
eye_left = plt.Circle((-0.75, 1), 0.3, color='black')
eye_right = plt.Circle((0.75, 1), 0.3, color='black')
mouth = Ellipse((0, -1.25), width=1.0, height=0.2, edgecolor='black', facecolor='none')  # Oval mouth
ax.add_patch(face)
ax.add_patch(eye_left)
ax.add_patch(eye_right)
ax.add_patch(mouth)

# Update function for animation
def update(frame):
    # Adjust the mouth vertical height based on audio amplitude
    start_idx = frame * int(frame_rate / 30)
    end_idx = (frame + 1) * int(frame_rate / 30)
    # Jaw motion logic:
    amplitude = np.abs(audio_data[start_idx:end_idx]).mean() / 32768.0
    height = 0.2 + amplitude * 0.5  # Adjust this factor to change mouth movement sensitivity
    mouth.height = height

# Create animation
anim = FuncAnimation(
    fig, 
    update, 
    frames=n_frames // int(frame_rate / 30), 
    interval=1000 / 30, 
    repeat=False  # Disable looping
)

# Play audio and show animation
def play_audio():
    sd.play(audio_data, samplerate=frame_rate)
    plt.show()
    sd.wait()  # Wait until the sound has finished playing

play_audio()
