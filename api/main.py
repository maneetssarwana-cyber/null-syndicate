import os
import uuid
import shutil
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import (
    SPATIAL_DEDUP_RADIUS_METERS,
    TEMPORAL_DEDUP_WINDOW_MINUTES,
    RABIES_SLA_MINUTES,
    STRAY_MEDICAL_SLA_HOURS,
    GEOFENCE_RADIUS_METERS,
    RABIES_CONSENSUS_THRESHOLD,
    GEMINI_API_KEY,
    GOOGLE_MAPS_API_KEY
)
from core.deduplication import SpatioTemporalDeduplicator
from core.consensus import TripleCheckRabiesConsensus
from core.vision_engine import IndiePulseVisionEngine
from core.audio_engine import IndiePulseAudioEngine
from core.integrity_engine import IndiePulseIntegrityEngine
from core.sla_manager import SLAManager

app = FastAPI(
    title="IndiePulse (IndieGuard Engine)",
    description="Smart City Stray Dog Care, Rabies Warning & Municipal Tracking System",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Engines
deduplicator = SpatioTemporalDeduplicator(
    radius_meters=SPATIAL_DEDUP_RADIUS_METERS,
    window_minutes=TEMPORAL_DEDUP_WINDOW_MINUTES
)
consensus_engine = TripleCheckRabiesConsensus(threshold=RABIES_CONSENSUS_THRESHOLD)
vision_engine = IndiePulseVisionEngine(api_key=GEMINI_API_KEY)
audio_engine = IndiePulseAudioEngine(api_key=GEMINI_API_KEY)
integrity_engine = IndiePulseIntegrityEngine(upload_dir=UPLOAD_DIR)
sla_manager = SLAManager(
    rabies_sla_minutes=RABIES_SLA_MINUTES,
    medical_sla_hours=STRAY_MEDICAL_SLA_HOURS
)

DOSSIERS: List[Dict[str, Any]] = []

def seed_demo_cases():
    now = datetime.utcnow()
    global DOSSIERS
    DOSSIERS = [
        {
            "id": "CASE-RABIES-8941",
            "state": "Delhi",
            "district": "New Delhi",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "landmark": "Near Metro Station Gate 2, North Ring Road",
            "tier": "TIER_1_RABIES_QUARANTINE",
            "status": "DISPATCH_PENDING",
            "consensus": {
                "consensus_reached": True,
                "tier": "TIER_1_RABIES_QUARANTINE",
                "average_confidence": 0.94,
                "block_confidences": [0.94, 0.91, 0.96],
                "reason": "All 3 video checks confirmed severe rabies symptoms (>85% certainty).",
                "dispatch_unit": "Quarantine Net Squad #1 (Catch Poles & Safety Gear)",
                "required_equipment": [
                    "Bite-Proof Kevlar Sleeves & Gloves",
                    "Humane Animal Catch Pole",
                    "Safe Quarantine Enclosure"
                ],
                "geofence_alert": {
                    "enabled": True,
                    "radius_meters": 500,
                    "message": "SAFETY WARNING: Suspected rabid animal reported within 500m. Please keep children and pets indoors."
                },
                "sla_minutes": 45
            },
            "temporal_blocks": [
                {
                    "block": 1,
                    "rabies_confidence": 0.94,
                    "saliva_foaming": True,
                    "dropped_jaw": True,
                    "ataxia": True,
                    "notes": "First 5 Seconds: Heavy white foamy saliva dripping, lower jaw hanging open."
                },
                {
                    "block": 2,
                    "rabies_confidence": 0.91,
                    "saliva_foaming": True,
                    "dropped_jaw": True,
                    "ataxia": True,
                    "notes": "Next 5 Seconds: Severe stumbling, loss of back-leg balance, biting at thin air."
                },
                {
                    "block": 3,
                    "rabies_confidence": 0.96,
                    "saliva_foaming": True,
                    "dropped_jaw": True,
                    "ataxia": True,
                    "notes": "Final 5 Seconds: Heavy saliva continues. Dog unable to coordinate walking."
                }
            ],
            "audio_analysis": {
                "has_audio": True,
                "classification": "HOARSE_RABIES_HOWL",
                "label": "Laryngeal Paralysis (Rabies Howl)",
                "icon": "alert-triangle",
                "badge_color": "red",
                "laryngeal_paralysis": True,
                "pain_whining": False,
                "confidence": 0.95,
                "notes": "Acoustic Spectrum: Low-frequency subharmonic rasping confirming laryngeal vocal cord paresis ('rabies voice')."
            },
            "integrity_analysis": {
                "status": "VERIFIED_AUTHENTIC",
                "badge_color": "green",
                "badge_label": "Verified Authentic Live Capture",
                "integrity_score": 0.98,
                "phash": "c4d2e8b1a3f01948",
                "is_recycled": False,
                "freshness": {"fresh": True, "source_age_hours": 0.1, "status": "FRESH_LIVE_CAPTURE"},
                "geo_verification": {"consistent": True, "status": "VERIFIED_WITHIN_BOUNDS", "notes": "Coordinates verified in New Delhi ward perimeter."},
                "flags": [],
                "notes": "Verified authentic live device capture. Coordinates match Ward 4 grid. Zero pHash collision."
            },
            "sources": [
                {"source_type": "Street Camera #08", "reporter": "City Surveillance Grid", "timestamp": now.isoformat()},
                {"source_type": "Citizen Phone Upload", "reporter": "+91 98765 43210", "timestamp": (now + timedelta(minutes=3)).isoformat()}
            ],
            "created_at": now.isoformat(),
            "sla_deadline": (now + timedelta(minutes=45)).isoformat(),
            "is_escalated": False,
            "dispatched_to": None
        },
        {
            "id": "CASE-VET-3312",
            "state": "Delhi",
            "district": "Central Delhi",
            "latitude": 28.6185,
            "longitude": 77.2140,
            "landmark": "Market Alley, Behind Post Office, Ward 7",
            "tier": "TIER_2_STRAY_MEDICAL_AID",
            "status": "DISPATCHED",
            "consensus": {
                "consensus_reached": False,
                "tier": "TIER_2_STRAY_MEDICAL_AID",
                "average_confidence": 0.08,
                "block_confidences": [0.12, 0.08, 0.05],
                "reason": "Not Rabies. Dog has a leg injury and needs veterinary medical attention.",
                "condition_diagnosed": "Leg Injury / Bone Fracture (Needs Splint & Dressing)",
                "dispatch_unit": "Mobile Vet Clinic Van #2",
                "required_equipment": ["Bandages & Splints", "Pain Relief Medicine", "Antiseptic Spray"],
                "geofence_alert": {"enabled": False, "radius_meters": 0},
                "sla_minutes": 720
            },
            "temporal_blocks": [
                {
                    "block": 1,
                    "rabies_confidence": 0.12,
                    "saliva_foaming": False,
                    "dropped_jaw": False,
                    "ataxia": False,
                    "notes": "First 5 Seconds: Dog holding up its right hind leg. Clean saliva, no foaming."
                },
                {
                    "block": 2,
                    "rabies_confidence": 0.08,
                    "saliva_foaming": False,
                    "dropped_jaw": False,
                    "ataxia": False,
                    "notes": "Next 5 Seconds: Mentally alert and calm. Responsive when called."
                },
                {
                    "block": 3,
                    "rabies_confidence": 0.05,
                    "saliva_foaming": False,
                    "dropped_jaw": False,
                    "ataxia": False,
                    "notes": "Final 5 Seconds: Sitting down resting. No signs of rabies."
                }
            ],
            "audio_analysis": {
                "has_audio": True,
                "classification": "ACUTE_PAIN_WHINE",
                "label": "Acute Pain Whine (Orthopedic Trauma)",
                "icon": "volume-2",
                "badge_color": "amber",
                "laryngeal_paralysis": False,
                "pain_whining": True,
                "confidence": 0.12,
                "notes": "Acoustic Spectrum: High-frequency pain whimpering (>2.2 kHz) and distress yelps; vocal cords healthy."
            },
            "integrity_analysis": {
                "status": "VERIFIED_AUTHENTIC",
                "badge_color": "green",
                "badge_label": "Verified Authentic Citizen Upload",
                "integrity_score": 0.95,
                "phash": "b8a1c9d2f4e30871",
                "is_recycled": False,
                "freshness": {"fresh": True, "source_age_hours": 1.0, "status": "FRESH_LIVE_CAPTURE"},
                "geo_verification": {"consistent": True, "status": "VERIFIED_WITHIN_BOUNDS", "notes": "Coordinates verified in Central Delhi perimeter."},
                "flags": [],
                "notes": "Verified authentic live citizen upload."
            },
            "sources": [
                {"source_type": "Citizen Phone Upload", "reporter": "Local Animal Caretaker", "timestamp": (now - timedelta(hours=1)).isoformat()}
            ],
            "created_at": (now - timedelta(hours=1)).isoformat(),
            "sla_deadline": (now + timedelta(hours=11)).isoformat(),
            "is_escalated": False,
            "dispatched_to": "Mobile Vet Clinic Van #2",
            "eta_minutes": 6
        }
    ]

seed_demo_cases()

# Valid video extensions
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".3gp"}
DISALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".aac", ".ogg", ".m4a", ".flac"}

