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

    def analyze_pixels(self, rgba_array: List[int], width: int, height: int) -> Dict[str, Any]:
        """
        Analyzes raw RGBA pixel buffers from mobile camera capture for botanical flora,
        floral petal chrominance, and insect/pollinator signatures.
        """
        import numpy as np
        if not rgba_array or width <= 0 or height <= 0:
            return {"category": "non_botanical", "confidence": 0.3, "label": "No image data", "reason": "empty_frame"}

        arr = np.array(rgba_array, dtype=np.float32).reshape((height, width, 4))
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        total_pixels = float(width * height)

        # 1. Edge & Texture complexity (gradients to detect non-nature flat walls / floors)
        gx = np.diff(r + g + b, axis=1)
        gy = np.diff(r + g + b, axis=0)
        edge_variance = float(np.var(gx) + np.var(gy))

        # 2. Excess Green Vegetation Index: ExG = 2G - R - B
        total_rgb = r + g + b + 1e-5
        exg = (2.0 * g - r - b) / total_rgb
        green_foliage_ratio = float(np.sum((exg > 0.12) & (g > 40.0)) / total_pixels)

        # 3. Floral Petal Chrominance (Yellow, Violet, Magenta, Red, White petals)
        # Yellow petals (R and G high, B low)
        yellow_petals = (r > 130) & (g > 110) & (b < 100) & (r + g > 2.2 * b)
        # Violet / Purple / Magenta petals (R and B high, G lower)
        purple_petals = (r > 90) & (b > 110) & (g < r * 0.9) & (g < b * 0.9)
        # Bright warm petals (Red / Pink / Orange)
        warm_petals = (r > 140) & (g < r * 0.8) & (b < r * 0.8)
        # White blossoms in botanical context
        white_blossoms = (r > 180) & (g > 180) & (b > 180) & (green_foliage_ratio > 0.15)
        
        floral_mask = yellow_petals | purple_petals | warm_petals | white_blossoms
        floral_ratio = float(np.sum(floral_mask) / total_pixels)

        # 4. Insect / Pollinator contrast on foliage (dark high-contrast clusters)
        dark_clusters = (r < 55) & (g < 55) & (b < 55)
        insect_contrast = float(np.sum(dark_clusters & (exg < 0.05)) / total_pixels)

        # Decision engine
        # Blank / indoor / flat surface rejection:
        if edge_variance < 35.0 and green_foliage_ratio < 0.10 and floral_ratio < 0.04:
            return {
                "category": "non_botanical",
                "confidence": 0.85,
                "label": "Non-botanical / Flat surface",
                "species": "Indoor or untextured background",
                "reason": "Scene lacks botanical structure, foliage, or floral pigmentation."
            }

        # Floral blossom detection:
        if floral_ratio > 0.06 or (floral_ratio > 0.02 and green_foliage_ratio > 0.15):
            conf = min(0.96, 0.72 + floral_ratio * 2.0)
            return {
                "category": "flower",
                "confidence": round(conf, 2),
                "label": "Floral Blossom / Nectar Host",
                "species": "Lavandula / Floral Corolla",
                "reason": f"Vibrant floral petal chrominance detected ({floral_ratio*100:.1f}% floral coverage)."
            }

        # Pollinator on vegetation:
        if (green_foliage_ratio > 0.15 or floral_ratio > 0.03) and 0.005 < insect_contrast < 0.25:
            return {
                "category": "bee",
                "confidence": 0.89,
                "label": "Pollinator / Insect Subject",
                "species": "Apis mellifera / Insecta",
                "reason": "Localized high-contrast pollinator morphology detected on botanical background."
            }

        # General foliage / plant:
        if green_foliage_ratio > 0.12 or edge_variance > 100.0:
            conf = min(0.94, 0.65 + green_foliage_ratio * 1.5)
            return {
                "category": "foliage",
                "confidence": round(conf, 2),
                "label": "Botanical Foliage / Canopy",
                "species": "Foliage vegetation",
                "reason": f"Photosynthetic vegetation index confirmed ({green_foliage_ratio*100:.1f}% canopy cover)."
            }

        return {
            "category": "non_botanical",
            "confidence": 0.75,
            "label": "Non-nature / Unconfirmed subject",
            "species": "Unclassified environment",
            "reason": "Image lacks distinct botanical chlorophyll or floral coloration."
        }
