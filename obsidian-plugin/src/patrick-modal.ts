import { App, Component, MarkdownRenderer, Modal, Setting } from "obsidian";
import type { PatrickApi } from "./patrick-api";
import type { PatrickAction, PatrickContext } from "./types";

type ContextProvider = () => Promise<PatrickContext>;

export class PatrickModal extends Modal {
  private readonly renderer = new Component();
  private input!: HTMLTextAreaElement;
  private response!: HTMLElement;
  private error!: HTMLElement;
  private submitButton!: HTMLButtonElement;

  constructor(
    app: App,
    private readonly api: PatrickApi,
    private readonly getContext: ContextProvider,
    private readonly initialMessage = "",
    private readonly action: PatrickAction = "ask"
  ) {
    super(app);
  }

  onOpen(): void {
    this.renderer.load();
    this.modalEl.addClass("patrick-modal");
    this.contentEl.createEl("h2", { text: "Ask Patrick" });
    this.input = this.contentEl.createEl("textarea", {
      cls: "patrick-question",
      attr: { placeholder: "Ask anything…", rows: "2", "aria-label": "Question for Patrick" }
    });
    this.input.value = this.initialMessage;
    this.input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        void this.submit();
      }
    });

    new Setting(this.contentEl)
      .addButton((button) => {
        this.submitButton = button.setButtonText("Ask").setCta().buttonEl;
        this.submitButton.addEventListener("click", () => void this.submit());
      });

    this.error = this.contentEl.createDiv({ cls: "patrick-error" });
    this.response = this.contentEl.createDiv({ cls: "patrick-response" });
    this.input.focus();
    if (this.initialMessage) void this.submit();
  }

  onClose(): void {
    this.renderer.unload();
    this.contentEl.empty();
  }

  private async submit(): Promise<void> {
    const message = this.input.value.trim();
    if (!message || this.submitButton.disabled) return;

    this.error.empty();
    this.submitButton.disabled = true;
    this.submitButton.setText("Thinking…");
    try {
      // Build context immediately before the request so edits made while the
      // modal is open are included in the conversation.
      const context = await this.getContext();
      const result = await this.api.chat({ message, action: this.action, context });
      this.response.empty();
      await MarkdownRenderer.render(this.app, result.response, this.response, context.note.path, this.renderer);
      const copy = this.response.createEl("button", { text: "Copy response", cls: "patrick-copy" });
      copy.addEventListener("click", () => void navigator.clipboard.writeText(result.response));
    } catch (error) {
      this.error.setText(error instanceof Error ? error.message : "Could not contact Patrick Core.");
    } finally {
      this.submitButton.disabled = false;
      this.submitButton.setText("Ask");
    }
  }
}
