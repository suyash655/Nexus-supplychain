"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Menu, X, ChevronRight, FolderUp, Search, Brain, Zap, Shield, Microscope, GitBranch, BarChart3, Dna, Link2, Globe } from "lucide-react";

/* ─────────────────────────────────────────────────────────
   NEXUS Marketing Layer — Full landing page components
   Uses INLINE STYLES to match existing codebase pattern.
   No Tailwind dependency — works with vanilla CSS globals.
   ───────────────────────────────────────────────────────── */

// ── Inline Button ──
interface BtnProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "ghost" | "gradient";
    size?: "sm" | "md" | "lg";
}

const Btn: React.FC<BtnProps> = ({ variant = "primary", size = "md", style, children, ...props }) => {
    const base: React.CSSProperties = {
        display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 8,
        fontWeight: 600, borderRadius: 10, border: "none", cursor: "pointer",
        transition: "all 0.2s ease", fontFamily: "var(--font-sans, Inter, sans-serif)",
        textDecoration: "none", whiteSpace: "nowrap",
    };

    const sizes: Record<string, React.CSSProperties> = {
        sm: { height: 36, padding: "0 16px", fontSize: 13 },
        md: { height: 42, padding: "0 20px", fontSize: 14 },
        lg: { height: 48, padding: "0 28px", fontSize: 15 },
    };

    const variants: Record<string, React.CSSProperties> = {
        primary: { background: "#fff", color: "#000" },
        secondary: { background: "rgba(255,255,255,0.08)", color: "#fff", border: "1px solid rgba(255,255,255,0.12)" },
        ghost: { background: "transparent", color: "rgba(255,255,255,0.7)", border: "1px solid rgba(255,255,255,0.15)" },
        gradient: {
            background: "linear-gradient(180deg, #fff 0%, rgba(255,255,255,0.85) 100%)",
            color: "#000", boxShadow: "0 4px 24px rgba(255,255,255,0.15)",
        },
    };

    return (
        <button style={{ ...base, ...sizes[size], ...variants[variant], ...style }} {...props}>
            {children}
        </button>
    );
};

