import { useState } from "react";
import Upload from "./components/Upload";
import Summary from "./components/Summary";
import Quiz from "./components/Quiz";
import Flashcards from "./components/Flashcards";
import Revision from "./components/Revision";
import "./App.css";

const TABS = [
  { id: "summary", label: "🧠 Summary" },
  { id: "quiz", label: "🧩 Quiz" },
  { id: "flashcards", label: "🗂 Flashcards" },
  { id: "revision", label: "⚡ Revision" },
] as const;

type TabId = (typeof TABS)[number]["id"];

const FEATURES = [
  { icon: "📄", label: "PDF & DOCX upload" },
  { icon: "🧠", label: "AI-powered summaries" },
  { icon: "🧩", label: "Auto-generated quizzes" },
  { icon: "🗂", label: "Smart flashcards" },
  { icon: "⚡", label: "Structured revision notes" },
  { icon: "🔍", label: "RAG-based retrieval" },
];

export default function App() {
  const [docsLoaded, setDocsLoaded] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>("summary");

  return (
    <div className="app">
      {/* ── HERO SECTION ── */}
      <section className="hero">
        {/* Left — branding */}
        <div className="hero-left">
          <div className="hero-logo-wrap">
            <img
              src="/final_logo.svg"
              alt="WisdomX AI logo"
              className="hero-logo"
            />
          </div>
          <div className="hero-text">
            <h1 className="hero-title">WisdomX AI</h1>
            <p className="hero-tagline">Study smarter, not harder.</p>
            <p className="hero-desc">
              Upload your notes or textbooks and let AI instantly transform them
              into summaries, quizzes, flashcards, and revision guides — powered
              by LLaMA&nbsp;3 and RAG.
            </p>
            <ul className="feature-list" aria-label="Features">
              {FEATURES.map((f) => (
                <li key={f.label} className="feature-item">
                  <span className="feature-icon" aria-hidden="true">
                    {f.icon}
                  </span>
                  {f.label}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Right — upload */}
        <div className="hero-right">
          <div className="upload-card">
            <h2 className="upload-card-title">Get started</h2>
            <p className="upload-card-sub">
              Upload a PDF or DOCX file to unlock all AI features.
            </p>
            <Upload onLoaded={setDocsLoaded} />
          </div>
        </div>
      </section>

      {/* ── TABS (shown after docs are loaded) ── */}
      {docsLoaded ? (
        <main className="app-main">
          <div className="tabs-container">
            <div className="tab-bar" role="tablist">
              {TABS.map((tab) => (
                <button
                  key={tab.id}
                  role="tab"
                  aria-selected={activeTab === tab.id}
                  className={`tab-btn ${activeTab === tab.id ? "active" : ""}`}
                  onClick={() => setActiveTab(tab.id)}>
                  {tab.label}
                </button>
              ))}
            </div>
            <div className="tab-panel">
              {activeTab === "summary" && <Summary />}
              {activeTab === "quiz" && <Quiz />}
              {activeTab === "flashcards" && <Flashcards />}
              {activeTab === "revision" && <Revision />}
            </div>
          </div>
        </main>
      ) : (
        <div className="empty-state">
          <span className="empty-icon">☝️</span>
          <p>Process your files above to unlock all AI features</p>
        </div>
      )}
    </div>
  );
}
