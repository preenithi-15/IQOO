import json
from typing import List, Dict, Any

class CitizenScienceExporter:
    """
    ADVANCED FEATURE: CITIZEN-SCIENCE DATABASE EXPORTER
    Exports collected bioacoustic observations in Darwin Core and GeoJSON standards.
    """
    
    def export_geojson(self, moments: List[Dict[str, Any]]) -> str:
        features = []
        for m in moments:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [m["coordinates"]["lon"], m["coordinates"]["lat"]]
                },
                "properties": {
                    "moment_id": m["moment_id"],
                    "title": m["title"],
                    "scientific_interpretation": m["scientific_interpretation"],
                    "confidence": m["confidence_score"],
                    "species": m["detected_species"],
                    "timestamp": m["timestamp"]
                }
            })
            
        geojson_doc = {
            "type": "FeatureCollection",
            "metadata": {
                "platform": "NATURA iQOO 15 Bioacoustic Explorer",
                "standard": "Darwin Core / OGC GeoJSON"
            },
            "features": features
        }
        return json.dumps(geojson_doc, indent=2)
