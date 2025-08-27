"""Computer Vision: object detection, scene analysis, content moderation."""

import cv2
import numpy as np
from typing import Dict, List, Tuple


class VisionProcessor:
    def __init__(self):
        # Initialize with basic OpenCV cascades for face/object detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def detect_faces(self, image_path: str) -> Dict:
        """Detect faces in image."""
        img = cv2.imread(image_path)
        if img is None:
            return {"faces": [], "face_count": 0}
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        face_data = []
        for (x, y, w, h) in faces:
            face_info = {
                "bbox": [int(x), int(y), int(w), int(h)],
                "center": [int(x + w/2), int(y + h/2)],
                "area": int(w * h),
                "confidence": 0.8  # Placeholder confidence
            }
            
            # Detect eyes within face region
            face_roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(face_roi_gray)
            face_info["eyes_detected"] = len(eyes)
            
            face_data.append(face_info)
        
        return {
            "faces": face_data,
            "face_count": len(faces),
            "has_people": len(faces) > 0
        }

    def analyze_scene(self, image_path: str) -> Dict:
        """Basic scene analysis."""
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Could not load image"}
        
        height, width = img.shape[:2]
        
        # Color analysis
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Dominant color analysis
        colors = cv2.split(img)
        color_means = [float(np.mean(c)) for c in colors]
        
        # Brightness and contrast
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        contrast = float(np.std(gray))
        
        # Edge detection for complexity
        edges = cv2.Canny(gray, 50, 150)
        edge_density = float(np.sum(edges > 0) / (width * height))
        
        # Basic scene classification based on color distribution
        scene_type = self._classify_scene_type(hsv, color_means, brightness)
        
        return {
            "scene_type": scene_type,
            "brightness": brightness,
            "contrast": contrast,
            "edge_density": edge_density,
            "color_distribution_bgr": color_means,
            "image_complexity": "high" if edge_density > 0.1 else "medium" if edge_density > 0.05 else "low"
        }

    def _classify_scene_type(self, hsv_img: np.ndarray, color_means: List[float], brightness: float) -> str:
        """Simple scene classification."""
        # Basic heuristics for scene classification
        blue_dominant = color_means[0] > color_means[1] and color_means[0] > color_means[2]  # B channel
        green_dominant = color_means[1] > color_means[0] and color_means[1] > color_means[2]  # G channel
        
        if brightness < 50:
            return "indoor_low_light"
        elif brightness > 180:
            return "outdoor_bright"
        elif green_dominant:
            return "nature_outdoor"
        elif blue_dominant:
            return "sky_water"
        else:
            return "indoor_general"

    def detect_objects(self, image_path: str) -> Dict:
        """Basic object detection using contours and shapes."""
        img = cv2.imread(image_path)
        if img is None:
            return {"objects": [], "object_count": 0}
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        objects = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Filter small objects
                x, y, w, h = cv2.boundingRect(contour)
                
                # Basic shape classification
                approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                shape = self._classify_shape(len(approx))
                
                objects.append({
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "area": int(area),
                    "shape": shape,
                    "aspect_ratio": round(w / h, 2) if h > 0 else 0
                })
        
        return {
            "objects": objects[:10],  # Limit to top 10 objects
            "object_count": len(objects),
            "detection_method": "contour_based"
        }

    def _classify_shape(self, vertex_count: int) -> str:
        """Classify shape based on vertex count."""
        if vertex_count == 3:
            return "triangle"
        elif vertex_count == 4:
            return "rectangle"
        elif vertex_count == 5:
            return "pentagon"
        elif vertex_count > 10:
            return "circle"
        else:
            return f"polygon_{vertex_count}"

    def content_safety_check(self, image_path: str) -> Dict:
        """Basic content safety analysis."""
        img = cv2.imread(image_path)
        if img is None:
            return {"safe": True, "reason": "Could not analyze image"}
        
        # Simple heuristics for content safety
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        # Very basic checks
        is_too_dark = brightness < 30  # Might indicate inappropriate content
        
        # Face detection for inappropriate content (very basic)
        faces = self.detect_faces(image_path)
        has_multiple_faces = faces["face_count"] > 5
        
        # Edge density check (very high might indicate inappropriate content)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (img.shape[0] * img.shape[1])
        high_complexity = edge_density > 0.15
        
        safety_score = 0.9  # Default high safety
        warnings = []
        
        if is_too_dark:
            safety_score -= 0.2
            warnings.append("very_dark_image")
        
        if has_multiple_faces:
            safety_score -= 0.1
            warnings.append("multiple_people")
        
        if high_complexity:
            safety_score -= 0.1
            warnings.append("high_visual_complexity")
        
        return {
            "safe": safety_score > 0.5,
            "safety_score": max(0.0, min(1.0, safety_score)),
            "warnings": warnings,
            "analysis_method": "basic_heuristics"
        }
