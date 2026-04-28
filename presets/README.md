# Presets

A preset is a reusable editorial pack under `presets/<name>/`.

Use a preset when multiple posts should share brand, writing, format, audience, or HTML template resources.

## Create A New Preset

1. Run `autobloggy new-preset --name <your-preset-name>`.
2. Edit `preset.yaml` and the resource files it references.
3. Run `autobloggy prep --preset <your-preset-name> --topic "..."`
4. Review the generated `blog_brief.md`.

## `preset.yaml`

Presets resolve resources generically:

```yaml
defaults:
  brand: general
  writing: general
  html_template: general
  audience: general
  format: blog

definitions:
  brand:
    general: brand_guide.md
  writing:
    general: writing_guide.md
  html_template:
    general: template.html
  audience:
    general: audience/general.md
    practitioner: audience/practitioner.md
  format:
    blog: formats/blog.md
    guide: formats/guide.md
```

Child presets can use `extends: default`, override defaults, and define only the resources that differ. Resource paths resolve relative to the preset where they are declared.
