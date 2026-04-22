# Discovery

## Post

- Slug: `the-difference-between-claude-desktop-extensions-plugins-extensions-skills-mcps-and-related-terms`
- Topic: clarify the boundary between Claude desktop extensions, plugins, skills, MCP, and adjacent terms so a technical reader can choose the right label without confusion
- Audience: AI/ML founders who need a practical mental model, not a product-tour glossary

## Search Angles

1. Main: `Claude desktop plugins extensions skills MCP differences Anthropic`
2. Technical: `Claude local MCP server desktop extension MCPB remote connector differences Anthropic`
3. Practitioner: `Claude Desktop extension allowlist enterprise custom connectors skills plugins`
4. Alternative: `Claude Code skills MCP plugins complete guide terminology confusion`
5. Frame: `unified directory skills connectors plugins Claude why terms are confusing`

## Sources Reviewed

Distinct sources used across the sweep: 15

Official / primary sources:

- [Connectors overview](https://claude.com/docs/connectors/overview)
- [Skills overview](https://claude.com/docs/skills/overview)
- [Plugins overview](https://claude.com/docs/plugins/overview)
- [Create plugins](https://code.claude.com/docs/en/plugins)
- [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
- [What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Browse skills, connectors, and plugins in one directory](https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory)
- [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
- [When to use desktop and web connectors](https://support.claude.com/en/articles/11725091-when-to-use-desktop-and-web-connectors)
- [Getting Started with Local MCP Servers on Claude Desktop](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [Enabling and using the desktop extension allowlist](https://support.claude.com/en/articles/12592343-enabling-and-using-the-desktop-extension-allowlist)
- [Deploying enterprise-grade MCP servers with desktop extensions](https://support.claude.com/en/articles/12702546-deploying-enterprise-grade-mcp-servers-with-desktop-extensions)
- [MCP Bundles (MCPB)](https://github.com/modelcontextprotocol/mcpb)

Secondary sources used only to assess content landscape and common framing:

- [Claude Code Extensibility: Skills vs MCP vs Plugins Explained](https://www.morphllm.com/claude-code-skills-mcp-plugins)
- [Claude Code Extensions: Skills, MCP & Hooks](https://codingnomads.com/claude-code-extensions-skills-mcp-hooks)

## What Existing Content Gets Right

- Official docs consistently separate `skills`, `plugins`, and `MCP` once you find the right page.
- Anthropic's cleanest distinction is: skills are procedural knowledge, MCP connects Claude to external services, and plugins bundle multiple capabilities.
- The support docs clearly distinguish local desktop extensions from remote connectors in operational terms.
- Third-party explainers often have a better decision-oriented voice than the official docs, especially around "teach Claude how" vs "connect Claude to something."

## What Existing Content Gets Wrong Or Leaves Implicit

- The terminology is spread across multiple surfaces and products, so readers have to infer the taxonomy.
- Many explanations are Claude Code-first even when the user's confusion starts in Claude Desktop.
- "Extension" is overloaded:
  - sometimes it means a local Claude Desktop installable
  - sometimes it is used informally as a catch-all for any Claude customization
- "Plugin" is also overloaded:
  - officially it is a bundle/package term associated with Claude Code and Cowork
  - unofficially many people use it as a synonym for connector or extension
- The DXT -> MCPB rename adds another layer of drift between older content and newer tooling.
- Anthropic's unified directory makes discovery easier, but it visually places skills, connectors, and plugins next to each other in a way that encourages casual synonym use.

## Strongest Insight For The Post

The confusion is not mainly about definitions. It comes from mixing four different axes:

1. Protocol
   - `MCP` is the underlying standard.
2. Integration type
   - `connector` is a concrete integration that uses MCP.
3. Reusable knowledge
   - `skill` is instructions, workflow logic, and optional resources that teach Claude how to do something.
4. Packaging / distribution
   - `plugin` bundles capabilities for Claude Code and Cowork.
   - `desktop extension` / `MCPB` packages local MCP capability for Claude Desktop.

That is the angle most current content fails to state plainly.

## Recommended Outline Direction

- Open with the actual source of confusion: Anthropic uses related terms across different products, and the UI now exposes several of them side by side.
- Introduce a simple axis-based model before defining individual terms.
- Clarify `MCP` first as the protocol, because every other term sits above it.
- Separate `connector` from `desktop extension`:
  - connector = integration shape
  - desktop extension / MCPB = local installation and packaging shape inside Claude Desktop
- Separate `skill` from any executable integration:
  - skill = teach Claude how
  - connector / MCP = let Claude reach something
- Treat `plugin` as a bundle/package term, not the universal word for all Claude add-ons.
- Include one compact table that maps "what are you trying to do?" to the right term.

## Suggested Outline Angles

### Angle 1

Start with the wrong mental model:

- "All of these are just Claude plugins"

Then replace it with:

- "These terms live on different layers of the stack"

### Angle 2

Organize the post by user need:

- need Claude to know a workflow -> skill
- need Claude to access a tool or dataset -> connector via MCP
- need a local packaged install in Desktop -> desktop extension / MCPB
- need a shareable bundle of multiple capabilities -> plugin

### Angle 3

Use product surface as a clarifier, not the main structure:

- Claude Desktop
- Claude Code
- Cowork

This works best as a side note or comparison box, not the main narrative.

## Risks To Avoid In Drafting

- Do not write as if `plugin` is the universal official Anthropic term.
- Do not define `MCP` as if it were itself a product add-on.
- Do not let the post drift into a Claude Code-only taxonomy with hooks, subagents, and commands unless they are needed briefly as "adjacent terms."
- Do not overload the post with every nearby concept. The reader goal is clarity, not exhaustiveness.
- Do not ignore the DXT/MCPB rename if desktop extensions are discussed in any implementation detail.

## Best Differentiators

- Use official Anthropic terminology as the evidence backbone.
- Explain why the confusion happens, not just what each term means.
- Give the reader a reusable decision rule:
  - "knowledge, connection, package, or surface?"
- Keep the piece anchored in Claude Desktop confusion while borrowing only the minimum Claude Code context needed to define `plugin` correctly.
