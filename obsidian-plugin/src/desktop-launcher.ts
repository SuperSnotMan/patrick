import { Notice } from "obsidian";
import { access, mkdtemp, rm, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { homedir, tmpdir } from "node:os";
import { join } from "node:path";
import type { PatrickContext } from "./types";

/** Linux adapter: update the background bridge, then optionally open its Tk UI. */
export class DesktopLauncher {
  async open(context: PatrickContext, serverUrl: string, configuredAppPath: string, background = false): Promise<void> {
    const appPath = configuredAppPath.trim() || join(homedir(), "Projects", "Patrick", "patrick-linux");
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
