from typing import List, Dict, Any, Optional

class TripleCheckRabiesConsensus:
    """
    Evaluates 3 consecutive 5-second temporal blocks (t1, t2, t3) combined with
    acoustic vocalization analysis and input integrity checks.
    
    Includes Anti-Hallucination Guardrails:
    1. Cross-Modal Shield: Overrules visual false alarms when audio shows aerodynamic panting.
    2. Uncertainty Tiering (50%-84%): Puts ambiguous cases in manual vet review rather than false alarms.
    3. Anti-Spoofing Demotion: Downgrades recycled/suspicious videos to mandatory vet verification.
    """
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def evaluate(
        self,
        block_evaluations: List[Dict[str, Any]],
        audio_analysis: Optional[Dict[str, Any]] = None,
        integrity_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Multimodal Consensus Evaluation merging Visual Motion + Acoustic Phonation + Integrity.
        """
        audio = audio_analysis or {
            "has_audio": False,
            "classification": "SILENT_STREAM",
            "laryngeal_paralysis": False,
            "pain_whining": False,
            "confidence": 0.0
        }

        integrity = integrity_analysis or {
            "status": "VERIFIED_AUTHENTIC",
            "integrity_score": 1.0,
            "is_recycled": False
        }

        if not block_evaluations or len(block_evaluations) < 3:
            return {
                "consensus_reached": False,
                "tier": "TIER_2_STRAY_MEDICAL_AID",
                "average_confidence": 0.0,
                "reason": "Insufficient temporal blocks (need at least 3 blocks: t1, t2, t3).",
                "dispatch_unit": "GOVERNMENT_MOBILE_VET_DISPENSARY",
                "sla_minutes": 720,
                "audio_correlation": "No visual consensus; audio unlinked.",
                "hallucination_shield_activated": False
            }

        confidences = [b.get("rabies_confidence", 0.0) for b in block_evaluations[:3]]
        all_passed = all(c >= self.threshold for c in confidences)
        avg_confidence = sum(confidences) / len(confidences)

        # Check for persistent visual salivation and ataxia across blocks
        persistent_foaming = sum(1 for b in block_evaluations if b.get("saliva_foaming")) >= 2
        persistent_ataxia = sum(1 for b in block_evaluations if b.get("ataxia")) >= 2
        laryngeal_howl = audio.get("laryngeal_paralysis", False)
        is_aerodynamic_panting = audio.get("classification") == "NORMAL_SUMMER_PANTING"
        is_suspicious_media = integrity.get("status") == "RECYCLED_OR_SUSPICIOUS"

        # -------------------------------------------------------------
        # GUARD 1: ANTI-HALLUCINATION CROSS-MODAL OVERRULE
        # If audio proves aerodynamic panting without laryngeal paralysis:
        # -------------------------------------------------------------
        if is_aerodynamic_panting and not laryngeal_howl:
            return {
                "consensus_reached": False,
                "tier": "TIER_2_STRAY_MEDICAL_AID",
                "average_confidence": round(avg_confidence, 3),
                "block_confidences": confidences,
                "threshold_required": self.threshold,
                "reason": (
                    "🛡️ Anti-Hallucination Shield Activated: Acoustic aerodynamic airflow (<300 Hz) confirmed "
                    "normal respiratory panting. Reclassified as Summer Heatstroke/Thirst to prevent false rabies culling."
                ),
                "condition_diagnosed": "Heatstroke / Summer Dehydration (Anti-Hallucination Safe Pass)",
                "audio_correlation": "Acoustics: Aerodynamic airflow without vocal cord distress.",
                "dispatch_unit": "GOVERNMENT_MOBILE_VET_DISPENSARY",
                "hallucination_shield_activated": True,
                "required_equipment": [
                    "Electrolytes & Fluid Therapy",
                    "Cooling Ice-Gel Packs",
                    "Oral Rehydration Solution"
                ],
                "geofence_alert": {
                    "enabled": False,
                    "radius_meters": 0,
                    "message": None
                },
                "sla_minutes": 720
            }

        # -------------------------------------------------------------
        # TIER 1: VERIFIED RABIES QUARANTINE RED ALERT
        # -------------------------------------------------------------
        if all_passed and (persistent_foaming or persistent_ataxia) and not is_suspicious_media:
            boosted_confidence = avg_confidence
            audio_text = "Audio: Silent stream or ambient."
            if laryngeal_howl:
                boosted_confidence = min(0.99, round(avg_confidence * 1.05, 3))
                audio_text = "Audio Confirmed: Laryngeal paresis ('rabies howl') confirms vocal cord paralysis."
                reason = "Multimodal Consensus Confirmed: Visual motor ataxia (3-block consensus) + Laryngeal vocal cord paresis ('rabies howl') detected."
            else:
                reason = "Triple-Check confirmed: Rabies symptoms sustained across 3 consecutive blocks with >85% confidence."

            return {
                "consensus_reached": True,
                "tier": "TIER_1_RABIES_QUARANTINE",
                "average_confidence": round(boosted_confidence, 3),
                "block_confidences": confidences,
                "threshold_required": self.threshold,
                "reason": reason,
                "audio_correlation": audio_text,
                "hallucination_shield_activated": False,
                "dispatch_unit": "MUNICIPAL_ANIMAL_CATCHERS_QUARANTINE_SQUAD",
                "required_equipment": [
                    "Bite-Resistant Kevlar Sleeves & Gloves",
                    "Humane Restraint Catch Pole",
                    "Isolation Quarantine Enclosure"
                ],
                "geofence_alert": {
                    "enabled": True,
                    "radius_meters": 500,
                    "message": "EMERGENCY ADVISORY: Suspected rabid animal detected within 500m. Keep pets indoors."
                },
                "sla_minutes": 45
            }

        # -------------------------------------------------------------
        # GUARD 2: UNCERTAINTY ZONE (50% - 84%) OR SUSPICIOUS MEDIA
        # Holds case for rapid human veterinarian review rather than triggering panic
        # -------------------------------------------------------------
        if (0.50 <= avg_confidence < 0.85) or (all_passed and is_suspicious_media):
            reason_text = (
                "⚠️ Uncertainty Tier Triggered: Confidence in ambiguous range (50%–84%). Case held for manual "
                "veterinary optical scrub before public ward advisory." if not is_suspicious_media
                else "⚠️ Integrity Warning: Media flagged as recycled or modified. Automated alert suspended for manual review."
            )

            return {
                "consensus_reached": False,
                "tier": "AMBIGUOUS_VET_REVIEW_REQUIRED",
                "average_confidence": round(avg_confidence, 3),
                "block_confidences": confidences,
                "threshold_required": self.threshold,
                "reason": reason_text,
                "condition_diagnosed": "Ambiguous Neurological Symptoms (Vet Verification Required)",
                "audio_correlation": "Acoustics: Moderate distress noted; insufficient for automated quarantine.",
                "hallucination_shield_activated": True,
                "dispatch_unit": "RAPID_VET_TELEPHOTO_PATROL",
                "required_equipment": [
                    "Telephoto Diagnostic Camera",
                    "Calming Pheromone Spray",
                    "Protective Gauntlets"
                ],
                "geofence_alert": {
                    "enabled": False,
                    "radius_meters": 0,
                    "message": None
                },
                "sla_minutes": 20 # 20-minute rapid review
            }

        # -------------------------------------------------------------
        # TIER 2: STRAY MEDICAL AID (TRAUMA, FRACTURES, WOUNDS)
        # -------------------------------------------------------------
        has_fracture = any(b.get("physical_fracture") for b in block_evaluations)
        has_wound = any(b.get("maggot_wound") for b in block_evaluations)
        pain_whine = audio.get("pain_whining", False)

        condition = "Heat Exhaustion / Dehydration (Normal Panting)"
        audio_text = "Acoustics: Aerodynamic panting without distress vocalization."
        
        if has_fracture and has_wound:
            condition = "Severe Trauma: Fracture & Open Wound"
            audio_text = "Acoustics: Pain vocalization detected accompanying multiple physical traumas." if pain_whine else "Acoustics: Severe localized physical trauma."
        elif has_fracture:
            condition = "Physical Trauma: Suspected Limb Fracture"
            audio_text = "Acoustics: Shrill pain yelping confirms acute orthopedic trauma." if pain_whine else "Acoustics: Orthopedic limp observed visually."
        elif has_wound:
            condition = "Cutaneous Infection / Maggot Wound"
            audio_text = "Acoustics: Whimpering distress associated with tissue irritation." if pain_whine else "Acoustics: Localized wound site."

        return {
            "consensus_reached": False,
            "tier": "TIER_2_STRAY_MEDICAL_AID",
            "average_confidence": round(avg_confidence, 3),
            "block_confidences": confidences,
            "threshold_required": self.threshold,
            "reason": f"Rabies ruled out (did not meet sustained 85% consensus). Classified as {condition}.",
            "condition_diagnosed": condition,
            "audio_correlation": audio_text,
            "hallucination_shield_activated": False,
            "dispatch_unit": "GOVERNMENT_MOBILE_VET_DISPENSARY",
            "required_equipment": [
                "Antiseptic Dressing Kit",
                "Pain Management Injectables",
                "Electrolytes & Fluid Therapy"
            ],
            "geofence_alert": {
                "enabled": False,
                "radius_meters": 0,
                "message": None
            },
            "sla_minutes": 720
        }
