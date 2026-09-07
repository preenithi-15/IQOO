# NATURA Dependencies and Environment Specification

## System Requirements
- **Platform**: iQOO 15 (Snapdragon 8 Elite Gen 5 NPU) / Android 15 / Cross-Platform Desktop Bridge
- **Python**: >= 3.10 (tested on 3.10 - 3.13)
- **Audio Output**: Stereo 48kHz, 24-bit DAC
- **Audio Input**: Triple microphone array with high SNR (>68dB) & optional USB-C Nature Probe

## Python Core Dependencies
- `numpy` (>= 1.24.0): Tensor arithmetic, buffer windows, FFT operations.
- `scipy` (>= 1.10.0): Digital signal processing (`scipy.signal`), heterodyne modulation, spectrogram STFT, WAV file I/O (`scipy.io.wavfile`).

## Optional Platform Extensions
- `fastapi` & `uvicorn`: vivo Office Kit REST & WebSocket streaming.
- `opencv-python`: Camera frame capture and video encoding.
- `onnxruntime`: On-device NPU accelerated model execution.
