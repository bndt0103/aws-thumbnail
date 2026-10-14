"""Generate sample images for thumbnail processing and invalid-input checks."""

from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1] / "tests/samples"
root.mkdir(parents=True, exist_ok=True)
for name, size, mode, color in [
    ("landscape.jpg", (1600, 1000), "RGB", "#2865ac"),
    ("portrait.jpg", (900, 1500), "RGB", "#bf6c4b"),
    ("square.png", (1000, 1000), "RGB", "#287764"),
    ("transparent.png", (800, 600), "RGBA", (0, 0, 0, 0)),
    ("small.png", (80, 60), "RGB", "#956daf"),
]:
    img = Image.new(mode, size, color)
    d = ImageDraw.Draw(img)
    w, h = size
    d.rectangle((w // 5, h // 5, w * 4 // 5, h * 4 // 5), fill="#f5d787")
    d.text((w // 4, h // 3), f"TEST IMAGE {size[0]} x {size[1]}", fill="#14243a")
    img.save(root / name)
(root / "broken.jpg").write_text("This is not an image", encoding="utf-8")
print("Created synthetic fixtures:", root)
