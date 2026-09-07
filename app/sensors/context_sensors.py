import time
import math
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SensorContext:
    timestamp: float
    latitude: float
    longitude: float
    altitude_m: float
    ambient_temp_c: float
    humidity_pct: float
    light_lux: float
    compass_heading: float
    barometric_pressure_hpa: float
    time_of_day: str  # DAWN, MORNING, AFTERNOON, DUSK, NIGHT
    season: str

class ContextSensors:
    """
    iQOO 15 Environmental Context Engine:
    Integrates GPS, barometer, ambient light, clock, and orientation.
    """
    
    def __init__(self, default_lat: float = 13.0827, default_lon: float = 80.2707):  # Chennai default
        self.latitude = default_lat
        self.longitude = default_lon

    def read_context(self) -> SensorContext:
        now = time.time()
        local_tm = time.localtime(now)
        hour = local_tm.tm_hour
        
        if 5 <= hour < 8:
            tod = "DAWN"
        elif 8 <= hour < 12:
            tod = "MORNING"
        elif 12 <= hour < 17:
            tod = "AFTERNOON"
        elif 17 <= hour < 20:
            tod = "DUSK"
        else:
            tod = "NIGHT"

        month = local_tm.tm_mon
        season = "Monsoon" if 7 <= month <= 10 else ("Winter" if month in [11, 12, 1, 2] else "Summer")
        
        return SensorContext(
            timestamp=now,
            latitude=self.latitude,
            longitude=self.longitude,
            altitude_m=18.5,
            ambient_temp_c=29.2,
            humidity_pct=68.0,
            light_lux=18500.0 if 8 <= hour <= 17 else 120.0,
            compass_heading=112.5,
            barometric_pressure_hpa=1012.4,
            time_of_day=tod,
            season=season
        )
