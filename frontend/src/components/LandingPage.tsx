import type { SVGProps } from "react";
import "./LandingPage.css";

type IconP = SVGProps<SVGSVGElement> & { size?: number };

const LogoMark = ({ size = 32 }: { size?: number }) => (
  <img className="landing-logo-img" src="/logo.png" alt="ConteXora Logo" style={{ width: size, height: size, objectFit: "contain", marginRight: "12px" }} />
);



// ============== CTA / header icons ==============
const SparkleIcon = ({ size = 16 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2l1.9 5.6L19.5 9.5l-5.6 1.9L12 17l-1.9-5.6L4.5 9.5l5.6-1.9L12 2z" />
  </svg>
);

const ArrowRightIcon = ({ size = 16 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12" />
    <polyline points="12 5 19 12 12 19" />
  </svg>
);

const UserIcon = ({ size = 16 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="8" r="4" />
    <path d="M4 21c0-4 3.6-7 8-7s8 3 8 7" />
  </svg>
);

// ============== Footer step icons ==============
const UploadDocIcon = ({ size = 26 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
    <polyline points="14 2 14 8 20 8" />
  </svg>
);

const AskIcon = ({ size = 26 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.5 8.5 0 0 1-4-1L3 20l1-5.5a8.38 8.38 0 0 1-1-4A8.5 8.5 0 0 1 11.5 2a8.38 8.38 0 0 1 8.5 8.5z" />
    <circle cx="9" cy="11" r="0.8" fill="currentColor" stroke="none" />
    <circle cx="12" cy="11" r="0.8" fill="currentColor" stroke="none" />
    <circle cx="15" cy="11" r="0.8" fill="currentColor" stroke="none" />
  </svg>
);

const AnswersIcon = ({ size = 26 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 18h6" />
    <path d="M10 22h4" />
    <path d="M12 2a6 6 0 0 0-4 10.5c.6.5 1 1.3 1 2.1V15h6v-.4c0-.8.4-1.6 1-2.1A6 6 0 0 0 12 2z" />
  </svg>
);

const InsightsIcon = ({ size = 26 }: IconP) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="20" x2="5" y2="10" />
    <line x1="12" y1="20" x2="12" y2="4" />
    <line x1="19" y1="20" x2="19" y2="14" />
    <path d="M4 20h16" />
  </svg>
);

interface Props {
  onExplore: () => void;
  onNavigate: (path: string) => void;
}

const footerSteps = [
  { key: "upload", label: "Upload PDFs", Icon: UploadDocIcon },
  { key: "ask", label: "Ask Questions", Icon: AskIcon },
  { key: "answers", label: "Get Answers", Icon: AnswersIcon },
  { key: "insights", label: "Gain Insights", Icon: InsightsIcon },
];

export function LandingPage({ onExplore, onNavigate }: Props) {
  return (
    <div className="landing-container">
      {/* Background Dot Grid */}
      <div className="landing-bg-dots" />
      <div className="landing-bg-glow" />

      {/* ================= HEADER ================= */}
      <header className="landing-header">
        <div className="landing-brand" onClick={() => onNavigate("/")} style={{ cursor: "pointer" }}>
          <LogoMark size={44} />
          <div className="landing-brand-text">
            <h1 className="landing-brand-name">
              <span>ConteX</span><span style={{ fontWeight: 400 }}>ora</span>
            </h1>
            <p className="landing-brand-tagline">Transforming Context into Intelligence</p>
          </div>
        </div>

        <div className="header-right-group">
          <nav className="landing-nav">
            <a href="#" className="landing-nav-link active" onClick={(e) => { e.preventDefault(); onNavigate("/"); }}>Home</a>
            <a href="#" className="landing-nav-link">Pricing</a>
            <a href="#" className="landing-nav-link">About Us</a>
            <a href="#" className="landing-nav-link">Contact Us</a>
          </nav>
          <div className="header-divider" />
          <button className="landing-signin-btn" title="Sign In">
            <UserIcon size={16} />
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
            AI-powered Retrieval-Augmented Generation platform for understanding
            documents with accurate, grounded responses.
          </p>

          <div className="landing-actions-group">
            <button className="landing-cta-btn" onClick={onExplore} title="Explore ConteXora">
              <SparkleIcon size={16} />
              <span>Explore ConteXora</span>
              <ArrowRightIcon size={16} />
            </button>
          </div>
        </div>

        {/* Right Column: Schema and Circuit Node Connections */}
        {/* Right Column: Features Schematic Illustration */}
        <div className="landing-hero-right">
          <img className="landing-hero-illustration" src="/hero-illustration.png" alt="ConteXora Features Schematic Illustration" />
        </div>
      </main>

      {/* ================= FOOTER BAND ================= */}
      <footer className="landing-footer-band">
        <div className="landing-footer-quote">
          <p>&ldquo;From documents to understanding,<br />from context to intelligence.&rdquo;</p>
        </div>

        <div className="landing-footer-steps">
          {footerSteps.map(({ key, label, Icon }) => (
            <div className="footer-step" key={key}>
              <Icon size={26} />
              <span>{label}</span>
            </div>
          ))}
        </div>
      </footer>

      <div className="landing-legal-bar">
        <span>&copy; 2026 ConteXora. All rights reserved.</span>
        <div className="legal-links">
          <a href="#" className="footer-link">Privacy Policy</a>
          <span className="footer-separator">|</span>
          <a href="#" className="footer-link">Terms of Service</a>
        </div>
      </div>
    </div>
  );
}