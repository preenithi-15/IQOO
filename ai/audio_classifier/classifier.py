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
            return {
                "dom_freq": 0.0, "centroid": 0.0, "energy": 0.0, "peak_to_avg": 1.0,
                "audible_dom_freq": 0.0, "bee_band_ratio": 0.0, "cricket_band_ratio": 0.0,
                "flatness": 0.0
            }
            
        fft_mag = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), d=1.0 / self.sample_rate)
        
        peak_idx = int(np.argmax(fft_mag))
        dom_freq = float(freqs[peak_idx])
        
        sum_mag = float(np.sum(fft_mag)) + 1e-12
        centroid = float(np.sum(freqs * fft_mag) / sum_mag)
        
        energy = float(np.mean(audio**2))
        peak_to_avg = float(np.max(fft_mag) / (np.mean(fft_mag) + 1e-12))
        
        # Audio above 80Hz (ignoring DC bias and room/AC sub-bass rumble)
        audible_mask = freqs >= 80.0
        if np.any(audible_mask):
            audible_fft = fft_mag[audible_mask]
            audible_freqs = freqs[audible_mask]
            audible_dom_freq = float(audible_freqs[np.argmax(audible_fft)])
        else:
            audible_dom_freq = dom_freq

        # Band energy distributions
        bee_mask = (freqs >= 160.0) & (freqs <= 380.0)
        cricket_mask = (freqs >= 4000.0) & (freqs <= 8000.0)
        bee_band_ratio = float(np.sum(fft_mag[bee_mask]) / sum_mag) if np.any(bee_mask) else 0.0
        cricket_band_ratio = float(np.sum(fft_mag[cricket_mask]) / sum_mag) if np.any(cricket_mask) else 0.0

        # Spectral flatness
        geom_mean = np.exp(np.mean(np.log(np.maximum(fft_mag, 1e-10))))
        arith_mean = np.mean(fft_mag) + 1e-12
        flatness = float(geom_mean / arith_mean)
        
        return {
            "dom_freq": dom_freq,
            "audible_dom_freq": audible_dom_freq,
            "centroid": centroid,
            "energy": energy,
            "peak_to_avg": peak_to_avg,
            "bee_band_ratio": bee_band_ratio,
            "cricket_band_ratio": cricket_band_ratio,
            "flatness": flatness
        }

    def classify(self, audio: np.ndarray, context_hint: Optional[str] = None) -> AudioClassification:
        feats = self.extract_features(audio)
        dom = feats["dom_freq"]
        aud_dom = feats["audible_dom_freq"]
        centroid = feats["centroid"]
        
        # Determine effective dominant frequency (prefer audible peak if raw peak is sub-80Hz rumble)
        effective_dom = aud_dom if (dom < 80.0 and aud_dom >= 80.0) else dom
        
        # 1. Bat / Plant Ultrasonic (> 18 kHz)
        if effective_dom >= 18000.0 or centroid >= 18000.0:
            primary = "ultrasonic_echolocation"
            sci = "Pipistrellus pipistrellus"
            conf = 0.89
            sec = [{"label": "plant_xylem_cavitation", "confidence": 0.35}]
            band = (20000.0, 60000.0)
            pattern = "Frequency-modulated ultrasonic sweep"

        # 2. Honeybee (Apis mellifera): wingbeat fundamental 210 - 280 Hz (or broader 170 - 360 Hz)
        elif (210.0 <= effective_dom <= 280.0) or (170.0 <= effective_dom <= 360.0 and feats["bee_band_ratio"] > 0.08):
            primary = "honeybee_wingbeat"
            sci = "Apis mellifera"
            conf = 0.93 if (225.0 <= effective_dom <= 255.0) else 0.88
            sec = [{"label": "bumblebee_bombus", "confidence": 0.45}, {"label": "ambient_hum", "confidence": 0.12}]
            band = (200.0, 1200.0)
            pattern = "Harmonic wingbeat oscillation"
            
        # 3. Tree cricket (Oecanthinae): stridulation 4200 - 7800 Hz (or high cricket band concentration)
        elif (4200.0 <= effective_dom <= 7800.0) or (3800.0 <= effective_dom <= 8500.0 and feats["cricket_band_ratio"] > 0.08):
            primary = "tree_cricket_stridulation"
            sci = "Oecanthus fultoni"
            conf = 0.91
            sec = [{"label": "cicada_tymbals", "confidence": 0.38}, {"label": "bush_cricket", "confidence": 0.42}]
            band = (4500.0, 8000.0)
            pattern = "Rhythmic resonant stridulation"

        # 4. Songbird vocalization (1400 - 3800 Hz)
        elif 1400.0 <= effective_dom <= 3800.0:
            primary = "songbird_vocalization"
            sci = "Passeriformes spp."
            conf = 0.87
            sec = [{"label": "common_myna", "confidence": 0.55}, {"label": "house_sparrow", "confidence": 0.48}]
            band = (1500.0, 4200.0)
            pattern = "Modulated avian syrinx whistle"
            
        # 5. Rain precipitation
        elif feats["peak_to_avg"] < 4.0 and feats["energy"] > 0.005:
            primary = "rain_percussion"
            sci = "Hydrometeorological"
            conf = 0.84
            sec = [{"label": "rustling_leaves", "confidence": 0.40}]
            band = (50.0, 12000.0)
            pattern = "Stochastic acoustic droplet impact"
            
        # 6. Rustling leaves / Wind
        elif effective_dom < 200.0 and feats["energy"] > 0.001:
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
