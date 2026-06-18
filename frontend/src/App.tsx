import { useEffect, useMemo, useState } from "react";
import { api } from "./api/client";
import { useDocuments } from "./hooks/useDocuments";
import { useChat } from "./hooks/useChat";
import { useTheme } from "./hooks/useTheme";
import type { DocumentInfo } from "./types";
import { Sidebar } from "./components/Sidebar";
import { ChatView } from "./components/ChatView";
import { Composer } from "./components/Composer";
import { NoDocument } from "./components/EmptyState";
import { FileIcon, MenuIcon } from "./components/icons";

export default function App() {
  const { documents, loading, error, refresh } = useDocuments();
  const { theme, toggle } = useTheme();

  const [activeCollection, setActiveCollection] = useState<string | null>(null);
  const [online, setOnline] = useState<boolean | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const chat = useChat(activeCollection);

  const activeDoc = useMemo<DocumentInfo | null>(
    () => documents.find((d) => d.collection === activeCollection) ?? null,
    [documents, activeCollection],
  );

  // Health poll for the connection indicator.
  useEffect(() => {
    let alive = true;
    const check = async () => {
      const ok = await api.health();
      if (alive) setOnline(ok);
    };
    void check();
    const id = setInterval(check, 20000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  // Auto-select the first document once loaded (and keep selection valid
  // after deletions).
  useEffect(() => {
    if (documents.length === 0) {
      setActiveCollection(null);
      return;
    }
    const stillExists = documents.some((d) => d.collection === activeCollection);
    if (!stillExists) {
      setActiveCollection(documents[0].collection);
    }
  }, [documents, activeCollection]);

  const handleSelect = (doc: DocumentInfo) => {
    setActiveCollection(doc.collection);
    setSidebarOpen(false);
  };

  const handleDelete = async (doc: DocumentInfo) => {
    const ok = window.confirm(
      `Delete "${doc.name}"? This removes it from the index and cannot be undone.`,
    );
    if (!ok) return;
    try {
      await api.deleteDocument(doc.collection);
      await refresh();
    } catch (e) {
      window.alert(e instanceof Error ? e.message : "Failed to delete document.");
    }
  };

  return (
    <div className="app">
      {sidebarOpen && (
        <div className="scrim" onClick={() => setSidebarOpen(false)} />
      )}

      <Sidebar
        open={sidebarOpen}
        documents={documents}
        loading={loading}
        error={error}
        activeCollection={activeCollection}
        theme={theme}
        onSelect={handleSelect}
        onDelete={handleDelete}
        onUploaded={refresh}
        onClearConversation={chat.clear}
        onToggleTheme={toggle}
      />

      <main className="main">
        <header className="topbar">
          <button
            className="icon-btn menu-btn"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
          >
            <MenuIcon size={18} />
          </button>

          <div className="doc-title">
            {activeDoc ? (
              <>
                <span className="doc-icon">
                  <FileIcon size={18} />
                </span>
                <span
                  style={{
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {activeDoc.name}
                </span>
              </>
            ) : (
              <span className="muted">No document selected</span>
            )}
          </div>

          <div className="spacer" />

          <div className={`status-dot ${online ? "online" : online === false ? "offline" : ""}`}>
            <span className="dot" />
            {online === null ? "Connecting…" : online ? "Connected" : "Offline"}
          </div>
        </header>

        {!activeDoc ? (
          <NoDocument />
        ) : (
          <>
            <ChatView
              documentName={activeDoc.name}
              messages={chat.messages}
              onPickSuggestion={chat.send}
            />
            <Composer
              disabled={!activeDoc}
              isStreaming={chat.isStreaming}
              onSend={chat.send}
              onStop={chat.stop}
            />
          </>
        )}
      </main>
    </div>
  );
}
