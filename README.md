# NATURA — AI Multimodal Nature Explorer
### *Hear Beyond Human Hearing • Use your phone to look beyond the screen*

NATURA turns the **iQOO 15** into an AI-powered multimodal nature explorer. It uses the phone's camera, microphone, sensors, Snapdragon 8 Elite Gen 5 computing platform, stereo speakers, and display to simultaneously observe the environment and build a real-time understanding of the natural world around the user.

---

## 1. Problem & Innovation
Humans perceive only a tiny fraction of natural biological activity. Much acoustic and vibrational activity occurs outside the human audible range (20 Hz - 20 kHz) or is drowned out by ambient noise. Meanwhile, smartphones normally act as barriers that pull users away from nature.

**NATURA turns the iQOO 15 into a bridge, not a barrier**:
- **SEE**: 50MP computer vision detects species, blooms, and pollinators.
- **HEAR**: High-sensitivity acoustic DSP captures micro-acoustics; heterodyne sonification shifts ultrasonic signals into audible frequencies.
- **DISCOVER**: Multimodal fusion correlates what is seen with what is heard.
- **UNDERSTAND**: Evidence-based Nature Interpreter produces grounded, 3-layer interpretations with confidence levels.
- **EXPERIENCE**: Nature Composer transforms bioacoustics into generative musical soundscapes.
- **SAVE**: Curates discoveries into rich, multi-asset Nature Moments and personal Nature Albums.

---

## 2. Core Architecture
```
[ Microphone ]  --> [ DSP & Adaptive Filter ] --> [ Heterodyne Sonifier ] --> [ Bioacoustic Classifier ]
                                                                                         |
[ Camera ]      --> [ Vision Object Classifier ] ----------------------------------------+--> [ Multimodal Fusion ]
                                                                                         |             |
[ Sensors/GPS ] --> [ Context Engine: Time/Temp/Orientation ] --------------------------+             v
                                                                                         [ Nature Interpreter ]
                                                                                         (3 Layers + Confidence)
                                                                                               |
                                                                         +---------------------+---------------------+
                                                                         v                                           v
                                                              [ Nature Composer ]                           [ Nature Cinema ]
                                                          (Acoustics -> Generative Music)             (Nature Moment Multi-Asset)
```

---

## 3. Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run End-to-End Demo
```bash
python demo/run_demo.py
```

### Launch Web Dashboard / vivo Office Kit Bridge
```bash
python -m app.ui.web_dashboard --port 8080
```
Open `http://localhost:8080` in your browser.
