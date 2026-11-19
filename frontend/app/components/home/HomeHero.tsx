"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
    animate,
    motion,
    useReducedMotion,
    type Variants,
} from "framer-motion";
import {
    Activity,
    ArrowUpRight,
    Lock,
    Menu,
    Network,
    ShieldCheck,
    TrendingUp,
    X,
} from "lucide-react";
import "./home.css";

/* ── Routes: verify these against your app/ folder ── */
const ROUTES = {
    platform: "/",
    riskEngine: "/causal",
    topology: "/graph",
    mitigation: "/mitigation",
    controlTower: "/control-tower",
    launch: "/pipeline",
    demo: "/dashboard",
    terms: "/terms",
    privacy: "/privacy",
} as const;

const NAV = [
    { label: "Platform", href: ROUTES.platform },
    { label: "Risk Engine", href: ROUTES.riskEngine },
    { label: "Topology", href: ROUTES.topology },
    { label: "Mitigation", href: ROUTES.mitigation },
    { label: "Control Tower", href: ROUTES.controlTower },
];

/* ── Panel data: sample values, labelled as such. Wire to your API later. ── */
const SNAPSHOT = {
    nodes: 3,
    nodeNames: "Titan Logistics, Vanguard Assemblies, Delta Port",
    exposure: 1420000,
    exposureNote: "94.2% mitigation coverage via autonomous rerouting",
};

const CAPABILITIES = [
    { icon: Network, title: "Graph Topology", text: "Directed graph with degree centrality and cascade blast-radius modeling." },
    { icon: Activity, title: "Anomaly Detection", text: "Multi-feature Isolation Forest isolating delay, volume, and cost outliers in-process." },
    { icon: TrendingUp, title: "Holt-Winters Forecast", text: "Additive trend and quarterly seasonality with P10/P90 confidence bounds." },
    { icon: ShieldCheck, title: "Mitigation Agent", text: "6-node LangGraph workflow with deterministic fallback and human approval gate." },
    { icon: Lock, title: "Enterprise Security", text: "Strict RBAC enforcement, rotating JWT tokens, and untrusted CSV prompt sanitization." },
];

const EASE = [0.16, 1, 0.3, 1] as const;

const container: Variants = {
    hidden: {},
    show: { transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
};
const rise: Variants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.7, ease: EASE } },
};

/* Stable formatters (defined outside components on purpose) */
const fmtInt = (v: number) => Math.round(v).toString();
const fmtUsd = (v: number) => "$" + Math.round(v).toLocaleString("en-US");

function CountUp({ to, format }: { to: number; format: (v: number) => string }) {
    const reduce = useReducedMotion();
    const ref = useRef<HTMLSpanElement>(null);

    useEffect(() => {
        const node = ref.current;
        if (!node) return;
        if (reduce) {
            node.textContent = format(to);
            return;
        }
        const controls = animate(0, to, {
            duration: 1.4,
            delay: 0.5,
            ease: EASE,
            onUpdate: (v) => {
                node.textContent = format(v);
            },
        });
        return () => controls.stop();
    }, [to, format, reduce]);

    return <span ref={ref}>{format(to)}</span>;
}