@app.get("/api/health")
def health_check():
    return {
        "status": "ONLINE",
        "service": "IndiePulse (IndieGuard Engine)",
        "gemini_live_connected": vision_engine.use_live_api,
        "has_gemini_key": bool(vision_engine.api_key),
        "active_cases": len(DOSSIERS)
    }

@app.get("/api/settings/gemini_status")
def get_gemini_status():
    """Returns current Gemini API key status and masked representation."""
    return {
        "status": "CONFIGURED" if vision_engine.api_key else "NOT_CONFIGURED",
        "gemini_live_connected": vision_engine.use_live_api,
        "has_key": bool(vision_engine.api_key),
        "masked_key": vision_engine.get_masked_key()
    }

@app.post("/api/settings/gemini_test")
def test_gemini_api():
    """Performs live connectivity check against Google Gemini servers."""
    return vision_engine.test_connection()

@app.post("/api/settings/gemini_key")
def set_gemini_key(api_key: str = Form(...)):
    """Allows setting the Gemini API key live from the UI and persists it to .env."""
    global vision_engine, audio_engine
    cleaned_key = api_key.strip()
    vision_engine = IndiePulseVisionEngine(api_key=cleaned_key)
    audio_engine = IndiePulseAudioEngine(api_key=cleaned_key)
    
    # Persist to .env file
    env_file = BASE_DIR / ".env"
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"# IndiePulse Environment Configuration\nGEMINI_API_KEY={cleaned_key}\n")
    except Exception as e:
        print(f"[Main] Warning saving .env: {e}")

    # Test the key
    test_result = vision_engine.test_connection()
    return {
        "status": "SUCCESS" if test_result.get("success") else "SAVED_WITH_NOTICE",
        "gemini_live_connected": vision_engine.use_live_api,
        "masked_key": vision_engine.get_masked_key(),
        "test_result": test_result,
        "message": "Gemini API key saved and activated for Vision & Audio engines!"
    }

