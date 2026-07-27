"use client";

import React, { useMemo, useState, useEffect } from "react";
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

const formatTimestamp = (timestamp: string | Date | null): string => {
  if (!timestamp) return "";
  const date = typeof timestamp === "string" ? new Date(timestamp) : timestamp;
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
  return date.toLocaleDateString();
};

export const KpiCard = React.memo(function KpiCard({ label, value, delta, deltaDir, sub, onClick, loading, noData, timestamp, isLive }: KpiCardProps) {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isHovered, setIsHovered] = useState(false);

  // Move useMemo before conditional returns to maintain hook order
  const dotColor = useMemo(() =>
    deltaDir === "up"
      ? "#22C55E"
      : deltaDir === "down"
      ? "#FF4444"
      : "#FF9500", [deltaDir]);

  const freshnessText = formatTimestamp(timestamp);

  useEffect(() => {
    if (isLive) {
      const interval = setInterval(() => setCurrentTime(new Date()), 60000); // Update every minute
      return () => clearInterval(interval);
    }
  }, [isLive]);

  if (loading) {
    return <SkeletonKPI />;
  }

  if (noData) {
    return (
      <div
        className="kpi-card"
        style={{
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: 6,
          padding: 20,
          cursor: onClick ? "pointer" : "default",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          minHeight: 96,
        }}
        onClick={onClick}
      >
        <div style={{ fontSize: 13, color: "var(--color-text-3)", fontStyle: "italic" }}>
          No data yet
        </div>
      </div>
    );
  }

  return (
    <div
      className="kpi-card"
      style={{
        background: isHovered && onClick ? "var(--color-surface-2)" : "var(--color-surface)",
        border: isHovered && onClick ? "1px solid var(--color-accent)" : "1px solid var(--color-border)",
        borderRadius: 6,
        padding: 20,
        cursor: onClick ? "pointer" : "default",
        position: "relative",
        overflow: "hidden",
        willChange: "transform",
        transition: "all 0.2s ease",
      }}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Live pulse indicator */}
      {isLive && (
        <div style={{
          position: "absolute",
          top: 16,
          right: 16,
          display: "flex",
          alignItems: "center",
          gap: 4,
        }}>
          <div style={{
            width: 6,
            height: 6,
            borderRadius: "50%",
            background: "var(--color-ok)",
            animation: "pulse 2s infinite",
          }} />
          <span style={{ fontSize: 10, color: "var(--color-ok)", fontWeight: 500 }}>LIVE</span>
        </div>
      )}

      {/* Freshness timestamp */}
      {freshnessText && !isLive && (
        <div style={{
          position: "absolute",
          top: 16,
          right: 16,
          fontSize: 10,
          color: "var(--color-text-3)",
          fontWeight: 400,
        }}>
          {freshnessText}
        </div>
      )}

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

      {/* Click affordance indicator */}
      {onClick && (
        <div style={{
          position: "absolute",
          bottom: 16,
          right: 16,
          opacity: isHovered ? 1 : 0,
          transition: "opacity 0.2s ease",
        }}>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4.5 4.5L7.5 7.5M7.5 4.5L4.5 7.5" stroke="var(--color-text-3)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      )}
    </div>
  );
});
