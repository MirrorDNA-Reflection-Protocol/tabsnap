"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Props = { jobId: string; initialTab: string };

export default function CorrectionEditor({ jobId, initialTab }: Props) {
  const [tab, setTab] = useState(initialTab);
  const [notes, setNotes] = useState("");
  const [rating, setRating] = useState(3);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      const res = await fetch(`${API_URL}/api/jobs/${jobId}/corrections`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          corrected_tab: tab,
          notes: notes || null,
          rating,
        }),
      });
      if (res.ok) setSaved(true);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      style={{
        background: "#111",
        borderRadius: 8,
        padding: "1.5rem",
        marginTop: "1.5rem",
      }}
    >
      <h3 style={{ marginTop: 0 }}>Edit Tab</h3>
      <textarea
        value={tab}
        onChange={(e) => {
          setTab(e.target.value);
          setSaved(false);
        }}
        rows={16}
        style={{
          width: "100%",
          fontFamily: '"Fira Code", "Courier New", monospace',
          fontSize: "0.85rem",
          lineHeight: 1.5,
          background: "#0a0a0a",
          color: "#4ade80",
          border: "1px solid #333",
          borderRadius: 6,
          padding: "1rem",
          resize: "vertical",
          boxSizing: "border-box",
        }}
      />

      <div style={{ marginTop: "1rem" }}>
        <label style={{ color: "#aaa", display: "block", marginBottom: "0.3rem" }}>
          Notes (optional)
        </label>
        <input
          type="text"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="e.g. AI got the last note wrong"
          style={{
            width: "100%",
            background: "#0a0a0a",
            color: "#e0e0e0",
            border: "1px solid #333",
            borderRadius: 6,
            padding: "0.5rem 0.8rem",
            boxSizing: "border-box",
          }}
        />
      </div>

      <div
        style={{
          marginTop: "1rem",
          display: "flex",
          alignItems: "center",
          gap: "1rem",
        }}
      >
        <label style={{ color: "#aaa" }}>Rating:</label>
        {[1, 2, 3, 4, 5].map((v) => (
          <button
            key={v}
            onClick={() => setRating(v)}
            style={{
              width: 32,
              height: 32,
              borderRadius: "50%",
              border: "1px solid #333",
              background: rating >= v ? "#2563eb" : "#222",
              color: "#fff",
              cursor: "pointer",
              fontSize: "0.8rem",
            }}
          >
            {v}
          </button>
        ))}
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        style={{
          marginTop: "1rem",
          padding: "0.6rem 2rem",
          background: saved ? "#16a34a" : "#2563eb",
          color: "#fff",
          border: "none",
          borderRadius: 6,
          cursor: saving ? "not-allowed" : "pointer",
          fontWeight: 600,
        }}
      >
        {saving ? "Saving..." : saved ? "Saved" : "Save Correction"}
      </button>
    </div>
  );
}
