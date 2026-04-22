# Frame

## Query

`unified directory skills connectors plugins Claude why terms are confusing`

## Source 1

### [Browse skills, connectors, and plugins in one directory](https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory)

- Core thesis: Claude now groups multiple customization types in one discovery surface.
- Useful points:
  - Skills, connectors, and plugins live in one directory.
  - The install action looks similar across categories.
  - The directory is product UX, not a taxonomy lesson.
- Gaps / misses:
  - This page explains where to click, not how the concepts differ.

## Source 2

### [Connectors overview](https://claude.com/docs/connectors/overview)

- Core thesis: the same ecosystem is described through product-surface-specific labels.
- Useful points:
  - Claude Desktop: full MCP support and local desktop extensions.
  - Claude Code: remote MCP access and plugins.
  - Claude Cowork: full MCP and plugin support.
  - MCP Apps sit underneath connectors as UI components.
- Gaps / misses:
  - The terminology map is distributed across platform rows instead of being stated head-on.

## Source 3

### [MCP Bundles (MCPB)](https://github.com/modelcontextprotocol/mcpb)

- Core thesis: even the local packaging term has changed recently.
- Useful points:
  - DXT became MCPB.
  - `.dxt` became `.mcpb`.
  - Old articles and repos may still use the older names.
- Gaps / misses:
  - Rename churn makes the ecosystem feel less stable than it is.

## Source 4

### [What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills)

- Core thesis: the official help center already contains the cleanest cross-category distinction for skills.
- Useful points:
  - Skills vs projects, skills vs MCP, and skills vs custom instructions are all spelled out.
  - The key phrase is that skills provide procedural knowledge while MCP connects Claude to external services and data sources.
- Gaps / misses:
  - The help article stops at skills and does not extend the same clean comparison into plugins and desktop extensions.

## Takeaway

The framing opportunity is to organize the post around four different axes that the current docs mix together:

- `What Claude knows` -> skills
- `What Claude can reach` -> connectors built on MCP
- `How capability is packaged/distributed` -> plugins or desktop extensions / MCPB
- `Which product surface supports it` -> Claude Desktop, Claude Code, Cowork, Claude.ai

That framing feels more useful than a dictionary-style glossary because it explains the source of the confusion.
