# Georgian Brand Guide

## Identity

Georgian is a growth-equity fund that invests in AI-native software companies. The blog demonstrates AI thought leadership to founders, investors, and operators. Every post reinforces Georgian's identity as practitioners — people who build alongside portfolio companies, not just advise from a distance.

## Colour Palette

| Swatch | Name | Hex | Usage |
|--------|------|-----|-------|
| Primary | Blue | `#2746DA` | Hero backgrounds, primary chart series, dominant colour |
| Primary | Yellow | `#F8DB31` | Pull quote fills, contrasting chart series, paired with Blue |
| Text | Navy | `#012970` | Body text, headers, overlay text on light backgrounds |
| Accent | Orange | `#F7901E` | Third chart series only |
| Accent | Light Orange | `#F1BC0B` | Only alongside Yellow — never standalone |
| Background | Cool Gray | `#EBEBEB` | Backgrounds and dividers only — never text or icons |
| — | White | `#FFFFFF` | — |

**Usage rules:**
- Hero images and banners: Blue or Navy as the dominant background.
- Pull quotes and callout boxes: Yellow fill with Navy text, or Navy fill with White text.
- Data charts: Blue primary series → Yellow secondary → Orange tertiary (only if needed).
- Do not use Light Orange without Yellow alongside it.
- Cool Gray is for backgrounds and dividers only.

## Typography

| Element | Brand Font | Web Fallback | Notes |
|---------|-----------|--------------|-------|
| Post Title (H1) | Playfair Bold | Georgia, serif | Sentence case, 40pt+ |
| Section Header (H2) | Proxima Nova Semibold | Trebuchet MS | ALL CAPS, tracked wide |
| Sub-header (H3) | Proxima Nova Bold | Arial Bold | Sentence case |
| Body Copy | Proxima Nova Regular | Arial / Calibri | 16–18px, 1.5× line height |
| Captions & Footnotes | Proxima Nova Italic | Arial Italic | 12–14px, Navy or Gray |
| Pull Quotes | Proxima Nova Bold | Georgia Bold Italic | Large, left-aligned, coloured |

## Visual Identity

### Colour Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--color-brand-blue` | `#2746DA` | Dominant backgrounds, primary series, key connectors |
| `--color-brand-yellow` | `#F8DB31` | Secondary series, highlighted callouts, emphasis fills |
| `--color-brand-navy` | `#012970` | Body text, headers, labels, overlay text on light surfaces |
| `--color-brand-orange` | `#F7901E` | Tertiary chart series only |
| `--color-brand-light-orange` | `#F1BC0B` | Use only alongside Yellow, never standalone |
| `--color-brand-gray` | `#EBEBEB` | Backgrounds, dividers, low-emphasis surfaces |
| `--color-brand-white` | `#FFFFFF` | Inverted text and clean surface areas |

Do not invent alternate brand colours. Quote these hex values exactly in generated CSS.

### Typography Tokens

| Token | Stack | Usage |
|-------|-------|-------|
| `--font-display` | `"Playfair Display", Georgia, serif` | Large headlines and hero numerals |
| `--font-heading` | `"Proxima Nova", "Avenir Next", "Trebuchet MS", sans-serif` | Section titles and callout headers |
| `--font-body` | `"Proxima Nova", Arial, Calibri, sans-serif` | Body text, labels, captions |
| `--font-accent` | `"Proxima Nova", Georgia, serif` | Pull quotes and emphasized callouts |

Use sentence case except where the brand guide already specifies all-caps section headers.

### Chart Palette

Use this order unless the brief explicitly needs fewer series:

1. `--color-brand-blue`
2. `--color-brand-yellow`
3. `--color-brand-orange`

`--color-brand-light-orange` may appear only as a supporting accent next to Yellow. Charts should use direct labels where possible, with a short source caption beneath the visual.

### Component Patterns

- `pull-quote-band`: Blue or Navy background with White text, or Yellow background with Navy text
- `operator-framework`: 3-5 labeled columns or cards showing steps, criteria, or tradeoffs
- `portfolio-proof-strip`: restrained metric or evidence cards, never a noisy dashboard

Include subtle dividers, generous whitespace, and simple geometric framing over decorative illustration.

### Iconography And External Libraries

- Icons: use a restrained stroke icon set; prefer Lucide or inline SVG equivalents
- External libraries: allow hosted web fonts, one charting library if needed, and an icon CDN only when inline SVG is impractical

Keep the file self-contained beyond that allowlist.

### Aspect Ratios

- Default embed: `16 / 9`
- Side-by-side comparison or framework: `4 / 3`
- Pull quote or tall process: `3 / 4`

## Disclosures

Copy the exact text below into the CMS footnote field when applicable.

- **Portfolio company logos or names appear:**
  > "The information herein contains logos of third-party companies. These logos are the trademarked property of the respective companies and do not suggest or imply any affiliation, endorsement, or sponsorship of Georgian or any fund, vehicle or product."

- **Research or analysis cited:**
  > "The information herein is for illustrative and informational purposes only and is subject to change. The information is as of [DATE] unless otherwise indicated."

- **Portfolio performance metrics or forward-looking statements:** Contact Marketing (Megan V.) before publishing.
