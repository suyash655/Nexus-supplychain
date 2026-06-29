"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [analysisStatus, setAnalysisStatus] = useState<string>("");
  const router = useRouter();

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a CSV file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setUploadStatus("Uploading file...");
    setAnalysisStatus("");

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const token = localStorage.getItem("nexus_token");
      
      const headers: Record<string, string> = {};
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const res = await fetch(`${apiUrl}/upload`, {
        method: "POST",
        headers,
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        const errorMsg = data.detail || data.message || "Upload failed";
        alert(`Upload failed: ${errorMsg}`);
        setUploadStatus(`Upload failed: ${errorMsg}`);
        setLoading(false);
        return;
      }

      if (data.status !== "success") {
        alert("Upload failed or invalid CSV");
        setUploadStatus("Upload failed");
        setLoading(false);
        return;
      }

      setUploadStatus(`Upload successful! ${data.rows_inserted} rows inserted.`);

      // Check if analysis started
      if (data.analysis_started && data.upload_id) {
        setAnalysisStatus("Analysis started in background...");
        
        // Poll for analysis progress
        pollAnalysisProgress(data.upload_id, apiUrl);
      } else {
        // No analysis or analysis skipped
        setTimeout(() => {
          router.push("/dashboard");
        }, 1000);
      }

    } catch (err) {
      alert("Upload failed. Check backend.");
      setUploadStatus("Upload failed");
    } finally {
      if (!analysisStatus) {
        setLoading(false);
      }
    }
  };

  const pollAnalysisProgress = async (uploadId: string, apiUrl: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const res = await fetch(`${apiUrl}/analysis/progress/${uploadId}`);
        const progress = await res.json();
        
        if (progress) {
          const percentage = Math.round(progress.progress_percentage);
          setAnalysisStatus(`Analysis in progress: ${percentage}% (${progress.completed_stages}/${progress.total_stages} stages)`);
          
          if (progress.status === "completed" || progress.status === "partial" || progress.status === "failed") {
            clearInterval(pollInterval);
            setLoading(false);
            setAnalysisStatus(`Analysis ${progress.status}. Redirecting to mapping...`);
            
            setTimeout(() => {
              router.push("/upload/map");
            }, 1500);
          }
        }
      } catch (err) {
        console.error("Error polling analysis progress:", err);
      }
    }, 2000); // Poll every 2 seconds

    // Safety timeout after 5 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      setLoading(false);
      setAnalysisStatus("Analysis taking longer than expected. You can proceed to mapping.");
      setTimeout(() => {
        router.push("/upload/map");
      }, 2000);
    }, 300000); // 5 minutes
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

        {/* Status Messages */}
        {uploadStatus && (
          <div className="mt-4 p-3 rounded-lg bg-white/5 border border-white/10 text-sm">
            {uploadStatus}
          </div>
        )}
        
        {analysisStatus && (
          <div className="mt-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-sm">
            {analysisStatus}
          </div>
        )}

        {/* 🔑 IMPORTANT FIX: type="button" */}
        <button
          type="button"
          onClick={handleUpload}
          disabled={loading}
          className="mt-6 w-full rounded-lg bg-white/10 py-3
                     hover:bg-white/20 transition disabled:opacity-50"
        >
          {loading ? "Processing..." : "Upload & Analyze"}
        </button>
      </div>
    </main>
  );
}
