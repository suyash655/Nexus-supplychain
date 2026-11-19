"use client";

import React, { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { animate, useReducedMotion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import { SkeletonKPI } from "../feedback/Skeleton";

export interface KpiCardProps {
  label: string;
  value: string | number;
  delta?: string | null;
  deltaDir?: "up" | "down" | "neutral";
  sub?: string;
  onClick?: () => void;
  loading?: boolean;
  noData?: boolean;
  timestamp?: string | Date | null;
  isLive?: boolean;
}

const useIsoLayoutEffect = typeof window !== "undefined" ? useLayoutEffect : useEffect;

const formatTimestamp = (timestamp: string | Date | null): string => {
  if (!timestamp) return "";
  const date = typeof timestamp === "string" ? new Date(timestamp) : timestamp;
  const diffMins = Math.floor((Date.now() - date.getTime()) / 60000);
  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
  return date.toLocaleDateString();
};

/* "2,847" / "4.7d" / "94%" / "₹1.2L" -> { prefix, target, suffix, decimals, grouped } */
function parseValue(text: string) {
  const m = text.match(/^([^\d-]*)(-?[\d,]*\.?\d+)(.*)$/);
  if (!m) return null;
  const raw = m[2];
  const target = parseFloat(raw.replace(/,/g, ""));
  if (!Number.isFinite(target)) return null;
  return {
    prefix: m[1],
    suffix: m[3],
    target,
    decimals: raw.includes(".") ? raw.split(".")[1].length : 0,
    grouped: raw.includes(","),
  };
}

/* Counts up once when the value appears or changes. The final frame is always the original text. */
function AnimatedValue({ value }: { value: string | number }) {
  const text = String(value);
  const reduce = useReducedMotion();
  const ref = useRef<HTMLSpanElement>(null);

  useIsoLayoutEffect(() => {
    const node = ref.current;
    if (!node) return;
    node.textContent = text;

    const parsed = parseValue(text);
    if (!parsed || reduce) return;

    const fmt = (n: number) =>
      parsed.prefix +
      (parsed.grouped
        ? n.toLocaleString("en-US", {
          minimumFractionDigits: parsed.decimals,
          maximumFractionDigits: parsed.decimals,
        })
        : n.toFixed(parsed.decimals)) +
      parsed.suffix;

    node.textContent = fmt(0);
    const controls = animate(0, parsed.target, {
      duration: 1,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => {
        node.textContent = fmt(v);
      },
      onComplete: () => {
        node.textContent = text;
      },
    });

    return () => {
      controls.stop();
      node.textContent = text;
    };
  }, [text, reduce]);

  return <span ref={ref}>{text}</span>;
}

export const KpiCard = React.memo(function KpiCard({
  label,
  value,
  delta,
  deltaDir,
  sub,
  onClick,
  loading,
  noData,
  timestamp,
  isLive,
}: KpiCardProps) {
  const [, setTick] = useState(0);

  // Hooks stay above every conditional return to keep hook order stable
  const deltaColor = useMemo(
    () =>
      deltaDir === "up"
        ? "var(--color-ok)"
        : deltaDir === "down"
          ? "var(--color-danger)"
          : "var(--color-text-2)",
    [deltaDir]
  );

  // Re-render once a minute so "5m ago" labels stay accurate
  useEffect(() => {
    if (!timestamp) return;
    const id = setInterval(() => setTick((t) => t + 1), 60000);
    return () => clearInterval(id);
  }, [timestamp]);

  if (loading) return <SkeletonKPI />;

  const interactive = typeof onClick === "function";
  const interactiveProps = interactive
    ? {
      role: "button" as const,
      tabIndex: 0,
      onClick,
      onKeyDown: (e: React.KeyboardEvent) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick?.();
        }
      },
    }
    : {};

  if (noData) {
    return (
      <div
        className="kpi-card"
        style={{ alignItems: "center", justifyContent: "center", cursor: interactive ? "pointer" : "default" }}
        {...interactiveProps}
      >
        <div style={{ fontSize: 13, color: "var(--color-text-3)" }}>No data yet</div>
      </div>
    );
  }

  const freshnessText = formatTimestamp(timestamp ?? null);
  const hasBadge = !!isLive || !!freshnessText;

  return (
    <div
      className="kpi-card"
      style={{ position: "relative", cursor: interactive ? "pointer" : "default" }}
      {...interactiveProps}
    >
      {isLive ? (
        <div style={{ position: "absolute", top: 16, right: 16, display: "flex", alignItems: "center", gap: 6 }}>
          <span
            aria-hidden="true"
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: "var(--color-ok)",
              animation: "pulse 2s ease-in-out infinite",
            }}
          />
          <span style={{ fontSize: 10, letterSpacing: "0.1em", color: "var(--color-ok)", fontWeight: 500 }}>
            LIVE
          </span>
        </div>
      ) : freshnessText ? (
        <div style={{ position: "absolute", top: 16, right: 16, fontSize: 10, color: "var(--color-text-3)" }}>
          {freshnessText}
        </div>
      ) : null}

      <div>
        <div className="kpi-label" style={{ paddingRight: hasBadge ? 64 : 0 }}>
          {label}
        </div>
        <div className="kpi-value">
          <AnimatedValue value={value} />
        </div>
      </div>

      {(delta || sub) && (
        <div style={{ marginTop: 12, paddingRight: interactive ? 20 : 0 }}>
          {delta && (
            <div className="kpi-delta" style={{ color: deltaColor, marginTop: 0 }}>
              <span
                aria-hidden="true"
                style={{ width: 6, height: 6, borderRadius: "50%", background: deltaColor, flexShrink: 0 }}
              />
              {delta}
            </div>
          )}
          {sub && (
            <div
              style={{
                marginTop: delta ? 6 : 0,
                fontSize: 12,
                color: "var(--color-text-3)",
                overflowWrap: "anywhere",
              }}
            >
              {sub}
            </div>
          )}
        </div>
      )}

      {interactive && (
        <ArrowUpRight
          className="kpi-go"
          size={14}
          aria-hidden="true"
          style={{ position: "absolute", right: 16, bottom: 16, color: "var(--color-text-3)" }}
        />
      )}
    </div>
  );
});