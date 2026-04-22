# Main

## Query

`Claude desktop plugins extensions skills MCP differences Anthropic`

## Source 1

### [Connectors overview](https://claude.com/docs/connectors/overview)

- Core thesis: Anthropic treats connectors as the integration layer, powered by MCP.
- Useful points:
  - Connectors give Claude access to tools, data, and UI.
  - MCP is the protocol underneath connectors, not the user-facing packaging term.
  - Plugins are separate from connectors: they bundle MCP connectors, skills, slash commands, and sub-agents.
  - Platform support varies by surface: Claude Desktop gets full MCP support and local desktop extensions; Claude Code gets remote MCP access and plugins; Cowork gets full MCP and plugin support.
- Gaps / misses:
  - Good taxonomy, but it assumes the reader already understands why "connector," "MCP," "plugin," and "desktop extension" are not interchangeable.
  - The product-surface split is easy to miss.

## Source 2

### [Skills overview](https://claude.com/docs/skills/overview)

- Core thesis: Skills are reusable instructions, scripts, and resources that Claude loads dynamically for specific tasks.
- Useful points:
  - Skills are procedural, not connective.
  - Skills load on demand through progressive disclosure.
  - Anthropic explicitly compares skills against plugins, projects, MCP, and custom instructions.
  - The official contrast is sharp: skills are task procedures, MCP connects external services, plugins are bundles.
- Gaps / misses:
  - The page explains what skills are, but not why people confuse them with plugins or extensions in practice.
  - It is concept-first, not decision-first.

## Source 3

### [Plugins overview](https://claude.com/docs/plugins/overview)

- Core thesis: Plugins are shareable capability packages that bundle multiple extension types.
- Useful points:
  - Plugins originated in Claude Code.
  - Anthropic positions plugins as a packaging layer that can include skills, MCP connectors, slash commands, and sub-agents.
  - Official platform availability is narrow: Claude Code and Cowork, not "all Claude products."
- Gaps / misses:
  - The page is clear about composition but easy to overgeneralize from. Readers can leave thinking "plugin" is the generic Claude term for any add-on.
  - It does not spend much time on how plugins relate to Claude Desktop terminology.

## Takeaway

The best official baseline is:

- `MCP` = protocol
- `connector` = an integration built on MCP
- `skill` = reusable instructions/workflow knowledge
- `plugin` = bundle/package that can include skills and connectors
- `desktop extension` = Claude Desktop's local extension packaging/install surface

The main content gap is that Anthropic documents these pieces mostly in separate product docs, so a reader has to assemble the taxonomy themselves.
