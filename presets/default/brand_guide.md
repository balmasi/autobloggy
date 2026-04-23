# Default Brand Guide

## Naming & Terminology

- Use product, company, and tool names exactly as the source material spells them. Never invent abbreviations or alternatives.
- Prefer terms already established in the source over synonyms or category language you introduce.
- Keep claims scoped to what the source or approved strategy can support.

## Visual Identity

No publisher-specific brand defined. Apply these neutral defaults:

### Colour Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--color-bg` | `#F7F7F5` | Page or card background |
| `--color-surface` | `#FFFFFF` | Elevated panels and chart surfaces |
| `--color-text` | `#1F2933` | Body copy and labels |
| `--color-muted` | `#52606D` | Secondary labels and captions |
| `--color-accent` | `#0F766E` | Highlights, key lines, callouts |
| `--color-accent-soft` | `#D9F3EF` | Accent backgrounds and subtle fills |
| `--color-border` | `#D9E2EC` | Rules, borders, separators |

Use only these colour values in generated CSS unless the visual needs the source asset's original colours.

### Typography Tokens

| Token | Stack | Usage |
|-------|-------|-------|
| `--font-display` | `"Georgia", "Times New Roman", serif` | Titles and large callouts |
| `--font-body` | `"Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif` | Body copy, labels, annotations |
| `--font-mono` | `"SFMono-Regular", "SF Mono", Consolas, "Liberation Mono", monospace` | Code, numeric callouts, axis ticks |

Use weight and size to create hierarchy. Avoid decorative or novelty fonts.

### Chart Palette

Use this palette order for charts and diagrams:

1. `--color-accent`
2. `#2563EB`
3. `#7C3AED`
4. `#F59E0B`

Label axes and key data points directly. Cite the source in a caption below the figure. Never use 3D charts.

### Component Patterns

- `stat-card`: one large number, one short label, one supporting sentence
- `comparison-grid`: two or three columns with short headers and concise bullets
- `process-strip`: 3-5 ordered steps with arrows or dividers

### Iconography And External Libraries

- Icons: use simple stroke icons only; prefer inline SVG
- External libraries: none required by default; if a charting library materially helps, prefer a single lightweight CDN dependency and keep the rest of the file self-contained

### Aspect Ratios

- Standard embed: `16 / 9`
- Dense comparison or dashboard: `4 / 3`
- Tall process or timeline: `3 / 4`

## Disclosures

No standing disclosure language defined. Add publisher-specific legal or compliance footnotes here when the publisher requires them.
