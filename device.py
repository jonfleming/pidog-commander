import pyaudio

pa = pyaudio.PyAudio()

for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"Input Device ID {i} - {info['name']}")
        for rate in [8000, 11025, 16000, 22050, 32000, 44100, 48000]:
            try:
                if pa.is_format_supported(rate,
                                           input_device=info['index'],
                                           input_channels=1,
                                           input_format=pyaudio.paInt16):
                    print(f"  Supported sample rate: {rate}")
            except ValueError:
                continue