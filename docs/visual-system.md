# META-KORE visual system (Phase 1 draft, awaiting approval)

Direction: Computational Editorial. Black field, paper-white type and line, motion as traces of computation. See the implementation plan for the rationale.

## Tokens

| Token | Value | Use |
|---|---|---|
| `ink` | `#0A0A0B` | Background |
| `paper` | `#F2EFE8` | Primary type and line |
| `ash` | `#8B9098` | Secondary text, grid, annotations |
| `rule` | `#2A2C30` | Hairlines, faint grid on ink |
| `signal` | `#FF4D2E` | Optional accent, max one element per composition. **Undecided; the draft header uses none.** |

Contrast: paper on ink is about 17:1, ash on ink about 6:1 (passes AA for body text).

## Type

- Display and body: Space Grotesk (fallback Inter, Helvetica Neue, Arial).
- Labels and metadata: IBM Plex Mono (fallback JetBrains Mono, Consolas, monospace).
- GitHub renders README SVGs as images, so web fonts do not load inside them. The generator therefore converts all header text to outlines (wordmark in Inter Bold, labels in JetBrains Mono; needs `pip install fonttools` and those fonts installed). Space Grotesk is not bundled, so Inter Bold stands in until it is added. Without fontTools the generator falls back to live text for editing only.

## Grid and line

- Artwork canvas 1600 x 500 (3.2:1); displays at about 888 px wide in the README column, so minimum label size is 20 px on canvas (about 11 px displayed).
- 12-column grid, 40 px margin, 8 px baseline unit.
- Line weights: hairline 1, standard 2, emphasis 4 (canvas px). Never thinner than 1 px displayed.
- Annotations: mono, uppercase, letter-spacing 0.12em, numbered `01 / 02 / 03`.

## Graphic language

Plotted curves (superposed sines, Lissajous), coordinate ticks and crosshairs, node-and-edge diagrams, fine grids. Every mark should look measured, not decorated.

## Motion

- One signature loop in the README, 6 to 8 s, under 1.5 MB, no flashing, no more than 15 fps.
- README: GIF (animated SVG is not reliable on GitHub). Companion site: CSS/JS with `prefers-reduced-motion` fallback.
- First candidate: **plotted waveform that drifts phase**, rendered from the same generator as the static header so the two match.

## Plates

Each project gets one animated "plate": a figure of how it works, drawn in the same system (ink field, 80 px grid, axis ticks, mono labels, paper-white line, no accent colour).

- Canvas 1600 x 400. Corner labels: `PLATE nn / NAME` top left, a short descriptor top right, `PHASE x RAD` bottom left (the same readout as the header).
- Each plate is a pure function of loop position `u` in [0, 1) in `scripts/plates.py`, so every loop is seamless.
- Private projects are labelled `PRIVATE` in the descriptor and show only how the idea works, never code or internals.
- Build: `python scripts/render-plates.py [name ...] [--width 1200]` writes `assets/plates/<name>.gif` (16 colours, 12 fps, about 40 to 140 KB each). `--stills DIR` writes PNG stills for review. Needs ffmpeg and Node with Playwright.
- `assets/identity/social.png` (1280 x 640) is the repository social preview image; GitHub only accepts it as a manual upload in repository settings.

Plates so far: 01 allowance, 02 kitty, 03 tab-shelf, 04 simple_shell, 05 monty, 06 sorting_algorithms, 07 binary_trees, 08 daily haiku, 09 actionextract.

## Open decisions

1. Mark: `META-KORE` wordmark, `MK` monogram, or both (draft uses both).
2. Accent: strict monochrome vs one `signal` colour.
3. Signature animation: waveform (draft), network, field or typographic.
4. Headline copy.
