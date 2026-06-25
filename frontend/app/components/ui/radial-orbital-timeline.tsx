"use client";
import { useState, useEffect, useRef } from "react";
import { ArrowRight, Link as LinkIcon, Zap } from "lucide-react";

interface TimelineItem {
    id: number;
    title: string;
    date: string;
    content: string;
    category: string;
    icon: React.ElementType;
    relatedIds: number[];
    status: "completed" | "in-progress" | "pending";
    energy: number;
}

interface RadialOrbitalTimelineProps {
    timelineData: TimelineItem[];
}

const STATUS_COLORS: Record<string, { bg: string; color: string; border: string; label: string }> = {
    completed:   { bg: "var(--color-primary-light)", color: "var(--color-primary)", border: "var(--color-primary)", label: "COMPLETE" },
    "in-progress": { bg: "rgba(6,182,212,0.12)", color: "#06b6d4", border: "#06b6d4", label: "IN PROGRESS" },
    pending:     { bg: "rgba(148,163,184,0.08)", color: "var(--color-text-muted)", border: "var(--color-border)", label: "PENDING" },
};

const NODE_COLORS: Record<string, { bg: string; border: string; icon: string }> = {
    completed:   { bg: "var(--color-primary)", border: "var(--color-primary)", icon: "#fff" },
    "in-progress": { bg: "rgba(6,182,212,0.2)", border: "#06b6d4", icon: "#06b6d4" },
    pending:     { bg: "var(--color-surface-2)", border: "var(--color-border)", icon: "var(--color-text-muted)" },
};

