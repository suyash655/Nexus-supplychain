"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Menu, X, ChevronRight, FolderUp, Search, Brain, Zap, Shield, Microscope, GitBranch, BarChart3, Dna, Link2, Globe, Database, Cloud, Server, Code, Check, Star, Layers, Cpu, Network, Lock, ArrowUpRight } from "lucide-react";

/* ─────────────────────────────────────────────────────────
   NEXUS Marketing Layer — Full landing page components
   Uses INLINE STYLES to match existing codebase pattern.
   Preserves existing color palette from globals.css:
   --color-bg: #0A0A0A
   --color-surface: #111111
   --color-accent: #E8FF47
   --color-text-1: #F5F5F5
   --color-text-2: #888888
   --color-border: #222222
   ───────────────────────────────────────────────────────── */

// ── Inline Button ──
interface BtnProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "ghost" | "accent" | "outline";
    size?: "sm" | "md" | "lg";
}

const Btn: React.FC<BtnProps> = ({ variant = "primary", size = "md", style, children, ...props }) => {
    const base: React.CSSProperties = {
        display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 8,
        fontWeight: 600, borderRadius: 8, border: "none", cursor: "pointer",
        transition: "all 0.3s ease", fontFamily: "var(--font-sans, Inter, sans-serif)",
        textDecoration: "none", whiteSpace: "nowrap",
        position: "relative", overflow: "hidden",
    };

    const sizes: Record<string, React.CSSProperties> = {
        sm: { height: 36, padding: "0 16px", fontSize: 13 },
        md: { height: 42, padding: "0 20px", fontSize: 14 },
        lg: { height: 48, padding: "0 24px", fontSize: 15 },
    };

    const variants: Record<string, React.CSSProperties> = {
        primary: { background: "var(--color-accent, #E8FF47)", color: "#0A0A0A" },
        secondary: { background: "var(--color-surface, #111111)", color: "var(--color-text-1, #F5F5F5)", border: "1px solid var(--color-border, #222222)" },
        ghost: { background: "transparent", color: "var(--color-text-2, #888888)", border: "1px solid var(--color-border, #222222)" },
        accent: { background: "var(--color-accent, #E8FF47)", color: "#0A0A0A" },
        outline: { background: "transparent", color: "var(--color-text-1, #F5F5F5)", border: "1px solid var(--color-border-hi, #333333)" },
    };

    return (
        <button 
            style={{ ...base, ...sizes[size], ...variants[variant], ...style }} 
            {...props}
            onMouseEnter={(e) => {
                // Enhanced hover effects
                if (variant === "primary" || variant === "accent") {
                    e.currentTarget.style.transform = "translateY(-2px)";
                    e.currentTarget.style.boxShadow = "0 8px 24px rgba(232, 255, 71, 0.25)";
                } else if (variant === "secondary" || variant === "outline") {
                    e.currentTarget.style.background = "var(--color-surface-2, #1A1A1A)";
                    e.currentTarget.style.borderColor = "var(--color-border-hi, #333333)";
                    e.currentTarget.style.transform = "translateY(-2px)";
                } else if (variant === "ghost") {
                    e.currentTarget.style.background = "var(--color-surface-2, #1A1A1A)";
                    e.currentTarget.style.color = "var(--color-text-1, #F5F5F5)";
                    e.currentTarget.style.transform = "translateY(-2px)";
                }
            }}
            onMouseLeave={(e) => {
                // Reset to base styles
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "none";
                if (variant === "secondary" || variant === "outline") {
                    e.currentTarget.style.background = "var(--color-surface, #111111)";
                    e.currentTarget.style.borderColor = "var(--color-border, #222222)";
                } else if (variant === "ghost") {
                    e.currentTarget.style.background = "transparent";
                    e.currentTarget.style.color = "var(--color-text-2, #888888)";
                }
            }}
            onMouseDown={(e) => {
                // Active/pressed state
                e.currentTarget.style.transform = "translateY(0)";
            }}
            onMouseUp={(e) => {
                // Release active state
                if (variant === "primary" || variant === "accent") {
                    e.currentTarget.style.transform = "translateY(-2px)";
                } else {
                    e.currentTarget.style.transform = "translateY(-2px)";
                }
            }}
        >
            {children}
        </button>
    );
};

