"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a CSV file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (data.status !== "success") {
        alert("Upload failed or invalid CSV");
        return;
      }

      // ✅ Redirect ONLY after confirmed upload
      router.push("/upload/map");

    } catch (err) {
      alert("Upload failed. Check backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-[#0e1116] text-white">
      <div className="w-full max-w-md border border-white/15 rounded-xl p-8">
        <h1 className="text-2xl font-semibold mb-4">
          Upload Supply Chain Data
        </h1>

        <p className="text-sm text-white/60 mb-6">
          Upload a CSV file to analyze supplier risk and delays.
        </p>

        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm text-white
                     file:mr-4 file:py-2 file:px-4
                     file:rounded-lg file:border-0
                     file:bg-[var(--accent)]
                     file:text-black file:font-semibold
                     hover:file:opacity-90"
        />

        {/* 🔑 IMPORTANT FIX: type="button" */}
        <button
          type="button"
          onClick={handleUpload}
          disabled={loading}
          className="mt-6 w-full rounded-lg bg-white/10 py-3
                     hover:bg-white/20 transition disabled:opacity-50"
        >
          {loading ? "Uploading..." : "Upload & Analyze"}
        </button>
      </div>
    </main>
  );
}
