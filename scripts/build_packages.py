"""Run from any directory: python scripts/build_packages.py [--skip-layer]."""

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)


def archive(source, target, prefix=""):
    with ZipFile(target, "w", ZIP_DEFLATED) as z:
        for p in sorted(source.rglob("*")):
            if p.is_file() and not any(
                x in p.parts for x in ("__pycache__", ".pytest_cache", ".venv")
            ):
                if p.name.startswith(".env"):
                    continue
                z.write(p, prefix + p.relative_to(source).as_posix())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-layer", action="store_true")
    args = parser.parse_args()
    archive(ROOT / "src/processor", DIST / "lambda_processor.zip")
    archive(ROOT / "src/web", DIST / "web_app.zip", "web/")
    if not args.skip_layer:
        with tempfile.TemporaryDirectory(prefix="cloud-photo-layer-") as temp:
            python_dir = Path(temp) / "python"
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "Pillow==12.3.0",
                    "--platform",
                    "manylinux_2_28_x86_64",
                    "--platform",
                    "manylinux2014_x86_64",
                    "--implementation",
                    "cp",
                    "--python-version",
                    "3.12",
                    "--abi",
                    "cp312",
                    "--only-binary=:all:",
                    "--no-deps",
                    "--target",
                    str(python_dir),
                ],
                check=True,
            )
            archive(Path(temp), DIST / "pillow_py312_x86_64.zip")
    print("Packages created in", DIST)
    for name in ("lambda_processor.zip", "web_app.zip", "pillow_py312_x86_64.zip"):
        p = DIST / name
        if not p.exists():
            continue
        print(p.name, p.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
