import time
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class CameraFrame:
    frame_id: int
    timestamp: float
    width: int
    height: int
    detected_objects: list
    scene_description: str
    dominant_colors: list

class VisionCapture:
    """
    iQOO 15 Triple 50MP Camera interface simulation and capture pipeline.
    Captures high-resolution macro frames of pollinators, flowers, and canopies.
    """
    
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.frame_count = 0

    def capture_frame(self, scene_preset: Optional[str] = None) -> CameraFrame:
        """Captures a camera frame with metadata and optical features."""
        self.frame_count += 1
        now = time.time()
        
        if scene_preset == "honeybee":
            objects = [{"label": "honeybee", "confidence": 0.94, "bbox": [0.42, 0.38, 0.58, 0.52]}]
            scene = "Honeybee (Apis mellifera) hovering over yellow flowering plant."
            colors = ["#F4D03F", "#27AE60", "#784212"]
        elif scene_preset == "cricket":
            objects = [{"label": "tree_cricket", "confidence": 0.89, "bbox": [0.35, 0.50, 0.50, 0.65]}]
            scene = "Tree cricket perched beneath broad leaf surface."
            colors = ["#2ECC71", "#1E8449", "#D4AC0D"]
        elif scene_preset == "bat":
            objects = [{"label": "pipistrelle_bat", "confidence": 0.86, "bbox": [0.20, 0.15, 0.35, 0.30]}]
            scene = "Microbat in crepuscular flight against dusk canopy."
            colors = ["#17202A", "#2C3E50", "#566573"]
        elif scene_preset == "flower_only":
            objects = [{"label": "flowering_lavender", "confidence": 0.96, "bbox": [0.25, 0.20, 0.75, 0.80]}]
            scene = "Vibrant flowering lavender bush in direct sunlight."
            colors = ["#8E44AD", "#27AE60", "#F7DC6F"]
        else:
            objects = [{"label": "foliage", "confidence": 0.75, "bbox": [0.1, 0.1, 0.9, 0.9]}]
            scene = "Lush botanical foliage with natural daylight diffusion."
            colors = ["#1E8449", "#27AE60", "#52BE80"]

        return CameraFrame(
            frame_id=self.frame_count,
            timestamp=now,
            width=self.width,
            height=self.height,
            detected_objects=objects,
            scene_description=scene,
            dominant_colors=colors
        )