@app.get("/api/location/status")
def get_location_api_status():
    """Returns Google Maps API integration status."""
    has_key = bool(GOOGLE_MAPS_API_KEY)
    masked = f"{GOOGLE_MAPS_API_KEY[:6]}••••••••{GOOGLE_MAPS_API_KEY[-4:]}" if (has_key and len(GOOGLE_MAPS_API_KEY) > 8) else ""
    return {
        "google_maps_configured": has_key,
        "masked_key": masked,
        "fallback_provider": "OpenStreetMap / Nominatim (Free, No Billing Required)"
    }

@app.get("/api/location/reverse_geocode")
def reverse_geocode(lat: float, lon: float):
    """
    Reverse geocodes coordinates to street, district, and state.
    Uses Google Maps Geocoding API if key is present and billing is active.
    Seamlessly falls back to OpenStreetMap / Nominatim.
    """
    if GOOGLE_MAPS_API_KEY:
        try:
            url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={GOOGLE_MAPS_API_KEY}"
            req = urllib.request.Request(url, headers={"User-Agent": "IndiePulse/2.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read().decode("utf-8"))
                if data.get("status") == "OK" and data.get("results"):
                    result = data["results"][0]
                    address = result.get("formatted_address", "")
                    
                    state = ""
                    district = ""
                    landmark = ""
                    for comp in result.get("address_components", []):
                        types = comp.get("types", [])
                        if "administrative_area_level_1" in types:
                            state = comp.get("long_name", "")
                        elif "administrative_area_level_2" in types:
                            district = comp.get("long_name", "")
                        elif "sublocality" in types or "route" in types or "neighborhood" in types:
                            if not landmark:
                                landmark = comp.get("long_name", "")

                    return {
                        "success": True,
                        "provider": "google_maps",
                        "address": address,
                        "landmark": landmark or (address.split(",")[0] if address else "Detected Location"),
                        "district": district or "Urban District",
                        "state": state or "State",
                        "latitude": lat,
                        "longitude": lon
                    }
                else:
                    print(f"[LocationAPI] Google Maps notice ({data.get('status')}): {data.get('error_message')}. Using high-precision Nominatim fallback.")
        except Exception as e:
            print(f"[LocationAPI] Google Maps notice: {e}. Using high-precision Nominatim fallback.")

    # High-precision Nominatim / OpenStreetMap fallback
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": "IndiePulse-Animal-Rescue/2.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode("utf-8"))
            addr_info = data.get("address", {})
            
            state = addr_info.get("state", "Delhi")
            district = (
                addr_info.get("city") or
                addr_info.get("state_district") or
                addr_info.get("county") or
                addr_info.get("suburb") or
                "Central District"
            )
            road = addr_info.get("road") or addr_info.get("neighbourhood") or addr_info.get("suburb") or ""
            amenity = addr_info.get("amenity") or addr_info.get("building") or ""
            landmark = f"{amenity} {road}".strip() if (amenity or road) else data.get("display_name", "").split(",")[0]
            
            return {
                "success": True,
                "provider": "nominatim_fallback",
                "address": data.get("display_name", f"{lat}, {lon}"),
                "landmark": landmark or "Live GPS Pinned Locality",
                "district": district,
                "state": state,
                "latitude": lat,
                "longitude": lon
            }
    except Exception as e:
        print(f"[LocationAPI] Fallback error: {e}")

    return {
        "success": True,
        "provider": "local_coordinates",
        "address": f"GPS Pin ({round(lat, 4)}, {round(lon, 4)})",
        "landmark": "Detected Device GPS Location",
        "district": "Detected District",
        "state": "Detected State",
        "latitude": lat,
        "longitude": lon
    }

@app.get("/api/dossiers")
def get_all_dossiers():
    now = datetime.utcnow()
    augmented = []
    for d in DOSSIERS:
        sla_info = sla_manager.check_sla_status(d, now)
        if sla_info["is_breached"] and not d.get("is_escalated"):
            d["is_escalated"] = True
            d["status"] = "ESCALATED_TO_DISTRICT_MAGISTRATE"
            
        d_copy = dict(d)
        d_copy["sla_info"] = sla_info
        augmented.append(d_copy)
    return augmented

@app.post("/api/ingest")
async def ingest_report(
    source_type: str = Form("Citizen Phone Upload"),
    state: Optional[str] = Form("Delhi"),
    district: Optional[str] = Form("New Delhi"),
    latitude: float = Form(28.6145),
    longitude: float = Form(77.2095),
    landmark: Optional[str] = Form("Main Market Road"),
    reporter: Optional[str] = Form("Citizen"),
    video_file: Optional[UploadFile] = File(None)
):
    now = datetime.utcnow()

    # Strict File Validation
    saved_filename = "recorded_clip.mp4"
    if video_file:
        file_ext = Path(video_file.filename).suffix.lower()

        # Specific user requirement: Error on MP3 or audio
        if file_ext in DISALLOWED_AUDIO_EXTENSIONS or (video_file.content_type and "audio" in video_file.content_type):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format! Audio files (.mp3, .wav) cannot be triaged. Please upload a video (.mp4, .mov, .avi) showing the dog's movement, face, or injury."
            )

        if file_ext not in ALLOWED_VIDEO_EXTENSIONS and file_ext != "":
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format '{file_ext}'. Please upload a valid video file (.mp4, .mov, .avi)."
            )

        file_path = UPLOAD_DIR / f"{uuid.uuid4().hex[:8]}_{video_file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        saved_filename = file_path.name

    # 1. 200-Meter Smart Merge (Deduplication)
    existing_dossier = deduplicator.find_matching_dossier(latitude, longitude, now, DOSSIERS)

    if existing_dossier:
        new_source = {
            "source_type": source_type,
            "reporter": reporter,
            "filename": saved_filename,
            "timestamp": now.isoformat()
        }
        existing_dossier["sources"].append(new_source)
        return {
            "status": "MERGED_INTO_EXISTING_CASE",
            "dossier_id": existing_dossier["id"],
            "message": "A report was already active on this exact street (within 200m). Your video has been added to the case file as an additional camera angle!",
            "total_angles": len(existing_dossier["sources"]),
            "dossier": existing_dossier
        }

    video_full_path = str(UPLOAD_DIR / saved_filename)

    # 2. Input Integrity & Anti-Spoofing Verification (pHash, Freshness, Geo Bounds)
    integrity_analysis = integrity_engine.verify_media(
        video_full_path,
        state=state or "Delhi",
        district=district or "New Delhi",
        lat=latitude,
        lon=longitude
    )

    # 3. Vision Triage (3-Step Video Check)
    block_evaluations = vision_engine.analyze_video(video_full_path, filename_hint=saved_filename)

    # 4. Audio Triage (Vocalization & Laryngeal Paralysis Check)
    audio_analysis = audio_engine.analyze_audio(video_full_path, filename_hint=saved_filename)

    # 5. Multimodal Safety Consensus with Anti-Hallucination Guardrails
    consensus = consensus_engine.evaluate(
        block_evaluations,
        audio_analysis=audio_analysis,
        integrity_analysis=integrity_analysis
    )
    tier = consensus["tier"]
    deadline = sla_manager.calculate_deadline(tier, now)

    new_dossier = {
        "id": f"CASE-{uuid.uuid4().hex[:6].upper()}",
        "state": state or "Delhi",
        "district": district or "New Delhi",
        "latitude": latitude,
        "longitude": longitude,
        "landmark": landmark,
        "tier": tier,
        "status": "DISPATCH_PENDING",
        "consensus": consensus,
        "temporal_blocks": block_evaluations,
        "audio_analysis": audio_analysis,
        "integrity_analysis": integrity_analysis,
        "sources": [
            {
                "source_type": source_type,
                "reporter": reporter,
                "filename": saved_filename,
                "timestamp": now.isoformat()
            }
        ],
        "created_at": now.isoformat(),
        "sla_deadline": deadline.isoformat(),
        "is_escalated": False,
        "dispatched_to": None
    }
    DOSSIERS.insert(0, new_dossier)

    return {
        "status": "NEW_CASE_REGISTERED",
        "dossier_id": new_dossier["id"],
        "tier": tier,
        "consensus": consensus,
        "sla_deadline": new_dossier["sla_deadline"],
        "dossier": new_dossier
    }

