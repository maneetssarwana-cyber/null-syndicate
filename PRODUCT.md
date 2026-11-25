# IndiePulse — Product Context & Specifications
*Adhering to Impeccable AI Design & Engineering Standards*

## Executive Summary
IndiePulse is an autonomous smart city stray animal clinical triage, public health warning, and municipal accountability engine. It bridges the gap between panicked citizens encountering distressed or aggressive street dogs and municipal animal welfare/quarantine teams.

## Core Problem
1. **Urban Stray Crisis:** Over 35 million free-roaming dogs in India; 20,000+ human rabies fatalities annually (36% of the global burden). Rabies has a 100% case-fatality rate once neurological symptoms manifest.
2. **Diagnostic Paralysis:** Citizens cannot distinguish harmless summer heat exhaustion/panting from furious or paralytic rabies, or acute orthopedic trauma/fractures.
3. **Response Vacuum & False Alarms:** Municipal helplines operate with 24–48 hour backlogs and zero SLA accountability. Ghost calls and recycled viral videos waste critical squad resources.
4. **CCTV Infrastructure Deficit:** Dedicated municipal CCTV street cameras with high-resolution animal coverage are not universally available across every ward, neighborhood, or alley.

## Solution Architecture
1. **Dual-Role Operations:**
   - **Citizen Community Portal:** Zero-typing reporting with auto-detected GPS reverse geocoding (Google Maps API + Nominatim fallback), 15-second mobile video triage, real-time arrival timers, and reassurance notifications (*"Relax, Mobile Vet Van #2 is arriving in ~6 mins"*).
   - **Municipal SOC Command Center:** Live Ward GIS map, 500m rabies containment rings, CCTV & Phone Camera surveillance grid, automated fleet assignment, and hard 45-minute SLA countdown with auto-escalation to the District Magistrate (DM).
2. **Phone Camera as a CCTV Alternative:**
   - Since dedicated CCTV is absent in many sectors, smartphones act as lightweight, high-mobility smart surveillance nodes.
   - Zero-install mobile web streaming (`static/phone_cam.html`) via `getUserMedia` + WebSocket frame streaming, providing high-resolution camera feeds with sub-200ms edge latency.
3. **Dual-Stream Multimodal Triage:**
   - **Visual Stream:** 3-block temporal verification ($t_1, t_2, t_3$) evaluating lower jaw drop (mandible paralysis), saliva foaming, and pelvic-limb ataxia.
   - **Acoustic Stream:** Real-time phonation analysis detecting laryngeal paralysis (hoarse low-frequency rabies howling, $<450\text{ Hz}$) vs. acute orthopedic pain whines ($>2.2\text{ kHz}$) vs. normal rhythmic summer panting.
4. **Anti-Hallucination & Anti-Spoofing Shield:**
   - Cross-modal override: acoustic aerodynamic panting overrules optical false alarms.
   - Uncertainty tiering: 50%–84% confidence cases are flagged for veterinary review (`TIER_3_VET_REVIEW`) rather than triggering false public panic.
   - Media integrity: 64-bit difference hashing (`dHash`) against recycled viral media + EXIF capture freshness checks + municipal ward polygon boundary enforcement.
5. **Transfer Learning / Fine-Tuning Pipeline:**
   - **CV Backbone:** Pretrained YOLOv8 / MobileNetV4 fine-tuned on stray canine gait, ataxia, and mandibular paralysis.
   - **Audio Backbone:** Pretrained YAMNet / PANNs AudioSet embeddings fine-tuned on canine vocalizations.
   - **Cloud Hybrid:** Google Gemini 3.5 Flash Multimodal API for high-level semantic reasoning and cross-modal clinical validation.
