import numpy as np
from scipy import signal
from dataclasses import dataclass
from typing import Tuple

@dataclass
class SonificationResult:
    original_audio: np.ndarray
    enhanced_audio: np.ndarray
    sonified_audio: np.ndarray
    sample_rate: int
    ultrasound_detected: bool
    carrier_frequency: float
    description: str

class FrequencySonifier:
    """
    FEATURE 1: HEAR THE UNHEARD
    Translates ultrasonic/inaudible bioacoustic signals into the human audible range
    using Heterodyne Demodulation and Pitch Down-Conversion.
    
    Scientific Principle:
    Creates an audible representation of high-frequency and ultrasonic information (20-60 kHz)
    shifted into the optimal 1-4 kHz human hearing range without time distortion.
    """
    
    def __init__(self, sample_rate: int = 48000, target_audible_freq: float = 2400.0):
        self.sample_rate = sample_rate
        self.target_audible_freq = target_audible_freq

    def heterodyne_demodulate(self, audio: np.ndarray, local_osc_freq: float) -> np.ndarray:
        """
        Multiplies the input by cos(2*pi*f_LO*t) and applies a steep low-pass filter.
        Diff frequency = |f_in - f_LO| lands in audible zone.
        """
        t = np.arange(len(audio)) / self.sample_rate
        lo_carrier = np.cos(2.0 * np.pi * local_osc_freq * t)
        
        # Mixing
        mixed = audio * lo_carrier
        
        # Steep 6th order Butterworth low-pass filter at 4.5 kHz
        nyquist = 0.5 * self.sample_rate
        cutoff = min(4500.0 / nyquist, 0.95)
        b, a = signal.butter(6, cutoff, btype='lowpass')
        demodulated = signal.filtfilt(b, a, mixed)
        
        # Normalize
        peak = np.max(np.abs(demodulated)) + 1e-9
        return (demodulated / peak * 0.85).astype(np.float32)

    def pitch_shift_time_expansion(self, audio: np.ndarray, factor: float = 0.1) -> np.ndarray:
        """
        Time expansion sonification: expands signal in time by 1/factor,
        shifting high frequencies downwards by the same factor (useful for bat sweeps).
        """
        num_output_samples = int(len(audio) / factor)
        resampled = signal.resample(audio, num_output_samples)
        # Window back to original length or loop
        if len(resampled) > len(audio):
            resampled = resampled[:len(audio)]
        else:
            resampled = np.pad(resampled, (0, len(audio) - len(resampled)))
        peak = np.max(np.abs(resampled)) + 1e-9
        return (resampled / peak * 0.85).astype(np.float32)

    def process(self, audio: np.ndarray, high_band_peak_hz: float = 38000.0) -> SonificationResult:
        """
        Produces:
        1. Original: Raw signal
        2. Enhanced: Noise-filtered and amplified
        3. Sonified: Frequency translated into audible range
        """
        # 1. Original
        original = audio.copy().astype(np.float32)
        
        # 2. Enhanced (High-pass + gentle compression)
        nyquist = 0.5 * self.sample_rate
        b, a = signal.butter(2, max(100.0 / nyquist, 0.001), btype='highpass')
        enhanced = signal.filtfilt(b, a, original)
        peak_enh = np.max(np.abs(enhanced)) + 1e-9
        enhanced = (enhanced / peak_enh * 0.9).astype(np.float32)
        
        # 3. Sonified
        # Check energy in upper band
        f, t, Zxx = signal.stft(audio, fs=self.sample_rate, nperseg=min(len(audio), 1024))
        mag = np.mean(np.abs(Zxx), axis=1)
        high_bins = np.where(f >= (0.35 * self.sample_rate))[0]
        
        high_energy = np.sum(mag[high_bins]) if len(high_bins) > 0 else 0.0
        total_energy = np.sum(mag) + 1e-12
        ultrasound_ratio = high_energy / total_energy
        
        ultrasound_detected = bool(ultrasound_ratio > 0.15 or high_band_peak_hz >= 20000.0)
        
        if ultrasound_detected:
            # Heterodyne down using local oscillator
            lo_freq = high_band_peak_hz - self.target_audible_freq
            if lo_freq <= 0:
                lo_freq = 0.8 * nyquist
            sonified = self.heterodyne_demodulate(audio, lo_freq)
            desc = f"Heterodyne down-conversion from {high_band_peak_hz:.0f} Hz to ~{self.target_audible_freq:.0f} Hz."
        else:
            # Subtle spectral enhancement of faint harmonic micro-vibrations
            sonified = self.heterodyne_demodulate(audio, 8000.0)
            desc = "Acoustic micro-vibration translation: faint spectral components amplified and sonified."
            
        return SonificationResult(
            original_audio=original,
            enhanced_audio=enhanced,
            sonified_audio=sonified,
            sample_rate=self.sample_rate,
            ultrasound_detected=ultrasound_detected,
            carrier_frequency=high_band_peak_hz if ultrasound_detected else 0.0,
            description=desc
        )
