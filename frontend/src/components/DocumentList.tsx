import type { DocumentInfo } from "../types";
import { FileIcon, TrashIcon } from "./icons";

interface Props {
  documents: DocumentInfo[];
  loading: boolean;
  activeCollection: string | null;
  onSelect: (doc: DocumentInfo) => void;
  onDelete: (doc: DocumentInfo) => void;
}

export function DocumentList({
  documents,
  loading,
  activeCollection,
  onSelect,
  onDelete,
}: Props) {
  return (
    <div>
      <h3 className="section-label">
        <span>Library</span>
        {!loading && <span className="count-pill">{documents.length}</span>}
      </h3>

      {loading && (
        <div className="doc-list">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="skeleton"
              style={{ height: 38, marginBottom: 4 }}
            />
          ))}
        </div>
      )}

      {!loading && documents.length === 0 && (
        <p className="muted">No documents yet. Upload a PDF to get started.</p>
      )}

      {!loading && documents.length > 0 && (
        <div className="doc-list">
          {documents.map((doc) => (
            <div
              key={doc.collection}
              className={`doc-item ${
                doc.collection === activeCollection ? "active" : ""
              }`}
              role="button"
              tabIndex={0}
              onClick={() => onSelect(doc)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") onSelect(doc);
              }}
            >
              <span className="doc-icon">
                <FileIcon size={17} />
              </span>
              <span className="doc-name" title={doc.name}>
                {doc.name}
              </span>
              <button
                className="doc-del"
                title="Delete document"
                aria-label={`Delete ${doc.name}`}
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(doc);
                }}
              >
                <TrashIcon size={15} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
