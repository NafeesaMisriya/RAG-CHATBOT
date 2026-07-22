import { useState } from "react";
import type { Source } from "../types";
import { resolveFileUrl } from "../api/client";
import { BookIcon, ExternalIcon, ChevronIcon } from "./icons";

// Drop title/unit/page header lines that the ingestor prepends to chunk text
function cleanSnippet(text: string | null): string {
  if (!text) return "";
  return text
    .split("\n")
    .filter((line) => {
      const u = line.trim().toUpperCase();
      return !(
        u.startsWith("TITLE:") ||
        u.startsWith("UNIT:") ||
        u.startsWith("PAGE:")
      );
    })
    .join("\n")
    .trim();
}

export function Sources({ sources }: { sources: Source[] }) {
  const [open, setOpen] = useState(false);

  if (!sources.length) return null;

  return (
    <div className="sources">
      <button
        className={`sources-btn ${open ? "open" : ""}`}
        onClick={() => setOpen(!open)}
        title={open ? "Hide sources" : "Show sources"}
      >
        <ChevronIcon size={15} className="arrow-icon" />
        <BookIcon size={15} />
        {sources.length === 1 ? "1 Source" : `${sources.length} Sources`}
      </button>

      {open && (
        <div className="sources-content">
          {sources.map((s, i) => {
            const url = resolveFileUrl(s.source_url);
            const snippet = cleanSnippet(s.content).slice(0, 400);
            return (
              <div className="source-row" key={i}>
                <div className="s-title">{s.title || "Document Source"}</div>
                {url ? (
                  <a className="s-link" href={url} target="_blank" rel="noreferrer">
                    <ExternalIcon size={13} />
                    Open Page {s.page ?? "?"}
                  </a>
                ) : (
                  s.page != null && <div className="muted">Page {s.page}</div>
                )}
                {snippet && <div className="s-snippet">"{snippet}..."</div>}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
