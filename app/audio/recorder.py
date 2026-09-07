import numpy as np
import threading
import time
from typing import Optional, Callable
from .quality import AudioQualityAnalyzer, QualityReport

class AudioRecorder:
    """
    Captures or simulates real-time audio streams with circular buffer management,
    recording quality assessment, and stream broadcasting.
    """
    
    def __init__(self, sample_rate: int = 48000, buffer_seconds: int = 10):
        self.sample_rate = sample_rate
        self.buffer_size = sample_rate * buffer_seconds
        self.buffer = np.zeros(self.buffer_size, dtype=np.float32)
        self.write_pos = 0
        self.is_recording = False
        self.lock = threading.Lock()
        self.quality_analyzer = AudioQualityAnalyzer(sample_rate)

    def push_samples(self, samples: np.ndarray):
        """Push incoming PCM audio samples into circular ring buffer."""
        with self.lock:
            n = len(samples)
            if n >= self.buffer_size:
                self.buffer[:] = samples[-self.buffer_size:]
                self.write_pos = 0
            else:
                end_pos = self.write_pos + n
                if end_pos <= self.buffer_size:
                    self.buffer[self.write_pos:end_pos] = samples
                    self.write_pos = (self.write_pos + n) % self.buffer_size
                else:
                    first_part = self.buffer_size - self.write_pos
                    self.buffer[self.write_pos:] = samples[:first_part]
                    self.buffer[:n - first_part] = samples[first_part:]
                    self.write_pos = n - first_part

    def get_latest_buffer(self, seconds: float = 3.0) -> np.ndarray:
        """Retrieve the latest N seconds of recorded audio uninterrupted."""
        with self.lock:
            req_samples = min(int(seconds * self.sample_rate), self.buffer_size)
            curr = self.write_pos
            if curr >= req_samples:
                return self.buffer[curr - req_samples:curr].copy()
            else:
                # Wrap around
                tail = self.buffer[self.buffer_size - (req_samples - curr):]
                head = self.buffer[:curr]
                return np.concatenate([tail, head]).copy()

    def get_quality_report(self, window_sec: float = 1.0) -> QualityReport:
        """Computes real-time recording quality indicator."""
        audio = self.get_latest_buffer(window_sec)
        return self.quality_analyzer.analyze(audio)
