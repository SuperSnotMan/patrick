import { Notice, Platform } from "obsidian";
import type { PatrickContext } from "./types";

/**
 * Desktop companion bridge.
 *
 * On desktop this updates the background bridge state and optionally opens the
 * native PySide6 window. On mobile those Node-only operations are unavailable,
 * so the launcher degrades to a no-op while the rest of the plugin (chat over
 * the REST API) keeps working unchanged.
 */
export class DesktopLauncher {
  async open(context: PatrickContext, serverUrl: string, configuredAppPath: string, background = false): Promise<void> {
    if (Platform.isMobile) {
      // Mobile has no native companion and no Node runtime. The plugin still
      // talks to Patrick Core over HTTP, so there is nothing to launch here.
      return;
    }

    await this.openDesktop(context, serverUrl, configuredAppPath, background);
  }

  private async openDesktop(context: PatrickContext, serverUrl: string, configuredAppPath: string, background: boolean): Promise<void> {
    // Imported lazily so the Node-only modules are never evaluated on mobile.
    const { access, mkdtemp, rm, writeFile } = await import("node:fs/promises");
    const { spawn } = await import("node:child_process");
    const { homedir, tmpdir } = await import("node:os");
    const { join } = await import("node:path");

    const appPath = configuredAppPath.trim() || join(homedir(), "Projects", "Patrick", "desktop");
    const bridge = join(appPath, "bridge_client.py");
    const launcher = join(appPath, "launch.sh");
    let directory: string | undefined;
    try {
      await access(bridge);
      if (!background) await access(launcher);
      directory = await mkdtemp(join(tmpdir(), "patrick-context-"));
      const contextFile = join(directory, "context.json");
      await writeFile(contextFile, JSON.stringify(context), { encoding: "utf8", mode: 0o600 });
      const child = spawn("/usr/bin/python3", [bridge, "--context-file", contextFile, "--server-url", serverUrl], {
        detached: true,
        stdio: "ignore",
      });
      child.once("error", () => { if (directory) void rm(directory, { recursive: true, force: true }); });
      child.unref();
      if (!background) {
        const window = spawn(launcher, [], { detached: true, stdio: "ignore" });
        window.unref();
      }
    } catch {
      if (directory) await rm(directory, { recursive: true, force: true });
      new Notice("Patrick Linux companion is not installed. Configure its path in Patrick settings.");
    }
  }
}