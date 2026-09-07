from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from ai.audio_classifier.classifier import AudioClassification
from ai.vision_classifier.classifier import VisualDetection
from app.sensors.context_sensors import SensorContext

@dataclass
class MultimodalHypothesis:
    scene_summary: str
    correlated_subject: str
    visual_evidence: str
    acoustic_evidence: str
    environmental_context: str
    joint_confidence: float
    is_unknown_or_uncertain: bool

class MultimodalFusionEngine:
    """
    FEATURE 2: MULTIMODAL NATURE AI
    Fuses Audio ('What is happening acoustically?') +
          Camera ('What is happening visually?') +
          Context ('Where and when is this happening?')
    """
    
    def fuse(self, 
             audio_result: AudioClassification, 
             visual_results: List[VisualDetection], 
             context: SensorContext) -> MultimodalHypothesis:
        
        has_bee_audio = "bee" in audio_result.primary_label
        has_cricket_audio = "cricket" in audio_result.primary_label
        has_bat_audio = "ultrasonic" in audio_result.primary_label
        
        vis_subjects = [v.detected_species for v in visual_results]
        has_bee_vis = any("Honeybee" in s for s in vis_subjects)
        has_flower_vis = any("Plant" in s or "Lavender" in s for s in vis_subjects)
        has_cricket_vis = any("Cricket" in s for s in vis_subjects)
        has_bat_vis = any("Pipistrelle" in s or "Bat" in s for s in vis_subjects)
        
        ctx_str = f"{context.time_of_day} at {context.ambient_temp_c:.1f}°C in {context.season}"
        
        # Case 1: Honeybee Audio + Flower/Bee Visual
        if has_bee_audio and (has_bee_vis or has_flower_vis):
            joint_conf = min(0.99, (audio_result.confidence * 0.5) + 0.45)
            return MultimodalHypothesis(
                scene_summary="Active pollinator foraging in flowering vegetation",
                correlated_subject="Apis mellifera (Honeybee)",
                visual_evidence="Bee detected in micro-proximity to nectar-bearing corolla.",
                acoustic_evidence=f"Wingbeat fundamental at {audio_result.frequency_band_hz[0]:.0f}Hz with harmonic overtone stack.",
                environmental_context=ctx_str,
                joint_confidence=round(joint_conf, 2),
                is_unknown_or_uncertain=False
            )
            
        # Case 2: Tree cricket stridulation + Leaf/Cricket visual
        elif has_cricket_audio:
            joint_conf = min(0.98, (audio_result.confidence * 0.6) + (0.35 if has_cricket_vis else 0.20))
            return MultimodalHypothesis(
                scene_summary="Orthopteran thermoregulation and acoustic mating display",
                correlated_subject="Oecanthinae (Tree Cricket)",
                visual_evidence="Leaf canopy refuge providing acoustic resonance chamber." if not has_cricket_vis else "Visual sighting of tree cricket on leaf underside.",
                acoustic_evidence=f"Resonant 5.2 kHz continuous chirp train.",
                environmental_context=ctx_str,
                joint_confidence=round(joint_conf, 2),
                is_unknown_or_uncertain=False
            )
            
        # Case 3: Ultrasonic bat echolocation
        elif has_bat_audio:
            joint_conf = min(0.95, (audio_result.confidence * 0.7) + (0.25 if has_bat_vis else 0.15))
            return MultimodalHypothesis(
                scene_summary="Crepuscular echolocating predator foraging flight",
                correlated_subject="Microchiroptera (Insectivorous Bat)",
                visual_evidence="Open airspace foraging corridor at canopy boundary.",
                acoustic_evidence="Frequency-modulated ultrasonic pulses (32-48 kHz).",
                environmental_context=ctx_str,
                joint_confidence=round(joint_conf, 2),
                is_unknown_or_uncertain=False
            )
            
        # Case 4: Insufficient evidence (UNKNOWN / UNCERTAIN)
        elif audio_result.confidence < 0.50 and len(visual_results) == 0:
            return MultimodalHypothesis(
                scene_summary="Uncharacterized biological or abiotic event",
                correlated_subject="Unknown Organism / Background",
                visual_evidence="No focal species detected in frame.",
                acoustic_evidence="Diffuse low-amplitude acoustic energy without identifiable bioacoustic signature.",
                environmental_context=ctx_str,
                joint_confidence=0.32,
                is_unknown_or_uncertain=True
            )
            
        else:
            return MultimodalHypothesis(
                scene_summary="General environmental habitat ambiance",
                correlated_subject="Botanical Ecosystem",
                visual_evidence="Vegetation backdrop.",
                acoustic_evidence=audio_result.pattern_type,
                environmental_context=ctx_str,
                joint_confidence=0.65,
                is_unknown_or_uncertain=False
            )
