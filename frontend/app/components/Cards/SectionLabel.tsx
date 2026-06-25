"use client";

import React from "react";

export interface SectionLabelProps {
  children: React.ReactNode;
}

export function SectionLabel({ children }: SectionLabelProps) {
  return (
    <div
      style={{
        fontSize: 11,
        fontWeight: 500,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        color: "var(--color-text-2)",
        marginBottom: 12,
      }}
    >
      {children}
    </div>
  );
}
