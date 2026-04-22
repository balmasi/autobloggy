# Technical

## Query

`Claude local MCP server desktop extension MCPB remote connector differences Anthropic`

## Source 1

### [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)

- Core thesis: remote connectors are MCP servers reached through Anthropic's cloud, not through the local machine.
- Useful points:
  - Anthropic now distinguishes local MCP from remote MCP.
  - Remote custom connectors work across Claude, Cowork, and Claude Desktop, but the connection originates from Anthropic infrastructure.
  - The page explicitly says local MCP servers configured in Claude Desktop are a separate mechanism.
  - Interactive connectors are still connectors; the UI is a capability on top of MCP, not a separate protocol.
- Gaps / misses:
  - Good network model, but the page is framed around setup rather than terminology.
  - It helps explain "remote connector" vs "local desktop extension," but only if the reader is already deep enough to notice the distinction.

## Source 2

### [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)

- Core thesis: MCP is the transport/tool standard used across Claude products, including cross-surface import and reuse.
- Useful points:
  - Claude Code can import MCP server definitions from Claude Desktop.
  - Claude Code can itself act as an MCP server and be connected back into Claude Desktop.
  - This reinforces that MCP is a protocol layer, not a specific Claude Desktop feature.
- Gaps / misses:
  - The page is Claude Code-centric, so Desktop readers may not realize which concepts generalize and which are Code-specific.
  - It explains how to configure MCP, not how to explain the ecosystem in plain language.

## Source 3

### [MCP Bundles (MCPB)](https://github.com/modelcontextprotocol/mcpb)

- Core thesis: what Anthropic previously called DXT/Desktop Extensions has been renamed to MCP Bundles.
- Useful points:
  - The repo states the rename from DXT to MCPB directly.
  - `.mcpb` files are zip bundles containing a local MCP server and a `manifest.json`.
  - Claude Desktop is an example client that can open the file and show an installation dialog.
  - This makes the relationship explicit: a desktop extension is a distribution/install artifact for a local MCP server, not a new integration protocol.
- Gaps / misses:
  - This is developer-facing infrastructure language, not end-user help language.
  - The rename itself is part of the confusion because older content still says DXT/Desktop Extension while newer tooling says MCPB.

## Takeaway

The strongest technical frame is:

- `MCP` is the underlying protocol.
- `remote connector` is an MCP server reached over the internet.
- `local desktop extension` is the Desktop-side packaging and install path for local MCP capability.
- `MCPB` is the current bundle format name behind that local extension model.

This is one of the highest-value distinctions for the eventual outline because many posts collapse all four into "plugins."
