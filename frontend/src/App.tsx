import { useEffect, useRef, useState } from "react";
import "./App.css";
import {
  deleteDocument,
  getDocuments,
  uploadDocument,
  type Document,
} from "./services/api";

function DocumentIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M6 3.75h7.25L18 8.5v11.75H6V3.75Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path
        d="M13 3.75V9h5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ConversationIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M5 5.5h14v10H9l-4 3v-13Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function SettingsIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M9.7 4.8 10.5 3h3l.8 1.8 1.8.9 1.9-.5 2.1 2.1-.5 1.9.9 1.8 1.8.8v3l-1.8.8-.9 1.8.5 1.9-2.1 2.1-1.9-.5-1.8.9-.8 1.8h-3l-.8-1.8-1.8-.9-1.9.5-2.1-2.1.5-1.9-.9-1.8-1.8-.8v-3l1.8-.8.9-1.8-.5-1.9 2.1-2.1 1.9.5 1.8-.9Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <circle
        cx="12"
        cy="12"
        r="3"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      />
    </svg>
  );
}



function UploadIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 15V4m0 0L8 8m4-4 4 4M5 14.5v4h14v-4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M5 7h14M10 11v6m4-6v6M9 7l.7-2h4.6l.7 2m-9 0 .8 13h10.4l.8-13"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    async function loadDocuments() {
      try {
        setError(null);
        const data = await getDocuments();
        setDocuments(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load documents.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadDocuments();
  }, []);

  async function handleFileUpload(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (file.type !== "application/pdf") {
      setError("Only PDF files can be uploaded.");
      event.target.value = "";
      return;
    }

    try {
      setUploading(true);
      setError(null);

      const document = await uploadDocument(file);

      setDocuments((current) => {
  const exists = current.some(
    (item) => item.document_id === document.document_id,
  );

  if (exists) {
    return current.map((item) =>
      item.document_id === document.document_id ? document : item,
    );
  }

  return [...current, document];
});
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to upload the document.",
      );
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function handleDelete(documentId: string) {
    const document = documents.find(
      (item) => item.document_id === documentId,
    );

    if (!document) {
      return;
    }

    const confirmed = window.confirm(
      `Delete "${document.filename}"? This will remove the document and its indexed evidence.`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(documentId);
      setError(null);

      await deleteDocument(documentId);

      setDocuments((current) =>
        current.filter((item) => item.document_id !== documentId),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to delete the document.",
      );
    } finally {
      setDeletingId(null);
    }
  }

  function openFilePicker() {
    fileInputRef.current?.click();
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">E</div>
          <span>EvidenceAI</span>
        </div>

        <nav className="sidebar-nav" aria-label="Main navigation">
          <button className="nav-item active" type="button">
            <DocumentIcon />
            <span>Documents</span>
          </button>

          <button className="nav-item" type="button">
            <ConversationIcon />
            <span>Conversations</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <button className="nav-item" type="button">
            <SettingsIcon />
            <span>Settings</span>
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>Documents</h1>
            <p>
              Manage the documents EvidenceAI uses to answer your questions.
            </p>
          </div>

          <button className="icon-button" type="button" aria-label="Settings">
            <SettingsIcon />
          </button>
        </header>

        <section className="documents-workspace">
          <div className="documents-header">
            <div>
              <h2>Your Documents</h2>
              <p>
                {documents.length === 0
                  ? "No documents uploaded yet."
                  : `${documents.length} ${
                      documents.length === 1 ? "document" : "documents"
                    } available`}
              </p>
            </div>

            <button
              className="upload-button"
              type="button"
              onClick={openFilePicker}
              disabled={uploading}
            >
              <UploadIcon />
              {uploading ? "Uploading..." : "Upload PDF"}
            </button>

            <input
              ref={fileInputRef}
              className="hidden-file-input"
              type="file"
              accept="application/pdf,.pdf"
              onChange={handleFileUpload}
            />
          </div>

          {error && (
            <div className="error-banner" role="alert">
              <span>{error}</span>

              <button
                type="button"
                onClick={() => setError(null)}
                aria-label="Dismiss error"
              >
                ×
              </button>
            </div>
          )}

          {loading ? (
            <div className="documents-state">
              <div className="loading-spinner" />
              <p>Loading documents...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="documents-state empty-state">
              <div className="empty-icon">
                <DocumentIcon />
              </div>

              <h3>No documents yet</h3>

              <p>
                Upload a PDF to start asking questions and retrieving
                evidence.
              </p>

              <button
                className="secondary-upload-button"
                type="button"
                onClick={openFilePicker}
                disabled={uploading}
              >
                <UploadIcon />
                Upload your first PDF
              </button>
            </div>
          ) : (
            <div className="document-list">
              {documents.map((document) => (
                <article className="document-card" key={document.document_id}>
                  <div className="document-icon">
                    <DocumentIcon />
                  </div>

                  <div className="document-info">
                    <h3 title={document.filename}>{document.filename}</h3>

                    <div className="document-meta">
                      <span>{document.pages} pages</span>
                      <span className="meta-dot">•</span>
                      <span>{document.chunks} chunks</span>
                    </div>
                  </div>

                  <button
                    className="delete-button"
                    type="button"
                    onClick={() => handleDelete(document.document_id)}
                    disabled={deletingId === document.document_id}
                    aria-label={`Delete ${document.filename}`}
                    title="Delete document"
                  >
                    <TrashIcon />
                  </button>
                </article>
              ))}
            </div>
          )}
        </section>

        <div className="question-bar">
          <input
            type="text"
            placeholder="Ask a question about your documents..."
            aria-label="Ask a question"
          />

          <button className="send-button" type="button" aria-label="Send question">
            ↑
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;