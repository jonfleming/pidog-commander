#!/usr/bin/python3
"""
Mock version of transcribe_mic.py for local testing without Google Cloud Speech API
"""

import time
import threading
import random
import os

def process_text(text):
    """Default mock process text function"""
    print("Mock heard:", str(text))

def process_text_gui(text):
    """Mock GUI process text function"""
    print("Mock GUI heard:", str(text))
    # In real implementation this would use pyautogui
    # For mock, we just print what would happen
    if "enter" in text or "new line" in text:
        print("Mock: Would press Enter...")
    elif "tab" in text or "next" in text:
        print("Mock: Would press Tab...")
    elif "escape" in text:
        print("Mock: Would press Esc...")
    elif "f11" in text or "full screen" in text:
        print("Mock: Would press F11...")
    elif "period" in text or "next" in text:
        print("Mock: Would type period...")
    elif "delete" in text or "backspace" in text:
        print("Mock: Would delete...")
    elif "space" in text:
        print("Mock: Would press Space...")
    else:
        print(f"Mock: Would type '{text}'")

def record(duration, filename, sr=16000, channels=1, frames_per_buffer=1024):
    """Mock record function"""
    print(f'Mock: Recording {duration} seconds to {filename}...')
    time.sleep(duration)
    
    # Create a dummy wav file
    with open(filename, 'wb') as f:
        f.write(b'MOCK_WAV_DATA')
    
    print('Mock: Recording complete.')

def transcribe_file(speech_file, sr=16000, language_code='en-US', speech_adaptation=None):
    """Mock transcribe file function"""
    print(f'Mock: Transcribing file {speech_file}...')
    
    # Mock transcription results
    mock_transcripts = [
        "sit down",
        "stand up", 
        "shake hands",
        "bark",
        "lie down"
    ]
    
    transcript = random.choice(mock_transcripts)
    print(f'Mock Transcript: {transcript}')
    return transcript

def transcribe_streaming(sr=16000, channels=1, frames_per_buffer=1024, language_code='en-US', callback=process_text_gui, speech_adaptation=None):
    """
    Mock streaming transcription that simulates voice commands
    """
    print(f"Mock: Starting streaming transcription (sample rate: {sr})")
    
    # Get phrases from speech adaptation if available
    if speech_adaptation and hasattr(speech_adaptation, 'phrase_sets'):
        # Extract phrases from the adaptation object
        phrases = []
        for phrase_set in speech_adaptation.phrase_sets:
            for phrase in phrase_set.phrases:
                phrases.append(phrase['value'])
        test_commands = phrases
    else:
        # Default test commands
        test_commands = [
            "sit", "stand", "lie down", "shake", "bark", "howl", "pant",
            "forward", "backward", "turn left", "turn right", "wag tail",
            "look left", "look right", "look up", "look down", "sleep",
            "pushup", "surprise", "alert", "attack", "reset", "yes", "no",
            "think", "lick", "five", "twist"
        ]
    
    print(f"Mock: Available voice commands: {test_commands}")
    
    def simulate_voice_input():
        """Simulate periodic voice commands for testing"""
        command_count = 0
        print("Mock: Voice command simulation started...")
        print("Mock: Commands will be generated every 10-30 seconds")
        
        while True:
            # Wait between 10-30 seconds between commands
            wait_time = random.uniform(10, 30)
            time.sleep(wait_time)
            
            command = random.choice(test_commands)
            command_count += 1
            
            print(f"\n=== Mock Voice Input #{command_count} ===")
            print(f"Simulated voice command: '{command}'")
            print("=" * 40)
            
            if callback:
                try:
                    callback(command)
                except Exception as e:
                    print(f"Mock: Error in callback for command '{command}': {e}")
    
    # Start simulation thread
    print("Mock: Starting voice input simulation thread...")
    voice_thread = threading.Thread(target=simulate_voice_input, daemon=True)
    voice_thread.start()
    
    print("Mock: Streaming simulation active. Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nMock: Streaming stopped by user.')
    
    return voice_thread

def get_speech_adaptation(phrases_file):
    """Mock speech adaptation function"""
    print(f"Mock: Loading speech adaptation from {phrases_file}")
    
    phrases = []
    
    # Try to read phrases from file
    if os.path.exists(phrases_file):
        try:
            with open(phrases_file, 'r') as f:
                file_phrases = f.read().splitlines()
            phrases = [phrase.strip() for phrase in file_phrases if phrase.strip()]
            print(f"Mock: Loaded {len(phrases)} phrases from {phrases_file}")
        except Exception as e:
            print(f"Mock: Error reading {phrases_file}: {e}")
    else:
        print(f"Mock: Phrases file {phrases_file} not found, using defaults")
    
    # Use defaults if no phrases loaded
    if not phrases:
        phrases = [
            "sit", "stand", "lie down", "shake", "bark", "howl", "pant",
            "forward", "backward", "turn left", "turn right", "wag tail",
            "look left", "look right", "look up", "look down", "sleep",
            "pushup", "surprise", "alert", "attack", "reset", "yes", "no",
            "think", "lick", "five", "twist"
        ]
        print(f"Mock: Using {len(phrases)} default phrases")
    
    # Create mock adaptation object
    class MockPhraseSet:
        def __init__(self, phrases):
            self.phrases = [{'value': phrase, 'boost': 10} for phrase in phrases]
    
    class MockSpeechAdaptation:
        def __init__(self, phrase_sets):
            self.phrase_sets = phrase_sets
    
    phrase_set = MockPhraseSet(phrases)
    adaptation = MockSpeechAdaptation([phrase_set])
    
    print(f"Mock: Speech adaptation created with phrases: {phrases[:5]}{'...' if len(phrases) > 5 else ''}")
    return adaptation

def main():
    """Mock main function for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Mock audio transcription for testing'
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
        transcribe_streaming(sr=int(args.sample), language_code=args.language, 
                           callback=callback_fn, speech_adaptation=speech_adaptation)
    else:
        record(sr=int(args.sample), duration=args.duration, filename=args.file)
        transcribe_file(sr=int(args.sample), speech_file=args.file, 
                       language_code=args.language, speech_adaptation=speech_adaptation)

if __name__ == '__main__':
    main()
