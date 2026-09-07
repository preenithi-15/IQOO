from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class VisualDetection:
    detected_species: str
    taxonomic_group: str  # Insecta, Aves, Plantae, Fungi
    confidence: float
    context_role: str     # POLLINATOR, HOST_PLANT, PREDATOR, HABITAT
    bounding_box: List[float]

class VisionClassifier:
    """Edge vision classifier identifying flora, fauna, and pollinator relationships."""
    
    def classify_frame(self, frame_objects: list) -> List[VisualDetection]:
        results = []
        for obj in frame_objects:
            lbl = obj.get("label", "unknown")
            conf = obj.get("confidence", 0.5)
            bbox = obj.get("bbox", [0.0, 0.0, 1.0, 1.0])
            
            if "bee" in lbl:
                results.append(VisualDetection(
                    detected_species="Apis mellifera (Western Honeybee)",
                    taxonomic_group="Insecta",
                    confidence=conf,
                    context_role="POLLINATOR",
                    bounding_box=bbox
                ))
            elif "cricket" in lbl:
                results.append(VisualDetection(
                    detected_species="Oecanthus fultoni (Tree Cricket)",
                    taxonomic_group="Insecta",
                    confidence=conf,
                    context_role="COMMUNICATOR",
                    bounding_box=bbox
                ))
            elif "bat" in lbl:
                results.append(VisualDetection(
                    detected_species="Pipistrellus pipistrellus (Common Pipistrelle)",
                    taxonomic_group="Mammalia",
                    confidence=conf,
                    context_role="AERIAL_FORAGER",
                    bounding_box=bbox
                ))
            elif "lavender" in lbl or "flower" in lbl:
                results.append(VisualDetection(
                    detected_species="Lavandula angustifolia (English Lavender)",
                    taxonomic_group="Plantae",
                    confidence=conf,
                    context_role="HOST_PLANT",
                    bounding_box=bbox
                ))
            else:
                results.append(VisualDetection(
                    detected_species="General Botanical Habitat",
                    taxonomic_group="Plantae",
                    confidence=conf,
                    context_role="HABITAT",
                    bounding_box=bbox
                ))
        return results
