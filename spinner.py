import sys
import time
import threading
from colorama import init, Fore

# Initialize colorama
init()

class Spinner:
    """A class to display and control a spinner in the console."""
    
    def __init__(self, message="Processing", delay=0.1):
        self.message = message
        self.delay = delay
        self.spinner_chars = ['|', '/', '-', '\\']
        self.running = False
        self.spinner_thread = None
    
    def spin(self):
        i = 0
        while self.running:
            sys.stdout.write(f"\r{Fore.GREEN}{self.spinner_chars[i]}{Fore.GREEN} {self.message}")
            sys.stdout.flush()
            time.sleep(self.delay)
            i = (i + 1) % len(self.spinner_chars)
    
    def start(self):
        self.running = True
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
    
    def stop(self):
        self.running = False
        if self.spinner_thread:
            # Clear the line when done
            sys.stdout.write(f"\r{' ' * (len(self.message) + 2)}\r")
            sys.stdout.flush()
            # Reset color
            sys.stdout.write(Fore.RESET)
            sys.stdout.flush()

# Example usage
if __name__ == "__main__":
    # Create and start the spinner
    spinner = Spinner("Working on something important...")
    spinner.start()
    
    # Simulate your actual process
    try:
        # Your actual work goes here
        time.sleep(5)  # Simulating work that takes 5 seconds
    finally:
        # Stop the spinner when process completes
        spinner.stop()
        print(f"{Fore.GREEN}✓{Fore.RESET} Process completed successfully!")