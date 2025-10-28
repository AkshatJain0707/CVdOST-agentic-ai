from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

def make_image(path: Path, size=(256, 256), color=(0, 128, 255), text="RESUMATE"):
    img = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except Exception:
        w, h = font.getsize(text)
    draw.text(((size[0]-w)/2, (size[1]-h)/2), text, fill=(255,255,255), font=font)
    img.save(path)

if __name__ == "__main__":
    make_image(ASSETS_DIR / "logo.png", size=(180, 180), text="RESUMATE")
    make_image(ASSETS_DIR / "icon.png", size=(120, 120), text="RA")
    print("Placeholders generated:", ASSETS_DIR / "logo.png", ASSETS_DIR / "icon.png")
