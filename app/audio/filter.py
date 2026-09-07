import numpy as np
from scipy import signal

class AdaptiveNoiseFilter:
    """Adaptive spectral gating and filtering for outdoor environmental recordings."""
    
    def __init__(self, sample_rate: int = 48000, n_fft: int = 1024, hop_length: int = 512):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.noise_profile = None

    def remove_wind_rumble(self, audio: np.ndarray, cutoff_hz: float = 80.0) -> np.ndarray:
        """Highpass Butterworth filter to eliminate sub-80Hz wind and turbulence."""
        if len(audio) < 64:
            return audio
        nyquist = 0.5 * self.sample_rate
        norm_cutoff = min(cutoff_hz / nyquist, 0.99)
        b, a = signal.butter(4, norm_cutoff, btype='highpass')
        return signal.filtfilt(b, a, audio)

    def bandpass_bioacoustics(self, audio: np.ndarray, low_hz: float = 120.0, high_hz: float = 14000.0) -> np.ndarray:
        """Bandpass filter tuned to biological acoustic signals."""
        if len(audio) < 64:
            return audio
        nyquist = 0.5 * self.sample_rate
        low = max(low_hz / nyquist, 0.001)
        high = min(high_hz / nyquist, 0.99)
        b, a = signal.butter(4, [low, high], btype='bandpass')
        return signal.filtfilt(b, a, audio)

    def spectral_subtraction(self, audio: np.ndarray, alpha: float = 2.0, beta: float = 0.02) -> np.ndarray:
        """Adaptive spectral subtraction for stationary ambient noise reduction."""
        if len(audio) < self.n_fft:
            return audio
            
        window = np.hanning(self.n_fft)
        # Compute STFT
        f, t, Zxx = signal.stft(audio, fs=self.sample_rate, window=window, 
                                nperseg=self.n_fft, noverlap=self.n_fft - self.hop_length)
        
        magnitude = np.abs(Zxx)
        phase = np.angle(Zxx)
        
        # Estimate noise profile from 10% quietest frames
        frame_energies = np.sum(magnitude**2, axis=0)
        quiet_indices = np.argsort(frame_energies)[:max(2, int(0.15 * len(frame_energies)))]
        noise_profile = np.mean(magnitude[:, quiet_indices], axis=1, keepdims=True)
        
        # Subtract noise spectrum
        subtracted_mag = magnitude - (alpha * noise_profile)
        # Floor with spectral floor beta
        floor = beta * magnitude
        cleaned_mag = np.maximum(subtracted_mag, floor)
        
        # Reconstruct with original phase
        Zxx_cleaned = cleaned_mag * np.exp(1j * phase)
        _, cleaned_audio = signal.istft(Zxx_cleaned, fs=self.sample_rate, window=window,
                                         nperseg=self.n_fft, noverlap=self.n_fft - self.hop_length)
        
        # Match length
        if len(cleaned_audio) > len(audio):
            cleaned_audio = cleaned_audio[:len(audio)]
        elif len(cleaned_audio) < len(audio):
            cleaned_audio = np.pad(cleaned_audio, (0, len(audio) - len(cleaned_audio)))
            
        return cleaned_audio.astype(np.float32)

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Full cleanup pipeline: rumble removal + spectral subtraction + normalization."""
        clean = self.remove_wind_rumble(audio)
        clean = self.spectral_subtraction(clean)
        peak = np.max(np.abs(clean)) + 1e-9
        if peak > 0:
            clean = clean / peak * 0.9  # Headroom normalization
        return clean
