import {
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
} from "react";
import {
  askQuestion,
  deleteDocument,
  getDocuments,
  uploadDocument,
  type AskResponse,
  type Document,
} from "./services/api";
import "./App.css";

function DocumentIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M6 3.5h8l4 4V20.5H6z" />
      <path d="M14 3.5v4h4M9 12h6M9 16h6" />
    </svg>
  );
}

function ConversationIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M5 5.5h14v10H9l-4 3v-13z" />
      <path d="M8 9.5h8M8 12.5h5" />
    </svg>
  );
}

function SettingsIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7z" />
      <path d="M19 13.5v-3l-2-.6a5.7 5.7 0 0 0-.7-1.6l.9-1.9-2.1-2.1-1.9.9a5.7 5.7 0 0 0-1.6-.7L11 2.5H9l-.6 2a5.7 5.7 0 0 0-1.6.7l-1.9-.9-2.1 2.1.9 1.9a5.7 5.7 0 0 0-.7 1.6l-2 .6v3l2 .6c.2.6.4 1.1.7 1.6l-.9 1.9 2.1 2.1 1.9-.9c.5.3 1 .5 1.6.7l.6 2h3l.6-2c.6-.2 1.1-.4 1.6-.7l1.9.9 2.1-2.1-.9-1.9c.3-.5.5-1 .7-1.6z" />
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 16V5" />
      <path d="m8 9 4-4 4 4" />
      <path d="M5 15v4h14v-4" />
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M5 7h14M10 11v6M14 11v6M9 7V4h6v3M7 7l1 14h8l1-14" />
    </svg>
  );
}

