import numpy as np
from scipy import signal
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class SpectralFeatures:
    spectral_centroid: float
    spectral_rolloff: float
    spectral_spread: float
    zero_crossing_rate: float
    dominant_frequency: float
    energy: float

class SpectrogramAnalyzer:
    """STFT, Mel-spectrogram, and bioacoustic spectral feature extraction."""
    
    def __init__(self, sample_rate: int = 48000, n_fft: int = 1024, hop_length: int = 512):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length

    def compute_stft(self, audio: np.ndarray):
        """Computes frequencies, time bins, and dB magnitude spectrogram."""
        if len(audio) < self.n_fft:
            audio = np.pad(audio, (0, self.n_fft - len(audio)))
        window = np.hanning(self.n_fft)
        f, t, Zxx = signal.stft(audio, fs=self.sample_rate, window=window,
                                nperseg=self.n_fft, noverlap=self.n_fft - self.hop_length)
        mag = np.abs(Zxx)
        mag_db = 20 * np.log10(mag + 1e-9)
        mag_db = np.clip(mag_db, -80.0, 0.0)
        return f, t, mag_db

    def extract_features(self, audio: np.ndarray) -> SpectralFeatures:
        """Calculates spectral centroid, rolloff, spread, dominant freq, and ZCR."""
        if len(audio) == 0:
            return SpectralFeatures(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            
        f, t, Zxx = signal.stft(audio, fs=self.sample_rate, nperseg=min(len(audio), self.n_fft))
        mag = np.abs(Zxx)
        mean_spectrum = np.mean(mag, axis=1) + 1e-12
        sum_mag = np.sum(mean_spectrum)
        
        # Spectral Centroid: sum(f * mag) / sum(mag)
        centroid = float(np.sum(f * mean_spectrum) / sum_mag)
        
        # Spectral Spread / Variance: sqrt(sum((f - centroid)^2 * mag) / sum(mag))
        spread = float(np.sqrt(np.sum(((f - centroid)**2) * mean_spectrum) / sum_mag))
        
        # Spectral Rolloff: frequency below which 85% of spectral energy lies
        cum_energy = np.cumsum(mean_spectrum)
        rolloff_idx = np.where(cum_energy >= 0.85 * sum_mag)[0]
        rolloff = float(f[rolloff_idx[0]]) if len(rolloff_idx) > 0 else float(f[-1])
        
        # Dominant frequency
        dominant_idx = np.argmax(mean_spectrum)
        dominant_freq = float(f[dominant_idx])
        
        # Zero Crossing Rate (ZCR)
        signs = np.sign(audio)
        zcr = float(np.mean(np.abs(np.diff(signs))) / 2.0)
        
        # Total energy
        energy = float(np.mean(audio**2))
        
        return SpectralFeatures(
            spectral_centroid=round(centroid, 1),
            spectral_rolloff=round(rolloff, 1),
            spectral_spread=round(spread, 1),
            zero_crossing_rate=round(zcr, 4),
            dominant_frequency=round(dominant_freq, 1),
            energy=round(energy, 6)
        )

    def ascii_spectrogram(self, mag_db: np.ndarray, rows: int = 10, cols: int = 40) -> str:
        """Renders a compact text-based spectrogram for CLI / terminal displays."""
        if mag_db.size == 0:
            return "No spectral data"
        # Resample matrix to rows x cols
        h, w = mag_db.shape
        row_indices = np.linspace(h - 1, 0, rows, dtype=int)
        col_indices = np.linspace(0, w - 1, cols, dtype=int)
        sub = mag_db[np.ix_(row_indices, col_indices)]
        
        # Characters from quiet to intense
        chars = " .:-=+*#%@"
        out = []
        for r in range(rows):
            line = []
            for c in range(cols):
                val = sub[r, c]  # range -80 to 0
                norm = int(np.clip((val + 80.0) / 80.0 * (len(chars) - 1), 0, len(chars) - 1))
                line.append(chars[norm])
            out.append("".join(line))
        return "\n".join(out)
