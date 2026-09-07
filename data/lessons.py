from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Lesson:
    lesson_id: str
    title: str
    organism: str
    what_we_know: str
    sound_appearance: str
    what_humans_hear: str
    what_humans_cannot_hear: str
    scientific_methods: str
    try_it_yourself: str

class NatureLanguageBook:
    """
    FEATURE 9: LEARN NATURE LANGUAGE
    Interactive educational curriculum.
    """
    
    def __init__(self):
        self.lessons = [
            Lesson(
                lesson_id="lesson_01_honeybee",
                title="The Language of the Honeybee: Flight Beats and Waggle Vibrations",
                organism="Apis mellifera (Western Honeybee)",
                what_we_know="Honeybees communicate distance and angle to pollen sources via rhythmic waggle dances inside the dark hive.",
                sound_appearance="A solid 240 Hz horizontal fundamental line with dense harmonic overtones up to 1.2 kHz.",
                what_humans_hear="A continuous low pitch hum or buzzing sound.",
                what_humans_cannot_hear="Sub-audible substrate vibrations transmitted through the honeycomb and micro-pulses between wing strokes.",
                scientific_methods="Laser Doppler vibrometry and high-sensitivity piezoelectric contact sensors on comb cells.",
                try_it_yourself="Point NATURA LIVE at a flower bed in morning light. Observe the fundamental frequency lock onto 240 Hz."
            ),
            Lesson(
                lesson_id="lesson_02_tree_cricket",
                title="The Thermometer of the Dusk: Tree Cricket Stridulation",
                organism="Oecanthus fultoni (Snowy Tree Cricket)",
                what_we_know="Tree crickets rub their wings together (stridulation). Chirp rate is directly proportional to temperature (Dolbear Law).",
                sound_appearance="Narrow resonant band centered between 4.8 kHz and 5.6 kHz with steady rhythmic pulsation.",
                what_humans_hear="A high-pitched musical rhythmic chirping.",
                what_humans_cannot_hear="Micro-harmonic friction teeth transients that exceed 16 kHz.",
                scientific_methods="Calibrated acoustic microphones paired with synchronized thermal sensors.",
                try_it_yourself="Use NATURA Dolbear calculator: count chirps in 15 seconds + 40 = temperature in Fahrenheit."
            ),
            Lesson(
                lesson_id="lesson_03_bat_echolocation",
                title="Sculpting Space with Echoes: Microbat Ultrasonic Radar",
                organism="Pipistrellus pipistrellus (Common Pipistrelle)",
                what_we_know="Bats emit ultrasonic frequency sweeps to create high-resolution topological maps of prey in pitch blackness.",
                sound_appearance="Steep diagonal downward chirps from 48 kHz to 28 kHz lasting 3-5 milliseconds.",
                what_humans_hear="Total silence (human hearing upper bound is ~20 kHz).",
                what_humans_cannot_hear="The entire echolocation sweep and rapid terminal feeding buzz.",
                scientific_methods="High-bandwidth ultrasonic microphones (96 kHz sampling) and heterodyne frequency divide mixers.",
                try_it_yourself="Activate NATURA 'Hear the Unheard' sonifier at dusk near streetlights or ponds."
            ),
            Lesson(
                lesson_id="lesson_04_plant_cavitation",
                title="Thirst and Acoustics: Ultrasonic Plant Cavitation",
                organism="Xylem Vascular Plants (Flora)",
                what_we_know="Drought-stressed plants experience cavitation: air bubbles burst within water-transporting xylem conduits.",
                sound_appearance="Acoustic impulsive clicks in the 20 kHz - 100 kHz range.",
                what_humans_hear="Silence; the plant appears completely motionless.",
                what_humans_cannot_hear="Cavitation shockwaves vibrating the stem wall.",
                scientific_methods="Broadband acoustic emission sensors clamped to the plant stem with ultrasound preamplifiers.",
                try_it_yourself="Connect the NATURA Probe contact sensor to an unwatered potted plant to detect micro-vibrations."
            )
        ]

    def get_all_lessons(self) -> List[Lesson]:
        return self.lessons

    def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        for l in self.lessons:
            if l.lesson_id == lesson_id:
                return l
        return None
