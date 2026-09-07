import numpy as np

class SoundscapeGenerator:
    """Generates continuous atmospheric nature soundscapes tuned to ecological resonance."""
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate

    def generate_soundscape(self, duration_sec: float = 10.0, root_freq: float = 136.1) -> np.ndarray:
        n_samples = int(duration_sec * self.sample_rate)
        t = np.linspace(0, duration_sec, n_samples, endpoint=False)
        
        drone1 = np.sin(2 * np.pi * root_freq * t) * 0.3
        drone2 = np.sin(2 * np.pi * (root_freq * 1.5) * t) * 0.2
        drone3 = np.sin(2 * np.pi * (root_freq * 2.0) * t) * 0.15
        
        lfo = 0.5 * (1.0 + np.sin(2 * np.pi * 0.08 * t))
        soundscape = (drone1 + drone2 + drone3) * lfo
        
        peak = np.max(np.abs(soundscape)) + 1e-9
        return (soundscape / peak * 0.85).astype(np.float32)
