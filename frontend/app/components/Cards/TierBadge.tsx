"use client";

import React from "react";

export interface TierBadgeProps {
  tier: string;
}

const KNOWN = ["critical", "catastrophic", "severe", "elevated"];

export function TierBadge({ tier }: TierBadgeProps) {
  const t = tier?.toLowerCase();
  const variant = KNOWN.includes(t) ? `risk-${t}` : "risk-stable";

  return <span className={`risk-badge ${variant}`}>{tier}</span>;
}