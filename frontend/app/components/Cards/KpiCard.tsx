"use client";

import React from "react";

export interface KpiCardProps {
  label: string;
  value: string | number;
  delta?: string | null;
  deltaDir?: "up" | "down" | "neutral";
  sub?: string;
}

export function KpiCard({ label, value, delta, deltaDir, sub }: KpiCardProps) {
  const dotColor =
    deltaDir === "up"
      ? "#22C55E"
      : deltaDir === "down"
      ? "#FF4444"
      : "#F59E0B";

  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: 6,
        padding: 20,
        transition: "border-color 120ms cubic-bezier(0.16,1,0.3,1)",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--color-border-hi)")}
      onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--color-border)")}
    >
      <div
        style={{
          fontSize: 11,
          fontWeight: 500,
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          color: "var(--color-text-2)",
          marginBottom: 8,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 32,
          fontWeight: 700,
          color: "var(--color-text-1)",
          lineHeight: 1.1,
          letterSpacing: "-0.02em",
        }}
      >
        {value}
      </div>
      {delta && (
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 4,
            marginTop: 8,
            fontSize: 11,
            fontWeight: 500,
            color: dotColor,
          }}
        >
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: dotColor,
              flexShrink: 0,
            }}
          />
          {delta}
        </div>
      )}
      {sub && (
        <div style={{ marginTop: 8, fontSize: 11, color: "var(--color-text-3)" }}>
          {sub}
        </div>
      )}
    </div>
  );
}
