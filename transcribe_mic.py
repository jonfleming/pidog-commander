import argparse
import os
import wave
import sys
import pyaudio
from spinner import Spinner
from google.cloud import speech

# PyAutoGUI will be imported only if needed
pyautogui = None
speech_adaptation = None

if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    print('Error: The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/jon/jonefleming-n8n-31f098b2ea64.json'

def process_text(text):
    print("heard:", str(text))

def process_text_gui(text):
    global pyautogui
    if pyautogui is None:
        try:
            import pyautogui
        except ImportError:
            print("Warning: pyautogui not installed. GUI automation disabled.")
            return process_text(text)

    print("heard:", str(text))

    if "enter" in text or "new line" in text:
        print("Pressing Enter...")
        pyautogui.hotkey("enter")
    elif "tab" in text or "next" in text:
        print("Pressing Tab...")
        pyautogui.hotkey("tab")
    elif "escape" in text:
        print("Pressing Esc...")
        pyautogui.hotkey("escape")
    elif "f11" in text or "full screen" in text:
        print("Pressing F11...")
        pyautogui.hotkey("f11")
    elif "period" in text or "next" in text:
        print("Pressing period...")
        pyautogui.typewrite(". ")
    elif "delete" in text or "backspace" in text:
        print("Deleting...")
#        pyautogui.hotkey("numlock") # Ensure numlock is off
        pyautogui.hotkey('home')
        pyautogui.hotkey('shift', 'down')
        pyautogui.hotkey("backspace")
#        pyautogui.hotkey("numlock") # Turn numlock back on
    elif "space" in text:
        print("Pressing Space...")
        pyautogui.hotkey("space")
    else:
        pyautogui.typewrite(str(text))

def record(duration, filename, sr=16000, channels=1, frames_per_buffer=1024):
    pa = pyaudio.PyAudio()

    try:
        stream = pa.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sr,
                        input=True,
                        frames_per_buffer=frames_per_buffer)
    except Exception as e:
        print(f'Could not open microphone stream: {e}')
        pa.terminate()
        sys.exit(1)

    print(f'Recording {duration} seconds...')
    frames = []

    for _ in range(int(sr / frames_per_buffer * duration)):
        try:
            data = stream.read(frames_per_buffer, exception_on_overflow=False)
            frames.append(data)
        except OSError as e:
            if e.errno == -9981:  # Input overflow
                print("Warning: Input overflow occurred, some audio data may have been lost")
                continue
            else:
                raise e

    print('Recording complete.')

    stream.stop_stream()
    stream.close()
    pa.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sr)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_file(speech_file, sr=16000, language_code='en-US', speech_adaptation=None):
    client = speech.SpeechClient()

    with open(speech_file, 'rb') as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sr,
        language_code=language_code,
        adaptation=speech_adaptation,
    )

    print('Transcribing...')
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        transcript = result.alternatives[0].transcript
        print(f'Transcript: {transcript}')
    
def transcribe_streaming(sr=16000, channels=1, frames_per_buffer=1024, language_code='en-US', callback=process_text_gui, speech_adaptation=None):
    """
    Continuously record audio from microphone and stream to Google Cloud Speech-to-Text.
    Press Ctrl+C to stop streaming.
    """
    spinner = Spinner("")
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sr,
        language_code=language_code,
        adaptation=speech_adaptation,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    pa = pyaudio.PyAudio()
    try:
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sr,
            input=True,
            frames_per_buffer=frames_per_buffer,
        )
    except Exception as e:
        print(f'Could not open microphone stream: {e}')
        pa.terminate()
        return

    print('Streaming... Press Ctrl+C to stop.')
    spinner.start()

    def request_generator():
        while True:
            try:
                data = stream.read(frames_per_buffer, exception_on_overflow=False)
            except KeyboardInterrupt:
                return
            yield speech.StreamingRecognizeRequest(audio_content=data)

    requests = request_generator()
    try:
        # streaming_recognize expects positional args: (streaming_config, requests)
        responses = client.streaming_recognize(streaming_config, requests)
        for response in responses:
            for result in response.results:
                transcript = result.alternatives[0].transcript
                if result.is_final:
                    callback(transcript)
                else:
                    pass
                    # print(f'Partial: {transcript}', end='\r')
    except KeyboardInterrupt:
        print('\nStreaming stopped.')
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

def get_speech_adaptation(phrases_file):
    # read phrases from file
    if not os.path.exists(phrases_file):
        print(f'Error: Phrases file {phrases_file} does not exist.')
        sys.exit(1)
    
    with open(phrases_file, 'r') as f:
        phrases = f.read().splitlines()
    
    phrases = [{'value': phrase.strip(), 'boost': 10} for phrase in phrases if phrase.strip()]
    
    if not phrases:
        print(f'Error: No valid phrases found in {phrases_file}.')
        sys.exit(1)

    # Create a PhraseSet with the phrases
    phrase_set = speech.PhraseSet(phrases=phrases)
    
    # Create SpeechAdaptation with the PhraseSet
    adaptation = speech.SpeechAdaptation(
        phrase_sets=[phrase_set]
    )

    return adaptation

def main():
    global speech_adaptation
    parser = argparse.ArgumentParser(
        description='Record audio from microphone and transcribe using Google Cloud Speech-to-Text'
    )
    parser.add_argument('--duration', '-d', type=float, default=5.0,
                        help='Recording duration in seconds')
    parser.add_argument('--file', '-f', type=str, default='output.wav',
                        help='Output WAV file name')
    parser.add_argument('--phrases', '-p', type=str, default=None,
                        help='Speech adaptation phrases file')
    parser.add_argument('--language', '-l', type=str, default='en-US',
                        help='Language code (e.g., en-US)')
    parser.add_argument('--stream', '-s', action='store_true',
                        help='Enable continuous streaming recognition')
    parser.add_argument('--sample', '-sr', type=str, default="44100",
                        help='Recording sample rate in Hz')
    parser.add_argument('--gui', '-g', action='store_true',
                        help='Enable keyboard automation with PyAutoGUI')

    args = parser.parse_args()
    callback_fn = process_text_gui if args.gui else process_text
    speech_adaptation = get_speech_adaptation(args.phrases) if args.phrases else None

    if args.stream:
        transcribe_streaming(sr=int(args.sample), language_code=args.language, callback=callback_fn, speech_adaptation=speech_adaptation)
    else:
        record(sr=int(args.sample), duration=args.duration, filename=args.file)
        transcribe_file(sr=int(args.sample), speech_file=args.file, language_code=args.language, speech_adaptation=speech_adaptation)

if __name__ == '__main__':
    main()