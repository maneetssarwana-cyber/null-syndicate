"""
Generates 3 realistic MP4 demo video clips using Pillow + FFmpeg.
Outputs H.264 encoded MP4 files into static/videos/ and uploads/
"""
import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

STATIC_VIDEOS = Path(r"C:\Users\manee\.gemini\antigravity\scratch\indiepulse\static\videos")
UPLOADS_DIR = Path(r"C:\Users\manee\.gemini\antigravity\scratch\indiepulse\uploads")
STATIC_VIDEOS.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

def create_demo_video(filename: str, title: str, subtitle: str, color_scheme: str, alert_type: str):
    output_static = STATIC_VIDEOS / filename
    output_upload = UPLOADS_DIR / filename

    width, height = 640, 360
    fps = 20
    duration_sec = 8
    total_frames = fps * duration_sec

    # Start ffmpeg process to encode raw image stream into H.264 MP4
    cmd = [
        "ffmpeg", "-y",
        "-f", "image2pipe",
        "-vcodec", "png",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_static)
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for i in range(total_frames):
        # Create background
        img = Image.new("RGB", (width, height), (20, 24, 33))
        draw = ImageDraw.Draw(img)

        # Dynamic scanning line
        scan_y = int((i % 40) / 40.0 * height)
        draw.line([(0, scan_y), (width, scan_y)], fill=(60, 80, 110), width=1)

        # Surveillance Grid Lines
        draw.rectangle([20, 20, width - 20, height - 20], outline=(40, 50, 70), width=2)
        draw.line([(width // 2 - 10, height // 2), (width // 2 + 10, height // 2)], fill=(100, 120, 150), width=1)
        draw.line([(width // 2, height // 2 - 10), (width // 2, height // 2 + 10)], fill=(100, 120, 150), width=1)

        # Title bar
        timecode = f"2026-11-21 22:50:{i // fps:02d}.{int((i % fps) * (100 / fps)):02d}"
        draw.rectangle([30, 30, width - 30, 75], fill=(30, 36, 50))
        draw.text((40, 36), f"SURVEILLANCE GRID: {title}", fill=(220, 220, 240))
        draw.text((40, 54), f"TIMECODE: {timecode} | FPS: 20.0 H.264", fill=(140, 160, 190))

        # Simulated Bounding Box around canine target
        # Add slight wobble / ataxia motion for rabies
        wobble_x = int(10 * (1 if alert_type == "RABIES" else 0) * ((i % 10) - 5))
        box_x1 = 180 + wobble_x
        box_y1 = 100
        box_x2 = 460 + wobble_x
        box_y2 = 270

        box_color = (217, 154, 155) if alert_type == "RABIES" else (169, 189, 170) if alert_type == "SAFE" else (224, 159, 94)
        draw.rectangle([box_x1, box_y1, box_x2, box_y2], outline=box_color, width=2)

        # Target classification tag
        draw.rectangle([box_x1, box_y1 - 22, box_x1 + 170, box_y1], fill=box_color)
        tag_text = "CANINE [RABIES SUSPECT]" if alert_type == "RABIES" else "CANINE [PANTING SAFE]" if alert_type == "SAFE" else "CANINE [FRACTURE WOUND]"
        draw.text((box_x1 + 6, box_y1 - 18), tag_text, fill=(20, 20, 20))

        # Bottom Telemetry Panel
        draw.rectangle([30, height - 70, width - 30, height - 30], fill=(25, 30, 42))
        draw.text((40, height - 65), f"DIAGNOSTIC CUE: {subtitle}", fill=(240, 240, 250))
        t_block = f"BLOCK t_{min(3, (i // (fps * 2)) + 1)} (5s window)"
        draw.text((40, height - 48), f"TEMPORAL CONSENSUS: {t_block} | CONF: 94%" if alert_type == "RABIES" else f"STATUS: CLEAR | {t_block}", fill=(180, 190, 210))

        img.save(proc.stdin, "PNG")

    proc.stdin.close()
    proc.wait()
    print(f"[+] Created: {output_static}")

    # Copy to uploads directory for ingestion testing
    import shutil
    shutil.copyfile(output_static, output_upload)
    print(f"[+] Replicated to uploads: {output_upload}")

def main():
    print("Generating demo MP4 video files...")
    create_demo_video(
        "rabid_dog_sample.mp4",
        "WARD 4 NORTH RING ROAD [CAM-08]",
        "Continuous Salivary Foaming, Paralyzed Dropped Jaw, Hind-limb Ataxia",
        "rose",
        "RABIES"
    )
    create_demo_video(
        "summer_panting_sample.mp4",
        "SECTOR 9 COMMUNITY PARK [CAM-02]",
        "Clean Pink Tongue, Thin Clear Saliva, Coordinated Gait, Heat Rest",
        "sage",
        "SAFE"
    )
    create_demo_video(
        "fracture_wound_sample.mp4",
        "CIVIC MARKET ALLEYWAY [CAM-14]",
        "Unilateral Hind Leg Non-Weight Bearing, Trauma Limp, Clean Saliva",
        "amber",
        "INJURY"
    )
    print("All sample videos successfully generated and embedded!")

if __name__ == "__main__":
    main()
