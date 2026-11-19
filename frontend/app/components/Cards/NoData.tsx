"use client";

import React from "react";
import Link from "next/link";

export interface NoDataProps {
  msg?: string;
  height?: number | string;
  actionText?: string;
  actionHref?: string;
  icon?: React.ReactNode;
}

export function NoData({ msg, height = 160, actionText, actionHref, icon }: NoDataProps) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 12,
        minHeight: height,
        fontSize: 13,
        color: "var(--color-text-3)",
        padding: 20,
      }}
    >
      {icon || (
        <svg
          width="44"
          height="44"
          viewBox="0 0 48 48"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
          style={{ opacity: 0.35, color: "var(--color-text-3)" }}
        >
          <rect x="8" y="8" width="32" height="32" rx="6" stroke="currentColor" strokeWidth="1.5" />
          <line x1="16" y1="18" x2="32" y2="18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="16" y1="24" x2="32" y2="24" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="16" y1="30" x2="24" y2="30" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      )}
      <div style={{ textAlign: "center", lineHeight: 1.5 }}>
        {msg ?? "No data available yet."}
      </div>
      {actionText && actionHref && (
        <Link href={actionHref} className="btn btn-secondary btn-sm">
          {actionText}
        </Link>
      )}
    </div>
  );
}