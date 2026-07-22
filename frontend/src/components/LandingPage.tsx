import type { SVGProps } from "react";
import "./LandingPage.css";

type IconP = SVGProps<SVGSVGElement> & { size?: number };

const LogoMark = ({ size = 32 }: { size?: number }) => (
  <img className="landing-logo-img" src="/contexora-mark.png" alt="Contexora Logo" style={{ width: size, height: size }} />
);

// High-fidelity SVG icons matching the mockup symbols
const UserIcon = ({ size = 18 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

const SparkIcon = ({ size = 18 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1" />
    <circle cx="12" cy="12" r="3.2" />
  </svg>
);

const FileIcon = ({ size = 20 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
    <line x1="10" y1="9" x2="8" y2="9" />
  </svg>
);

const ImageIcon = ({ size = 20 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    <circle cx="9" cy="9" r="2" />
    <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
  </svg>
);

const TableIcon = ({ size = 20 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2" />
    <line x1="3" y1="9" x2="21" y2="9" />
    <line x1="3" y1="15" x2="21" y2="15" />
    <line x1="9" y1="3" x2="9" y2="21" />
    <line x1="15" y1="3" x2="15" y2="21" />
  </svg>
);

const BrainIcon = ({ size = 20 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1 0-3.12 3 3 0 0 1 0-4.88 2.5 2.5 0 0 1 0-3.12A2.5 2.5 0 0 1 9.5 2z" />
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 0-3.12 3 3 0 0 0 0-4.88 2.5 2.5 0 0 0 0-3.12A2.5 2.5 0 0 0 14.5 2z" />
  </svg>
);

const ChatBubbleIcon = ({ size = 24 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    <circle cx="8" cy="10" r="1" fill="currentColor" />
    <circle cx="12" cy="10" r="1" fill="currentColor" />
    <circle cx="16" cy="10" r="1" fill="currentColor" />
  </svg>
);

const LightbulbIcon = ({ size = 24 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A5 5 0 0 0 8 8c0 1 .4 2.5 1.5 3.5.7.8 1.3 1.5 1.5 2.5" />
    <line x1="9" y1="18" x2="15" y2="18" />
    <line x1="10" y1="22" x2="14" y2="22" />
  </svg>
);

const BarChartIcon = ({ size = 24 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10" />
    <line x1="12" y1="20" x2="12" y2="4" />
    <line x1="6" y1="20" x2="6" y2="14" />
  </svg>
);

const ArrowRightIcon = ({ size = 16 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12" />
    <polyline points="12 5 19 12 12 19" />
  </svg>
);

interface Props {
  onExplore: () => void;
}

export function LandingPage({ onExplore }: Props) {
  return (
    <div className="landing-container">
      {/* ================= HEADER ================= */}
      <header className="landing-header">
        <div className="landing-brand">
          <LogoMark size={36} />
          <div className="landing-brand-text">
            <h1 className="landing-brand-name">Contexora</h1>
            <p className="landing-brand-tagline">Transforming Context into Intelligence</p>
          </div>
        </div>

        <nav className="landing-nav">
          <a href="#" className="landing-nav-link active">Home</a>
          <a href="#" className="landing-nav-link">Pricing</a>
          <a href="#" className="landing-nav-link">About Us</a>
          <a href="#" className="landing-nav-link">Contact Us</a>
        </nav>

        <div className="header-right-group">
          <div className="header-divider" />
          <button className="landing-signin-btn" title="Sign In">
            <UserIcon size={18} />
            <span>Sign In</span>
          </button>
        </div>
      </header>

      {/* ================= HERO SECTION ================= */}
      <main className="landing-hero">
        {/* Left Column: Headlines & CTA */}
        <div className="landing-hero-left">
          <h2 className="landing-headline">
            Intelligent Document <br />
            <span className="gold-text">Understanding</span>
          </h2>
          <div className="landing-headline-underline" />
          <p className="landing-subtitle">
            AI-powered Retrieval-Augmented Generation platform for understanding documents with accurate, grounded responses.
          </p>
          <button className="landing-cta-btn" onClick={onExplore} title="Explore Contexora">
            <SparkIcon size={18} />
            <span>Explore Contexora</span>
            <ArrowRightIcon size={16} />
          </button>
        </div>

        {/* Right Column: Schema and Circuit Node Connections */}
        <div className="landing-hero-right">
          {/* Circuit background container with SVG circuit lines */}
          <div className="circuit-board-bg" />

          {/* Central Logo Panel representing the AI circle shield */}
          <div className="landing-hero-logo-panel">
            <div className="inner-shield">
              <img className="landing-large-logo" src="/contexora-mark.png" alt="Contexora Logo Mark" />
            </div>
            
            {/* Golden terminals extending to the right side of the circle */}
            <div className="gold-terminals">
              <div className="terminal-line t-top">
                <span className="terminal-dot" />
              </div>
              <div className="terminal-line t-mid">
                <span className="terminal-dot" />
              </div>
              <div className="terminal-line t-bot">
                <span className="terminal-dot" />
              </div>
            </div>
          </div>

          {/* Connected Feature Nodes */}
          <div className="feature-node documents">
            <div className="feature-card">
              <FileIcon size={20} />
              <span>Documents</span>
            </div>
            <div className="connector-line line-documents" />
          </div>

          <div className="feature-node images">
            <div className="feature-card">
              <ImageIcon size={20} />
              <span>Images</span>
            </div>
            <div className="connector-line line-images" />
          </div>

          <div className="feature-node tables">
            <div className="feature-card">
              <TableIcon size={20} />
              <span>Tables</span>
            </div>
            <div className="connector-line line-tables" />
          </div>

          <div className="feature-node knowledge">
            <div className="feature-card">
              <BrainIcon size={20} />
              <span>Knowledge</span>
            </div>
            <div className="connector-line line-knowledge" />
          </div>
        </div>
      </main>

      {/* ================= FOOTER ================= */}
      <footer className="landing-footer">
        {/* SVG Curved border wave with gold trim overlay */}
        <div className="footer-wave-container">
          <svg viewBox="0 0 1440 60" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
            <path d="M0,30 C360,10 720,50 1440,30 L1440,60 L0,60 Z" fill="#08192e" />
            <path d="M0,30 C360,10 720,50 1440,30" stroke="#c99a2e" strokeWidth="2.5" />
          </svg>
        </div>

        <div className="landing-footer-content">
          {/* Quote Section */}
          <div className="landing-footer-left">
            <span className="quote-mark">“</span>
            <p className="landing-footer-tagline">
              From documents to understanding,<br />
              from context to intelligence.
            </p>
            <span className="quote-mark">”</span>
          </div>

          {/* Step Cards Section */}
          <div className="landing-footer-right">
            <div className="footer-step">
              <FileIcon size={24} className="step-icon" />
              <div className="step-meta">
                <h4 className="step-title">Upload</h4>
                <p className="step-desc">PDFs</p>
              </div>
            </div>

            <div className="footer-step">
              <ChatBubbleIcon size={24} className="step-icon" />
              <div className="step-meta">
                <h4 className="step-title">Ask</h4>
                <p className="step-desc">Questions</p>
              </div>
            </div>

            <div className="footer-step">
              <LightbulbIcon size={24} className="step-icon" />
              <div className="step-meta">
                <h4 className="step-title">Get</h4>
                <p className="step-desc">Answers</p>
              </div>
            </div>

            <div className="footer-step">
              <BarChartIcon size={24} className="step-icon" />
              <div className="step-meta">
                <h4 className="step-title">Gain</h4>
                <p className="step-desc">Insights</p>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
