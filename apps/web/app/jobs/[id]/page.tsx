"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import AudioPlayer from "@/components/AudioPlayer";
import TabViewer from "@/components/TabViewer";
import ConfidenceBadge from "@/components/ConfidenceBadge";
import CorrectionEditor from "@/components/CorrectionEditor";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const STAGE_LABELS: Record<string, string> = {
  normalizing_audio: "Normalizing audio",
  fingerprinting: "Checking song match",
  separating_stems: "Separating stems",
  transcribing_notes: "Detecting notes",
  detecting_tempo: "Detecting tempo",
  building_tab: "Building playable tab",
  scoring_confidence: "Scoring confidence",
  done: "Complete",
};

type JobStatus = {
  job_id: string;
  status: string;
  stage: string | null;
  progress: number;
};

type JobResult = {
  job_id: string;
  song_match: { found: boolean; title: string | null; artist: string | null; confidence: number };
  tempo_bpm: number;
  tuning: string;
  chords: any[];
  tab: { format: string; bars: any[] };
  ascii_tab: string;
  confidence: number;
  midi_url: string | null;
  audio_preview_url: string | null;
};

export default function JobPage() {
  const { id } = useParams<{ id: string }>();
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [result, setResult] = useState<JobResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const pollStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/jobs/${id}`);
      if (!res.ok) throw new Error("Failed to fetch job status");
      const data: JobStatus = await res.json();
      setStatus(data);

      if (data.status === "done") {
        const rr = await fetch(`${API_URL}/api/jobs/${id}/result`);
        if (rr.ok) setResult(await rr.json());
      }
    } catch (err: any) {
      setError(err.message);
    }
  }, [id]);

  useEffect(() => {
    pollStatus();
    const interval = setInterval(() => {
      if (!result) pollStatus();
    }, 2000);
    return () => clearInterval(interval);
  }, [pollStatus, result]);

  // --- Processing screen ---
  if (!result && status?.status !== "failed") {
    return (
      <div style={{ paddingTop: "3rem", textAlign: "center" }}>
        <h2>Processing your audio...</h2>
        <div
          style={{
            margin: "2rem auto",
            maxWidth: 400,
            background: "#1a1a1a",
            borderRadius: 8,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              height: 8,
              width: `${status?.progress || 0}%`,
              background: "#2563eb",
              transition: "width 0.5s",
            }}
          />
        </div>
        <p style={{ color: "#aaa" }}>
          {STAGE_LABELS[status?.stage || ""] || status?.stage || "Queued..."}
        </p>
        <p style={{ color: "#666", fontSize: "0.85rem" }}>
          {status?.progress || 0}%
        </p>
      </div>
    );
  }

  // --- Error screen ---
  if (status?.status === "failed") {
    return (
      <div style={{ paddingTop: "3rem", textAlign: "center" }}>
        <h2 style={{ color: "#ef4444" }}>Processing failed</h2>
        <p style={{ color: "#999" }}>{status.stage}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ paddingTop: "3rem", textAlign: "center" }}>
        <h2 style={{ color: "#ef4444" }}>Error</h2>
        <p style={{ color: "#999" }}>{error}</p>
      </div>
    );
  }

  if (!result) return null;

  // --- Result screen ---
  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.5rem",
        }}
      >
        <div>
          <h2 style={{ margin: 0 }}>Your Tab</h2>
          <p style={{ color: "#888", margin: "0.25rem 0" }}>
            Tempo: {result.tempo_bpm} BPM &middot; Tuning: {result.tuning}
          </p>
        </div>
        <ConfidenceBadge confidence={result.confidence} />
      </div>

      {result.audio_preview_url && (
        <AudioPlayer src={`${API_URL}${result.audio_preview_url}`} />
      )}

      <TabViewer bars={result.tab.bars} />

      <div
        style={{
          display: "flex",
          gap: "1rem",
          margin: "1.5rem 0",
          flexWrap: "wrap",
        }}
      >
        {result.midi_url && (
          <a
            href={`${API_URL}${result.midi_url}`}
            download
            style={{
              padding: "0.5rem 1.2rem",
              background: "#1a1a1a",
              border: "1px solid #333",
              borderRadius: 6,
              color: "#e0e0e0",
              textDecoration: "none",
            }}
          >
            Download MIDI
          </a>
        )}
        <a
          href={`${API_URL}/files/${result.job_id}/tab.txt`}
          download
          style={{
            padding: "0.5rem 1.2rem",
            background: "#1a1a1a",
            border: "1px solid #333",
            borderRadius: 6,
            color: "#e0e0e0",
            textDecoration: "none",
          }}
        >
          Download Tab (.txt)
        </a>
      </div>

      <CorrectionEditor jobId={result.job_id} initialTab={result.ascii_tab} />
    </div>
  );
}
