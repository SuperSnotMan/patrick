# Patrick for Obsidian

A deliberately thin Obsidian client for Patrick Core. It provides an `Patrick: Ask` command and selected-text actions under the editor context menu.

## Develop

```bash
npm install
npm run dev
```

Copy `manifest.json`, `styles.css`, and the generated `main.js` into your vault's `.obsidian/plugins/patrick/` folder, then enable **Patrick** in Obsidian's Community Plugins settings. Patrick Core defaults to `http://localhost:8000`; change it in the plugin settings if needed.

Every request also includes an automatically gathered `context` object: vault name, active-note title and path, full note contents, one-based cursor line, and selected text (or an empty string). The plugin reads only the current note; it does not search or index the vault. Patrick Core uses the current note content as the sole source for answers.

## Desktop companion

Use **Patrick: Open desktop window** to open the native companion with the active note context. Its **Always on top** control is a real desktop-window setting, so it can remain visible above another application. By default the launcher looks for the companion at `~/Projects/Patrick/patrick-desktop`; override that path in Patrick's plugin settings when needed.
