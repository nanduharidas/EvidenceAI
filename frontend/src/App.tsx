import "./App.css";

function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">E</div>
          <span>EvidenceAI</span>
        </div>

        <nav className="sidebar-nav">
          <button className="nav-item active">
            <span>▣</span>
            Documents
          </button>

          <button className="nav-item">
            <span>◷</span>
            Conversations
          </button>
        </nav>

        <div className="sidebar-bottom">
          <button className="nav-item">
            <span>⚙</span>
            Settings
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>Document Q&A</h1>
            <p>Ask questions and get answers grounded in your documents.</p>
          </div>

          <button className="icon-button" aria-label="Settings">
            ⚙
          </button>
        </header>

        <section className="workspace">
          <div className="welcome">
            <div className="welcome-icon">✦</div>

            <h2>Welcome to EvidenceAI</h2>

            <p>
              Upload a PDF and ask questions about its contents.
              EvidenceAI will retrieve relevant evidence and cite its sources.
            </p>

            <button className="upload-button">
              <span>＋</span>
              Upload PDF
            </button>
          </div>
        </section>

        <div className="question-bar">
          <input
            type="text"
            placeholder="Ask a question about your documents..."
            aria-label="Ask a question"
          />

          <button className="send-button" aria-label="Send question">
            ↑
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;