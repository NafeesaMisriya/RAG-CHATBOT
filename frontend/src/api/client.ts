import type {
  DocumentInfo,
  StreamEvent,
} from "../types";

// Base URL of the backend. Empty string means "use same-origin relative
// paths", which in development are proxied by Vite to the FastAPI server
// (see vite.config.ts). In production set VITE_API_URL to the API origin.
const API_BASE = import.meta.env.VITE_API_URL ?? "";

// When API_BASE is empty we route through the "/api" dev proxy prefix;
// otherwise we hit the configured origin directly.
const apiUrl = (path: string): string =>
  API_BASE ? `${API_BASE}${path}` : `/api${path}`;

/** Resolve a server-relative "/files/..." path to a browser-loadable URL. */
export function resolveFileUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  // Static files are served at /files on the API origin (proxied in dev).
  return API_BASE ? `${API_BASE}${url}` : url;
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  async health(): Promise<boolean> {
    try {
      const res = await fetch(apiUrl("/health"));
      return res.ok;
    } catch {
      return false;
    }
  },

  listDocuments(): Promise<DocumentInfo[]> {
    return fetch(apiUrl("/documents")).then((r) =>
      handle<DocumentInfo[]>(r),
    );
  },

  async uploadDocument(
    file: File,
    onProgress?: (pct: number) => void,
  ): Promise<{ message: string; collection?: string }> {
    // Use XMLHttpRequest so we can report upload progress to the UI.
    return new Promise((resolve, reject) => {
      const form = new FormData();
      form.append("file", file);

      const xhr = new XMLHttpRequest();
      xhr.open("POST", apiUrl("/upload"));

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable && onProgress) {
          onProgress(Math.round((e.loaded / e.total) * 100));
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            resolve(JSON.parse(xhr.responseText));
          } catch {
            reject(new Error("Invalid server response"));
          }
        } else {
          reject(new Error(xhr.responseText || `Upload failed (${xhr.status})`));
        }
      };

      xhr.onerror = () => reject(new Error("Network error during upload"));
      xhr.send(form);
    });
  },

  deleteDocument(collection: string): Promise<{ message: string }> {
    return fetch(apiUrl(`/documents/${encodeURIComponent(collection)}`), {
      method: "DELETE",
    }).then((r) => handle<{ message: string }>(r));
  },

  /**
   * Stream a chat answer over SSE. Yields parsed StreamEvents as they
   * arrive. Pass an AbortSignal to cancel an in-flight stream.
   */
  async *streamChat(
    params: {
      question: string;
      collection_name: string;
      session_id: string;
    },
    signal?: AbortSignal,
  ): AsyncGenerator<StreamEvent> {
    const res = await fetch(apiUrl("/chat/stream"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
      signal,
    });

    if (!res.ok || !res.body) {
      const text = await res.text().catch(() => "");
      throw new Error(text || `Chat request failed (${res.status})`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // SSE frames are separated by a blank line. Process complete frames
      // and keep any trailing partial frame in the buffer.
      const frames = buffer.split("\n\n");
      buffer = frames.pop() ?? "";

      for (const frame of frames) {
        const line = frame.trim();
        if (!line.startsWith("data:")) continue;
        const json = line.slice("data:".length).trim();
        if (!json) continue;
        try {
          yield JSON.parse(json) as StreamEvent;
        } catch {
          // Ignore malformed frames rather than aborting the stream.
        }
      }
    }
  },
};
