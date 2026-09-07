import numpy as np
from scipy.io import wavfile
from pathlib import Path

def generate_bioacoustic_samples(output_dir: Path, sample_rate: int = 48000):
    """Generates synthetic ground-truth bioacoustic audio recordings for verification."""
    output_dir.mkdir(parents=True, exist_ok=True)
    duration = 4.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # 1. Honeybee (Apis mellifera) wingbeat: 240 Hz + harmonics
    bee_f0 = 240.0
    bee_buzz = (
        0.5 * np.sin(2 * np.pi * bee_f0 * t) +
        0.3 * np.sin(2 * np.pi * 2 * bee_f0 * t) +
        0.15 * np.sin(2 * np.pi * 3 * bee_f0 * t) +
        0.05 * np.sin(2 * np.pi * 4 * bee_f0 * t)
    )
    bee_mod = 0.5 * (1.0 + 0.3 * np.sin(2 * np.pi * 3.5 * t))
    bee_audio = bee_buzz * bee_mod + np.random.normal(0, 0.02, len(t))
    bee_audio = (bee_audio / np.max(np.abs(bee_audio)) * 0.85).astype(np.float32)
    wavfile.write(str(output_dir / "sample_bee.wav"), sample_rate, bee_audio)
    
    # 2. Tree Cricket (Oecanthinae): 5200 Hz pulsed stridulation
    cricket_f0 = 5200.0
    pulse_train = (np.sin(2 * np.pi * 18.0 * t) > 0.0).astype(float)
    cricket_sound = np.sin(2 * np.pi * cricket_f0 * t) * pulse_train
    cricket_audio = cricket_sound * 0.7 + np.random.normal(0, 0.015, len(t))
    cricket_audio = (cricket_audio / np.max(np.abs(cricket_audio)) * 0.85).astype(np.float32)
    wavfile.write(str(output_dir / "sample_cricket.wav"), sample_rate, cricket_audio)
    
    # 3. Ultrasonic Bat Echolocation Sweep (down-sampled representation with 21kHz peak)
    bat_audio = np.zeros_like(t)
    n_pulses = 12
    pulse_indices = np.linspace(1000, len(t) - 4000, n_pulses, dtype=int)
    for p_idx in pulse_indices:
        t_pulse = np.linspace(0, 0.008, 384, endpoint=False)
        sweep = np.sin(2 * np.pi * (22000 * t_pulse - 0.5 * (22000 - 18000) * t_pulse**2 / 0.008))
        env = np.hanning(len(t_pulse))
        bat_audio[p_idx:p_idx+384] += sweep * env * 0.8
    bat_audio += np.random.normal(0, 0.01, len(t))
    bat_audio = (bat_audio / (np.max(np.abs(bat_audio)) + 1e-9) * 0.85).astype(np.float32)
    wavfile.write(str(output_dir / "sample_bat_ultrasonic.wav"), sample_rate, bat_audio)
    
    # 4. Rain & Wind (Stochastic percussion & pink noise rumble)
    rain_audio = np.random.normal(0, 0.1, len(t))
    wavfile.write(str(output_dir / "sample_rain_wind.wav"), sample_rate, rain_audio.astype(np.float32))
    
    print(f"Generated 4 bioacoustic test recordings in {output_dir}")

if __name__ == "__main__":
    demo_dir = Path(__file__).resolve().parent / "sample_recordings"
    generate_bioacoustic_samples(demo_dir)
