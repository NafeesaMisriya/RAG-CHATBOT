import { useRef, useState } from "react";
import { api } from "../api/client";
import { UploadIcon, FileIcon, CheckIcon, AlertIcon } from "./icons";

interface Props {
  onUploaded: () => void;
}

type Status =
  | { kind: "idle" }
  | { kind: "uploading"; pct: number }
  | { kind: "success"; msg: string }
  | { kind: "exists" }
  | { kind: "error"; msg: string };

export function UploadPanel({ onUploaded }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const [drag, setDrag] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const pick = (f: File | null) => {
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".pdf")) {
      setStatus({ kind: "error", msg: "Only PDF files are supported." });
      return;
    }
    setFile(f);
    setStatus({ kind: "idle" });
  };

  const ingest = async () => {
    if (!file) return;
    setStatus({ kind: "uploading", pct: 0 });
    try {
      const res = await api.uploadDocument(file, (pct) =>
        setStatus({ kind: "uploading", pct }),
      );
      if (res.message === "Document already exists.") {
        setStatus({ kind: "exists" });
      } else {
        setStatus({ kind: "success", msg: "Document indexed successfully." });
        setFile(null);
        onUploaded();
      }
    } catch (e) {
      setStatus({
        kind: "error",
        msg: e instanceof Error ? e.message : "Upload failed.",
      });
    }
  };

  const uploading = status.kind === "uploading";

  return (
    <div>
      <h3 className="section-label">Add document</h3>

      {!file && (
        <div
          className={`dropzone ${drag ? "drag" : ""}`}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDrag(true);
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDrag(false);
            pick(e.dataTransfer.files[0] ?? null);
          }}
        >
          <div className="dz-icon">
            <UploadIcon size={24} />
          </div>
          <div className="dz-title">Drop a PDF or click to browse</div>
          <div className="dz-hint">Max one file at a time</div>
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf,.pdf"
            hidden
            onChange={(e) => pick(e.target.files?.[0] ?? null)}
          />
        </div>
      )}

      {file && (
        <div className="upload-card">
          <div className="upload-file">
            <FileIcon size={16} />
            <span className="name">{file.name}</span>
            <span className="muted">{(file.size / 1024 / 1024).toFixed(1)} MB</span>
          </div>

          {uploading && (
            <div className="progress">
              <span style={{ width: `${(status as { pct: number }).pct}%` }} />
            </div>
          )}

          <div style={{ display: "flex", gap: 8 }}>
            <button
              className="btn btn-primary btn-sm btn-block"
              onClick={ingest}
              disabled={uploading}
            >
              {uploading ? "Indexing…" : "Ingest document"}
            </button>
            {!uploading && (
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => {
                  setFile(null);
                  setStatus({ kind: "idle" });
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      )}

      {status.kind === "success" && (
        <div className="alert alert-success" style={{ marginTop: 10 }}>
          <CheckIcon size={15} />
          <span>{status.msg}</span>
        </div>
      )}
      {status.kind === "exists" && (
        <div className="alert alert-warning" style={{ marginTop: 10 }}>
          <AlertIcon size={15} />
          <span>This document is already indexed.</span>
        </div>
      )}
      {status.kind === "error" && (
        <div className="alert alert-danger" style={{ marginTop: 10 }}>
          <AlertIcon size={15} />
          <span>{status.msg}</span>
        </div>
      )}
    </div>
  );
}
