from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class ObservationStats:
    total_observations: int
    acoustic_events: int
    locations_explored: int
    nature_sessions: int
    soundscapes_created: int

class NatureObservationsTracker:
    """
    FEATURE 8: NATURE OBSERVATIONS
    Turns nature exploration into a lifelong journey.
    Example: 23 discoveries | 12 nature observations | 8 locations | 15 soundscapes.
    """
    
    def __init__(self):
        self.stats = ObservationStats(
            total_observations=17,
            acoustic_events=43,
            locations_explored=6,
            nature_sessions=21,
            soundscapes_created=15
        )

    def record_session(self, n_events: int, location: str, created_soundscape: bool = True):
        self.stats.nature_sessions += 1
        self.stats.acoustic_events += n_events
        self.stats.total_observations += 1
        if created_soundscape:
            self.stats.soundscapes_created += 1

    def get_summary(self) -> Dict[str, Any]:
        return {
            "nature_observations_recorded": self.stats.total_observations,
            "acoustic_events_detected": self.stats.acoustic_events,
            "locations_explored": self.stats.locations_explored,
            "nature_sessions": self.stats.nature_sessions,
            "soundscapes_composed": self.stats.soundscapes_created,
            "journey_level": "Level 4 — Bioacoustic Naturalist"
        }
