import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class TimelineEvent:
    event_id: str
    start_time: float
    end_time: float
    species_or_type: str
    confidence: float
    dominant_frequency: float
    amplitude_db: float
    description: str

class AcousticTimeline:
    """
    FEATURE 6: ACOUSTIC TIMELINE
    Builds an interactive chronological map of acoustic events in a recording.
    Allows users to tap and jump to specific biological events.
    """
    
    def __init__(self, sample_rate: int = 48000, window_sec: float = 0.5):
        self.sample_rate = sample_rate
        self.window_sec = window_sec
        self.window_size = int(window_sec * sample_rate)

    def analyze_timeline(self, audio: np.ndarray, classifier_fn=None) -> List[TimelineEvent]:
        """Segments audio stream and identifies distinct temporal acoustic events."""
        total_samples = len(audio)
        if total_samples < self.window_size:
            return []
            
        events: List[TimelineEvent] = []
        n_windows = total_samples // self.window_size
        
        current_event = None
        
        for i in range(n_windows):
            start_s = i * self.window_sec
            end_s = (i + 1) * self.window_sec
            chunk = audio[i * self.window_size : (i + 1) * self.window_size]
            
            rms = np.sqrt(np.mean(chunk**2) + 1e-12)
            rms_db = 20 * np.log10(rms + 1e-9)
            
            # Simple FFT to find dominant freq
            fft_mag = np.abs(np.fft.rfft(chunk))
            freqs = np.fft.rfftfreq(len(chunk), d=1.0 / self.sample_rate)
            dom_idx = np.argmax(fft_mag)
            dom_freq = float(freqs[dom_idx])
            
            # Use classifier if provided, else heuristic identification
            if classifier_fn:
                pred_label, pred_conf, pred_desc = classifier_fn(chunk)
            else:
                pred_label, pred_conf, pred_desc = self._heuristic_identify(dom_freq, rms_db)
                
            if pred_label != "ambient_background" and rms_db > -55.0:
                event_item = TimelineEvent(
                    event_id=f"evt_{i:03d}",
                    start_time=round(start_s, 2),
                    end_time=round(end_s, 2),
                    species_or_type=pred_label,
                    confidence=round(pred_conf, 2),
                    dominant_frequency=round(dom_freq, 1),
                    amplitude_db=round(float(rms_db), 1),
                    description=pred_desc
                )
                events.append(event_item)
                
        return events

    def _heuristic_identify(self, freq: float, rms_db: float):
        if 200.0 <= freq <= 300.0:
            return "honeybee_wingbeat", 0.92, "Honeybee (Apis mellifera) wing beat frequency pattern"
        elif 4000.0 <= freq <= 7500.0:
            return "tree_cricket_stridulation", 0.88, "Tree cricket rhythmic stridulation"
        elif freq >= 18000.0:
            return "ultrasonic_echolocation", 0.85, "High-frequency bat echolocation pulse"
        elif 1500.0 <= freq <= 3800.0:
            return "songbird_vocalization", 0.84, "Avian acoustic call"
        else:
            return "ambient_background", 0.40, "Ambient environmental sound"
