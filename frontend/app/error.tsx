"use client";

import { useEffect } from "react";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("NEXUS Error Boundary caught:", error);
  }, [error]);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#030712",
        color: "#f1f5f9",
        fontFamily: "Inter, system-ui, sans-serif",
      }}
    >
      <div
        style={{
          textAlign: "center",
          maxWidth: 480,
          padding: 40,
        }}
      >
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: 16,
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.2)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 24px",
            fontSize: 28,
          }}
        >
          ⚠
        </div>

        <h1
          style={{
            fontSize: 24,
            fontWeight: 800,
            marginBottom: 8,
            letterSpacing: "-0.02em",
          }}
        >
          Something went wrong
        </h1>

        <p
          style={{
            fontSize: 14,
            color: "#94a3b8",
            lineHeight: 1.6,
            marginBottom: 8,
          }}
        >
          An unexpected error occurred while loading this page.
        </p>

        <p
          style={{
            fontSize: 12,
            color: "#64748b",
            marginBottom: 28,
            fontFamily: "monospace",
            background: "rgba(255,255,255,0.03)",
            padding: "8px 16px",
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.06)",
            wordBreak: "break-word",
          }}
        >
          {error.message || "Unknown error"}
        </p>

        <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
          <button
            onClick={reset}
            style={{
              padding: "12px 24px",
              background: "linear-gradient(135deg, #6366f1, #4f46e5)",
              color: "#fff",
              border: "none",
              borderRadius: 12,
              fontSize: 14,
              fontWeight: 700,
              cursor: "pointer",
              boxShadow: "0 0 20px rgba(99, 102, 241, 0.2)",
            }}
          >
            Try Again
          </button>

          <a
            href="/dashboard"
            style={{
              padding: "12px 24px",
              background: "rgba(255,255,255,0.05)",
              color: "#94a3b8",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 12,
              fontSize: 14,
              fontWeight: 600,
              textDecoration: "none",
              display: "inline-flex",
              alignItems: "center",
            }}
          >
            Go to Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
