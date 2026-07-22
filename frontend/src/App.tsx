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
import { UploadPanel } from "./components/UploadPanel";
import { FileIcon, MenuIcon, SunIcon, MoonIcon, UserIcon, CloseIcon } from "./components/icons";
import { LandingPage } from "./components/LandingPage";

export default function App() {
  const { documents, loading, error, refresh } = useDocuments();
  const { theme, toggle } = useTheme();

  const [activeCollection, setActiveCollection] = useState<string | null>(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  // Lightweight router state tracking
  const [path, setPath] = useState(() => window.location.pathname);

  useEffect(() => {
    const handlePopState = () => {
      setPath(window.location.pathname);
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const navigate = (newPath: string) => {
    window.history.pushState({}, "", newPath);
    setPath(newPath);
  };

  const chat = useChat(activeCollection);

  const activeDoc = useMemo<DocumentInfo | null>(
    () => documents.find((d) => d.collection === activeCollection) ?? null,
    [documents, activeCollection],
  );

  // Auto-select the first document once loaded
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

  if (path === "/" || path === "") {
    return <LandingPage onExplore={() => navigate("/chat")} />;
  }

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
        onSelect={handleSelect}
        onDelete={handleDelete}
        onClearConversation={chat.clear}
        onOpenUpload={() => setUploadModalOpen(true)}
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

          {activeDoc ? (
            <div className="active-doc-title">
              <span className="doc-icon">
                <FileIcon size={18} />
              </span>
              <span className="doc-select-title">{activeDoc.name}</span>
            </div>
          ) : (
            <div className="active-doc-title">
              <span className="muted">No document selected</span>
            </div>
          )}

          <div className="topbar-actions">
            <button
              className="icon-btn"
              onClick={toggle}
              title={theme === "light" ? "Switch to dark theme" : "Switch to light theme"}
              aria-label="Toggle theme"
            >
              {theme === "light" ? <MoonIcon size={18} /> : <SunIcon size={18} />}
            </button>
            <button className="icon-btn" title="Settings & Profile" aria-label="Profile">
              <UserIcon size={18} />
            </button>
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

      {uploadModalOpen && (
        <div className="modal-overlay" onClick={() => setUploadModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <span className="modal-title">Upload Document</span>
              <button
                className="modal-close"
                onClick={() => setUploadModalOpen(false)}
                aria-label="Close upload modal"
              >
                <CloseIcon size={18} />
              </button>
            </div>
            <UploadPanel
              onUploaded={() => {
                setUploadModalOpen(false);
                void refresh();
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
