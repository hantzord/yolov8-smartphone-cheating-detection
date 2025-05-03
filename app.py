import os
import tkinter as tk

# Import our utility modules
from utils.screen_capture import ScreenCapture
from utils.detection import SmartphoneDetector
from gui import SmartphoneMonitorGUI

def main():
    """
    Main function to initialize and run the Smartphone Monitor application
    """
    # Set up model path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "model", "best.pt")
    
    # Fallback to alternative model path if the primary one doesn't exist
    if not os.path.exists(model_path):
        mobile_model_path = os.path.join(os.path.dirname(base_dir), "mobile_yolov8_model", "weights", "best.pt")
        if os.path.exists(mobile_model_path):
            model_path = mobile_model_path
    
    # Create Tkinter root window
    root = tk.Tk()
    
    # Initialize the screen capture and detector modules
    screen_capture = ScreenCapture(capture_interval=1.5)
    
    try:
        # Load the detection model
        detector = SmartphoneDetector(model_path)
        
        # Create and start the GUI application
        app = SmartphoneMonitorGUI(root, detector, screen_capture)
        
        # Start the main event loop
        root.mainloop()
    except Exception as e:
        # If an error occurs during initialization, show an error message
        import traceback
        traceback.print_exc()
        from tkinter import messagebox
        messagebox.showerror("Error", f"An error occurred during initialization: {e}")

if __name__ == "__main__":
    main() 