"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { CSSProperties, ReactNode } from "react";

const EASE = [0.16, 1, 0.3, 1] as const;

export type Tone = "info" | "warn" | "danger" | "success" | "neutral";

/* Fade-up entrance that triggers once as the element scrolls into view */
export function Reveal({
    children,
    delay = 0,
    className,
    style,
}: {
    children: ReactNode;
    delay?: number;
    className?: string;
    style?: CSSProperties;
}) {
    const reduce = useReducedMotion();
    return (
        <motion.div
            className={className}
            style={{ height: "100%", minWidth: 0, ...style }}
            initial={reduce ? false : { opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "0px 0px -40px 0px" }}
            transition={{ duration: 0.6, delay, ease: EASE }}
        >
            {children}
        </motion.div>
    );
}

export function PageHeader({
    eyebrow,
    title,
    subtitle,
    actions,
}: {
    eyebrow?: string;
    title: string;
    subtitle?: string;
    actions?: ReactNode;
}) {
    return (
        <Reveal style={{ height: "auto" }}>
            <div className="page-header" style={{ alignItems: "flex-start", flexWrap: "wrap" }}>
                <div style={{ minWidth: 0 }}>
                    {eyebrow && (
                        <div className="text-micro" style={{ marginBottom: 6 }}>
                            {eyebrow}
                        </div>
                    )}
                    <h1 className="page-title">{title}</h1>
                    {subtitle && <p className="page-subtitle">{subtitle}</p>}
                </div>
                {actions && <div className="toolbar" style={{ justifyContent: "flex-end" }}>{actions}</div>}
            </div>
        </Reveal>
    );
}

export function Panel({
    title,
    action,
    children,
    flush,
    delay = 0,
    style,
}: {
    title?: string;
    action?: ReactNode;
    children: ReactNode;
    flush?: boolean;
    delay?: number;
    style?: CSSProperties;
}) {
    return (
        <Reveal delay={delay}>
            <section className={`panel ${flush ? "panel-flush" : ""}`} style={style} aria-label={title}>
                {(title || action) && (
                    <header className="panel-head">
                        {title ? <h2 className="panel-title">{title}</h2> : <span />}
                        {action}
                    </header>
                )}
                <div className={flush ? undefined : "panel-pad"}>{children}</div>
            </section>
        </Reveal>
    );
}

export function Notice({
    tone = "info",
    title,
    children,
    action,
}: {
    tone?: Exclude<Tone, "neutral">;
    title: string;
    children?: ReactNode;
    action?: ReactNode;
}) {
    return (
        <div className="notice" data-tone={tone} role={tone === "danger" ? "alert" : "status"}>
            <div>
                <span className="n-title">{title}</span>
                {children}
            </div>
            {action}
        </div>
    );
}

export function Pill({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
    return (
        <span className="pill" data-tone={tone}>
            {children}
        </span>
    );
}

export function Segmented<T extends string>({
    value,
    onChange,
    options,
    label,
}: {
    value: T;
    onChange: (v: T) => void;
    options: { value: T; label: string }[];
    label: string;
}) {
    return (
        <div className="seg" role="group" aria-label={label}>
            {options.map((o) => (
                <button
                    key={o.value}
                    type="button"
                    aria-pressed={value === o.value}
                    onClick={() => onChange(o.value)}
                >
                    {o.label}
                </button>
            ))}
        </div>
    );
}

/* Progress bar that fills in on mount */
export function Meter({
    value,
    color,
    delay = 0,
    wide,
}: {
    value: number;
    color: string;
    delay?: number;
    wide?: boolean;
}) {
    const reduce = useReducedMotion();
    const pct = Math.max(0, Math.min(100, Number.isFinite(value) ? value : 0));
    return (
        <div className={`meter ${wide ? "meter-wide" : ""}`} role="presentation">
            <motion.div
                style={{ background: color }}
                initial={reduce ? false : { width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 0.8, delay, ease: EASE }}
            />
        </div>
    );
}