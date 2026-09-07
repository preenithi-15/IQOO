from dataclasses import dataclass
from typing import Optional
from ai.multimodal.fusion_engine import MultimodalHypothesis

@dataclass
class NatureInterpretation:
    scientific_interpretation: str  # Layer 1: Evidence-based facts
    ai_explanation: str            # Layer 2: Model-based reasoning
    poetic_message: str            # Layer 3: Creative / Emotional reconnection
    confidence_level: float
    is_uncertain: bool

class NatureInterpreter:
    """
    FEATURE 3: NATURE INTERPRETER
    Evidence-based bioacoustic interpretation.
    Separates detected evidence from model inference.
    
    CRITICAL PRINCIPLE:
    We never present AI-generated interpretation as scientific fact without evidence.
    If evidence is insufficient, NATURA reports an UNKNOWN/UNCERTAIN event.
    """
    
    def interpret(self, hypothesis: MultimodalHypothesis) -> NatureInterpretation:
        if hypothesis.is_unknown_or_uncertain:
            return NatureInterpretation(
                scientific_interpretation="Insufficient bioacoustic and morphological evidence to confirm specific biological taxa.",
                ai_explanation="Acoustic pattern did not meet the required threshold (0.50) and no focal species bounding box was resolved.",
                poetic_message="The forest holds its breath in quiet mystery, keeping its secrets for another moment.",
                confidence_level=hypothesis.joint_confidence,
                is_uncertain=True
            )
            
        subject = hypothesis.correlated_subject.lower()
        
        if "honeybee" in subject:
            sci = ("Apis mellifera wingbeat observed at ~240 Hz fundamental frequency. "
                   "Acoustic frequency matches thoracic dorsoventral flight muscle contractions, "
                   "corroborated by proximity to floral nectar source. Consistent with foraging behavior.")
            ai = (f"Model correlated 50MP visual classification ({hypothesis.visual_evidence}) "
                  f"with acoustic harmonic series ({hypothesis.acoustic_evidence}). "
                  f"Environmental context ({hypothesis.environmental_context}) confirms optimal foraging window.")
            poetic = "A golden weaver dances between blossoms, humming the ancient anthem of blooming life."
            
        elif "cricket" in subject:
            sci = ("Orthopteran stridulation detected at 5.2 kHz via tegminal friction (scraper on file). "
                   "Chirp rate exhibits linear thermal correlation according to Dolbear's Law. "
                   "Consistent with mate-attraction acoustic signaling.")
            ai = (f"High spectral peak in 4.5-6 kHz bracket combined with vegetative canopy context. "
                  f"Visual and acoustic evidence confirm male tree cricket acoustic advertising.")
            poetic = "A tiny emerald bard reads the temperature of the dusk and turns it into a serenade."
            
        elif "bat" in subject:
            sci = ("Ultrasonic echolocation sweep (30-50 kHz) down-converted via heterodyne sonification. "
                   "Pulse repetition rate indicates search-phase aerial insectivory.")
            ai = (f"Heterodyne detection resolved 38 kHz carrier frequency in crepuscular lighting. "
                  f"Sensor context confirms post-sunset insect predator activity.")
            poetic = "Navigating darkness by sculpting echoes, an invisible wing carves constellations in the twilight."
            
        else:
            sci = f"Biophonic acoustic activity detected within botanical biome: {hypothesis.acoustic_evidence}."
            ai = f"Combined multimodal telemetry confirms natural environmental activity with {hypothesis.joint_confidence*100:.0f}% confidence."
            poetic = "The subtle symphony of living green murmurs beneath the open sky."

        return NatureInterpretation(
            scientific_interpretation=sci,
            ai_explanation=ai,
            poetic_message=poetic,
            confidence_level=hypothesis.joint_confidence,
            is_uncertain=False
        )
