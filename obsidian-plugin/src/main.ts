import { Editor, Menu, Notice, Platform, Plugin, PluginSettingTab, Setting } from "obsidian";
import { buildObsidianContext } from "./context";
import { DesktopLauncher } from "./desktop-launcher";
import { resolveConnection } from "./connection";
import { PatrickApi } from "./patrick-api";
import { PatrickModal } from "./patrick-modal";
import type { PatrickAction } from "./types";

interface PatrickSettings {
  serverUrl: string;
  desktopAppPath: string;
}

const DEFAULT_SETTINGS: PatrickSettings = { serverUrl: "http://localhost:8000", desktopAppPath: "" };

export default class PatrickPlugin extends Plugin {
  settings: PatrickSettings = DEFAULT_SETTINGS;

  async onload(): Promise<void> {
    try {
      await this.loadSettings();
      this.addCommand({ id: "ask", name: "Ask", callback: () => this.openAskModal() });
      this.registerEvent(this.app.workspace.on("editor-menu", (menu, editor) => this.addContextMenu(menu, editor)));
      this.addSettingTab(new PatrickSettingTab(this.app, this));

      if (Platform.isMobile) return;

      this.addCommand({ id: "open-desktop-window", name: "Open desktop window", callback: () => void this.openDesktopWindow() });
      this.registerEvent(this.app.workspace.on("file-open", () => void this.syncContextInBackground()));
      this.app.workspace.onLayoutReady(() => void this.syncContextInBackground());
    } catch (error) {
      // A failure here must not disable the plugin on mobile. Log and stay enabled.
      console.error("Patrick failed to initialise fully:", error);
    }
  }

  openAskModal(): void {
    void this.resolveApi().then((api) =>
      new PatrickModal(this.app, api, () => buildObsidianContext(this.app)).open()
    );
  }

  private async openDesktopWindow(): Promise<void> {
    const context = await buildObsidianContext(this.app);
    await new DesktopLauncher().open(context, this.settings.serverUrl, this.settings.desktopAppPath);
  }

  /** Keep the native companion current without opening or focusing its window. */
  private async syncContextInBackground(): Promise<void> {
    const context = await buildObsidianContext(this.app);
    await new DesktopLauncher().open(context, this.settings.serverUrl, this.settings.desktopAppPath, true);
  }

  private addContextMenu(menu: Menu, editor: Editor): void {
    const selectedText = editor.getSelection();
    if (!selectedText) return;

    const items: Array<[PatrickAction, string]> = [
      ["explain", "Explain"], ["summarise", "Summarise"], ["quiz", "Quiz Me"], ["improve_writing", "Improve Writing"]
    ];
    menu.addSeparator();
    for (const [action, title] of items) {
      menu.addItem((item) => item.setTitle(`Patrick: ${title}`).setIcon("sparkles").onClick(() => void this.runAction(action, editor)));
    }
  }

  private runAction(action: PatrickAction, editor: Editor): void {
    const prompt = `${action.replace("_", " ")}: ${editor.getSelection()}`;
    void this.resolveApi().then((api) =>
      new PatrickModal(this.app, api, () => buildObsidianContext(this.app, editor), prompt, action).open()
    );
  }

  private get api(): PatrickApi {
    return new PatrickApi(this.settings.serverUrl);
  }

  /** Resolve the active Patrick Core connection, falling back gracefully. */
  private async resolveApi(): Promise<PatrickApi> {
    const connection = await resolveConnection(this.settings.serverUrl);
    if (connection.source === "local") {
      new Notice("Patrick Core is not reachable. Using local-only mode.");
    }
    return new PatrickApi(connection.baseUrl);
  }

  async loadSettings(): Promise<void> {
    this.settings = { ...DEFAULT_SETTINGS, ...(await this.loadData()) };
  }

  async saveSettings(): Promise<void> {
    await this.saveData(this.settings);
  }
}

class PatrickSettingTab extends PluginSettingTab {
  constructor(app: import("obsidian").App, private readonly plugin: PatrickPlugin) { super(app, plugin); }
  display(): void {
    this.containerEl.empty();
    new Setting(this.containerEl)
      .setName("Patrick Core URL")
      .setDesc("The local Patrick Core server address.")
      .addText((text) => text.setPlaceholder(DEFAULT_SETTINGS.serverUrl).setValue(this.plugin.settings.serverUrl).onChange(async (value) => {
        this.plugin.settings.serverUrl = value.trim() || DEFAULT_SETTINGS.serverUrl;
        await this.plugin.saveSettings();
      }));
    new Setting(this.containerEl)
      .setName("Patrick Linux companion path")
      .setDesc("Leave empty for ~/Projects/Patrick/desktop.")
      .addText((text) => text.setPlaceholder("~/Projects/Patrick/desktop").setValue(this.plugin.settings.desktopAppPath).onChange(async (value) => {
        this.plugin.settings.desktopAppPath = value.trim();
        await this.plugin.saveSettings();
      }));
  }
}
