---
slug: the-difference-between-claude-desktop-extensions-plugins-extensions-skills-mcps-and-related-terms
title: Claude connectors, extensions, plugins, skills, and MCP are different layers
preset: georgian
preset_dir: presets/georgian
generated_at: '2026-04-22T03:08:20+00:00'
status: approved
approved_at: '2026-04-22T03:17:01+00:00'
---

# Outline

Title: Claude connectors, extensions, plugins, skills, and MCP are different layers

## Why this vocabulary feels messier than it is
- Open with a concrete observation from the product itself: in one place Anthropic says `connectors`, in another `skills`, in another `plugins`, and inside Claude Desktop the UI talks about `extensions`.
- Frame the reader problem directly: the same ecosystem is described with several nearby labels, so smart users end up treating them as synonyms.
- Land the opening claim fast: these terms are related, but they describe different layers of the stack.

## The product teaches different words in different places
- Explain why this is confusing now, not in the abstract:
  - Anthropic spreads the terminology across Claude Desktop, Claude Code, Cowork, and the unified directory.
  - Older `DXT` language still exists while newer tooling says `MCPB`.
  - Community posts often use `plugin` or `extension` as a catch-all even when the official docs do not.
- Keep this section to one short paragraph. No industry overview.

## The clean model is protocol, integration, instruction, and package
- State the core takeaway in one sentence:
  - If you separate protocol, integration, reusable instruction, packaging, and product surface, the vocabulary becomes straightforward.
- Promise the decision rule the reader can reuse:
  - ask whether you mean what Claude can reach, what Claude knows, how the capability is packaged, or where it runs

## MCP is the protocol, not the add-on
- Define `MCP` as the protocol and open standard, not as a plugin or end-user feature.
- Clarify what MCP actually does:
  - it gives AI clients a standard way to connect to tools, data, and, in some cases, UI
- Clarify what MCP is not:
  - not the same as a connector
  - not the same as a desktop extension
  - not the same as a skill
- Use one plain-language example:
  - a connector can use MCP
  - a desktop extension can package a local MCP-powered capability
- Drafting note: this section should remove the biggest conceptual error first, because every later definition depends on it.

## Connectors are the integration layer
- Define `connector` as the actual integration that lets Claude reach an external tool, data source, or interactive UI.
- Make the official framing explicit:
  - Anthropic uses `connector` for the integration layer across Claude products
  - connectors are powered by `MCP`, but they are not the same thing as `MCP`
- Split the connector world into the main shapes the reader will encounter:
  - prebuilt connectors from Anthropic
  - custom remote connectors using remote MCP
  - interactive connectors that can render UI components in the chat
- Use one practical example:
  - a GitHub, Slack, or Google Drive integration is best described as a connector
- Key mistake to call out:
  - people often say `plugin` when they really mean a connector

## Desktop extensions are the local packaging model
- Anchor this section in the distinction the reader actually needs:
  - a connector is the integration concept
  - a desktop extension is the local Claude Desktop installation and packaging term
- Then define `desktop extension` more precisely:
  - a desktop extension is the local Claude Desktop installation and packaging model for local capability
  - it is related to connectors, but it is not the generic name for all connectors
- Clarify the local vs remote split:
  - remote connectors talk to cloud-hosted services
  - desktop extensions package local access in Claude Desktop
- Define `desktop extension` as a Claude Desktop packaging and installation term for local capability, not a new protocol.
- Mention the rename briefly:
  - older material may say `DXT`
  - newer tooling says `MCPB`
- Use one practical contrast:
  - remote connector for a web service
  - desktop extension for local files, local apps, or internal resources reachable from the machine
- Key mistake to call out:
  - people say `extension` when they really mean either connector in general or a very specific local Desktop installable

## Skills teach Claude how to work
- Define `skill` as reusable instructions, workflow logic, scripts, and supporting resources that Claude loads when relevant.
- Make the contrast explicit:
  - `skill` = procedural knowledge
  - `connector` over `MCP` = external reach
- Explain why the distinction gets blurry in practice:
  - some partner skills are designed to work with connectors, so the workflow feels unified even though the underlying roles differ
- Use one concrete example pair:
  - a brand voice or deployment skill
  - versus a GitHub or Notion connector
- Key mistake to call out:
  - treating a skill as if it were the thing that connects Claude to a service

## Plugins bundle capabilities instead of naming every add-on
- Define `plugin` as a shareable bundle that can include skills, connectors, slash commands, and sub-agents.
- Clarify the official scope:
  - plugin is an official term in Claude Code and Cowork
  - it is not the broad Anthropic-wide label for every customization surface
- Explain why `plugin` still matters in this post even if the reader started with Claude Desktop confusion:
  - plugin is one of the main words people import from Claude Code into broader Claude conversations
  - that language drift is one reason the categories get blurred
- Tie this back to the reader's confusion:
  - many community explanations use `plugin` as shorthand for any Claude add-on, which collapses several different layers into one word
- Briefly place the adjacent terms without letting them take over the piece:
  - `slash commands` are explicit user-invoked workflows
  - `sub-agents` are delegated workers
  - `MCP Apps` are UI components surfaced through connectors
- Key mistake to call out:
  - once everything becomes a plugin, the reader loses the difference between packaging, protocol, and capability

## Why even careful users keep mixing these terms up
- Pull together the meta-explanation:
  - the unified directory places skills, connectors, and plugins next to each other
  - product surfaces use different labels for related concepts
  - older DXT language and newer MCPB language both remain in circulation
- Make the point explicit:
  - the confusion is not because the stack is incoherent
  - the confusion comes from mixing categories that answer different questions
- Use this section as the bridge into the decision table.

## A simple map for using the right term
- Insert a compact terminology map with five rows:
  - If you need Claude to connect to a web or cloud service -> `connector`
  - If you need Claude to know a workflow -> `skill`
  - If you mean the open standard underneath connectors and local integrations -> `MCP`
  - If you need a local packaged install in Claude Desktop -> `desktop extension` / `MCPB`
  - If you need a shareable bundle of multiple capabilities -> `plugin`
- Optional second column:
  - what people often say instead
  - why that shortcut is misleading

## The label changes the expectation
- Tell the reader what to do differently in real conversations and docs:
  - use `MCP` when talking about the standard
  - use `connector` when talking about the integration
  - use `desktop extension` when you mean the local Claude Desktop installable
  - use `skill` when you mean reusable instructions or workflow logic
  - use `plugin` only when you mean the bundle/package model
- Explain why precision matters:
  - the wrong word creates the wrong expectations about setup, security, portability, and where the capability actually lives

## The stack makes sense once you sort the layer
- Restate the thesis in one short paragraph:
  - the ecosystem is less messy than it sounds once you stop treating every term as the same category
- End with the reusable mental model:
  - protocol, connection, knowledge, package, surface
- Final line should leave the reader able to explain the stack to a teammate without adding new confusion.