export default function HomeHero() {
    const reduce = useReducedMotion();
    const [menuOpen, setMenuOpen] = useState(false);

    useEffect(() => {
        if (!menuOpen) return;
        const onKey = (e: KeyboardEvent) => {
            if (e.key === "Escape") setMenuOpen(false);
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [menuOpen]);

    const initial = reduce ? false : "hidden";

    return (
        <main className="nx-home">
            <div className="nx-frame">
                <div className="nx-bg" aria-hidden="true" />
                <div className="nx-ribs" aria-hidden="true" />
                <div className="nx-sheen" aria-hidden="true" />

                {/* ── Navigation ── */}
                <header className="nx-nav" data-testid="navigation">
                    <Link href="/" className="nx-brand" aria-label="NEXUS home">
                        <span className="nx-brand-name">NEXUS</span>
                        <span className="nx-brand-ver">V2.4</span>
                    </Link>

                    <nav className="nx-pill" aria-label="Primary">
                        {NAV.map((item, i) => (
                            <Link
                                key={item.label}
                                href={item.href}
                                aria-current={i === 0 ? "page" : undefined}
                            >
                                {item.label}
                            </Link>
                        ))}
                    </nav>

                    <div className="nx-actions">
                        <Link href={ROUTES.demo} className="nx-circle" aria-label="Open dashboard">
                            <ArrowUpRight size={18} strokeWidth={1.5} />
                        </Link>
                        <button
                            type="button"
                            className="nx-circle"
                            aria-label={menuOpen ? "Close menu" : "Open menu"}
                            aria-expanded={menuOpen}
                            aria-controls="nx-menu"
                            onClick={() => setMenuOpen((o) => !o)}
                        >
                            {menuOpen ? <X size={18} strokeWidth={1.5} /> : <Menu size={18} strokeWidth={1.5} />}
                        </button>
                    </div>

                    {menuOpen && (
                        <div id="nx-menu" className="nx-menu" role="menu">
                            {NAV.map((item) => (
                                <Link key={item.label} href={item.href} role="menuitem" onClick={() => setMenuOpen(false)}>
                                    {item.label}
                                </Link>
                            ))}
                        </div>
                    )}
                </header>

                {/* ── Hero ── */}
                <motion.section
                    className="nx-hero"
                    data-testid="hero"
                    variants={container}
                    initial={initial}
                    animate="show"
                >
                    <motion.aside className="nx-panel" variants={rise} aria-label="Sample risk snapshot">
                        <p className="nx-panel-kicker">
                            <span className="nx-dot" aria-hidden="true" />
                            Sample dataset // demo mode
                        </p>
                        <div className="nx-panel-row">
                            <p className="nx-label">Critical bottleneck exposure</p>
                            <p className="nx-value"><CountUp to={SNAPSHOT.nodes} format={fmtInt} /> Active Nodes</p>
                            <p className="nx-note">{SNAPSHOT.nodeNames}</p>
                        </div>
                        <div className="nx-panel-row">
                            <p className="nx-label">Estimated disruption exposure</p>
                            <p className="nx-value"><CountUp to={SNAPSHOT.exposure} format={fmtUsd} /></p>
                            <p className="nx-note">{SNAPSHOT.exposureNote}</p>
                        </div>
                    </motion.aside>

                    <div className="nx-copy">
                        <h1 className="nx-title">
                            <motion.span className="nx-line" variants={rise}>Autonomous risk intelligence</motion.span>
                            <motion.span className="nx-line" variants={rise}>for complex supply chains.</motion.span>
                        </h1>
                        <motion.p className="nx-lede" variants={rise}>
                            Ingest multi-tier supplier data, detect cascading failure modes, and
                            generate human-in-the-loop mitigation plans before production halts.
                        </motion.p>
                    </div>

                    <motion.div className="nx-ctas" variants={rise}>
                        <Link href={ROUTES.launch} className="nx-btn nx-btn-primary">Launch Pipeline</Link>
                        <Link href={ROUTES.demo} className="nx-btn nx-btn-ghost">Explore Live Demo</Link>
                    </motion.div>
                </motion.section>

                {/* ── Capability strip ── */}
                <motion.ul
                    className="nx-strip"
                    variants={container}
                    initial={initial}
                    animate="show"
                >
                    {CAPABILITIES.map(({ icon: Icon, title, text }) => (
                        <motion.li key={title} variants={rise}>
                            <Icon size={18} strokeWidth={1.4} aria-hidden="true" />
                            <h2>{title}</h2>
                            <p>{text}</p>
                        </motion.li>
                    ))}
                </motion.ul>

                <footer className="nx-footer">
                    <span>© {new Date().getFullYear()} NEXUS</span>
                    <span className="nx-footer-links">
                        <Link href={ROUTES.terms}>Terms of Service</Link>
                        <Link href={ROUTES.privacy}>Privacy Policy</Link>
                    </span>
                </footer>
            </div>
        </main>
    );
}