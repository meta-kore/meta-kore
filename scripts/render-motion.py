#!/usr/bin/env python3
"""Render the header loop to assets/motion/header-loop.gif.
Needs ffmpeg, plus either ImageMagick 7 (magick) or Node with Playwright (Chromium) on PATH. Frames go to a temp dir.
Usage: python scripts/render-motion.py [frames] [width]
"""
import math, shutil, subprocess, sys, tempfile, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("ba", ROOT / "scripts" / "build-assets.py")
ba = importlib.util.module_from_spec(spec); spec.loader.exec_module(ba)

frames = int(sys.argv[1]) if len(sys.argv) > 1 else 48
width = int(sys.argv[2]) if len(sys.argv) > 2 else 888
out = ROOT / "assets" / "motion"; out.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    svgs = []
    for i in range(frames):
        phase = 2 * math.pi * i / frames  # full cycle -> seamless loop
        svg = d / f"f{i:03d}.svg"
        svg.write_text(ba.header(phase), encoding="utf-8")
        svgs.append(str(svg))
    if shutil.which("magick"):
        for svg in svgs:
            subprocess.run(["magick", "-background", "none", "-density", "96", svg,
                            "-resize", f"{width}x", svg[:-4] + ".png"], check=True)
    else:
        subprocess.run(["node", str(ROOT / "scripts" / "rasterize.js"), str(width), str(d), *svgs], check=True)
    pal = d / "pal.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "12", "-i", str(d / "f%03d.png"),
                    "-vf", "palettegen=max_colors=24", str(pal)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "12", "-i", str(d / "f%03d.png"),
                    "-i", str(pal), "-lavfi", "paletteuse=dither=none", "-loop", "0",
                    str(out / "header-loop.gif")], check=True)
print("wrote", out / "header-loop.gif")
