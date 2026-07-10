# Transferred Learnings Brand Guide

## Identity

Transferred Learnings (TL) is Georgian's AI builder community. It brings together AI researchers, engineers, founders, and practitioners for real talk about what is working in the field, run both online and through in-person "TL/IRL" events. The brand voice is technical, direct, and practitioner-first. The community arc is **EXPLORE → LEARN → BUILD**: start curious, get concrete, ship something.

The look is dark-mode and technical — obsidian surfaces, an electric-green accent, and a blue-to-green gradient — with clean monospaced type.

## Wordmarks

| Asset | File | Usage |
|-------|------|-------|
| Primary wordmark | `assets/wordmark-color.png` | Stacked "Georgian / TRANSFERRED LEARNINGS" — Georgian in white, TRANSFERRED LEARNINGS in electric green. Default lockup on obsidian backgrounds. |
| Wordmark (black) | `assets/wordmark-black.png` | Monochrome black lockup for light backgrounds and print. |
| Wordmark (white) | `assets/wordmark-white.png` | Monochrome white lockup for photos and busy dark backgrounds. |
| Discord icon | `assets/discord-icon.png` | "GTL" monogram used as the community avatar / favicon. |

The full design source lives at `assets/brand-guide-source.jpg` (reference only, not shipped in posts).

## Colour Palette

| Swatch | Name | Hex | Usage |
|--------|------|-----|-------|
| Primary | Obsidian | `#12131B` | Dominant background for heroes and dark surfaces |
| Primary | White | `#FFFFFF` | Headers on dark surfaces; clean light reading surfaces |
| Accent | Electric Green | `#81F353` | Accent, links, subheaders when a gradient is not available |
| Accent | Georgian Blue | `#2746DA` | Start of the accent gradient; secondary chart series |
| Accent | Accent Gradient | `#2746DA → #81F353` | Georgian Blue → Electric Green, left-to-right. Subheaders and emphasis. |
| Support | Gray Scale | — | Supporting surfaces, dividers, and low-emphasis fills only |

**Usage rules:**
- Obsidian is the dominant background. Reserve white/light surfaces for long-form body reading.
- Subheaders use the accent gradient (Georgian Blue → Electric Green). If the editing surface cannot render a gradient, use flat Electric Green.
- Electric Green is an accent, not a body colour. Never set body copy in green.
- Gray scale is for supporting surfaces and dividers only — never for body text or icons.

### Print

For any printed collateral, substitute the screen colours with these specs:

| Name | Hex | Pantone | Book |
|------|-----|---------|------|
| Electric Green Print | `#69FF47` | Pantone 13-0340 TN "Green Gecko" | f+h nylon brights TN |
| Electric Green Print (alt) | `#44D62C` | Pantone 802 C | Pastels & Neons Coated |
| Obsidian Print | `#101820` | Pantone Black 6 C | Solid Coated-V5 |

## Typography

Primary font is **SUSE Mono Semibold** — a monospaced typeface. Readability is the single most important property of body text, so body copy is always a dark font on a light background.

| Element | Font | Colour | Notes |
|---------|------|--------|-------|
| Headers | SUSE Mono Semibold | White | On obsidian / dark surfaces |
| Subheaders | SUSE Mono Semibold | Accent Gradient (fallback Electric Green) | Blue → Green left-to-right |
| Body Copy | SUSE Mono | Obsidian `#12131B` on light background | Readability first: always dark font on light background |

## Visual Identity

### Colour Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--color-brand-obsidian` | `#12131B` | Dominant dark background; body text on light surfaces |
| `--color-brand-white` | `#FFFFFF` | Headers on dark; clean light surfaces |
| `--color-brand-green` | `#81F353` | Accent, links, flat subheaders, primary chart series |
| `--color-brand-blue` | `#2746DA` | Gradient start; secondary chart series |
| `--gradient-accent` | `linear-gradient(90deg, #2746DA 0%, #81F353 100%)` | Subheaders and emphasis fills |

Do not invent alternate brand colours. Quote these hex values exactly in generated CSS.

### Typography Tokens

| Token | Stack | Usage |
|-------|-------|-------|
| `--font-heading` | `"SUSE Mono", ui-monospace, "SFMono-Regular", Menlo, monospace` | Headers and subheaders (semibold) |
| `--font-body` | `"SUSE Mono", ui-monospace, "SFMono-Regular", Menlo, monospace` | Body text, labels, captions |

SUSE Mono is available as a hosted Google Font. If web fonts are unavailable, fall back to the system monospace stack above.

### Chart Palette

Use this order unless the brief explicitly needs fewer series:

1. `--color-brand-green`
2. `--color-brand-blue`
3. Gray scale supporting tones

Use the accent gradient only for a single emphasized series or a hero connector. Charts should use direct labels where possible, with a short source caption beneath the visual.

### Approved Textures

Three textures are approved for hero and section backgrounds — ideally rendered with the accent gradient, otherwise flat Electric Green:

1. Neon lines / tubes
2. Grids / tech-spec linework
3. Abstract lights

Keep textures on dark obsidian surfaces. Never place a texture behind body copy.

### Component Patterns

- `hero-band`: obsidian background, white header, gradient or neon texture, wordmark top-left
- `journey-strip`: EXPLORE → LEARN → BUILD progression as a labeled, arrowed row
- `event-card`: near-square (1 / 1) TL/IRL card — obsidian, gradient texture, white title, small green eyebrow

Favor clean geometric framing and generous whitespace over decorative illustration.

### Iconography And External Libraries

- Icons: restrained stroke icon set; prefer Lucide or inline SVG equivalents
- External libraries: allow the hosted SUSE Mono web font, one charting library if needed, and an icon CDN only when inline SVG is impractical

Keep the file self-contained beyond that allowlist.

### Aspect Ratios

- Default embed: `16 / 9`
- Event card / social tile: `1 / 1`
- Side-by-side comparison or framework: `4 / 3`

## Disclosures

Transferred Learnings is a Georgian community brand. When a post carries Georgian branding, mentions Georgian portfolio companies, or makes investment-related or performance claims, Georgian's disclosure and compliance rules apply — see `presets/georgian/brand_guide.md` for the exact disclosure text and, for portfolio performance or forward-looking statements, contact Georgian Marketing before publishing.
