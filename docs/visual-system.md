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
- GitHub renders README SVGs as images, so web fonts do not load inside them. Final header text must be **converted to outlines** so it looks identical everywhere. The generator keeps live text in the draft for editing only.

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

## Open decisions

1. Mark: `META-KORE` wordmark, `MK` monogram, or both (draft uses both).
2. Accent: strict monochrome vs one `signal` colour.
3. Signature animation: waveform (draft), network, field or typographic.
4. Headline copy.
