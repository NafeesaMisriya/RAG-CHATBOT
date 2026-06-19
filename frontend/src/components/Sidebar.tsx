import type { DocumentInfo } from "../types";
import { DocumentList } from "./DocumentList";
import { UploadPanel } from "./UploadPanel";
import { SunIcon, MoonIcon, PlusIcon } from "./icons";

interface Props {
  open: boolean;
  documents: DocumentInfo[];
  loading: boolean;
  error: string | null;
  activeCollection: string | null;
  theme: "light" | "dark";
  onSelect: (doc: DocumentInfo) => void;
  onDelete: (doc: DocumentInfo) => void;
  onUploaded: () => void;
  onClearConversation: () => void;
  onToggleTheme: () => void;
}

export function Sidebar({
  open,
  documents,
  loading,
  error,
  activeCollection,
  theme,
  onSelect,
  onDelete,
  onUploaded,
  onClearConversation,
  onToggleTheme,
}: Props) {
  return (
    <aside className={`sidebar ${open ? "open" : ""}`}>
      <div className="sidebar-header">
        <img className="brand-logo" src="/contexora-mark.png" alt="ConteXora logo" />
        <div className="brand-text">
          <div className="brand-name">
            <span className="hi">ConteX</span>ora
          </div>
          <div className="brand-tag">Transforming Context into Intelligence</div>
        </div>
      </div>

      <div className="sidebar-scroll">
        <UploadPanel onUploaded={onUploaded} />

        {error && (
          <div className="alert alert-danger">
            <span>{error}</span>
          </div>
        )}

        <DocumentList
          documents={documents}
          loading={loading}
          activeCollection={activeCollection}
          onSelect={onSelect}
          onDelete={onDelete}
        />
      </div>

      <div className="sidebar-footer">
        <button
          className="btn btn-ghost btn-sm"
          onClick={onClearConversation}
          disabled={!activeCollection}
          title="Start a fresh conversation for this document"
        >
          <PlusIcon size={15} /> New chat
        </button>
        <button
          className="icon-btn"
          onClick={onToggleTheme}
          title={theme === "light" ? "Switch to dark" : "Switch to light"}
          aria-label="Toggle theme"
        >
          {theme === "light" ? <MoonIcon size={17} /> : <SunIcon size={17} />}
        </button>
      </div>
    </aside>
  );
}
