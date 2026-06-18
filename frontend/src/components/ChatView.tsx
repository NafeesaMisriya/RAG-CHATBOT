import { useEffect, useRef } from "react";
import type { ChatMessage } from "../types";
import { MessageBubble } from "./MessageBubble";
import { NewConversation } from "./EmptyState";

interface Props {
  documentName: string;
  messages: ChatMessage[];
  onPickSuggestion: (q: string) => void;
}

export function ChatView({ documentName, messages, onPickSuggestion }: Props) {
  const endRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the latest content as it streams, but only when the
  // user is already near the bottom (so reading history isn't disrupted).
  const lastLen = messages.length;
  const lastContent = messages[lastLen - 1]?.content.length ?? 0;
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const nearBottom =
      el.scrollHeight - el.scrollTop - el.clientHeight < 160;
    if (nearBottom) {
      endRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [lastLen, lastContent]);

  if (messages.length === 0) {
    return (
      <div className="chat-scroll center-col" ref={scrollRef}>
        <NewConversation documentName={documentName} onPick={onPickSuggestion} />
      </div>
    );
  }

  return (
    <div className="chat-scroll" ref={scrollRef}>
      <div className="chat-inner">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}
