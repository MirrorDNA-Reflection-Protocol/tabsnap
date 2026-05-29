"use client";

type Bar = {
  bar_index: number;
  time_start: number;
  time_end: number;
  confidence: number;
  lines: string[];
};

type Props = { bars: Bar[] };

export default function TabViewer({ bars }: Props) {
  if (!bars || bars.length === 0) {
    return <p style={{ color: "#666" }}>No tab data available.</p>;
  }

  return (
    <div
      style={{
        background: "#111",
        borderRadius: 8,
        padding: "1.5rem",
        overflowX: "auto",
        marginBottom: "1.5rem",
      }}
    >
      <h3 style={{ marginTop: 0, marginBottom: "1rem" }}>Generated Tab</h3>
      {bars.map((bar) => (
        <div key={bar.bar_index} style={{ marginBottom: "1.5rem" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: "0.75rem",
              color: "#666",
              marginBottom: "0.25rem",
            }}
          >
            <span>Bar {bar.bar_index}</span>
            <span>
              {bar.time_start.toFixed(1)}s - {bar.time_end.toFixed(1)}s
            </span>
          </div>
          <pre
            style={{
              fontFamily: '"Fira Code", "Courier New", monospace',
              fontSize: "0.9rem",
              lineHeight: 1.5,
              color: "#4ade80",
              margin: 0,
              whiteSpace: "pre",
            }}
          >
            {bar.lines.join("\n")}
          </pre>
        </div>
      ))}
    </div>
  );
}
