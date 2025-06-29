# PiDog Commander - Mock Mode Setup

This guide explains how to run the PiDog Commander locally on a non-Pi device using mock implementations of the hardware dependencies.

## Overview

The mock mode allows you to:
- Test the web interface and voice commands without Pi hardware
- Develop and debug the application on any computer
- See simulated camera feed with moving elements
- Observe all robot actions logged to console
- Use web-based speech recognition (browser-dependent)

## Quick Start

### 1. Install Dependencies

```bash
# Install mock requirements (minimal dependencies)
pip install -r requirements_mock.txt
```

### 2. Run Mock Mode

```bash
# Run the mock version
python main_mock.py
```

### 3. Open Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

## What's Mocked

### Hardware Components
- **Picamera2**: Generates fake video frames with timestamp and moving elements
- **PiDog Robot**: All movements and actions are simulated and logged to console
- **Google Cloud Speech**: Replaced with simulated voice commands every 10-30 seconds
- **Audio Input**: No microphone required, commands are generated automatically

### Mock Files Created
- `mock_hardware.py` - Core mock implementations for Picamera2 and PiDog
- `transcribe_mic_mock.py` - Mock speech recognition without Google Cloud API
- `main_mock.py` - Modified main script that uses mocked components
- `requirements_mock.txt` - Minimal dependencies for local testing

## Features in Mock Mode

### Web Interface
- All original buttons work and send commands to mock robot
- Enhanced UI with mock mode indicators
- Web speech recognition (if browser supports it)
- Real-time command feedback

### Mock Camera Feed
- Displays simulated video stream at `/stream.mjpg`
- Shows timestamp, frame counter, and moving red circle
- Updates at ~30 FPS like real camera

### Voice Command Simulation
- Automatically generates random voice commands every 10-30 seconds
- Uses phrases from `phrases.txt` if available
- Commands are clearly logged with timestamps

### Robot Action Simulation
- All robot actions are logged with realistic timing
- Simulates movement durations (sit: 2s, bark: 1s, etc.)
- Tracks current robot state and position
- RGB strip commands are logged

## Available Commands

The mock system supports all original voice commands:

### Basic Actions
- sit, stand, lie down, shake, bark, howl, pant, sleep

### Movements  
- forward, backward, turn left, turn right, wag tail

### Head Movements
- look left, look right, look up, look down, think, yes, no

### Special Actions
- high five (or "5"), lick, pushup, twist, surprise, alert, attack, reset

## Testing Different Scenarios

### 1. Test Web Commands
Click any button in the web interface to see immediate mock robot response.

### 2. Test Voice Recognition (Browser)
- Click "Toggle Voice Recognition" button
- Speak commands if your browser supports speech recognition
- Commands will be processed by the mock robot

### 3. Test Automatic Voice Simulation
- Let the application run and observe automatic voice commands
- Commands appear every 10-30 seconds in the console

### 4. Test Camera Feed
- Observe the mock camera stream showing moving elements
- Verify the video feed updates continuously

## Console Output Example

```
🤖 PIDOG COMMANDER - MOCK MODE
==================================================
Mock hardware initialized successfully!
Starting web server on http://localhost:8000
Voice commands will be simulated automatically
==================================================

Mock: Loading speech adaptation from phrases.txt
Mock: Loaded 25 phrases from phrases.txt
Mock: Starting streaming transcription (sample rate: 44100)
Mock: Voice command simulation started...

=== Mock Voice Input #1 ===
Simulated voice command: 'sit'
========================================
heard: sit
Mock PiDog executing action: sit (steps: 1, speed: 80)
Mock PiDog completed action: sit
```

## Customizing Mock Behavior

### Modify Voice Command Frequency
Edit `transcribe_mic_mock.py`, line ~75:
```python
wait_time = random.uniform(10, 30)  # Change timing here
```

### Add Custom Commands
Edit `phrases.txt` to include your custom voice commands.

### Modify Camera Feed
Edit `mock_hardware.py`, `_generate_frames()` method to customize the mock video.

### Change Robot Action Timing
Edit `mock_hardware.py`, `do_action()` method to adjust action durations.

## Troubleshooting

### Port Already in Use
If port 8000 is busy, modify `main_mock.py`:
```python
address = ('', 8001)  # Change port number
```

### Missing Dependencies
Install required packages:
```bash
pip install Pillow numpy
```

### Browser Speech Recognition Not Working
- Use Chrome/Edge for best speech recognition support
- Ensure microphone permissions are granted
- HTTPS may be required for some browsers (use local development server)

### Mock Commands Not Appearing
- Check console output for error messages
- Verify `phrases.txt` exists and contains commands
- Ensure voice simulation thread is starting

## Development Tips

### Adding New Mock Features
1. Add new methods to `MockPiDog` class in `mock_hardware.py`
2. Update action durations in the `action_duration` dictionary
3. Test with both web interface and simulated voice commands

### Debugging Mock Issues
- All mock actions are logged to console with timestamps
- Use print statements in mock methods for detailed debugging
- Monitor browser console for web interface issues

### Extending Mock Capabilities
- Add new mock hardware components by following the existing pattern
- Create mock classes that simulate the real hardware API
- Use `patch_imports()` to replace real modules with mocks

## Switching Back to Real Hardware

To run on actual Pi hardware:
1. Use `main.py` instead of `main_mock.py`
2. Install real requirements: `pip install -r requirements.txt`
3. Ensure Pi hardware is connected and configured
4. Set up Google Cloud Speech API credentials

## File Structure

```
pidog-commander/
├── main.py                 # Original Pi version
├── main_mock.py           # Mock version for local testing
├── mock_hardware.py       # Mock hardware implementations
├── transcribe_mic_mock.py # Mock speech recognition
├── requirements.txt       # Pi requirements
├── requirements_mock.txt  # Mock requirements
├── pidog_commands.py      # Command processing (works with both)
├── preset_actions.py      # Action definitions (works with both)
└── phrases.txt           # Voice command phrases
```

This mock setup provides a complete development and testing environment for the PiDog Commander without requiring any Pi-specific hardware.
