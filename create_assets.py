from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def draw_heart(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, fill: str):
    points = []
    for i in range(240):
        t = math.pi * 2 * i / 240
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        points.append((cx + x * scale, cy + y * scale))
    draw.polygon(points, fill=fill)


def create_logo(path: Path, compact: bool = False):
    width, height = (640, 180) if not compact else (320, 320)
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, width - 8, height - 8), radius=28, fill=(255, 255, 255, 245), outline=(220, 38, 38, 255), width=4)

    heart_cx, heart_cy = (92, 88) if not compact else (160, 122)
    draw_heart(draw, heart_cx, heart_cy, 4.3 if not compact else 5.8, "#dc2626")

    pulse = [
        (34, heart_cy),
        (62, heart_cy),
        (74, heart_cy - 18),
        (86, heart_cy + 18),
        (100, heart_cy - 8),
        (116, heart_cy),
        (150, heart_cy),
    ]
    if compact:
        pulse = [(x + 68, y + 42) for x, y in pulse]
    draw.line(pulse, fill="white", width=5, joint="curve")

    cross_x, cross_y = (150, 42) if not compact else (226, 66)
    draw.rounded_rectangle((cross_x - 9, cross_y - 25, cross_x + 9, cross_y + 25), radius=4, fill="#0f766e")
    draw.rounded_rectangle((cross_x - 25, cross_y - 9, cross_x + 25, cross_y + 9), radius=4, fill="#0f766e")

    if not compact:
        draw.text((190, 42), "CVD Predictor", font=font(42, True), fill="#991b1b")
        draw.text((194, 96), "Heart Disease Prediction System", font=font(22), fill="#0f766e")
    else:
        draw.text((42, 230), "CVD", font=font(42, True), fill="#991b1b")
        draw.text((128, 230), "Predictor", font=font(36, True), fill="#0f766e")

    image.save(path)


def create_background(path: Path):
    width, height = 1600, 1000
    image = Image.new("RGB", (width, height), "#07111f")
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
        ratio = y / height
        color = (
            int(7 + 20 * ratio),
            int(17 + 70 * ratio),
            int(31 + 65 * ratio),
        )
        draw.line((0, y, width, y), fill=color)

    for x in range(0, width, 80):
        draw.line((x, 0, x, height), fill=(255, 255, 255, 13))
    for y in range(0, height, 80):
        draw.line((0, y, width, y), fill=(255, 255, 255, 13))

    draw_heart(draw, 1220, 420, 18, (220, 38, 38, 88))
    draw_heart(draw, 340, 710, 10, (15, 118, 110, 90))

    base_y = 520
    pulse = []
    x = 70
    pattern = [0, 0, -35, 62, -95, 24, 0, 0, 0, -18, 36, 0]
    for idx in range(70):
        pulse.append((x, base_y + pattern[idx % len(pattern)]))
        x += 22
    draw.line(pulse, fill=(252, 165, 165, 190), width=5, joint="curve")

    for cx, cy, r, color in [
        (1120, 750, 120, (255, 255, 255, 18)),
        (240, 260, 160, (20, 184, 166, 26)),
        (820, 210, 190, (220, 38, 38, 22)),
    ]:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)

    draw.text((86, 94), "CVD Predictor", font=font(66, True), fill=(255, 255, 255, 215))
    draw.text((92, 176), "Cardiovascular AI Screening", font=font(30), fill=(189, 231, 226, 220))

    image.save(path, quality=92)


if __name__ == "__main__":
    create_logo(ASSETS_DIR / "logo.png")
    create_logo(ASSETS_DIR / "medical_logo.png", compact=True)
    create_background(ASSETS_DIR / "heart_bg.jpg")
    print("Generated logo.png, medical_logo.png, and heart_bg.jpg")
