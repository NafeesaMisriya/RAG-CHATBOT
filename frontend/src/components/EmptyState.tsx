import { BookIcon, SparkIcon, UploadIcon } from "./icons";

const SUGGESTIONS = [
  "Summarize this document",
  "What are the key topics covered?",
  "Explain the main concept in simple terms",
  "List the most important points",
];

export function NoDocument() {
  return (
    <div className="empty">
      <div className="empty-icon">
        <UploadIcon size={32} />
      </div>
      <h2>Welcome to DocuMind</h2>
      <p>
        Upload a PDF from the sidebar to build a searchable knowledge base, then
        ask questions and get grounded, cited answers.
      </p>
    </div>
  );
}

export function NewConversation({
  documentName,
  onPick,
}: {
  documentName: string;
  onPick: (q: string) => void;
}) {
  return (
    <div className="empty">
      <div className="empty-icon">
        <BookIcon size={32} />
      </div>
      <h2>Chat with {documentName}</h2>
      <p>
        Ask a question and DocuMind will retrieve the most relevant passages,
        figures, and pages to answer — with sources you can verify.
      </p>
      <div className="suggestions">
        {SUGGESTIONS.map((s) => (
          <button key={s} className="suggestion" onClick={() => onPick(s)}>
            <SparkIcon size={14} style={{ marginRight: 6, verticalAlign: "-2px" }} />
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
