import mss
import numpy as np
import time
import threading

class ScreenCapture:
    def __init__(self, capture_interval=1.5):
        """
        Initialize screen capture utility
        Args:
            capture_interval: Time between captures in seconds (default: 1.5)
        """
        self.capture_interval = capture_interval
        self._running = False
        self._capture_thread = None
        self._callback = None
        self.last_screenshot = None

    def start_capture(self, callback=None):
        """
        Start continuous screen capture
        Args:
            callback: Function to call with screenshot data
        """
        if self._running:
            return False
        
        self._running = True
        self._callback = callback
        self._capture_thread = threading.Thread(target=self._capture_loop)
        self._capture_thread.daemon = True
        self._capture_thread.start()
        return True

    def stop_capture(self):
        """Stop the screen capture process"""
        self._running = False
        if self._capture_thread:
            self._capture_thread.join(timeout=2.0)
            self._capture_thread = None
        return True

    def take_single_screenshot(self):
        """Take a single screenshot and return it as numpy array"""
        with mss.mss() as sct:
            monitor = sct.monitors[0]  # Capture the entire screen
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            return img
    
    def _capture_loop(self):
        """Main capture loop that runs in a separate thread"""
        with mss.mss() as sct:
            while self._running:
                try:
                    start_time = time.time()
                    
                    # Capture the entire screen menggunakan instance MSS dari thread ini
                    monitor = sct.monitors[0]
                    screenshot = sct.grab(monitor)
                    img = np.array(screenshot)
                    self.last_screenshot = img
                    
                    # Call the callback function if provided
                    if self._callback:
                        self._callback(img)
                    
                    # Calculate sleep time to maintain the desired interval
                    elapsed = time.time() - start_time
                    sleep_time = max(0, self.capture_interval - elapsed)
                    time.sleep(sleep_time)
                except Exception as e:
                    print(f"Error during screen capture: {e}")
                    time.sleep(1)  # Sleep briefly before retrying

    @property
    def is_running(self):
        """Check if the capture is currently running"""
        return self._running 

    def set_capture_interval(self, interval):
        """
        Update the capture interval
        Args:
            interval: New time between captures in seconds
        """
        self.capture_interval = max(0.1, float(interval))
        return True 