"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import UploadBox from "@/components/UploadBox";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [tuning, setTuning] = useState("EADGBE");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    const form = new FormData();
    form.append("file", file);
    form.append("instrument", "guitar");
    form.append("tuning", tuning);

    try {
      const res = await fetch(`${API_URL}/api/jobs`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Upload failed (${res.status})`);
      }
      const data = await res.json();
      router.push(`/jobs/${data.job_id}`);
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", paddingTop: "3rem" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
        Hear a riff. Get the tab.
      </h1>
      <p style={{ color: "#999", marginBottom: "2rem" }}>
        Upload 10-30 seconds of guitar audio.
      </p>

      <UploadBox onFileSelect={setFile} selectedFile={file} />

      <div style={{ marginTop: "1.5rem" }}>
        <label style={{ color: "#aaa", marginRight: "0.5rem" }}>Tuning:</label>
        <select
          value={tuning}
          onChange={(e) => setTuning(e.target.value)}
          style={{
            background: "#1a1a1a",
            color: "#e0e0e0",
            border: "1px solid #333",
            borderRadius: 6,
            padding: "0.4rem 0.8rem",
          }}
        >
          <option value="EADGBE">Standard (EADGBE)</option>
          <option value="DADGBE">Drop D</option>
          <option value="DGDGBE">Open G</option>
        </select>
      </div>

      <button
        onClick={handleSubmit}
        disabled={!file || uploading}
        style={{
          marginTop: "1.5rem",
          padding: "0.8rem 2.5rem",
          fontSize: "1rem",
          fontWeight: 600,
          background: file && !uploading ? "#2563eb" : "#333",
          color: "#fff",
          border: "none",
          borderRadius: 8,
          cursor: file && !uploading ? "pointer" : "not-allowed",
        }}
      >
        {uploading ? "Uploading..." : "Generate Tab"}
      </button>

      {error && (
        <p style={{ color: "#ef4444", marginTop: "1rem" }}>{error}</p>
      )}
    </div>
  );
}
