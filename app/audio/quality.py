import numpy as np
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class QualityReport:
    snr_db: float
    rms_db: float
    peak_amplitude: float
    clipping_detected: bool
    noise_floor_db: float
    rating: str  # EXCELLENT, GOOD, FAIR, POOR
    advice: str

class AudioQualityAnalyzer:
    """Analyzes recording quality in real-time, computing SNR, clipping, and noise floor."""
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate

    def analyze(self, samples: np.ndarray) -> QualityReport:
        if len(samples) == 0:
            return QualityReport(0.0, -100.0, 0.0, False, -100.0, "POOR", "No audio received.")
        
        audio = samples.astype(np.float32)
        # Normalize if integer
        if np.issubdtype(samples.dtype, np.integer):
            max_val = np.iinfo(samples.dtype).max
            audio = audio / max_val
            
        peak = float(np.max(np.abs(audio)))
        rms = float(np.sqrt(np.mean(audio**2) + 1e-12))
        rms_db = float(20 * np.log10(rms + 1e-9))
        
        # Clipping check (samples >= 0.98 of full scale)
        clipped_count = np.sum(np.abs(audio) >= 0.98)
        clipping_detected = bool(clipped_count > (0.001 * len(audio)))
        
        # Estimate noise floor via lowest 15th percentile energy of 20ms frames
        frame_size = int(0.02 * self.sample_rate)
        if len(audio) >= frame_size:
            n_frames = len(audio) // frame_size
            frames = audio[:n_frames * frame_size].reshape(n_frames, frame_size)
            frame_rms = np.sqrt(np.mean(frames**2, axis=1) + 1e-12)
            noise_rms = np.percentile(frame_rms, 15)
            signal_rms = np.percentile(frame_rms, 90)
        else:
            noise_rms = 1e-4
            signal_rms = rms

        noise_floor_db = float(20 * np.log10(noise_rms + 1e-9))
        signal_db = float(20 * np.log10(signal_rms + 1e-9))
        snr_db = float(np.clip(signal_db - noise_floor_db, 0.0, 60.0))
        
        # Determine rating
        if clipping_detected:
            rating = "POOR"
            advice = "Input clipped. Lower microphone gain or step slightly back."
        elif snr_db >= 22.0:
            rating = "EXCELLENT"
            advice = "Optimal acoustic clarity. High bioacoustic SNR."
        elif snr_db >= 12.0:
            rating = "GOOD"
            advice = "Good acoustic clarity for reliable identification."
        elif snr_db >= 6.0:
            rating = "FAIR"
            advice = "Ambient noise present. Shield microphone from wind or move closer."
        else:
            rating = "POOR"
            advice = "Signal obscured by noise. Enable adaptive noise filter or approach subject."
            
        return QualityReport(
            snr_db=round(snr_db, 1),
            rms_db=round(rms_db, 1),
            peak_amplitude=round(peak, 3),
            clipping_detected=clipping_detected,
            noise_floor_db=round(noise_floor_db, 1),
            rating=rating,
            advice=advice
        )