function cleanText(text: string) {
  return text
    .replace(/<EOS>/gi, "")
    .replace(/<pad>/gi, "")
    .replace(/\s+/g, " ")
    .trim();
}

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<
    {
      id: string;
      role: "user" | "assistant";
      content: string;
      response?: AskResponse;
    }[]
  >([]);
  const [conversationId, setConversationId] = useState<
    string | undefined
  >();
  const [asking, setAsking] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    async function loadDocuments() {
      try {
        setLoading(true);
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

    void loadDocuments();
  }, []);

  async function handleUpload(file: File) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.");
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
            item.document_id === document.document_id
              ? document
              : item,
          );
        }

        return [...current, document];
      });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to upload document.",
      );
    } finally {
      setUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (file) {
      void handleUpload(file);
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
        current.filter(
          (item) => item.document_id !== documentId,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to delete document.",
      );
    } finally {
      setDeletingId(null);
    }
  }

  async function handleAskQuestion() {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || asking) {
      return;
    }

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user" as const,
      content: trimmedQuestion,
    };

    setMessages((current) => [...current, userMessage]);
    setQuestion("");
    setAsking(true);
    setError(null);

    try {
      const response = await askQuestion(
        trimmedQuestion,
        conversationId,
      );

      setConversationId(response.conversation_id);

      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: cleanText(response.answer),
          response,
        },
      ]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to get an answer.",
      );
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">E</div>

          <div>
            <div className="brand-name">EvidenceAI</div>
            <div className="brand-subtitle">
              Document Intelligence
            </div>
          </div>
        </div>

        <nav
          className="sidebar-nav"
          aria-label="Main navigation"
        >
          <button
            className="nav-item active"
            type="button"
          >
            <DocumentIcon />
            <span>Documents</span>
          </button>

          <button
            className="nav-item"
            type="button"
          >
            <ConversationIcon />
            <span>Conversations</span>
          </button>

          <button
            className="nav-item"
            type="button"
          >
            <SettingsIcon />
            <span>Settings</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot" />
          <span>Local AI system</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>Documents</h1>
            <p>
              Ask questions and get answers backed by
              evidence.
            </p>
          </div>

          <div className="topbar-actions">
            <input
              ref={fileInputRef}
              className="hidden-file-input"
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
            />

            <button
              className="upload-button"
              type="button"
              onClick={() =>
                fileInputRef.current?.click()
              }
              disabled={uploading}
            >
              <UploadIcon />
              <span>
                {uploading
                  ? "Uploading..."
                  : "Upload PDF"}
              </span>
            </button>
          </div>
        </header>

        {error && (
          <div
            className="error-banner"
            role="alert"
          >
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

        {messages.length > 0 && (
          <section
            className="chat-workspace"
            aria-label="Conversation"
          >
            {messages.map((message) => (
              <article
                className={`chat-message ${message.role}`}
                key={message.id}
              >
                <div className="message-label">
                  {message.role === "user"
                    ? "You"
                    : "EvidenceAI"}
                </div>

                <div className="message-content">
                  {message.role === "assistant"
                    ? message.content
                        .split(/(\[\d+\])/g)
                        .map((part, index) =>
                          /^\[\d+\]$/.test(part) ? (
                            <span
                              className="citation-badge"
                              key={index}
                            >
                              {part}
                            </span>
                          ) : (
                            <span key={index}>
                              {part}
                            </span>
                          ),
                        )
                    : message.content}
                </div>

                {message.role === "assistant" &&
                  message.response &&
                  message.response.sources.length >
                    0 && (
                    <div className="evidence-preview">
                      <div className="evidence-title">
                        <span>Evidence</span>

                        <span className="evidence-count">
                          {
                            message.response.sources
                              .length
                          }{" "}
                          sources
                        </span>
                      </div>

                      {message.response.sources.map(
                        (source, index) => (
                          <details
                            className="evidence-item"
                            key={source.chunk_id}
                          >
                            <summary>
                              <div className="evidence-summary">
                                <span className="evidence-number">
                                  [{index + 1}]
                                </span>

                                <span
                                  className="evidence-source"
                                  title={
                                    source.document
                                  }
                                >
                                  {source.document}
                                </span>

                                <span className="evidence-page">
                                  Page {source.page}
                                </span>
                              </div>

                              <span className="evidence-chevron">
                                ›
                              </span>
                            </summary>

                            <div className="evidence-quote">
                              {cleanText(source.text)}
                            </div>
                          </details>
                        ),
                      )}
                    </div>
                  )}
              </article>
            ))}

            {asking && (
              <article className="chat-message assistant">
                <div className="message-label">
                  EvidenceAI
                </div>

                <div className="message-content thinking-indicator">
                  <span />
                  <span />
                  <span />
                </div>
              </article>
            )}
          </section>
        )}

        <section className="documents-section">
          <div className="section-heading">
            <div>
              <h2>Your Documents</h2>

              <p>
                {documents.length === 0
                  ? "Upload a PDF to start asking questions."
                  : `${documents.length} ${
                      documents.length === 1
                        ? "document"
                        : "documents"
                    } available`}
              </p>
            </div>
          </div>

          {loading ? (
            <div className="empty-state">
              <div className="loading-spinner" />
              <p>Loading documents...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">
                <DocumentIcon />
              </div>

              <h3>No documents yet</h3>

              <p>
                Upload a PDF and EvidenceAI will index it
                for evidence-based questions.
              </p>

              <button
                className="empty-upload-button"
                type="button"
                onClick={() =>
                  fileInputRef.current?.click()
                }
                disabled={uploading}
              >
                <UploadIcon />
                Upload your first PDF
              </button>
            </div>
          ) : (
            <div className="document-grid">
              {documents.map((document) => (
                <article
                  className="document-card"
                  key={document.document_id}
                >
                  <div className="document-card-top">
                    <div className="document-icon">
                      <DocumentIcon />
                    </div>

                    <button
                      className="delete-button"
                      type="button"
                      onClick={() =>
                        void handleDelete(
                          document.document_id,
                        )
                      }
                      disabled={
                        deletingId ===
                        document.document_id
                      }
                      aria-label={`Delete ${document.filename}`}
                      title="Delete document"
                    >
                      <TrashIcon />
                    </button>
                  </div>

                  <div
                    className="document-name"
                    title={document.filename}
                  >
                    {document.filename}
                  </div>

                  <div className="document-meta">
                    <span>
                      {document.pages} pages
                    </span>

                    <span className="meta-dot">
                      •
                    </span>

                    <span>
                      {document.chunks} chunks
                    </span>
                  </div>

                  <div className="document-id">
                    ID: {document.document_id}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <div className="question-bar">
          <input
            type="text"
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();
                void handleAskQuestion();
              }
            }}
            placeholder="Ask a question about your documents..."
            aria-label="Ask a question"
            disabled={asking}
          />

          <button
            className="send-button"
            type="button"
            onClick={() =>
              void handleAskQuestion()
            }
            disabled={
              !question.trim() || asking
            }
            aria-label="Send question"
          >
            {asking ? "…" : "↑"}
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;