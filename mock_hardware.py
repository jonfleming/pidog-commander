#!/usr/bin/python3
"""
Mock implementations for Picamera2 and PiDog hardware for local testing
"""

import io
import time
import threading
from threading import Condition
import random
import logging
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Mock Picamera2 classes and functions
class MockJpegEncoder:
    """Mock JPEG encoder"""
    def __init__(self):
        pass

class MockFileOutput:
    """Mock file output"""
    def __init__(self, output_stream):
        self.output_stream = output_stream

class MockPicamera2:
    """Mock Picamera2 class that generates fake video frames"""
    
    def __init__(self):
        self.sensor_modes = [
            {'size': (640, 480), 'format': 'RGB888'},
            {'size': (1920, 1080), 'format': 'RGB888'},
            {'size': (1280, 720), 'format': 'RGB888'}
        ]
        self.config = None
        self.recording = False
        self.output_stream = None
        self.encoder = None
        self.frame_thread = None
        self.controls = {}
        
    def create_video_configuration(self, main=None, raw=None):
        """Create mock video configuration"""
        return {
            'main': main or {'size': (640, 480), 'format': 'XRGB8888'},
            'raw': raw or self.sensor_modes[0]
        }
    
    def configure(self, config):
        """Configure the mock camera"""
        self.config = config
        print(f"Mock camera configured with: {config}")
    
    def start_recording(self, encoder, file_output):
        """Start mock recording that generates fake frames"""
        self.encoder = encoder
        self.output_stream = file_output.output_stream
        self.recording = True
        
        # Start thread to generate fake frames
        self.frame_thread = threading.Thread(target=self._generate_frames, daemon=True)
        self.frame_thread.start()
        print("Mock camera recording started")
    
    def stop_recording(self):
        """Stop mock recording"""
        self.recording = False
        if self.frame_thread:
            self.frame_thread.join(timeout=1)
        print("Mock camera recording stopped")
    
    def set_controls(self, controls):
        """Set camera controls"""
        self.controls.update(controls)
        print(f"Mock camera controls set: {controls}")
    
    def _generate_frames(self):
        """Generate fake camera frames"""
        frame_count = 0
        while self.recording:
            try:
                # Create a simple test image
                img = Image.new('RGB', (640, 480), color=(50, 100, 150))
                draw = ImageDraw.Draw(img)
                
                # Add some dynamic content
                timestamp = time.strftime("%H:%M:%S")
                draw.text((10, 10), f"Mock Camera Feed", fill=(255, 255, 255))
                draw.text((10, 30), f"Time: {timestamp}", fill=(255, 255, 255))
                draw.text((10, 50), f"Frame: {frame_count}", fill=(255, 255, 255))
                
                # Add a moving circle for visual feedback
                circle_x = 50 + (frame_count % 540)
                draw.ellipse([circle_x, 200, circle_x + 50, 250], fill=(255, 0, 0))
                
                # Convert to JPEG bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=85)
                jpeg_bytes = img_byte_arr.getvalue()
                
                # Write to output stream
                if self.output_stream:
                    self.output_stream.write(jpeg_bytes)
                
                frame_count += 1
                time.sleep(1/30)  # ~30 FPS
                
            except Exception as e:
                logging.error(f"Error generating mock frame: {e}")
                break

# Mock RGB Strip class
class MockRGBStrip:
    """Mock RGB strip for PiDog"""
    def __init__(self):
        self.mode = 'off'
        self.color = 'white'
        self.bps = 1.0
    
    def set_mode(self, mode, color='white', bps=1.0):
        """Set RGB strip mode"""
        self.mode = mode
        self.color = color
        self.bps = bps
        print(f"Mock RGB Strip: mode={mode}, color={color}, bps={bps}")

