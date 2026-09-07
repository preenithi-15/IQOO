# System Limitations and Boundary Conditions

1. **Hardware Microphones**:
   - Built-in smartphone microphones typically exhibit rapid sensitivity attenuation above 22 kHz.
   - True ultrasonic reception (>24 kHz to 96 kHz) requires the optional USB-C **Nature Probe**.
2. **Acoustic Clutter**:
   - High-decibel urban environments ($>75 \text{ dB}$) reduce bioacoustic detection accuracy.
   - The adaptive spectral gate mitigates stationary noise, but sudden impulsive noises can trigger transient flags.
3. **Visual Obstruction**:
   - Dense foliage can obscure insects; NATURA gracefully degrades to acoustic-only confidence ratings.
