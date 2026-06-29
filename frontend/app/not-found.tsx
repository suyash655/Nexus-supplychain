import Link from "next/link";

export default function NotFound() {
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
      <div style={{ textAlign: "center", maxWidth: 480, padding: 40 }}>
        <div
          style={{
            fontSize: 80,
            fontWeight: 900,
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            lineHeight: 1,
            marginBottom: 16,
          }}
        >
          404
        </div>

        <h1
          style={{
            fontSize: 24,
            fontWeight: 800,
            marginBottom: 8,
            letterSpacing: "-0.02em",
          }}
        >
          Page not found
        </h1>

        <p
          style={{
            fontSize: 14,
            color: "#94a3b8",
            lineHeight: 1.6,
            marginBottom: 32,
          }}
        >
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>

        <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
          <Link
            href="/dashboard"
            style={{
              padding: "12px 24px",
              background: "linear-gradient(135deg, #6366f1, #4f46e5)",
              color: "#fff",
              border: "none",
              borderRadius: 12,
              fontSize: 14,
              fontWeight: 700,
              textDecoration: "none",
              boxShadow: "0 0 20px rgba(99, 102, 241, 0.2)",
            }}
          >
            Go to Dashboard
          </Link>

          <Link
            href="/"
            style={{
              padding: "12px 24px",
              background: "rgba(255,255,255,0.05)",
              color: "#94a3b8",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 12,
              fontSize: 14,
              fontWeight: 600,
              textDecoration: "none",
            }}
          >
            Home
          </Link>
        </div>
      </div>
    </div>
  );
}
