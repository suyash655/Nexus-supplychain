"use client";

import React from "react";

export interface TierBadgeProps {
  tier: string;
}

export function TierBadge({ tier }: TierBadgeProps) {
  const t = tier?.toLowerCase();
  const style =
    t === "critical"
      ? {
          background: "rgba(255,68,68,0.08)",
          color: "#FF4444",
          border: "1px solid rgba(255,68,68,0.18)",
        }
      : t === "elevated"
      ? {
          background: "rgba(255,149,0,0.08)",
          color: "#FF9500",
          border: "1px solid rgba(255,149,0,0.18)",
        }
      : {
          background: "rgba(34,197,94,0.08)",
          color: "#22C55E",
          border: "1px solid rgba(34,197,94,0.18)",
        };

  return (
    <span
      style={{
        ...style,
        padding: "2px 8px",
        borderRadius: 999,
        fontSize: 11,
        fontWeight: 500,
      }}
    >
      {tier}
    </span>
  );
}
