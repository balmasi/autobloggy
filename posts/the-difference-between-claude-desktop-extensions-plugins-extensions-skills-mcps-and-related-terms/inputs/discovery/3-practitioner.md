# Practitioner

## Query

`Claude Desktop extension allowlist enterprise custom connectors skills plugins`

## Source 1

### [When to use desktop and web connectors](https://support.claude.com/en/articles/11725091-when-to-use-desktop-and-web-connectors)

- Core thesis: Anthropic draws a practical line between local desktop extensions and remote web connectors based on data location, collaboration, and setup model.
- Useful points:
  - Local desktop extensions are for local files, apps, and system resources.
  - Remote connectors are for cloud tools, shared workspaces, and cross-device access.
  - Anthropic recommends using both together when needed.
- Gaps / misses:
  - This is decision-useful, but it never steps back and says "desktop extension is still part of the connector/MCP family."
  - It solves workflow choice more than language choice.

## Source 2

### [Getting Started with Local MCP Servers on Claude Desktop](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)

- Core thesis: Claude Desktop can install and manage local MCP-powered extensions operationally like productized add-ons.
- Useful points:
  - Extensions have a dedicated settings and logs surface in Claude Desktop.
  - Official directory extensions auto-update by default.
  - Privately distributed `.mcpb` files require manual updates.
- Gaps / misses:
  - The article is operational and assumes the conceptual model is already understood.
  - It uses "extension" as the product term without stopping to explain how it relates to MCP.

## Source 3

### [Enabling and using the desktop extension allowlist](https://support.claude.com/en/articles/12592343-enabling-and-using-the-desktop-extension-allowlist)

- Core thesis: desktop extensions are now managed enough to have org-level governance controls.
- Useful points:
  - Owners can allowlist approved extensions.
  - Non-allowlisted installations can be force-deleted.
  - Once allowlisting is active, users can install only sanctioned extensions from the in-app registry or approved custom `.mcpb` uploads.
- Gaps / misses:
  - This adds governance detail but not conceptual clarity.
  - The operational language makes extensions sound like a separate category from connectors, even though the docs elsewhere place them under the connector/MCP umbrella.

## Source 4

### [Deploying enterprise-grade MCP servers with desktop extensions](https://support.claude.com/en/articles/12702546-deploying-enterprise-grade-mcp-servers-with-desktop-extensions)

- Core thesis: Anthropic presents desktop extensions as the enterprise delivery vehicle for local MCP access.
- Useful points:
  - Extensions are positioned as a way to reach internal resources, local files, internal tools, and local apps.
  - The built-in Node runtime reduces install friction.
  - The article explicitly ties enterprise MCP servers to desktop extensions.
- Gaps / misses:
  - This is excellent evidence for the packaging/deployment angle, but it is not written as a terminology explainer.

## Takeaway

Practitioner-facing docs point to a simple rule:

- If the capability lives on your machine or inside your network boundary, Anthropic tends to talk about `desktop extensions`.
- If the capability is cloud-hosted and broadly portable, Anthropic tends to talk about `connectors` and `remote MCP`.

The missing bridge is saying clearly that these are two delivery shapes built on the same MCP foundation.
