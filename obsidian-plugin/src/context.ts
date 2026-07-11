import { App, Editor, MarkdownView } from "obsidian";
import type { PatrickContext } from "./types";

/**
 * Builds the complete request context for the active note without searching or
 * indexing the vault. Keep new, optional context sources alongside `note` so
 * the request shape can grow without changing callers.
 */
export async function buildObsidianContext(app: App, editor?: Editor): Promise<PatrickContext> {
  const view = app.workspace.getActiveViewOfType(MarkdownView);
  const activeEditor = editor ?? view?.editor;
  const file = app.workspace.getActiveFile();
  const cursor = activeEditor?.getCursor();
  let content = "";

  if (file) {
    try {
      content = await app.vault.read(file);
    } catch (error) {
      // Context collection must never prevent a user from asking Patrick.
      console.warn("Patrick could not read the active note.", error);
    }
  }

  return {
    vault: app.vault.getName(),
    note: {
      title: file?.basename ?? "",
      path: file?.path ?? "",
      content,
      cursor_line: cursor ? cursor.line + 1 : 0,
      selection: activeEditor?.getSelection() ?? ""
    }
  };
}
