import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, List

@dataclass
class NatureMoment:
    moment_id: str
    title: str
    timestamp: float
    duration_sec: float
    video_summary: str
    original_audio_path: str
    enhanced_audio_path: str
    sonified_audio_path: str
    music_soundscape_path: str
    scientific_interpretation: str
    ai_captions: List[Dict[str, Any]]
    detected_species: List[str]
    confidence_score: float
    location_name: str
    coordinates: Dict[str, float]

class NatureCinema:
    """
    FEATURE 5: NATURE CINEMA
    Synthesizes a complete Nature Moment from multimodal observations.
    """
    
    def assemble_moment(self,
                        moment_id: str,
                        title: str,
                        duration_sec: float,
                        video_desc: str,
                        species: List[str],
                        confidence: float,
                        scientific_interp: str,
                        location: str,
                        lat: float,
                        lon: float) -> NatureMoment:
        
        captions = [
            {"time_sec": 0.0, "text": "NATURA LIVE: Multimodal acoustic sensing initiated."},
            {"time_sec": 1.5, "text": f"Subject Identified: {', '.join(species)} (Confidence: {confidence*100:.0f}%)."},
            {"time_sec": 3.5, "text": "Heterodyne translation active: Inaudible acoustic harmonics sonified into human range."},
            {"time_sec": 5.5, "text": "Nature Composer: Bioacoustic frequency mapped to ambient organic soundscape."}
        ]
        
        return NatureMoment(
            moment_id=moment_id,
            title=title,
            timestamp=time.time(),
            duration_sec=duration_sec,
            video_summary=video_desc,
            original_audio_path=f"recordings/{moment_id}_original.wav",
            enhanced_audio_path=f"recordings/{moment_id}_enhanced.wav",
            sonified_audio_path=f"recordings/{moment_id}_sonified.wav",
            music_soundscape_path=f"recordings/{moment_id}_composition.wav",
            scientific_interpretation=scientific_interp,
            ai_captions=captions,
            detected_species=species,
            confidence_score=confidence,
            location_name=location,
            coordinates={"lat": lat, "lon": lon}
        )
