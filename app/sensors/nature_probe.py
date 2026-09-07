import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class NatureProbeStatus:
    connected: bool
    firmware_version: str
    sensor_type: str  # CONTACT_PIEZO, ULTRASONIC_MEMS, DUAL_MODE
    sample_rate_hz: int
    battery_level_pct: int

class NatureProbe:
    """
    SECTION 16: OPTIONAL EXTENSION — NATURE PROBE
    USB-C connected external probe expanding sensing capabilities:
    - High-sensitivity bioacoustic microphone
    - Contact microphone for substrate/plant stem vibrations
    - Ultrasonic transducer (up to 96 kHz) for bat echolocation & insect cavitation
    """
    
    def __init__(self, auto_connect: bool = True):
        self.connected = auto_connect
        self.mode = "DUAL_MODE"
        self.sample_rate = 96000

    def get_status(self) -> NatureProbeStatus:
        return NatureProbeStatus(
            connected=self.connected,
            firmware_version="v2.4-Snapdragon-OTG",
            sensor_type=self.mode,
            sample_rate_hz=self.sample_rate,
            battery_level_pct=92
        )

    def read_ultrasonic_burst(self, duration_s: float = 0.5) -> np.ndarray:
        """Simulates high-bandwidth ultrasonic transducer capture (e.g., 35-50 kHz bat sweep)."""
        t = np.linspace(0, duration_s, int(self.sample_rate * duration_s), endpoint=False)
        # Linear frequency chirp from 48kHz down to 26kHz
        chirp = np.sin(2 * np.pi * (48000 * t - 0.5 * (48000 - 26000) * t**2 / duration_s))
        # Amplitude envelope
        env = np.hanning(len(t))
        return (chirp * env).astype(np.float32)
