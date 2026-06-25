"use client";

import React from "react";
import Link from "next/link";

export interface NoDataProps {
  msg?: string;
  height?: number | string;
  actionText?: string;
  actionHref?: string;
}

export function NoData({ msg, height = 160, actionText, actionHref }: NoDataProps) {
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
      }}
    >
      <div>{msg ?? "No data. Agents are monitoring."}</div>
      {actionText && actionHref && (
        <Link href={actionHref} className="btn btn-secondary btn-sm">
          {actionText}
        </Link>
      )}
    </div>
  );
}
