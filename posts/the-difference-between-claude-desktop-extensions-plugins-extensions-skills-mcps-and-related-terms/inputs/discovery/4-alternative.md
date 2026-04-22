# Alternative

## Query

`Claude Code skills MCP plugins complete guide terminology confusion`

## Source 1

### [Claude Code Extensibility: Skills vs MCP vs Plugins Explained](https://www.morphllm.com/claude-code-skills-mcp-plugins)

- Core thesis: the clean mental model is skills for procedures, MCP for external tools, plugins for bundles, hooks for automation, and commands for prompt shortcuts.
- Useful points:
  - Strong decision-oriented framing.
  - Clear distinction between "teach Claude how" and "connect Claude to."
  - Helpful reminder that a plugin can contain skills and MCP.
- Gaps / misses:
  - It is Claude Code-first, not Claude Desktop-first.
  - It expands the taxonomy beyond the user's immediate confusion, which can help technical readers but overwhelm broader readers.
  - Some details are fast-moving and depend on current Claude Code behavior.

## Source 2

### [Claude Code Extensions: Skills, MCP & Hooks](https://codingnomads.com/claude-code-extensions-skills-mcp-hooks)

- Core thesis: most confusion comes from mixing reusable knowledge, isolated workers, automation hooks, and packaging under one vague idea of "extensions."
- Useful points:
  - Useful line: skill = reusable content; subagent = isolated worker.
  - Strong framing of plugin as packaging rather than a separate extension type.
  - Good "what do you want Claude to know vs connect to vs automate" decision lens.
- Gaps / misses:
  - Also Code-centric.
  - Includes warnings that some fields or behaviors may have changed, which undercuts authority.
  - Not grounded in Claude Desktop terminology.

## Source 3

### [Browse skills, connectors, and plugins in one directory](https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory)

- Core thesis: Anthropic's product UI now presents skills, connectors, and plugins side by side in one unified directory.
- Useful points:
  - One interface now exposes all three concepts.
  - Installation flow looks similar even though the underlying category is different.
  - This is likely part of why users collapse the terms in conversation.
- Gaps / misses:
  - The unified directory improves discoverability, but it flattens conceptual distance at the point of installation.
  - It does not teach a mental model; it assumes the user already knows which tab they need.

## Takeaway

The strongest alternative framing is not "there are too many definitions," but "the UI and community content encourage category collapse."

That suggests the post should not merely define terms. It should explain why smart users keep mixing them up.
