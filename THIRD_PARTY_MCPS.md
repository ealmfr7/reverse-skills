# Third-Party MCP Servers

This file tracks third-party MCP servers used by this stack.

## `mobile-mcp`

- Local path: `third_party/mobile-mcp/`
- Source repository: https://github.com/mobile-next/mobile-mcp
- Package: https://www.npmjs.com/package/@mobilenext/mobile-mcp
- Installed Codex MCP name: `mobile-mcp`
- Installed command:

```bash
codex mcp add mobile-mcp -- npx -y @mobilenext/mobile-mcp@latest
```

Current submodule revision:

```text
468d9e99a57769d8e37d510d2db45ffdc4c2b4bb
```

`mobile-mcp` provides mobile device automation for Android and iOS through an
MCP server. For Android it uses ADB and UI Automator; for iOS it uses native
accessibility and WebDriverAgent-related tooling. It exposes agent-oriented
tools for listing devices, launching/installing apps, taking screenshots,
listing visible UI elements with coordinates, tapping, long-pressing, swiping,
typing, pressing device buttons, and opening URLs.

Use it when an agent needs to inspect and control a real device, emulator,
simulator, or native mobile app through structured accessibility snapshots and
coordinate-based fallback actions.
