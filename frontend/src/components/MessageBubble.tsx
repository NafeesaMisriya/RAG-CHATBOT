import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "../types";
import { Sources } from "./Sources";
import { ImageGallery } from "./ImageGallery";
import { CheckDoubleIcon } from "./icons";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  const showTyping = message.streaming && !message.content;

  // Track the timestamp locally for each bubble when it mounts
  const [timeStr] = useState(() =>
    new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }),
  );

  if (isUser) {
    return (
      <div className="msg user">
        <div className="body">
          <div className="bubble">
            <p style={{ whiteSpace: "pre-wrap" }}>{message.content}</p>
          </div>
          <div className="msg-meta">
            <span>{timeStr}</span>
            <CheckDoubleIcon size={14} className="check-icon" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="msg assistant">
      <div className="avatar">
        <img src="/contexora-mark.png" alt="ConteXora logo" />
      </div>
      <div className="body" style={{ width: "100%" }}>
        <div className="card">
          <div className="msg-header">
            <span className="msg-author">ConteXora</span>
            <span className="msg-meta">{timeStr}</span>
          </div>

          {showTyping ? (
            <div className="typing">
              <span />
              <span />
              <span />
            </div>
          ) : (
            <div className={`prose ${message.error ? "error" : ""}`}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
              {message.streaming && <span className="cursor" />}
            </div>
          )}

          {!message.streaming && (
            <>
              {message.images && message.images.length > 0 && (
                <ImageGallery images={message.images} />
              )}
              {message.sources && message.sources.length > 0 && (
                <Sources sources={message.sources} />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
