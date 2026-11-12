#!/usr/bin/env python3
"""Render project plates (scripts/plates.py) to assets/plates/<name>.gif.
Needs ffmpeg and Node with Playwright (Chromium) on PATH.

Usage:
  python scripts/render-plates.py [name ...] [--width 888]
  python scripts/render-plates.py --stills DIR [name ...]   # PNG stills for review
"""
import argparse, importlib.util, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("plates", ROOT / "scripts" / "plates.py")
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

ap = argparse.ArgumentParser()
ap.add_argument("names", nargs="*")
ap.add_argument("--width", type=int, default=888)
ap.add_argument("--stills")
ap.add_argument("--colors", type=int, default=16)
a = ap.parse_args()
names = a.names or list(P.PLATES)
out = ROOT / "assets" / "plates"; out.mkdir(parents=True, exist_ok=True)

for name in names:
    n, draw = P.PLATES[name]
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        idx = [0, n // 4, n // 2, (3 * n) // 4] if a.stills else range(n)
        svgs = []
        for i in idx:
            f = d / f"{name}-{i:03d}.svg"
            f.write_text(draw(i / n), encoding="utf-8")
            svgs.append(str(f))
        subprocess.run(["node", str(ROOT / "scripts" / "rasterize.js"), str(a.width), str(d), *svgs], check=True)
        if a.stills:
            dest = Path(a.stills); dest.mkdir(parents=True, exist_ok=True)
            for f in sorted(d.glob("*.png")):
                f.replace(dest / f.name)
            print("stills", name)
            continue
        pal = d / "pal.png"
        src = ["-framerate", "12", "-i", str(d / f"{name}-%03d.png")]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *src, "-vf",
                        f"palettegen=max_colors={a.colors}", str(pal)], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *src, "-i", str(pal), "-lavfi",
                        "paletteuse=dither=none", "-loop", "0", str(out / f"{name}.gif")], check=True)
        print("wrote", out / f"{name}.gif", (out / f"{name}.gif").stat().st_size // 1024, "KB")
