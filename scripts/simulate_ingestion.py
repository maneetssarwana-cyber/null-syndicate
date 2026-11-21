"""
CLI Ingestion Simulator for IndiePulse
Usage:
  python simulate_ingestion.py --type rabies
  python simulate_ingestion.py --type panting
  python simulate_ingestion.py --type injury
"""
import sys
import argparse
import requests

API_URL = "http://127.0.0.1:8000/api/ingest"

def send_test_report(case_type: str):
    cases = {
        "rabies": {
            "source_type": "CITIZEN_UPLOAD",
            "latitude": 28.6142,
            "longitude": 77.2092,
            "landmark": "Near Metro Gate 2, Ring Road",
            "reporter": "Citizen Dog Feeder",
            "filename": "rabid_dog_sample.mp4"
        },
        "panting": {
            "source_type": "CITIZEN_UPLOAD",
            "latitude": 28.6210,
            "longitude": 77.2180,
            "landmark": "Sector 9 Residential Park",
            "reporter": "Local Resident",
            "filename": "summer_panting_heat.mp4"
        },
        "injury": {
            "source_type": "CCTV_STREAM",
            "latitude": 28.6189,
            "longitude": 77.2145,
            "landmark": "Civic Market Alleyway",
            "reporter": "CCTV-NDEL-W7-14",
            "filename": "injured_puppy_fracture.mp4"
        }
    }

    target = cases.get(case_type.lower(), cases["rabies"])
    print(f"[*] Dispatching test ingestion: {case_type.upper()} to {API_URL}...")

    # Create dummy video bytes
    files = {"video_file": (target["filename"], b"simulated-video-stream", "video/mp4")}
    data = {
        "source_type": target["source_type"],
        "latitude": target["latitude"],
        "longitude": target["longitude"],
        "landmark": target["landmark"],
        "reporter": target["reporter"]
    }

    try:
        res = requests.post(API_URL, data=data, files=files)
        print(f"[+] Status Code: {res.status_code}")
        print(f"[+] Response:\n{res.text}")
    except Exception as e:
        print(f"[-] Error connecting to IndiePulse API: {e}")
        print("    Make sure the server is running on http://127.0.0.1:8000")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["rabies", "panting", "injury"], default="rabies")
    args = parser.parse_args()
    send_test_report(args.type)
