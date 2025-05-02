import os
import cv2
import numpy as np
from ultralytics import YOLO

class SmartphoneDetector:
    def __init__(self, model_path):
        """
        Initialize the smartphone detector
        Args:
            model_path: Path to the YOLOv8 .pt model file
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load the YOLOv8 model
        self.model = YOLO(model_path)
        self.detection_count = 0
        self.last_detection_time = 0
        self.smartphone_detected = False
        self.last_confidence = 0.0  # Untuk melacak confidence level terakhir
        self.last_detections = []   # Untuk menyimpan bounding box hasil deteksi
        
        # Threshold untuk confidence (nilai antara 0-1)
        # Nilai lebih tinggi = lebih ketat/selektif
        self.confidence_threshold = 0.5  # Meningkatkan dari 0.25 ke 0.5
    
    def detect_smartphone(self, image, exclusion_zones=None):
        """
        Detect smartphones in the given image
        Args:
            image: Image as numpy array (from screen capture)
            exclusion_zones: List of tuples (x1,y1,x2,y2) yang merupakan area yang dikecualikan
        Returns:
            Boolean indicating if a smartphone was detected and the image with detection boxes
        """
        # Make sure the image is in the right format (RGB)
        if image.shape[-1] == 4:  # RGBA to RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        
        # Run detection with threshold yang lebih tinggi
        results = self.model(image, conf=self.confidence_threshold)  # Menggunakan threshold dari class variable
        
        # Process results
        result_image = image.copy()
        
        # Check if any smartphone was detected
        smartphones_found = False
        smartphones_outside_exclusion = False  # Flag untuk smartphone di luar exclusion zone
        max_conf = 0.0  # Untuk melacak confidence tertinggi
        detected_boxes = []  # Untuk menyimpan semua bounding box
        
        if results and len(results) > 0:
            # Get the predictions from the first result
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get class index
                    cls_id = int(box.cls.item())
                    # Get confidence score
                    conf = box.conf.item()
                    
                    # Get class name jika tersedia
                    class_name = result.names[cls_id] if hasattr(result, 'names') and result.names else f"Class {cls_id}"
                    
                    # Check if it's a smartphone with sufficient confidence
                    if conf > self.confidence_threshold:  # Menggunakan threshold yang sama
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Check if this detection is in any exclusion zone
                        in_exclusion_zone = False
                        if exclusion_zones:
                            # Calculate center of the detection
                            center_x = (x1 + x2) / 2
                            center_y = (y1 + y2) / 2
                            
                            # Check if center is in any exclusion zone
                            for ex_x1, ex_y1, ex_x2, ex_y2 in exclusion_zones:
                                if (ex_x1 <= center_x <= ex_x2 and ex_y1 <= center_y <= ex_y2):
                                    in_exclusion_zone = True
                                    break
                        
                        # Mark that smartphone was found (regardless of exclusion)
                        smartphones_found = True
                        
                        # Store detection info
                        detected_boxes.append((x1, y1, x2, y2, conf, cls_id, in_exclusion_zone))
                        
                        # Track highest confidence
                        if conf > max_conf:
                            max_conf = conf
                        
                        # Only draw if not in exclusion zone
                        if not in_exclusion_zone:
                            smartphones_outside_exclusion = True
                            
                            # Draw bounding box
                            cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            
                            # Add label dengan nama class dan confidence
                            label = f"{class_name}: {conf:.2f}"
                            cv2.putText(
                                result_image,
                                label,
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0),
                                2
                            )
                        else:
                            # Draw dashed bounding box with different color for excluded detections
                            cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 0, 255), 3)
                            
                            # Add "EXCLUDED" label
                            cv2.putText(
                                result_image,
                                "EXCLUDED",
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 0, 255),
                                1
                            )
        
        # Update detection state
        self.smartphone_detected = smartphones_found
        self.last_detections = detected_boxes  # Simpan semua box deteksi
        
        if smartphones_found:
            self.detection_count += 1
            self.last_confidence = max_conf  # Simpan confidence tertinggi
        
        # Return True only if there are smartphones outside exclusion zones
        return smartphones_outside_exclusion, result_image
        
    def set_confidence_threshold(self, value):
        """
        Set the confidence threshold for detection
        Args:
            value: Threshold value between 0 and 1
        """
        if 0 <= value <= 1:
            self.confidence_threshold = value
            return True
        return False 