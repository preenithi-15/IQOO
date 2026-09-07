import numpy as np
from scipy import signal
from scipy.ndimage import median_filter

class AcousticSourceSeparator:
    """
    ADVANCED FEATURE: ACOUSTIC SOURCE SEPARATION
    Isolates overlapping natural sound events (e.g. bee wingbeat + wind + rain)
    using Harmonic-Percussive Source Separation (HPSS).
    """
    
    def __init__(self, sample_rate: int = 48000, n_fft: int = 1024, hop_length: int = 256):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length

    def separate_harmonic_percussive(self, audio: np.ndarray):
        """Separates sustained tone (bee, cricket) from transient bursts (rain, twig snaps)."""
        if len(audio) < self.n_fft:
            return audio, audio
            
        window = np.hanning(self.n_fft)
        f, t, Zxx = signal.stft(audio, fs=self.sample_rate, window=window,
                                nperseg=self.n_fft, noverlap=self.n_fft - self.hop_length)
        
        mag = np.abs(Zxx)
        phase = np.angle(Zxx)
        
        # Median filter across time for Harmonic components (horizontal lines in spectrogram)
        harm_mag = median_filter(mag, size=(1, 15))
        # Median filter across frequency for Percussive components (vertical lines in spectrogram)
        perc_mag = median_filter(mag, size=(15, 1))
        
        # Soft mask
        mask_h = harm_mag / (harm_mag + perc_mag + 1e-12)
        mask_p = perc_mag / (harm_mag + perc_mag + 1e-12)
        
        Zxx_h = (mag * mask_h) * np.exp(1j * phase)
        Zxx_p = (mag * mask_p) * np.exp(1j * phase)
        
        _, audio_harmonic = signal.istft(Zxx_h, fs=self.sample_rate, window=window,
                                         nperseg=self.n_fft, noverlap=self.n_fft - self.hop_length)
        _, audio_percussive = signal.istft(Zxx_p, fs=self.sample_rate, window=window,
                                           nperseg=self.n_fft, noverlap=self.n_fft - self.hop_length)
        
        # Trim to match length
        audio_harmonic = audio_harmonic[:len(audio)]
        audio_percussive = audio_percussive[:len(audio)]
        
        return audio_harmonic.astype(np.float32), audio_percussive.astype(np.float32)
