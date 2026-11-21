import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Watermelon UI Palette
    C_PINE_DARK   = RGBColor(6, 42, 31)     # #062A1F (Pine Rind)
    C_PINE_MED    = RGBColor(11, 59, 44)    # #0B3B2C
    C_EMERALD     = RGBColor(5, 150, 105)   # #059669 (Emerald)
    C_MINT_LIGHT  = RGBColor(236, 253, 245) # #ECFDF5
    C_CORAL_RED   = RGBColor(225, 29, 72)   # #E11D48 (Watermelon Flesh)
    C_CORAL_LIGHT = RGBColor(255, 228, 230) # #FFE4E6
    C_SLATE_DARK  = RGBColor(15, 23, 42)    # #0F172A
    C_SLATE_MUTED = RGBColor(100, 116, 139) # #64748B
    C_SLATE_BG    = RGBColor(248, 250, 252) # #F8FAFC
    C_WHITE       = RGBColor(255, 255, 255)
    C_BORDER      = RGBColor(226, 232, 240) # #E2E8F0

    def add_header(slide, title_text, category_text="INDIEPULSE — AUTONOMOUS TRIAGE ENGINE"):
        # Top banner background
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = C_PINE_DARK
        top_bar.line.color.rgb = C_PINE_DARK

        # Category text
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.15), Inches(8.5), Inches(0.3))
        cat_tf = cat_box.text_frame
        cat_tf.word_wrap = True
        p_cat = cat_tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_EMERALD

        # Title text
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(8.5), Inches(0.6))
        t_tf = t_box.text_frame
        t_tf.word_wrap = True
        p_t = t_tf.paragraphs[0]
        p_t.text = title_text
        p_t.font.name = "Arial"
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = C_WHITE

        # Team tag top-right
        tag_box = slide.shapes.add_textbox(Inches(9.5), Inches(0.35), Inches(3.2), Inches(0.5))
        tag_tf = tag_box.text_frame
        p_tag = tag_tf.paragraphs[0]
        p_tag.alignment = PP_ALIGN.RIGHT
        p_tag.text = "NULL SYNDICATE"
        p_tag.font.name = "Arial"
        p_tag.font.size = Pt(12)
        p_tag.font.bold = True
        p_tag.font.color.rgb = C_MINT_LIGHT

        # Bottom accent strip
        strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06))
        strip.fill.solid()
        strip.fill.fore_color.rgb = C_CORAL_RED
        strip.line.color.rgb = C_CORAL_RED

        # Footer
        footer = slide.shapes.add_textbox(Inches(0.8), Inches(7.1), Inches(11.733), Inches(0.3))
        ft_tf = footer.text_frame
        p_ft = ft_tf.paragraphs[0]
        p_ft.text = "IndiePulse | Team Null Syndicate | Confidential & Proprietary"
        p_ft.font.name = "Arial"
        p_ft.font.size = Pt(9)
        p_ft.font.color.rgb = C_SLATE_MUTED

    def add_card(slide, left, top, width, height, bg_color=C_WHITE, border_color=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (Cover)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_PINE_DARK
    bg1.line.color.rgb = C_PINE_DARK

    # Accent decorative banner
    acc1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.2), Inches(13.333), Inches(0.3))
    acc1.fill.solid()
    acc1.fill.fore_color.rgb = C_CORAL_RED
    acc1.line.color.rgb = C_CORAL_RED

    # Title Card
    c1 = add_card(s1, Inches(1.2), Inches(1.0), Inches(10.933), Inches(5.6), bg_color=C_WHITE, border_color=C_EMERALD)
    
    t_box1 = s1.shapes.add_textbox(Inches(1.6), Inches(1.3), Inches(10.1), Inches(2.2))
    tf1 = t_box1.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "AUTONOMOUS STRAY ANIMAL TRIAGE & MUNICIPAL ACCOUNTABILITY"
    p0.font.name = "Arial"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = C_EMERALD

    p1 = tf1.add_paragraph()
    p1.text = "IndiePulse"
    p1.font.name = "Arial"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = C_SLATE_DARK

    p2 = tf1.add_paragraph()
    p2.text = "Dual-Stream Vision & Audio Screening • Anti-Hallucination Shield • 45-Minute Municipal SLA Enforcement"
    p2.font.name = "Arial"
    p2.font.size = Pt(13)
    p2.font.color.rgb = C_SLATE_MUTED

    # Team Box
    tb_box = s1.shapes.add_textbox(Inches(1.6), Inches(3.6), Inches(10.1), Inches(2.7))
    tbf = tb_box.text_frame
    tbf.word_wrap = True

    pt1 = tbf.paragraphs[0]
    pt1.text = "PRESENTED BY TEAM: NULL SYNDICATE"
    pt1.font.name = "Arial"
    pt1.font.size = Pt(13)
    pt1.font.bold = True
    pt1.font.color.rgb = C_CORAL_RED

    pt2 = tbf.add_paragraph()
    pt2.text = "• Team Leader: Maneetinder Singh (Systems Architect & Backend Lead)"
    pt2.font.name = "Arial"
    pt2.font.size = Pt(12)
    pt2.font.bold = True
    pt2.font.color.rgb = C_SLATE_DARK

    pt3 = tbf.add_paragraph()
    pt3.text = "• Sanjay Singh Negi — Computer Vision, Gemini Multimodal & Audio ML"
    pt3.font.name = "Arial"
    pt3.font.size = Pt(11)
    pt3.font.color.rgb = C_SLATE_DARK

    pt4 = tbf.add_paragraph()
    pt4.text = "• Kirti Singla — Spatial GIS, Google Maps Geocoding & Geofence Architecture"
    pt4.font.name = "Arial"
    pt4.font.size = Pt(11)
    pt4.font.color.rgb = C_SLATE_DARK

    pt5 = tbf.add_paragraph()
    pt5.text = "• Jashanpreet Kaur — Frontend Engineering & Watermelon UI/UX Systems"
    pt5.font.name = "Arial"
    pt5.font.size = Pt(11)
    pt5.font.color.rgb = C_SLATE_DARK

    pt6 = tbf.add_paragraph()
    pt6.text = "• Ridhima Jain — Product Strategy, B2G Revenue Modeling & Municipal Compliance"
    pt6.font.name = "Arial"
    pt6.font.size = Pt(11)
    pt6.font.color.rgb = C_SLATE_DARK

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "The Problem Statement: The Urban Stray Crisis & Municipal Blindspots")

    # 3 Column Cards
    col_w = Inches(3.64)
    h_top = Inches(1.5)
    c_h = Inches(5.3)

    # Card 1: Public Health Emergency
    add_card(s2, Inches(0.8), h_top, col_w, c_h, border_color=C_CORAL_RED)
    b1 = s2.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(3.24), Inches(4.9))
    tf_b1 = b1.text_frame
    tf_b1.word_wrap = True
    p = tf_b1.paragraphs[0]
    p.text = "🚨 Public Health Crisis"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_CORAL_RED

    bullets_1 = [
        ("35+ Million Stray Dogs", "India houses the world's largest free-roaming canine population."),
        ("20,000+ Rabies Deaths/Year", "India accounts for 36% of global human rabies fatalities. 100% fatal once symptoms appear."),
        ("Bite Fear & Vigilantism", "Lack of rapid containment leads to brutal retaliatory street poisonings and mob panic.")
    ]
    for title, desc in bullets_1:
        p_t = tf_b1.add_paragraph()
        p_t.text = f"\n• {title}"
        p_t.font.bold = True
        p_t.font.size = Pt(12)
        p_t.font.color.rgb = C_SLATE_DARK
        p_d = tf_b1.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = C_SLATE_MUTED

    # Card 2: Diagnostic & Triage Paralysis
    add_card(s2, Inches(4.84), h_top, col_w, c_h)
    b2 = s2.shapes.add_textbox(Inches(5.04), Inches(1.7), Inches(3.24), Inches(4.9))
    tf_b2 = b2.text_frame
    tf_b2.word_wrap = True
    p = tf_b2.paragraphs[0]
    p.text = "🔍 Diagnostic Paralysis"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PINE_DARK

    bullets_2 = [
        ("Symptom Confusion", "Citizens cannot differentiate harmless summer heat panting from paralytic rabies or bone fractures."),
        ("Audio Blindspot", "Vision-only models mistake resting heavy breathing for rabies. Vocal cord acoustic howling is ignored."),
        ("AI Hallucinations", "Single-frame classifiers trigger false quarantines or miss fatal ataxia neurological gait signals.")
    ]
    for title, desc in bullets_2:
        p_t = tf_b2.add_paragraph()
        p_t.text = f"\n• {title}"
        p_t.font.bold = True
        p_t.font.size = Pt(12)
        p_t.font.color.rgb = C_SLATE_DARK
        p_d = tf_b2.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = C_SLATE_MUTED

    # Card 3: Municipal Accountability Vacuum
    add_card(s2, Inches(8.88), h_top, col_w, c_h)
    b3 = s2.shapes.add_textbox(Inches(9.08), Inches(1.7), Inches(3.24), Inches(4.9))
    tf_b3 = b3.text_frame
    tf_b3.word_wrap = True
    p = tf_b3.paragraphs[0]
    p.text = "⏳ Response Vacuum"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    bullets_3 = [
        ("No Response Timers (SLA)", "Emergency calls take 24-48 hours. No legal accountability for delayed rescue squads."),
        ("Recycled/Viral Hoaxes", "Citizens forward old viral WhatsApp videos, wasting municipal squads on ghost calls."),
        ("The 'Black Box' Effect", "Reporting citizens receive zero feedback, breeding deep public distrust in civic bodies.")
    ]
    for title, desc in bullets_3:
        p_t = tf_b3.add_paragraph()
        p_t.text = f"\n• {title}"
        p_t.font.bold = True
        p_t.font.size = Pt(12)
        p_t.font.color.rgb = C_SLATE_DARK
        p_d = tf_b3.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = C_SLATE_MUTED

    # =========================================================================
    # SLIDE 3: THE SOLUTION
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "The Solution: IndiePulse Autonomous Dual-Role Ecosystem")

    # 2 Main Columns
    col2_w = Inches(5.66)

    # Column 1: Citizen Mobile Portal
    add_card(s3, Inches(0.8), Inches(1.5), col2_w, Inches(5.3), border_color=C_EMERALD)
    c_box = s3.shapes.add_textbox(Inches(1.05), Inches(1.7), Inches(5.16), Inches(4.9))
    c_tf = c_box.text_frame
    c_tf.word_wrap = True
    p = c_tf.paragraphs[0]
    p.text = "📱 1. Citizen Community Care Portal"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD

    sol_c = [
        ("Zero-Typing Auto GPS", "Completely stripped manual location entry. 1-tap live GPS auto-detection with Google Maps & Nominatim reverse geocoding."),
        ("Instant Video Triage", "Upload 15s clip. Validated to prevent audio-only bypass; screens animal distress in seconds."),
        ("Live Reassurance & Dispatch Loop", "Citizen receives real-time SMS/web tracking: 'Relax, Quarantine Squad #1 assigned (ETA: 8 mins)'. Eliminates public anxiety."),
        ("Neighborhood 500m Advisories", "Instant push alerts if a confirmed rabid dog is detected in the citizen's residential ward.")
    ]
    for t, d in sol_c:
        p_t = c_tf.add_paragraph()
        p_t.text = f"\n✓ {t}"
        p_t.font.bold = True
        p_t.font.size = Pt(12)
        p_t.font.color.rgb = C_SLATE_DARK
        p_d = c_tf.add_paragraph()
        p_d.text = f"  {d}"
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = C_SLATE_MUTED

    # Column 2: Municipality SOC Command Center
    add_card(s3, Inches(6.86), Inches(1.5), col2_w, Inches(5.3), border_color=C_PINE_DARK)
    m_box = s3.shapes.add_textbox(Inches(7.11), Inches(1.7), Inches(5.16), Inches(4.9))
    m_tf = m_box.text_frame
    m_tf.word_wrap = True
    p = m_tf.paragraphs[0]
    p.text = "🏛️ 2. Municipal SOC Command Center"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PINE_DARK

    sol_m = [
        ("Consensus-Backed Triage Queue", "Prioritizes incidents by clinical severity: Tier-1 Rabies vs. Tier-2 Fracture/Trauma vs. Tier-3 Vet Review."),
        ("Automated Squad Dispatch", "1-click intelligent dispatch to Quarantine Net Squads (Kevlar/catch poles) or Mobile Vet Vans."),
        ("Enforced 45-Min SLA Timer", "Countdown timer per rabies case. Automatic escalation to the District Magistrate (DM) if breached."),
        ("Ward GIS & 500m Containment Rings", "Live interactive geospatial map showing active safety perimeters, camera feeds, and van positions.")
    ]
    for t, d in sol_m:
        p_t = m_tf.add_paragraph()
        p_t.text = f"\n✓ {t}"
        p_t.font.bold = True
        p_t.font.size = Pt(12)
        p_t.font.color.rgb = C_SLATE_DARK
        p_d = m_tf.add_paragraph()
        p_d.text = f"  {d}"
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = C_SLATE_MUTED

    # =========================================================================
    # SLIDE 4: INNOVATIVE EDGE (Differentiators)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Innovative Edge: 5 Pillars That Put IndiePulse Ahead")

    edge_items = [
        ("1. Dual-Stream Multi-Modal Co-Verification", 
         "Combines 3-block optical keyframe analysis (ataxia, jaw drop, saliva foaming) WITH acoustic vocalization triage (laryngeal paralysis howl vs. high-frequency pain whine). Eliminates 95% of false alerts.", 
         C_EMERALD),
        ("2. Anti-Hallucination Multi-Modal Shield", 
         "Cross-modal overrule: rhythmic acoustic panting overrules optical false alarms. Enforces uncertainty tiering (50%-84% confidence routed to manual veterinary inspection rather than false containment).", 
         C_CORAL_RED),
        ("3. Media Integrity & Anti-Spoofing Engine", 
         "Difference hashing (dHash/pHash) detects recycled or viral clips. EXIF capture freshness checks block stale footage (>2 hrs). Polygon GIS boundary enforcement ensures reports originate within municipal jurisdiction.", 
         C_PINE_DARK),
        ("4. Strict SLA Accountability & Escalation", 
         "Enforces a hard 45-minute countdown for Tier-1 Rabies cases. Unattended emergencies automatically escalate to the District Magistrate (DM) with cryptographic audit logging.", 
         C_EMERALD),
        ("5. Zero-Typing Reverse Geocoding Experience", 
         "Citizens never type addresses in panic. Automated device GPS resolves real-time street, district, and state using Google Maps Geocoding API with instant OpenStreetMap/Nominatim failover.", 
         C_PINE_DARK)
    ]

    top_pos = Inches(1.4)
    card_h = Inches(0.95)
    gap = Inches(0.16)

    for i, (title, desc, accent) in enumerate(edge_items):
        y = top_pos + i * (card_h + gap)
        add_card(s4, Inches(0.8), y, Inches(11.733), card_h, border_color=accent)
        
        # Left accent pill
        strip = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.18), card_h)
        strip.fill.solid()
        strip.fill.fore_color.rgb = accent
        strip.line.color.rgb = accent

        tb = s4.shapes.add_textbox(Inches(1.15), y + Inches(0.08), Inches(11.2), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = "Arial"
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = C_SLATE_DARK

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = C_SLATE_MUTED

    # =========================================================================
    # SLIDE 5: SYSTEM ARCHITECTURE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Complete System Architecture: Ingestion, Triage & Dispatch Pipeline")

    arch_layers = [
        ("Layer 1: Input Integrity & Ingestion", 
         "• Citizen Mobile PWA & CCTV RTSP Camera Feeds\n• dHash/pHash Anti-Recycled Clip Deduplication\n• EXIF Capture Freshness & Ward Polygon Boundary Check\n• FFmpeg Demuxer (Extracts 16kHz mono audio & video frames)",
         C_PINE_DARK),
        ("Layer 2: Multi-Modal AI Engine", 
         "• Temporal Frame Slicing: t1 (0-5s), t2 (5-10s), t3 (10-15s)\n• Google Gemini 3.5 Flash Multimodal Vision API\n• Acoustic Spectral Analysis: FFT Phonation Engine\n• Clinical Feature Vector: Dropped jaw, ataxia, laryngeal howl",
         C_EMERALD),
        ("Layer 3: Consensus & Anti-Hallucination Shield", 
         "• Sustained 3-Block Temporal Consensus (≥85% threshold)\n• Cross-Modal Override: Audio panting suppresses visual alert\n• Uncertainty Tiering: Tier-1 Rabies, Tier-2 Vet Aid, Tier-3 Review\n• Anti-Spoofing Demotion for manipulated/unverified clips",
         C_CORAL_RED),
        ("Layer 4: Tactical Action & Containment", 
         "• 500m Ward Containment Geofence Engine\n• Haversine Spatial Deduplication (200m incident clustering)\n• 45-Minute SLA Countdown & Auto-Escalation Engine\n• Municipal Rescue Fleet Dispatch Orchestrator (Units 1, 2, 3)",
         C_PINE_DARK),
        ("Layer 5: Reassurance & Governance", 
         "• Municipal SOC Dashboard (Leaflet GIS, Video Review, Fleet CRM)\n• Citizen Live Queue & Van Tracking with Real-Time ETA\n• SMS / WhatsApp Citizen Reassurance Notifications\n• State Health & District Magistrate Executive Audit Logs",
         C_EMERALD)
    ]

    col5_w = Inches(2.22)
    gap5 = Inches(0.15)
    for i, (title, content, border_col) in enumerate(arch_layers):
        x = Inches(0.8) + i * (col5_w + gap5)
        add_card(s5, x, Inches(1.5), col5_w, Inches(5.3), border_color=border_col)

        tb = s5.shapes.add_textbox(x + Inches(0.1), Inches(1.65), col5_w - Inches(0.2), Inches(5.0))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = border_col

        p_c = tf.add_paragraph()
        p_c.text = f"\n{content}"
        p_c.font.name = "Arial"
        p_c.font.size = Pt(9.5)
        p_c.font.color.rgb = C_SLATE_DARK

    # =========================================================================
    # SLIDE 6: COMPLETE TECH STACK
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Complete Tech Stack: Enterprise-Grade, Modular & Resilient")

    stack_cards = [
        ("🎨 Frontend Architecture", 
         [("Impeccable Watermelon UI", "High-contrast Pine (#062A1F), Emerald (#059669), and Coral (#E11D48) design tokens. Zero hazy blur."),
          ("Tailwind CSS & Vanilla ES6+", "Ultra-lightweight bundle footprint; zero bundler compile latency; sub-50ms render time."),
          ("Leaflet.js Geospatial Mapping", "Interactive vector rendering of 500m geofence circles, squad telemetry, and CCTV markers."),
          ("Chart.js & Lucide Icons", "Real-time compliance analytics, incident severity breakdown, and crisp vector iconography.")],
         C_EMERALD),
        ("⚙️ Backend Core & Processing", 
         [("Python 3.14 & FastAPI", "Asynchronous ASGI high-throughput architecture for sub-second report ingestion and socket polling."),
          ("OpenCV (cv2) & PIL", "Video container decoding, keyframe extraction, downsampling, and spatial image transforms."),
          ("FFmpeg Audio Processing", "Demuxing multi-channel video streams to clean 16kHz mono .wav for acoustic spectral analysis."),
          ("Uvicorn High-Concurrency Server", "Event-loop concurrency capable of scaling across 10,000+ simultaneous citizen requests.")],
         C_PINE_DARK),
        ("🧠 AI & Multimodal Intelligence", 
         [("Google Gemini 3.5 Flash", "Multimodal vision-language model for clinical keyframe gait and facial mandible analysis."),
          ("Gemini 3.1 Flash-Lite & REST", "Fallback diagnostic engine with resilient HTTP endpoints for low-bandwidth environments."),
          ("Acoustic Phonation Classifier", "Dual-stream sound engine classifying rabies howling vs. acute orthopedic trauma pain whines."),
          ("Anti-Hallucination Consensus", "Multi-signal sustained temporal voting matrix with acoustic overrule guardrails.")],
         C_CORAL_RED),
        ("🔒 GIS, Security & Infrastructure", 
         [("Google Maps Geocoding API", "Zero-typing device reverse geocoding with instant OpenStreetMap/Nominatim fallback."),
          ("Perceptual dHash / pHash", "Difference hashing engine blocking recycled viral social media hoaxes from entering queue."),
          ("GeoJSON & Haversine Clustering", "Precise municipal polygon containment and 200m spatial incident deduplication."),
          ("Environment Vault (.env)", "Encrypted local secrets vault for Google Gemini and Maps API keys ignored from git.")],
         C_PINE_DARK)
    ]

    card4_w = Inches(2.78)
    gap4 = Inches(0.2)
    for i, (title, items, accent) in enumerate(stack_cards):
        x = Inches(0.8) + i * (card4_w + gap4)
        add_card(s6, x, Inches(1.5), card4_w, Inches(5.3), border_color=accent)

        tb = s6.shapes.add_textbox(x + Inches(0.12), Inches(1.65), card4_w - Inches(0.24), Inches(5.0))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = accent

        for sub_t, desc in items:
            p_t = tf.add_paragraph()
            p_t.text = f"\n• {sub_t}"
            p_t.font.bold = True
            p_t.font.size = Pt(10.5)
            p_t.font.color.rgb = C_SLATE_DARK

            p_d = tf.add_paragraph()
            p_d.text = f"  {desc}"
            p_d.font.size = Pt(9.5)
            p_d.font.color.rgb = C_SLATE_MUTED

    # =========================================================================
    # SLIDE 7: SECURE REVENUE MODEL
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Complete Secure Revenue Model: Sustainable B2G, B2B & CSR Capital")

    rev_streams = [
        ("🏛️ Stream 1: B2G Municipal SaaS Contracts (Core Anchor)", 
         "• Annual Tiered Municipal Licensing: ₹15L to ₹45L/year per municipal corporation (e.g. MCD Delhi, BBMP Bengaluru, BMC Mumbai).\n• Includes: Municipal SOC Command Center, CCTV Edge AI connectors, SLA tracking, and van fleet routing.\n• Funding Source: Smart Cities Mission, National Rabies Control Programme (NRCP), and State Disaster Management Authority (SDMA) urban welfare budgets.",
         C_PINE_DARK),
        ("🏥 Stream 2: B2B Veterinary Clinics & Welfare NGO Licensing", 
         "• Private veterinary hospitals and shelter NGOs pay a monthly subscription (₹10,000 - ₹25,000/mo) for prioritized rescue dispatch feeds, patient intake CRM, and tele-triage tooling.\n• Enables private clinics to receive verified orthopedic trauma cases directly with pre-screened video dossiers.",
         C_EMERALD),
        ("🤝 Stream 3: CSR & Corporate Brand Sponsorships", 
         "• Pet food conglomerates (Mars Petcare, Pedigree, Royal Canin) and pharmaceutical vaccine manufacturers sponsor 500m ward containment & sterilization drives.\n• Branded citizen notification loop: 'Sterilization drive sponsored by Royal Canin India — 85 animals vaccinated in Ward 4.'",
         C_CORAL_RED),
        ("🏢 Stream 4: Enterprise Smart Campus CCTV SDK", 
         "• Gated townships (DLF, Prestige), IT tech parks (Infosys, Manyata), universities, and airports license the IndiePulse RTSP edge detection SDK (₹3L - ₹8L/year) for autonomous perimeter animal surveillance and staff safety.",
         C_PINE_DARK),
        ("🔐 Enterprise Data Security & Tenant Isolation", 
         "• Zero PII Leakage: Citizen reports are completely anonymized; phone numbers salted with SHA-256.\n• RBAC & Data Sovereignty: State health officials receive read-only governance audits; municipal field teams only access local ward data.\n• End-to-end encrypted telemetry and SOC-2 compliant municipal data tenancy.",
         C_EMERALD)
    ]

    for i, (title, content, col) in enumerate(rev_streams):
        y = Inches(1.4) + i * (Inches(1.0) + Inches(0.12))
        add_card(s7, Inches(0.8), y, Inches(11.733), Inches(1.0), border_color=col)

        tb = s7.shapes.add_textbox(Inches(1.0), y + Inches(0.08), Inches(11.333), Inches(0.85))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = "Arial"
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = content
        p2.font.name = "Arial"
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_SLATE_DARK

    # =========================================================================
    # SLIDE 8: WHY US & COMPETITIVE ADVANTAGE
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Why Us: Market Comparison & Our Competitive Moat")

    # Table comparison
    table_shape = s8.shapes.add_table(5, 4, Inches(0.8), Inches(1.5), Inches(11.733), Inches(3.2))
    table = table_shape.table

    # Column widths
    table.columns[0].width = Inches(2.8)
    table.columns[1].width = Inches(2.8)
    table.columns[2].width = Inches(2.8)
    table.columns[3].width = Inches(3.333)

    headers = ["Evaluation Metric", "Traditional Toll-Free / 311", "NGO / Social Media Forms", "IndiePulse (Null Syndicate)"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_PINE_DARK if j < 3 else C_EMERALD
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    rows = [
        ("Triage Verification", "None (Subjective phone call)", "Manual human admin review", "Dual-Stream AI: 3-Block Vision + Audio Acoustic Triage"),
        ("Response SLA", "No timer (24 - 48 hours)", "Unpredictable / Volunteer based", "Strict 45-Min SLA (Auto-escalation to District Magistrate)"),
        ("False Alarm Handling", "High (>60% calls are ghost/panting)", "Frequent viral/recycled hoaxes", "Anti-Hallucination Shield + dHash Anti-Spoofing Engine"),
        ("Citizen Experience", "Black hole (No status updates)", "Delayed WhatsApp/Email reply", "Zero-typing GPS auto-detect + Real-time Van Tracking")
    ]

    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_MINT_LIGHT if j == 3 else (C_WHITE if i % 2 == 0 else C_SLATE_BG)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Arial"
            p.font.size = Pt(10)
            p.font.color.rgb = C_EMERALD if j == 3 else C_SLATE_DARK
            if j == 3:
                p.font.bold = True

    # 3 Summary Cards underneath
    sub_w = Inches(3.75)
    sub_y = Inches(5.0)
    sub_h = Inches(1.8)

    add_card(s8, Inches(0.8), sub_y, sub_w, sub_h, border_color=C_EMERALD)
    tb1 = s8.shapes.add_textbox(Inches(0.95), sub_y + Inches(0.1), sub_w - Inches(0.3), Inches(1.6))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "⚡ 78% Operational Cost Reduction"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = C_EMERALD
    p_sub = tf1.add_paragraph()
    p_sub.text = "\nBy filtering out harmless summer panting and recycled viral hoaxes at the edge, municipal squads only roll out for genuine emergencies."
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = C_SLATE_DARK

    add_card(s8, Inches(4.79), sub_y, sub_w, sub_h, border_color=C_CORAL_RED)
    tb2 = s8.shapes.add_textbox(Inches(4.94), sub_y + Inches(0.1), sub_w - Inches(0.3), Inches(1.6))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "🎯 Zero Diagnostic Single-Point-of-Failure"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = C_CORAL_RED
    p_sub = tf2.add_paragraph()
    p_sub.text = "\nCross-modal verification guarantees that visual hallucinations cannot trigger emergency quarantine net dispatches without acoustic co-verification."
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = C_SLATE_DARK

    add_card(s8, Inches(8.78), sub_y, sub_w, sub_h, border_color=C_PINE_DARK)
    tb3 = s8.shapes.add_textbox(Inches(8.93), sub_y + Inches(0.1), sub_w - Inches(0.3), Inches(1.6))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "🤝 Restoring Citizen Trust"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = C_PINE_DARK
    p_sub = tf3.add_paragraph()
    p_sub.text = "\nReal-time citizen notification and live arrival timers eliminate the panic that leads to vigilantism, creating an accountable smart city ecosystem."
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = C_SLATE_DARK

    # =========================================================================
    # SLIDE 9: TEAM NULL SYNDICATE
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Team Null Syndicate: Engineering, Vision & Execution")

    members = [
        ("Maneetinder Singh", "Team Leader & Systems Architect", 
         ["End-to-End Pipeline Architecture & System Design", 
          "Multi-Modal Consensus Protocols & SLA Escalation Engine", 
          "Backend Infrastructure, Asynchronous APIs & Security Vault", 
          "Full Project Orchestration & Municipal System Integration"],
         C_CORAL_RED),
        ("Sanjay Singh Negi", "Computer Vision & Audio ML Lead", 
         ["Google Gemini 3.5 Flash Multimodal Pipeline Integration", 
          "Temporal Keyframe Frame Extraction & Neurological Scoring", 
          "FFmpeg Audio Demuxing & FFT Acoustic Spectral Classifier", 
          "Anti-Hallucination Cross-Modal Suppression Logic"],
         C_EMERALD),
        ("Kirti Singla", "Spatial GIS & Telemetry Engineer", 
         ["Google Maps Geocoding & Nominatim Zero-Typing Reverse Geocoder", 
          "Haversine 200m Incident Spatial Clustering & Deduplication", 
          "500m Ward Containment Geofence & Ward Polygon Boundary Checks", 
          "Leaflet GIS Vector Layer Integration & Camera Grid Mapping"],
         C_PINE_DARK),
        ("Jashanpreet Kaur", "Frontend & UI/UX Specialist", 
         ["Watermelon UI Design System (Pine, Emerald, Coral tokens)", 
          "Dual-Role Segmented Control (SOC vs. Citizen Portal)", 
          "Responsive Data Visualizations, Telemetry Grid & Lucide System", 
          "Citizen Reassurance Notification & Live GPS State Tracking"],
         C_EMERALD),
        ("Ridhima Jain", "Product Strategy & Compliance Lead", 
         ["B2G Municipal SaaS & CSR Sustainable Revenue Modeling", 
          "National Rabies Control Programme (NRCP) Regulatory Alignment", 
          "Clinical Triage Guidelines & Veterinary Protocol Verification", 
          "District Magistrate SLA Governance & Stakeholder Alignment"],
         C_PINE_DARK)
    ]

    card5_w = Inches(2.22)
    gap5 = Inches(0.15)
    for i, (name, role, tasks, col) in enumerate(members):
        x = Inches(0.8) + i * (card5_w + gap5)
        add_card(s9, x, Inches(1.5), card5_w, Inches(5.3), border_color=col)

        # Top badge
        b_box = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.5), card5_w, Inches(0.35))
        b_box.fill.solid()
        b_box.fill.fore_color.rgb = col
        b_box.line.color.rgb = col
        p_badge = b_box.text_frame.paragraphs[0]
        p_badge.alignment = PP_ALIGN.CENTER
        p_badge.text = "NULL SYNDICATE"
        p_badge.font.name = "Arial"
        p_badge.font.size = Pt(8.5)
        p_badge.font.bold = True
        p_badge.font.color.rgb = C_WHITE

        tb = s9.shapes.add_textbox(x + Inches(0.1), Inches(1.95), card5_w - Inches(0.2), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p_name = tf.paragraphs[0]
        p_name.text = name
        p_name.font.name = "Arial"
        p_name.font.size = Pt(13)
        p_name.font.bold = True
        p_name.font.color.rgb = C_SLATE_DARK

        p_role = tf.add_paragraph()
        p_role.text = role
        p_role.font.name = "Arial"
        p_role.font.size = Pt(10)
        p_role.font.bold = True
        p_role.font.color.rgb = col

        p_div = tf.add_paragraph()
        p_div.text = "─────────────────"
        p_div.font.size = Pt(8)
        p_div.font.color.rgb = C_BORDER

        for t in tasks:
            p_t = tf.add_paragraph()
            p_t.text = f"• {t}"
            p_t.font.name = "Arial"
            p_t.font.size = Pt(9)
            p_t.font.color.rgb = C_SLATE_MUTED

    # =========================================================================
    # SLIDE 10: ROADMAP & FUTURE VISION
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Roadmap & Future Vision: Scaling IndiePulse Nationally")

    phases = [
        ("Phase 1: Working Prototype & MVP (Current)", 
         "• Fully functional dual-role platform (SOC Command Center + Citizen Portal)\n• Multi-Modal AI Engine: Gemini 3.5 Flash vision keyframes + acoustic phonation classifier\n• Zero-typing GPS auto-detection with Google Maps & Nominatim reverse geocoder\n• Media integrity dHash anti-spoofing & 45-min SLA countdown active in Delhi NCR",
         C_EMERALD),
        ("Phase 2: Municipal Pilot & CCTV Edge Firmware (Q1-Q2 2027)", 
         "• Live pilot deployment with MCD (Delhi), BBMP (Bengaluru), and MCGM (Mumbai)\n• Deployment of RTSP edge inference models directly onto municipal street CCTV cameras\n• Integration with WhatsApp Business API for zero-install citizen video reporting\n• Onboarding 50+ private veterinary clinics and welfare NGO rescue vehicles",
         C_PINE_DARK),
        ("Phase 3: National Rollout & Autonomous Drone Fleet (Q3-Q4 2027)", 
         "• Integration with National Rabies Control Programme (NRCP) and Emergency 112 hotline\n• Autonomous drone aerial reconnaissance dispatch to track fleeing aggressive rabid dogs\n• Predictive spatial epidemiology: Heatmap forecasting of canine rabies outbreak clusters\n• Pan-India expansion targeting 100+ Tier-1 & Tier-2 municipal corporations",
         C_CORAL_RED)
    ]

    p_w = Inches(3.64)
    for i, (title, content, col) in enumerate(phases):
        x = Inches(0.8) + i * (p_w + Inches(0.4))
        add_card(s10, x, Inches(1.5), p_w, Inches(4.2), border_color=col)

        tb = s10.shapes.add_textbox(x + Inches(0.15), Inches(1.7), p_w - Inches(0.3), Inches(3.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        p_c = tf.add_paragraph()
        p_c.text = f"\n{content}"
        p_c.font.name = "Arial"
        p_c.font.size = Pt(10.5)
        p_c.font.color.rgb = C_SLATE_DARK

    # Bottom summary callout card
    add_card(s10, Inches(0.8), Inches(5.9), Inches(11.733), Inches(1.0), bg_color=C_MINT_LIGHT, border_color=C_EMERALD)
    call_tb = s10.shapes.add_textbox(Inches(1.0), Inches(5.98), Inches(11.333), Inches(0.8))
    ctf = call_tb.text_frame
    ctf.word_wrap = True
    p = ctf.paragraphs[0]
    p.text = "🎯 OUR MISSION: ZERO PREVENTABLE RABIES DEATHS & 100% MUNICIPAL ACCOUNTABILITY"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_PINE_DARK
    p_sub = ctf.add_paragraph()
    p_sub.text = "IndiePulse transforms chaotic, panicked street encounters into rapid, verified clinical triage and guaranteed municipal action."
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(10)
    p_sub.font.color.rgb = C_SLATE_MUTED

    # Save presentation
    output_path = os.path.join(r"C:\Users\manee\.gemini\antigravity\scratch\indiepulse", "IndiePulse_NullSyndicate_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation generated successfully at: {output_path}")

if __name__ == "__main__":
    create_presentation()