# Master Fleet Registry
FLEET_UNITS = [
    {
        "id": "UNIT-01",
        "name": "Quarantine Net Squad #1",
        "type": "QUARANTINE_SQUAD",
        "vehicle": "Isolation Enclosure Truck (DL-01-AB-1029)",
        "equipment": "Humane catch poles, Kevlar bite-proof suits, isolation cages",
        "base_station": "Central Ward 4 Depot",
        "status": "STANDBY", # STANDBY | EN_ROUTE | ON_SITE
        "assigned_case_id": None,
        "assigned_locality": None,
        "eta_minutes": None
    },
    {
        "id": "UNIT-02",
        "name": "Mobile Vet Clinic Van #2",
        "type": "MOBILE_VET",
        "vehicle": "Mobile Surgical Van (DL-07-VT-2034)",
        "equipment": "Splints, antiseptic wound dressing, pain relief injectables, surgical kit",
        "lead_officer": "Dr. Sharma (Veterinary Officer)",
        "base_station": "Ward 7 Dispensary",
        "status": "EN_ROUTE",
        "assigned_case_id": "CASE-VET-3312",
        "assigned_locality": "Market Alley, Behind Post Office",
        "eta_minutes": 6
    },
    {
        "id": "UNIT-03",
        "name": "Rapid Response Van #3",
        "type": "RAPID_RESPONSE",
        "vehicle": "Multi-utility Rescue Van (DL-02-CD-4421)",
        "equipment": "Hydration tanks, animal stretchers, emergency first aid",
        "base_station": "Civic Centre Hub",
        "status": "STANDBY",
        "assigned_case_id": None,
        "assigned_locality": None,
        "eta_minutes": None
    }
]

