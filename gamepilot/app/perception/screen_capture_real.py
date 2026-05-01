"""
Real-time screen capture module using mss (cross-platform).
Falls back to mock mode if mss is not available.
"""
from typing import Any, Optional
import numpy as np

try:
    import mss
    import mss.tools
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


class ScreenCapture:
    """Real-time screen capture using mss."""
    
    def __init__(self, monitor: Optional[int] = None):
        """
        Initialize screen capture.
        
        Args:
            monitor: Monitor number to capture (None = primary monitor)
        """
        if not MSS_AVAILABLE:
            raise ImportError(
                "mss not installed. Install with: pip install mss\n"
                "Or run in demo mode using video files."
            )
        
        self.sct = mss.mss()
        self.monitor = monitor if monitor is not None else 1
        self.monitor_info = self.sct.monitors[self.monitor]
        
    def capture(self) -> np.ndarray:
        """
        Capture current screen as numpy array.
        
        Returns:
            np.ndarray: RGB image of shape (H, W, 3)
        """
        # Capture screen
        sct_img = self.sct.grab(self.monitor_info)
        
        # Convert to numpy array (BGRA format from mss)
        img = np.array(sct_img)
        
        # Convert BGRA to RGB
        img = img[:, :, :3]  # Drop alpha channel
        img = img[:, :, ::-1]  # BGR to RGB
        
        return img
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        Capture a specific region of the screen.
        
        Args:
            x: Left coordinate
            y: Top coordinate
            width: Region width
            height: Region height
            
        Returns:
            np.ndarray: RGB image of the region
        """
        region = {
            "left": x,
            "top": y,
            "width": width,
            "height": height,
        }
        
        sct_img = self.sct.grab(region)
        img = np.array(sct_img)
        img = img[:, :, :3]  # Drop alpha
        img = img[:, :, ::-1]  # BGR to RGB
        
        return img
    
    def get_monitor_info(self) -> dict:
        """Get information about the current monitor."""
        return self.monitor_info.copy()
    
    def list_monitors(self) -> list:
        """List all available monitors."""
        return self.sct.monitors
    
    def close(self):
        """Release screen capture resources."""
        if hasattr(self, 'sct'):
            self.sct.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Backward compatibility functions
def capture_screen() -> np.ndarray:
    """
    Capture the primary monitor.
    
    Returns:
        np.ndarray: RGB image
    """
    if MSS_AVAILABLE:
        with ScreenCapture() as sc:
            return sc.capture()
    else:
        # Fallback to mock for testing
        return np.zeros((480, 640, 3), dtype=np.uint8)


def capture_screen_region(x: int, y: int, width: int, height: int) -> np.ndarray:
    """
    Capture a specific region of the primary monitor.
    
    Args:
        x, y: Top-left corner coordinates
        width, height: Region dimensions
        
    Returns:
        np.ndarray: RGB image of the region
    """
    if MSS_AVAILABLE:
        with ScreenCapture() as sc:
            return sc.capture_region(x, y, width, height)
    else:
        # Fallback to mock
        return np.zeros((height, width, 3), dtype=np.uint8)


# FPS monitoring
class FPSMonitor:
    """Monitor and track capture FPS."""
    
    def __init__(self, window_size: int = 30):
        """
        Args:
            window_size: Number of frames to average over
        """
        import time
        self.window_size = window_size
        self.frame_times = []
        self.last_time = time.time()
        
    def tick(self) -> float:
        """
        Record a frame and return current FPS.
        
        Returns:
            float: Current FPS
        """
        import time
        current_time = time.time()
        delta = current_time - self.last_time
        self.last_time = current_time
        
        self.frame_times.append(delta)
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
        
        if not self.frame_times:
            return 0.0
        
        avg_delta = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_delta if avg_delta > 0 else 0.0


if __name__ == "__main__":
    # Test screen capture
    import cv2
    
    print("Screen Capture Test")
    print(f"mss available: {MSS_AVAILABLE}")
    
    if not MSS_AVAILABLE:
        print("Install mss to enable real screen capture: pip install mss")
    else:
        with ScreenCapture() as sc:
            print(f"\nMonitor info: {sc.get_monitor_info()}")
            print(f"All monitors: {sc.list_monitors()}")
            
            # Capture and display
            fps_monitor = FPSMonitor()
            
            print("\nCapturing screen for 5 seconds (press Q to quit)...")
            import time
            start = time.time()
            
            while time.time() - start < 5:
                img = sc.capture()
                fps = fps_monitor.tick()
                
                # Resize for display
                display_img = cv2.resize(img, (960, 540))
                
                # Add FPS overlay
                cv2.putText(
                    display_img,
                    f"FPS: {fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2
                )
                
                cv2.imshow("GamePilot Screen Capture", display_img)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cv2.destroyAllWindows()
            print(f"\nFinal FPS: {fps:.1f}")