export default function RadialOrbitalTimeline({ timelineData }: RadialOrbitalTimelineProps) {
    const [expandedId, setExpandedId] = useState<number | null>(null);
    const [rotationAngle, setRotationAngle] = useState<number>(0);
    const [autoRotate, setAutoRotate] = useState<boolean>(true);
    const [pulseEffect, setPulseEffect] = useState<Record<number, boolean>>({});
    const containerRef = useRef<HTMLDivElement>(null);

    const handleContainerClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (e.target === containerRef.current) {
            setExpandedId(null);
            setPulseEffect({});
            setAutoRotate(true);
        }
    };

    const toggleItem = (id: number) => {
        if (expandedId === id) {
            setExpandedId(null);
            setPulseEffect({});
            setAutoRotate(true);
        } else {
            setExpandedId(id);
            setAutoRotate(false);
            const item = timelineData.find(i => i.id === id);
            const pulse: Record<number, boolean> = {};
            item?.relatedIds.forEach(rId => { pulse[rId] = true; });
            setPulseEffect(pulse);
            const idx = timelineData.findIndex(i => i.id === id);
            setRotationAngle(270 - (idx / timelineData.length) * 360);
        }
    };

    useEffect(() => {
        if (!autoRotate) return;
        const t = setInterval(() => {
            setRotationAngle(prev => Number(((prev + 0.3) % 360).toFixed(3)));
        }, 50);
        return () => clearInterval(t);
    }, [autoRotate]);

    const calculateNodePosition = (index: number, total: number) => {
        const angle = ((index / total) * 360 + rotationAngle) % 360;
        const radius = 165;
        const radian = (angle * Math.PI) / 180;
        const x = radius * Math.cos(radian);
        const y = radius * Math.sin(radian);
        const zIndex = Math.round(100 + 50 * Math.cos(radian));
        const opacity = Math.max(0.45, Math.min(1, 0.45 + 0.55 * ((1 + Math.sin(radian)) / 2)));
        return { x, y, zIndex, opacity };
    };

    const getRelatedItems = (itemId: number) =>
        timelineData.find(i => i.id === itemId)?.relatedIds ?? [];

    const isRelatedToActive = (itemId: number): boolean => {
        if (!expandedId) return false;
        return getRelatedItems(expandedId).includes(itemId);
    };

    return (
        <div
            ref={containerRef}
            onClick={handleContainerClick}
            style={{
                width: "100%",
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                position: "relative",
                background: "transparent",
                overflow: "hidden",
            }}
        >
            {/* Orbit ring */}
            <div style={{
                position: "absolute",
                width: 330,
                height: 330,
                borderRadius: "50%",
                border: "1px solid var(--color-border-subtle)",
                pointerEvents: "none",
            }} />

            {/* Central orb */}
            <div style={{
                position: "absolute",
                width: 48,
                height: 48,
                borderRadius: "50%",
                background: "linear-gradient(135deg, var(--color-primary), var(--color-accent))",
                boxShadow: "0 0 32px rgba(99,102,241,0.4)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                zIndex: 10,
                pointerEvents: "none",
            }}>
                <div style={{
                    width: 20,
                    height: 20,
                    borderRadius: "50%",
                    background: "rgba(255,255,255,0.85)",
                }} />
                {/* Ping rings */}
                <div style={{
                    position: "absolute",
                    width: 60,
                    height: 60,
                    borderRadius: "50%",
                    border: "1px solid rgba(99,102,241,0.3)",
                    animation: "ping 2s ease-out infinite",
                    opacity: 0.6,
                }} />
                <div style={{
                    position: "absolute",
                    width: 72,
                    height: 72,
                    borderRadius: "50%",
                    border: "1px solid rgba(99,102,241,0.15)",
                    animation: "ping 2s ease-out infinite",
                    animationDelay: "0.6s",
                    opacity: 0.4,
                }} />
            </div>

            {/* Nodes */}
            {timelineData.map((item, index) => {
                const pos = calculateNodePosition(index, timelineData.length);
                const isExpanded = expandedId === item.id;
                const isRelated = isRelatedToActive(item.id);
                const isPulsing = pulseEffect[item.id];
                const Icon = item.icon;
                const nodeStyle = NODE_COLORS[item.status];
                const statusStyle = STATUS_COLORS[item.status];

                return (
                    <div
                        key={item.id}
                        style={{
                            position: "absolute",
                            transform: `translate(${pos.x}px, ${pos.y}px)`,
                            zIndex: isExpanded ? 200 : pos.zIndex,
                            opacity: isExpanded ? 1 : pos.opacity,
                            transition: "opacity 0.4s ease, transform 0.7s ease",
                            cursor: "pointer",
                        }}
                        onClick={e => { e.stopPropagation(); toggleItem(item.id); }}
                    >
                        {/* Energy glow */}
                        {isPulsing && (
                            <div style={{
                                position: "absolute",
                                inset: -8,
                                borderRadius: "50%",
                                background: "radial-gradient(circle, rgba(99,102,241,0.25) 0%, transparent 70%)",
                                animation: "pulse-glow 1.5s ease-in-out infinite",
                            }} />
                        )}

                        {/* Node circle */}
                        <div style={{
                            width: isExpanded ? 48 : 38,
                            height: isExpanded ? 48 : 38,
                            borderRadius: "50%",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            border: `2px solid ${isExpanded ? "var(--color-primary)" : isRelated ? "#06b6d4" : nodeStyle.border}`,
                            background: isExpanded ? "var(--color-primary)" : isRelated ? "rgba(6,182,212,0.15)" : nodeStyle.bg,
                            color: isExpanded ? "#fff" : nodeStyle.icon,
                            transition: "all 0.3s ease",
                            boxShadow: isExpanded ? "0 0 20px rgba(99,102,241,0.5)" : isRelated ? "0 0 12px rgba(6,182,212,0.4)" : "none",
                        }}>
                            <Icon size={15} />
                        </div>

                        {/* Label */}
                        <div style={{
                            position: "absolute",
                            top: 46,
                            left: "50%",
                            transform: `translateX(-50%) scale(${isExpanded ? 1.1 : 1})`,
                            whiteSpace: "nowrap",
                            fontSize: 10,
                            fontWeight: 600,
                            letterSpacing: "0.08em",
                            textTransform: "uppercase",
                            color: isExpanded ? "var(--color-text)" : "var(--color-text-muted)",
                            fontFamily: "var(--font-sans)",
                            transition: "all 0.3s ease",
                            pointerEvents: "none",
                        }}>
                            {item.title}
                        </div>

                        {/* Expanded card — anchored safely */}
                        {isExpanded && (
                            <div
                                style={{
                                    position: "absolute",
                                    top: 60,
                                    left: "50%",
                                    transform: "translateX(-50%)",
                                    width: 240,
                                    background: "var(--color-surface)",
                                    border: "1px solid var(--color-border)",
                                    borderRadius: 12,
                                    boxShadow: "0 20px 40px rgba(0,0,0,0.4), 0 0 0 1px var(--color-primary-glow)",
                                    zIndex: 300,
                                    overflow: "hidden",
                                    fontFamily: "var(--font-sans)",
                                }}
                                onClick={e => e.stopPropagation()}
                            >
                                {/* Connector line */}
                                <div style={{
                                    position: "absolute",
                                    top: -8,
                                    left: "50%",
                                    transform: "translateX(-50%)",
                                    width: 1,
                                    height: 8,
                                    background: "var(--color-border)",
                                }} />

                                {/* Card Header */}
                                <div style={{ padding: "14px 16px 10px" }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                                        <span style={{
                                            display: "inline-flex",
                                            alignItems: "center",
                                            padding: "2px 8px",
                                            borderRadius: "var(--radius-full)",
                                            fontSize: 10,
                                            fontWeight: 700,
                                            letterSpacing: "0.06em",
                                            background: statusStyle.bg,
                                            color: statusStyle.color,
                                            border: `1px solid ${statusStyle.border}`,
                                        }}>
                                            {statusStyle.label}
                                        </span>
                                        <span style={{
                                            fontSize: 10,
                                            fontFamily: "var(--font-mono)",
                                            color: "var(--color-text-muted)",
                                        }}>
                                            {item.date}
                                        </span>
                                    </div>
                                    <div style={{
                                        fontSize: 13,
                                        fontWeight: 700,
                                        color: "var(--color-text)",
                                        fontFamily: "var(--font-display)",
                                    }}>
                                        {item.title}
                                    </div>
                                </div>

                                {/* Card Body */}
                                <div style={{ padding: "0 16px 14px", borderTop: "1px solid var(--color-border-subtle)" }}>
                                    <p style={{
                                        fontSize: 12,
                                        color: "var(--color-text-secondary)",
                                        lineHeight: 1.6,
                                        marginTop: 10,
                                        marginBottom: 12,
                                    }}>
                                        {item.content}
                                    </p>

                                    {/* Impact bar */}
                                    <div style={{ marginBottom: 12 }}>
                                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                                            <span style={{ fontSize: 10, color: "var(--color-text-muted)", display: "flex", alignItems: "center", gap: 4 }}>
                                                <Zap size={9} /> Impact Level
                                            </span>
                                            <span style={{ fontSize: 10, fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}>
                                                {item.energy}%
                                            </span>
                                        </div>
                                        <div style={{
                                            height: 4,
                                            borderRadius: "var(--radius-full)",
                                            background: "var(--color-surface-2)",
                                            overflow: "hidden",
                                        }}>
                                            <div style={{
                                                height: "100%",
                                                width: `${item.energy}%`,
                                                background: "linear-gradient(90deg, var(--color-primary), var(--color-accent))",
                                                borderRadius: "var(--radius-full)",
                                            }} />
                                        </div>
                                    </div>

                                    {/* Related nodes */}
                                    {item.relatedIds.length > 0 && (
                                        <div>
                                            <div style={{
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 4,
                                                marginBottom: 6,
                                            }}>
                                                <LinkIcon size={9} color="var(--color-text-muted)" />
                                                <span style={{
                                                    fontSize: 9,
                                                    fontWeight: 600,
                                                    textTransform: "uppercase",
                                                    letterSpacing: "0.08em",
                                                    color: "var(--color-text-muted)",
                                                }}>
                                                    Connected
                                                </span>
                                            </div>
                                            <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                                                {item.relatedIds.map(relId => {
                                                    const rel = timelineData.find(i => i.id === relId);
                                                    return (
                                                        <button
                                                            key={relId}
                                                            onClick={e => { e.stopPropagation(); toggleItem(relId); }}
                                                            style={{
                                                                display: "inline-flex",
                                                                alignItems: "center",
                                                                gap: 4,
                                                                padding: "3px 8px",
                                                                borderRadius: 6,
                                                                border: "1px solid var(--color-border)",
                                                                background: "var(--color-surface-2)",
                                                                color: "var(--color-text-secondary)",
                                                                fontSize: 10,
                                                                fontWeight: 600,
                                                                cursor: "pointer",
                                                                fontFamily: "var(--font-sans)",
                                                                transition: "all 0.15s ease",
                                                            }}
                                                            onMouseOver={e => {
                                                                (e.currentTarget as HTMLElement).style.borderColor = "var(--color-primary)";
                                                                (e.currentTarget as HTMLElement).style.color = "var(--color-primary)";
                                                            }}
                                                            onMouseOut={e => {
                                                                (e.currentTarget as HTMLElement).style.borderColor = "var(--color-border)";
                                                                (e.currentTarget as HTMLElement).style.color = "var(--color-text-secondary)";
                                                            }}
                                                        >
                                                            {rel?.title}
                                                            <ArrowRight size={8} />
                                                        </button>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
