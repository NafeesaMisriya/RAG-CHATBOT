import type { DocumentInfo } from "../types";
import { FileIcon, TrashIcon } from "./icons";

const PAGE_COUNTS: Record<string, string> = {
  "biology_txt": "128 pages",
  "chemistry": "95 pages",
  "english": "76 pages",
  "real_image_test_pdf": "24 pages",
  "biology_genetics_7pages_with_chart_table": "7 pages"
};

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
              style={{ height: 48, marginBottom: 8, borderRadius: 8 }}
            />
          ))}
        </div>
      )}

      {!loading && documents.length === 0 && (
        <p className="muted" style={{ fontSize: "0.85rem", padding: "12px 0" }}>
          No documents yet. Ingest a PDF to get started.
        </p>
      )}

      {!loading && documents.length > 0 && (
        <div className="doc-list">
          {documents.map((doc) => {
            const pageCount = PAGE_COUNTS[doc.collection];
            return (
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
                  <FileIcon size={18} />
                </span>
                <div className="doc-details">
                  <span className="doc-name" title={doc.name}>
                    {doc.name}
                  </span>
                  {pageCount && <span className="doc-pages">{pageCount}</span>}
                </div>
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
            );
          })}
        </div>
      )}
    </div>
  );
}
