# Presets

A preset is a reusable editorial pack under `presets/<name>/`.

Use a preset when you want multiple posts to share the same strategy structure, writing style, or brand rules.

## Create A New Preset

1. Copy `presets/default/` to `presets/<your-preset-name>/`.
2. Edit the three files in the new folder.
3. Run `autobloggy new-post --preset <your-preset-name> ...` and review the generated `strategy.md`.

## What Each File Does

- `strategy_template.md`: shapes the per-post `strategy.md`
- `writing_guide.md`: defines voice, style, dos, and don'ts
- `brand_guide.md`: captures brand language, positioning, and terminology rules

## Example

```text
presets/
  my-preset/
    strategy_template.md
    writing_guide.md
    brand_guide.md
```
