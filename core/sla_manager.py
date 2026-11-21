from datetime import datetime, timedelta
from typing import Dict, Any, List

class SLAManager:
    """
    Tracks municipal response SLAs:
    - 45 Minutes for Rabies Red Alert
    - 12 Hours for Stray Medical Aid
    If countdown expires, escalates to District Magistrate with 1-click state hotline.
    """
    def __init__(self, rabies_sla_minutes: int = 45, medical_sla_hours: int = 12):
        self.rabies_sla_minutes = rabies_sla_minutes
        self.medical_sla_hours = medical_sla_hours

    def calculate_deadline(self, tier: str, start_time: datetime) -> datetime:
        if tier == "TIER_1_RABIES_QUARANTINE":
            return start_time + timedelta(minutes=self.rabies_sla_minutes)
        return start_time + timedelta(hours=self.medical_sla_hours)

    def check_sla_status(self, dossier: Dict[str, Any], current_time: datetime = None) -> Dict[str, Any]:
        if current_time is None:
            current_time = datetime.utcnow()

        deadline = dossier["sla_deadline"]
        if isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))

        remaining_seconds = (deadline - current_time).total_seconds()
        is_breached = remaining_seconds <= 0 and dossier.get("status") not in ["DISPATCHED", "RESOLVED"]

        # Format countdown MM:SS or HH:MM:SS
        if remaining_seconds > 0:
            hrs = int(remaining_seconds // 3600)
            mins = int((remaining_seconds % 3600) // 60)
            secs = int(remaining_seconds % 60)
            countdown_str = f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs > 0 else f"{mins:02d}:{secs:02d}"
        else:
            countdown_str = "00:00 (EXPIRED)"

        state_escalation = None
        if is_breached or dossier.get("is_escalated"):
            state_escalation = {
                "escalated": True,
                "escalation_authority": "Office of the District Magistrate & State Animal Welfare Board",
                "grievance_portal_reference": f"GOV-DM-ESC-{dossier['id'][:8].upper()}",
                "citizen_hotline_action": {
                    "unlocked": True,
                    "helpline_number": "1800-11-2026 (Toll-Free Emergency State Desk)",
                    "message": "Click to auto-dial State Grievance Desk with pre-filed case evidence dossier."
                }
            }

        return {
            "remaining_seconds": max(0, int(remaining_seconds)),
            "countdown_display": countdown_str,
            "is_breached": is_breached,
            "state_escalation": state_escalation
        }
