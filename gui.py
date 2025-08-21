import os
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk
from datetime import datetime
import winsound
import json

class SmartphoneMonitorGUI:
    """
    Class responsible for the graphical user interface of the Smartphone Detection Monitor
    """
    
    def __init__(self, root, detector, screen_capture):
        """
        Initialize the GUI components
        
        Args:
            root: Tkinter root window
            detector: SmartphoneDetector instance for detection operations
            screen_capture: ScreenCapture instance for capturing screen
        """
        self.root = root
        self.detector = detector
        self.screen_capture = screen_capture
        
        # Main window configuration
        self.root.title("Smartphone Monitor")
        self.root.geometry("1024x768")
        self.root.resizable(True, True)
        
        # GUI state variables
        self.is_monitoring = False
        self.notification_shown = False
        self.notification_window = None
        self.notification_tabs = None
        self.tab_count = 0
        self.current_image = None
        self.display_width = 800
        self.display_height = 450
        
        # Exclusion zones
        self.exclusion_zones = []
        self.is_selecting_zone = False
        self.start_x = None
        self.start_y = None
        self.current_rectangle = None
        self.scaled_exclusion_zones = []
        self.exclusion_colors = []
        
        # Speed control
        self.speed_value = tk.DoubleVar(value=1.5)
        self.threshold_value = tk.DoubleVar(value=0.5)
        
        # Path to the exclusion zones file
        self.exclusion_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "excluded_areas.json")
        
        # Configure styles
        self.configure_styles()
        
        # Create UI components
        self.create_widgets()
        
        # Load exclusion zones if file exists
        self.load_exclusion_zones()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Configure>", self.on_resize)
    
    def configure_styles(self):
        """Configure styles for the application"""
        # Configure the main window background
        self.root.configure(bg="#f0f0f0")
        
        # Configure ttk styles
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 11, "bold"))
        
        # Buttons styles
        style.configure("Green.TButton", background="#4CAF50", foreground="black")
        style.configure("Red.TButton", background="#F44336", foreground="black")
    
    def create_widgets(self):
        """Create all GUI components"""
        # Main container with padding
        self.main_container = ttk.Frame(self.root, padding=10)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self.create_header()
        
        # Create control panel
        self.create_control_panel()
        
        # Create settings panel
        self.create_settings_panel()
        
        # Create preview area
        self.create_preview_area()
        
        # Create bottom panel (exclusion zones and log)
        self.create_bottom_panel()
        
        # Add initial message to log
        self.log_message("Application started. Click 'Start Monitoring' to begin detection.")
    
    def create_header(self):
        """Create the header section of the GUI"""
        # Top header frame
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title label
        title_label = ttk.Label(
            header_frame,
            text="Smartphone Detection Monitor",
            font=("Arial", 16, "bold"),
        )
        title_label.pack(pady=(0, 10))
    
    def create_control_panel(self):
        """Create the control panel with monitoring buttons and status"""
        # Control panel with more appealing design
        control_panel = ttk.Frame(self.main_container)
        control_panel.pack(fill=tk.X, pady=(0, 10))
        
        # Create two columns - control buttons and status
        controls_frame = ttk.Frame(control_panel)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        status_frame = ttk.Frame(control_panel)
        status_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Start button with improved style
        self.start_btn = tk.Button(
            controls_frame, 
            text="Start Monitoring", 
            command=self.start_monitoring,
            bg="#4CAF50",
            fg="black",
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            width=20,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10), pady=5)
        
        # Stop button with improved style
        self.stop_btn = tk.Button(
            controls_frame, 
            text="Stop Monitoring", 
            command=self.stop_monitoring,
            bg="#cccccc",
            fg="black",
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            width=20,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_btn.pack(side=tk.LEFT, pady=5)
        
        # Add hover effects for buttons
        def on_start_enter(e):
            if self.start_btn['state'] != 'disabled':
                self.start_btn['bg'] = '#45a049'  # Darker green on hover
        
        def on_start_leave(e):
            if self.start_btn['state'] != 'disabled':
                self.start_btn['bg'] = '#4CAF50'  # Original green
        
        def on_stop_enter(e):
            if self.stop_btn['state'] != 'disabled':
                self.stop_btn['bg'] = '#da190b'  # Darker red on hover
        
        def on_stop_leave(e):
            if self.stop_btn['state'] != 'disabled':
                self.stop_btn['bg'] = '#F44336'  # Original red
        
        self.start_btn.bind("<Enter>", on_start_enter)
        self.start_btn.bind("<Leave>", on_start_leave)
        self.stop_btn.bind("<Enter>", on_stop_enter)
        self.stop_btn.bind("<Leave>", on_stop_leave)
        
        # Status indicator with better visualization
        ttk.Label(status_frame, text="Status:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.status_indicator = ttk.Label(
            status_frame, 
            text="●", 
            foreground="red",
            font=("Arial", 16)
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(5, 5))
        self.status_label = ttk.Label(status_frame, text="Not Monitoring", foreground="red")
        self.status_label.pack(side=tk.LEFT)
    
    def create_settings_panel(self):
        """Create the settings panel with threshold and speed controls"""
        # Settings frame
        settings_frame = ttk.LabelFrame(self.main_container, text="Detection Settings", padding=5)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Threshold slider
        ttk.Label(settings_frame, text="Confidence Threshold:").pack(side=tk.LEFT, padx=(5, 5))
        
        self.threshold_slider = ttk.Scale(
            settings_frame,
            from_=0.1,
            to=0.9,
            orient=tk.HORIZONTAL,
            variable=self.threshold_value,
            length=200,
            command=self.update_threshold
        )
        self.threshold_slider.pack(side=tk.LEFT, padx=(0, 5))
        
        # Label untuk menampilkan nilai threshold saat ini
        self.threshold_label = ttk.Label(settings_frame, text="0.50")
        self.threshold_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Tombol reset threshold
        ttk.Button(
            settings_frame,
            text="Reset",
            command=self.reset_threshold,
            width=8
        ).pack(side=tk.LEFT)
        
        # Separator
        ttk.Separator(settings_frame, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10, pady=5)
        
        # Speed control
        ttk.Label(settings_frame, text="Detection Speed:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.speed_slider = ttk.Scale(
            settings_frame,
            from_=0.5,
            to=5.0,
            orient=tk.HORIZONTAL,
            variable=self.speed_value,
            length=200,
            command=self.update_detection_speed
        )
        self.speed_slider.pack(side=tk.LEFT, padx=(0, 5))
        
        # Label untuk menampilkan nilai speed saat ini
        self.speed_label = ttk.Label(settings_frame, text="1.50 sec")
        self.speed_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Tombol reset speed
        ttk.Button(
            settings_frame,
            text="Reset",
            command=self.reset_detection_speed,
            width=8
        ).pack(side=tk.LEFT)
    
    def create_preview_area(self):
        """Create the preview area for displaying screen captures"""
        # Preview area with improved layout
        preview_frame = ttk.LabelFrame(self.main_container, text="Screen Monitoring Preview", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas untuk preview dengan aspect ratio 16:9
        self.preview_canvas = tk.Canvas(
            preview_frame,
            bg="black", 
            width=self.display_width,
            height=self.display_height
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Message when no preview is available
        self.preview_message = self.preview_canvas.create_text(
            self.display_width // 2,
            self.display_height // 2,
            text="Screen preview will appear here when monitoring starts",
            fill="white",
            font=("Arial", 12),
            justify=tk.CENTER
        )
    
    def create_bottom_panel(self):
        """Create the bottom panel with exclusion zone controls and log area"""
        # Bottom frame for exclusion zone controls and log
        bottom_frame = ttk.Frame(self.main_container)
        bottom_frame.pack(fill=tk.BOTH, expand=False)
        
        # Frame untuk exclusion zones dengan tampilan yang lebih baik
        exclusion_frame = ttk.LabelFrame(bottom_frame, text="Exclusion Zones", padding=5)
        exclusion_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        
        # Exclusion zone buttons in a better layout
        self.select_zone_btn = ttk.Button(
            exclusion_frame,
            text="Select Area",
            command=self.start_exclusion_selection,
            width=15
        )
        self.select_zone_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Tombol untuk memuat gambar eksternal
        self.load_screenshot_btn = ttk.Button(
            exclusion_frame,
            text="Load Screenshot",
            command=self.load_external_screenshot,
            width=15
        )
        self.load_screenshot_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Tombol untuk menyimpan exclusion zones
        self.save_zones_btn = ttk.Button(
            exclusion_frame,
            text="Save Zones",
            command=self.save_exclusion_zones,
            width=15
        )
        self.save_zones_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Tombol untuk membersihkan zona eksklusif
        ttk.Button(
            exclusion_frame,
            text="Clear Zones",
            command=self.clear_exclusion_zones,
            width=15
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status exclusion zones
        self.exclusion_status = ttk.Label(
            exclusion_frame,
            text="No exclusion areas defined"
        )
        self.exclusion_status.pack(side=tk.LEFT, padx=5)
        
        # Log area for application messages
        log_frame = ttk.LabelFrame(bottom_frame, text="Application Log", padding=5)
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Scrolled text area for log
        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            height=6,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_area.configure(state=tk.DISABLED)  # Make read-only
    
    # Monitoring control methods
    
    def start_monitoring(self):
        """Start the monitoring process"""
        if self.is_monitoring or not self.detector:
            return
        
        self.is_monitoring = True
        self.notification_shown = False
        
        # Update buttons
        self.start_btn.config(state=tk.DISABLED, bg="#cccccc")  # Gray when disabled
        self.stop_btn.config(state=tk.NORMAL, bg="#F44336")  # Red when enabled
        self.status_label.config(text="Monitoring", foreground="green")
        self.status_indicator.config(foreground="green")
        
        # Log the action
        self.log_message("Monitoring started")
        
        # Log exclusion zones if defined
        if self.exclusion_zones:
            self.log_message(f"Using {len(self.exclusion_zones)} exclusion zone(s):")
            for i, zone in enumerate(self.exclusion_zones):
                x1, y1, x2, y2 = zone
                self.log_message(f"  Zone {i+1}: ({x1},{y1}) to ({x2},{y2})")
        
        # Start screen capture with our callback
        self.screen_capture.start_capture(callback=self.process_screenshot)
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        # Update buttons
        self.start_btn.config(state=tk.NORMAL, bg="#4CAF50")  # Green when enabled
        self.stop_btn.config(state=tk.DISABLED, bg="#cccccc")  # Gray when disabled
        self.status_label.config(text="Not Monitoring", foreground="red")
        self.status_indicator.config(foreground="red")
        
        # Log the action
        self.log_message("Monitoring stopped")
        
        # Stop screen capture
        self.screen_capture.stop_capture()
        
        # If notification window exists, add a message that monitoring has stopped
        if self.notification_window and self.notification_window.winfo_exists():
            self.root.after(100, lambda: messagebox.showinfo(
                "Monitoring Stopped", 
                "Monitoring has been stopped. All detection alerts will remain open for your review.",
                parent=self.notification_window))
    
    # Image processing methods
    
    def process_screenshot(self, screenshot):
        """
        Process a screenshot to detect smartphones
        Args:
            screenshot: Numpy array of screenshot data
        """
        if not self.is_monitoring or not self.detector:
            return
        
        try:
            # Detect smartphones in the screenshot, kirimkan exclusion zones ke detector
            smartphones_detected, result_image = self.detector.detect_smartphone(
                screenshot, 
                exclusion_zones=self.exclusion_zones if self.exclusion_zones else None
            )
            
            # Update the preview with detected objects
            self.current_image = result_image
            self.update_preview_image(result_image)
            
            # Only process detections if any smartphones are detected outside exclusion zones
            if smartphones_detected:
                # Ada smartphone di luar exclusion zone, tampilkan alert
                detection_info = self.get_detection_info(result_image)
                
                self.log_message("ALERT: Smartphone detected outside exclusion zone!")
                self.show_notification(detection_info)
                self.notification_shown = True
            # If no smartphone and notification was shown before, just log it but keep notifications open
            elif not smartphones_detected and self.notification_shown:
                self.log_message("No smartphone detected outside exclusion zones")
                
        except Exception as e:
            self.log_message(f"Error during detection: {e}")
    
    def update_preview_image(self, image):
        """Update the preview canvas with the current image and exclusion zones"""
        if image is None:
            return
            
        # Store image for later use
        self.current_image = image
        
        # Get canvas dimensions for scaling
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Default to preset values if canvas is not yet measured
        if canvas_width <= 1:
            canvas_width = self.display_width
        if canvas_height <= 1:
            canvas_height = self.display_height
        
        # Get image dimensions
        h, w = image.shape[:2]
        
        # Calculate scale to fit image into canvas
        scale_w = canvas_width / w
        scale_h = canvas_height / h
        scale = min(scale_w, scale_h)
        
        # Resize image to fit canvas
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize for display
        image_resized = cv2.resize(image, (new_w, new_h))
        
        # Convert to PIL Image for tkinter (OpenCV uses BGR, PIL uses RGB)
        pil_img = Image.fromarray(cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB))
        
        # Convert to PhotoImage for canvas
        self.tk_img = ImageTk.PhotoImage(image=pil_img)
        
        # Clear previous image and message
        self.preview_canvas.delete("all")
        
        # Calculate position to center image
        x_pos = (canvas_width - new_w) // 2
        y_pos = (canvas_height - new_h) // 2
        
        # Add image to canvas
        self.preview_canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=self.tk_img)
        
        # Recalculate scaled exclusion zones for new dimensions
        self.calculate_scaled_exclusion_zones()
        
        # Draw all exclusion zones
        for i, (x1, y1, x2, y2) in enumerate(self.scaled_exclusion_zones):
            color = self.exclusion_colors[i] if i < len(self.exclusion_colors) else '#ff0000'
            self.preview_canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=color,
                width=2,
                dash=(5, 5),
                fill=color,
                stipple="gray25",  # Semi-transparent fill
                tags=f"zone_{i}"
            )
    
    # Event handling methods
    
    def on_resize(self, event):
        """Handle window resize to update the preview canvas"""
        if hasattr(self, 'preview_canvas') and self.current_image is not None:
            # Only process if it's our main window being resized
            if event.widget == self.root:
                self.update_preview_image(self.current_image)
    
    def on_close(self):
        """Cleanup and close the application"""
        if self.is_monitoring:
            self.stop_monitoring()
        
        # Close notification window if open
        if self.notification_window and self.notification_window.winfo_exists():
            self.notification_window.destroy()
        
        self.root.destroy()
    
    # Utility methods
    
    def log_message(self, message):
        """Add a message to the log area with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, log_entry)
        self.log_area.see(tk.END)  # Scroll to the end
        self.log_area.config(state=tk.DISABLED)
    
    def update_threshold(self, event=None):
        """Update the threshold value when slider is moved"""
        # Update label dengan nilai threshold
        value = self.threshold_value.get()
        self.threshold_label.config(text=f"{value:.2f}")
        
        # Update threshold pada detector jika sudah diinisialisasi
        if hasattr(self, 'detector') and self.detector:
            self.detector.set_confidence_threshold(value)
            self.log_message(f"Detection threshold updated to {value:.2f}")
    
    def reset_threshold(self):
        """Reset threshold to default value (0.5)"""
        self.threshold_value.set(0.5)
        self.update_threshold()
    
    def update_detection_speed(self, event=None):
        """Update the detection speed when slider is moved"""
        # Update label dengan nilai speed
        value = self.speed_value.get()
        self.speed_label.config(text=f"{value:.2f} sec")
        
        # Update detection speed pada screen_capture
        self.screen_capture.set_capture_interval(value)
        self.log_message(f"Detection speed updated to {value:.2f} seconds")
    
    def reset_detection_speed(self):
        """Reset detection speed to default value (1.5 seconds)"""
        self.speed_value.set(1.5)
        self.update_detection_speed()
    
    # Exclusion zone methods
    
    def start_exclusion_selection(self):
        """Start the process of selecting an exclusion zone"""
        if self.is_monitoring:
            messagebox.showinfo("Warning", "Please stop monitoring before selecting exclusion areas.")
            return
        
        if not self.is_selecting_zone:
            self.is_selecting_zone = True
            self.select_zone_btn.config(text="Cancel Selection", style="Red.TButton")
            self.exclusion_status.config(text="Click and drag to select an area")
            
            # Bind mouse events to canvas
            self.preview_canvas.bind("<ButtonPress-1>", self.on_mouse_down)
            self.preview_canvas.bind("<B1-Motion>", self.on_mouse_drag)
            self.preview_canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
            
            # Take a screenshot to show on canvas if no current image
            if self.current_image is None:
                try:
                    screenshot = self.screen_capture.capture_screen()
                    self.current_image = screenshot
                    self.update_preview_image(screenshot)
                except Exception as e:
                    self.log_message(f"Error taking screenshot: {e}")
        else:
            self.cancel_exclusion_selection()
    
    def cancel_exclusion_selection(self):
        """Cancel the selection process"""
        self.is_selecting_zone = False
        self.select_zone_btn.config(text="Select Area", style="TButton")
        self.exclusion_status.config(text=f"{len(self.exclusion_zones)} exclusion area(s) defined")
        
        # Remove the current rectangle if it exists
        if self.current_rectangle:
            self.preview_canvas.delete(self.current_rectangle)
            self.current_rectangle = None
            
        # Unbind mouse events
        self.preview_canvas.unbind("<ButtonPress-1>")
        self.preview_canvas.unbind("<B1-Motion>")
        self.preview_canvas.unbind("<ButtonRelease-1>")
        
        # Redraw exclusion zones
        self.update_preview_image(self.current_image)
    
    def on_mouse_down(self, event):
        """Handle mouse button press for starting rectangle selection"""
        if not self.is_selecting_zone:
            return
            
        # Record start position
        self.start_x = event.x
        self.start_y = event.y
        
        # Create a new rectangle
        self.current_rectangle = self.preview_canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2, dash=(5, 5)
        )
    
    def on_mouse_drag(self, event):
        """Handle mouse drag for resizing selection rectangle"""
        if not self.is_selecting_zone or self.current_rectangle is None:
            return
            
        # Update rectangle size
        self.preview_canvas.coords(self.current_rectangle, self.start_x, self.start_y, event.x, event.y)
    
    def on_mouse_up(self, event):
        """Handle mouse button release to finalize selection"""
        if not self.is_selecting_zone or self.current_rectangle is None:
            return
            
        # Get the final coordinates
        end_x = event.x
        end_y = event.y
        
        # Ensure coordinates are ordered (top-left, bottom-right)
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        # Check if the rectangle is too small
        if abs(x2 - x1) < 20 or abs(y2 - y1) < 20:
            messagebox.showinfo("Warning", "Selection area is too small. Please try again.")
            self.preview_canvas.delete(self.current_rectangle)
            self.current_rectangle = None
            return
        
        # Convert canvas coordinates to actual screen coordinates
        if self.current_image is not None:
            h, w = self.current_image.shape[:2]
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # Calculate scale used for display
            scale_w = canvas_width / w
            scale_h = canvas_height / h
            scale = min(scale_w, scale_h)
            
            # Calculate offset for centering
            new_w = int(w * scale)
            new_h = int(h * scale)
            x_offset = (canvas_width - new_w) // 2
            y_offset = (canvas_height - new_h) // 2
            
            # Adjust coordinates based on scale and offset
            # Convert from canvas to scaled image coordinates
            x1_scaled = (x1 - x_offset) / scale if x1 >= x_offset else 0
            y1_scaled = (y1 - y_offset) / scale if y1 >= y_offset else 0
            x2_scaled = (x2 - x_offset) / scale if x2 >= x_offset else 0
            y2_scaled = (y2 - y_offset) / scale if y2 >= y_offset else 0
            
            # Ensure coordinates are within image bounds
            x1_scaled = max(0, min(w, x1_scaled))
            y1_scaled = max(0, min(h, y1_scaled))
            x2_scaled = max(0, min(w, x2_scaled))
            y2_scaled = max(0, min(h, y2_scaled))
            
            # Store the actual screen coordinates (make sure they're always in order)
            x1_final = min(x1_scaled, x2_scaled)
            y1_final = min(y1_scaled, y2_scaled)
            x2_final = max(x1_scaled, x2_scaled)
            y2_final = max(y1_scaled, y2_scaled)
            
            # Store as integers
            self.exclusion_zones.append((
                int(x1_final), 
                int(y1_final), 
                int(x2_final), 
                int(y2_final)
            ))
            
            # Store the canvas coordinates for display
            self.scaled_exclusion_zones.append((x1, y1, x2, y2))
            
            # Add a default color for this zone
            self.exclusion_colors.append('#ff0000')  # Red as default
            
            # Update the status
            self.exclusion_status.config(text=f"{len(self.exclusion_zones)} exclusion area(s) defined")
            
            # Display information about the zone
            self.log_message(f"Added exclusion zone: ({int(x1_final)},{int(y1_final)}) to ({int(x2_final)},{int(y2_final)})")
        
        # Remove temporary rectangle
        self.preview_canvas.delete(self.current_rectangle)
        self.current_rectangle = None
        
        # Return to normal mode
        self.cancel_exclusion_selection()
    
    def clear_exclusion_zones(self):
        """Clear all defined exclusion zones"""
        if self.is_selecting_zone:
            self.cancel_exclusion_selection()
            
        self.exclusion_zones = []
        self.scaled_exclusion_zones = []
        self.exclusion_colors = []
        self.exclusion_status.config(text="No exclusion areas defined")
        self.log_message("All exclusion zones cleared")
        
        # Redraw preview without zones
        if self.current_image is not None:
            self.update_preview_image(self.current_image)
    
    def load_external_screenshot(self):
        """Load an external screenshot image for zone selection"""
        if self.is_monitoring:
            messagebox.showinfo("Warning", "Please stop monitoring before loading an external screenshot.")
            return
            
        # Prompt user to select an image file
        file_path = filedialog.askopenfilename(
            title="Select Screenshot Image",
            filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg;*.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            # Load the image using OpenCV (in BGR format)
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError("Failed to load image")
                
            # Store as current image in BGR format (OpenCV standard)
            self.current_image = img
            
            # Update preview (the update_preview_image function handles BGR->RGB conversion)
            self.update_preview_image(img)
            
            # Log success
            self.log_message(f"Loaded external screenshot: {os.path.basename(file_path)}")
            
            # Automatically start selection mode
            self.start_exclusion_selection()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            self.log_message(f"Error loading image: {e}")
    
    def calculate_scaled_exclusion_zones(self):
        """Calculate scaled exclusion zones for display based on current canvas size"""
        self.scaled_exclusion_zones = []
        
        if not self.exclusion_zones or self.current_image is None:
            return
            
        h, w = self.current_image.shape[:2]
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Calculate scale used for display
        scale_w = canvas_width / w
        scale_h = canvas_height / h
        scale = min(scale_w, scale_h)
        
        # Calculate offset for centering
        new_w = int(w * scale)
        new_h = int(h * scale)
        x_offset = (canvas_width - new_w) // 2
        y_offset = (canvas_height - new_h) // 2
        
        # Transform each zone to canvas coordinates
        for x1, y1, x2, y2 in self.exclusion_zones:
            # Scale to canvas size
            x1_canvas = int(x1 * scale) + x_offset
            y1_canvas = int(y1 * scale) + y_offset
            x2_canvas = int(x2 * scale) + x_offset
            y2_canvas = int(y2 * scale) + y_offset
            
            self.scaled_exclusion_zones.append((x1_canvas, y1_canvas, x2_canvas, y2_canvas))
    
    def load_exclusion_zones(self):
        """Load exclusion zones from JSON file"""
        try:
            if os.path.exists(self.exclusion_file):
                with open(self.exclusion_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load exclusion zones
                    if 'excluded_areas' in data:
                        self.exclusion_zones = data['excluded_areas']
                        
                    # Load colors if available
                    if 'colors' in data:
                        self.exclusion_colors = data['colors']
                    else:
                        # Create default colors if none exist
                        self.exclusion_colors = ['#ff0000'] * len(self.exclusion_zones)
                    
                    # Update status label
                    if self.exclusion_zones:
                        self.exclusion_status.config(text=f"{len(self.exclusion_zones)} exclusion area(s) loaded")
                        self.log_message(f"Loaded {len(self.exclusion_zones)} exclusion zones from file")
                    
                    # Calculate scaled exclusion zones if we have a current image
                    if self.current_image is not None:
                        self.calculate_scaled_exclusion_zones()
                        self.update_preview_image(self.current_image)
        except Exception as e:
            self.log_message(f"Error loading exclusion zones: {e}")
    
    def save_exclusion_zones(self):
        """Save exclusion zones to JSON file"""
        if not self.exclusion_zones:
            messagebox.showinfo("Info", "No exclusion zones to save.")
            return
            
        try:
            # Ensure we have colors for all zones
            while len(self.exclusion_colors) < len(self.exclusion_zones):
                self.exclusion_colors.append('#ff0000')  # Default red for new zones
                
            # Create data structure to save
            data = {
                'excluded_areas': self.exclusion_zones,
                'colors': self.exclusion_colors[:len(self.exclusion_zones)]
            }
            
            # Save to file
            with open(self.exclusion_file, 'w') as f:
                json.dump(data, f)
                
            self.log_message(f"Saved {len(self.exclusion_zones)} exclusion zones to file")
            messagebox.showinfo("Success", f"Saved {len(self.exclusion_zones)} exclusion zones successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save exclusion zones: {e}")
            self.log_message(f"Error saving exclusion zones: {e}")
    
    # Detection and notification methods
    
    def get_detection_info(self, image):
        """Ekstrak informasi deteksi dari gambar hasil deteksi"""
        # Default info
        info = {
            'time': datetime.now(),
            'confidence': self.threshold_value.get(),
            'position': 'Unknown',
            'thumbnail': None
        }
        
        # Coba ekstrak kotak deteksi jika ada
        try:
            # Buat thumbnail dari gambar deteksi (fokus pada area deteksi)
            h, w = image.shape[:2]
            
            # Cari kotak deteksi hijau
            mask = np.zeros((h, w), dtype=np.uint8)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Range warna hijau (untuk kotak deteksi)
            lower_green = np.array([40, 100, 100])
            upper_green = np.array([80, 255, 255])
            
            # Dapatkan mask untuk warna hijau
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # Temukan kontur untuk bounding boxes
            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Ambil kontur terbesar (kemungkinan objek smartphone)
                c = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(c)
                
                # Update posisi di info
                # Format posisi: x,y (bagian mana dari layar - kiri/tengah/kanan, atas/tengah/bawah)
                x_pos = "left" if x < image.shape[1]/3 else "center" if x < 2*image.shape[1]/3 else "right"
                y_pos = "top" if y < image.shape[0]/3 else "middle" if y < 2*image.shape[0]/3 else "bottom"
                info['position'] = f"{x_pos}-{y_pos} ({x},{y})"
                
                # Gunakan gambar penuh sebagai thumbnail (tanpa crop)
                info['thumbnail'] = image.copy()
                
                # Ambil confidence dari nama kotak jika tersedia
                if hasattr(self, 'detector') and hasattr(self.detector, 'last_confidence'):
                    info['confidence'] = self.detector.last_confidence
            else:
                # Jika tidak ada smartphone terdeteksi, tetap gunakan gambar penuh
                info['thumbnail'] = image.copy()
        except Exception as e:
            print(f"Error extracting detection info: {e}")
            # Jika terjadi error, tetap gunakan gambar penuh
            info['thumbnail'] = image.copy()
            
        return info
    
    def show_notification(self, detection_info=None):
        """Show a popup notification for smartphone detection"""
        # Mainkan suara notifikasi
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except:
            pass  # Jika gagal, lanjut tanpa suara
        
        # Create a new window if it doesn't exist or was closed
        if not self.notification_window or not self.notification_window.winfo_exists():
            self.notification_window = tk.Toplevel(self.root)
            self.notification_window.title("⚠️ SMARTPHONE DETECTION ALERTS ⚠️")
            self.notification_window.geometry("550x600")
            self.notification_window.attributes('-topmost', True)  # Keep on top
            self.notification_window.resizable(True, True)  # Allow resizing
            self.notification_window.minsize(500, 400)  # Set minimum size
            
            # Create notebook (tab control)
            self.notification_tabs = ttk.Notebook(self.notification_window)
            self.notification_tabs.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Reset tab count
            self.tab_count = 0
        
        # Increment tab count for new tab
        self.tab_count += 1
        current_tab_id = self.tab_count
        
        # Create a new tab frame
        tab_frame = ttk.Frame(self.notification_tabs)
        
        # Add the new tab with a unique name
        detection_time = detection_info['time'] if detection_info else datetime.now()
        tab_title = f"Alert {current_tab_id} - {detection_time.strftime('%H:%M:%S')}"
        self.notification_tabs.add(tab_frame, text=tab_title)
        
        # Select the newly created tab
        self.notification_tabs.select(tab_frame)
        
        # Create main vertical layout frame
        main_layout = ttk.Frame(tab_frame)
        main_layout.pack(fill=tk.BOTH, expand=True)
        
        # Frame header dengan efek highlight
        header_frame = tk.Frame(main_layout, bg="#990000", height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=(10,0))
        
        # Judul alert dengan animasi berkedip
        title_frame = tk.Frame(header_frame, bg="#990000")
        title_frame.pack(pady=10)
        
        # Icon peringatan
        warning_label = tk.Label(
            title_frame,
            text="⚠️",
            font=("Arial", 32),
            bg="#990000",
            fg="yellow"
        )
        warning_label.pack(side=tk.LEFT, padx=(0,10))
        
        # Judul peringatan
        title_label = tk.Label(
            title_frame,
            text="SMARTPHONE DETECTED!",
            font=("Arial", 18, "bold"),
            bg="#990000",
            fg="white"
        )
        title_label.pack(side=tk.LEFT)
        
        # Buat title berkedip untuk menarik perhatian
        blink_state = True
        
        def blink_title():
            nonlocal blink_state
            if self.notification_window and self.notification_window.winfo_exists():
                blink_state = not blink_state
                title_label.configure(fg="yellow" if blink_state else "white")
                warning_label.configure(fg="white" if blink_state else "yellow")
                tab_frame.after(500, blink_title)
        
        # Mulai animasi berkedip
        blink_title()
        
        # Button bar at bottom - now separate from scrolling content
        button_frame = tk.Frame(main_layout, bg="white", padx=15, pady=10)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 10))
        
        # Create scrollable frame for content
        content_container = ttk.Frame(main_layout)
        content_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        content_canvas = tk.Canvas(content_container, bg="white")
        scrollbar = ttk.Scrollbar(content_container, orient=tk.VERTICAL, command=content_canvas.yview)
        content_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create frame for content inside canvas
        content_frame = tk.Frame(content_canvas, bg="white", padx=15, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create window in canvas to hold content frame
        content_canvas_window = content_canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        
        # Configure scrolling
        def configure_scroll_region(event):
            content_canvas.configure(scrollregion=content_canvas.bbox("all"))
            # Make sure content frame width matches canvas width
            content_canvas.itemconfig(content_canvas_window, width=content_canvas.winfo_width())
        
        content_frame.bind("<Configure>", configure_scroll_region)
        content_canvas.bind("<Configure>", lambda e: content_canvas.itemconfig(content_canvas_window, width=e.width))
        
        # Waktu deteksi
        detection_time = detection_info['time'] if detection_info else datetime.now()
        time_frame = tk.Frame(content_frame, bg="white")
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            time_frame, 
            text="Detection Time:", 
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(side=tk.LEFT)
        
        tk.Label(
            time_frame,
            text=detection_time.strftime("%Y-%m-%d %H:%M:%S"),
            font=("Arial", 10),
            bg="white",
            fg="#333333"
        ).pack(side=tk.RIGHT)
        
        # Confidence level
        conf_frame = tk.Frame(content_frame, bg="white")
        conf_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            conf_frame, 
            text="Confidence Level:", 
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(side=tk.LEFT)
        
        confidence = detection_info['confidence'] if detection_info else self.threshold_value.get()
        tk.Label(
            conf_frame,
            text=f"{confidence:.2f}",
            font=("Arial", 10),
            bg="white",
            fg="#333333"
        ).pack(side=tk.RIGHT)
        
        # Posisi smartphone pada layar
        pos_frame = tk.Frame(content_frame, bg="white")
        pos_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            pos_frame, 
            text="Screen Position:", 
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(side=tk.LEFT)
        
        position = detection_info['position'] if detection_info else "Unknown"
        tk.Label(
            pos_frame,
            text=position,
            font=("Arial", 10),
            bg="white",
            fg="#333333"
        ).pack(side=tk.RIGHT)
        
        # Separator
        ttk.Separator(content_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Alert message
        message_label = tk.Label(
            content_frame,
            text="A smartphone has been detected on your screen. This could indicate unauthorized device usage during your monitoring session.",
            font=("Arial", 10),
            bg="white",
            wraplength=380,
            justify=tk.LEFT
        )
        message_label.pack(pady=(0, 15), anchor='w')
        
        # Thumbnail preview jika tersedia
        if detection_info and detection_info['thumbnail'] is not None:
            thumbnail = detection_info['thumbnail']
            # Konversi OpenCV ke PIL dan kemudian ke PhotoImage
            h, w = thumbnail.shape[:2]
            
            # Batasi ukuran thumbnail tapi tetap lebih besar dari sebelumnya
            max_size = 350  # Meningkatkan ukuran maksimum thumbnail dari 200 menjadi 350
            if h > max_size or w > max_size:
                scale = min(max_size / h, max_size / w)
                h = int(h * scale)
                w = int(w * scale)
                thumbnail = cv2.resize(thumbnail, (w, h))
            
            # Buat frame untuk thumbnail
            thumb_frame = tk.Frame(content_frame, bg="white", bd=1, relief=tk.SUNKEN)
            thumb_frame.pack(pady=(0, 10))
            
            # Konversi format gambar dari BGR ke RGB untuk tampilan yang benar
            pil_img = Image.fromarray(cv2.cvtColor(thumbnail, cv2.COLOR_BGR2RGB))
            img_tk = ImageTk.PhotoImage(pil_img)
            
            # Simpan referensi untuk mencegah garbage collection
            thumb_frame.image = img_tk
            
            # Label untuk menampilkan thumbnail
            thumb_label = tk.Label(thumb_frame, image=img_tk, bd=0, cursor="hand2")
            thumb_label.pack(padx=2, pady=2)
            
            # Label caption
            tk.Label(
                content_frame,
                text="Detection Preview",
                font=("Arial", 8),
                bg="white",
                fg="#666666"
            ).pack()
            
            # Store full image for viewing
            full_image = detection_info['thumbnail'].copy()
            
            # Make thumbnail clickable to view full image
            thumb_label.bind("<Button-1>", lambda e, img=full_image: self.show_full_image(img))
            
            # Add View Full Image button
            view_full_btn = tk.Button(
                content_frame,
                text="View Full Image",
                command=lambda img=full_image: self.show_full_image(img),
                bg="#2979ff",
                fg="white",
                font=("Arial", 10, "bold"),
                relief=tk.GROOVE,
                borderwidth=2,
                padx=10,
                pady=5,
                cursor="hand2"
            )
            view_full_btn.pack(pady=(0, 15))
        
        # Tombol Close Tab dengan style lebih menarik
        close_tab_btn = tk.Button(
            button_frame,
            text="Close This Tab",
            command=lambda t=tab_frame: self.close_notification_tab(t),
            bg="#ff3333",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.GROOVE,
            borderwidth=4,
            padx=15,
            pady=8,
            cursor="hand2"  # Cursor berubah jadi tangan saat hover
        )
        close_tab_btn.pack(side=tk.RIGHT)
        
        # Hover effect for button
        def on_enter(e):
            close_tab_btn['bg'] = '#ff0000'
        
        def on_leave(e):
            close_tab_btn['bg'] = '#ff3333'
        
        close_tab_btn.bind("<Enter>", on_enter)
        close_tab_btn.bind("<Leave>", on_leave)
        
        # Tombol Close All di kiri
        close_all_btn = tk.Button(
            button_frame,
            text="Close All Tabs",
            command=lambda: self.notification_window.destroy(),
            bg="#555555",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.GROOVE,
            borderwidth=4,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        close_all_btn.pack(side=tk.LEFT)
    
    def close_notification_tab(self, tab):
        """Close a specific tab in the notification window"""
        if self.notification_tabs and tab:
            tab_id = self.notification_tabs.index(tab)
            self.notification_tabs.forget(tab_id)
            
            # If no more tabs, close the window
            if self.notification_tabs.index("end") == 0:
                self.notification_window.destroy()
                self.notification_window = None
    
    def show_full_image(self, image):
        """Display the full-sized detection image in a new window"""
        if image is None:
            return
            
        # Create a new window for the full image
        full_img_window = tk.Toplevel(self.root)
        full_img_window.title("Full Detection Image")
        full_img_window.attributes('-topmost', True)  # Keep on top
        
        # Get screen dimensions for sizing the window
        screen_width = full_img_window.winfo_screenwidth()
        screen_height = full_img_window.winfo_screenheight()
        
        # Set window size to 80% of screen dimensions
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        full_img_window.geometry(f"{window_width}x{window_height}")
        
        # Convert OpenCV image to PIL and then to PhotoImage
        h, w = image.shape[:2]
        
        # Calculate scale to fit window
        scale = min(window_width / w, window_height / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        # Resize the image
        resized_img = cv2.resize(image, (new_w, new_h))
        # Convert BGR to RGB for correct color display
        pil_img = Image.fromarray(cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB))
        img_tk = ImageTk.PhotoImage(pil_img)
        
        # Create canvas to display the image
        canvas = tk.Canvas(full_img_window, width=window_width, height=window_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Store reference to prevent garbage collection
        canvas.image = img_tk
        
        # Calculate position to center the image
        x_pos = (window_width - new_w) // 2
        y_pos = (window_height - new_h) // 2
        
        # Display image on canvas
        canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=img_tk)
        
        # Add close button at the bottom
        close_btn = tk.Button(
            full_img_window,
            text="Close",
            command=full_img_window.destroy,
            bg="#ff3333",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.GROOVE,
            borderwidth=4,
            padx=15,
            pady=5
        )
        close_btn.pack(pady=10) 