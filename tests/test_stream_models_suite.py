"""
IndiePulse — Smartphone Streaming & Transfer Learning Direct Test Suite
Directly exercises endpoint handlers in api.main:
1. get_active_streams()
2. register_phone_stream(...)
3. push_stream_frame(...)
4. convert_snapshot_to_dossier(...)
5. get_model_statistics()
6. update_model_configuration(...)
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import api.main as app_main

def run_suite():
    print("=" * 70, flush=True)
    print("INDIEPULSE — DIRECT STREAMING & MODEL GOVERNANCE VERIFICATION", flush=True)
    print("=" * 70, flush=True)

    # 1. Test get_active_streams
    streams = app_main.get_active_streams()
    assert len(streams) >= 2, f"Expected at least 2 active streams, got {len(streams)}"
    assert any(s["id"] == "PHONE-CAM-01" for s in streams)
    print(f"[PASS] 1. get_active_streams() -> {len(streams)} active streams retrieved.", flush=True)

    # 2. Test register_phone_stream
    reg = app_main.register_phone_stream(
        device_model="Samsung Galaxy S24 Ultra",
        resolution="1280x720",
        fps=30,
        battery_pct=88
    )
    assert reg["status"] == "REGISTERED"
    stream_id = reg["stream_id"]
    print(f"[PASS] 2. register_phone_stream() -> Created edge stream: {stream_id}", flush=True)

    # 3. Test push_stream_frame
    res_frame = app_main.push_stream_frame(
        stream_id=stream_id,
        frame_b64="data:image/jpeg;base64,/9j/4AAQSkZJRg==",
        battery_pct=86,
        fps=28,
        latency_ms=34.2
    )
    assert res_frame["status"] == "PROCESSED"
    assert "cv_result" in res_frame
    print(f"[PASS] 3. push_stream_frame() -> Processed frame: {res_frame['cv_result']['predicted_class']} ({res_frame['cv_result']['confidence']*100:.1f}%)", flush=True)

    # 4. Test convert_snapshot_to_dossier
    dossier_res = app_main.convert_snapshot_to_dossier(
        stream_id=stream_id,
        landmark="Sector 14 Metro Station",
        district="South West Delhi",
        state="Delhi"
    )
    assert dossier_res["status"] == "CASE_CREATED"
    dossier = dossier_res["dossier"]
    assert dossier["id"].startswith("CASE-STREAM-")
    assert dossier["landmark"] == "Sector 14 Metro Station"
    print(f"[PASS] 4. convert_snapshot_to_dossier() -> Case Created: {dossier['id']} (Tier: {dossier['tier']})", flush=True)

    # 5. Test get_model_statistics
    stats = app_main.get_model_statistics()
    assert "cv_model" in stats
    assert "audio_model" in stats
    assert stats["cv_model"]["eval_metrics"]["accuracy"] >= 0.90
    print(f"[PASS] 5. get_model_statistics() -> CV Acc: {stats['cv_model']['eval_metrics']['accuracy']*100:.1f}%, Audio F1: {stats['audio_model']['eval_metrics']['f1_score']*100:.1f}%", flush=True)

    # 6. Test update_model_configuration
    cfg_res = app_main.update_model_configuration(
        rabies_threshold=0.88,
        ataxia_sensitivity=0.82,
        audio_phonation_threshold=0.75,
        active_backbone="yolov8n_cls"
    )
    assert cfg_res["status"] == "UPDATED"
    assert cfg_res["config"]["rabies_threshold"] == 0.88
    assert cfg_res["config"]["active_backbone"] == "yolov8n_cls"
    print(f"[PASS] 6. update_model_configuration() -> Rabies Cutoff: {cfg_res['config']['rabies_threshold']}, Backbone: {cfg_res['config']['active_backbone']}", flush=True)

    print("=" * 70, flush=True)
    print("ALL 6/6 STREAMING & MODEL GOVERNANCE TESTS PASSED (0 FAILURES)", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    run_suite()
