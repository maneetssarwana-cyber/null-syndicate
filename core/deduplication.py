import math
from datetime import datetime
from typing import List, Dict, Optional, Any

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two GPS coordinates in meters.
    """
    R = 6371000.0  # Earth's mean radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class SpatioTemporalDeduplicator:
    """
    Groups reports originating within a configured radius (e.g. 200m)
    and time window (e.g. 45 min) into a single consolidated multi-angle dossier.
    """
    def __init__(self, radius_meters: float = 200.0, window_minutes: float = 45.0):
        self.radius_meters = radius_meters
        self.window_minutes = window_minutes

    def find_matching_dossier(
        self, 
        latitude: float, 
        longitude: float, 
        timestamp: datetime, 
        dossiers: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        for d in dossiers:
            # Skip dossiers that are already resolved or closed
            if d.get("status") in ["RESOLVED", "CLOSED"]:
                continue

            dist = haversine_distance_meters(latitude, longitude, d["latitude"], d["longitude"])
            created_at = d["created_at"]
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            
            time_diff_min = abs((timestamp - created_at).total_seconds()) / 60.0

            if dist <= self.radius_meters and time_diff_min <= self.window_minutes:
                return d

        return None
