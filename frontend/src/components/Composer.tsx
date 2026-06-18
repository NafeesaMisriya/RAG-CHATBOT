import { useLayoutEffect, useRef, useState } from "react";
import { SendIcon, StopIcon } from "./icons";

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
            <StopIcon size={18} />
          </button>
        ) : (
          <button
            className="send-btn"
            onClick={submit}
            disabled={disabled || !text.trim()}
            title="Send"
          >
            <SendIcon size={18} />
          </button>
        )}
      </div>
      <div className="composer-hint">
        DocuMind answers from your document. Press Enter to send, Shift+Enter for a new line.
      </div>
    </div>
  );
}
