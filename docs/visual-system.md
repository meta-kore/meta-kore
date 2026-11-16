# META-KORE visual system

Direction: Computational Editorial. Black field, paper-white type and line, motion as traces of computation. Approved and in use across the profile and the project READMEs.

## Tokens

| Token | Value | Use |
|---|---|---|
| `ink` | `#0A0A0B` | Background |
| `paper` | `#F2EFE8` | Primary type and line |
| `ash` | `#8B9098` | Secondary text, grid, annotations |
| `rule` | `#2A2C30` | Hairlines, faint grid on ink |
| `signal` | `#FF4D2E` | Reserved accent, max one element per composition. **Not used: the system is strictly monochrome.** |

Contrast: paper on ink is about 17:1, ash on ink about 6:1 (passes AA for body text).

## Type

- Display and body: Space Grotesk (fallback Inter, Helvetica Neue, Arial). Used for the wordmark.
- Labels and metadata: IBM Plex Mono (fallback JetBrains Mono, Consolas, monospace).
- GitHub renders README SVGs as images, so web fonts do not load inside them. The generator therefore converts all text to outlines, using fonts vendored in `assets/fonts/` (Space Grotesk Bold for the wordmark, JetBrains Mono Regular for labels; both SIL OFL, licence texts alongside). It needs `pip install fonttools`. Without fontTools it falls back to live text, for editing only. IBM Plex Mono remains the spec's first-choice mono; JetBrains Mono is what the assets actually use.

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

- Canvas 1600 x 460 (content laid out on 1600 x 400 and shifted down 30 px for the corner labels). Primary labels are 42 px on the canvas, about 9 px on a phone and 23 px at README width; keep new text at or above that. Corner labels: `PLATE nn / NAME` top left, a short descriptor top right, `PHASE x RAD` bottom left (the same readout as the header).
- Each plate is a pure function of loop position `u` in [0, 1) in `scripts/plates.py`, so every loop is seamless.
- Private projects are labelled `PRIVATE` in the descriptor and show only how the idea works, never code or internals.
- Build: `python scripts/render-plates.py [name ...] [--width 1200]` writes `assets/plates/<name>.gif` (16 colours, 12 fps, about 55 to 155 KB each). `--stills DIR` writes PNG stills for review. Needs ffmpeg and Node with Playwright.
- `assets/identity/social.png` (1280 x 640) is the repository social preview image; GitHub only accepts it as a manual upload in repository settings.

Plates so far: 01 allowance, 02 kitty, 03 tab-shelf, 04 simple_shell, 05 monty, 06 sorting_algorithms, 07 binary_trees, 08 daily-haiku, 09 actionextract, 10 printf. The hackathon submissions (`allowance`, `kitty`) show their plate on the profile only; their own READMEs are left as submitted.

## Marks

- **Wordmark:** `META-KORE`, Space Grotesk Bold, outlined. Used in the header and social card.
- **Monogram:** `MK`, two plotted strokes on a 200 unit grid: the M is two verticals joined by a V, the K is a vertical with two arms, and a small node marks the vertex of the M. Defined once in `scripts/build-assets.py` (`MK_PATHS`) and used by `mark.svg` and the avatar.
- **Avatar:** `assets/identity/avatar.png` (500 x 500), the monogram on the ink grid. GitHub crops avatars to a circle; the monogram sits well inside it.

## Assets

| File | Use |
|---|---|
| `assets/motion/header-loop.gif` | Animated header at the top of the profile README |
| `assets/identity/header.svg` | Static header (same artwork, phase 0) |
| `assets/identity/mark.svg`, `avatar.svg` / `avatar.png` | Monogram and profile picture |
| `assets/identity/social.svg` / `social.png` | Repository social preview, 1280 x 640 |
| `assets/plates/*.gif` | One animated plate per project (see Plates) |
| `assets/fonts/` | Vendored fonts and licences |

Rebuild everything: `python scripts/build-assets.py`, `python scripts/render-motion.py`, `python scripts/render-plates.py`, then rasterize the avatar and social card with `node scripts/rasterize.js <width> <outdir> <svg>`.

Some things GitHub only accepts through its web interface, not through any API: the profile picture, the repository social preview and the profile's pinned repositories.

## Adding a project to the system

1. Add a plate function to `scripts/plates.py` that shows how the project works, using the project's real behaviour and exact repo name in the title. Register it in `PLATES`.
2. `python scripts/render-plates.py <name> --width 1200`, then view stills with `--stills DIR` and check labels at 358 px wide.
3. In the project's own README, put the GIF at `assets/plate.gif` and embed it directly under the title; add the project to the profile README with its name first, then the plate, then one or two sentences.

## Decisions (resolved)

1. Mark: both. Wordmark for the header, MK monogram for the avatar.
2. Accent: none. Strict monochrome.
3. Signature animation: the drifting waveform, with per-project plates in the same language.
4. Headline copy: still open; the positioning line on the profile is a draft until confirmed.
