import { PatrickApi } from "../patrick-api";
import type { PatrickContext, PatrickResponse } from "../types";
import type { RemoteAiProvider } from "./types";

/**
 * Adapts the existing Patrick Core REST client to the RemoteAiProvider
 * interface. This is the only provider implemented today; local providers are
 * added later against the same contract without changing callers.
 */
export class PatrickCoreRemoteProvider implements RemoteAiProvider {
  readonly id = "patrick-core";
  readonly kind = "remote" as const;

  constructor(private readonly api: PatrickApi) {}

  async isAvailable(): Promise<boolean> {
    try {
      const result = await this.api.chat({ message: "", action: "ask", context: emptyContext() });
      // An empty message still round-trips through the server; treat any
      // well-formed response as "available".
      return typeof result.response === "string";
    } catch {
      return false;
    }
  }

  async complete(prompt: string, context: PatrickContext): Promise<PatrickResponse> {
    return this.api.chat({ message: prompt, action: "ask", context });
  }
}

function emptyContext(): PatrickContext {
  return {
    vault: "",
    vault_path: "",
    note: { title: "", path: "", content: "", cursor_line: 0, selection: "" },
  };
}