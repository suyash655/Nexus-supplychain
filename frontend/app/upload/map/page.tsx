"use client";

/**
 * /upload/map
 *
 * Shown when the backend returns HTTP 422 (ambiguous_column_mapping).
 * Fetches the last-uploaded file's detected columns from GET /upload/columns,
 * renders a dropdown per canonical field, and POSTs the confirmed mapping to
 * POST /upload/confirm, then redirects to /dashboard.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "../../components/Sidebar";
import TopNav from "../../components/TopNav";
import { CheckCircle2, AlertCircle, ArrowRight, Columns } from "lucide-react";
import { apiFetch } from "@/lib/api";

// Canonical fields the user must map their columns to.
const CANONICAL_FIELDS: { key: string; label: string; required: boolean }[] = [
  { key: "supplier",      label: "Supplier / Vendor",    required: true  },
  { key: "sku",           label: "SKU / Product ID",      required: true  },
  { key: "delay_days",    label: "Delay Days",            required: false },
  { key: "cost",          label: "Cost / Invoice Amount", required: false },
  { key: "order_date",    label: "Order Date",            required: false },
  { key: "delivery_date", label: "Delivery Date",         required: false },
  { key: "warehouse",     label: "Warehouse / Facility",  required: false },
  { key: "region",        label: "Region / Country",      required: false },
  { key: "quantity",      label: "Quantity / Units",      required: false },
  { key: "quality_score", label: "Quality Score",         required: false },
];

export default function ColumnMapPage() {
  const router = useRouter();
  const [columns, setColumns]         = useState<string[]>([]);
  const [suggested, setSuggested]     = useState<Record<string, string>>({});
  const [mapping, setMapping]         = useState<Record<string, string>>({});
  const [loading, setLoading]         = useState(true);
  const [submitting, setSubmitting]   = useState(false);
  const [error, setError]             = useState<string | null>(null);
  const [success, setSuccess]         = useState(false);

  // Load last-uploaded file's columns + any suggested mapping from the backend
  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/upload/columns");
        if (!res.ok) throw new Error("Could not load column list from server.");
        const data = await res.json();

        const cols: string[]                  = data.columns ?? [];
        const suggestedMap: Record<string, string> = data.mapping ?? {};

        setColumns(cols);
        setSuggested(suggestedMap);

        // Pre-fill mapping with server suggestions
        const initial: Record<string, string> = {};
        CANONICAL_FIELDS.forEach(({ key }) => {
          initial[key] = suggestedMap[key] ?? "";
        });
        setMapping(initial);
      } catch (err: any) {
        setError(err.message ?? "Failed to load columns.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSelect = (canonical: string, raw: string) => {
    setMapping(prev => ({ ...prev, [canonical]: raw }));
  };

  const handleConfirm = async () => {
    // Validate required fields
    const missing = CANONICAL_FIELDS.filter(f => f.required && !mapping[f.key]);
    if (missing.length > 0) {
      setError(`Required fields not mapped: ${missing.map(f => f.label).join(", ")}`);
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // Store the confirmed mapping in localStorage so the next
      // /upload call can pass it, then trigger analysis via /upload/confirm
      const flatMapping: Record<string, string> = {};
      Object.entries(mapping).forEach(([canonical, raw]) => {
        if (raw) flatMapping[canonical] = raw;
      });
      localStorage.setItem("nexus_confirmed_mapping", JSON.stringify(flatMapping));

      const res = await apiFetch("/upload/confirm", { method: "POST" });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? "Confirm failed");
      }

      setSuccess(true);
      setTimeout(() => router.push("/dashboard"), 1200);
    } catch (err: any) {
      setError(err.message ?? "Failed to confirm mapping.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <TopNav />
        <main
          className="main-content"
          style={{ display: "flex", alignItems: "flex-start", justifyContent: "center" }}
        >
          <div style={{ width: "100%", maxWidth: 680 }}>

            {/* ── Header ── */}
            <div style={{ marginBottom: 28 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                <Columns size={22} color="#facc15" />
                <h1 style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-0.02em" }}>
                  Confirm Column Mapping
                </h1>
              </div>
              <p style={{ fontSize: 13, color: "var(--color-text-muted)" }}>
                Some columns could not be mapped automatically. Select the correct source
                column for each field, then click Confirm.
              </p>
            </div>

            {/* ── Error banner ── */}
            {error && (
              <div
                style={{
                  display: "flex", alignItems: "center", gap: 10,
                  padding: "10px 14px", marginBottom: 20,
                  background: "rgba(239,68,68,0.08)",
                  border: "1px solid rgba(239,68,68,0.2)",
                  borderRadius: 10, color: "#ef4444", fontSize: 13,
                }}
              >
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            {/* ── Success banner ── */}
            {success && (
              <div
                style={{
                  display: "flex", alignItems: "center", gap: 10,
                  padding: "10px 14px", marginBottom: 20,
                  background: "rgba(34,197,94,0.08)",
                  border: "1px solid rgba(34,197,94,0.2)",
                  borderRadius: 10, color: "#22c55e", fontSize: 13,
                }}
              >
                <CheckCircle2 size={16} />
                Mapping confirmed. Redirecting to dashboard…
              </div>
            )}

            {/* ── Loading skeleton ── */}
            {loading && (
              <div className="card" style={{ padding: 40, textAlign: "center", color: "var(--color-text-muted)", fontSize: 13 }}>
                Loading columns from server…
              </div>
            )}

            {/* ── Mapping form ── */}
            {!loading && columns.length > 0 && !success && (
              <div className="card" style={{ padding: 24 }}>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    columnGap: 32,
                    rowGap: 18,
                  }}
                >
                  {CANONICAL_FIELDS.map(({ key, label, required }) => {
                    const isSuggested = !!suggested[key];
                    return (
                      <div key={key}>
                        <label
                          style={{
                            display: "block",
                            fontSize: 11,
                            fontWeight: 600,
                            textTransform: "uppercase",
                            letterSpacing: "0.08em",
                            color: required
                              ? "var(--color-text-muted)"
                              : "var(--color-text-muted)",
                            marginBottom: 6,
                          }}
                        >
                          {label}
                          {required && (
                            <span style={{ color: "#ef4444", marginLeft: 3 }}>*</span>
                          )}
                          {isSuggested && (
                            <span
                              style={{
                                marginLeft: 6,
                                fontSize: 9,
                                color: "#22c55e",
                                fontWeight: 500,
                                textTransform: "none",
                                letterSpacing: 0,
                              }}
                            >
                              auto-detected
                            </span>
                          )}
                        </label>

                        <select
                          value={mapping[key] ?? ""}
                          onChange={e => handleSelect(key, e.target.value)}
                          style={{
                            width: "100%",
                            padding: "9px 12px",
                            background: "var(--color-surface)",
                            border: `1px solid ${
                              required && !mapping[key]
                                ? "rgba(239,68,68,0.4)"
                                : "var(--color-border-subtle)"
                            }`,
                            borderRadius: 8,
                            color: mapping[key] ? "var(--color-text)" : "var(--color-text-muted)",
                            fontSize: 13,
                            outline: "none",
                            cursor: "pointer",
                            transition: "border-color 150ms ease-out",
                          }}
                          onFocus={e => {
                            e.target.style.borderColor = "var(--color-primary)";
                          }}
                          onBlur={e => {
                            e.target.style.borderColor =
                              required && !mapping[key]
                                ? "rgba(239,68,68,0.4)"
                                : "var(--color-border-subtle)";
                          }}
                        >
                          <option value="">— skip this field —</option>
                          {columns.map(col => (
                            <option key={col} value={col}>
                              {col}
                            </option>
                          ))}
                        </select>
                      </div>
                    );
                  })}
                </div>

                {/* ── Confirm button ── */}
                <div style={{ marginTop: 28, display: "flex", justifyContent: "flex-end" }}>
                  <button
                    onClick={handleConfirm}
                    disabled={submitting}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      padding: "12px 28px",
                      background: submitting ? "rgba(250,204,21,0.4)" : "#facc15",
                      color: "#000",
                      border: "none",
                      borderRadius: 10,
                      fontWeight: 700,
                      fontSize: 14,
                      cursor: submitting ? "wait" : "pointer",
                      transition: "opacity 150ms ease-out",
                    }}
                  >
                    {submitting ? "Confirming…" : "Confirm Mapping"}
                    {!submitting && <ArrowRight size={16} />}
                  </button>
                </div>
              </div>
            )}

            {/* ── No columns fallback ── */}
            {!loading && columns.length === 0 && !success && (
              <div
                className="card"
                style={{ padding: 40, textAlign: "center", color: "var(--color-text-muted)" }}
              >
                <p style={{ fontSize: 14, marginBottom: 12 }}>
                  No column data found. Please upload a file first.
                </p>
                <a
                  href="/upload"
                  style={{
                    fontSize: 13,
                    fontWeight: 600,
                    color: "#facc15",
                    textDecoration: "none",
                  }}
                >
                  ← Back to Upload
                </a>
              </div>
            )}

          </div>
        </main>
      </div>
    </div>
  );
}
