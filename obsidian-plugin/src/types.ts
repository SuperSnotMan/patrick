export type PatrickAction = "ask" | "explain" | "summarise" | "quiz" | "improve_writing";

export interface PatrickNoteContext {
  title: string;
  path: string;
  content: string;
  /** One-based line number. Zero means no editor cursor is available. */
  cursor_line: number;
  selection: string;
}

export interface PatrickContext {
  vault: string;
  note: PatrickNoteContext;
}

export interface PatrickRequest {
  message: string;
  action: PatrickAction;
  context: PatrickContext;
}

export interface PatrickResponse {
  response: string;
}
