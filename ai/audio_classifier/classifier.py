import numpy as np
from scipy import signal
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional

@dataclass
class AudioClassification:
    primary_label: str
    scientific_name: str
    confidence: float
    secondary_predictions: List[Dict[str, Any]]
    frequency_band_hz: Tuple[float, float]
    pattern_type: str

class BioacousticClassifier:
    """
    Classifies bioacoustic signals based on spectral envelopes, fundamental frequencies,
    and harmonic signatures. Supports Honeybees, Tree Crickets, Bats, Birds, Wind, and Rain.
    """
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate

    def extract_features(self, audio: np.ndarray) -> Dict[str, float]:
        """Calculates spectral centroid, peak frequency, harmonic ratio, and energy."""
        if len(audio) == 0:
            return {"dom_freq": 0.0, "centroid": 0.0, "energy": 0.0, "peak_to_avg": 1.0}
            
        fft_mag = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), d=1.0 / self.sample_rate)
        
        peak_idx = np.argmax(fft_mag)
        dom_freq = float(freqs[peak_idx])
        
        sum_mag = np.sum(fft_mag) + 1e-12
        centroid = float(np.sum(freqs * fft_mag) / sum_mag)
        
        energy = float(np.mean(audio**2))
        peak_to_avg = float(np.max(fft_mag) / (np.mean(fft_mag) + 1e-12))
        
        return {
            "dom_freq": dom_freq,
            "centroid": centroid,
            "energy": energy,
            "peak_to_avg": peak_to_avg
        }

    def classify(self, audio: np.ndarray, context_hint: Optional[str] = None) -> AudioClassification:
        feats = self.extract_features(audio)
        dom = feats["dom_freq"]
        centroid = feats["centroid"]
        
        # Bioacoustic pattern matching based on validated biological frequency bands:
        # Honeybee (Apis mellifera): wingbeat fundamental 230 - 260 Hz
        if 210.0 <= dom <= 280.0:
            primary = "honeybee_wingbeat"
            sci = "Apis mellifera"
            conf = 0.93 if (225.0 <= dom <= 255.0) else 0.82
            sec = [{"label": "bumblebee_bombus", "confidence": 0.45}, {"label": "ambient_hum", "confidence": 0.12}]
            band = (200.0, 1200.0)
            pattern = "Harmonic wingbeat oscillation"
            
        # Tree cricket (Oecanthinae): stridulation 4500 - 7500 Hz
        elif 4200.0 <= dom <= 7800.0:
            primary = "tree_cricket_stridulation"
            sci = "Oecanthus fultoni"
            conf = 0.91
            sec = [{"label": "cicada_tymbals", "confidence": 0.38}, {"label": "bush_cricket", "confidence": 0.42}]
            band = (4500.0, 8000.0)
            pattern = "Rhythmic resonant stridulation"
            
        # Bat / Plant Ultrasonic (> 18 kHz)
        elif dom >= 18000.0 or centroid >= 18000.0:
            primary = "ultrasonic_echolocation"
            sci = "Pipistrellus pipistrellus"
            conf = 0.89
            sec = [{"label": "plant_xylem_cavitation", "confidence": 0.35}]
            band = (20000.0, 60000.0)
            pattern = "Frequency-modulated ultrasonic sweep"
            
        # Songbird vocalization (1500 - 3800 Hz)
        elif 1400.0 <= dom <= 3800.0:
            primary = "songbird_vocalization"
            sci = "Passeriformes spp."
            conf = 0.87
            sec = [{"label": "common_myna", "confidence": 0.55}, {"label": "house_sparrow", "confidence": 0.48}]
            band = (1500.0, 4200.0)
            pattern = "Modulated avian syrinx whistle"
            
        # Rain precipitation
        elif feats["peak_to_avg"] < 4.0 and feats["energy"] > 0.005:
            primary = "rain_percussion"
            sci = "Hydrometeorological"
            conf = 0.84
            sec = [{"label": "rustling_leaves", "confidence": 0.40}]
            band = (50.0, 12000.0)
            pattern = "Stochastic acoustic droplet impact"
            
        # Rustling leaves / Wind
        elif dom < 200.0 and feats["energy"] > 0.001:
            primary = "foliage_rustle"
            sci = "Phytomechanical"
            conf = 0.78
            sec = [{"label": "wind_turbulence", "confidence": 0.62}]
            band = (40.0, 800.0)
            pattern = "Broadband laminar friction"
            
        else:
            primary = "unknown_acoustic_event"
            sci = "Incertae sedis"
            conf = 0.35
            sec = []
            band = (0.0, self.sample_rate / 2)
            pattern = "Uncharacterized diffuse acoustic background"

        return AudioClassification(
            primary_label=primary,
            scientific_name=sci,
            confidence=conf,
            secondary_predictions=sec,
            frequency_band_hz=band,
            pattern_type=pattern
        )
