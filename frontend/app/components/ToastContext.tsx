"use client";

import { createContext, useContext, useState, useCallback, ReactNode } from "react";

type ToastType = "success" | "error" | "info" | "warning";

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastContextValue {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextValue>({
  showToast: () => {},
});

export function useToast() {
  return useContext(ToastContext);
}

let toastCounter = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: ToastType = "info") => {
    const id = ++toastCounter;
    setToasts((prev) => [...prev, { id, message, type }]);

    // Auto-dismiss after 4 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const typeStyles: Record<ToastType, { bg: string; border: string; color: string }> = {
    success: { bg: "rgba(34, 197, 94, 0.12)", border: "rgba(34, 197, 94, 0.3)", color: "#22c55e" },
    error: { bg: "rgba(239, 68, 68, 0.12)", border: "rgba(239, 68, 68, 0.3)", color: "#ef4444" },
    warning: { bg: "rgba(245, 158, 11, 0.12)", border: "rgba(245, 158, 11, 0.3)", color: "#f59e0b" },
    info: { bg: "rgba(99, 102, 241, 0.12)", border: "rgba(99, 102, 241, 0.3)", color: "#818cf8" },
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}

      {/* Toast container — fixed bottom-right */}
      <div
        style={{
          position: "fixed",
          bottom: 24,
          right: 24,
          zIndex: 9999,
          display: "flex",
          flexDirection: "column",
          gap: 8,
          pointerEvents: "none",
        }}
      >
        {toasts.map((toast) => {
          const style = typeStyles[toast.type];
          return (
            <div
              key={toast.id}
              style={{
                pointerEvents: "auto",
                padding: "12px 20px",
                background: style.bg,
                border: `1px solid ${style.border}`,
                borderRadius: 12,
                color: style.color,
                fontSize: 13,
                fontWeight: 600,
                backdropFilter: "blur(16px)",
                boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
                cursor: "pointer",
                animation: "slideInRight 0.3s ease-out",
                maxWidth: 400,
                lineHeight: 1.5,
              }}
              onClick={() => dismiss(toast.id)}
              role="alert"
              aria-live="polite"
            >
              {toast.message}
            </div>
          );
        })}
      </div>

      <style>{`
        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(100px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </ToastContext.Provider>
  );
}
