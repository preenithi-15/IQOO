import sqlite3
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

class NatureStorage:
    """
    FEATURE 7: NATURE ALBUM PERSISTENCE
    Stores Nature Moments, acoustic telemetry, and discoveries in SQLite and JSON.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            self.base_dir = Path(os.environ.get("NATURA_DATA_DIR", ".")) / "data_store"
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(self.base_dir / "natura.db")
        else:
            self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS nature_moments (
            moment_id TEXT PRIMARY KEY,
            title TEXT,
            timestamp REAL,
            duration_sec REAL,
            video_summary TEXT,
            scientific_interpretation TEXT,
            confidence_score REAL,
            location_name TEXT,
            latitude REAL,
            longitude REAL,
            species_json TEXT,
            captions_json TEXT
        )
        """)
        conn.commit()
        conn.close()

    def save_moment(self, moment_dict: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        INSERT OR REPLACE INTO nature_moments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            moment_dict["moment_id"],
            moment_dict["title"],
            moment_dict["timestamp"],
            moment_dict["duration_sec"],
            moment_dict["video_summary"],
            moment_dict["scientific_interpretation"],
            moment_dict["confidence_score"],
            moment_dict["location_name"],
            moment_dict["coordinates"]["lat"],
            moment_dict["coordinates"]["lon"],
            json.dumps(moment_dict["detected_species"]),
            json.dumps(moment_dict["ai_captions"])
        ))
        conn.commit()
        conn.close()

    def list_moments(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        SELECT moment_id, title, timestamp, duration_sec, video_summary, 
               scientific_interpretation, confidence_score, location_name, 
               latitude, longitude, species_json, captions_json 
        FROM nature_moments ORDER BY timestamp DESC
        """)
        rows = cur.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            results.append({
                "moment_id": r[0],
                "title": r[1],
                "timestamp": r[2],
                "duration_sec": r[3],
                "video_summary": r[4],
                "scientific_interpretation": r[5],
                "confidence_score": r[6],
                "location_name": r[7],
                "coordinates": {"lat": r[8], "lon": r[9]},
                "detected_species": json.loads(r[10]),
                "ai_captions": json.loads(r[11])
            })
        return results
