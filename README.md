# Smartphone Detection Monitor

A Python desktop application that can:
1. Capture the entire screen in real-time with a refresh interval of 1-2 seconds
2. Use a YOLOv8 model to detect smartphones in the screen capture
3. Show popup notifications when smartphones are detected
4. Provide a simple interface with monitoring controls and a log area

## Requirements

- Python 3.8 or newer
- Windows operating system

## Installation

1. Clone this repository or download the ZIP file
2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure the YOLOv8 model file (`smartphone_detector.pt`) is in the `model` directory
2. Run the application:
   ```
   python main.py
   ```
3. Use the "Start Monitoring" button to begin detection
4. A popup notification will appear when a smartphone is detected
5. Use the "Stop Monitoring" button to end detection

## Project Structure

```
project/
├── main.py               # Main application entry point
├── model/
│   └── smartphone_detector.pt  # YOLOv8 model for smartphone detection
├── utils/
│   ├── screen_capture.py      # Screen capture functionality
│   └── detection.py           # YOLOv8 detection implementation
├── assets/
│   └── icons/                # Application icons
└── README.md                # This file
```

## Libraries Used

- **Screen Capture**: mss (for fast screen capture)
- **Object Detection**: Ultralytics YOLOv8 / torch
- **GUI**: Tkinter (for a lightweight desktop interface)
- **Image Processing**: OpenCV, Numpy, PIL

## Notes

- The application is designed to be lightweight and responsive
- Detection happens in memory without saving screenshots to disk
- Adjustable capture interval in the ScreenCapture class (default: 1.5 seconds)
- Notifications appear as popups on the screen when smartphones are detected 