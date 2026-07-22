import type { DocumentInfo } from "../types";
import { DocumentList } from "./DocumentList";
import { PlusIcon, SettingsIcon } from "./icons";

interface Props {
  open: boolean;
  documents: DocumentInfo[];
  loading: boolean;
  error: string | null;
  activeCollection: string | null;
  onSelect: (doc: DocumentInfo) => void;
  onDelete: (doc: DocumentInfo) => void;
  onClearConversation: () => void;
  onOpenUpload: () => void;
}

export function Sidebar({
  open,
  documents,
  loading,
  error,
  activeCollection,
  onSelect,
  onDelete,
  onClearConversation,
  onOpenUpload,
}: Props) {
  return (
    <aside className={`sidebar ${open ? "open" : ""}`}>
      <div className="sidebar-header">
        <img className="brand-logo" src="/contexora-mark.png" alt="ConteXora logo" />
        <div className="brand-text">
          <div className="brand-name">
            <span>ConteX</span>ora
          </div>
          <div className="brand-tag">Transforming Context into Intelligence</div>
        </div>
      </div>

      <div className="sidebar-scroll">
        <button className="btn btn-primary" onClick={onOpenUpload} title="Upload a new PDF document">
          <PlusIcon size={16} /> Add Document
        </button>

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
          <PlusIcon size={15} /> New Chat
        </button>
        <button
          className="icon-btn"
          title="Settings"
          aria-label="Settings"
        >
          <SettingsIcon size={18} />
        </button>
      </div>
    </aside>
  );
}
