import type { PatrickContext, PatrickResponse } from "../types";

/**
 * Provider architecture (interfaces only — no implementations yet).
 *
 * Patrick will eventually support answering from three sources:
 *   - LocalVaultSearch: index/query the user's Obsidian vault on-device.
 *   - LocalAiProvider:   a local LLM running on the user's machine.
 *   - RemoteAiProvider:  the existing Patrick Core server (OpenRouter, etc.).
 *
 * Defining these contracts now lets the UI and connection layer be built
 * against stable interfaces. Concrete implementations are added later without
 * touching callers.
 */

/** Searches the local vault and returns ranked note snippets. */
export interface LocalVaultSearch {
  /** Return up to `limit` relevant passages for `query` within `context`. */
  search(query: string, context: PatrickContext, limit?: number): Promise<VaultSearchResult[]>;
}

export interface VaultSearchResult {
  path: string;
  title: string;
  snippet: string;
  score: number;
}

/** A model that produces a reply from a prompt + retrieved context. */
export interface AiProvider {
  readonly id: string;
  readonly kind: "local" | "remote";
  /** True if the provider is currently usable (installed, reachable, etc.). */
  isAvailable(): Promise<boolean>;
  /** Generate a reply. Implementations decide how to use `context`. */
  complete(prompt: string, context: PatrickContext): Promise<PatrickResponse>;
}

/** Local LLM provider (e.g. a model served from the user's device). */
export interface LocalAiProvider extends AiProvider {
  readonly kind: "local";
}

/** Remote LLM provider (e.g. Patrick Core over HTTP). */
export interface RemoteAiProvider extends AiProvider {
  readonly kind: "remote";
}