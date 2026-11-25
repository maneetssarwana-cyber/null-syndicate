# IndiePulse — Design System & Visual Craft Standards
*Watermelon UI Platform Specifications (`ui.watermelon.sh`) & Impeccable Standards (`pbakaus/impeccable`)*

## 1. Design Philosophy
- **Anti-Vibe-Coding:** Strictly eliminate hazy backdrop blurs, pastel translucent layers, ungrounded gradients, and unreadable micro-text.
- **High-Contrast Tactical Clarity:** The system must function in bright daylight on municipal field tablets and under night-shift SOC command center conditions.
- **Watermelon UI Palette:**
  - **Watermelon Rind (Pine & Emerald):** Solid structure, active operational states, and safe verifications.
    - Pine Deep: `#062A1F` (header, primary containers)
    - Pine Medium: `#0B3B2C`
    - Emerald Green: `#059669` (primary tactical actions, active units, verified safe)
    - Mint Tint: `#ECFDF5`, `#D1FAE5` (pill backgrounds, active row highlights)
  - **Watermelon Flesh (Coral & Crimson):** Critical alerts, Tier-1 Rabies quarantine, 500m geofence rings, and SLA breach countdowns.
    - Crimson Coral: `#E11D48`
    - Rose Deep: `#BE123C`
    - Coral Tint: `#FFF1F2`, `#FFE4E6`
  - **Slate & White Foundations:**
    - Dark Text / Foreground: `#0F172A`, `#1E293B`
    - Muted Labels / Telemetry: `#64748B`, `#475569`
    - Card Surfaces: Solid `#FFFFFF` with `#E2E8F0` / `#CBD5E1` crisp 1px borders
    - Canvas Background: `#F8FAFC`
- **Typography:**
  - UI Sans: `Inter`, system-ui, sans-serif (crisp tracking `-0.012em`)
  - Telemetry Monospace: `JetBrains Mono`, monospace (case IDs, coordinates, confidence scores, SLA countdown timers)

## 2. Component Guidelines (Watermelon UI Tokens)
1. **Containers (`.wm-card`, `.wm-card-elevated`):** Solid white surface, 12px-14px border radius, 1px solid `#E2E8F0` border, crisp tactile shadow (`--wm-shadow-xs` / `--wm-shadow-sm`).
2. **Buttons (`.wm-btn-primary`, `.wm-btn-coral`, `.wm-btn-secondary`):**
   - Minimum 36px height with 600 weight text.
   - Tactile active state with `scale(0.98)` feedback.
3. **Pills & Badges (`.wm-pill-critical`, `.wm-pill-normal`, `.wm-pill-warning`):**
   - Explicit rounded-full pills with border and text contrast ratio exceeding WCAG AAA (7:1).
4. **Segmented Controls (`.wm-segmented`, `.wm-segment-btn`):**
   - Deep Pine `#062A1F` track with crisp white elevated active pill.
5. **Telemetry Monospace Blocks:**
   - Dedicated metrics displays with label in uppercase 10px bold slate, value in 16px-28px bold monospace.

## 3. Live Streaming & Phone Camera UX
- **Phone Camera Node (`static/phone_cam.html`):**
  - Instant camera viewfinder with active bounding boxes.
  - Controls: Flashlight/Torch toggle, Switch Lens (Front/Back), Stream Quality selector (720p / 480p / 360p), Audio VU level meter.
  - Streaming status: Pulsing green live indicator, live FPS meter, stream latency counter, and connection ping.
- **Municipal SOC Stream Monitor:**
  - Multi-source switcher: CCTV Feeds vs. Connected Phone Nodes vs. IP RTSP stream.
  - QR Code Pairing Modal: Instant scan-to-stream connection flow.
  - Real-time model confidence threshold sliders (Rabies threshold, Ataxia sensitivity, Audio phonation threshold).
