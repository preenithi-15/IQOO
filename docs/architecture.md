# NATURA Technical Architecture

## 1. System Pipeline
The NATURA system operates on a low-latency streaming pipeline:
1. **Sensory Ingestion (`app/audio`, `app/camera`, `app/sensors`)**:
   - Real-time audio stream at 48kHz (or up to 192kHz with Nature Probe).
   - Video frames sampled at 30 FPS.
   - Sensor telemetry (GPS coordinates, heading, accelerometer lux/temperature) sampled at 10 Hz.
2. **Signal Conditioning & DSP (`app/audio/filter.py`, `ai/sonification`)**:
   - Adaptive spectral subtraction eliminates ambient vehicle/wind rumble.
   - Heterodyne down-conversion demodulates ultrasound (e.g. 40 kHz) into audible spectrum (2 kHz).
3. **Edge AI Inference (`ai/audio_classifier`, `ai/vision_classifier`, `ai/multimodal`)**:
   - Bioacoustic feature extractor computes Mel-frequency spectral centroids, rolloff, and zero crossings.
   - Cross-modal fusion matrix merges visual candidate bounding boxes with acoustic signatures.
4. **Nature Interpreter (`ai/nature_interpreter`)**:
   - Confidence-calibrated reasoning engine evaluates evidence vs. hypothesis.
   - Outputs: Scientific Fact + AI Model Reasoning + Poetic Narrative.
5. **Generative Composition (`music/composer`, `music/soundscape`)**:
   - Maps acoustic parameters directly to musical theory stems (Rhythm, Melody, Texture, Percussion).
6. **Archival & Experience (`app/video`, `data/storage`)**:
   - Packages synchronized Nature Moments.
