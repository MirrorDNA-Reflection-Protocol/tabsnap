import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "TabSnap — Hear a riff. Get the tab.",
  description: "Upload guitar audio and get a playable tab instantly.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          backgroundColor: "#0a0a0a",
          color: "#e0e0e0",
          minHeight: "100vh",
        }}
      >
        <header
          style={{
            padding: "1rem 2rem",
            borderBottom: "1px solid #222",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
          }}
        >
          <span style={{ fontSize: "1.4rem", fontWeight: 700, color: "#fff" }}>
            TabSnap
          </span>
          <span style={{ fontSize: "0.85rem", color: "#888" }}>MVP</span>
        </header>
        <main style={{ maxWidth: 900, margin: "0 auto", padding: "2rem 1rem" }}>
          {children}
        </main>
      </body>
    </html>
  );
}
