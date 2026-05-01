"""
OCR reader for extracting text from game HUD elements (HP, MP, resources, quest text).
Uses EasyOCR for robust text detection and recognition.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import re

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


class HUDReader:
    """
    OCR-based reader for game HUD elements.
    
    Can extract:
    - HP/MP values (e.g., "HP: 75/100")
    - Resource counts (e.g., "Gold: 1234")
    - Level/XP (e.g., "Level 45", "XP: 12350/15000")
    - Quest text
    """
    
    def __init__(
        self,
        languages: List[str] = ['en'],
        gpu: bool = False,
    ):
        """
        Initialize OCR reader.
        
        Args:
            languages: List of language codes (e.g., ['en', 'it'])
            gpu: Whether to use GPU acceleration
        """
        if not EASYOCR_AVAILABLE:
            raise ImportError(
                "easyocr not installed. Install with: pip install easyocr\n"
                "Or use mock detector for testing."
            )
        
        print(f"Initializing EasyOCR for languages: {languages}")
        print(f"GPU enabled: {gpu}")
        
        self.reader = easyocr.Reader(languages, gpu=gpu)
        self.gpu = gpu
        
    def read_text(self, image: np.ndarray, detail: int = 0) -> List[Tuple]:
        """
        Extract all text from an image.
        
        Args:
            image: RGB image
            detail: 0 = bounding box coordinates + text
                   1 = detailed info (box, text, confidence)
                   
        Returns:
            list: Detected text regions
        """
        results = self.reader.readtext(image, detail=detail)
        return results
    
    def read_region(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> List[Tuple]:
        """
        Read text from a specific region of the image.
        
        Args:
            image: Full RGB image
            x, y: Top-left coordinates
            width, height: Region dimensions
            
        Returns:
            list: Detected text in the region
        """
        # Extract region
        region = image[y:y+height, x:x+width]
        return self.read_text(region)
    
    def extract_hp_mp(
        self,
        image: np.ndarray,
        hp_region: Optional[Tuple[int, int, int, int]] = None,
        mp_region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Dict[str, int]:
        """
        Extract HP and MP values from predefined regions.
        
        Args:
            image: RGB image
            hp_region: (x, y, width, height) for HP bar text
            mp_region: (x, y, width, height) for MP bar text
            
        Returns:
            dict: {"hp": value, "mp": value, "hp_max": value, "mp_max": value}
        """
        result = {
            "hp": 100,
            "hp_max": 100,
            "mp": 100,
            "mp_max": 100,
        }
        
        # Read HP
        if hp_region:
            x, y, w, h = hp_region
            hp_text_results = self.read_region(image, x, y, w, h)
            hp_value = self._parse_hp_mp_text(hp_text_results)
            if hp_value:
                result["hp"] = hp_value.get("current", 100)
                result["hp_max"] = hp_value.get("max", 100)
        
        # Read MP
        if mp_region:
            x, y, w, h = mp_region
            mp_text_results = self.read_region(image, x, y, w, h)
            mp_value = self._parse_hp_mp_text(mp_text_results)
            if mp_value:
                result["mp"] = mp_value.get("current", 100)
                result["mp_max"] = mp_value.get("max", 100)
        
        return result
    
    def extract_resources(
        self,
        image: np.ndarray,
        resource_regions: Dict[str, Tuple[int, int, int, int]]
    ) -> Dict[str, int]:
        """
        Extract resource counts (gold, items, etc.).
        
        Args:
            image: RGB image
            resource_regions: {"resource_name": (x, y, w, h)}
            
        Returns:
            dict: {"resource_name": count}
        """
        resources = {}
        
        for name, region in resource_regions.items():
            x, y, w, h = region
            text_results = self.read_region(image, x, y, w, h)
            
            # Extract numbers from text
            for result in text_results:
                text = result[1] if len(result) > 1 else ""
                numbers = re.findall(r'\d+', text)
                if numbers:
                    resources[name] = int(numbers[0])
                    break
        
        return resources
    
    def _parse_hp_mp_text(self, text_results: List[Tuple]) -> Optional[Dict[str, int]]:
        """
        Parse HP/MP text like "75/100" or "HP: 75" or "75".
        
        Args:
            text_results: OCR results
            
        Returns:
            dict: {"current": value, "max": value} or None
        """
        if not text_results:
            return None
        
        # Concatenate all detected text
        full_text = " ".join([result[1] if len(result) > 1 else "" for result in text_results])
        
        # Try to find "X/Y" pattern
        slash_pattern = r'(\d+)\s*/\s*(\d+)'
        match = re.search(slash_pattern, full_text)
        if match:
            return {
                "current": int(match.group(1)),
                "max": int(match.group(2)),
            }
        
        # Try to find standalone number
        number_pattern = r'(\d+)'
        match = re.search(number_pattern, full_text)
        if match:
            value = int(match.group(1))
            return {
                "current": value,
                "max": 100,  # Assume max is 100 if not specified
            }
        
        return None


class MockHUDReader:
    """Mock HUD reader for testing when EasyOCR is not available."""
    
    def read_text(self, image: np.ndarray, detail: int = 0) -> List[Tuple]:
        """Return empty results."""
        return []
    
    def read_region(self, image: np.ndarray, x: int, y: int, width: int, height: int) -> List[Tuple]:
        """Return empty results."""
        return []
    
    def extract_hp_mp(
        self,
        image: np.ndarray,
        hp_region: Optional[Tuple[int, int, int, int]] = None,
        mp_region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Dict[str, int]:
        """Return default values."""
        return {
            "hp": 100,
            "hp_max": 100,
            "mp": 100,
            "mp_max": 100,
        }
    
    def extract_resources(
        self,
        image: np.ndarray,
        resource_regions: Dict[str, Tuple[int, int, int, int]]
    ) -> Dict[str, int]:
        """Return empty dict."""
        return {}


def create_hud_reader(languages: List[str] = ['en'], gpu: bool = False) -> HUDReader:
    """
    Factory function to create HUD reader with fallback to mock.
    
    Args:
        languages: Language codes for OCR
        gpu: Whether to use GPU
        
    Returns:
        HUDReader or MockHUDReader
    """
    if EASYOCR_AVAILABLE:
        try:
            return HUDReader(languages=languages, gpu=gpu)
        except Exception as e:
            print(f"Failed to initialize HUDReader: {e}")
            print("Falling back to MockHUDReader")
            return MockHUDReader()
    else:
        print("EasyOCR not available, using MockHUDReader")
        return MockHUDReader()


if __name__ == "__main__":
    # Test HUD reader
    import cv2
    
    print("HUD Reader Test")
    print(f"EasyOCR available: {EASYOCR_AVAILABLE}")
    
    if EASYOCR_AVAILABLE:
        # Create reader
        reader = create_hud_reader(languages=['en'], gpu=False)
        
        # Test on sample text
        print("\nCreating test image with HP/MP text...")
        
        # Create a test image with text
        test_img = np.ones((100, 400, 3), dtype=np.uint8) * 255
        cv2.putText(
            test_img,
            "HP: 75/100",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 0),
            2
        )
        cv2.putText(
            test_img,
            "MP: 50/80",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 0),
            2
        )
        
        # Read all text
        print("\nReading text from image...")
        results = reader.read_text(test_img)
        print(f"Detected text: {results}")
        
        # Extract HP/MP
        print("\nExtracting HP/MP...")
        hp_mp = reader.extract_hp_mp(
            test_img,
            hp_region=(0, 0, 200, 50),
            mp_region=(0, 50, 200, 50)
        )
        print(f"HP/MP values: {hp_mp}")
        
        cv2.imshow("Test Image", test_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("\nInstall easyocr to enable HUD reading:")
        print("pip install easyocr")
