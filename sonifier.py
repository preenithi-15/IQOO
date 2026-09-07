"""
NATURA Bioacoustics Sonification Engine
Translates non-audible acoustic frequencies (ultrasound/infrasound) into human audible spectrum
using Pitch Scaling (Granular Synthesis) and Heterodyning.
"""

import numpy as np
from scipy import signal


class BioacousticSonifier:
    def __init__(self, sample_rate: int = 48000, fft_size: int = 2048):
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.hop_length = fft_size // 4

    def compute_spectrogram(self, audio_data: np.ndarray):
        """Computes STFT magnitude spectrogram for visualization and analysis."""
        frequencies, times, stft = signal.stft(
            audio_data,
            fs=self.sample_rate,
            nperseg=self.fft_size,
            noverlap=self.fft_size - self.hop_length
        )
        spectrogram = np.abs(stft)
        # Convert to dB scale
        spectrogram_db = 20 * np.log10(np.maximum(spectrogram, 1e-5))
        return frequencies, times, spectrogram_db

    def heterodyne_downconvert(self, audio_data: np.ndarray, carrier_freq: float = 35000.0) -> np.ndarray:
        """
        Heterodyning down-conversion for ultrasonic frequencies (e.g. 35kHz bat call).
        Multiplies by cos(2*pi*f_c*t) and applies low-pass filter at 8kHz.
        """
        t = np.arange(len(audio_data)) / self.sample_rate
        carrier = np.cos(2 * np.pi * carrier_freq * t)
        mixed = audio_data * carrier
        
        # Low-pass filter to isolate difference frequency band
        nyquist = self.sample_rate / 2
        cutoff = 8000.0 / nyquist
        b, a = signal.butter(4, cutoff, btype='low')
        sonified = signal.filtfilt(b, a, mixed)
        return sonified / (np.max(np.abs(sonified)) + 1e-6)

    def pitch_scale_sonify(self, audio_data: np.ndarray, scale_factor: float = 0.25) -> np.ndarray:
        """
        Resamples audio signal to shift ultrasonic frequencies down into audible spectrum.
        """
        num_samples = int(len(audio_data) / scale_factor)
        resampled = signal.resample(audio_data, num_samples)
        # Truncate or pad to match length
        if len(resampled) > len(audio_data):
            return resampled[:len(audio_data)]
        else:
            return np.pad(resampled, (0, len(audio_data) - len(resampled)))

    def clean_and_enhance(self, audio_data: np.ndarray) -> np.ndarray:
        """Applies spectral noise reduction and bandpass filter (200Hz - 12kHz)."""
        nyquist = self.sample_rate / 2
        low = 200.0 / nyquist
        high = min(12000.0 / nyquist, 0.99)
        b, a = signal.butter(3, [low, high], btype='band')
        enhanced = signal.filtfilt(b, a, audio_data)
        return enhanced / (np.max(np.abs(enhanced)) + 1e-6)


if __name__ == "__main__":
    # Test BioacousticSonifier
    sr = 48000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Simulated 30kHz ultrasonic wave + 400Hz bird sound
    ultrasonic_sig = 0.5 * np.sin(2 * np.pi * 30000 * t) + 0.3 * np.sin(2 * np.pi * 400 * t)
    
    sonifier = BioacousticSonifier(sample_rate=sr)
    freqs, times, spec = sonifier.compute_spectrogram(ultrasonic_sig)
    sonified = sonifier.heterodyne_downconvert(ultrasonic_sig, carrier_freq=28000)
    print(f"Spectrogram shape: {spec.shape}, Sonified signal max: {np.max(sonified):.4f}")
