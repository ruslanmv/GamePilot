"""
YOLO-based object detection for game entities (enemies, loot, NPCs, HUD elements).
Uses Ultralytics YOLOv8 for fast real-time detection.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class YOLOGameDetector:
    """
    YOLO-based detector for game entities.
    
    Detects:
    - Enemies (enemy)
    - Loot/items (loot)
    - NPCs (npc)
    - Quest markers (quest_marker)
    - HUD elements (hp_bar, mp_bar, minimap)
    """
    
    # Expected class names (can be customized per game)
    DEFAULT_CLASSES = [
        "enemy",
        "loot",
        "npc",
        "quest_marker",
        "hp_bar",
        "mp_bar",
        "minimap",
        "inventory_icon",
    ]
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = "cpu",
    ):
        """
        Initialize YOLO detector.
        
        Args:
            model_path: Path to trained YOLO model (.pt file)
                       If None, uses pretrained YOLO-NAS-S (general object detection)
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
            device: Device to run on ('cpu' or 'cuda')
        """
        if not YOLO_AVAILABLE:
            raise ImportError(
                "ultralytics not installed. Install with: pip install ultralytics\n"
                "Or use MockDetector for testing."
            )
        
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        
        # Load model
        if model_path and Path(model_path).exists():
            self.model = YOLO(model_path)
        else:
            # Use pretrained YOLOv8n as fallback (fast, lightweight)
            # In production, you'd train on game-specific data
            print("Warning: No custom model found, using pretrained YOLOv8n")
            print("For game-specific detection, train a custom model and pass model_path")
            self.model = YOLO("yolov8n.pt")
        
        self.model.to(device)
        
    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Run detection on a frame.
        
        Args:
            frame: RGB image (H, W, 3)
            
        Returns:
            dict: Detection results with counts and bounding boxes
        """
        # Run inference
        results = self.model(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False,
        )[0]
        
        # Parse results
        detections = {
            "enemy_near": False,
            "loot_visible": False,
            "npc_visible": False,
            "quest_marker": "unknown",
            "hp": 100,  # Default, will be overridden by OCR
            "mp": 100,
            "detections": [],
        }
        
        if results.boxes is not None and len(results.boxes) > 0:
            boxes = results.boxes.cpu().numpy()
            
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0]
                
                # Get class name
                class_name = results.names[cls_id] if cls_id < len(results.names) else f"class_{cls_id}"
                
                detection = {
                    "class": class_name,
                    "confidence": conf,
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "center": [float((x1 + x2) / 2), float((y1 + y2) / 2)],
                }
                
                detections["detections"].append(detection)
                
                # Update state flags based on detections
                if "enemy" in class_name.lower() or "monster" in class_name.lower():
                    detections["enemy_near"] = True
                elif "loot" in class_name.lower() or "item" in class_name.lower():
                    detections["loot_visible"] = True
                elif "npc" in class_name.lower() or "character" in class_name.lower():
                    detections["npc_visible"] = True
                elif "quest" in class_name.lower() or "marker" in class_name.lower():
                    # Determine direction based on position
                    frame_h, frame_w = frame.shape[:2]
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    
                    if center_x < frame_w * 0.33:
                        detections["quest_marker"] = "west"
                    elif center_x > frame_w * 0.66:
                        detections["quest_marker"] = "east"
                    elif center_y < frame_h * 0.33:
                        detections["quest_marker"] = "north"
                    elif center_y > frame_h * 0.66:
                        detections["quest_marker"] = "south"
                    else:
                        detections["quest_marker"] = "center"
        
        return detections
    
    def detect_with_visualization(self, frame: np.ndarray) -> Tuple[Dict[str, Any], np.ndarray]:
        """
        Run detection and return both results and annotated frame.
        
        Args:
            frame: RGB image
            
        Returns:
            tuple: (detections dict, annotated frame)
        """
        # Run inference
        results = self.model(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False,
        )[0]
        
        # Get annotated frame
        annotated = results.plot()
        
        # Parse detections (same as detect())
        detections = self.detect(frame)
        
        return detections, annotated
    
    def update_thresholds(self, conf: Optional[float] = None, iou: Optional[float] = None):
        """Update detection thresholds."""
        if conf is not None:
            self.conf_threshold = conf
        if iou is not None:
            self.iou_threshold = iou


class MockDetectorYOLO:
    """Mock detector for testing when YOLO is not available."""
    
    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """Return mock detections."""
        return {
            "enemy_near": False,
            "loot_visible": False,
            "npc_visible": False,
            "quest_marker": "north",
            "hp": 75,
            "mp": 80,
            "detections": [],
        }
    
    def detect_with_visualization(self, frame: np.ndarray) -> Tuple[Dict[str, Any], np.ndarray]:
        """Return mock detections and original frame."""
        return self.detect(frame), frame


def create_yolo_detector(
    model_path: Optional[str] = None,
    conf: float = 0.5,
    device: str = "cpu",
) -> YOLOGameDetector:
    """
    Factory function to create YOLO detector with fallback to mock.
    
    Args:
        model_path: Path to custom model
        conf: Confidence threshold
        device: 'cpu' or 'cuda'
        
    Returns:
        YOLOGameDetector or MockDetectorYOLO
    """
    if YOLO_AVAILABLE:
        try:
            return YOLOGameDetector(model_path=model_path, conf_threshold=conf, device=device)
        except Exception as e:
            print(f"Failed to initialize YOLO detector: {e}")
            print("Falling back to MockDetector")
            return MockDetectorYOLO()
    else:
        print("YOLO not available, using MockDetector")
        return MockDetectorYOLO()


if __name__ == "__main__":
    # Test detector
    import cv2
    
    print("YOLO Detector Test")
    print(f"YOLO available: {YOLO_AVAILABLE}")
    
    if YOLO_AVAILABLE:
        # Create detector
        detector = create_yolo_detector(device="cpu")
        
        # Test on webcam or sample image
        print("\nTesting on webcam feed (press Q to quit)...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Webcam not available, using blank test frame")
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            results = detector.detect(test_frame)
            print(f"\nDetection results: {results}")
        else:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect with visualization
                detections, annotated = detector.detect_with_visualization(frame_rgb)
                
                # Convert back to BGR for display
                annotated_bgr = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
                
                # Add detection summary
                y_offset = 30
                for key in ["enemy_near", "loot_visible", "npc_visible"]:
                    text = f"{key}: {detections[key]}"
                    cv2.putText(
                        annotated_bgr,
                        text,
                        (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )
                    y_offset += 25
                
                cv2.imshow("YOLO Game Detection", annotated_bgr)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
    else:
        print("\nInstall ultralytics to enable YOLO detection:")
        print("pip install ultralytics")
