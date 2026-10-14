"""Image transformation, independent from AWS so it can be tested locally."""

from io import BytesIO
import warnings
from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

MAX_BYTES = 10 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 24_000_000
SIZES = (150, 400, 1000)


class InvalidImage(ValueError):
    pass


def make_thumbnails(data, watermark="CLOUD PHOTO"):
    if not data or len(data) > MAX_BYTES:
        raise InvalidImage("Image must be between 1 byte and 10 MiB")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as probe:
                if probe.format not in ("JPEG", "PNG"):
                    raise InvalidImage("Only real JPEG/PNG images are accepted")
                if probe.width * probe.height > Image.MAX_IMAGE_PIXELS:
                    raise InvalidImage("Image exceeds 24 million pixels")
                if getattr(probe, "n_frames", 1) != 1:
                    raise InvalidImage("Animated images are not supported")
                image_format = probe.format
                probe.verify()
            with Image.open(BytesIO(data)) as source:
                oriented = ImageOps.exif_transpose(source).convert("RGBA")
                white = Image.new("RGBA", oriented.size, "white")
                white.alpha_composite(oriented)
                base = white.convert("RGB")
    except (
        UnidentifiedImageError,
        OSError,
        SyntaxError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise InvalidImage("Invalid, damaged, or oversized image") from exc

    outputs = []
    for size in SIZES:
        thumb = base.copy()
        thumb.thumbnail((size, size), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(thumb)
        text = watermark[:32]
        font_size = max(8, min(30, thumb.width // 12))
        font = ImageFont.load_default(size=font_size)
        while (
            font_size > 6
            and draw.textbbox((0, 0), text, font=font)[2] > thumb.width - 8
        ):
            font_size -= 1
            font = ImageFont.load_default(size=font_size)
        box = draw.textbbox((0, 0), text, font=font)
        x = max(0, thumb.width - box[2] - 6)
        y = max(0, thumb.height - (box[3] - box[1]) - 6)
        draw.rectangle(
            (max(0, x - 3), max(0, y - 3), thumb.width, thumb.height), fill="#182235"
        )
        draw.text((x, y - box[1]), text, font=font, fill="white")
        buffer = BytesIO()
        # Saving fresh JPEG data strips EXIF (including GPS) from thumbnails.
        thumb.save(buffer, "JPEG", quality=85, optimize=True)
        outputs.append(
            {
                "size": size,
                "width": thumb.width,
                "height": thumb.height,
                "data": buffer.getvalue(),
            }
        )
    return {
        "width": base.width,
        "height": base.height,
        "format": image_format,
        "bytes": len(data),
    }, outputs
