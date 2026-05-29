"use client";

type Props = { confidence: number };

function label(c: number): string {
  if (c >= 0.8) return "Strong draft";
  if (c >= 0.6) return "Playable draft";
  if (c >= 0.4) return "Needs review";
  return "Experimental";
}

function color(c: number): string {
  if (c >= 0.8) return "#4ade80";
  if (c >= 0.6) return "#facc15";
  if (c >= 0.4) return "#fb923c";
  return "#ef4444";
}

export default function ConfidenceBadge({ confidence }: Props) {
  const pct = Math.round(confidence * 100);
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "0.5rem",
        padding: "0.4rem 0.8rem",
        background: "#1a1a1a",
        border: `1px solid ${color(confidence)}`,
        borderRadius: 6,
      }}
    >
      <span style={{ color: color(confidence), fontWeight: 600 }}>{pct}%</span>
      <span style={{ color: "#999", fontSize: "0.8rem" }}>
        {label(confidence)}
      </span>
    </div>
  );
}
