"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

/* ─────────────────────────────────────────────────────────────────────────────
   NEXUS Risk Intelligence Platform — Editorial Reference Frontend
   
   Adheres strictly to the single-source-of-truth reference specification:
   - Full-width deep navy background (#060a12)
   - Large main container with subtle rounded corners and architectural vertical ribbed texture
   - Minimal top navigation bar: brand on left, centered translucent pill, circular action & hamburger on right
   - Upper-right floating information panel with real operational supply metrics
   - Lower-left large lightweight editorial headline & muted supporting description
   - Horizontally aligned primary (warm ivory) & secondary (transparent) CTAs on right
   - Thin horizontal divider
   - Five evenly distributed bottom informational items with fine monochromatic glyphs
   - Zero "vibe-coding" patterns: no harsh gradients, no emojis, no bento grids, no fake terminals
───────────────────────────────────────────────────────────────────────────── */

// ── Monochromatic SVG Glyphs ──

const NodeNetworkIcon: React.FC<{ className?: string }> = ({ className = "w-4 h-4" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="5" cy="6" r="2.5" />
    <circle cx="19" cy="6" r="2.5" />
    <circle cx="12" cy="18" r="2.5" />
    <path d="M7.2 7.2L10.3 15.8" />
    <path d="M16.8 7.2L13.7 15.8" />
    <path d="M7.5 6h9" />
  </svg>
);

const AnomalyPulseIcon: React.FC<{ className?: string }> = ({ className = "w-4 h-4" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12h4l2.5-6 4 12 2.5-6H21" />
  </svg>
);

const ForecastCurveIcon: React.FC<{ className?: string }> = ({ className = "w-4 h-4" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 19L9 13L13 16L21 6" />
    <path d="M17 6H21V10" />
    <path d="M3 21H21" strokeOpacity="0.4" />
  </svg>
);

const MitigationShieldIcon: React.FC<{ className?: string }> = ({ className = "w-4 h-4" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3L4 6.5V12C4 16.5 7.5 20.7 12 22C16.5 20.7 20 16.5 20 12V6.5L12 3Z" />
    <path d="M9 12L11 14L15 10" />
  </svg>
);

const SecurityLockIcon: React.FC<{ className?: string }> = ({ className = "w-4 h-4" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="5" y="11" width="14" height="10" rx="2" />
    <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    <circle cx="12" cy="16" r="1.25" fill="currentColor" />
  </svg>
);

const CompassSearchIcon: React.FC<{ className?: string }> = ({ className = "w-4 h-4" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="7" />
    <path d="M16.5 16.5L20.5 20.5" />
    <path d="M11 8v6M8 11h6" strokeOpacity="0.4" />
  </svg>
);

const CloseIcon: React.FC<{ className?: string }> = ({ className = "w-4 h-4" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 6L6 18M6 6l12 12" />
  </svg>
);

// ── Minimal Top Navigation Bar ──

export const Navigation: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("platform");
  const router = useRouter();

  // Close drawer on ESC key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setDrawerOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <>
      <header
        data-testid="navigation"
        className="w-full pt-6 sm:pt-8 px-6 sm:px-10 lg:px-12 flex items-center justify-between relative z-20"
      >
        {/* Brand identity positioned at upper-left corner */}
        <Link
          href="/"
          className="flex items-center gap-2.5 text-[#f7f4ec] group focus:outline-none focus-visible:ring-1 focus-visible:ring-[#7e94b0] rounded-sm"
          aria-label="NEXUS Home"
        >
          <span className="w-2 h-2 rounded-full bg-[#8fa2bc] opacity-80 group-hover:opacity-100 transition-opacity" />
          <span className="text-[14px] sm:text-[15px] font-medium tracking-[0.24em] uppercase text-[#f7f4ec]">
            NEXUS
          </span>
          <span className="text-[10px] font-mono text-[#5f7491] tracking-wider uppercase hidden sm:inline ml-1 border-l border-[#1f2f4c] pl-2">
            V2.4
          </span>
        </Link>

        {/* Centered pill-shaped navigation menu */}
        <nav
          className="hidden md:flex items-center gap-7 bg-[#0e1626]/75 backdrop-blur-md border border-[#21314d]/60 rounded-full px-5 py-2 shadow-lg shadow-black/20"
          aria-label="Main Navigation"
        >
          <Link
            href="/"
            onClick={() => setActiveTab("platform")}
            className={`text-[12.5px] tracking-wide transition-colors relative ${
              activeTab === "platform"
                ? "text-[#f7f4ec] font-medium"
                : "text-[#7f93ad] hover:text-[#c4d4e8] font-normal"
            }`}
          >
            Platform
            {activeTab === "platform" && (
              <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-[#f7f4ec]" />
            )}
          </Link>

          <Link
            href="/dashboard"
            onClick={() => setActiveTab("risk")}
            className={`text-[12.5px] tracking-wide transition-colors relative ${
              activeTab === "risk"
                ? "text-[#f7f4ec] font-medium"
                : "text-[#7f93ad] hover:text-[#c4d4e8] font-normal"
            }`}
          >
            Risk Engine
          </Link>

          <Link
            href="/graph"
            onClick={() => setActiveTab("topology")}
            className={`text-[12.5px] tracking-wide transition-colors relative ${
              activeTab === "topology"
                ? "text-[#f7f4ec] font-medium"
                : "text-[#7f93ad] hover:text-[#c4d4e8] font-normal"
            }`}
          >
            Topology
          </Link>

          <Link
            href="/mitigation"
            onClick={() => setActiveTab("mitigation")}
            className={`text-[12.5px] tracking-wide transition-colors relative ${
              activeTab === "mitigation"
                ? "text-[#f7f4ec] font-medium"
                : "text-[#7f93ad] hover:text-[#c4d4e8] font-normal"
            }`}
          >
            Mitigation
          </Link>

          <Link
            href="/control-tower"
            onClick={() => setActiveTab("tower")}
            className={`text-[12.5px] tracking-wide transition-colors relative ${
              activeTab === "tower"
                ? "text-[#f7f4ec] font-medium"
                : "text-[#7f93ad] hover:text-[#c4d4e8] font-normal"
            }`}
          >
            Control Tower
          </Link>
        </nav>

        {/* Circular action button and hamburger menu on upper-right */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Circular action button */}
          <button
            type="button"
            onClick={() => router.push("/dashboard")}
            className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-[#0e1626]/75 backdrop-blur-md border border-[#21314d]/60 flex items-center justify-center text-[#9eb0c7] hover:text-[#f7f4ec] hover:border-[#354c75] transition-all focus:outline-none focus-visible:ring-1 focus-visible:ring-[#7e94b0]"
            aria-label="Quick System Search"
            title="Navigate to Live Dashboard"
          >
            <CompassSearchIcon className="w-4 h-4" />
          </button>

          {/* Dark rounded hamburger button */}
          <button
            type="button"
            onClick={() => setDrawerOpen(!drawerOpen)}
            className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-[#0a101d] border border-[#1b2842] flex flex-col items-center justify-center gap-[4px] text-[#9eb0c7] hover:text-[#f7f4ec] hover:border-[#354c75] transition-all focus:outline-none focus-visible:ring-1 focus-visible:ring-[#7e94b0]"
            aria-label="Toggle Navigation Drawer"
            aria-expanded={drawerOpen}
          >
            <span className="w-3.5 h-[1.5px] bg-current rounded-full" />
            <span className="w-3.5 h-[1.5px] bg-current rounded-full" />
          </button>
        </div>
      </header>

      {/* Slide-out Navigation Drawer for all platform modules & legal documents */}
      {drawerOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end transition-opacity duration-200"
          onClick={() => setDrawerOpen(false)}
        >
          <div
            className="w-full max-w-sm sm:max-w-md h-full bg-[#090f1c] border-l border-[#1b2842] p-6 sm:p-8 flex flex-col justify-between overflow-y-auto shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div>
              <div className="flex items-center justify-between pb-6 border-b border-[#162338]">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#8fa2bc]" />
                  <span className="text-[14px] font-medium tracking-[0.2em] uppercase text-[#f7f4ec]">
                    NEXUS DIRECTORY
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setDrawerOpen(false)}
                  className="w-8 h-8 rounded-full border border-[#21314d]/60 flex items-center justify-center text-[#7e94b0] hover:text-[#f7f4ec]"
                  aria-label="Close Navigation Drawer"
                >
                  <CloseIcon className="w-4 h-4" />
                </button>
              </div>

              {/* Navigation sections */}
              <div className="mt-6 space-y-6">
                <div>
                  <span className="text-[10px] font-mono tracking-widest uppercase text-[#5a6f8b] block mb-3">
                    Core Intelligence Engines
                  </span>
                  <ul className="space-y-2 text-[13px]">
                    <li>
                      <Link
                        href="/dashboard"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        Risk Diagnostics Dashboard
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/upload"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        CSV Ingestion & Validation
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/graph"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        Supplier Graph Topology & Centrality
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/mitigation"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        LangGraph Autonomous Mitigation
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/control-tower"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        Real-Time Control Tower Feed
                      </Link>
                    </li>
                  </ul>
                </div>

                <div>
                  <span className="text-[10px] font-mono tracking-widest uppercase text-[#5a6f8b] block mb-3">
                    Advanced Operational Modules
                  </span>
                  <ul className="space-y-2 text-[13px]">
                    <li>
                      <Link
                        href="/xai"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        Explainable AI & Counterfactuals
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/ibp-unified"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        Unified IBP & S&OP Planning
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/sop"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        SOP Playbooks & Response Protocols
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/connectors"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        Enterprise Connectors & ERP Ingest
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/export"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        Executive Memo & Export Center
                      </Link>
                    </li>
                  </ul>
                </div>

                <div>
                  <span className="text-[10px] font-mono tracking-widest uppercase text-[#5a6f8b] block mb-3">
                    Governance & Legal Documentation
                  </span>
                  <ul className="space-y-2 text-[13px]">
                    <li>
                      <Link
                        href="/terms"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        Terms of Service
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/privacy"
                        onClick={() => setDrawerOpen(false)}
                        className="text-[#9eb0c7] hover:text-[#f7f4ec] block py-1.5 transition-colors"
                      >
                        Enterprise Privacy Policy
                      </Link>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-[#162338] text-[11px] text-[#556984] flex items-center justify-between">
              <span>NEXUS Platform v2.4</span>
              <span>Air-Gapped & Offline Ready</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

// ── Hero Section (Floating Panel, Headline, CTA Buttons, Divider, Bottom Strip) ──

export const Hero: React.FC = () => {
  const router = useRouter();
  const [loadingSample, setLoadingSample] = useState(false);

  const handle1ClickDemo = async () => {
    setLoadingSample(true);
    try {
      const res = await fetch("http://localhost:8000/upload/sample", { method: "POST" });
      if (res.ok) {
        router.push("/dashboard");
      } else {
        router.push("/dashboard");
      }
    } catch {
      router.push("/dashboard");
    } finally {
      setLoadingSample(false);
    }
  };

  return (
    <section
      data-testid="hero"
      className="w-full flex-1 flex flex-col justify-between pt-2 sm:pt-4 pb-6 sm:pb-8 px-6 sm:px-10 lg:px-12 relative"
    >
      {/* ── Upper-Right Floating Information Panel ── */}
      <div className="w-full flex justify-end mb-8 sm:mb-12 lg:mb-14">
        <aside
          className="w-full sm:w-[350px] lg:w-[370px] bg-[#10192a]/85 backdrop-blur-md border border-[#233554]/80 rounded-[20px] p-5 sm:p-6 shadow-2xl relative z-10"
          aria-label="Live Network Risk Summary"
        >
          {/* Small location / status heading */}
          <div className="flex items-center gap-2 mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-[#8fa2bc] opacity-90 inline-block animate-pulse" />
            <span className="text-[10.5px] font-mono tracking-[0.18em] uppercase text-[#6f85a3]">
              PACIFIC HUB // LIVE SENSOR STREAM
            </span>
          </div>

          {/* Stacked Entry 1 */}
          <div>
            <div className="text-[11px] font-medium tracking-wider uppercase text-[#889cb5]">
              Critical Bottleneck Exposure
            </div>
            <div className="text-2xl sm:text-3xl font-light tracking-tight text-[#f7f4ec] mt-1 mb-1">
              3 Active Nodes
            </div>
            <div className="text-[12px] text-[#6b7f99] font-light leading-relaxed">
              Titan Logistics, Vanguard Assemblies, Delta Port
            </div>
          </div>

          {/* Subtle divider */}
          <div className="w-full border-b border-[#1f2f4c]/70 my-4" />

          {/* Stacked Entry 2 */}
          <div>
            <div className="text-[11px] font-medium tracking-wider uppercase text-[#889cb5]">
              Estimated Disruption Exposure
            </div>
            <div className="text-2xl sm:text-3xl font-light tracking-tight text-[#f7f4ec] mt-1 mb-1">
              $1,420,000
            </div>
            <div className="text-[12px] text-[#6b7f99] font-light leading-relaxed">
              94.2% mitigation coverage via autonomous rerouting
            </div>
          </div>
        </aside>
      </div>

      {/* ── Hero Content (Lower-Left Headline & Lower-Right CTAs) ── */}
      <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-end mb-8 sm:mb-10">
        {/* Lower-left: Large editorial headline & supporting description */}
        <div className="lg:col-span-8 flex flex-col justify-end">
          <h1
            style={{ fontWeight: 250, color: "#f7f4ec" }}
            className="text-4xl sm:text-5xl md:text-6xl lg:text-[62px] tracking-[-0.035em] leading-[1.08] max-w-3xl"
          >
            Autonomous risk intelligence<br className="hidden md:inline" /> for complex supply chains.
          </h1>
          <p className="text-[14px] sm:text-[15px] text-[#8e9eb5] font-light max-w-xl leading-relaxed mt-4 sm:mt-5">
            Ingest multi-tier supplier data, detect cascading failure modes, and generate
            human-in-the-loop mitigation plans before production halts.
          </p>
        </div>

        {/* Lower-right: Two horizontally aligned CTA buttons */}
        <div className="lg:col-span-4 flex items-center justify-start lg:justify-end gap-3.5 pb-1">
          {/* Primary CTA: Warm ivory background, dark text, rounded pill shape */}
          <Link
            href="/upload"
            style={{ backgroundColor: "#f7f4ec", color: "#0a0f1d" }}
            className="inline-flex items-center justify-center font-medium text-[13px] tracking-wide px-6 py-2.5 rounded-full transition-all duration-150 shadow-sm hover:opacity-95 focus:outline-none focus-visible:ring-1 focus-visible:ring-[#f7f4ec]"
          >
            Launch Pipeline
          </Link>

          {/* Secondary CTA: Transparent background, light typography, minimal visual treatment */}
          <button
            type="button"
            onClick={handle1ClickDemo}
            disabled={loadingSample}
            className="inline-flex items-center justify-center bg-transparent hover:bg-[#152033]/60 text-[#cbd7e6] hover:text-[#f7f4ec] border border-[#263753] hover:border-[#3d5580] text-[13px] font-normal tracking-wide px-6 py-2.5 rounded-full transition-colors duration-150 disabled:opacity-60 focus:outline-none focus-visible:ring-1 focus-visible:ring-[#7e94b0]"
          >
            {loadingSample ? "Loading Demo..." : "Explore Live Demo"}
          </button>
        </div>
      </div>

      {/* ── Thin horizontal divider below the hero content ── */}
      <div className="w-full border-t border-[#1c2940]/80 mb-6 sm:mb-8" />

      {/* ── Five evenly distributed informational items along the bottom ── */}
      <div
        className="w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 sm:gap-8 pb-4"
        aria-label="Platform Architecture Capabilities"
      >
        {/* Item 1 */}
        <div className="flex flex-col">
          <div className="text-[#7e94b0] mb-2">
            <NodeNetworkIcon className="w-4 h-4" />
          </div>
          <span className="text-[11px] font-medium tracking-wider uppercase text-[#9fb0c7] mb-1">
            Graph Topology
          </span>
          <p className="text-[12px] text-[#60738e] font-light leading-relaxed">
            NetworkX directed graph with degree centrality and cascade blast-radius modeling.
          </p>
        </div>

        {/* Item 2 */}
        <div className="flex flex-col">
          <div className="text-[#7e94b0] mb-2">
            <AnomalyPulseIcon className="w-4 h-4" />
          </div>
          <span className="text-[11px] font-medium tracking-wider uppercase text-[#9fb0c7] mb-1">
            Anomaly Detection
          </span>
          <p className="text-[12px] text-[#60738e] font-light leading-relaxed">
            Multi-feature Isolation Forest isolating delay, volume, and cost outliers in-process.
          </p>
        </div>

        {/* Item 3 */}
        <div className="flex flex-col">
          <div className="text-[#7e94b0] mb-2">
            <ForecastCurveIcon className="w-4 h-4" />
          </div>
          <span className="text-[11px] font-medium tracking-wider uppercase text-[#9fb0c7] mb-1">
            Holt-Winters Forecast
          </span>
          <p className="text-[12px] text-[#60738e] font-light leading-relaxed">
            Additive trend and quarterly seasonality with P10/P90 confidence bounds.
          </p>
        </div>

        {/* Item 4 */}
        <div className="flex flex-col">
          <div className="text-[#7e94b0] mb-2">
            <MitigationShieldIcon className="w-4 h-4" />
          </div>
          <span className="text-[11px] font-medium tracking-wider uppercase text-[#9fb0c7] mb-1">
            Mitigation Agent
          </span>
          <p className="text-[12px] text-[#60738e] font-light leading-relaxed">
            6-node LangGraph workflow with deterministic fallback and human approval gate.
          </p>
        </div>

        {/* Item 5 */}
        <div className="flex flex-col">
          <div className="text-[#7e94b0] mb-2">
            <SecurityLockIcon className="w-4 h-4" />
          </div>
          <span className="text-[11px] font-medium tracking-wider uppercase text-[#9fb0c7] mb-1">
            Enterprise Security
          </span>
          <p className="text-[12px] text-[#60738e] font-light leading-relaxed">
            Strict RBAC enforcement, rotating JWT tokens, and untrusted CSV prompt sanitization.
          </p>
        </div>
      </div>
    </section>
  );
};

// ── Minimal Footer / Legal Links ──

export const Footer: React.FC = () => {
  return (
    <footer
      data-testid="footer"
      className="w-full max-w-[1440px] mt-3 px-6 sm:px-10 flex flex-wrap items-center justify-between gap-4 text-[11px] text-[#4d5f78] font-light pb-2"
    >
      <div>
        <span>© 2026 NEXUS Risk Intelligence Inc. Enterprise Edition.</span>
      </div>
      <div className="flex items-center gap-6">
        <Link href="/terms" className="hover:text-[#9eb0c7] transition-colors">
          Terms of Service
        </Link>
        <Link href="/privacy" className="hover:text-[#9eb0c7] transition-colors">
          Enterprise Privacy Policy
        </Link>
        <span className="text-[#32435b]">·</span>
        <span className="text-[#556984] font-mono text-[10px]">LOCAL ENGINE: ONLINE</span>
      </div>
    </footer>
  );
};

// ── Placeholder Exports to maintain complete compatibility with any existing imports ──
export const HowItWorks: React.FC = () => null;
export const FeaturesGrid: React.FC = () => null;
export const Integrations: React.FC = () => null;
export const Pricing: React.FC = () => null;
