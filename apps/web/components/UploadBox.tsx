"use client";

import { useRef } from "react";

type Props = {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
};

const ACCEPTED = ".mp3,.wav,.m4a";

export default function UploadBox({ onFileSelect, selectedFile }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) onFileSelect(f);
  };

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      style={{
        border: "2px dashed #333",
        borderRadius: 12,
        padding: "3rem 2rem",
        cursor: "pointer",
        background: selectedFile ? "#111" : "transparent",
        transition: "background 0.2s",
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        onChange={(e) => onFileSelect(e.target.files?.[0] || null)}
        style={{ display: "none" }}
      />
      {selectedFile ? (
        <p style={{ margin: 0, color: "#4ade80" }}>
          {selectedFile.name} ({(selectedFile.size / 1024).toFixed(0)} KB)
        </p>
      ) : (
        <p style={{ margin: 0, color: "#666" }}>
          Drop an audio file here, or click to browse.
          <br />
          <span style={{ fontSize: "0.85rem" }}>MP3, WAV, or M4A — max 30 seconds</span>
        </p>
      )}
    </div>
  );
}