// ── Navigation ──
export const Navigation = React.memo(() => {
    const [open, setOpen] = React.useState(false);

    const navStyle: React.CSSProperties = {
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 100,
        borderBottom: "1px solid var(--color-border, #222222)",
        background: "rgba(10,10,10,0.85)", backdropFilter: "blur(16px)",
    };

    const navLinks = [
        { href: "#how-it-works", label: "How it Works" },
        { href: "#features", label: "Features" },
        { href: "#integrations", label: "Integrations" },
        { href: "#pricing", label: "Pricing" },
    ];

    const handleSmoothScroll = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
        e.preventDefault();
        const element = document.querySelector(href);
        if (element) {
            element.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };

    return (
        <header style={navStyle}>
            <nav style={{ maxWidth: 1200, margin: "0 auto", padding: "12px 24px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <Link href="/" style={{ fontSize: 22, fontWeight: 700, color: "var(--color-text-1, #F5F5F5)", textDecoration: "none", letterSpacing: "-0.03em" }}>
                    NEXUS<span style={{ color: "var(--color-accent, #E8FF47)" }}>.</span>
                </Link>

                {/* Desktop nav */}
                <div style={{ display: "flex", gap: 32, position: "absolute", left: "50%", transform: "translateX(-50%)" }} className="nav-desktop-links">
                    {navLinks.map((l) => (
                        <a 
                            key={l.href} 
                            href={l.href} 
                            style={{ fontSize: 14, color: "var(--color-text-2, #888888)", textDecoration: "none", transition: "color 0.2s ease", cursor: "pointer", fontWeight: 500 }}
                            onClick={(e) => handleSmoothScroll(e, l.href)}
                            onMouseEnter={(e) => (e.currentTarget.style.color = "var(--color-text-1, #F5F5F5)")}
                            onMouseLeave={(e) => (e.currentTarget.style.color = "var(--color-text-2, #888888)")}>
                            {l.label}
                        </a>
                    ))}
                </div>

                {/* Desktop CTA */}
                <div style={{ display: "flex", gap: 12 }} className="nav-desktop-cta">
                    <Link href="/login" style={{ textDecoration: "none" }}>
                        <Btn variant="outline" size="sm">Sign in</Btn>
                    </Link>
                    <Link href="/login" style={{ textDecoration: "none" }}>
                        <Btn variant="primary" size="sm">Get Started <ArrowRight size={14} /></Btn>
                    </Link>
                </div>

                {/* Mobile toggle */}
                <button 
                    onClick={() => setOpen(!open)} 
                    style={{ display: "none", background: "none", border: "none", color: "var(--color-text-1, #F5F5F5)", cursor: "pointer", padding: 8 }} 
                    className="nav-mobile-toggle"
                    aria-label="Toggle menu"
                >
                    {open ? <X size={24} /> : <Menu size={24} />}
                </button>
            </nav>

            {/* Mobile menu */}
            {open && (
                <div style={{ background: "rgba(10,10,10,0.95)", backdropFilter: "blur(16px)", borderTop: "1px solid var(--color-border, #222222)", padding: "16px 24px" }} className="nav-mobile-menu">
                    {navLinks.map((l) => (
                        <a 
                            key={l.href} 
                            href={l.href} 
                            onClick={(e) => {
                                handleSmoothScroll(e, l.href);
                                setOpen(false);
                            }}
                            style={{ display: "block", padding: "12px 0", fontSize: 16, color: "var(--color-text-2, #888888)", textDecoration: "none", cursor: "pointer", fontWeight: 500 }}
                            onMouseEnter={(e) => (e.currentTarget.style.color = "var(--color-text-1, #F5F5F5)")}
                            onMouseLeave={(e) => (e.currentTarget.style.color = "var(--color-text-2, #888888)")}
                        >
                            {l.label}
                        </a>
                    ))}
                    <div style={{ borderTop: "1px solid var(--color-border, #222222)", paddingTop: 16, marginTop: 8, display: "flex", flexDirection: "column", gap: 12 }}>
                        <Link href="/login" style={{ textDecoration: "none" }}><Btn variant="outline" size="sm" style={{ width: "100%" }}>Sign in</Btn></Link>
                        <Link href="/login" style={{ textDecoration: "none" }}><Btn variant="primary" size="sm" style={{ width: "100%" }}>Get Started</Btn></Link>
                    </div>
                </div>
            )}

            {/* Responsive CSS */}
            <style>{`
                @media (max-width: 968px) {
                    .nav-desktop-links, .nav-desktop-cta { display: none !important; }
                    .nav-mobile-toggle { display: block !important; }
                }
                @media (min-width: 969px) {
                    .nav-mobile-menu { display: none !important; }
                }
            `}</style>
        </header>
    );
});
Navigation.displayName = "Navigation";

// ── Hero ──
export const Hero = React.memo(() => {
    return (
        <section style={{ position: "relative", minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "100px 24px 60px", background: "var(--color-bg, #0A0A0A)", overflow: "hidden" }}>
            {/* Background glow */}
            <div style={{ position: "absolute", top: "20%", left: "50%", transform: "translateX(-50%)", width: 700, height: 700, borderRadius: "50%", background: "radial-gradient(circle, rgba(232,255,71,0.08) 0%, transparent 70%)", pointerEvents: "none" }} />
            <div style={{ position: "absolute", top: "40%", left: "30%", width: 400, height: 400, borderRadius: "50%", background: "radial-gradient(circle, rgba(99,102,241,0.06) 0%, transparent 70%)", pointerEvents: "none" }} />

            {/* 2-Column Layout */}
            <div style={{ maxWidth: 1200, margin: "0 auto", width: "100%", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 48, alignItems: "center", position: "relative", zIndex: 1 }}>

                {/* Left Column - Text Content */}
                <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
                    {/* Announcement badge */}
                    <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "8px 16px", borderRadius: 50, border: "1px solid var(--color-border, #222222)", background: "var(--color-surface, #111111)", width: "fit-content" }}>
                        <span style={{ fontSize: 12, color: "var(--color-accent, #E8FF47)", fontWeight: 600 }}>NEW</span>
                        <span style={{ fontSize: 12, color: "var(--color-text-2, #888888)" }}>AI-assisted Risk Propagation Engine</span>
                        <ChevronRight size={14} style={{ color: "var(--color-text-2, #888888)" }} />
                    </div>

                    {/* Headline */}
                    <h1 style={{
                        fontSize: "clamp(40px, 5vw, 56px)", fontWeight: 800, lineHeight: 1.1,
                        color: "var(--color-text-1, #F5F5F5)", marginBottom: 16,
                        letterSpacing: "-0.04em",
                    }}>
                        Supply Chain Intelligence{"\n"}that thinks ahead of risk
                    </h1>

                    {/* Subheadline */}
                    <p style={{ fontSize: 18, color: "var(--color-text-2, #888888)", lineHeight: 1.7, marginBottom: 8, fontWeight: 400 }}>
                        Upload your supply data. NEXUS maps your entire network, predicts cascading failures,
                        and surfaces AI-driven counterfactuals — before disruptions hit your bottom line.
                    </p>

                    {/* CTA Buttons */}
                    <div style={{ display: "flex", gap: 16, marginBottom: 32, flexWrap: "wrap" }}>
                        <Link href="/login" style={{ textDecoration: "none" }}>
                            <Btn variant="primary" size="lg">
                                Start for free <ArrowRight size={18} />
                            </Btn>
                        </Link>
                        <Link href="/dashboard" style={{ textDecoration: "none" }}>
                            <Btn variant="outline" size="lg">Try the demo</Btn>
                        </Link>
                    </div>

                    {/* Social Proof / Trust Badges */}
                    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                        <p style={{ fontSize: 13, color: "var(--color-text-3, #555555)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                            Trusted by supply chain teams at
                        </p>
                        <div style={{ display: "flex", gap: 24, alignItems: "center", flexWrap: "wrap" }}>
                            {["TechCorp", "GlobalMfg", "SupplyAI", "RiskOps"].map((company) => (
                                <div 
                                    key={company}
                                    style={{ 
                                        fontSize: 14, fontWeight: 600, color: "var(--color-text-3, #555555)",
                                        transition: "color 0.2s ease", cursor: "default"
                                    }}
                                    onMouseEnter={(e) => e.currentTarget.style.color = "var(--color-text-2, #888888)"}
                                    onMouseLeave={(e) => e.currentTarget.style.color = "var(--color-text-3, #555555)"}
                                >
                                    {company}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right Column - Dashboard Preview */}
                <div style={{ position: "relative" }}>
                    {/* Glow effect */}
                    <div style={{ position: "absolute", top: -20, left: "50%", transform: "translateX(-50%)", width: "80%", height: 60, background: "radial-gradient(ellipse, rgba(232,255,71,0.15) 0%, transparent 70%)", borderRadius: 999, pointerEvents: "none" }} />

                    <div style={{ position: "relative", borderRadius: 16, border: "1px solid var(--color-border, #222222)", overflow: "hidden", boxShadow: "0 25px 50px -12px rgba(0,0,0,0.5)", background: "var(--color-surface, #111111)" }}>
                        {/* Browser chrome */}
                        <div style={{ background: "var(--color-surface-2, #1A1A1A)", borderBottom: "1px solid var(--color-border, #222222)", padding: "12px 16px", display: "flex", alignItems: "center", gap: 8 }}>
                            <span style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--color-danger, #FF4444)" }} />
                            <span style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--color-warn, #F59E0B)" }} />
                            <span style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--color-ok, #22C55E)" }} />
                            <div style={{ marginLeft: 16, flex: 1, background: "var(--color-surface, #111111)", borderRadius: 6, padding: "5px 12px", fontSize: 12, color: "var(--color-text-3, #555555)" }}>
                                nexus.app/dashboard
                            </div>
                            {/* Illustrative label */}
                            <div style={{ 
                                padding: "4px 8px", 
                                borderRadius: 4, 
                                background: "rgba(232,255,71,0.1)", 
                                border: "1px solid rgba(232,255,71,0.3)", 
                                fontSize: 10, 
                                color: "var(--color-accent, #E8FF47)", 
                                fontWeight: 500,
                                textTransform: "uppercase",
                                letterSpacing: "0.05em"
                            }}>
                                Illustrative
                            </div>
                        </div>

                        {/* Dashboard mock */}
                        <div style={{ background: "var(--color-bg, #0A0A0A)", padding: 20, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
                            {/* Top KPI */}
                            {[
                                { label: "Overall Risk Score", value: "78.4", color: "var(--color-danger, #FF4444)", sub: "+5.2% this week" },
                                { label: "Active Suppliers", value: "142", color: "var(--color-warn, #F59E0B)", sub: "12 at elevated risk" },
                                { label: "Anomalies Detected", value: "23", color: "#38bdf8", sub: "via Isolation Forest" },
                            ].map((k) => (
                                <div key={k.label} style={{ background: "var(--color-surface, #111111)", borderRadius: 12, padding: 16, border: "1px solid var(--color-border, #222222)" }}>
                                    <div style={{ fontSize: 11, color: "var(--color-text-3, #555555)", fontWeight: 500, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.05em" }}>{k.label}</div>
                                    <div style={{ fontSize: 28, fontWeight: 700, color: k.color, letterSpacing: "-0.02em" }}>{k.value}</div>
                                    <div style={{ fontSize: 11, color: "var(--color-text-3, #555555)", marginTop: 4 }}>{k.sub}</div>
                                </div>
                            ))}

                            {/* Bar chart */}
                            <div style={{ gridColumn: "span 2", background: "var(--color-surface, #111111)", borderRadius: 12, padding: 16, border: "1px solid var(--color-border, #222222)" }}>
                                <div style={{ fontSize: 11, color: "var(--color-text-3, #555555)", fontWeight: 500, marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>Risk by Supplier (top 8)</div>
                                <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 80 }}>
                                    {[82, 74, 68, 65, 58, 51, 43, 31].map((h, i) => (
                                        <div key={i} style={{ flex: 1, borderRadius: "4px 4px 0 0", height: `${h}%`, background: h > 70 ? "var(--color-danger, #FF4444)" : h > 50 ? "var(--color-warn, #F59E0B)" : "var(--color-ok, #22C55E)", opacity: 0.7, transition: "height 0.4s ease" }} />
                                    ))}
                                </div>
                            </div>

                            {/* Resilience */}
                            <div style={{ background: "var(--color-surface, #111111)", borderRadius: 12, padding: 16, border: "1px solid var(--color-border, #222222)", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                                <div style={{ fontSize: 11, color: "var(--color-text-3, #555555)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em" }}>Network Resilience</div>
                                <div style={{ fontSize: 36, fontWeight: 700, color: "#a78bfa", letterSpacing: "-0.02em" }}>67.2</div>
                                <div style={{ fontSize: 11, color: "var(--color-text-3, #555555)" }}>Structural Robustness: Medium</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Responsive */}
            <style>{`
                @media (max-width: 968px) {
                    section > div:first-of-type {
                        grid-template-columns: 1fr !important;
                        gap: 40px !important;
                    }
                }
            `}</style>
        </section>
    );
});
Hero.displayName = "Hero";

// ── How It Works ──
export const HowItWorks = () => {
    const steps = [
        { num: "01", title: "Connect Your Data", desc: "Upload CSV/Excel or connect via S3, SQL, or REST API.", Icon: FolderUp },
        { num: "02", title: "Map & Validate", desc: "Auto-detect columns, set dimensions vs measures, enforce data quality.", Icon: Search },
        { num: "03", title: "AI Analyzes", desc: "ML pipeline runs risk scoring, anomaly detection, and time-series forecasts.", Icon: Brain },
        { num: "04", title: "Act on Insights", desc: "Get counterfactual recommendations and cascade simulations.", Icon: Zap },
    ];

    return (
        <section id="how-it-works" style={{ background: "var(--color-bg, #0A0A0A)", padding: "80px 24px", borderTop: "1px solid var(--color-border, #222222)" }}>
            <div style={{ maxWidth: 1200, margin: "0 auto" }}>
                {/* Section Header */}
                <div style={{ textAlign: "center", marginBottom: 48 }}>
                    <div style={{ 
                        display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 14px", borderRadius: 50, 
                        border: "1px solid var(--color-accent, #E8FF47)", background: "rgba(232,255,71,0.08)", marginBottom: 24 
                    }}>
                        <span style={{ fontSize: 11, color: "var(--color-accent, #E8FF47)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                            How It Works
                        </span>
                    </div>
                    <h2 style={{
                        fontSize: "clamp(32px, 4vw, 48px)", fontWeight: 700, color: "var(--color-text-1, #F5F5F5)",
                        marginBottom: 16, letterSpacing: "-0.03em", lineHeight: 1.2,
                    }}>
                        From raw data to decisions in minutes
                    </h2>
                    <p style={{ color: "var(--color-text-2, #888888)", maxWidth: 600, margin: "0 auto", fontSize: 16, lineHeight: 1.7 }}>
                        No data science degree required. NEXUS handles the heavy lifting.
                    </p>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 32 }}>
                    {steps.map((s, i) => (
                        <div 
                            key={s.num} 
                            style={{ 
                                position: "relative", cursor: "pointer", transition: "transform 0.3s ease",
                                padding: 24, borderRadius: 16, border: "1px solid var(--color-border, #222222)",
                                background: "var(--color-surface, #111111)"
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = "translateY(-4px)";
                                e.currentTarget.style.borderColor = "var(--color-border-hi, #333333)";
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = "translateY(0)";
                                e.currentTarget.style.borderColor = "var(--color-border, #222222)";
                            }}
                            onClick={() => {
                                console.log(`Step clicked: ${s.title}`);
                            }}
                            role="button"
                            tabIndex={0}
                            onKeyDown={(e) => {
                                if (e.key === "Enter" || e.key === " ") {
                                    e.preventDefault();
                                    console.log(`Step activated: ${s.title}`);
                                }
                            }}
                        >
                            <div 
                                style={{ 
                                    width: 56, height: 56, borderRadius: 12, background: "rgba(232,255,71,0.1)", 
                                    display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20,
                                    transition: "background 0.2s ease, transform 0.2s ease"
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.background = "rgba(232,255,71,0.15)";
                                    e.currentTarget.style.transform = "scale(1.05)";
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.background = "rgba(232,255,71,0.1)";
                                    e.currentTarget.style.transform = "scale(1)";
                                }}
                            >
                                <s.Icon size={28} color="var(--color-accent, #E8FF47)" />
                            </div>
                            <div style={{ fontSize: 12, color: "var(--color-text-3, #555555)", fontWeight: 700, marginBottom: 12, letterSpacing: "0.1em" }}>STEP {s.num}</div>
                            <h3 style={{ color: "var(--color-text-1, #F5F5F5)", fontWeight: 600, fontSize: 18, marginBottom: 12, letterSpacing: "-0.01em" }}>{s.title}</h3>
                            <p style={{ color: "var(--color-text-2, #888888)", fontSize: 14, lineHeight: 1.6 }}>{s.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

// ── Features Section (Zig-Zag Layout) ──
export const FeaturesGrid = () => {
    const features = [
        { 
            Icon: Shield, 
            title: "Composite Risk Scoring", 
            desc: "Multi-factor 0–100 risk scores using delay, cost, quality, and consistency metrics.",
            badge: "ML",
            points: ["Real-time risk calculations", "Customizable weight factors", "Historical trend analysis", "Automated alert thresholds"]
        },
        { 
            Icon: Microscope, 
            title: "Anomaly Detection", 
            desc: "Isolation Forest + Z-score + IQR: three methods, one unified anomaly pipeline.",
            badge: "ML",
            points: ["Multiple detection algorithms", "Reduced false positives", "Pattern learning", "Real-time monitoring"]
        },
        { 
            Icon: GitBranch, 
            title: "Graph Intelligence", 
            desc: "Force-directed network topology with PageRank, betweenness, and cascade simulation.",
            badge: "Graph",
            points: ["Interactive network visualization", "Critical path identification", "Cascade impact modeling", "Supplier dependency mapping"]
        },
        { 
            Icon: BarChart3, 
            title: "Time-Series Forecast", 
            desc: "Holt-Winters triple exponential smoothing for delay and cost prediction.",
            badge: "Forecast",
            points: ["Predictive delay modeling", "Cost projection analysis", "Seasonality detection", "Confidence intervals"]
        },
    ];

    return (
        <section id="features" style={{ background: "var(--color-bg, #0A0A0A)", padding: "80px 24px", borderTop: "1px solid var(--color-border, #222222)" }}>
            <div style={{ maxWidth: 1200, margin: "0 auto" }}>
                {/* Section Header */}
                <div style={{ textAlign: "center", marginBottom: 48 }}>
                    <div style={{ 
                        display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 14px", borderRadius: 50, 
                        border: "1px solid var(--color-accent, #E8FF47)", background: "rgba(232,255,71,0.08)", marginBottom: 24 
                    }}>
                        <span style={{ fontSize: 11, color: "var(--color-accent, #E8FF47)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                            Features
                        </span>
                    </div>
                    <h2 style={{ 
                        fontSize: "clamp(32px, 4vw, 48px)", fontWeight: 700, color: "var(--color-text-1, #F5F5F5)", 
                        marginBottom: 16, letterSpacing: "-0.03em", lineHeight: 1.2 
                    }}>
                        Every analytical skill, one platform
                    </h2>
                    <p style={{ 
                        color: "var(--color-text-2, #888888)", maxWidth: 600, margin: "0 auto", fontSize: 16, lineHeight: 1.7 
                    }}>
                        A complete data analytics toolkit for supply chain intelligence that scales with your needs.
                    </p>
                </div>

                {/* Zig-Zag Feature Rows */}
                <div style={{ display: "flex", flexDirection: "column", gap: 96 }}>
                    {features.map((feature, index) => {
                        const isEven = index % 2 === 0;
                        
                        return (
                            <div 
                                key={feature.title}
                                style={{ 
                                    display: "grid", 
                                    gridTemplateColumns: "1fr 1fr", 
                                    gap: 64, 
                                    alignItems: "center",
                                    direction: isEven ? "ltr" : "rtl"
                                }}
                            >
                                {/* Image/Dashboard Side */}
                                <div style={{ 
                                    order: isEven ? 1 : 2,
                                    position: "relative"
                                }}>
                                    <div style={{ 
                                        borderRadius: 16, 
                                        border: "1px solid var(--color-border, #222222)", 
                                        overflow: "hidden", 
                                        boxShadow: "0 20px 40px -12px rgba(0,0,0,0.4)",
                                        background: "var(--color-surface, #111111)",
                                        padding: 32,
                                        minHeight: 280,
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center"
                                    }}>
                                        <div style={{ 
                                            width: 80, height: 80, borderRadius: 20, 
                                            background: "rgba(232,255,71,0.1)", 
                                            display: "flex", alignItems: "center", justifyContent: "center" 
                                        }}>
                                            <feature.Icon size={40} color="var(--color-accent, #E8FF47)" />
                                        </div>
                                    </div>
                                </div>

                                {/* Text Content Side */}
                                <div style={{ order: isEven ? 2 : 1, display: "flex", flexDirection: "column", gap: 16 }}>
                                    {/* Badge */}
                                    <div style={{ 
                                        display: "inline-flex", alignItems: "center", gap: 6, padding: "4px 12px", 
                                        borderRadius: 50, background: "rgba(232,255,71,0.1)", width: "fit-content" 
                                    }}>
                                        <span style={{ fontSize: 11, color: "var(--color-accent, #E8FF47)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                                            {feature.badge}
                                        </span>
                                    </div>

                                    {/* Heading */}
                                    <h3 style={{ 
                                        fontSize: 28, fontWeight: 700, color: "var(--color-text-1, #F5F5F5)", 
                                        marginBottom: 8, letterSpacing: "-0.02em", lineHeight: 1.3 
                                    }}>
                                        {feature.title}
                                    </h3>

                                    {/* Description */}
                                    <p style={{ 
                                        fontSize: 16, color: "var(--color-text-2, #888888)", lineHeight: 1.7, marginBottom: 16 
                                    }}>
                                        {feature.desc}
                                    </p>

                                    {/* Bullet Points */}
                                    <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 12 }}>
                                        {feature.points.map((point, i) => (
                                            <li key={i} style={{ 
                                                display: "flex", alignItems: "center", gap: 12, fontSize: 14, 
                                                color: "var(--color-text-2, #888888)" 
                                            }}>
                                                <span style={{ 
                                                    width: 20, height: 20, borderRadius: 4, 
                                                    background: "rgba(232,255,71,0.1)", 
                                                    display: "flex", alignItems: "center", justifyContent: "center",
                                                    flexShrink: 0
                                                }}>
                                                    <Check size={12} color="var(--color-accent, #E8FF47)" />
                                                </span>
                                                {point}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Responsive */}
            <style>{`
                @media (max-width: 968px) {
                    section > div > div[style*="gridTemplateColumns"] {
                        grid-template-columns: 1fr !important;
                        gap: 32px !important;
                    }
                    section > div > div[style*="gridTemplateColumns"] > div:first-child {
                        order: 1 !important;
                    }
                    section > div > div[style*="gridTemplateColumns"] > div:last-child {
                        order: 2 !important;
                    }
                }
            `}</style>
        </section>
    );
};

// ── Integrations Section (Grid Layout) ──
export const Integrations = () => {
    const integrations = [
        { Icon: Database, name: "PostgreSQL", desc: "Direct database connection for real-time sync" },
        { Icon: Cloud, name: "AWS S3", desc: "Secure cloud storage for large datasets" },
        { Icon: Server, name: "REST API", desc: "Custom API endpoints for flexible integration" },
        { Icon: Code, name: "Webhooks", desc: "Real-time event notifications and triggers" },
        { Icon: Layers, name: "Snowflake", desc: "Data warehouse integration for analytics" },
        { Icon: Cpu, name: "Kafka", desc: "Stream processing for real-time data pipelines" },
        { Icon: Network, name: "GraphQL", desc: "Flexible query language for data fetching" },
        { Icon: Lock, name: "Auth0", desc: "Enterprise-grade authentication and security" },
    ];

    return (
        <section id="integrations" style={{ background: "var(--color-bg, #0A0A0A)", padding: "80px 24px", borderTop: "1px solid var(--color-border, #222222)" }}>
            <div style={{ maxWidth: 1200, margin: "0 auto" }}>
                {/* Section Header */}
                <div style={{ textAlign: "center", marginBottom: 48 }}>
                    <div style={{ 
                        display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 14px", borderRadius: 50, 
                        border: "1px solid var(--color-accent, #E8FF47)", background: "rgba(232,255,71,0.08)", marginBottom: 24 
                    }}>
                        <span style={{ fontSize: 11, color: "var(--color-accent, #E8FF47)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                            Integrations
                        </span>
                    </div>
                    <h2 style={{ 
                        fontSize: "clamp(32px, 4vw, 48px)", fontWeight: 700, color: "var(--color-text-1, #F5F5F5)", 
                        marginBottom: 16, letterSpacing: "-0.03em", lineHeight: 1.2 
                    }}>
                        Connect with your existing stack
                    </h2>
                    <p style={{ 
                        color: "var(--color-text-2, #888888)", maxWidth: 600, margin: "0 auto", fontSize: 16, lineHeight: 1.7 
                    }}>
                        Seamlessly integrate NEXUS with your favorite tools and data sources.
                    </p>
                </div>

                {/* Integration Cards Grid */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 24 }}>
                    {integrations.map((integration) => (
                        <div
                            key={integration.name}
                            style={{
                                background: "var(--color-surface, #111111)",
                                border: "1px solid var(--color-border, #222222)",
                                borderRadius: 16,
                                padding: 24,
                                cursor: "pointer",
                                transition: "all 0.3s ease",
                                position: "relative",
                                overflow: "hidden",
                            }}
                            onClick={() => {
                                console.log(`Integration clicked: ${integration.name}`);
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = "translateY(-4px)";
                                e.currentTarget.style.borderColor = "var(--color-border-hi, #333333)";
                                e.currentTarget.style.boxShadow = "0 12px 24px -8px rgba(0,0,0,0.4)";
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = "translateY(0)";
                                e.currentTarget.style.borderColor = "var(--color-border, #222222)";
                                e.currentTarget.style.boxShadow = "none";
                            }}
                            onMouseDown={(e) => {
                                e.currentTarget.style.transform = "translateY(-2px)";
                            }}
                            onMouseUp={(e) => {
                                e.currentTarget.style.transform = "translateY(-4px)";
                            }}
                            role="button"
                            tabIndex={0}
                            onKeyDown={(e) => {
                                if (e.key === "Enter" || e.key === " ") {
                                    e.preventDefault();
                                    console.log(`Integration activated: ${integration.name}`);
                                }
                            }}
                        >
                            {/* Icon Container */}
                            <div style={{ 
                                width: 56, height: 56, borderRadius: 12, 
                                background: "rgba(232,255,71,0.1)", 
                                display: "flex", alignItems: "center", justifyContent: "center",
                                marginBottom: 16,
                                transition: "background 0.2s ease"
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.background = "rgba(232,255,71,0.15)";
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.background = "rgba(232,255,71,0.1)";
                            }}
                            >
                                <integration.Icon size={28} color="var(--color-accent, #E8FF47)" />
                            </div>

                            {/* Integration Name */}
                            <h3 style={{ 
                                fontSize: 18, fontWeight: 600, color: "var(--color-text-1, #F5F5F5)", 
                                marginBottom: 8, letterSpacing: "-0.01em" 
                            }}>
                                {integration.name}
                            </h3>

                            {/* Description */}
                            <p style={{ 
                                fontSize: 14, color: "var(--color-text-2, #888888)", lineHeight: 1.6, marginBottom: 16 
                            }}>
                                {integration.desc}
                            </p>

                            {/* Arrow Icon */}
                            <div style={{ 
                                display: "flex", alignItems: "center", gap: 8, 
                                color: "var(--color-accent, #E8FF47)", fontSize: 13, fontWeight: 500 
                            }}>
                                <span>Learn more</span>
                                <ArrowUpRight size={16} />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

// ── Pricing Section (3-Column Highlight Layout) ──
export const Pricing = () => {
    const [annual, setAnnual] = React.useState(false);

    const tiers = [
        {
            name: "Starter", monthly: 0, annually: 0,
            features: ["Up to 10,000 rows", "3 data connectors", "Basic risk scores", "CSV export", "Email support"],
            cta: "Start free", popular: false,
        },
        {
            name: "Pro", monthly: 79, annually: 59, popular: true,
            features: ["Up to 500,000 rows", "All connectors (S3, SQL, API)", "Full ML suite + XAI", "Graph Intelligence", "Priority support + Slack"],
            cta: "Start Pro trial",
        },
        {
            name: "Enterprise", monthly: null, annually: null, popular: false,
            features: ["Unlimited rows & seats", "Custom connectors", "Dedicated infra & SLA", "RBAC + Audit Logs", "Custom training + onboarding"],
            cta: "Contact us",
        },
    ];

    const cardBase: React.CSSProperties = {
        position: "relative", borderRadius: 16, padding: 32, display: "flex", flexDirection: "column",
        border: "1px solid var(--color-border, #222222)", background: "var(--color-surface, #111111)", 
        transition: "all 0.3s ease", cursor: "pointer",
    };

    return (
        <section id="pricing" style={{ background: "var(--color-bg, #0A0A0A)", padding: "80px 24px", borderTop: "1px solid var(--color-border, #222222)" }}>
            <div style={{ maxWidth: 1200, margin: "0 auto" }}>
                {/* Section Header */}
                <div style={{ textAlign: "center", marginBottom: 48 }}>
                    <div style={{ 
                        display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 14px", borderRadius: 50, 
                        border: "1px solid var(--color-accent, #E8FF47)", background: "rgba(232,255,71,0.08)", marginBottom: 24 
                    }}>
                        <span style={{ fontSize: 11, color: "var(--color-accent, #E8FF47)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                            Pricing
                        </span>
                    </div>
                    <h2 style={{ 
                        fontSize: "clamp(32px, 4vw, 48px)", fontWeight: 700, color: "var(--color-text-1, #F5F5F5)", 
                        marginBottom: 16, letterSpacing: "-0.03em", lineHeight: 1.2 
                    }}>
                        Simple, honest pricing
                    </h2>
                    <p style={{ 
                        color: "var(--color-text-2, #888888)", maxWidth: 600, margin: "0 auto", fontSize: 16, lineHeight: 1.7 
                    }}>
                        Start free and scale as you grow. No hidden fees.
                    </p>

                    {/* Billing Toggle */}
                    <div style={{ display: "inline-flex", gap: 4, background: "var(--color-surface, #111111)", borderRadius: 50, padding: 4, border: "1px solid var(--color-border, #222222)", marginTop: 32 }}>
                        <button 
                            onClick={() => setAnnual(false)} 
                            onKeyDown={(e) => {
                                if (e.key === "Enter" || e.key === " ") {
                                    e.preventDefault();
                                    setAnnual(false);
                                }
                            }}
                            aria-pressed={!annual}
                            role="switch"
                            style={{
                                padding: "10px 24px", borderRadius: 50, fontSize: 14, fontWeight: 500, border: "none", cursor: "pointer",
                                background: !annual ? "var(--color-accent, #E8FF47)" : "transparent", 
                                color: !annual ? "#0A0A0A" : "var(--color-text-2, #888888)",
                                transition: "all 0.2s ease",
                            }}
                        >
                            Monthly
                        </button>
                        <button 
                            onClick={() => setAnnual(true)} 
                            onKeyDown={(e) => {
                                if (e.key === "Enter" || e.key === " ") {
                                    e.preventDefault();
                                    setAnnual(true);
                                }
                            }}
                            aria-pressed={annual}
                            role="switch"
                            style={{
                                padding: "10px 24px", borderRadius: 50, fontSize: 14, fontWeight: 500, border: "none", cursor: "pointer",
                                background: annual ? "var(--color-accent, #E8FF47)" : "transparent", 
                                color: annual ? "#0A0A0A" : "var(--color-text-2, #888888)",
                                transition: "all 0.2s ease",
                            }}
                        >
                            Annual <span style={{ color: "var(--color-ok, #22C55E)", fontSize: 12, marginLeft: 4, fontWeight: 600 }}>−25%</span>
                        </button>
                    </div>
                </div>

                {/* 3-Column Pricing Grid */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24, alignItems: "start" }}>
                    {tiers.map((t) => (
                        <div 
                            key={t.name} 
                            style={{
                                ...cardBase,
                                ...(t.popular ? { 
                                    borderColor: "var(--color-accent, #E8FF47)", 
                                    background: "rgba(232,255,71,0.04)",
                                    transform: "scale(1.05)",
                                    zIndex: 2,
                                    boxShadow: "0 20px 40px -12px rgba(0,0,0,0.5)"
                                } : {}),
                            }}
                            onMouseEnter={(e) => {
                                if (!t.popular) {
                                    e.currentTarget.style.transform = "translateY(-4px)";
                                    e.currentTarget.style.borderColor = "var(--color-border-hi, #333333)";
                                    e.currentTarget.style.background = "var(--color-surface-2, #1A1A1A)";
                                }
                            }}
                            onMouseLeave={(e) => {
                                if (!t.popular) {
                                    e.currentTarget.style.transform = "translateY(0)";
                                    e.currentTarget.style.borderColor = "var(--color-border, #222222)";
                                    e.currentTarget.style.background = "var(--color-surface, #111111)";
                                }
                            }}
                            onMouseDown={(e) => {
                                if (!t.popular) {
                                    e.currentTarget.style.transform = "translateY(-2px)";
                                }
                            }}
                            onMouseUp={(e) => {
                                if (!t.popular) {
                                    e.currentTarget.style.transform = "translateY(-4px)";
                                }
                            }}
                        >
                            {t.popular && (
                                <span style={{
                                    position: "absolute", top: -12, left: "50%", transform: "translateX(-50%)",
                                    background: "var(--color-accent, #E8FF47)", color: "#0A0A0A", fontSize: 11, fontWeight: 700,
                                    padding: "4px 16px", borderRadius: 50, letterSpacing: "0.03em",
                                }}>BEST VALUE</span>
                            )}

                            {/* Plan Name */}
                            <div style={{ fontSize: 20, fontWeight: 700, color: "var(--color-text-1, #F5F5F5)", marginBottom: 12 }}>
                                {t.name}
                            </div>

                            {/* Price */}
                            <div style={{ marginBottom: 24 }}>
                                {t.monthly === null ? (
                                    <span style={{ fontSize: 42, fontWeight: 800, color: "var(--color-text-1, #F5F5F5)", letterSpacing: "-0.02em" }}>Custom</span>
                                ) : t.monthly === 0 ? (
                                    <span style={{ fontSize: 42, fontWeight: 800, color: "var(--color-text-1, #F5F5F5)", letterSpacing: "-0.02em" }}>Free</span>
                                ) : (
                                    <>
                                        <span style={{ fontSize: 42, fontWeight: 800, color: "var(--color-text-1, #F5F5F5)", letterSpacing: "-0.02em" }}>${annual ? t.annually : t.monthly}</span>
                                        <span style={{ fontSize: 16, color: "var(--color-text-3, #555555)", marginLeft: 4 }}>/mo</span>
                                    </>
                                )}
                            </div>

                            {/* Description */}
                            <p style={{ fontSize: 14, color: "var(--color-text-2, #888888)", lineHeight: 1.6, marginBottom: 24 }}>
                                {t.popular ? "Perfect for growing teams that need advanced analytics." : 
                                 t.name === "Starter" ? "Great for getting started with supply chain analytics." :
                                 "For large organizations with custom requirements."}
                            </p>

                            {/* Features */}
                            <ul style={{ listStyle: "none", padding: 0, margin: 0, flex: 1, marginBottom: 32, display: "flex", flexDirection: "column", gap: 12 }}>
                                {t.features.map((f) => (
                                    <li key={f} style={{ fontSize: 14, color: "var(--color-text-2, #888888)", display: "flex", alignItems: "flex-start", gap: 12, lineHeight: 1.5 }}>
                                        <span style={{ 
                                            color: "var(--color-accent, #E8FF47)", fontSize: 16, lineHeight: "20px", flexShrink: 0 
                                        }}>✓</span>
                                        {f}
                                    </li>
                                ))}
                            </ul>

                            {/* CTA Button */}
                            <Link href="/login" style={{ textDecoration: "none" }}>
                                <Btn 
                                    variant={t.popular ? "primary" : "outline"} 
                                    size="lg" 
                                    style={{ width: "100%", borderRadius: 12 }}
                                >
                                    {t.cta}
                                </Btn>
                            </Link>
                        </div>
                    ))}
                </div>
            </div>

            {/* Responsive */}
            <style>{`
                @media (max-width: 968px) {
                    section > div > div[style*="gridTemplateColumns"] {
                        grid-template-columns: 1fr !important;
                        gap: 24px !important;
                    }
                    section > div > div[style*="gridTemplateColumns"] > div[style*="scale(1.05)"] {
                        transform: scale(1) !important;
                        box-shadow: none !important;
                    }
                }
            `}</style>
        </section>
    );
};

// ── Footer ──
export const Footer = () => (
    <footer style={{ background: "var(--color-bg, #0A0A0A)", borderTop: "1px solid var(--color-border, #222222)", padding: "48px 24px" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: 24 }}>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <span style={{ fontSize: 20, fontWeight: 700, color: "var(--color-text-1, #F5F5F5)", letterSpacing: "-0.02em" }}>
                    NEXUS<span style={{ color: "var(--color-accent, #E8FF47)" }}>.</span>
                </span>
                <p style={{ fontSize: 13, color: "var(--color-text-3, #555555)" }}>© 2026 Nexus AI. All rights reserved.</p>
            </div>
            <div style={{ display: "flex", gap: 32 }}>
                {["Privacy", "Terms", "Status"].map((l) => (
                    <a 
                        key={l} 
                        href="#" 
                        style={{ fontSize: 14, color: "var(--color-text-2, #888888)", textDecoration: "none", transition: "color 0.2s ease", fontWeight: 500 }}
                        onMouseEnter={(e) => (e.currentTarget.style.color = "var(--color-text-1, #F5F5F5)")}
                        onMouseLeave={(e) => (e.currentTarget.style.color = "var(--color-text-2, #888888)")}
                    >
                        {l}
                    </a>
                ))}
            </div>
        </div>
    </footer>
);

// ── Exported layout wrapper ──
export default function MarketingPage({ children }: { children?: React.ReactNode }) {
    return (
        <main style={{ minHeight: "100vh", background: "#000", color: "#fff" }}>
            <Navigation />
            <Hero />
            {children}
        </main>
    );
}
