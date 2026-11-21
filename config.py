# IndiePulse Configuration
import os
from pathlib import Path

# Load .env file automatically if present
ENV_PATH = Path(__file__).resolve().parent / ".env"
if ENV_PATH.exists():
    try:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val
    except Exception as e:
        print(f"[Config] Notice reading .env: {e}")

# -------------------------------------------------------------
# Core Operational Thresholds
# -------------------------------------------------------------
SPATIAL_DEDUP_RADIUS_METERS: float = 200.0       # 200m spatial clustering
TEMPORAL_DEDUP_WINDOW_MINUTES: float = 45.0      # 45 minutes time-window

# Triple-Check Rabies Consensus Parameters
TEMPORAL_BLOCK_DURATION_SEC: float = 5.0        # 5 seconds per frame block
NUM_TEMPORAL_BLOCKS: int = 3                    # t1, t2, t3
RABIES_CONSENSUS_THRESHOLD: float = 0.85        # >85% required on ALL 3 blocks

# Municipal SLA Timers
RABIES_SLA_MINUTES: int = 45                    # 45 Minutes for Rabies Red Alert
STRAY_MEDICAL_SLA_HOURS: int = 12               # 12 Hours for Stray Medical Aid
GEOFENCE_RADIUS_METERS: float = 500.0           # 500m Ward safety perimeter

# Vision Model Configuration
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
DEFAULT_MODEL: str = "gemini-2.5-flash"
MOCK_FALLBACK: bool = True                      # Fallback smoothly if offline or no API key