// ── Navigation ──
export const Navigation = React.memo(() => {
    const [open, setOpen] = React.useState(false);

    const navStyle: React.CSSProperties = {
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 100,
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        background: "rgba(0,0,0,0.85)", backdropFilter: "blur(16px)",
    };

    const navLinks = [
        { href: "#how-it-works", label: "How it Works" },
        { href: "#features", label: "Features" },
        { href: "#pricing", label: "Pricing" },
    ];

    return (
        <header style={navStyle}>
            <nav style={{ maxWidth: 1200, margin: "0 auto", padding: "16px 24px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <Link href="/" style={{ fontSize: 22, fontWeight: 700, color: "#fff", textDecoration: "none", letterSpacing: "-0.03em" }}>
                    NEXUS<span style={{ color: "#6366f1" }}>.</span>
                </Link>

                {/* Desktop nav */}
                <div style={{ display: "flex", gap: 32, position: "absolute", left: "50%", transform: "translateX(-50%)" }} className="nav-desktop-links">
                    {navLinks.map((l) => (
                        <a key={l.href} href={l.href} style={{ fontSize: 13, color: "rgba(255,255,255,0.5)", textDecoration: "none", transition: "color 0.2s" }}
                            onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
                            onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(255,255,255,0.5)")}>
                            {l.label}
                        </a>
                    ))}
                </div>

                {/* Desktop CTA */}
                <div style={{ display: "flex", gap: 10 }} className="nav-desktop-cta">
                    <Link href="/login" style={{ textDecoration: "none" }}>
                        <Btn variant="ghost" size="sm">Sign in</Btn>
                    </Link>
                    <Link href="/login" style={{ textDecoration: "none" }}>
                        <Btn variant="primary" size="sm">Get Started <ArrowRight size={14} /></Btn>
                    </Link>
                </div>

                {/* Mobile toggle */}
                <button onClick={() => setOpen(!open)} style={{ display: "none", background: "none", border: "none", color: "#fff", cursor: "pointer" }} className="nav-mobile-toggle">
                    {open ? <X size={24} /> : <Menu size={24} />}
                </button>
            </nav>

            {/* Mobile menu */}
            {open && (
                <div style={{ background: "rgba(0,0,0,0.95)", backdropFilter: "blur(16px)", borderTop: "1px solid rgba(255,255,255,0.06)", padding: "16px 24px" }} className="nav-mobile-menu">
                    {navLinks.map((l) => (
                        <a key={l.href} href={l.href} onClick={() => setOpen(false)}
                            style={{ display: "block", padding: "12px 0", fontSize: 14, color: "rgba(255,255,255,0.6)", textDecoration: "none" }}>
                            {l.label}
                        </a>
                    ))}
                    <div style={{ borderTop: "1px solid rgba(255,255,255,0.08)", paddingTop: 16, marginTop: 8, display: "flex", flexDirection: "column", gap: 8 }}>
                        <Link href="/login" style={{ textDecoration: "none" }}><Btn variant="ghost" size="sm" style={{ width: "100%" }}>Sign in</Btn></Link>
                        <Link href="/login" style={{ textDecoration: "none" }}><Btn variant="primary" size="sm" style={{ width: "100%" }}>Get Started</Btn></Link>
                    </div>
                </div>
            )}

            {/* Responsive CSS */}
            <style>{`
                @media (max-width: 768px) {
                    .nav-desktop-links, .nav-desktop-cta { display: none !important; }
                    .nav-mobile-toggle { display: block !important; }
                }
                @media (min-width: 769px) {
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
        <section style={{ position: "relative", minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-start", padding: "120px 24px 60px", background: "#000", overflow: "hidden" }}>
            {/* Background glow */}
            <div style={{ position: "absolute", top: "20%", left: "50%", transform: "translateX(-50%)", width: 700, height: 700, borderRadius: "50%", background: "radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%)", pointerEvents: "none" }} />
            <div style={{ position: "absolute", top: "40%", left: "30%", width: 400, height: 400, borderRadius: "50%", background: "radial-gradient(circle, rgba(6,182,212,0.06) 0%, transparent 70%)", pointerEvents: "none" }} />

            {/* Announcement badge */}
            <div style={{ marginBottom: 32, display: "inline-flex", alignItems: "center", gap: 10, padding: "8px 18px", borderRadius: 50, border: "1px solid rgba(255,255,255,0.12)", background: "rgba(255,255,255,0.03)", backdropFilter: "blur(8px)", position: "relative", zIndex: 1 }}>
                <span style={{ fontSize: 12, color: "rgba(255,255,255,0.5)" }}>Now with AI-powered Causal Genome Engine</span>
                <a href="#features" style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 12, color: "#818cf8", textDecoration: "none" }}>
                    Explore <ChevronRight size={12} />
                </a>
            </div>

            {/* Headline */}
            <h1 style={{
                fontSize: "clamp(36px, 5vw, 64px)", fontWeight: 600, textAlign: "center",
                maxWidth: 800, lineHeight: 1.1, marginBottom: 20, position: "relative", zIndex: 1,
                background: "linear-gradient(180deg, #ffffff 20%, rgba(255,255,255,0.55) 100%)",
                WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
                backgroundClip: "text", letterSpacing: "-0.04em",
            }}>
                Supply Chain Intelligence{"\n"}that thinks ahead of risk
            </h1>

            <p style={{ fontSize: "clamp(14px, 1.2vw, 16px)", textAlign: "center", maxWidth: 560, color: "rgba(255,255,255,0.4)", lineHeight: 1.7, marginBottom: 40, position: "relative", zIndex: 1 }}>
                Upload your supply data. NEXUS maps your entire network, predicts cascading failures,
                and surfaces AI-driven counterfactuals — before disruptions hit your bottom line.
            </p>

            {/* CTAs */}
            <div style={{ display: "flex", gap: 14, position: "relative", zIndex: 1, marginBottom: 64, flexWrap: "wrap", justifyContent: "center" }}>
                <Link href="/login" style={{ textDecoration: "none" }}>
                    <Btn variant="gradient" size="lg">
                        Start for free <ArrowRight size={16} />
                    </Btn>
                </Link>
                <Link href="/dashboard" style={{ textDecoration: "none" }}>
                    <Btn variant="secondary" size="lg">Try the demo</Btn>
                </Link>
                <a href="#how-it-works" style={{ textDecoration: "none" }}>
                    <Btn variant="ghost" size="lg">See how it works</Btn>
                </a>
            </div>

            {/* Dashboard preview */}
            <div style={{ width: "100%", maxWidth: 1000, position: "relative", zIndex: 1 }}>
                {/* Glow */}
                <div style={{ position: "absolute", top: -40, left: "50%", transform: "translateX(-50%)", width: "70%", height: 80, background: "radial-gradient(ellipse, rgba(99,102,241,0.25) 0%, transparent 70%)", borderRadius: 999, pointerEvents: "none" }} />

                <div style={{ position: "relative", borderRadius: 16, border: "1px solid rgba(255,255,255,0.08)", overflow: "hidden", boxShadow: "0 32px 80px rgba(0,0,0,0.6)" }}>
                    {/* Browser chrome */}
                    <div style={{ background: "rgba(17,17,17,0.9)", borderBottom: "1px solid rgba(255,255,255,0.06)", padding: "12px 16px", display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "rgba(239,68,68,0.7)" }} />
                        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "rgba(245,158,11,0.7)" }} />
                        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "rgba(34,197,94,0.7)" }} />
                        <div style={{ marginLeft: 16, flex: 1, background: "rgba(255,255,255,0.04)", borderRadius: 6, padding: "5px 12px", fontSize: 12, color: "rgba(255,255,255,0.3)" }}>
                            nexus.app/dashboard
                        </div>
                    </div>

                    {/* Dashboard mock */}
                    <div style={{ background: "#0a0a0f", padding: 20, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
                        {/* Top KPI */}
                        {[
                            { label: "Overall Risk Score", value: "78.4", color: "#ef4444", sub: "+5.2% this week" },
                            { label: "Active Suppliers", value: "142", color: "#facc15", sub: "12 at elevated risk" },
                            { label: "Anomalies Detected", value: "23", color: "#38bdf8", sub: "via Isolation Forest" },
                        ].map((k) => (
                            <div key={k.label} style={{ background: "rgba(255,255,255,0.02)", borderRadius: 12, padding: 16, border: "1px solid rgba(255,255,255,0.05)" }}>
                                <div style={{ fontSize: 11, color: "rgba(255,255,255,0.35)", fontWeight: 500, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.05em" }}>{k.label}</div>
                                <div style={{ fontSize: 28, fontWeight: 700, color: k.color, letterSpacing: "-0.02em" }}>{k.value}</div>
                                <div style={{ fontSize: 11, color: "rgba(255,255,255,0.25)", marginTop: 4 }}>{k.sub}</div>
                            </div>
                        ))}

                        {/* Bar chart */}
                        <div style={{ gridColumn: "span 2", background: "rgba(255,255,255,0.02)", borderRadius: 12, padding: 16, border: "1px solid rgba(255,255,255,0.05)" }}>
                            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.35)", fontWeight: 500, marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>Risk by Supplier (top 8)</div>
                            <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 80 }}>
                                {[82, 74, 68, 65, 58, 51, 43, 31].map((h, i) => (
                                    <div key={i} style={{ flex: 1, borderRadius: "4px 4px 0 0", height: `${h}%`, background: h > 70 ? "#ef4444" : h > 50 ? "#f59e0b" : "#34d399", opacity: 0.7, transition: "height 0.4s ease" }} />
                                ))}
                            </div>
                        </div>

                        {/* Resilience */}
                        <div style={{ background: "rgba(255,255,255,0.02)", borderRadius: 12, padding: 16, border: "1px solid rgba(255,255,255,0.05)", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.35)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em" }}>Network Resilience</div>
                            <div style={{ fontSize: 36, fontWeight: 700, color: "#a78bfa", letterSpacing: "-0.02em" }}>67.2</div>
                            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.25)" }}>Structural Robustness: Medium</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Responsive */}
            <style>{`
                @media (max-width: 768px) {
                    section > div[style*="gridTemplateColumns"] { grid-template-columns: 1fr !important; }
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
        <section id="how-it-works" style={{ background: "#000", padding: "96px 24px", borderTop: "1px solid rgba(255,255,255,0.04)" }}>
            <div style={{ maxWidth: 1000, margin: "0 auto" }}>
                <div style={{ textAlign: "center", marginBottom: 64 }}>
                    <h2 style={{
                        fontSize: "clamp(28px, 3.5vw, 40px)", fontWeight: 600, color: "#fff",
                        marginBottom: 12, letterSpacing: "-0.03em",
                    }}>
                        From raw data to decisions in minutes
                    </h2>
                    <p style={{ color: "rgba(255,255,255,0.4)", maxWidth: 480, margin: "0 auto", fontSize: 14, lineHeight: 1.6 }}>
                        No data science degree required. NEXUS handles the heavy lifting.
                    </p>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 32 }}>
                    {steps.map((s, i) => (
                        <div key={s.num} style={{ position: "relative" }}>
                            <div style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(99,102,241,0.1)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 16 }}>
                                <s.Icon size={22} color="#818cf8" />
                            </div>
                            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.2)", fontWeight: 700, marginBottom: 8, letterSpacing: "0.1em" }}>STEP {s.num}</div>
                            <h3 style={{ color: "#fff", fontWeight: 600, fontSize: 16, marginBottom: 8 }}>{s.title}</h3>
                            <p style={{ color: "rgba(255,255,255,0.4)", fontSize: 13, lineHeight: 1.6 }}>{s.desc}</p>
                            {i < steps.length - 1 && (
                                <div style={{ position: "absolute", top: 24, right: -16, width: 8, height: 1, background: "rgba(255,255,255,0.1)" }} className="step-connector" />
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

// ── Features Grid ──
export const FeaturesGrid = () => {
    const features = [
        { Icon: Shield, title: "Composite Risk Scoring", desc: "Multi-factor 0–100 risk scores using delay, cost, quality, and consistency metrics.", tag: "ML" },
        { Icon: Microscope, title: "Anomaly Detection", desc: "Isolation Forest + Z-score + IQR: three methods, one unified anomaly pipeline.", tag: "ML" },
        { Icon: GitBranch, title: "Graph Intelligence", desc: "Force-directed network topology with PageRank, betweenness, and cascade simulation.", tag: "Graph" },
        { Icon: BarChart3, title: "Time-Series Forecast", desc: "Holt-Winters triple exponential smoothing for delay and cost prediction.", tag: "Forecast" },
        { Icon: Dna, title: "Explainable AI", desc: "Feature importance, counterfactual explanations, and actionable recommendations.", tag: "XAI" },
        { Icon: Link2, title: "Data Connectors", desc: "CSV, S3, PostgreSQL, REST API — real-time ingestion with auto-validation.", tag: "Ingestion" },
        { Icon: Brain, title: "Causal Genome", desc: "Root-cause identification via structural causal inference, beyond correlation.", tag: "Causal" },
        { Icon: Globe, title: "World Event Monitor", desc: "Geopolitical signal integration for proactive supply chain resilience.", tag: "Intel" },
    ];

    return (
        <section id="features" style={{ background: "#000", padding: "96px 24px", borderTop: "1px solid rgba(255,255,255,0.04)" }}>
            <div style={{ maxWidth: 1100, margin: "0 auto" }}>
                <div style={{ textAlign: "center", marginBottom: 64 }}>
                    <h2 style={{ fontSize: "clamp(28px, 3.5vw, 40px)", fontWeight: 600, color: "#fff", marginBottom: 12, letterSpacing: "-0.03em" }}>
                        Every analytical skill, one platform
                    </h2>
                    <p style={{ color: "rgba(255,255,255,0.4)", maxWidth: 520, margin: "0 auto", fontSize: 14, lineHeight: 1.6 }}>
                        A complete data analytics toolkit for supply chain intelligence.
                    </p>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
                    {features.map((f) => (
                        <div key={f.title} style={{
                            background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
                            borderRadius: 14, padding: 24, transition: "all 0.3s ease", cursor: "default",
                        }}
                            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.04)"; e.currentTarget.style.borderColor = "rgba(99,102,241,0.3)"; e.currentTarget.style.transform = "translateY(-2px)"; }}
                            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.02)"; e.currentTarget.style.borderColor = "rgba(255,255,255,0.06)"; e.currentTarget.style.transform = "translateY(0)"; }}
                        >
                            <div style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(99,102,241,0.1)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 12 }}>
                                <f.Icon size={22} color="#818cf8" />
                            </div>
                            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                                <h3 style={{ fontSize: 15, fontWeight: 600, color: "#fff" }}>{f.title}</h3>
                                <span style={{ fontSize: 10, fontWeight: 600, color: "#6366f1", background: "rgba(99,102,241,0.12)", padding: "2px 8px", borderRadius: 50, letterSpacing: "0.05em" }}>{f.tag}</span>
                            </div>
                            <p style={{ fontSize: 13, color: "rgba(255,255,255,0.4)", lineHeight: 1.6 }}>{f.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

// ── Pricing ──
export const Pricing = () => {
    const [annual, setAnnual] = React.useState(false);

    const tiers = [
        {
            name: "Starter", monthly: 0, annually: 0, color: "#e2e8f0",
            features: ["Up to 10,000 rows", "3 data connectors", "Basic risk scores", "CSV export", "Email support"],
            cta: "Start free", popular: false,
        },
        {
            name: "Pro", monthly: 79, annually: 59, color: "#818cf8", popular: true,
            features: ["Up to 500,000 rows", "All connectors (S3, SQL, API)", "Full ML suite + XAI", "Graph Intelligence", "Priority support + Slack"],
            cta: "Start Pro trial",
        },
        {
            name: "Enterprise", monthly: null, annually: null, color: "#f59e0b", popular: false,
            features: ["Unlimited rows & seats", "Custom connectors", "Dedicated infra & SLA", "RBAC + Audit Logs", "Custom training + onboarding"],
            cta: "Contact us",
        },
    ];

    const cardBase: React.CSSProperties = {
        position: "relative", borderRadius: 16, padding: 28, display: "flex", flexDirection: "column",
        border: "1px solid rgba(255,255,255,0.08)", background: "rgba(255,255,255,0.02)", transition: "all 0.3s ease",
    };

    return (
        <section id="pricing" style={{ background: "#000", padding: "96px 24px", borderTop: "1px solid rgba(255,255,255,0.04)" }}>
            <div style={{ maxWidth: 1000, margin: "0 auto" }}>
                <div style={{ textAlign: "center", marginBottom: 48 }}>
                    <h2 style={{ fontSize: "clamp(28px, 3.5vw, 40px)", fontWeight: 600, color: "#fff", marginBottom: 16, letterSpacing: "-0.03em" }}>
                        Simple, honest pricing
                    </h2>

                    {/* Billing toggle */}
                    <div style={{ display: "inline-flex", gap: 4, background: "rgba(255,255,255,0.04)", borderRadius: 50, padding: 4 }}>
                        <button onClick={() => setAnnual(false)} style={{
                            padding: "8px 20px", borderRadius: 50, fontSize: 13, fontWeight: 500, border: "none", cursor: "pointer",
                            background: !annual ? "#fff" : "transparent", color: !annual ? "#000" : "rgba(255,255,255,0.4)",
                            transition: "all 0.2s ease",
                        }}>Monthly</button>
                        <button onClick={() => setAnnual(true)} style={{
                            padding: "8px 20px", borderRadius: 50, fontSize: 13, fontWeight: 500, border: "none", cursor: "pointer",
                            background: annual ? "#fff" : "transparent", color: annual ? "#000" : "rgba(255,255,255,0.4)",
                            transition: "all 0.2s ease",
                        }}>Annual <span style={{ color: "#22c55e", fontSize: 11, marginLeft: 4 }}>−25%</span></button>
                    </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
                    {tiers.map((t) => (
                        <div key={t.name} style={{
                            ...cardBase,
                            ...(t.popular ? { borderColor: "rgba(99,102,241,0.4)", background: "rgba(99,102,241,0.04)" } : {}),
                        }}>
                            {t.popular && (
                                <span style={{
                                    position: "absolute", top: -12, left: "50%", transform: "translateX(-50%)",
                                    background: "#6366f1", color: "#fff", fontSize: 11, fontWeight: 600,
                                    padding: "4px 14px", borderRadius: 50, letterSpacing: "0.03em",
                                }}>Most Popular</span>
                            )}

                            <div style={{ fontSize: 18, fontWeight: 600, color: t.color, marginBottom: 8 }}>{t.name}</div>

                            <div style={{ marginBottom: 20 }}>
                                {t.monthly === null ? (
                                    <span style={{ fontSize: 36, fontWeight: 700, color: "#fff" }}>Custom</span>
                                ) : t.monthly === 0 ? (
                                    <span style={{ fontSize: 36, fontWeight: 700, color: "#fff" }}>Free</span>
                                ) : (
                                    <>
                                        <span style={{ fontSize: 36, fontWeight: 700, color: "#fff" }}>${annual ? t.annually : t.monthly}</span>
                                        <span style={{ fontSize: 14, color: "rgba(255,255,255,0.3)", marginLeft: 4 }}>/mo</span>
                                    </>
                                )}
                            </div>

                            <ul style={{ listStyle: "none", padding: 0, margin: 0, flex: 1, marginBottom: 24 }}>
                                {t.features.map((f) => (
                                    <li key={f} style={{ fontSize: 13, color: "rgba(255,255,255,0.5)", padding: "6px 0", display: "flex", alignItems: "flex-start", gap: 8 }}>
                                        <span style={{ color: "#22c55e", fontSize: 14, lineHeight: "20px" }}>✓</span>{f}
                                    </li>
                                ))}
                            </ul>

                            <Link href="/login" style={{ textDecoration: "none" }}>
                                <Btn variant={t.popular ? "primary" : "secondary"} size="md" style={{ width: "100%", borderRadius: 12 }}>
                                    {t.cta}
                                </Btn>
                            </Link>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

// ── Footer ──
export const Footer = () => (
    <footer style={{ background: "#000", borderTop: "1px solid rgba(255,255,255,0.04)", padding: "48px 24px" }}>
        <div style={{ maxWidth: 1000, margin: "0 auto", display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: 16 }}>
            <span style={{ fontSize: 18, fontWeight: 700, color: "#fff" }}>NEXUS<span style={{ color: "#6366f1" }}>.</span></span>
            <p style={{ fontSize: 12, color: "rgba(255,255,255,0.2)" }}>© 2026 Nexus AI. All rights reserved.</p>
            <div style={{ display: "flex", gap: 24 }}>
                {["Privacy", "Terms", "Status"].map((l) => (
                    <a key={l} href="#" style={{ fontSize: 12, color: "rgba(255,255,255,0.3)", textDecoration: "none", transition: "color 0.2s" }}
                        onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
                        onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(255,255,255,0.3)")}>
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
