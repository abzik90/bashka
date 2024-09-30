import pyaudio

# Initialize the PyAudio object
p = pyaudio.PyAudio()

# List all available audio devices
print("Available audio devices:")
for i in range(p.get_device_count()):
    device_info = p.get_device_info_by_index(i)
    print(f"Index: {i}, Name: {device_info['name']}, Channels: {device_info['maxInputChannels']}")
print(p.get_default_input_device_info())
# Terminate the PyAudio object
p.terminate()
