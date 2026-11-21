"""
Self-Verification Test Script for IndiePulse
Tests all core computational logic without requiring network or external APIs.
"""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime, timedelta

from core.deduplication import SpatioTemporalDeduplicator, haversine_distance_meters
from core.consensus import TripleCheckRabiesConsensus
from core.sla_manager import SLAManager
from core.vision_engine import IndiePulseVisionEngine

def run_tests():
    print("=" * 60)
    print(" 🐕 INDIEPULSE PIPELINE VERIFICATION SUITE")
    print("=" * 60)

    # 1. Test Haversine & Spatial Deduplication
    print("\n[TEST 1] Testing 200m Spatial Deduplication...")
    dedup = SpatioTemporalDeduplicator(radius_meters=200.0, window_minutes=45.0)

    p1 = (28.6139, 77.2090)
    # Point ~110 meters away
    p2_nearby = (28.6145, 77.2095)
    # Point ~600 meters away
    p3_far = (28.6190, 77.2140)

    d1 = haversine_distance_meters(p1[0], p1[1], p2_nearby[0], p2_nearby[1])
    d2 = haversine_distance_meters(p1[0], p1[1], p3_far[0], p3_far[1])

    print(f"  -> Distance P1 to P2 (nearby): {d1:.1f}m (Expected < 200m)")
    print(f"  -> Distance P1 to P3 (far):    {d2:.1f}m (Expected > 200m)")
    assert d1 <= 200.0, "Nearby point failed 200m threshold!"
    assert d2 > 200.0, "Far point should exceed 200m threshold!"

    now = datetime.utcnow()
    mock_dossiers = [{
        "id": "CASE-101",
        "latitude": p1[0],
        "longitude": p1[1],
        "created_at": now,
        "status": "ACTIVE"
    }]

    match = dedup.find_matching_dossier(p2_nearby[0], p2_nearby[1], now + timedelta(minutes=10), mock_dossiers)
    assert match is not None and match["id"] == "CASE-101", "Deduplication failed to group nearby sighting!"
    print("  ✓ Deduplication 200m grouping: PASSED")

    # 2. Test Triple-Check Rabies Consensus
    print("\n[TEST 2] Testing 'Triple-Check' Consensus Engine...")
    consensus = TripleCheckRabiesConsensus(threshold=0.85)

    # Scenario A: All 3 blocks exceed 85% with foaming/ataxia
    rabies_blocks = [
        {"block": 1, "rabies_confidence": 0.92, "saliva_foaming": True, "dropped_jaw": True, "ataxia": True},
        {"block": 2, "rabies_confidence": 0.88, "saliva_foaming": True, "dropped_jaw": True, "ataxia": True},
        {"block": 3, "rabies_confidence": 0.95, "saliva_foaming": True, "dropped_jaw": True, "ataxia": True}
    ]
    res_rabies = consensus.evaluate(rabies_blocks)
    assert res_rabies["consensus_reached"] is True, "Failed to reach consensus on rabid blocks!"
    assert res_rabies["tier"] == "TIER_1_RABIES_QUARANTINE", "Wrong tier assigned to rabies case!"
    print("  ✓ Triple-Check Rabies Red Alert (>85% on t1, t2, t3): PASSED")

    # Scenario B: False Alarm (Summer Panting) - t1 high due to panting, but t2 & t3 clear
    panting_blocks = [
        {"block": 1, "rabies_confidence": 0.70, "saliva_foaming": False, "dropped_jaw": False, "ataxia": False},
        {"block": 2, "rabies_confidence": 0.30, "saliva_foaming": False, "dropped_jaw": False, "ataxia": False},
        {"block": 3, "rabies_confidence": 0.15, "saliva_foaming": False, "dropped_jaw": False, "ataxia": False}
    ]
    res_panting = consensus.evaluate(panting_blocks)
    assert res_panting["consensus_reached"] is False, "False alarm wrongly flagged as rabies!"
    assert res_panting["tier"] == "TIER_2_STRAY_MEDICAL_AID", "Wrong tier for non-rabid dog!"
    print("  ✓ Summer Panting False Alarm Prevention: PASSED")

    # Scenario C: Physical Injury / Fracture
    injury_blocks = [
        {"block": 1, "rabies_confidence": 0.10, "saliva_foaming": False, "dropped_jaw": False, "ataxia": False, "physical_fracture": True},
        {"block": 2, "rabies_confidence": 0.05, "saliva_foaming": False, "dropped_jaw": False, "ataxia": False, "physical_fracture": True},
        {"block": 3, "rabies_confidence": 0.02, "saliva_foaming": False, "dropped_jaw": False, "ataxia": False, "physical_fracture": True}
    ]
    res_injury = consensus.evaluate(injury_blocks)
    assert res_injury["consensus_reached"] is False
    assert "Fracture" in res_injury["condition_diagnosed"]
    print("  ✓ Trauma / Fracture Differentiation: PASSED")

    # 3. Test SLA Manager & State Escalation
    print("\n[TEST 3] Testing SLA & State Escalation Engine...")
    sla = SLAManager(rabies_sla_minutes=45, medical_sla_hours=12)

    rabies_deadline = sla.calculate_deadline("TIER_1_RABIES_QUARANTINE", now)
    assert (rabies_deadline - now).total_seconds() == 45 * 60, "Rabies SLA must be 45 minutes!"

    # Test breach condition
    expired_dossier = {
        "id": "CASE-EXP-1234",
        "sla_deadline": (now - timedelta(minutes=5)).isoformat(),
        "status": "DISPATCH_PENDING",
        "is_escalated": False
    }
    status = sla.check_sla_status(expired_dossier, now)
    assert status["is_breached"] is True, "SLA breach not detected!"
    assert status["state_escalation"]["escalated"] is True, "State escalation not generated!"
    print("  ✓ 45-Min SLA & District Magistrate Auto-Escalation: PASSED")

    print("\n" + "=" * 60)
    print(" 🎯 ALL INDIEPULSE VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
