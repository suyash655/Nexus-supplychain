"use client";

import React from "react";

export interface KpiCardProps {
  label: string;
  value: string | number;
  delta?: string | null;
  deltaDir?: "up" | "down" | "neutral";
  sub?: string;
  onClick?: () => void;
}

export function KpiCard({ label, value, delta, deltaDir, sub, onClick }: KpiCardProps) {
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
        transition: "border-color 120ms cubic-bezier(0.16,1,0.3,1), transform 120ms cubic-bezier(0.16,1,0.3,1), box-shadow 120ms cubic-bezier(0.16,1,0.3,1)",
        cursor: onClick ? "pointer" : "default",
        position: "relative",
        overflow: "hidden",
      }}
      onClick={onClick}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = "var(--color-border-hi)";
        if (onClick) {
          e.currentTarget.style.transform = "translateY(-2px)";
          e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)";
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "var(--color-border)";
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "none";
      }}
      onMouseDown={(e) => {
        if (onClick) {
          e.currentTarget.style.transform = "translateY(0)";
        }
      }}
      onMouseUp={(e) => {
        if (onClick) {
          e.currentTarget.style.transform = "translateY(-2px)";
        }
      }}
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
          transition: "color 0.2s ease",
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
            transition: "opacity 0.2s ease",
          }}
        >
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: dotColor,
              flexShrink: 0,
              transition: "transform 0.2s ease",
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
