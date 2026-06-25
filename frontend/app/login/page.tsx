"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("email", email);
      formData.append("password", password);

      if (mode === "register") {
        formData.append("username", username);
        formData.append("full_name", fullName);
      }

      const res = await fetch(`${API_BASE}/auth/${mode}`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (data.error || !res.ok) {
        setError(data.detail || data.error || "Authentication failed");
        return;
      }

      // Store token in localStorage AND cookie (for middleware auth check)
      localStorage.setItem("nexus_token", data.access_token);
      localStorage.setItem("nexus_user", JSON.stringify(data.user));
      document.cookie = `nexus_token=${data.access_token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;

      router.push("/dashboard");
    } catch {
      setError("Connection failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoAccess = () => {
    // Set a demo token so middleware allows access
    document.cookie = `nexus_token=demo; path=/; max-age=${60 * 60 * 24}; SameSite=Lax`;
    router.push("/dashboard");
  };

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "#030712",
      position: "relative",
      overflow: "hidden",
    }}>
      {/* Ambient glow effects */}
      <div style={{
        position: "absolute", top: "10%", left: "20%", width: 400, height: 400,
        background: "radial-gradient(circle, rgba(6, 182, 212, 0.08), transparent 70%)",
        borderRadius: "50%", filter: "blur(80px)", pointerEvents: "none",
      }} />
      <div style={{
        position: "absolute", bottom: "20%", right: "15%", width: 350, height: 350,
        background: "radial-gradient(circle, rgba(236, 72, 153, 0.06), transparent 70%)",
        borderRadius: "50%", filter: "blur(80px)", pointerEvents: "none",
      }} />

      <div style={{
        width: 440, padding: 40,
        background: "rgba(15, 23, 42, 0.6)",
        border: "1px solid rgba(148, 163, 184, 0.1)",
        borderRadius: 20,
        backdropFilter: "blur(24px)",
        position: "relative", zIndex: 1,
      }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            width: 56, height: 56,
            background: "linear-gradient(135deg, #06b6d4, #ec4899)",
            borderRadius: 16, marginBottom: 16,
            fontSize: 24, fontWeight: 900, color: "#fff",
            boxShadow: "0 0 30px rgba(6, 182, 212, 0.3)",
          }}>
            N
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 800, color: "#f1f5f9", margin: 0, letterSpacing: "-0.02em" }}>
            NEXUS
          </h1>
          <p style={{ fontSize: 13, color: "#64748b", marginTop: 4 }}>
            Autonomous Data Intelligence Platform
          </p>
        </div>

        {/* Tab switcher */}
        <div style={{
          display: "flex", gap: 0, marginBottom: 28,
          background: "rgba(255,255,255,0.03)", borderRadius: 12,
          border: "1px solid rgba(148, 163, 184, 0.08)", padding: 4,
        }}>
          {(["login", "register"] as const).map(m => (
            <button
              key={m}
              onClick={() => { setMode(m); setError(""); }}
              style={{
                flex: 1, padding: "10px 0", borderRadius: 8, border: "none",
                background: mode === m ? "rgba(6, 182, 212, 0.15)" : "transparent",
                color: mode === m ? "#06b6d4" : "#64748b",
                fontWeight: 600, fontSize: 13, cursor: "pointer",
                transition: "all 0.2s",
                textTransform: "uppercase", letterSpacing: "0.05em",
              }}
            >
              {m === "login" ? "Sign In" : "Create Account"}
            </button>
          ))}
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {mode === "register" && (
            <>
              <InputField label="Full Name" value={fullName} onChange={setFullName} placeholder="John Doe" />
              <InputField label="Username" value={username} onChange={setUsername} placeholder="johndoe" />
            </>
          )}
          <InputField label="Email" value={email} onChange={setEmail} type="email" placeholder="john@company.com" />
          <InputField label="Password" value={password} onChange={setPassword} type="password" placeholder="••••••••" />

          {error && (
            <div style={{
              padding: "10px 14px", background: "rgba(239, 68, 68, 0.1)",
              border: "1px solid rgba(239, 68, 68, 0.2)", borderRadius: 10,
              color: "#ef4444", fontSize: 13, marginBottom: 16,
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%", padding: "14px 0",
              background: loading ? "rgba(6, 182, 212, 0.3)" : "linear-gradient(135deg, #06b6d4, #0891b2)",
              color: "#fff", border: "none", borderRadius: 12,
              fontSize: 14, fontWeight: 700, cursor: loading ? "wait" : "pointer",
              boxShadow: loading ? "none" : "0 0 20px rgba(6, 182, 212, 0.25)",
              transition: "all 0.3s",
              textTransform: "uppercase", letterSpacing: "0.08em",
            }}
          >
            {loading ? "Authenticating..." : mode === "login" ? "Sign In to NEXUS" : "Create Account"}
          </button>
        </form>

        {/* Footer */}
        <p style={{ textAlign: "center", fontSize: 11, color: "#475569", marginTop: 24, lineHeight: 1.6 }}>
          Enterprise-grade supply chain intelligence<br />
          Powered by Causal Genome Engine™
        </p>

        <button
          onClick={handleDemoAccess}
          style={{
            display: "block", width: "100%", textAlign: "center", marginTop: 16,
            fontSize: 13, color: "#818cf8", background: "none", border: "none",
            fontWeight: 500, cursor: "pointer", transition: "color 0.2s",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = "#a5b4fc")}
          onMouseLeave={(e) => (e.currentTarget.style.color = "#818cf8")}
        >
          Skip to demo →
        </button>
      </div>
    </div>
  );
}

function InputField({ label, value, onChange, type = "text", placeholder = "" }: {
  label: string; value: string; onChange: (v: string) => void; type?: string; placeholder?: string;
}) {
  return (
    <div style={{ marginBottom: 16 }}>
      <label style={{ display: "block", fontSize: 11, fontWeight: 600, color: "#94a3b8", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.1em" }}>
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        required
        style={{
          width: "100%", padding: "12px 14px",
          background: "rgba(15, 23, 42, 0.8)",
          border: "1px solid rgba(148, 163, 184, 0.12)",
          borderRadius: 10, color: "#f1f5f9", fontSize: 14,
          outline: "none", transition: "border-color 0.2s",
          boxSizing: "border-box",
        }}
        onFocus={e => e.target.style.borderColor = "rgba(6, 182, 212, 0.5)"}
        onBlur={e => e.target.style.borderColor = "rgba(148, 163, 184, 0.12)"}
      />
    </div>
  );
}
