import { Platform, requestUrl } from "obsidian";

/**
 * Connection resolution for Patrick Core.
 *
 * The plugin must reach Patrick Core from many environments:
 *   1. A local Patrick server on the LAN (desktop or mobile on the same network).
 *   2. A future public endpoint (not yet implemented — kept as a clean seam).
 *   3. A local-only placeholder when nothing else is reachable.
 *
 * This module owns that priority logic so callers (the API client) only ever
 * ask for "the active connection" without knowing how it was chosen.
 */

/** A resolved connection target. */
export interface PatrickConnection {
  /** Base URL the API client should talk to. */
  baseUrl: string;
  /** Where this connection came from, for diagnostics/UI. */
  source: "lan" | "public" | "local";
}

/** Builds the ordered list of candidate endpoints from user configuration. */
function candidateUrls(configuredUrl: string): string[] {
  const trimmed = configuredUrl.trim();
  const candidates: string[] = [];

  // 1. The user-configured LAN server (default http://localhost:8000).
  if (trimmed) {
    candidates.push(trimmed);
  }

  // 2. Future public endpoint. Intentionally left as a documented seam; the
  //    public host is resolved elsewhere (e.g. a settings field) when added.
  //    Until then it contributes nothing so the priority chain stays honest.
  const publicUrl = resolvePublicEndpoint();
  if (publicUrl) {
    candidates.push(publicUrl);
  }

  return candidates;
}

/**
 * Placeholder for the future public endpoint.
 *
 * Returns null today. When the public endpoint is introduced, return the
 * configured public URL here — no other code needs to change because the
 * priority chain already honours whatever this returns.
 */
function resolvePublicEndpoint(): string | null {
  return null;
}

/** The fallback used when no real server is reachable. */
const LOCAL_PLACEHOLDER: PatrickConnection = {
  baseUrl: "http://localhost:8000",
  source: "local",
};

/** True if the endpoint answers a basic health check. */
async function isReachable(baseUrl: string): Promise<boolean> {
  try {
    const result = await requestUrl({
      url: `${baseUrl.replace(/\/$/, "")}/`,
      method: "GET",
      throw: false,
    });
    return result.status >= 200 && result.status < 400;
  } catch {
    return false;
  }
}

/**
 * Resolve the best available Patrick Core connection.
 *
 * Tries candidates in priority order (LAN first, then public) and returns the
 * first that responds. If none respond, returns the local-only placeholder so
 * the UI can show a clear "offline / local-only" state instead of crashing.
 */
export async function resolveConnection(configuredUrl: string): Promise<PatrickConnection> {
  // On mobile the configured LAN URL is the only realistic option; the public
  // seam is still evaluated uniformly so behaviour stays consistent.
  for (const url of candidateUrls(configuredUrl)) {
    if (await isReachable(url)) {
      const source: PatrickConnection["source"] = url === resolvePublicEndpoint() ? "public" : "lan";
      return { baseUrl: url, source };
    }
  }

  return LOCAL_PLACEHOLDER;
}

/** Synchronous best-effort base URL without a network probe (e.g. for setup). */
export function preferredUrl(configuredUrl: string): string {
  const candidates = candidateUrls(configuredUrl);
  return candidates[0] || LOCAL_PLACEHOLDER.baseUrl;
}

export const isMobile = Platform.isMobile;