@app.get("/api/fleet")
def get_fleet_status():
    """Returns live fleet status for both municipality dispatchers and citizens."""
    return FLEET_UNITS

@app.post("/api/dossiers/{dossier_id}/dispatch")
def dispatch_responder(
    dossier_id: str,
    responder_name: str = Form("Quarantine Net Squad #1"),
    eta_minutes: int = Form(8),
    notes: Optional[str] = Form("Dispatched with full emergency safety equipment.")
):
    now = datetime.utcnow()
    target_dossier = None
    for d in DOSSIERS:
        if d["id"] == dossier_id:
            d["status"] = "DISPATCHED"
            d["dispatched_to"] = responder_name
            d["dispatched_at"] = now.isoformat()
            d["eta_minutes"] = eta_minutes
            d["dispatch_notes"] = notes
            target_dossier = d
            break

    if not target_dossier:
        raise HTTPException(status_code=404, detail="Case not found")

    # Update corresponding fleet unit
    for unit in FLEET_UNITS:
        if unit["name"].lower() in responder_name.lower() or responder_name.lower() in unit["name"].lower():
            unit["status"] = "EN_ROUTE"
            unit["assigned_case_id"] = dossier_id
            unit["assigned_locality"] = target_dossier.get("landmark", "Ward Area")
            unit["eta_minutes"] = eta_minutes

    return {
        "status": "SUCCESS",
        "message": f"Successfully dispatched {responder_name} to {target_dossier.get('landmark')}",
        "dossier": target_dossier,
        "fleet": FLEET_UNITS
    }

