import { requestUrl } from "obsidian";
import type { PatrickRequest, PatrickResponse } from "./types";

/** Keeps Patrick Core's HTTP contract in one place as endpoints grow. */
export class PatrickApi {
  constructor(private readonly baseUrl: string) {}

  async chat(request: PatrickRequest): Promise<PatrickResponse> {
    const result = await requestUrl({
      url: `${this.baseUrl.replace(/\/$/, "")}/chat`,
      method: "POST",
      contentType: "application/json",
      body: JSON.stringify(request),
      throw: false
    });

    if (result.status < 200 || result.status >= 300) {
      throw new Error(`Patrick Core returned HTTP ${result.status}.`);
    }

    const body = result.json as Partial<PatrickResponse>;
    if (typeof body.response !== "string") {
      throw new Error("Patrick Core returned an invalid chat response.");
    }
    return { response: body.response };
  }
}
