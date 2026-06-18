// Shared domain types mirroring the FastAPI backend payloads.

export interface DocumentInfo {
  name: string;
  collection: string;
}

export interface Source {
  title: string | null;
  page: number | null;
  content: string | null;
  source_document: string | null;
  source_url: string | null;
}

export interface RetrievedImage {
  page: number | null;
  image_path: string | null;
  image_url: string | null;
  rerank_score: number;
}

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  sources?: Source[];
  images?: RetrievedImage[];
  // Transient flags used while an assistant message streams in.
  streaming?: boolean;
  error?: boolean;
}

// Discriminated union of server-sent events emitted by /chat/stream.
export type StreamEvent =
  | { type: "token"; data: string }
  | { type: "sources"; data: Source[] }
  | { type: "images"; data: RetrievedImage[] }
  | { type: "error"; data: string }
  | { type: "done" };
