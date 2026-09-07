# Scientific Basis for Bioacoustic Interpretation & Sonification

## 1. Frequency Demodulation (Heterodyning)
Heterodyning mixes an incoming high-frequency signal $x(t) = A \cos(2\pi f_{in} t + \phi)$ with a local oscillator reference $s_{LO}(t) = \cos(2\pi f_{LO} t)$:
$$y_{mixed}(t) = x(t) \cdot s_{LO}(t) = \frac{A}{2} [\cos(2\pi(f_{in} - f_{LO})t + \phi) + \cos(2\pi(f_{in} + f_{LO})t + \phi)]$$
Filtering with a steep Low-Pass Filter (cut-off at 4 kHz) preserves the difference frequency $f_{audible} = |f_{in} - f_{LO}|$, allowing the human ear to perceive ultrasonic phenomena without alteration of temporal dynamics.

## 2. Evidence-Based Grounding vs. Hallucination
NATURA never fabricates biological assertions:
- If acoustic confidence $< 0.50$ or visual corroboration is missing when required, status is marked `UNCERTAIN` or `UNKNOWN_EVENT`.
- Hypotheses are explicitly verified against known bioacoustic frequency envelopes.