@app.post("/api/dossiers/{dossier_id}/simulate_breach")
def simulate_sla_breach(dossier_id: str):
    for d in DOSSIERS:
        if d["id"] == dossier_id:
            d["sla_deadline"] = (datetime.utcnow() - timedelta(minutes=2)).isoformat()
            d["is_escalated"] = True
            d["status"] = "ESCALATED_TO_DISTRICT_MAGISTRATE"
            return {
                "status": "BREACH_TRIGGERED",
                "message": "City response time expired! Escalated to District Magistrate.",
                "dossier": d
            }
    raise HTTPException(status_code=404, detail="Case not found")

@app.post("/api/reset")
def reset_to_initial_demo():
    seed_demo_cases()
    # Reset fleet
    global FLEET_UNITS
    FLEET_UNITS[0]["status"] = "STANDBY"
    FLEET_UNITS[0]["assigned_case_id"] = None
    FLEET_UNITS[0]["assigned_locality"] = None
    FLEET_UNITS[0]["eta_minutes"] = None

    FLEET_UNITS[1]["status"] = "EN_ROUTE"
    FLEET_UNITS[1]["assigned_case_id"] = "CASE-VET-3312"
    FLEET_UNITS[1]["assigned_locality"] = "Market Alley, Behind Post Office"
    FLEET_UNITS[1]["eta_minutes"] = 6

    FLEET_UNITS[2]["status"] = "STANDBY"
    FLEET_UNITS[2]["assigned_case_id"] = None
    FLEET_UNITS[2]["assigned_locality"] = None
    FLEET_UNITS[2]["eta_minutes"] = None

    return {"status": "RESET_SUCCESSFUL", "total_cases": len(DOSSIERS)}

app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
