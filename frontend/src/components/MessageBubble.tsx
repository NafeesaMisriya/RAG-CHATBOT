import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "../types";
import { Sources } from "./Sources";
import { ImageGallery } from "./ImageGallery";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  const showTyping = message.streaming && !message.content;

  return (
    <div className={`msg ${message.role}`}>
      <div className="avatar">
        {isUser ? (
          "You"
        ) : (
          <img src="/contexora-mark.png" alt="ConteXora" />
        )}
      </div>
      <div className="body">
        <div className="role">{isUser ? "You" : "ConteXora"}</div>

        {showTyping ? (
          <div className="typing">
            <span />
            <span />
            <span />
          </div>
        ) : (
          <div className={`bubble ${message.error ? "error" : ""}`}>
            {isUser ? (
              <p style={{ whiteSpace: "pre-wrap" }}>{message.content}</p>
            ) : (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            )}
            {message.streaming && <span className="cursor" />}
          </div>
        )}

        {!isUser && !message.streaming && (
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
  );
}
