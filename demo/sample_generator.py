import numpy as np
from scipy.io import wavfile
from scipy import signal
from pathlib import Path

def generate_bioacoustic_samples(output_dir: Path, sample_rate: int = 48000, duration: float = 10.0):
    """Generates synthetic ground-truth 10-second bioacoustic audio recordings (Original, Enhanced, Sonified)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    n_samples = len(t)
    nyq = 0.5 * sample_rate
    
    # 1. HONEYBEE (Apis mellifera) - 10 SECONDS
    f0_curve = 235.0 + 10.0 * np.sin(2 * np.pi * 0.3 * t) + 15.0 * np.exp(-((t - 6.0)**2) / 0.8)
    phase = 2 * np.pi * np.cumsum(f0_curve) / sample_rate
    bee_buzz = (
        0.50 * np.sin(phase) +
        0.30 * np.sin(2 * phase) +
        0.18 * np.sin(3 * phase) +
        0.08 * np.sin(4 * phase) +
        0.04 * np.sin(5 * phase)
    )
    bee_flight_env = 0.55 + 0.35 * np.sin(2 * np.pi * 0.7 * t) * np.cos(2 * np.pi * 0.15 * t)
    pollen_bursts = 0.6 * np.exp(-((t - 5.8)**2) / 0.05) + 0.7 * np.exp(-((t - 6.4)**2) / 0.06)
    bee_body = bee_buzz * (bee_flight_env + pollen_bursts)
    wind_rumble = np.convolve(np.random.normal(0, 0.04, n_samples), np.ones(240)/240, mode='same')
    
    # Original
    bee_orig = (bee_body * 0.7 + wind_rumble + np.random.normal(0, 0.015, n_samples)).astype(np.float32)
    bee_orig = bee_orig / np.max(np.abs(bee_orig)) * 0.85
    wavfile.write(str(output_dir / "sample_bee.wav"), sample_rate, bee_orig)
    
    # Enhanced
    b_hp, a_hp = signal.butter(4, 150.0 / nyq, btype='highpass')
    bee_clean = signal.filtfilt(b_hp, a_hp, bee_body)
    b_pk, a_pk = signal.iirpeak(480.0 / nyq, Q=3.0)
    bee_enh = signal.filtfilt(b_pk, a_pk, bee_clean) * 0.5 + bee_clean * 0.7
    bee_enh = (bee_enh / np.max(np.abs(bee_enh)) * 0.90).astype(np.float32)
    wavfile.write(str(output_dir / "sample_bee_enhanced.wav"), sample_rate, bee_enh)
    
    # Sonified
    carrier = np.sin(2 * np.pi * 480.0 * t)
    son_chord = (
        0.4 * np.sin(2 * np.pi * 240.0 * t) +
        0.3 * np.sin(2 * np.pi * 360.0 * t) +
        0.2 * np.sin(2 * np.pi * 480.0 * t) +
        0.15 * np.sin(2 * np.pi * 720.0 * t)
    )
    flight_amp = np.abs(signal.hilbert(bee_body))
    flight_amp = np.convolve(flight_amp, np.ones(480)/480, mode='same')
    bee_son = son_chord * flight_amp * 1.5 + 0.25 * (bee_body * carrier)
    bee_son = (bee_son / np.max(np.abs(bee_son)) * 0.88).astype(np.float32)
    wavfile.write(str(output_dir / "sample_bee_sonified.wav"), sample_rate, bee_son)
    
    # 2. NIGHT FIELD CRICKET (Oecanthinae) - 10 SECONDS
    cricket_f0 = 5150.0
    chirp_rate = 14.0
    chirp_gate = (np.sin(2 * np.pi * chirp_rate * t) > 0.3).astype(float)
    chirp_gate = np.convolve(chirp_gate, np.hanning(120)/np.sum(np.hanning(120)), mode='same')
    warmup = np.clip(t / 2.0, 0.2, 1.0)
    cricket_body = np.sin(2 * np.pi * cricket_f0 * t + 0.3 * np.sin(2 * np.pi * 200 * t)) * chirp_gate * warmup
    
    # Original
    cricket_orig = (cricket_body * 0.75 + wind_rumble * 0.8 + np.random.normal(0, 0.012, n_samples)).astype(np.float32)
    cricket_orig = cricket_orig / np.max(np.abs(cricket_orig)) * 0.85
    wavfile.write(str(output_dir / "sample_cricket.wav"), sample_rate, cricket_orig)
    
    # Enhanced
    b_hp_c, a_hp_c = signal.butter(4, 2500.0 / nyq, btype='highpass')
    cricket_enh = signal.filtfilt(b_hp_c, a_hp_c, cricket_body)
    cricket_enh = (cricket_enh / np.max(np.abs(cricket_enh)) * 0.90).astype(np.float32)
    wavfile.write(str(output_dir / "sample_cricket_enhanced.wav"), sample_rate, cricket_enh)
    
    # Sonified
    chime_a = np.sin(2 * np.pi * 880.0 * t) * chirp_gate * warmup
    chime_e = np.sin(2 * np.pi * 1320.0 * t) * np.roll(chirp_gate, 800) * warmup
    cricket_son = (0.55 * chime_a + 0.35 * chime_e + 0.2 * (cricket_body * np.cos(2 * np.pi * (cricket_f0 - 880) * t)))
    cricket_son = (cricket_son / np.max(np.abs(cricket_son)) * 0.88).astype(np.float32)
    wavfile.write(str(output_dir / "sample_cricket_sonified.wav"), sample_rate, cricket_son)
    
    # 3. MONSOON RAIN ON TEAK LEAVES - 10 SECONDS
    rain_base = np.random.normal(0, 0.08, n_samples)
    b_lp_r, a_lp_r = signal.butter(2, 6000.0 / nyq, btype='lowpass')
    rain_wash = signal.filtfilt(b_lp_r, a_lp_r, rain_base)
    droplet_track = np.zeros(n_samples)
    np.random.seed(42)
    drop_times = np.random.uniform(0.1, 9.9, 140)
    for dt in drop_times:
        idx = int(dt * sample_rate)
        if idx + 400 < n_samples:
            d_len = np.random.randint(180, 380)
            t_drop = np.linspace(0, 1, d_len)
            pitch = np.random.uniform(1100, 2400)
            droplet = np.sin(2 * np.pi * pitch * t_drop * np.exp(-3.0 * t_drop)) * np.exp(-6.0 * t_drop)
            droplet_track[idx:idx+d_len] += droplet * np.random.uniform(0.3, 0.8)
            
    rain_body = rain_wash * 0.45 + droplet_track * 0.65
    
    # Original
    rain_orig = (rain_body + wind_rumble * 0.5).astype(np.float32)
    rain_orig = rain_orig / np.max(np.abs(rain_orig)) * 0.85
    wavfile.write(str(output_dir / "sample_rain_wind.wav"), sample_rate, rain_orig)
    
    # Enhanced
    b_enh_r, a_enh_r = signal.butter(2, [800.0 / nyq, 8000.0 / nyq], btype='bandpass')
    rain_enh = signal.filtfilt(b_enh_r, a_enh_r, rain_body)
    rain_enh = (rain_enh / np.max(np.abs(rain_enh)) * 0.90).astype(np.float32)
    wavfile.write(str(output_dir / "sample_rain_wind_enhanced.wav"), sample_rate, rain_enh)
    
    # Sonified
    kalimba_son = np.zeros(n_samples)
    pentatonic_freqs = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.50]
    for i, dt in enumerate(drop_times[:90]):
        idx = int(dt * sample_rate)
        if idx + 4000 < n_samples:
            note_freq = pentatonic_freqs[i % len(pentatonic_freqs)]
            t_note = np.linspace(0, 0.08, 4000)
            bell = np.sin(2 * np.pi * note_freq * t_note) * np.exp(-14.0 * t_note)
            kalimba_son[idx:idx+4000] += bell * 0.65
    rain_son = (0.65 * kalimba_son + 0.35 * rain_enh).astype(np.float32)
    rain_son = (rain_son / np.max(np.abs(rain_son)) * 0.88).astype(np.float32)
    wavfile.write(str(output_dir / "sample_rain_wind_sonified.wav"), sample_rate, rain_son)
    
    # 4. ULTRASONIC BAT ECHOLOCATION - 10 SECONDS
    bat_raw = np.zeros(n_samples)
    bat_son_synth = np.zeros(n_samples)
    search_times = np.linspace(0.4, 3.2, 7)
    approach_times = np.linspace(3.5, 6.8, 22)
    buzz_times = np.linspace(7.1, 8.5, 95)
    recovery_times = np.linspace(8.8, 9.7, 5)
    all_pulses = np.concatenate([search_times, approach_times, buzz_times, recovery_times])
    
    for pt in all_pulses:
        idx = int(pt * sample_rate)
        p_len = 350
        if idx + p_len < n_samples:
            t_p = np.linspace(0, 0.007, p_len)
            sweep_raw = np.sin(2 * np.pi * (22000 * t_p - 0.5 * 4000 * t_p**2 / 0.007)) * np.hanning(p_len)
            bat_raw[idx:idx+p_len] += sweep_raw * 0.85
            sweep_son = np.sin(2 * np.pi * (2800 * t_p - 0.5 * 1600 * t_p**2 / 0.007)) * np.hanning(p_len)
            bat_son_synth[idx:idx+p_len] += sweep_son * 0.95
            
    # Original
    bat_orig = (bat_raw + np.random.normal(0, 0.008, n_samples)).astype(np.float32)
    bat_orig = bat_orig / (np.max(np.abs(bat_orig)) + 1e-9) * 0.85
    wavfile.write(str(output_dir / "sample_bat_ultrasonic.wav"), sample_rate, bat_orig)
    
    # Enhanced: High-definition ultrasonic pulse isolation
    bat_enh = (bat_raw * 1.25).astype(np.float32)
    bat_enh = bat_enh / (np.max(np.abs(bat_enh)) + 1e-9) * 0.90
    wavfile.write(str(output_dir / "sample_bat_ultrasonic_enhanced.wav"), sample_rate, bat_enh)
    
    # Sonified: Full-spectrum heterodyne translation with audible sonar carrier
    # Scientific bat detector heterodyne local oscillator carrier (down-converts ultrasound into rich audible chirps)
    sonar_carrier = 0.12 * np.sin(2 * np.pi * 580.0 * t) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.5 * t))
    bat_son = (bat_son_synth * 0.85 + sonar_carrier + np.random.normal(0, 0.003, n_samples)).astype(np.float32)
    bat_son = bat_son / (np.max(np.abs(bat_son)) + 1e-9) * 0.88
    wavfile.write(str(output_dir / "sample_bat_ultrasonic_sonified.wav"), sample_rate, bat_son)
    
    print(f"Generated 12 bioacoustic recordings (Original, Enhanced, Sonified x 4 species, 10s duration) in {output_dir}")

if __name__ == "__main__":
    demo_dir = Path(__file__).resolve().parent / "sample_recordings"
    generate_bioacoustic_samples(demo_dir)
