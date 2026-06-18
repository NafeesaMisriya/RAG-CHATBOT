import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { ChatMessage } from "../types";

interface CollectionState {
  sessionId: string;
  messages: ChatMessage[];
}

const STORE_KEY = "documind.chats.v1";

function uid(): string {
  return (
    (typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.floor(Math.random() * 1e6)}`) as string
  );
}

function loadStore(): Record<string, CollectionState> {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    return raw ? (JSON.parse(raw) as Record<string, CollectionState>) : {};
  } catch {
    return {};
  }
}

/**
 * Manages per-collection conversations: each document keeps its own
 * session id (so backend memory stays scoped) and message history,
 * persisted to localStorage so reloads don't lose context.
 */
export function useChat(collection: string | null) {
  const [store, setStore] = useState<Record<string, CollectionState>>(loadStore);
  const [isStreaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  // Persist on change.
  useEffect(() => {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(store));
    } catch {
      /* quota / private mode — non-fatal */
    }
  }, [store]);

  // Ensure a state slot exists for the active collection.
  useEffect(() => {
    if (collection && !store[collection]) {
      setStore((s) => ({
        ...s,
        [collection]: { sessionId: uid(), messages: [] },
      }));
    }
  }, [collection, store]);

  const current = collection ? store[collection] : undefined;
  const messages = current?.messages ?? [];

  const patchMessages = useCallback(
    (col: string, updater: (prev: ChatMessage[]) => ChatMessage[]) => {
      setStore((s) => {
        const slot = s[col] ?? { sessionId: uid(), messages: [] };
        return { ...s, [col]: { ...slot, messages: updater(slot.messages) } };
      });
    },
    [],
  );

  const clear = useCallback(() => {
    if (!collection) return;
    // New session id resets backend memory for this document too.
    setStore((s) => ({
      ...s,
      [collection]: { sessionId: uid(), messages: [] },
    }));
  }, [collection]);

  const stop = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const send = useCallback(
    async (question: string) => {
      if (!collection || isStreaming) return;
      const slot = store[collection];
      const sessionId = slot?.sessionId ?? uid();

      const userMsg: ChatMessage = { id: uid(), role: "user", content: question };
      const assistantId = uid();
      const assistantMsg: ChatMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        streaming: true,
      };

      patchMessages(collection, (prev) => [...prev, userMsg, assistantMsg]);
      setStreaming(true);

      const controller = new AbortController();
      abortRef.current = controller;

      const update = (patch: Partial<ChatMessage>) =>
        patchMessages(collection, (prev) =>
          prev.map((m) => (m.id === assistantId ? { ...m, ...patch } : m)),
        );

      try {
        let answer = "";
        for await (const ev of api.streamChat(
          { question, collection_name: collection, session_id: sessionId },
          controller.signal,
        )) {
          if (ev.type === "token") {
            answer += ev.data;
            update({ content: answer });
          } else if (ev.type === "sources") {
            update({ sources: ev.data });
          } else if (ev.type === "images") {
            update({ images: ev.data });
          } else if (ev.type === "error") {
            // Server emitted a clean mid-stream error (e.g. LLM rate
            // limit). Show it on the assistant message; keep any partial
            // answer that streamed before the failure.
            update({
              streaming: false,
              error: true,
              content: answer ? `${answer}\n\n⚠️ ${ev.data}` : `⚠️ ${ev.data}`,
            });
          }
        }
        update({ streaming: false });
      } catch (e) {
        if (controller.signal.aborted) {
          // User stopped the stream — keep whatever streamed so far.
          update({ streaming: false });
        } else {
          update({
            streaming: false,
            error: true,
            content:
              e instanceof Error
                ? `⚠️ ${e.message}`
                : "⚠️ Something went wrong while answering.",
          });
        }
      } finally {
        setStreaming(false);
        abortRef.current = null;
      }
    },
    [collection, isStreaming, store, patchMessages],
  );

  return { messages, isStreaming, send, clear, stop };
}
