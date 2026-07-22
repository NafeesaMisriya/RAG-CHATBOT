import { useLayoutEffect, useRef, useState } from "react";
import { SendIcon, StopIcon, PaperclipIcon } from "./icons";

interface Props {
  disabled: boolean;
  isStreaming: boolean;
  onSend: (text: string) => void;
  onStop: () => void;
}

export function Composer({ disabled, isStreaming, onSend, onStop }: Props) {
  const [text, setText] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  // Auto-grow the textarea up to the CSS max-height.
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, [text]);

  const submit = () => {
    const value = text.trim();
    if (!value || disabled || isStreaming) return;
    onSend(value);
    setText("");
  };

  return (
    <div className="composer-wrap">
      <div className="composer">
        <button
          className="icon-btn"
          disabled={disabled}
          title="Add attachment (mock)"
          aria-label="Add attachment"
          style={{ marginBottom: 2 }}
        >
          <PaperclipIcon size={18} />
        </button>

        <textarea
          ref={ref}
          rows={1}
          value={text}
          placeholder="Ask anything about this document…"
          disabled={disabled}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        />

        {isStreaming ? (
          <button className="send-btn" onClick={onStop} title="Stop generating">
            <StopIcon size={16} />
          </button>
        ) : (
          <button
            className="send-btn"
            onClick={submit}
            disabled={disabled || !text.trim()}
            title="Send message"
          >
            <SendIcon size={16} />
          </button>
        )}
      </div>
      <div className="composer-hint">
        Enter to send, Shift+Enter for newline
      </div>
    </div>
  );
}