# Mock PiDog classes
class MockPiDog:
    """Mock PiDog robot class"""
    
    def __init__(self, leg_init_angles=None, head_init_angles=None, tail_init_angle=None):
        self.leg_init_angles = leg_init_angles or [25, 25, -25, -25, 70, -45, -70, 45]
        self.head_init_angles = head_init_angles or [0, 0, -25]
        self.tail_init_angle = tail_init_angle or [0]
        
        self.leg_current_angles = list(self.leg_init_angles)
        self.head_current_angles = list(self.head_init_angles)
        
        self.current_action = "idle"
        self.position = "standing"
        self.rgb_strip = MockRGBStrip()
        
        # Mock actions dictionary
        self.actions_dict = {
            'sit': [[[30, 60, -30, -60, 80, -45, -80, 45]]],
            'stand': [[[40, 15, -40, -15, 60, 5, -60, -5]]],
            'lie': [[[90, 90, -90, -90, 45, -45, -45, 45]]],
            'forward': [[[40, 15, -40, -15, 60, 5, -60, -5]]],
            'backward': [[[40, 15, -40, -15, 60, 5, -60, -5]]],
            'turn_left': [[[40, 15, -40, -15, 60, 5, -60, -5]]],
            'turn_right': [[[40, 15, -40, -15, 60, 5, -60, -5]]],
            'wag_tail': [[[40, 15, -40, -15, 60, 5, -60, -5]]],
            'doze_off': [[[90, 90, -90, -90, 45, -45, -45, 45]]],
            'push_up': [[[40, 15, -40, -15, 60, 5, -60, -5]]],
            'half_sit': [[[50, 40, -50, -40, 70, -35, -70, 35]]],
        }
        
        print(f"Mock PiDog initialized with leg_angles={leg_init_angles}, head_angles={head_init_angles}")
    
    def do_action(self, action_name, step_count=1, speed=None):
        """Execute a mock action"""
        self.current_action = action_name
        print(f"Mock PiDog executing action: {action_name} (steps: {step_count}, speed: {speed})")
        
        # Update current angles if action exists
        if action_name in self.actions_dict:
            self.leg_current_angles = list(self.actions_dict[action_name][0][0])
        
        # Simulate action duration
        action_duration = {
            'sit': 2.0,
            'lie': 2.5,
            'stand': 1.5,
            'forward': 1.0,
            'backward': 1.0,
            'turn_left': 1.5,
            'turn_right': 1.5,
            'wag_tail': 2.0,
            'doze_off': 3.0,
            'push_up': 2.5,
            'half_sit': 1.5,
        }
        
        duration = action_duration.get(action_name, 1.0)
        time.sleep(duration)
        print(f"Mock PiDog completed action: {action_name}")
        return True
    
    def read_distance(self):
        """Mock distance reading"""
        # Simulate a random distance between 10 and 100 cm
        distance = random.randint(10, 100)
        print(f"Mock PiDog read_distance: {distance} cm")
        return distance
    
    def legs_move(self, angles_list, immediately=False, speed=80):
        """Move legs to specified angles"""
        print(f"Mock PiDog legs_move: angles={len(angles_list)} positions, speed={speed}, immediately={immediately}")
        if angles_list:
            self.leg_current_angles = list(angles_list[-1])  # Use last position
        time.sleep(0.1 * len(angles_list))  # Simulate movement time
    
    def head_move(self, angles_list, pitch_comp=0, roll_comp=0, immediately=False, speed=80):
        """Move head to specified angles"""
        print(f"Mock PiDog head_move: angles={angles_list}, speed={speed}, pitch_comp={pitch_comp}")
        if angles_list:
            self.head_current_angles = list(angles_list[-1])
        time.sleep(0.1 * len(angles_list))
    
    def head_move_raw(self, angles_list, speed=80):
        """Move head with raw angles"""
        print(f"Mock PiDog head_move_raw: {len(angles_list)} positions, speed={speed}")
        if angles_list:
            self.head_current_angles = list(angles_list[-1])
        time.sleep(0.1 * len(angles_list))
    
    def legs_angle_calculation(self, leg_positions):
        """Calculate leg angles from positions"""
        # Mock calculation - return flattened list
        result = []
        for pos in leg_positions:
            result.extend(pos)
        print(f"Mock legs_angle_calculation: {leg_positions} -> {result}")
        return result
    
    def speak(self, sound_name, volume=100):
        """Mock speak function"""
        print(f"Mock PiDog speak: '{sound_name}' at volume {volume}")
        # Simulate speaking duration
        speak_durations = {
            'pant': 0.5,
            'single_bark_1': 0.3,
            'howling': 2.5,
        }
        duration = speak_durations.get(sound_name, 0.5)
        time.sleep(duration)
    
    def wait_all_done(self):
        """Wait for all movements to complete"""
        print("Mock PiDog wait_all_done")
        time.sleep(0.1)
    
    def wait_legs_done(self):
        """Wait for leg movements to complete"""
        print("Mock PiDog wait_legs_done")
        time.sleep(0.05)
    
    def wait_head_done(self):
        """Wait for head movements to complete"""
        print("Mock PiDog wait_head_done")
        time.sleep(0.05)
    
    def body_stop(self):
        """Stop body movement"""
        print("Mock PiDog body_stop")
        self.current_action = "idle"
    
    def reset(self):
        """Reset mock dog to default position"""
        self.current_action = "idle"
        self.position = "standing"
        self.leg_current_angles = list(self.leg_init_angles)
        self.head_current_angles = list(self.head_init_angles)
        print("Mock PiDog reset to default position")
    
    def close(self):
        """Close mock dog connection"""
        print("Mock PiDog connection closed")

# Function to patch imports
def patch_imports():
    """Patch the imports to use mock implementations"""
    import sys
    
    # Create mock modules
    mock_picamera2 = type(sys)('picamera2')
    mock_picamera2.Picamera2 = MockPicamera2
    
    mock_encoders = type(sys)('encoders')
    mock_encoders.JpegEncoder = MockJpegEncoder
    mock_picamera2.encoders = mock_encoders
    
    mock_outputs = type(sys)('outputs')
    mock_outputs.FileOutput = MockFileOutput
    mock_picamera2.outputs = mock_outputs
    
    # Create mock pidog module
    mock_pidog = type(sys)('pidog')
    mock_pidog.Pidog = MockPiDog
    
    # Add to sys.modules
    sys.modules['picamera2'] = mock_picamera2
    sys.modules['picamera2.encoders'] = mock_encoders
    sys.modules['picamera2.outputs'] = mock_outputs
    sys.modules['pidog'] = mock_pidog
    
    print("Hardware mocking enabled - Picamera2 and PiDog mocked for local testing")

if __name__ == "__main__":
    # Test the mock implementations
    patch_imports()
    
    # Test mock camera
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
    
    print("Testing mock camera...")
    picam2 = Picamera2()
    print(f"Sensor modes: {picam2.sensor_modes}")
    
    # Test mock dog
    print("Testing mock dog...")
    from pidog import Pidog
    dog = Pidog()
    dog.do_action("sit")
    dog.do_action("bark")
    dog.reset()
