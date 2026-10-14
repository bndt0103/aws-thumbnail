import sys
from io import BytesIO
from pathlib import Path
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/processor"))
from image_tools import InvalidImage, make_thumbnails


def encoded(size=(1600, 1000), mode="RGB", fmt="JPEG"):
    b = BytesIO()
    Image.new(mode, size, (0, 0, 0, 0) if mode == "RGBA" else "#589bd1").save(b, fmt)
    return b.getvalue()


@pytest.mark.parametrize("shape", [(1600, 1000), (900, 1500), (1000, 1000), (80, 60)])
def test_three_sizes_keep_ratio_and_no_upscale(shape):
    original, variants = make_thumbnails(encoded(shape))
    assert (original["width"], original["height"]) == shape
    assert [v["size"] for v in variants] == [150, 400, 1000]
    for v in variants:
        assert v["width"] <= min(shape[0], v["size"])
        assert v["height"] <= min(shape[1], v["size"])
        assert abs(v["width"] * shape[1] - v["height"] * shape[0]) <= max(shape)
        im = Image.open(BytesIO(v["data"]))
        assert im.format == "JPEG"
        assert im.getpixel((im.width - 2, im.height - 2)) != im.getpixel((0, 0))


def test_transparency_becomes_white():
    _, variants = make_thumbnails(encoded(mode="RGBA", fmt="PNG"))
    im = Image.open(BytesIO(variants[1]["data"]))
    assert all(c >= 250 for c in im.getpixel((0, 0)))


@pytest.mark.parametrize(
    "raw",
    [b"", b"not an image", b"x" * (10 * 1024 * 1024 + 1)],
    ids=["empty", "invalid", "oversize"],
)
def test_invalid_inputs_rejected(raw):
    with pytest.raises(InvalidImage):
        make_thumbnails(raw)


def test_actual_gif_rejected_even_if_named_jpg():
    with pytest.raises(InvalidImage):
        make_thumbnails(encoded(fmt="GIF"))


def test_exif_orientation_and_metadata_removed():
    image = Image.new("RGB", (1200, 800), "orange")
    exif = Image.Exif()
    exif[274] = 6
    raw = BytesIO()
    image.save(raw, "JPEG", exif=exif)
    original, variants = make_thumbnails(raw.getvalue())
    assert (original["width"], original["height"]) == (800, 1200)
    assert not Image.open(BytesIO(variants[0]["data"])).getexif()
