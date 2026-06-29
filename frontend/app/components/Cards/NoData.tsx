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
        height,
        fontSize: 13,
        color: "var(--color-text-3)",
        padding: 20,
        transition: "opacity 0.3s ease",
      }}
    >
      {icon || (
        <div 
          style={{ 
            fontSize: 32, 
            opacity: 0.4,
            marginBottom: 8,
            transition: "transform 0.3s ease"
          }}
        >
          ⊘
        </div>
      )}
      <div style={{ textAlign: "center", lineHeight: 1.5 }}>
        {msg ?? "No data. Agents are monitoring."}
      </div>
      {actionText && actionHref && (
        <Link 
          href={actionHref} 
          className="btn btn-secondary btn-sm"
          style={{
            transition: "all 0.2s ease",
          }}
        >
          {actionText}
        </Link>
      )}
    </div>
  );
}
